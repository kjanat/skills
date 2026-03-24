# Source Index

Canonical sources and version pins for vendored content.

## Provenance

| Source                                              | Ref    | Resolved       | Date       |
| --------------------------------------------------- | ------ | -------------- | ---------- |
| [statelyai/docs](https://github.com/statelyai/docs) | `main` | `a8fa2d9588b7` | 2026-03-23 |
| [xstate npm](https://www.npmjs.com/package/xstate)  | `5`    | `5.28.0`       | 2026-03-23 |

## External references (not vendored)

- [jsdocs.io/package/xstate](https://www.jsdocs.io/package/xstate) — rendered API browser
- [stately.ai/docs](https://stately.ai/docs) — official docs site

## Re-sync

```bash
# Update to latest
bash scripts/sync-docs.sh

# Pin specific versions
bash scripts/sync-docs.sh --xstate-version 5.28.0 --docs-ref a8fa2d9588b7
```

## Vendored layout

- `docs/` — narrative MDX from statelyai/docs (112 files)
- `api/` — TypeScript declarations from xstate npm (58 .d.ts files)
- `api/package.json` — package exports map

## Freshness rule

Guidance is pinned to versions above. When user asks about newer APIs:

1. Answer with pinned guidance first
2. State version limit
3. Recommend checking latest docs
