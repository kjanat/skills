#!/usr/bin/env -S uv run
"""Generic skill-eval runner.

Drives `claude -p --output-format json --json-schema ...` against each case in
a skill's `evals/evals.json`, validates the structured response with mechanical
assertions, and writes artifacts to `<skill>/evals/runs/<UTC-timestamp>/`.

Usage:
    uv run scripts/eval/run_eval.py <skill-name> [--limit N] [--model M] [-v]

Each eval case in `evals.json` looks like:
    {
        "id": 1,
        "name": "case-slug",
        "prompt": "User-facing task prompt.",
        "json_schema": { ...JSON Schema for structured output... },
        "assertions": [
            {"name": "Uses v9 pin",
             "path": "pinned_action_version",
             "op": "equals",
             "value": "v9"}
        ],
        "system_prompt": "optional override (else default points at SKILL.md)"
    }

Assertion ops: equals, not_equals, contains, not_contains, matches,
not_matches, truthy, falsy, length_gte, length_lte. `path` uses dotted access
(`a.b.0.c`); integer segments are list indices.
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import cast

import jsonschema

ROOT = Path(__file__).resolve().parent.parent.parent
SKILLS_DIR = ROOT / "skills"


# ─── Types ─────────────────────────────────────────────────────────────


type JsonValue = (
    None | bool | int | float | str | list["JsonValue"] | dict[str, "JsonValue"]
)
type JsonObject = dict[str, JsonValue]


@dataclass(frozen=True)
class Assertion:
    name: str
    path: str
    op: str
    value: JsonValue = None


@dataclass(frozen=True)
class EvalCase:
    id: int
    name: str
    prompt: str
    json_schema: JsonObject
    assertions: tuple[Assertion, ...]
    system_prompt: str | None = None


@dataclass
class AssertionResult:
    name: str
    path: str
    op: str
    expected: JsonValue
    actual: JsonValue
    passed: bool
    note: str = ""


@dataclass
class CaseResult:
    case: EvalCase
    duration_ms: int | None
    total_tokens: int | None
    total_cost_usd: float | None
    structured: JsonValue
    raw_result_text: str
    assertions: list[AssertionResult] = field(default_factory=list)
    error: str | None = None

    @property
    def passed(self) -> bool:
        return self.error is None and all(a.passed for a in self.assertions)


# ─── Loading ───────────────────────────────────────────────────────────


def load_evals(path: Path) -> list[EvalCase]:
    payload: JsonValue = cast(JsonValue, json.loads(path.read_text()))
    if not isinstance(payload, dict):
        raise ValueError(f"{path}: top level must be an object")
    raw_evals = payload.get("evals")
    if not isinstance(raw_evals, list) or not raw_evals:
        raise ValueError(f"{path}: 'evals' must be a non-empty list")
    cases: list[EvalCase] = []
    for index, item in enumerate(raw_evals):
        if not isinstance(item, dict):
            raise ValueError(f"{path}: eval[{index}] is not an object")
        try:
            cases.append(_parse_case(item, index))
        except (KeyError, TypeError, ValueError) as err:
            raise ValueError(f"{path}: eval[{index}] invalid: {err}") from err
    return cases


def _parse_case(item: JsonObject, index: int) -> EvalCase:
    eval_id_raw = item.get("id", index)
    if not isinstance(eval_id_raw, int) or isinstance(eval_id_raw, bool):
        raise ValueError("'id' must be an integer")
    eval_id = eval_id_raw
    raw_name = item.get("name")
    name = raw_name if isinstance(raw_name, str) and raw_name else f"eval-{eval_id}"
    prompt = item.get("prompt")
    if not isinstance(prompt, str) or not prompt.strip():
        raise ValueError("'prompt' must be a non-empty string")
    schema = item.get("json_schema")
    if not isinstance(schema, dict):
        raise ValueError("'json_schema' must be an object")
    try:
        jsonschema.Draft202012Validator.check_schema(schema)
    except jsonschema.SchemaError as err:
        raise ValueError(
            f"'json_schema' is not a valid JSON Schema: {err.message}"
        ) from err
    raw_assertions = item.get("assertions", [])
    if not isinstance(raw_assertions, list):
        raise ValueError("'assertions' must be a list when set")
    assertions = tuple(_parse_assertion(a, i) for i, a in enumerate(raw_assertions))
    system_prompt = item.get("system_prompt")
    if system_prompt is not None and not isinstance(system_prompt, str):
        raise ValueError("'system_prompt' must be a string when set")
    return EvalCase(
        id=eval_id,
        name=name,
        prompt=prompt,
        json_schema=schema,
        assertions=assertions,
        system_prompt=system_prompt,
    )


VALID_OPS = {
    "equals",
    "not_equals",
    "contains",
    "not_contains",
    "matches",
    "not_matches",
    "truthy",
    "falsy",
    "length_gte",
    "length_lte",
}


def _parse_assertion(item: JsonValue, index: int) -> Assertion:
    if not isinstance(item, dict):
        raise ValueError(f"assertion[{index}] is not an object")
    raw_name = item.get("name")
    name = raw_name if isinstance(raw_name, str) and raw_name else f"assertion-{index}"
    path = item.get("path", "")
    if not isinstance(path, str):
        raise ValueError(f"assertion[{index}].path must be a string")
    op = item.get("op")
    if not isinstance(op, str) or op not in VALID_OPS:
        raise ValueError(f"assertion[{index}].op must be one of {sorted(VALID_OPS)}")
    return Assertion(name=name, path=path, op=op, value=item.get("value"))


# ─── Path resolution ───────────────────────────────────────────────────


def get_at_path(obj: JsonValue, path: str) -> tuple[bool, JsonValue]:
    """Return (found, value). Empty path returns the root object."""
    if path == "":
        return True, obj
    cursor = obj
    for segment in path.split("."):
        if isinstance(cursor, dict) and segment in cursor:
            cursor = cursor[segment]
        elif isinstance(cursor, list):
            try:
                idx = int(segment)
            except ValueError:
                return False, None
            if 0 <= idx < len(cursor):
                cursor = cursor[idx]
            else:
                return False, None
        else:
            return False, None
    return True, cursor


def _as_int(value: JsonValue) -> int | None:
    return value if isinstance(value, int) and not isinstance(value, bool) else None


def _as_float(value: JsonValue) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int | float):
        return float(value)
    return None


# ─── Assertion engine ──────────────────────────────────────────────────


def evaluate_assertion(structured: JsonValue, assertion: Assertion) -> AssertionResult:
    found, actual = get_at_path(structured, assertion.path)
    if not found and assertion.op not in {
        "falsy",
        "not_contains",
        "not_matches",
        "not_equals",
    }:
        return AssertionResult(
            name=assertion.name,
            path=assertion.path,
            op=assertion.op,
            expected=assertion.value,
            actual=None,
            passed=False,
            note=f"path '{assertion.path}' not present in response",
        )
    expected = assertion.value
    op = assertion.op
    passed = False
    note = ""
    try:
        match op:
            case "equals":
                passed = actual == expected
            case "not_equals":
                passed = actual != expected
            case "contains":
                if isinstance(actual, str):
                    passed = isinstance(expected, str) and expected in actual
                elif isinstance(actual, list):
                    passed = expected in actual
                else:
                    note = f"contains: actual is {type(actual).__name__}, not str/list"
            case "not_contains":
                if not found:
                    passed = True
                elif isinstance(actual, str):
                    passed = isinstance(expected, str) and expected not in actual
                elif isinstance(actual, list):
                    passed = expected not in actual
                else:
                    note = (
                        f"not_contains: actual is {type(actual).__name__}, not str/list"
                    )
            case "matches":
                if not isinstance(expected, str):
                    note = "matches: value must be a regex string"
                elif isinstance(actual, str):
                    passed = re.search(expected, actual) is not None
                elif isinstance(actual, list):
                    passed = any(
                        isinstance(item, str) and re.search(expected, item)
                        for item in actual
                    )
                else:
                    note = f"matches: actual is {type(actual).__name__}, not str/list"
            case "not_matches":
                if not isinstance(expected, str):
                    note = "not_matches: value must be a regex string"
                elif not found:
                    passed = True
                elif isinstance(actual, str):
                    passed = re.search(expected, actual) is None
                elif isinstance(actual, list):
                    passed = not any(
                        isinstance(item, str) and re.search(expected, item)
                        for item in actual
                    )
                else:
                    note = (
                        f"not_matches: actual is {type(actual).__name__}, not str/list"
                    )
            case "truthy":
                passed = bool(actual)
            case "falsy":
                passed = not bool(actual)
            case "length_gte":
                if isinstance(actual, str | list | dict) and isinstance(expected, int):
                    passed = len(actual) >= expected
                else:
                    note = "length_gte: actual must be sized and value must be int"
            case "length_lte":
                if isinstance(actual, str | list | dict) and isinstance(expected, int):
                    passed = len(actual) <= expected
                else:
                    note = "length_lte: actual must be sized and value must be int"
            case _:
                note = f"unknown op {op!r}"
    except (TypeError, re.error) as err:
        note = f"{op} raised {type(err).__name__}: {err}"
        passed = False
    return AssertionResult(
        name=assertion.name,
        path=assertion.path,
        op=op,
        expected=expected,
        actual=actual,
        passed=passed,
        note=note,
    )


# ─── Claude invocation ─────────────────────────────────────────────────


def default_system_prompt(skill_dir: Path) -> str:
    return (
        "You are testing a documentation skill for an AI coding assistant.\n"
        f"Read this file in full: {skill_dir / 'SKILL.md'}\n"
        f"Then read any reference files its 'Reading order' (or equivalent) table points to inside {skill_dir / 'references'}.\n"
        "Follow the skill's guidance strictly to complete the user's task.\n"
        "Do not search the web. Do not consult any other source. Do not read any other skill.\n"
        "Output JSON matching the provided schema. Be precise — your fields will be checked mechanically."
    )


def run_claude(
    *,
    case: EvalCase,
    skill_dir: Path,
    model: str | None,
    verbose: bool,
) -> tuple[JsonObject, list[JsonValue]]:
    system_prompt = case.system_prompt or default_system_prompt(skill_dir)
    cmd = [
        "claude",
        "-p",
        "--output-format",
        "json",
        "--permission-mode",
        "bypassPermissions",
        "--no-session-persistence",
        "--disable-slash-commands",
        "--add-dir",
        str(skill_dir),
        "--system-prompt",
        system_prompt,
        "--json-schema",
        json.dumps(case.json_schema),
    ]
    if model:
        cmd.extend(["--model", model])
    cmd.append(case.prompt)
    if verbose:
        properties = case.json_schema.get("properties")
        schema_keys = list(properties.keys()) if isinstance(properties, dict) else []
        print(
            f"  $ claude -p (prompt={len(case.prompt)} chars, schema_keys={schema_keys})",
            file=sys.stderr,
        )
    completed = subprocess.run(
        cmd, cwd=skill_dir, capture_output=True, text=True, check=False
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"claude exited {completed.returncode}\nstdout:\n{completed.stdout}\nstderr:\n{completed.stderr}"
        )
    parsed: JsonValue = cast(JsonValue, json.loads(completed.stdout))
    if isinstance(parsed, dict):
        if parsed.get("type") != "result":
            raise RuntimeError(f"unexpected claude payload: {parsed!r}")
        return parsed, [parsed]
    if not isinstance(parsed, list):
        raise RuntimeError(f"unexpected claude output type: {type(parsed).__name__}")
    result_event = next(
        (e for e in parsed if isinstance(e, dict) and e.get("type") == "result"),
        None,
    )
    if result_event is None:
        raise RuntimeError(f"no result event in claude output: {parsed!r}")
    raw_events = parsed
    return result_event, raw_events


# ─── Run pipeline ──────────────────────────────────────────────────────


def run_case(
    *,
    case: EvalCase,
    skill_dir: Path,
    case_dir: Path,
    model: str | None,
    verbose: bool,
) -> CaseResult:
    case_dir.mkdir(parents=True, exist_ok=True)
    if verbose:
        print(f"[{case.name}] running", file=sys.stderr)
    try:
        result_event, raw_events = run_claude(
            case=case,
            skill_dir=skill_dir,
            model=model,
            verbose=verbose,
        )
    except Exception as err:
        return CaseResult(
            case=case,
            duration_ms=None,
            total_tokens=None,
            total_cost_usd=None,
            structured=None,
            raw_result_text="",
            error=str(err),
        )
    _ = (case_dir / "raw.json").write_text(json.dumps(raw_events, indent=2) + "\n")
    result_text = str(result_event.get("result", ""))
    _ = (case_dir / "result.txt").write_text(result_text)
    duration_ms = _as_int(result_event.get("duration_ms"))
    usage = result_event.get("usage")
    total_tokens: int | None = None
    if isinstance(usage, dict):
        token_total = sum(
            v
            for k, v in usage.items()
            if isinstance(v, int) and not isinstance(v, bool) and k.endswith("_tokens")
        )
        total_tokens = token_total or None
    total_cost = _as_float(result_event.get("total_cost_usd"))
    structured: JsonValue = result_event.get("structured_output")
    if structured is None:
        try:
            structured = cast(JsonValue, json.loads(result_text))
        except json.JSONDecodeError as err:
            return CaseResult(
                case=case,
                duration_ms=duration_ms,
                total_tokens=total_tokens,
                total_cost_usd=total_cost,
                structured=None,
                raw_result_text=result_text,
                error=f"no structured_output and result not valid JSON: {err}",
            )
    _ = (case_dir / "structured.json").write_text(
        json.dumps(structured, indent=2) + "\n"
    )
    assertion_results = [evaluate_assertion(structured, a) for a in case.assertions]
    case_result = CaseResult(
        case=case,
        duration_ms=duration_ms,
        total_tokens=total_tokens,
        total_cost_usd=total_cost,
        structured=structured,
        raw_result_text=result_text,
        assertions=assertion_results,
    )
    _ = (case_dir / "assertions.json").write_text(
        json.dumps([_assertion_to_dict(a) for a in assertion_results], indent=2) + "\n"
    )
    return case_result


def _assertion_to_dict(a: AssertionResult) -> JsonObject:
    return {
        "name": a.name,
        "path": a.path,
        "op": a.op,
        "expected": a.expected,
        "actual": a.actual,
        "passed": a.passed,
        "note": a.note,
    }


# ─── Reporting ─────────────────────────────────────────────────────────


def render_benchmark_md(
    skill_name: str, run_dir: Path, results: list[CaseResult], model: str | None
) -> str:
    lines: list[str] = []
    lines.append(f"# Eval results — `{skill_name}`")
    lines.append("")
    lines.append(f"- run: `{run_dir.name}`")
    lines.append(f"- model: `{model or 'default'}`")
    cases_passed = sum(1 for r in results if r.passed)
    total_assertions = sum(len(r.assertions) for r in results)
    passed_assertions = sum(1 for r in results for a in r.assertions if a.passed)
    lines.append(f"- cases: **{cases_passed}/{len(results)}** passed")
    lines.append(f"- assertions: **{passed_assertions}/{total_assertions}** passed")
    total_tokens = sum(r.total_tokens or 0 for r in results)
    total_ms = sum(r.duration_ms or 0 for r in results)
    total_cost = sum(r.total_cost_usd or 0.0 for r in results)
    lines.append(
        f"- tokens: {total_tokens}, time: {total_ms / 1000:.1f}s, cost: ${total_cost:.4f}"
    )
    lines.append("")
    lines.append("| case | passed | assertions | tokens | time |")
    lines.append("|------|--------|------------|--------|------|")
    for r in results:
        a_passed = sum(1 for a in r.assertions if a.passed)
        flag = "✓" if r.passed else "✗"
        lines.append(
            f"| {r.case.name} | {flag} | {a_passed}/{len(r.assertions)} "
            + f"| {r.total_tokens or '?'} | {(r.duration_ms or 0) / 1000:.1f}s |"
        )
    lines.append("")
    for r in results:
        lines.append(f"## {r.case.name}")
        lines.append("")
        if r.error:
            lines.append(f"**error**: `{r.error}`")
            lines.append("")
            continue
        for a in r.assertions:
            mark = "✓" if a.passed else "✗"
            extra = f" — {a.note}" if a.note else ""
            lines.append(
                f"- {mark} **{a.name}** (`{a.op}` on `{a.path or '<root>'}`){extra}"
            )
        lines.append("")
    return "\n".join(lines) + "\n"


def render_benchmark_json(
    skill_name: str, results: list[CaseResult], model: str | None
) -> JsonObject:
    return {
        "skill_name": skill_name,
        "model": model,
        "generated_at": datetime.now(UTC).isoformat(),
        "totals": {
            "cases": len(results),
            "cases_passed": sum(1 for r in results if r.passed),
            "assertions": sum(len(r.assertions) for r in results),
            "assertions_passed": sum(
                1 for r in results for a in r.assertions if a.passed
            ),
            "tokens": sum(r.total_tokens or 0 for r in results),
            "duration_ms": sum(r.duration_ms or 0 for r in results),
            "cost_usd": sum(r.total_cost_usd or 0.0 for r in results),
        },
        "cases": [_case_to_dict(r) for r in results],
    }


def _case_to_dict(r: CaseResult) -> JsonObject:
    return {
        "id": r.case.id,
        "name": r.case.name,
        "passed": r.passed,
        "error": r.error,
        "duration_ms": r.duration_ms,
        "total_tokens": r.total_tokens,
        "total_cost_usd": r.total_cost_usd,
        "assertions": [_assertion_to_dict(a) for a in r.assertions],
    }


# ─── CLI ───────────────────────────────────────────────────────────────


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run skill evals via claude -p with structured output."
    )
    _ = parser.add_argument("skill", help="Skill name (subdir of skills/)")
    _ = parser.add_argument("--limit", type=int, help="Run only the first N cases")
    _ = parser.add_argument("--only", help="Comma-separated case names to run")
    _ = parser.add_argument("--model", help="Model to pass to `claude --model`")
    _ = parser.add_argument(
        "--output-dir",
        type=Path,
        help="Write artifacts to this dir (defaults to evals/runs/<UTC-timestamp>)",
    )
    _ = parser.add_argument("-v", "--verbose", action="store_true")
    return parser.parse_args()


def resolve_skill_dir(name: str) -> Path:
    skill_dir = SKILLS_DIR / name
    if not skill_dir.is_dir():
        raise SystemExit(f"skill not found: {skill_dir}")
    if not (skill_dir / "SKILL.md").is_file():
        raise SystemExit(f"missing SKILL.md: {skill_dir}")
    return skill_dir


@dataclass(frozen=True)
class CliArgs:
    skill: str
    limit: int | None
    only: str | None
    model: str | None
    output_dir: Path | None
    verbose: bool


def _typed_args() -> CliArgs:
    raw = parse_args()
    return CliArgs(
        skill=cast(str, raw.skill),
        limit=cast("int | None", raw.limit),
        only=cast("str | None", raw.only),
        model=cast("str | None", raw.model),
        output_dir=cast("Path | None", raw.output_dir),
        verbose=cast(bool, raw.verbose),
    )


def main() -> int:
    if shutil.which("claude") is None:
        raise SystemExit("`claude` CLI not on PATH")
    args = _typed_args()
    skill_dir = resolve_skill_dir(args.skill)
    evals_path = skill_dir / "evals" / "evals.json"
    if not evals_path.is_file():
        raise SystemExit(f"missing evals: {evals_path}")
    cases = load_evals(evals_path)
    if args.only:
        wanted = {s.strip() for s in args.only.split(",") if s.strip()}
        cases = [c for c in cases if c.name in wanted]
        missing = wanted - {c.name for c in cases}
        if missing:
            raise SystemExit(f"unknown case names: {sorted(missing)}")
    if args.limit is not None:
        cases = cases[: args.limit]
    if not cases:
        raise SystemExit("no cases to run after filtering")
    run_dir = args.output_dir or (
        skill_dir / "evals" / "runs" / datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    )
    run_dir.mkdir(parents=True, exist_ok=True)
    results: list[CaseResult] = []
    for case in cases:
        results.append(
            run_case(
                case=case,
                skill_dir=skill_dir,
                case_dir=run_dir / case.name,
                model=args.model,
                verbose=args.verbose,
            )
        )
    benchmark = render_benchmark_json(args.skill, results, args.model)
    _ = (run_dir / "benchmark.json").write_text(json.dumps(benchmark, indent=2) + "\n")
    md = render_benchmark_md(args.skill, run_dir, results, args.model)
    _ = (run_dir / "benchmark.md").write_text(md)
    print(md)
    print(f"artifacts: {run_dir}")
    return 0 if all(r.passed for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
