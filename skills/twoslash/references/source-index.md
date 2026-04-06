# Source Index

Primary upstream sources used for this skill:

- `https://twoslash.netlify.app/refs/notations` for query markers, cut directives, emit display, and `@filename:` behavior.
- `https://twoslash.netlify.app/refs/options` for documented handbook options like `@errors`, `@noErrors`, `@noErrorsCutted`, `@noErrorValidation`, and `@keepNotations`.
- `https://raw.githubusercontent.com/twoslashes/twoslash/main/packages/twoslash/src/types/handbook-options.ts` for handbook options typed in source but not fully described in the public docs, notably `@noStaticSemanticInfo`.

Local snapshot:

- [`../example-docs.txt`](../example-docs.txt) is a local `gitingest` dump of the upstream Twoslash docs tree plus selected package metadata. Use it for broad grep/read passes when you want a single-file snapshot.

Additional upstream pages worth checking when the user goes beyond notation authoring:

- `https://twoslash.netlify.app/guide/highlight` for Shiki integration and the `@shikijs/twoslash` / `@shikijs/vitepress-twoslash` lane.
- `https://twoslash.netlify.app/guide/install` and `https://twoslash.netlify.app/refs/api` for programmatic usage via `createTwoslasher`, `twoslasher`, and cache reuse.
- `https://twoslash.netlify.app/refs/result` for `TwoslashReturn`, `nodes`, and `meta` structure.
- `https://twoslash.netlify.app/guide/migrate` for migration from `@typescript/twoslash`, `twoslasherLegacy`, and removed `playgroundURL` behavior.
- `https://twoslash.netlify.app/packages/cdn` for `twoslash-cdn` browser and worker usage.
- `https://twoslash.netlify.app/packages/eslint` for `twoslash-eslint` and `eslint-check` trigger wiring.
- `https://twoslash.netlify.app/packages/vue` for `twoslash-vue` and SFC handling.
- `https://github.com/twoslashes/twoslash/blob/main/docs/.vitepress/config.ts` for the Twoslash docs site's real VitePress transformer setup, including dual transformers and the `explicitTrigger` split for ESLint examples.

Provenance note:

- This skill intentionally emphasizes author-facing notation choices over Twoslash internals.
- Current skill coverage is strongest for docs-authoring questions around directives, flags, and snippet shaping.
- After ingesting upstream docs, the main uncovered lanes are programmatic API usage, result structure, migration details, and package-specific integrations.
- `example-docs.txt` is a convenience snapshot, not canonical. When precision matters, prefer the real upstream URLs above.
- Do not cite repo-style paths here unless the file actually exists in this skill directory; prefer real upstream URLs for external sources.
- If a user asks about options not covered here, prefer the upstream refs first, then the handbook option types.
