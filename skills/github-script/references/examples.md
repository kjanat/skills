# Examples

## Contents

- Print context
- Comment on issue
- Apply label
- GraphQL query
- External script file (ESM)
- External script file (TypeScript source)
- Use custom token
- Use exec helper
- Handle API errors
- Paginate REST results

## Print context

```yaml
- name: View context
  uses: actions/github-script@v8
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
      - uses: actions/github-script@v8
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
- uses: actions/github-script@v8
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
- uses: actions/github-script@v8
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
- uses: actions/github-script@v8
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
- uses: actions/github-script@v8
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
- uses: actions/github-script@v8
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

## Use exec helper

```yaml
- uses: actions/github-script@v8
  with:
    script: |
      const { exitCode, stdout, stderr } = await exec.getExecOutput('echo', ['hello'])
      console.log(exitCode, stdout, stderr)
```

## Handle API errors

```yaml
- uses: actions/github-script@v8
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
- uses: actions/github-script@v8
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
