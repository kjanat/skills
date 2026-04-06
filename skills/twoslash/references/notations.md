# Twoslash Notations

Use this file for exact directive names and the shortest correct explanation of each one.

## Query markers

| Notation | Use                                                    | Notes                                                                                                                                                                                                              |
| -------- | ------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `// ^?`  | Show type info for the identifier on the previous line | Best for inferred or expanded types.                                                                                                                                                                               |
| `// ^\|` | Show completions at the caret on the previous line     | Twoslash asks TypeScript for completions, filters by the typed prefix, and shows up to 5 results inline. Often pair with `// @noErrors`. <br> Do not include a `\` character before the pipe character and the `^` |
| `// ^^^` | Highlight a range on the previous line                 | Styling depends on the renderer or site theme.                                                                                                                                                                     |

## Cut directives

| Directive                                 | Use                           | Notes                                                                            |
| ----------------------------------------- | ----------------------------- | -------------------------------------------------------------------------------- |
| `// ---cut---`                            | Hide everything above         | Alias of `// ---cut-before---`. Hidden code still participates in type checking. |
| `// ---cut-before---`                     | Hide everything above         | Use when you want the explicit name instead of the shorthand.                    |
| `// ---cut-after---`                      | Hide everything below         | Good for trimming post-example noise.                                            |
| `// ---cut-start---` / `// ---cut-end---` | Hide the section between them | Pairs must match; multiple pairs are supported.                                  |

Cutting happens after TypeScript and editor metadata have been produced, so hidden code can still power imports, hovers, queries, and highlights.

## Diagnostics and render flags

| Flag                              | Use                                            | Notes                                                              |
| --------------------------------- | ---------------------------------------------- | ------------------------------------------------------------------ |
| `// @errors: 2322 2588`           | Assert exact TypeScript error codes            | Build fails if expected errors are missing or extra errors appear. |
| `// @noErrors`                    | Suppress diagnostics                           | Use sparingly; best for completion or partial-expression demos.    |
| `// @noErrorValidation`           | Render errors without validating them          | Keeps diagnostics visible but disables build-breaking validation.  |
| `// @noErrorsCutted`              | Ignore errors in hidden cut regions            | Useful when hidden setup is intentionally invalid or incomplete.   |
| `// @noStaticSemanticInfo`        | Disable pre-cached hover and semantic info     | Niche option. Do not lead with it for normal docs authoring.       |
| `// @showEmit`                    | Replace the source snippet with emitted output | Defaults to emitted `index.js` unless another file is selected.    |
| `// @showEmittedFile: index.d.ts` | Choose which emitted file to render            | Requires `// @showEmit`.                                           |
| `// @keepNotations`               | Keep Twoslash notations in the rendered code   | Primarily useful for tooling or source-mapping workflows.          |

## Files and compiler options

| Flag                 | Use                                      | Notes                                                                                         |
| -------------------- | ---------------------------------------- | --------------------------------------------------------------------------------------------- |
| `// @filename: a.ts` | Create a virtual file                    | This is the only author-facing Twoslash notation that remains visible unless you cut it away. |
| `// @target: ES2022` | Set compiler options inline              | Any TypeScript compiler option can be set with `// @flag: value`.                             |
| `// @strict: true`   | Override snippet-level compiler behavior | Prefer the fewest flags needed to make the example accurate.                                  |

## Default advice

- Prefer `@errors` over `@noErrors` when diagnostics are part of the teaching goal.
- Prefer cut directives over deleting setup that TypeScript still needs.
- Prefer `@showEmittedFile` only when the default emitted file is not the one the reader needs.
