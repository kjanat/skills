# Source Index

Primary upstream sources used for this skill:

- `https://twoslash.netlify.app/refs/notations` for query markers, cut directives, emit display, and `@filename:` behavior.
- `https://twoslash.netlify.app/refs/options` for documented handbook options like `@errors`, `@noErrors`, `@noErrorsCutted`, `@noErrorValidation`, and `@keepNotations`.
- `https://raw.githubusercontent.com/twoslashes/twoslash/main/packages/twoslash/src/types/handbook-options.ts` for handbook options typed in source but not fully described in the public docs, notably `@noStaticSemanticInfo`.

Provenance note:

- This skill intentionally emphasizes author-facing notation choices over Twoslash internals.
- If a user asks about options not covered here, prefer the upstream refs first, then the handbook option types.
