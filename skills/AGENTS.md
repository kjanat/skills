# SKILLS KNOWLEDGE BASE

Generated: 2026-03-26 Parent: `../AGENTS.md`

All installable skills live here. Use this file to pick the right skill fast,
then read that skill's `SKILL.md` and local `AGENTS.md` (if present).

## SKILL INDEX

| Skill                       | Focus                                | Local AGENTS |
| --------------------------- | ------------------------------------ | ------------ |
| `build-skill`               | authoring/validation meta-skill      | yes          |
| `changelog-writing`         | Keep a Changelog edits               | no           |
| `commit`                    | safe commit workflow                 | no           |
| `ezelsbruggen-schrijven`    | Dutch mnemonics and recall hooks     | no           |
| `github-docker-action`      | Docker container actions             | no           |
| `github-script`             | secure `actions/github-script` usage | yes          |
| `github-service-containers` | CI sidecar services                  | no           |
| `index-knowledge`           | generate hierarchical AGENTS docs    | no           |
| `lightning`                 | lightning physics reference corpus   | yes          |
| `threlte`                   | Threlte docs routing and examples    | yes          |
| `uv-versioning`             | uv version bump planning             | no           |
| `xstate`                    | XState v5 docs + API types           | yes          |
| `zod`                       | Zod v4 docs routing + API guidance   | yes          |

## HOW TO ROUTE

- Building or modifying skills: start at `build-skill/SKILL.md`.
- Dutch mnemonics or recall hooks: use `ezelsbruggen-schrijven/SKILL.md`.
- GitHub Actions inline JS: use `github-script/SKILL.md`.
- Vendored docs lookup: prefer `threlte`, `xstate`, or `zod` skill lanes.
- Domain science question (lightning): use `lightning/SKILL.md`.
- Repo maintenance: use `../scripts/maintain.sh`.

## SHARED CONVENTIONS

- Every skill has `SKILL.md`; most keep deep detail in `references/`.
- Vendored skills (`threlte`, `xstate`, `zod`) sync from upstream via `scripts/sync-docs.sh`.
- Do not hand-edit vendored content when a sync script exists.
- Keep guidance specific; avoid generic coding advice in skill docs.

## MAINTENANCE

```bash
./scripts/maintain.sh validate
./scripts/maintain.sh sync
./scripts/maintain.sh status
```

## SUBTREE HIERARCHY

```txt
skills/AGENTS.md
├── skills/build-skill/AGENTS.md
├── skills/github-script/AGENTS.md
├── skills/lightning/AGENTS.md
├── skills/threlte/AGENTS.md
├── skills/xstate/AGENTS.md
└── skills/zod/AGENTS.md
```
