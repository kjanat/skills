# Changes

- Bumped `actions/github-script@v8` to `actions/github-script@v9` per skill default pin (Node 24 runtime, runner >= v2.327.1 still applies; no runner change vs v8).
- Removed `const { getOctokit } = require('@actions/github')`. In v9, `@actions/github` is ESM-only, so `require('@actions/github')` fails at runtime.
- Use the injected `getOctokit` factory directly (it is already provided as a script argument alongside `github`, `context`, `core`, etc.). Did not redeclare it with `const`/`let` — that raises `SyntaxError` in v9 because it is an injected function parameter.
- Preserved `name:`, `on:`, `permissions:`, `jobs:` structure, the `env.APP_TOKEN` boundary (token read via `process.env.APP_TOKEN`, not interpolated into the script), and the `github.rest.*` style call (`appOctokit.rest.repos.createDispatchEvent`).
