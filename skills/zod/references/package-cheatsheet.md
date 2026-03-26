# Package Cheatsheet

Choose the package lane first, then load the matching vendored docs.

## `zod`

Use when:

- building ordinary application schemas
- validating request bodies, forms, configs, or external data
- teaching or explaining Zod 4 to most users

Do not avoid it unless:

- bundle size is a primary constraint and the user actually needs tree-shakable top-level helpers
- the user is building low-level tooling on top of Zod internals

Entry docs:

- `docs/packages/zod.mdx`
- `docs/basics.mdx`
- `docs/api.mdx`

## `zod/mini`

Use when:

- bundle-size or tree-shaking constraints are genuinely important
- the user accepts a more functional API in exchange for smaller bundles

Do not choose it when:

- the user just needs normal Zod examples
- discoverability and chained schema ergonomics matter more than bundle savings

Entry docs:

- `docs/packages/mini.mdx`
- `docs/api.mdx`

## `zod/v4/core`

Use when:

- the user is authoring tooling or libraries on top of Zod
- the question is about base classes, low-level internals, or extension points

Do not choose it when:

- the user is writing ordinary validation schemas
- the question is about request parsing, app-level schema composition, or form validation

Entry docs:

- `docs/packages/core.mdx`
- `docs/library-authors.mdx`
