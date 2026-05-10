# Examples

## Contents

- Print context
- Comment on issue
- Apply label
- GraphQL query
- External script file (ESM)
- External script file (TypeScript source)
- Use custom token
- Secondary client with `getOctokit` (cross-org / GitHub App)
- Use exec helper
- Handle API errors
- Paginate REST results

## Print context

```yaml
- name: View context
  uses: actions/github-script@v9
  with:
    script: console.log(context)
```

## Comment on issue

```yaml
on:
  issues:
    types: [opened]

jobs:
  comment:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/github-script@v9
        with:
          script: |
            await github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: 'Thanks for reporting.'
            })
```

## Apply label

```yaml
- uses: actions/github-script@v9
  with:
    script: |
      await github.rest.issues.addLabels({
        issue_number: context.issue.number,
        owner: context.repo.owner,
        repo: context.repo.repo,
        labels: ['Triage']
      })
```

## GraphQL query

```yaml
- uses: actions/github-script@v9
  with:
    script: |
      const query = `query($owner:String!, $name:String!) {
        repository(owner:$owner, name:$name){
          issues(first:10) { nodes { id number } }
        }
      }`

      const result = await github.graphql(query, {
        owner: context.repo.owner,
        name: context.repo.repo,
      })
      console.log(result)
```

## External script file (ESM)

```yaml
- uses: actions/checkout@v6
- uses: actions/github-script@v9
  with:
    script: |
      const { default: run } = await import(`${process.env.GITHUB_WORKSPACE}/scripts/task.mjs`)
      await run({ github, context, core })
```

`scripts/task.mjs`:

```javascript
// @ts-check
/** @param {import('@actions/github-script').AsyncFunctionArguments} args */
export default async function run({ github, context, core }) {
	const issue = await github.rest.issues.get({
		issue_number: context.issue.number,
		owner: context.repo.owner,
		repo: context.repo.repo,
	});

	core.info(`Issue title: ${issue.data.title}`);
}
```

## External script file (TypeScript source)

Compile TS first; import compiled JS in workflow:
(assumes `scripts/package.json` has `build` and emits `scripts/dist/task.mjs`)

```yaml
- uses: actions/checkout@v6
- run: npm ci --prefix scripts
- run: npm run build --prefix scripts
- uses: actions/github-script@v9
  with:
    script: |
      const { default: run } = await import(`${process.env.GITHUB_WORKSPACE}/scripts/dist/task.mjs`)
      await run({ github, context, core, exec, glob, io })
```

`scripts/src/task.ts`:

```typescript
import type { AsyncFunctionArguments } from '@actions/github-script';

export default async function run({ github, context, core }: AsyncFunctionArguments): Promise<void> {
	const issue = await github.rest.issues.get({
		issue_number: context.issue.number,
		owner: context.repo.owner,
		repo: context.repo.repo,
	});

	core.info(`Issue title: ${issue.data.title}`);
}
```

## Use custom token

```yaml
- uses: actions/github-script@v9
  with:
    github-token: ${{ secrets.MY_PAT }}
    script: |
      await github.rest.issues.addLabels({
        issue_number: context.issue.number,
        owner: context.repo.owner,
        repo: context.repo.repo,
        labels: ['Triage']
      })
```

## Secondary client with `getOctokit` (cross-org / GitHub App)

`getOctokit(token, opts?)` is injected into the script context (v9+). The
returned client inherits the same retry / request-log / proxy plugins as the
default `github` client. Use it when one step needs more than one identity —
typically the workflow's own `GITHUB_TOKEN` plus a PAT or App token for
another repo, org, or GHES instance.

`request` and `retry` options merge with the action defaults; other top-level
options (e.g. `baseUrl`, `userAgent`) replace them outright.

Caveat: `getOctokit` is a function parameter. Do not redeclare it with
`const`/`let` — that throws `SyntaxError`. Use it directly, or use `var` if
you must shadow it.

```yaml
- uses: actions/github-script@v9
  env:
    APP_TOKEN: ${{ secrets.MY_APP_TOKEN }}
  with:
    github-token: ${{ secrets.GITHUB_TOKEN }}
    script: |
      // Default `github` client uses GITHUB_TOKEN (current repo).
      await github.rest.issues.addLabels({
        issue_number: context.issue.number,
        owner: context.repo.owner,
        repo: context.repo.repo,
        labels: ['triage'],
      })

      // Secondary client with a different token for a cross-repo dispatch.
      const appOctokit = getOctokit(process.env.APP_TOKEN)
      await appOctokit.rest.repos.createDispatchEvent({
        owner: 'my-org',
        repo: 'another-repo',
        event_type: 'trigger-deploy',
      })
```

GHES with custom `baseUrl`:

```yaml
- uses: actions/github-script@v9
  env:
    GHES_TOKEN: ${{ secrets.GHES_PAT }}
  with:
    script: |
      const ghes = getOctokit(process.env.GHES_TOKEN, {
        baseUrl: 'https://github.example.com/api/v3',
      })

      const { data } = await ghes.rest.repos.listForOrg({ org: 'internal' })
      core.info(`Found ${data.length} repos on GHES`)
```

## Use exec helper

```yaml
- uses: actions/github-script@v9
  with:
    script: |
      const { exitCode, stdout, stderr } = await exec.getExecOutput('echo', ['hello'])
      console.log(exitCode, stdout, stderr)
```

## Handle API errors

```yaml
- uses: actions/github-script@v9
  with:
    script: |
      try {
        await github.rest.issues.createComment({
          issue_number: context.issue.number,
          owner: context.repo.owner,
          repo: context.repo.repo,
          body: 'Automated comment'
        })
      } catch (error) {
        core.setFailed(`github-script failed: ${error instanceof Error ? error.message : String(error)}`)
      }
```

## Paginate REST results

```yaml
- uses: actions/github-script@v9
  with:
    script: |
      const issues = await github.paginate(github.rest.issues.listForRepo, {
        owner: context.repo.owner,
        repo: context.repo.repo,
        state: 'open',
        per_page: 100,
      })

      core.info(`Open issues: ${issues.length}`)
```
