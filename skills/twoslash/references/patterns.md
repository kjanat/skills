# Twoslash Patterns

Use these patterns when writing or reviewing `ts twoslash` snippets.

## Hide setup, not meaning

If imports, fixtures, or helper declarations are required for type checking but not for teaching, keep them above `// ---cut---`.

```ts
import { helper } from './docs/.vitepress/twoslash/testing-fixtures';

// ---cut---
const result = helper('eu-west-1');
//    ^?
```

This keeps the symbol available to TypeScript while the rendered docs start at the reader-facing line.

## Model multi-file examples explicitly

Use `// @filename:` when the example depends on another module, ambient type, or fake package.

```ts
// @filename: a.ts
export const helloWorld: string = 'Hi';
// ---cut---
// @filename: b.ts
import { helloWorld } from './a';

console.log(helloWorld);
```

If the visible example should not show file boundaries, cut away the setup file and keep only the reader-facing file visible.

- Keep `@filename:` visible when file boundaries are part of the lesson.
- Cut it away when the extra file only exists to make the visible snippet compile.

## Pick the narrowest error mode

Use the smallest flag that matches the teaching goal.

- Use this decision matrix when choosing:

| Need                                                    | Prefer               | Why                                                          |
| ------------------------------------------------------- | -------------------- | ------------------------------------------------------------ |
| Exact error codes are part of the lesson                | `@errors`            | Guards the snippet against diagnostic drift.                 |
| Errors should render, but exact codes are not important | `@noErrorValidation` | Shows the problem without coupling docs to exact codes.      |
| Errors are incidental noise                             | `@noErrors`          | Keeps focus on completions or other non-diagnostic behavior. |
| Only hidden code is noisy                               | `@noErrorsCutted`    | Keeps visible code strict while forgiving cut-away setup.    |

- Use `@errors` when the exact diagnostic codes are the lesson.
- Use `@noErrors` when the expression is intentionally incomplete, such as `console.e` for completion demos.
- Use `@noErrorValidation` when you want errors rendered but do not want the snippet coupled to exact error codes.
- Use `@noErrorsCutted` when only the hidden region is noisy.

Avoid using `@noErrors` as a blanket escape hatch if the visible example is supposed to be valid TypeScript.

## Emit only when output is the lesson

Use `@showEmit` for transpilation-focused docs, not for ordinary authoring.

- Show emitted `.js` when explaining transpilation or module output.
- Add `@showEmittedFile` when you actually need `.d.ts`, `.map`, or the output from a non-default file.
- Keep the source example small; emitted output gets noisy fast.

## Review checklist

Before shipping a Twoslash snippet, check these:

1. The visible snippet teaches one thing, not three.
2. Hidden setup exists only to satisfy TypeScript or editor metadata.
3. Query markers point at the intended line above them.
4. Error flags are as narrow as possible.
5. Multi-file examples use `@filename:` instead of unexplained imports.
6. Emit mode is only used when the emitted file is the thing being taught.

## Authoring loop

Use this loop for new or edited snippets:

1. Write the full snippet so TypeScript has the context it needs.
2. Cut away setup that is not part of the lesson.
3. Verify each marker still points at the intended previous line.
4. Verify the chosen error mode is the narrowest one that works.
5. Verify the rendered file is the one the reader should see.
6. Re-check whether any visible `@filename:` lines are still pedagogically useful.

## Common mistakes

- Forgetting that `^?`, `^|`, and `^^^` always refer to the previous line.
- Using `@showEmittedFile` without `@showEmit`.
- Leaving `@filename:` visible when a cut directive should hide it.
- Removing helper code instead of cutting it, then wondering why the sample no longer type-checks.
- Using `@noErrors` when `@errors` would make the docs safer.
