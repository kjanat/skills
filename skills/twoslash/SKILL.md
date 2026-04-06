---
name: twoslash
description: Guides Twoslash-authored TypeScript documentation snippets, notation choice, and hidden fixture setup. Use when writing or reviewing `ts twoslash` code fences, `^?` queries, `^|` completions, `---cut---` directives, error assertions, or multi-file virtual examples.
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

1. Identify the teaching goal: type, completion, highlight, hidden setup, diagnostics, or emit.
2. Keep the rendered sample minimal; move scaffolding into cut regions or virtual files.
3. Add the smallest directive set that proves the point.
4. If errors are intentional, prefer exact validation with `@errors` over blanket suppression.
5. If the snippet is multi-file or emit-focused, verify the visible file is the one the reader actually needs.
6. Name the exact directives in the answer so the user can copy them directly.

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
