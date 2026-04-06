# Twoslash Evals

This skill ships with a small regression harness for response quality and trigger checks.

## Files

- `evals.json` holds output-quality prompts plus assertion lists.
- `trigger-queries.json` holds should-trigger and should-not-trigger queries.
- `runs/` stores generated artifacts from each run. It is gitignored.

## Run the harness

From the repo root:

```bash
uv run skills/twoslash/scripts/run-evals.py
```

Useful flags:

```bash
uv run skills/twoslash/scripts/run-evals.py --mode responses
uv run skills/twoslash/scripts/run-evals.py --mode triggers --trigger-mode proxy
uv run skills/twoslash/scripts/run-evals.py --model claude-sonnet-4-6 --judge-model claude-sonnet-4-6
uv run skills/twoslash/scripts/run-evals.py --limit 1 --verbose
```

## Output layout

Each run writes to `evals/runs/<timestamp>/`.

- `metadata.json` captures the config for the run.
- `benchmark.json` aggregates response and trigger results.
- `responses/eval-*/` stores raw Claude output, extracted text, timing, and grading.
- `triggers/query-*/` stores raw trigger classification results.

## Trigger modes

- `proxy` is the default. It classifies queries against the repo skill description and boundaries.
- `actual` tries to observe Claude's `Skill` tool directly.

Use `proxy` by default. In this environment, Claude already has a global `twoslash` skill installed under `~/.claude/skills/twoslash`, so true end-to-end trigger checks can collide with the global copy instead of the repo skill.

## How response evals work

The response lane runs Claude with slash commands disabled, then injects the repo skill files through the system prompt. That avoids the global-skill name collision and lets you grade the repo skill content directly.

The grading lane uses the assertions from `evals.json` and asks Claude for structured PASS/FAIL judgments with evidence.
