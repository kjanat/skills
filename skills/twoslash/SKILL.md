---
name: twoslash
description: Guides authoring and review of Twoslash-powered TypeScript docs examples, including hidden setup, type queries, completions, diagnostics, and multi-file snippets. Use when writing or reviewing `ts twoslash` fences or when docs examples need `---cut---`, `^?`, `^|`, `@filename`, or exact error assertions.
license: MIT
metadata:
  author: kjanat
  version: "1.0"
---

# Twoslash

Use for docs examples powered by Twoslash.

## Scope and defaults

- Prefer the smallest rendered snippet that still teaches the point.
- Keep setup imports, helper declarations, and fake files type-visible but reader-hidden with cut directives.
- Prefer `// @errors: ...` when the error itself is part of the lesson.
- Prefer `// @noErrors` only when the snippet is intentionally incomplete for some other reason, such as completion demos.
- Prefer `// @filename:` for multi-file context instead of explaining missing imports in prose.
- Prefer `// @showEmit` only when the emitted JS, `.d.ts`, or map file is the teaching target.
- Do not reach for this skill for plain TypeScript snippets that do not rely on Twoslash behavior.

## Gotchas

- `^?`, `^|`, and `^^^` always apply to the previous line.
- Hidden code still participates in type checking and editor metadata; prefer cutting setup over deleting it.
- `@filename:` stays visible unless you cut it away on purpose.
- `@showEmittedFile` is only meaningful together with `@showEmit`.

## Fast triage

```txt
What does the user need?
├─ Show an inferred type or resolved symbol
│  └─ references/notations.md -> query markers
├─ Show autocomplete or highlight a span
│  └─ references/notations.md -> query markers
├─ Hide setup, fixtures, or boilerplate
│  └─ references/patterns.md -> hidden-setup patterns
├─ Model multiple files or fake imports
│  └─ references/patterns.md -> multi-file patterns
├─ Show or validate diagnostics
│  └─ references/notations.md -> error flags
├─ Show emitted JS / .d.ts / source maps
│  └─ references/notations.md -> emit flags
└─ Explain provenance or edge options
   └─ references/source-index.md
```

## Response workflow

1. Identify whether this is new authoring or review of an existing snippet.
2. Identify the teaching goal: type, completion, highlight, hidden setup, diagnostics, or emit.
3. Keep the rendered sample minimal; move scaffolding into cut regions or virtual files.
4. Add the smallest directive set that proves the point.
5. If errors are intentional, prefer exact validation with `@errors` over blanket suppression.
6. If the snippet is multi-file or emit-focused, verify the visible file is the one the reader actually needs.
7. Name the exact directives in the answer so the user can copy them directly.

## Authoring defaults

- `^?` for inferred or resolved types.
- `^|` for completion lists; pair with `@noErrors` when the expression is intentionally unfinished.
- `^^^` for visual emphasis, not semantic explanation.
- `---cut---` or `---cut-before---` to hide setup above the visible snippet.
- `---cut-after---` or `---cut-start---` / `---cut-end---` to hide trailing or middle noise.
- `@filename:` to create virtual files, including fake `node_modules/@types` shims.

## Reading Order

| Task                                      | Files to read                                                             |
| ----------------------------------------- | ------------------------------------------------------------------------- |
| New to Twoslash authoring                 | [`SKILL.md`] -> [`references/notations.md`] -> [`references/patterns.md`] |
| Pick the right directive                  | [`references/notations.md`]                                               |
| Hide fixtures or multi-file setup         | [`references/patterns.md`]                                                |
| Explain lesser-used options or provenance | [`references/source-index.md`]                                            |
| Review a noisy or broken snippet          | [`references/patterns.md`] -> [`references/notations.md`]                 |

## In This Reference

| File                           | Purpose                                                         |
| ------------------------------ | --------------------------------------------------------------- |
| [`references/notations.md`]    | Exact notation names, flags, and when to use them               |
| [`references/patterns.md`]     | Authoring defaults, hidden-setup patterns, and review checklist |
| [`references/source-index.md`] | Upstream source URLs and provenance notes                       |

[`references/notations.md`]: ./references/notations.md
[`references/patterns.md`]: ./references/patterns.md
[`references/source-index.md`]: ./references/source-index.md
[`SKILL.md`]: ./SKILL.md
