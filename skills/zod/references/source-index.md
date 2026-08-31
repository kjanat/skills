# Source Index

Canonical sources and version pins for vendored content.

## Provenance

| Source                                              | Ref    | Resolved       | Sync date  |
| --------------------------------------------------- | ------ | -------------- | ---------- |
| [colinhacks/zod](https://github.com/colinhacks/zod) | `main` | `b801439b5fb1` | 2026-08-31 |

## Vendored subtree

- Upstream path: `packages/docs/content`
- Included: `.md` and `.mdx` files under that subtree
- Excluded: `content/blog/`, docs site app/components/pages/public assets, and build config

## Refresh

```bash
bash skills/zod/scripts/sync-docs.sh --ref main
bash skills/zod/scripts/sync-docs.sh --ref c7805073fef5b6b8857307c3d4b3597a70613bc2
```
