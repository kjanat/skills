# Skill Eval Harness

Repo-level runner that drives `claude -p --output-format json --json-schema ...`
against each case in a skill's `evals/evals.json`, then mechanically checks
assertions against the structured response. No LLM grading; no agent
self-reporting.

## Usage

```sh
uv sync                       # one-time: installs the `run-eval` entry point
uv run run-eval <skill-name>
uv run run-eval github-script --verbose
uv run run-eval twoslash --only case-a,case-b --model sonnet
```

Artifacts land in `skills/<skill>/evals/runs/<UTC-timestamp>/`:

- `benchmark.md` / `benchmark.json` — summary
- `<case>/raw.json` — full claude `--output-format json` event stream
- `<case>/result.txt` — extracted result text
- `<case>/structured.json` — parsed structured response (validated against `json_schema`)
- `<case>/assertions.json` — per-assertion pass/fail with evidence

Add `evals/runs/` to the skill's local `.gitignore` (already done for
github-script and twoslash).

## `evals.json` schema

A meta-schema lives at `scripts/eval/schema.json`. Reference it from each
skill's eval file so editors / CI validate the structure:

```json
{
    "$schema": "../../../scripts/eval/schema.json",
    "skill_name": "<name>",
    "evals": [...]
}
```

The runner validates each case's `json_schema` field as a real JSON Schema
(Draft 2020-12) at load time, and validates the agent's structured response
against that schema after every run — schema violations surface as failed
assertions in `benchmark.md`. The `$schema` reference also lights up
editor / CI validation while authoring `evals.json`.

```json
{
  "skill_name": "<must-match-frontmatter>",
  "evals": [
    {
      "id": 1,
      "name": "case-slug",
      "prompt": "User-facing task prompt.",
      "system_prompt": "(optional) overrides default skill-pointing prompt.",
      "json_schema": { "type": "object", "properties": { ... }, "required": [ ... ] },
      "assertions": [
        {"name": "human label", "path": "workflow_yaml", "op": "contains", "value": "actions/github-script@v9"}
      ]
    }
  ]
}
```

Default system prompt points the agent at `<skill_dir>/SKILL.md` and the
referenced files, then asks for JSON matching `json_schema`. Override via
`system_prompt` on a per-case basis if needed.

## Assertion ops

| op             | semantics                                |
| -------------- | ---------------------------------------- |
| `equals`       | strict `==`                              |
| `not_equals`   | strict `!=`                              |
| `contains`     | substring (string) or membership (list)  |
| `not_contains` | inverse of above                         |
| `matches`      | `re.search(value, actual)` finds a match |
| `not_matches`  | inverse of above                         |
| `truthy`       | `bool(actual)` is true                   |
| `falsy`        | `bool(actual)` is false                  |
| `length_gte`   | `len(actual) >= value`                   |
| `length_lte`   | `len(actual) <= value`                   |

`path` is dotted access into the structured response. Integer segments are
list indices: `change_notes.0`, `tags.2.name`. Empty path (`""`) targets the
root object.

## Why mechanical assertions

The agent fills `workflow_yaml` (or whatever the deliverable is) and the
harness regex-checks the artifact directly. Self-report fields like
"uses_v9: true" are not trusted — anything verifiable from the deliverable
text is checked there instead.

## Exit code

`0` if every assertion in every case passes. `1` otherwise. Suitable for CI.
