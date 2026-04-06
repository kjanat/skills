# Twoslash Examples

Curated copy-paste examples for the most common Twoslash authoring tasks.

Keep this file small. Add examples only when they cover a common authoring question that the core notation tables do not answer as quickly.

When editing marker lines like `//       ^|`, verify the real caret column with `uv run scripts/inspect-markers.py <file>` instead of guessing spaces.

## Hide setup with `---cut---`

Use when TypeScript needs setup code but readers should only see the teaching line.

```ts
const level: string = 'Danger';
// ---cut---
console.log(level);
```

Source: `docs/refs/notations.md` `cut-before` example.

## Show completions with `^|`

Use when the expression is intentionally incomplete and the goal is to show completions, not diagnostics.

```ts
// @noErrors
console.e;
//       ^|
```

Source: `docs/refs/notations.md` completions example.

## Model multi-file context with `@filename:`

Use when a snippet needs another virtual file for imports or ambient types.

```ts
// @filename: a.ts
export const helloWorld: string = 'Hi';
// ---cut---
// @filename: b.ts
import { helloWorld } from './a';

console.log(helloWorld);
```

Use `---cut---` when the setup file is only there to make the visible file compile.

Source: `docs/refs/notations.md` multi-file cut example.

## Assert exact diagnostics with `@errors`

Use when the error itself is part of the lesson and the docs should fail if diagnostics drift.

```ts
// @errors: 2322 2588
const str: string = 1;
str = 'Hello';
```

Prefer this over `@noErrors` when you care about the exact TypeScript errors.

Source: `docs/refs/options.md` `errors` example.

## Ignore errors only in hidden code with `@noErrorsCutted`

Use when the visible snippet should stay clean but hidden setup or teardown is intentionally noisy.

```ts
// @noErrorsCutted
const hello = 'world';
// ---cut-after---
hello = 'hi';
```

Source: `docs/refs/options.md` `noErrorsCutted` example.

## Show emitted declarations with `@showEmit`

Use when the emitted file is the teaching target instead of the TypeScript source.

```ts
// @declaration
// @showEmit
// @showEmittedFile: index.d.ts
export const hello = 'world';
```

Source: `docs/refs/notations.md` `showEmittedFile` `.d.ts` example.
