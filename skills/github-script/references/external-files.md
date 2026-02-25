# External ESM files

## Recommendation

Prefer external ESM modules over large inline scripts.

- Use `.mjs` modules by default (or `.js` with `// @ts-check`).
- Keep inline script as thin loader.
- Avoid CommonJS (`require`, `module.exports`) in new workflows.
- If you author in `.ts`, compile to `.mjs`/`.js` and import the built output.

## Practical patterns

Template assets in this skill root (copied from [`kp2bw/scripts/`](https://github.com/kjanat/kp2bw/tree/master/scripts))

- `assets/scripts/version-check-shared.mjs`: shared core logic template.
- `assets/scripts/uv-version.mjs` and `assets/scripts/stubs-version.mjs`: tiny entry module templates.
- `assets/package.json`: ESM + local typecheck command.
- `assets/tsconfig.json`: JS-check setup for github-script modules.
- `assets/check-uv-version-job.yml`: workflow job fragment loading `scripts/uv-version.mjs`.
- `assets/check-stubs-version-job.yml`: workflow job fragment loading `scripts/stubs-version.mjs`.

This pattern scales better than duplicating inline snippets.

## JSDoc typecheck setup (exact upstream-style)

Install types from the action source:

```sh
# if the current project uses another package manager, adjust accordingly
npm i -D @actions/github-script@github:actions/github-script
```

Use JSDoc in script modules:

```javascript
// @ts-check
/** @param {import('@actions/github-script').AsyncFunctionArguments} args */
export default async ({ core, context }) => {
	core.debug('Running something at the moment');
	return context.actor;
};
```

See bundled config/examples in `assets/package.json`, `assets/tsconfig.json`, and `assets/scripts/*.mjs`.

## Thin inline loader (ESM)

```yaml
- uses: actions/checkout@v6
- uses: actions/github-script@v8
  with:
    script: |
      const { default: run } = await import(`${process.env.GITHUB_WORKSPACE}/scripts/task.mjs`)
      await run({ github, context, core, exec, glob, io })
```

## External module (ESM, JSDoc)

```javascript
// @ts-check
/** @param {import('@actions/github-script').AsyncFunctionArguments} args */
export default async function run({ github, context, core }) {
	const title = context.payload.pull_request?.title ?? '';
	if (!title) {
		core.info('No PR title in event payload');
		return;
	}

	await github.rest.issues.createComment({
		issue_number: context.issue.number,
		owner: context.repo.owner,
		repo: context.repo.repo,
		body: `Saw title: ${title}`,
	});
}
```

## External module (TypeScript source, compiled runtime)

Use this when you want TypeScript authoring but predictable runtime imports.
Assumes `scripts/package.json` has `build` and emits `scripts/dist/*.mjs`.

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
	const title = context.payload.pull_request?.title ?? '';
	if (!title) {
		core.info('No PR title in event payload');
		return;
	}

	await github.rest.issues.createComment({
		issue_number: context.issue.number,
		owner: context.repo.owner,
		repo: context.repo.repo,
		body: `Saw title: ${title}`,
	});
}
```

## Inline-only exception

If script is truly tiny (1-3 lines), inline is fine. Still use ESM syntax and keep logic minimal.
