# Routing Map

Intent -> exact docs path bundles.

Freshness: pinned to `ebb4f7e28ee4db71d19109656cba80fb10eabe2c`.

## Learn track

Use when user needs concepts, architecture, or onboarding.

| Intent                    | Read first                                                     | Then                                                               |
| ------------------------- | -------------------------------------------------------------- | ------------------------------------------------------------------ |
| New to Threlte            | `apps/docs/src/content/learn/getting-started/introduction.mdx` | `installation.mdx`, `your-first-scene.mdx`                         |
| App structure confusion   | `apps/docs/src/content/learn/basics/app-structure.mdx`         | `reference/core/canvas.mdx`, `reference/core/use-threlte.mdx`      |
| Event model confusion     | `apps/docs/src/content/learn/basics/handling-events.mdx`       | `reference/extras/interactivity.mdx`                               |
| Asset loading patterns    | `apps/docs/src/content/learn/basics/loading-assets.mdx`        | `reference/core/use-loader.mdx`, `reference/extras/use-gltf.mdx`   |
| Render/update performance | `apps/docs/src/content/learn/basics/render-modes.mdx`          | `learn/basics/scheduling-tasks.mdx`, `reference/core/use-task.mdx` |
| Memory/disposal issues    | `apps/docs/src/content/learn/basics/disposing-objects.mdx`     | `learn/advanced/migration-guides.mdx`                              |
| Plugin architecture       | `apps/docs/src/content/learn/advanced/plugins.mdx`             | `reference/core/plugins.mdx`, `reference/extras/interactivity.mdx` |

## Reference track

Use when user needs exact API/props/hook semantics.

| Intent                      | Package lane       | Read first                                                    | Then                                                      |
| --------------------------- | ------------------ | ------------------------------------------------------------- | --------------------------------------------------------- |
| Base scene setup            | `@threlte/core`    | `apps/docs/src/content/reference/core/getting-started.mdx`    | `canvas.mdx`, `t.mdx`                                     |
| Generic Three object wiring | `@threlte/core`    | `apps/docs/src/content/reference/core/t.mdx`                  | `components.mdx`, `hooks.mdx`                             |
| Utility components/plugins  | `@threlte/extras`  | `apps/docs/src/content/reference/extras/getting-started.mdx`  | `orbit-controls.mdx`, `interactivity.mdx`, `suspense.mdx` |
| GLTF CLI generation         | `@threlte/gltf`    | `apps/docs/src/content/reference/gltf/getting-started.mdx`    | `learn/basics/loading-assets.mdx`                         |
| Physics                     | `@threlte/rapier`  | `apps/docs/src/content/reference/rapier/getting-started.mdx`  | `rigid-body.mdx`, `auto-colliders.mdx`, `framerate.mdx`   |
| Timeline animation          | `@threlte/theatre` | `apps/docs/src/content/reference/theatre/getting-started.mdx` | `theatre/studio.mdx`, `studio/getting-started.mdx`        |
| VR/AR                       | `@threlte/xr`      | `apps/docs/src/content/reference/xr/getting-started.mdx`      | `pointer-controls.mdx`, `teleport-controls.mdx`           |
| 3D flex layout              | `@threlte/flex`    | `apps/docs/src/content/reference/flex/getting-started.mdx`    | `flex.mdx`, `box.mdx`                                     |
| Authoring/dev tooling       | `@threlte/studio`  | `apps/docs/src/content/reference/studio/getting-started.mdx`  | `extensions.mdx`, `deploying-to-production.mdx`           |

## Example mirror

Upstream docs example source is mirrored locally in this skill:

- `skills/threlte/examples/`

Use it for exact implementation examples that match docs pages.
