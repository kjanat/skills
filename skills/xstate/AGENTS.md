# XSTATE KNOWLEDGE BASE

Vendored XState v5 docs + API declarations with script-based refresh workflow.

## STRUCTURE

```tree
xstate/
├── SKILL.md
├── references/                 # cheatsheet, routing-map, gotchas, source-index
├── scripts/
│   └── sync-docs.sh
├── docs/                       # vendored narrative MDX
└── api/                        # vendored TypeScript declarations
```

## WHERE TO LOOK

| Task                        | Location                                      | Notes                      |
| --------------------------- | --------------------------------------------- | -------------------------- |
| Quick syntax answer         | `references/cheatsheet.md`                    | Fastest v5 lookup          |
| Topic -> doc path routing   | `references/routing-map.md`                   | Use before freeform search |
| v4->v5 pitfalls             | `references/gotchas.md`, `docs/migration.mdx` | Migration lane             |
| API type signatures         | `api/dist/declarations/src/*.d.ts`            | Source for exact types     |
| Refresh vendored docs/types | `scripts/sync-docs.sh`                        | Rebuild corpus             |

## LOCAL CONVENTIONS

- Default to v5 idioms (`setup(...).createMachine(...)`).
- Prefer references for routing, docs for explanation, api for exact signatures.
- Keep version-freshness caveat when behavior may differ upstream.

## ANTI-PATTERNS

- Do not mix v4 patterns into default examples.
- Do not treat vendored files as hand-authored content.
- Do not skip `references/source-index.md` when provenance matters.
