# ZOD KNOWLEDGE BASE

Vendored Zod v4 routing skill with package-selection guidance and sync scripts.

## STRUCTURE

```tree
zod/
├── SKILL.md
├── references/                 # routing-map, gotchas, package-cheatsheet, source-index
├── scripts/
│   └── sync-docs.sh
└── docs/                       # vendored Zod docs (including v4 subtree)
```

## WHERE TO LOOK

| Task                  | Location                           | Notes                                |
| --------------------- | ---------------------------------- | ------------------------------------ |
| Topic routing         | `references/routing-map.md`        | Canonical topic map                  |
| Package choice        | `references/package-cheatsheet.md` | `zod` vs `zod/mini` vs `zod/v4/core` |
| Migration pitfalls    | `references/gotchas.md`            | Deprecated/avoid list                |
| Current API details   | `docs/api.mdx`, `docs/basics.mdx`  | Default answer sources               |
| Refresh vendored docs | `scripts/sync-docs.sh`             | Regenerates routing/provenance       |

## LOCAL CONVENTIONS

- Prefer root import examples: `import * as z from 'zod'`.
- Treat `zod/v4/core` as library-author lane, not app default.
- Keep migration answers explicit about deprecated Zod 3-era APIs.

## ANTI-PATTERNS

- Do not default to legacy error APIs (`message`, `errorMap`, etc.).
- Do not suggest sync parsing where async schema behavior is present.
- Do not hand-edit vendored docs when sync script governs content.
