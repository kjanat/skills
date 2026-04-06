# TWOSLASH KNOWLEDGE BASE

Twoslash authoring skill plus a local eval harness for response-quality and trigger checks.

## STRUCTURE

```tree
twoslash/
├── AGENTS.md
├── SKILL.md
├── example-docs.txt           # local gitingest snapshot of upstream docs
├── references/               # notations, authoring patterns, provenance
├── evals/                    # eval prompts, trigger queries, run docs
│   ├── README.md
│   ├── evals.json
│   ├── trigger-queries.json
│   └── runs/                 # generated eval artifacts; gitignored
└── scripts/
    ├── inspect-markers.py     # prints real line/column counts for Twoslash markers
    └── run-evals.py           # uv-run Python harness for response + trigger evals
```

## WHERE TO LOOK

| Task                         | Location                                | Notes                                            |
| ---------------------------- | --------------------------------------- | ------------------------------------------------ |
| Pick directives or flags     | `references/notations.md`               | Canonical notation map                           |
| Grab a copy-paste example    | `references/examples.md`                | Fast path for common snippet shapes              |
| Hide setup or shape snippets | `references/patterns.md`                | Default authoring patterns                       |
| Sweep upstream docs quickly  | `example-docs.txt`                      | Wide local snapshot, not canonical source        |
| Count marker columns         | `scripts/inspect-markers.py`            | Use this instead of guessing spaces              |
| Check provenance             | `references/source-index.md`            | Upstream refs and source file pointers           |
| Run evals                    | `evals/README.md`                       | CLI usage and output layout                      |
| Inspect benchmark results    | `evals/runs/<timestamp>/benchmark.json` | Aggregate pass rates and token/time totals       |
| Inspect one case deeply      | `evals/runs/<timestamp>/*/`             | Raw Claude JSON, extracted text, timing, grading |

## LOCAL CONVENTIONS

- Use `uv run scripts/run-evals.py` for Python harness execution.
- Use `uv run scripts/inspect-markers.py <file>` to inspect `^?`, `^|`, and `^^^` columns. Do not guess marker spacing.
- Treat `example-docs.txt` as a convenience snapshot for broad exploration, not the canonical source of truth.
- Keep generated artifacts under `evals/runs/`; do not write temp eval output elsewhere.
- Default trigger checks to `proxy` mode. In this environment, `actual` mode can miss or collide because Claude already has a globally installed `twoslash` skill.
- Response evals inject the repo skill files through the system prompt so the harness tests this repo copy, not the global skill.
- Keep eval prompts realistic and concrete. Prefer actual snippet rewrites over vague meta-prompts.

## ANTI-PATTERNS

- Do not rely on `actual` trigger mode as the primary quality gate in this repo.
- Do not treat generated `evals/runs/` artifacts as source content.
- Do not add generic TypeScript eval prompts that do not require Twoslash behavior.
