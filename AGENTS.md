# PROJECT KNOWLEDGE BASE

Generated: 2026-03-26 Commit: `19c66b6` Branch: `master`

Collection of [Agent Skills](https://agentskills.io/). Content repo only: docs,
references, and maintenance scripts.

## OVERVIEW

- Primary payload under `skills/`; each subdir is one installable skill.
- No runtime app here. Work is content curation, routing maps, vendored docs, and validation.
- Read `skills/AGENTS.md` before changing any skill.

## STRUCTURE

```tree
skills/     # Root of all skill content (repo root)
├── AGENTS.md
├── README.md
├── scripts/
│   └── maintain.sh
└── skills/
    ├── AGENTS.md
    ├── build-skill/
    ├── changelog-writing/
    ├── commit/
    ├── github-docker-action/
    ├── github-script/
    ├── github-service-containers/
    ├── index-knowledge/
    ├── lightning/
    ├── threlte/
    ├── twoslash/
    ├── uv-versioning/
    ├── xstate/
    └── zod/
```

## WHERE TO LOOK

| Task                   | Location                                       | Notes                                  |
| ---------------------- | ---------------------------------------------- | -------------------------------------- |
| Route to a skill       | `skills/AGENTS.md`                             | Canonical skill index and boundaries   |
| Add or edit any skill  | `skills/build-skill/AGENTS.md`                 | Meta-rules and validator workflow      |
| Run Twoslash evals     | `skills/twoslash/AGENTS.md`                    | Harness, trigger modes, output layout  |
| Run maintenance all-up | `scripts/maintain.sh`                          | `sync`, `validate`, `status`           |
| Validate one skill     | `skills/build-skill/scripts/validate_skill.sh` | Structural checks                      |
| Refresh vendored docs  | `scripts/maintain.sh sync <skill>`             | Uses each skill `scripts/sync-docs.sh` |

## CONVENTIONS

- Skill dirs: `SKILL.md` entrypoint, optional `references/`, `scripts/`, `assets/`.
- Keep `SKILL.md` concise; push depth to `references/`.
- Child AGENTS files own local rules; avoid duplicating parent guidance.
- Eval harnesses should write generated artifacts under skill-local ignored paths, not the repo root.
- Prefer deterministic sync scripts for vendored content (`xstate`, `threlte`, `zod`).

## ANTI-PATTERNS (THIS PROJECT)

- Never inline `${{ ... }}` inside `github-script` `script:` bodies; use `env` boundary.
- Never use Docker image `:latest` in docker-action examples.
- Do not duplicate long reference content in `SKILL.md`.
- Do not edit vendored docs/api manually when a sync script is the source of truth.

## COMMANDS

```bash
./scripts/maintain.sh
./scripts/maintain.sh sync
./scripts/maintain.sh sync xstate --dry-run
./scripts/maintain.sh validate
./scripts/maintain.sh status
```

## HIERARCHY

```txt
./AGENTS.md
└── ./skills/AGENTS.md
    ├── ./skills/build-skill/AGENTS.md
    ├── ./skills/github-script/AGENTS.md
    ├── ./skills/lightning/AGENTS.md
    ├── ./skills/threlte/AGENTS.md
    ├── ./skills/twoslash/AGENTS.md
    ├── ./skills/xstate/AGENTS.md
    └── ./skills/zod/AGENTS.md
```
