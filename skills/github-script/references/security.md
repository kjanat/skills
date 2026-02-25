# Security

## Rule of thumb

- If a value already exists on `context`/`context.payload`, read it there.
- Use `env` only for values not present in `context` (for example vars, secrets, matrix, step outputs).
- Never inline `${{ ... }}` inside script code.

## Safe pattern (context first)

```yaml
- uses: actions/github-script@v8
  with:
    script: |
      const title = context.payload.pull_request?.title ?? ''
      if (title.startsWith('octocat')) {
        console.log('ok')
      }
```

## Safe pattern (env only when needed)

```yaml
- uses: actions/github-script@v8
  env:
    TITLE_PREFIX: ${{ vars.TITLE_PREFIX }}
  with:
    script: |
      const prefix = process.env.TITLE_PREFIX ?? ''
      const title = context.payload.pull_request?.title ?? ''
      if (title.startsWith(prefix)) {
        console.log('ok')
      }
```

## Unsafe pattern

```yaml
- uses: actions/github-script@v8
  with:
    script: |
      const title = "${{ github.event.pull_request.title }}"
```

## Checklist

- Prefer `context` values over env pass-through.
- Keep `${{ ... }}` in workflow YAML fields (`env`, `if`, `with:` action inputs, etc.), not in script body.
- Read from `process.env`.
- Normalize missing values (`?? ''`, parse numbers safely).
- Validate untrusted input before API calls.
- Use least-privilege `permissions:` at workflow or job scope.
