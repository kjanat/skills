#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.14"
# dependencies = []
# ///

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal, NotRequired, TypedDict, TypeGuard


class ClaudeUsage(TypedDict):
    input_tokens: NotRequired[int]
    output_tokens: NotRequired[int]
    cache_read_input_tokens: NotRequired[int]
    cache_creation_input_tokens: NotRequired[int]


class AssertionGrade(TypedDict):
    text: str
    passed: bool
    evidence: str


class GradingSummary(TypedDict):
    passed: int
    failed: int
    total: int
    pass_rate: float


class GradingResult(TypedDict):
    assertion_results: list[AssertionGrade]
    summary: GradingSummary


class TriggerDecision(TypedDict):
    should_trigger: bool
    reason: str


@dataclass(frozen=True)
class OutputEval:
    id: int
    prompt: str
    expected_output: str
    assertions: tuple[str, ...]


@dataclass(frozen=True)
class TriggerQuery:
    query: str
    should_trigger: bool


@dataclass(frozen=True)
class ClaudeRun:
    raw_events: list[object]
    result_text: str
    duration_ms: int | None
    total_cost_usd: float | None
    usage: ClaudeUsage
    total_tokens: int | None
    skill_triggered: bool
    skill_base_dirs: tuple[str, ...]


ROOT_DIR = Path(__file__).resolve().parent.parent
EVALS_FILE = ROOT_DIR / "evals" / "evals.json"
TRIGGER_FILE = ROOT_DIR / "evals" / "trigger-queries.json"
RUNS_DIR = ROOT_DIR / "evals" / "runs"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run Twoslash eval prompts through Claude CLI and grade the responses.",
    )
    parser.add_argument(
        "--mode",
        choices=("all", "responses", "triggers"),
        default="all",
        help="Which eval lanes to run.",
    )
    parser.add_argument(
        "--trigger-mode",
        choices=("proxy", "actual"),
        default="proxy",
        help=(
            "How to evaluate triggering. 'proxy' classifies against the skill description. "
            "'actual' tries to observe Claude's Skill tool directly."
        ),
    )
    parser.add_argument("--model", help="Model name passed to `claude --model`.")
    parser.add_argument(
        "--judge-model",
        help="Optional model used for grading. Defaults to --model when omitted.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Only run the first N cases from each selected lane.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Directory for generated eval artifacts. Defaults to evals/runs/<timestamp>.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print progress while evals are running.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    judge_model = args.judge_model or args.model
    run_dir = args.output_dir or default_run_dir()
    run_dir.mkdir(parents=True, exist_ok=True)

    output_evals = load_output_evals(EVALS_FILE)
    trigger_queries = load_trigger_queries(TRIGGER_FILE)

    if args.limit is not None:
        output_evals = output_evals[: args.limit]
        trigger_queries = trigger_queries[: args.limit]

    write_json(
        run_dir / "metadata.json",
        {
            "generated_at": datetime.now(UTC).isoformat(),
            "skill_dir": str(ROOT_DIR),
            "mode": args.mode,
            "trigger_mode": args.trigger_mode,
            "model": args.model,
            "judge_model": judge_model,
            "limit": args.limit,
        },
    )

    response_summary: dict[str, object] | None = None
    trigger_summary: dict[str, object] | None = None

    if args.mode in {"all", "responses"}:
        response_summary = run_response_evals(
            evals=output_evals,
            run_dir=run_dir / "responses",
            model=args.model,
            judge_model=judge_model,
            verbose=args.verbose,
        )

    if args.mode in {"all", "triggers"}:
        trigger_summary = run_trigger_evals(
            queries=trigger_queries,
            run_dir=run_dir / "triggers",
            model=args.model,
            judge_model=judge_model,
            trigger_mode=args.trigger_mode,
            verbose=args.verbose,
        )

    benchmark = {
        "generated_at": datetime.now(UTC).isoformat(),
        "skill_dir": str(ROOT_DIR),
        "mode": args.mode,
        "trigger_mode": args.trigger_mode,
        "model": args.model,
        "judge_model": judge_model,
        "responses": response_summary,
        "triggers": trigger_summary,
    }
    write_json(run_dir / "benchmark.json", benchmark)
    print(json.dumps(benchmark, indent=2))


def default_run_dir() -> Path:
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    return RUNS_DIR / timestamp


def load_output_evals(path: Path) -> list[OutputEval]:
    payload = json.loads(path.read_text())
    evals = payload.get("evals")
    if not isinstance(evals, list):
        raise ValueError(f"Invalid eval file: {path}")
    loaded: list[OutputEval] = []
    for item in evals:
        if not isinstance(item, dict):
            raise ValueError(f"Invalid eval item in {path}: {item!r}")
        assertions = item.get("assertions")
        if not isinstance(assertions, list) or not all(
            isinstance(entry, str) for entry in assertions
        ):
            raise ValueError(f"Invalid assertions in {path}: {item!r}")
        loaded.append(
            OutputEval(
                id=int(item["id"]),
                prompt=str(item["prompt"]),
                expected_output=str(item["expected_output"]),
                assertions=tuple(assertions),
            )
        )
    return loaded


def load_trigger_queries(path: Path) -> list[TriggerQuery]:
    payload = json.loads(path.read_text())
    if not isinstance(payload, list):
        raise ValueError(f"Invalid trigger query file: {path}")
    loaded: list[TriggerQuery] = []
    for item in payload:
        if not isinstance(item, dict):
            raise ValueError(f"Invalid trigger query in {path}: {item!r}")
        loaded.append(
            TriggerQuery(
                query=str(item["query"]),
                should_trigger=bool(item["should_trigger"]),
            )
        )
    return loaded


def run_response_evals(
    *,
    evals: list[OutputEval],
    run_dir: Path,
    model: str | None,
    judge_model: str | None,
    verbose: bool,
) -> dict[str, object]:
    run_dir.mkdir(parents=True, exist_ok=True)
    skill_bundle = build_skill_bundle(ROOT_DIR)
    system_prompt = build_response_system_prompt(skill_bundle)

    case_summaries: list[dict[str, object]] = []
    passed_cases = 0
    total_assertions = 0
    passed_assertions = 0
    total_generation_tokens = 0
    total_generation_duration_ms = 0
    total_judge_tokens = 0
    total_judge_duration_ms = 0

    for eval_case in evals:
        if verbose:
            print(f"[responses] eval {eval_case.id}: generating")
        case_dir = run_dir / f"eval-{eval_case.id}"
        case_dir.mkdir(parents=True, exist_ok=True)
        generation_run = run_claude_json(
            prompt=eval_case.prompt,
            cwd=ROOT_DIR,
            model=model,
            system_prompt=system_prompt,
            json_schema=None,
            allow_skills=False,
        )
        save_claude_run(case_dir / "generation", generation_run)

        if generation_run.total_tokens is not None:
            total_generation_tokens += generation_run.total_tokens
        if generation_run.duration_ms is not None:
            total_generation_duration_ms += generation_run.duration_ms

        if verbose:
            print(f"[responses] eval {eval_case.id}: grading")
        grading_run = run_claude_json(
            prompt=build_grading_prompt(eval_case, generation_run.result_text),
            cwd=ROOT_DIR,
            model=judge_model,
            system_prompt=None,
            json_schema=None,
            allow_skills=False,
        )
        save_claude_run(case_dir / "grading", grading_run)
        grading_result = parse_grading_result(grading_run.result_text)
        write_json(case_dir / "grading.json", grading_result)

        if grading_run.total_tokens is not None:
            total_judge_tokens += grading_run.total_tokens
        if grading_run.duration_ms is not None:
            total_judge_duration_ms += grading_run.duration_ms

        assertion_summary = grading_result["summary"]
        total_assertions += int(assertion_summary["total"])
        passed_assertions += int(assertion_summary["passed"])
        case_passed = int(assertion_summary["failed"]) == 0
        if case_passed:
            passed_cases += 1

        case_summaries.append({
            "id": eval_case.id,
            "passed": case_passed,
            "prompt": eval_case.prompt,
            "generation": {
                "duration_ms": generation_run.duration_ms,
                "total_tokens": generation_run.total_tokens,
                "total_cost_usd": generation_run.total_cost_usd,
            },
            "grading": {
                "duration_ms": grading_run.duration_ms,
                "total_tokens": grading_run.total_tokens,
                "total_cost_usd": grading_run.total_cost_usd,
            },
            "summary": assertion_summary,
        })

    case_total = len(evals)
    return {
        "case_total": case_total,
        "case_passed": passed_cases,
        "case_pass_rate": ratio(passed_cases, case_total),
        "assertion_total": total_assertions,
        "assertion_passed": passed_assertions,
        "assertion_pass_rate": ratio(passed_assertions, total_assertions),
        "generation_total_tokens": total_generation_tokens,
        "generation_total_duration_ms": total_generation_duration_ms,
        "judge_total_tokens": total_judge_tokens,
        "judge_total_duration_ms": total_judge_duration_ms,
        "cases": case_summaries,
    }


def run_trigger_evals(
    *,
    queries: list[TriggerQuery],
    run_dir: Path,
    model: str | None,
    judge_model: str | None,
    trigger_mode: Literal["proxy", "actual"],
    verbose: bool,
) -> dict[str, object]:
    run_dir.mkdir(parents=True, exist_ok=True)
    if trigger_mode == "actual":
        return run_actual_trigger_evals(
            queries=queries,
            run_dir=run_dir,
            model=model,
            verbose=verbose,
        )
    return run_proxy_trigger_evals(
        queries=queries,
        run_dir=run_dir,
        judge_model=judge_model,
        verbose=verbose,
    )


def run_proxy_trigger_evals(
    *,
    queries: list[TriggerQuery],
    run_dir: Path,
    judge_model: str | None,
    verbose: bool,
) -> dict[str, object]:
    description = load_skill_description(ROOT_DIR / "SKILL.md")
    cases: list[dict[str, object]] = []
    passed = 0
    total_tokens = 0
    total_duration_ms = 0

    for index, query in enumerate(queries, start=1):
        if verbose:
            print(f"[triggers/proxy] query {index}: classifying")
        query_dir = run_dir / f"query-{index:02d}"
        query_dir.mkdir(parents=True, exist_ok=True)
        classifier_run = run_claude_json(
            prompt=build_trigger_prompt(description, query.query),
            cwd=ROOT_DIR,
            model=judge_model,
            system_prompt=None,
            json_schema=None,
            allow_skills=False,
        )
        save_claude_run(query_dir / "classification", classifier_run)
        decision = parse_trigger_decision(classifier_run.result_text)
        write_json(query_dir / "classification.json", decision)
        matched = bool(decision["should_trigger"]) is query.should_trigger
        if matched:
            passed += 1
        if classifier_run.total_tokens is not None:
            total_tokens += classifier_run.total_tokens
        if classifier_run.duration_ms is not None:
            total_duration_ms += classifier_run.duration_ms

        cases.append({
            "index": index,
            "query": query.query,
            "expected": query.should_trigger,
            "observed": bool(decision["should_trigger"]),
            "passed": matched,
            "reason": str(decision["reason"]),
            "duration_ms": classifier_run.duration_ms,
            "total_tokens": classifier_run.total_tokens,
        })

    total = len(queries)
    return {
        "mode": "proxy",
        "note": (
            "Proxy mode classifies queries against the repo skill description. "
            "Use this when a globally installed skill with the same name prevents reliable end-to-end trigger checks."
        ),
        "case_total": total,
        "case_passed": passed,
        "case_pass_rate": ratio(passed, total),
        "judge_total_tokens": total_tokens,
        "judge_total_duration_ms": total_duration_ms,
        "cases": cases,
    }


def run_actual_trigger_evals(
    *,
    queries: list[TriggerQuery],
    run_dir: Path,
    model: str | None,
    verbose: bool,
) -> dict[str, object]:
    repo_skill_dir = str(ROOT_DIR)
    cases: list[dict[str, object]] = []
    passed = 0
    total_tokens = 0
    total_duration_ms = 0
    collision_note: str | None = None

    for index, query in enumerate(queries, start=1):
        if verbose:
            print(f"[triggers/actual] query {index}: running")
        query_dir = run_dir / f"query-{index:02d}"
        query_dir.mkdir(parents=True, exist_ok=True)
        actual_run = run_claude_json(
            prompt=query.query,
            cwd=ROOT_DIR,
            model=model,
            system_prompt=None,
            json_schema=None,
            allow_skills=True,
        )
        save_claude_run(query_dir / "actual", actual_run)
        observed = actual_run.skill_triggered
        matched = observed is query.should_trigger

        if (
            actual_run.skill_base_dirs
            and repo_skill_dir not in actual_run.skill_base_dirs
        ):
            collision_note = (
                "Claude loaded a different `twoslash` skill than the repo copy. "
                f"Observed base directories: {', '.join(actual_run.skill_base_dirs)}"
            )
            matched = False

        if matched:
            passed += 1
        if actual_run.total_tokens is not None:
            total_tokens += actual_run.total_tokens
        if actual_run.duration_ms is not None:
            total_duration_ms += actual_run.duration_ms

        cases.append({
            "index": index,
            "query": query.query,
            "expected": query.should_trigger,
            "observed": observed,
            "passed": matched,
            "skill_base_dirs": list(actual_run.skill_base_dirs),
            "duration_ms": actual_run.duration_ms,
            "total_tokens": actual_run.total_tokens,
        })

    total = len(queries)
    return {
        "mode": "actual",
        "note": collision_note
        or "Actual mode checks whether Claude invoked a Skill tool named `twoslash`.",
        "case_total": total,
        "case_passed": passed,
        "case_pass_rate": ratio(passed, total),
        "generation_total_tokens": total_tokens,
        "generation_total_duration_ms": total_duration_ms,
        "cases": cases,
    }


def build_skill_bundle(skill_dir: Path) -> str:
    parts = [
        ("SKILL.md", (skill_dir / "SKILL.md").read_text()),
        (
            "references/notations.md",
            (skill_dir / "references" / "notations.md").read_text(),
        ),
        (
            "references/patterns.md",
            (skill_dir / "references" / "patterns.md").read_text(),
        ),
        (
            "references/source-index.md",
            (skill_dir / "references" / "source-index.md").read_text(),
        ),
    ]
    rendered = []
    for path, text in parts:
        rendered.append(f'<skill-file path="{path}">\n{text.rstrip()}\n</skill-file>')
    return "\n\n".join(rendered)


def build_response_system_prompt(skill_bundle: str) -> str:
    return (
        "You are evaluating a local Agent Skill outside the normal Skill tool loader. "
        "Treat the bundled skill files below as the active Twoslash skill and follow them as authoritative instructions. "
        "Answer the user request directly. Do not mention this harness, test setup, or missing Skill-tool activation.\n\n"
        f"{skill_bundle}"
    )


def build_grading_prompt(eval_case: OutputEval, response_text: str) -> str:
    assertions = "\n".join(f"- {assertion}" for assertion in eval_case.assertions)
    return (
        "Grade this model response against the eval assertions. Be strict. "
        "A PASS requires concrete evidence from the response text itself. "
        "If the response hints at something but does not actually provide it, FAIL the assertion. "
        "Return JSON only with this shape and no surrounding prose: "
        '{"assertion_results":[{"text":"...","passed":true,"evidence":"..."}],"summary":{"passed":0,"failed":0,"total":0,"pass_rate":0.0}}.\n\n'
        f"Eval prompt:\n{eval_case.prompt}\n\n"
        f"Expected output:\n{eval_case.expected_output}\n\n"
        f"Assertions:\n{assertions}\n\n"
        f"Model response:\n{response_text}\n"
    )


def build_trigger_prompt(description: str, query: str) -> str:
    return (
        "Decide whether the `twoslash` skill should trigger for the user query below. "
        "Base the decision primarily on the description field and the skill boundary that plain TypeScript snippets without Twoslash behavior should not trigger it.\n\n"
        'Return JSON only with this shape and no surrounding prose: {"should_trigger":true,"reason":"..."}.\n\n'
        "Skill name: twoslash\n"
        f"Skill description: {description}\n\n"
        f"User query: {query}\n"
    )


def load_skill_description(skill_md_path: Path) -> str:
    text = skill_md_path.read_text()
    match = re.search(r"^description:\s*(.+)$", text, flags=re.MULTILINE)
    if match is None:
        raise ValueError(f"Could not find description in {skill_md_path}")
    return match.group(1).strip().strip('"').strip("'")


def run_claude_json(
    *,
    prompt: str,
    cwd: Path,
    model: str | None,
    system_prompt: str | None,
    json_schema: dict[str, object] | None,
    allow_skills: bool,
) -> ClaudeRun:
    command = [
        "claude",
        "-p",
        "--output-format",
        "json",
        "--permission-mode",
        "bypassPermissions",
        "--no-session-persistence",
    ]
    if not allow_skills:
        command.append("--disable-slash-commands")
    if model is not None:
        command.extend(["--model", model])
    if system_prompt is not None:
        command.extend(["--system-prompt", system_prompt])
    if json_schema is not None:
        command.extend(["--json-schema", json.dumps(json_schema)])
    command.append(prompt)

    completed = subprocess.run(
        command,
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"Claude command failed with exit code {completed.returncode}\nSTDOUT:\n{completed.stdout}\nSTDERR:\n{completed.stderr}"
        )

    try:
        raw_events = json.loads(completed.stdout)
    except json.JSONDecodeError as error:
        raise RuntimeError(
            f"Could not parse Claude JSON output:\n{completed.stdout}"
        ) from error

    if not isinstance(raw_events, list):
        raise RuntimeError(f"Claude output was not a JSON array: {raw_events!r}")

    result_event = find_result_event(raw_events)
    usage = result_event.get("usage")
    typed_usage = coerce_usage(usage)
    skill_base_dirs = tuple(extract_skill_base_dirs(raw_events))

    return ClaudeRun(
        raw_events=raw_events,
        result_text=str(result_event.get("result", "")),
        duration_ms=coerce_optional_int(result_event.get("duration_ms")),
        total_cost_usd=coerce_optional_float(result_event.get("total_cost_usd")),
        usage=typed_usage,
        total_tokens=compute_total_tokens(typed_usage),
        skill_triggered=detect_skill_trigger(raw_events, "twoslash"),
        skill_base_dirs=skill_base_dirs,
    )


def find_result_event(raw_events: list[object]) -> dict[str, object]:
    for event in raw_events:
        if is_string_object_dict(event) and event.get("type") == "result":
            return event
    raise RuntimeError(f"Claude output did not include a result event: {raw_events!r}")


def detect_skill_trigger(raw_events: list[object], skill_name: str) -> bool:
    for event in raw_events:
        if not is_string_object_dict(event) or event.get("type") != "assistant":
            continue
        message = event.get("message")
        if not is_string_object_dict(message):
            continue
        content = message.get("content")
        if not isinstance(content, list):
            continue
        for chunk in content:
            if not is_string_object_dict(chunk):
                continue
            if chunk.get("type") != "tool_use":
                continue
            if chunk.get("name") != "Skill":
                continue
            tool_input = chunk.get("input")
            if (
                is_string_object_dict(tool_input)
                and tool_input.get("skill") == skill_name
            ):
                return True
    return False


def extract_skill_base_dirs(raw_events: list[object]) -> list[str]:
    paths: list[str] = []
    pattern = re.compile(r"Base directory for this skill:\s*(.+)")
    for event in raw_events:
        if not is_string_object_dict(event) or event.get("type") != "user":
            continue
        message = event.get("message")
        if not is_string_object_dict(message):
            continue
        content = message.get("content")
        if not isinstance(content, list):
            continue
        for chunk in content:
            if not is_string_object_dict(chunk) or chunk.get("type") != "text":
                continue
            text = chunk.get("text")
            if not isinstance(text, str):
                continue
            match = pattern.search(text)
            if match is not None:
                paths.append(match.group(1).strip())
    return paths


def parse_grading_result(result_text: str) -> GradingResult:
    try:
        payload = extract_json_payload(result_text)
    except json.JSONDecodeError as error:
        raise RuntimeError(
            f"Claude schema result was not valid JSON:\n{result_text}"
        ) from error
    if not is_string_object_dict(payload):
        raise RuntimeError(f"Claude grading result had unexpected type: {payload!r}")

    assertion_results = payload.get("assertion_results")
    summary = payload.get("summary")
    if not isinstance(assertion_results, list) or not is_string_object_dict(summary):
        raise RuntimeError(
            f"Claude grading result was missing expected keys: {payload!r}"
        )

    validated_assertions: list[AssertionGrade] = []
    for item in assertion_results:
        if not is_string_object_dict(item):
            raise RuntimeError(
                f"Claude grading assertion had unexpected type: {item!r}"
            )

        text = item.get("text")
        passed = item.get("passed")
        evidence = item.get("evidence")
        if (
            not isinstance(text, str)
            or not isinstance(passed, bool)
            or not isinstance(evidence, str)
        ):
            raise RuntimeError(f"Claude grading assertion was invalid: {item!r}")

        validated_assertions.append(
            AssertionGrade(text=text, passed=passed, evidence=evidence)
        )

    passed_count = summary.get("passed")
    failed_count = summary.get("failed")
    total_count = summary.get("total")
    pass_rate = summary.get("pass_rate")
    if (
        not isinstance(passed_count, int)
        or not isinstance(failed_count, int)
        or not isinstance(total_count, int)
        or not isinstance(pass_rate, int | float)
    ):
        raise RuntimeError(f"Claude grading summary was invalid: {summary!r}")

    validated_summary = GradingSummary(
        passed=passed_count,
        failed=failed_count,
        total=total_count,
        pass_rate=float(pass_rate),
    )
    return GradingResult(
        assertion_results=validated_assertions,
        summary=validated_summary,
    )


def parse_trigger_decision(result_text: str) -> TriggerDecision:
    try:
        payload = extract_json_payload(result_text)
    except json.JSONDecodeError as error:
        raise RuntimeError(
            f"Claude schema result was not valid JSON:\n{result_text}"
        ) from error
    if not is_string_object_dict(payload):
        raise RuntimeError(f"Claude trigger decision had unexpected type: {payload!r}")

    should_trigger = payload.get("should_trigger")
    reason = payload.get("reason")
    if not isinstance(should_trigger, bool) or not isinstance(reason, str):
        raise RuntimeError(f"Claude trigger decision was invalid: {payload!r}")

    return TriggerDecision(should_trigger=should_trigger, reason=reason)


def compute_total_tokens(usage: ClaudeUsage) -> int | None:
    token_keys = (
        "input_tokens",
        "output_tokens",
        "cache_read_input_tokens",
        "cache_creation_input_tokens",
    )
    values: list[int] = []
    for key in token_keys:
        value = usage.get(key)
        if isinstance(value, int):
            values.append(value)
    if not values:
        return None
    return sum(values)


def coerce_usage(value: object) -> ClaudeUsage:
    if not is_string_object_dict(value):
        return ClaudeUsage()

    usage = ClaudeUsage()
    for key in (
        "input_tokens",
        "output_tokens",
        "cache_read_input_tokens",
        "cache_creation_input_tokens",
    ):
        item = value.get(key)
        if isinstance(item, int):
            usage[key] = item
    return usage


def is_string_object_dict(value: object) -> TypeGuard[dict[str, object]]:
    return isinstance(value, dict) and all(isinstance(key, str) for key in value)


def extract_json_payload(result_text: str) -> object:
    stripped = result_text.strip()
    if stripped.startswith("```"):
        fenced_match = re.search(
            r"```(?:json)?\s*(\{.*\})\s*```", stripped, flags=re.DOTALL
        )
        if fenced_match is not None:
            return json.loads(fenced_match.group(1))

    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        start = stripped.find("{")
        end = stripped.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise
        return json.loads(stripped[start : end + 1])


def save_claude_run(base_path: Path, run: ClaudeRun) -> None:
    base_path.parent.mkdir(parents=True, exist_ok=True)
    write_json(base_path.with_suffix(".json"), run.raw_events)
    base_path.with_suffix(".txt").write_text(run.result_text)
    write_json(
        base_path.with_name(base_path.name + "-timing.json"),
        {
            "duration_ms": run.duration_ms,
            "total_cost_usd": run.total_cost_usd,
            "total_tokens": run.total_tokens,
            "usage": run.usage,
            "skill_triggered": run.skill_triggered,
            "skill_base_dirs": list(run.skill_base_dirs),
        },
    )


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n")


def ratio(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return numerator / denominator


def coerce_optional_int(value: object) -> int | None:
    return value if isinstance(value, int) else None


def coerce_optional_float(value: object) -> float | None:
    return value if isinstance(value, int | float) else None


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
