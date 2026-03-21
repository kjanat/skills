# Source Index

Canonical sources for this skill.

## Freshness

- Guidance is pinned to commit `ebb4f7e28ee4db71d19109656cba80fb10eabe2c`.
- It is only as up to date as that commit SHA.

## Source set

- Site: `https://threlte.xyz/`
- Repo root: `https://github.com/threlte/threlte`
- Docs app at commit:
  - `https://github.com/threlte/threlte/tree/ebb4f7e28ee4db71d19109656cba80fb10eabe2c/apps/docs`
- Docs content root at commit:
  - `https://github.com/threlte/threlte/tree/ebb4f7e28ee4db71d19109656cba80fb10eabe2c/apps/docs/src/content`

## Schema anchors

- Collections/categories schema:
  - `apps/docs/src/content.config.ts`
- Sidebar package order and navigation behavior:
  - `apps/docs/src/components/Menu/LeftSidebar/getLeftSidebarMenu.ts`
  - `apps/docs/src/layouts/DocsLayout.astro`

## Package order used in docs

1. `@threlte/core`
2. `@threlte/extras`
3. `@threlte/gltf`
4. `@threlte/rapier`
5. `@threlte/theatre`
6. `@threlte/xr`
7. `@threlte/flex`
8. `@threlte/studio`
9. `Documentation`

## Recency handling rule

When user asks about new APIs, migration changes, or "latest" behavior:

1. Answer with commit-pinned guidance first.
2. State recency limit explicitly.
3. Recommend checking latest docs/repo history.

## Mirror maintenance

- Mirrored example root: `skills/threlte/examples/`
- Keep workflow links pointing to paths that exist in that mirror.
