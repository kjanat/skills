# Runtime and migrations

## Current version guidance

Pin `actions/github-script@v9`.

- Runtime: Node 24
- Minimum self-hosted runner: `v2.327.1`

## Breaking changes by major version

## v9

- `@actions/github` upgraded to v9 (ESM-only). `require('@actions/github')` now fails at runtime; previous patterns like `const { getOctokit } = require('@actions/github')` must move to the new injected `getOctokit` factory.
- `getOctokit` is injected as a function parameter, alongside `github`/`context`/`core`/etc. Redeclaring it with `const` or `let` raises `SyntaxError`. Use it directly, or use `var getOctokit = ...` if you must shadow it.
- Other internals reached via `require('@actions/github')` (for example `@octokit/core` v7, updated octokit packages) may need v9-compatible call sites.
- `ACTIONS_ORCHESTRATION_ID` is appended to the user-agent for request tracing — informational, no script change required.
- Runtime and runner requirements unchanged from v8 (Node 24, runner `v2.327.1`).

## v8

- Runtime moved from Node 20 to Node 24

## v7

- Runtime moved from Node 16 to Node 20
- `previews` input only affects GraphQL calls

<details>
<summary>Legacy (v6/v5)</summary>

## v6

- Runtime moved from Node 12 to Node 16

## v5

- REST helper methods moved under `github.rest.*`
- `github.issues.createComment(...)` -> `github.rest.issues.createComment(...)`
- `github.request`, `github.paginate`, `github.graphql` unchanged

</details>

## Upgrade checklist

- Confirm runner version compatibility
- Check Node runtime breaking changes for script dependencies
- Replace legacy `github.<scope>.<method>` with `github.rest.<scope>.<method>`
- Remove any `require('@actions/github')` calls; switch to the injected `getOctokit` factory for secondary clients
- Audit script bodies for `const getOctokit` / `let getOctokit` shadowing — rename or delete those bindings
- Retest scripts relying on language/runtime edge behavior
