# Testing Docker Actions in Workflows

Workflow YAML patterns for testing public, private, and local actions.

## Public Action Usage

Reference by `owner/repo@tag`:

```yaml
on: [push]

jobs:
  hello_world_job:
    runs-on: ubuntu-latest
    name: A job to say hello
    steps:
      - name: Hello world action step
        id: hello
        uses: owner/hello-world-docker-action@v2
        with:
          who-to-greet: "Mona the Octocat"
      - name: Get the output time
        run: echo "The time was ${{ steps.hello.outputs.time }}"
```

Public actions work from any repository without checkout.

## Private/Internal Action (Same Repo)

Must checkout first, then reference with `./`:

```yaml
on: [push]

jobs:
  hello_world_job:
    runs-on: ubuntu-latest
    name: A job to say hello
    steps:
      - name: Checkout
        uses: actions/checkout@v5
      - name: Hello world action step
        uses: ./
        id: hello
        with:
          who-to-greet: "Mona the Octocat"
      - name: Get the output time
        run: echo "The time was ${{ steps.hello.outputs.time }}"
```

- `uses: ./` references the action at the repository root
- `uses: ./.github/actions/my-action` for subdirectory actions
- `actions/checkout@v5` is required for private actions

## Action in Subdirectory

```yaml
steps:
  - uses: actions/checkout@v5
  - uses: ./.github/actions/my-docker-action
    with:
      who-to-greet: "World"
```

## Accessing Action Outputs

```yaml
steps:
  - name: Run action
    id: my-step
    uses: ./
    with:
      input-name: "value"
  - name: Use output
    run: |
      echo "Result: ${{ steps.my-step.outputs.output-name }}"
```

## Accessing Container Build Artifacts

Container writes to `/github/workspace` map to `$GITHUB_WORKSPACE` on runner:

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v5
      - name: Containerized Build
        uses: ./.github/actions/my-container-action
      - name: Upload Build Artifacts
        uses: actions/upload-artifact@v4
        with:
          name: workspace_artifacts
          path: ${{ github.workspace }}
```

Files created at `/github/workspace` inside the container persist for later
steps in the same job.

## Version Pinning

| Reference                   | Behavior                        |
| --------------------------- | ------------------------------- |
| `uses: owner/action@v2`     | Major version tag (recommended) |
| `uses: owner/action@v2.1`   | Specific minor version          |
| `uses: owner/action@abc123` | Exact commit SHA (most secure)  |
| `uses: owner/action@main`   | Branch (least stable)           |

Best practice: Use SHA pinning for third-party actions, version tags for
your own.

## Repository Visibility Rules

| Visibility | Who Can Use                           |
| ---------- | ------------------------------------- |
| Public     | Any workflow in any repository        |
| Internal   | Only workflows in the same repository |
| Private    | Only workflows in the same repository |

Private repo actions can grant access to other repos via repository settings:
Settings > Actions > General > Access.

## Gotchas

- **Missing checkout**: Private/local actions require `actions/checkout@v5`
  before `uses: ./`
- **Tag not pushed**: `git push --follow-tags` to push annotated tags
- **Runner OS**: Docker container actions only run on `ubuntu-latest` (Linux).
  `macos-latest` and `windows-latest` are not supported
- **Self-hosted runners**: Must have Docker installed and run Linux

## See Also

- [action-metadata.md](action-metadata.md) - Defining inputs/outputs
- [entrypoint-scripts.md](entrypoint-scripts.md) - Setting outputs from container
