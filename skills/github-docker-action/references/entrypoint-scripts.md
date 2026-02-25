# Entrypoint Scripts

Writing the script that executes inside the Docker container.

## Starter Template

```sh
#!/bin/sh -l

echo "Hello $1"
time=$(date)
echo "time=$time" >> $GITHUB_OUTPUT
```

- `#!/bin/sh -l`: Login shell ensures profile/env are loaded
- `$1`: First positional arg from `action.yml` `args`
- `$GITHUB_OUTPUT`: File for setting step outputs

## Receiving Inputs

Inputs declared in `action.yml` and passed via `args` arrive as positional
parameters:

```yaml
# action.yml
args:
  - ${{ inputs.name }}
  - ${{ inputs.greeting }}
```

```sh
# entrypoint.sh
NAME="$1"
GREETING="$2"
echo "$GREETING $NAME"
```

Alternatively, inputs are available as environment variables:

```sh
# Automatic env var: INPUT_<NAME> (uppercased)
echo "Hello $INPUT_WHO_TO_GREET"
```

Positional args via `args` are preferred for clarity.

## Setting Outputs

Write `key=value` pairs to `$GITHUB_OUTPUT`:

```sh
echo "result=success" >> $GITHUB_OUTPUT
echo "time=$(date)" >> $GITHUB_OUTPUT
```

### Multi-line outputs

Use a unique delimiter:

```sh
EOF_MARKER=$(dd if=/dev/urandom bs=15 count=1 status=none | base64)
{
  echo "report<<${EOF_MARKER}"
  cat report.txt
  echo "${EOF_MARKER}"
} >> $GITHUB_OUTPUT
```

## Setting Environment Variables

For subsequent steps (not the current container):

```sh
echo "MY_VAR=some_value" >> $GITHUB_ENV
```

## Exit Codes

| Code | Meaning                 |
| ---- | ----------------------- |
| `0`  | Success (action passes) |
| `1`  | Failure (action fails)  |

```sh
if [ -z "$1" ]; then
  echo "::error::Input 'name' is required"
  exit 1
fi
```

## Workflow Commands

Log annotations from within the script:

```sh
echo "::debug::Debug message"
echo "::notice::Notice message"
echo "::warning::Warning message"
echo "::error::Error message"
echo "::error file=app.js,line=10::Something failed"
```

Group log output:

```sh
echo "::group::Build output"
make build
echo "::endgroup::"
```

## File Permissions

The entrypoint must be executable. Git tracks permissions explicitly:

```sh
# Add and mark executable
git add entrypoint.sh
git update-index --chmod=+x entrypoint.sh

# Verify (should show 100755)
git ls-files --stage entrypoint.sh
```

`100755` = executable. `100644` = not executable (will fail at runtime).

## Gotchas

- **Missing shebang**: Always include `#!/bin/sh -l` or `#!/bin/bash`
- **Not executable**: Container will fail to start. Use `git update-index
  --chmod=+x` — `chmod +x` alone doesn't persist in git
- **CRLF line endings**: If editing on Windows, ensure LF endings. CRLF
  causes `/bin/sh: bad interpreter` errors
- **No `$GITHUB_OUTPUT` write**: Outputs won't propagate to later steps
- **Unquoted variables**: Always quote `"$1"` to handle spaces in inputs

## See Also

- [action-metadata.md](action-metadata.md) - Declaring inputs/outputs
- [workflow-testing.md](workflow-testing.md) - Testing output values
