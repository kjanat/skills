# Inputs, outputs, retries

## Script arguments available in script

- `github`: authenticated Octokit client
- `octokit`: alias for `github`
- `context`: event/workflow context
- `core`, `glob`, `io`, `exec`
- wrapped `require`, plus `__original_require__`

## Output contract

Return value maps to `steps.<id>.outputs.result`.

```yaml
- uses: actions/github-script@v8
  id: set-result
  with:
    result-encoding: string
    script: return 'Hello'

- run: echo "${{ steps.set-result.outputs.result }}"
```

## Result encoding

- Default: JSON encoding
- Optional: `result-encoding: string`

## Retries

Retries are off by default.

```yaml
- uses: actions/github-script@v8
  with:
    retries: 3
    retry-exempt-status-codes: 400,401
    script: |
      await github.rest.issues.get({
        issue_number: context.issue.number,
        owner: context.repo.owner,
        repo: context.repo.repo,
      })
```

Default retry-exempt status codes: `400,401,403,404,422`.

Retries use Octokit retry plugin exponential backoff.
