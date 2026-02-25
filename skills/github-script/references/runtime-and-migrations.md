# Runtime and migrations

## Current version guidance

Pin `actions/github-script@v8`.

- Runtime: Node 24
- Minimum self-hosted runner: `v2.327.1`

## Breaking changes by major version

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
- Retest scripts relying on language/runtime edge behavior
