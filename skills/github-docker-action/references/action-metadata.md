# Action Metadata (action.yml)

The `action.yml` file defines your action's interface: inputs, outputs, and
how GitHub should run it.

## Starter Template

```yaml
name: "My Docker Action"
description: "Short description of what this action does"
inputs:
  who-to-greet:
    description: "Who to greet"
    required: true
    default: "World"
outputs:
  time:
    description: "The time we greeted you"
runs:
  using: "docker"
  image: "Dockerfile"
  args:
    - ${{ inputs.who-to-greet }}
```

## Top-Level Fields

| Field         | Required | Description                           |
| ------------- | -------- | ------------------------------------- |
| `name`        | Yes      | Display name in GitHub UI             |
| `description` | Yes      | Short explanation of the action       |
| `author`      | No       | Author name                           |
| `branding`    | No       | Icon and color for GitHub Marketplace |

## Inputs

```yaml
inputs:
  input-id:
    description: "What this input does"
    required: true # or false
    default: "fallback" # optional default value
```

- Input IDs use kebab-case (`who-to-greet`, not `whoToGreet`)
- Inputs are passed to Docker via `args` in the order listed
- Access in entrypoint as positional args: `$1`, `$2`, etc.
- Also available as env vars: `INPUT_WHO-TO-GREET` (uppercased, prefixed)

## Outputs

```yaml
outputs:
  output-id:
    description: "What this output contains"
```

Outputs are set from within the container by writing to `$GITHUB_OUTPUT`:

```sh
echo "output-id=value" >> $GITHUB_OUTPUT
```

Consumers access outputs via `${{ steps.<step-id>.outputs.output-id }}`.

## Runs Configuration (Docker)

```yaml
runs:
  using: "docker"
  image: "Dockerfile" # Build from local Dockerfile
  args:
    - ${{ inputs.who-to-greet }}
```

### Image Sources

| `image` Value                   | Behavior                          |
| ------------------------------- | --------------------------------- |
| `'Dockerfile'`                  | Build from Dockerfile in repo     |
| `'docker://alpine:3.21'`        | Pull pre-built public image       |
| `'docker://ghcr.io/org/img:v1'` | Pull pre-built private/GHCR image |

Using a pre-built image skips the build step and is faster.

### Optional `runs` Fields

| Field             | Purpose                                    |
| ----------------- | ------------------------------------------ |
| `args`            | Arguments passed to `ENTRYPOINT`           |
| `entrypoint`      | Override Dockerfile's `ENTRYPOINT`         |
| `env`             | Environment variables set in the container |
| `pre-entrypoint`  | Script to run before main entrypoint       |
| `post-entrypoint` | Script to run after main entrypoint        |

### Environment Variables in Runs

```yaml
runs:
  using: "docker"
  image: "Dockerfile"
  env:
    MY_VAR: "some-value"
    OTHER_VAR: ${{ inputs.some-input }}
```

## Branding (Marketplace)

```yaml
branding:
  icon: "award"
  color: "green"
```

Icons use [Feather icons](https://feathericons.com/). Colors: `white`,
`yellow`, `blue`, `green`, `orange`, `red`, `purple`, `gray-dark`.

## Gotchas

- **`args` order matters**: Positional args map to `$1`, `$2`, etc. in order
- **`using: 'docker'`**: Required for container actions (vs `using: 'node20'`
  for JavaScript actions)
- **Input env vars**: Automatically set as `INPUT_<NAME>` (uppercased, hyphens
  preserved) — but using `args` is more explicit

## See Also

- [dockerfile-patterns.md](dockerfile-patterns.md) - Dockerfile configuration
- [entrypoint-scripts.md](entrypoint-scripts.md) - Using inputs in scripts
- [workflow-testing.md](workflow-testing.md) - Testing the action
