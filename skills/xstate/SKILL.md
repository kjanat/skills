---
name: xstate
description: Routes XState v5 questions to vendored docs, API types, and practical patterns. Use when helping with state machines, actors, statecharts, setup/createMachine, invoked/spawned actors, or migrating from v4.
license: MIT
metadata:
  author: kjanat
  version: "1.0"
---

# XState v5

State management and orchestration via actors and state machines.

## Scope and freshness

- Vendored sources pinned to specific versions (see `references/source-index.md`)
- `docs/` — narrative MDX from [statelyai/docs](https://github.com/statelyai/docs)
- `api/` — TypeScript declarations from xstate npm package
- If user asks about newer APIs, state version limit, recommend checking latest docs

## Fast triage

```txt
What does user need?
├─ Quick syntax lookup
│  └─ references/cheatsheet.md
│
├─ Concept explanation (actors, machines, statecharts, guards, actions)
│  └─ Route via references/routing-map.md → load matching docs/ file
│
├─ TypeScript types / API surface
│  └─ api/ directory (.d.ts files)
│  └─ api/package.json for exports map
│
├─ Framework integration (React, Svelte, Vue, Store)
│  └─ references/routing-map.md § Integrations
│
├─ v4 → v5 migration
│  └─ references/gotchas.md + docs/migration.mdx + docs/upgrade.mdx
│
├─ Stately editor / visual tooling
│  └─ references/routing-map.md § Stately Editor
│
└─ Common mistakes / debugging
   └─ references/gotchas.md
```

## Defaults

- Prefer `setup({}).createMachine({})` pattern (v5 idiomatic)
- Use `setup()` for declaring actions, guards, actors, delays with type safety
- Always use object syntax for events: `{ type: 'EVENT_NAME' }`
- Prefer named actions/guards in `setup()` over inline functions
- Route to core XState first unless user asks about specific integration

## Reading Order

| Task                          | Files to read                                                     |
| ----------------------------- | ----------------------------------------------------------------- |
| Quick syntax reference        | `references/cheatsheet.md`                                        |
| Route to specific topic       | `references/routing-map.md`                                       |
| New to XState                 | `docs/quick-start.mdx` → `docs/machines.mdx` → `docs/actors.mdx`  |
| Understand actors             | `docs/actor-model.mdx` → `docs/actors.mdx` → `docs/invoke.mdx`    |
| TypeScript setup              | `docs/typescript.mdx` → `api/` declarations                       |
| Guards and conditions         | `references/cheatsheet.md` § Guards → `docs/guards.mdx`           |
| Delayed/eventless transitions | `docs/delayed-transitions.mdx` → `docs/eventless-transitions.mdx` |
| Parallel/history states       | `docs/parallel-states.mdx` → `docs/history-states.mdx`            |
| Testing state machines        | `docs/testing.mdx`                                                |
| React integration             | `docs/xstate-react.mdx`                                           |
| Svelte integration            | `docs/xstate-svelte.mdx`                                          |
| Vue integration               | `docs/xstate-vue.mdx`                                             |
| XState Store                  | `docs/xstate-store.mdx` → `docs/xstate-store-v2.mdx`              |
| v4 → v5 migration             | `references/gotchas.md` → `docs/migration.mdx`                    |
| Debug common issues           | `references/gotchas.md`                                           |
| Check freshness/provenance    | `references/source-index.md`                                      |

## In This Reference

| File                         | Purpose                                        |
| ---------------------------- | ---------------------------------------------- |
| `references/cheatsheet.md`   | Full v5 syntax cheatsheet with examples        |
| `references/routing-map.md`  | Topic → vendored doc file path (generated)     |
| `references/gotchas.md`      | v4→v5 migration pitfalls, common mistakes      |
| `references/source-index.md` | Provenance, version pins, re-sync instructions |

## Scripts

| Script                 | Purpose                                           |
| ---------------------- | ------------------------------------------------- |
| `scripts/sync-docs.sh` | Download + vendor docs and API types. Idempotent. |

## Vendored content

| Directory | Source         | Contents                                          |
| --------- | -------------- | ------------------------------------------------- |
| `docs/`   | statelyai/docs | ~112 MDX files covering all XState/Stately topics |
| `api/`    | xstate npm     | TypeScript declarations (.d.ts) + package.json    |
