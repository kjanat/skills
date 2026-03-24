# PROJECT KNOWLEDGE BASE

Collection of [Agent Skills](https://agentskills.io/) for AI coding agents.
Pure content repo — no build system, no CI, no runtime code.

## STRUCTURE

```tree
skills/
├── build-skill/             # Meta-skill: how to author new skills
│   ├── SKILL.md
│   ├── references/          # 7 deep-dive docs (anatomy, frontmatter, patterns, etc.)
│   └── scripts/             # init, validate, package shell scripts
├── changelog-writing/       # Keep a Changelog convention
│   ├── SKILL.md
│   └── references/          # example.md
├── github-docker-action/    # Docker container GitHub Actions
│   ├── SKILL.md
│   └── references/          # Dockerfile, action.yml, entrypoint, testing
├── github-script/           # actions/github-script@v8 workflows
│   ├── SKILL.md
│   ├── references/          # examples, security, external files, runtime
│   └── assets/              # reusable workflow YAMLs, ESM scripts, tsconfig
├── github-service-containers/ # Docker sidecar services in CI
│   ├── SKILL.md
│   └── references/          # postgres, redis
├── index-knowledge/         # Generate AGENTS.md knowledge bases
│   └── SKILL.md
├── uv-versioning/           # uv version bump workflows
│   └── SKILL.md
└── xstate/                  # XState v5 state machines + actors
    ├── SKILL.md
    ├── references/          # cheatsheet, routing-map, gotchas, source-index
    ├── scripts/             # sync-docs.sh (vendor docs + API types)
    ├── docs/                # vendored MDX from statelyai/docs (~112 files)
    └── api/                 # vendored .d.ts from xstate npm (~58 files)
```

## WHERE TO LOOK

| Task                     | Location                                |
| ------------------------ | --------------------------------------- |
| Add a new skill          | `build-skill/` (read FIRST)             |
| Validate a skill         | `build-skill/scripts/validate_skill.sh` |
| Scaffold a skill         | `build-skill/scripts/init_skill.sh`     |
| Package for distribution | `build-skill/scripts/package_skill.sh`  |
| Understand skill anatomy | `build-skill/references/anatomy.md`     |
| Frontmatter spec         | `build-skill/references/frontmatter.md` |

## SKILL ANATOMY

Every skill follows this convention (defined by `build-skill`):

- **`SKILL.md`** — entry point, YAML frontmatter + instructions. Target ~200 lines, max 500.
- **`references/`** — deep-dive markdown docs, loaded on demand. Target ~150 lines, max 200.
- **`scripts/`** — executable code the agent runs (shell, JS).
- **`assets/`** — output files (templates, configs). Not loaded into context.

### Frontmatter requirements

```yaml
---
name: skill-name          # must match directory, ^[a-z0-9]+(-[a-z0-9]+)*$
description: >-           # what it does + when to use ("Use when...")
  ...
license: MIT              # optional but conventional here
metadata:                 # optional but conventional here
  author: kjanat
  version: "1.0"
---
```

### Content conventions

- "Reading Order" table maps tasks to files (progressive disclosure)
- "In This Reference" table links all bundled reference files
- Cross-skill references use callout blocks (see `github-docker-action` <-> `github-service-containers`)
- Description uses third person ("Processes X" not "I process X")

## ANTI-PATTERNS

- **Expression injection**: NEVER inline `${{ }}` in `script:` body (`github-script`). Use `env:` boundary.
- **Content duplication**: link to references, don't copy content into SKILL.md.
- **Verbose skills**: telegraphic style. Overflow goes to `references/`.
- **Dead references**: remove any reference file not accessed by SKILL.md.
- **Unpinned images**: never use `:latest` tags in Dockerfiles (`github-docker-action`).
- **Generic advice**: skills contain only project-specific knowledge, not universal truths.

## CROSS-SKILL RELATIONSHIPS

```txt
build-skill ──────> (all skills follow its conventions)
github-docker-action <──> github-service-containers (mutual cross-refs)
```

## MAINTENANCE

```bash
# Project-level maintenance (root script)
./scripts/maintain.sh                       # sync + validate + status
./scripts/maintain.sh sync                  # sync all vendored skills
./scripts/maintain.sh sync xstate           # sync one skill
./scripts/maintain.sh sync xstate --dry-run # preview what would change
./scripts/maintain.sh validate              # validate all skills
./scripts/maintain.sh validate xstate       # validate one skill
./scripts/maintain.sh status                # show vendored content freshness
```

```bash
# Per-skill scripts (from build-skill)
bash skills/build-skill/scripts/validate_skill.sh skills/<skill-name>
bash skills/build-skill/scripts/package_skill.sh skills/<skill-name>
bash skills/build-skill/scripts/init_skill.sh <skill-name> [standard|minimal|reference-heavy|script-heavy]
```

## NOTES

- All skills authored by `kjanat`, all at version `1.0`, MIT licensed
- `index-knowledge` SKILL.md is 366 lines — exceeds the 200-line guideline; should split to references
- `build-skill` and `index-knowledge` lack `license`/`metadata` frontmatter fields
- `github-script/assets/` is the only skill using the assets directory
- `xstate` vendors external content via `sync-docs.sh` — first skill with auto-vendoring pattern
- No `.gitignore`, no CI, no linting config at repo level — intentionally pure content
