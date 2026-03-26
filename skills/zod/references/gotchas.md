# Zod v4 Gotchas

High-frequency mistakes and the preferred Zod 4 replacements.

## Error APIs

- Prefer the unified `error` option.
- Do not lead with old patterns like `invalid_type_error`, `required_error`, `message`, or `errorMap`.
- For migration work, point users to `docs/v4/changelog.mdx`.

## Refinements

- Prefer `.check()` when steering users toward current APIs.
- `superRefine()` still appears in historical examples, but treat it as deprecated guidance.
- If a user is maintaining old code, explain the replacement instead of pretending the old pattern never existed.

## Async parsing

- If a schema uses async refinements or async transforms, use `parseAsync()` or `safeParseAsync()`.
- Do not show sync parsing examples for clearly async schemas.
- At IO boundaries, `safeParseAsync()` is usually the safest reusable pattern.

## Imports and versioning

- For current Zod 4 application code, prefer:

```ts
import * as z from 'zod';
```

- Mention `"zod/v4"` only for migration or compatibility context.
- Do not default everyday app code to `zod/v4/core`.

## Package choice

- `zod` is the default for most users.
- `zod/mini` is not “better Zod”; it is the same functionality with different ergonomics for bundle-size-sensitive cases.
- `zod/v4/core` is for library authors and low-level internals, not ordinary schema construction.

## Input vs output types

- Reach for `z.input<typeof Schema>` and `z.output<typeof Schema>` when transforms, coercion, defaults, or codecs make types diverge.
- Do not assume `z.infer<typeof Schema>` tells the full story for transformed data flows.

## JSON Schema

- `z.toJSONSchema()` is the stable path to convert a Zod schema to JSON Schema.
- `z.fromJSONSchema()` is experimental; describe it with that caveat.
- Some Zod features cannot be represented cleanly in JSON Schema. Call that out instead of implying round-trip fidelity.

## Library-author integration

- For libraries built on top of Zod, route to `docs/library-authors.mdx` first.
- Peer dependency guidance matters. The vendored docs recommend supporting `^3.25.0 || ^4.0.0` where appropriate.
- If the user needs low-level internals, route to `docs/packages/core.mdx`.
