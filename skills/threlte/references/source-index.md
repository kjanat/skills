# Source Index

Canonical sources and version pins for vendored content.

## Provenance

| Source                                                | Ref    | Resolved       | Date       |
| ----------------------------------------------------- | ------ | -------------- | ---------- |
| [threlte/threlte](https://github.com/threlte/threlte) | `main` | `8e7aa269ab32` | 2026-07-06 |

## External references (not vendored)

- [threlte.xyz](https://threlte.xyz/) — official docs site
- [GitHub repo](https://github.com/threlte/threlte) — source code

## Re-sync

```bash
# Update to latest
bash scripts/sync-docs.sh

# Pin specific commit
bash scripts/sync-docs.sh --ref 8e7aa269ab32
```

## Vendored layout

- `docs/` — narrative MDX from apps/docs/src/content/ (246 files)
- `examples/` — Svelte example components from apps/docs/src/examples/ (612 files)

## Package order (from docs navigation)

1. `@threlte/core`
2. `@threlte/extras`
3. `@threlte/gltf`
4. `@threlte/rapier`
5. `@threlte/theatre`
6. `@threlte/xr`
7. `@threlte/flex`
8. `@threlte/studio`

## Freshness rule

Guidance is pinned to versions above. When user asks about newer APIs:

1. Answer with pinned guidance first
2. State version limit
3. Recommend checking latest docs
