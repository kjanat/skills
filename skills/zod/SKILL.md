---
name: zod
description: Routes Zod v4 questions to commit-pinned docs and directs models toward current Zod 4 APIs, package choices, and schema patterns. Use when helping with schema validation, parsing, inference, JSON Schema, codecs, metadata, or migrating from Zod 3.
license: MIT
metadata:
  author: kjanat
  version: "1.0"
---

# Zod v4

Use for Zod 4 guidance, routing, and API selection.

## Scope and freshness

- Vendored sources come from `colinhacks/zod`, pinned in `references/source-index.md`.
- Prefer the current Zod 4 API surface represented by the vendored docs.
- If the user asks about changes newer than the pinned commit, state the freshness limit and recommend checking the latest upstream docs.
- For ordinary app code, prefer root imports:

```ts
import * as z from 'zod';
```

- Mention legacy subpaths like `"zod/v4"` only for migration or interoperability context.

## What to recommend by default

- Prefer `import * as z from "zod"` for normal Zod 4 usage.
- Prefer `z.object({...})` and direct schema composition.
- Prefer `safeParse()` at IO boundaries where invalid user input is expected.
- Prefer `parse()` when failure should throw and stop the current flow.
- Prefer `parseAsync()` / `safeParseAsync()` when async refinements or transforms are involved.
- Prefer `z.infer`, `z.input`, and `z.output` to explain type flow.
- Prefer unified `error` options for error customization.
- Prefer `.check()` when guiding users toward current refinement patterns.
- Prefer `zod/mini` only when bundle-size or tree-shaking constraints are material.
- Prefer `zod/v4/core` only for library authors and low-level internals.

Avoid leading with:

- Zod 3-era error APIs like `message`, `invalid_type_error`, `required_error`, or `errorMap`.
- `"zod/v4"` imports unless the topic is migration/history.
- `zod/v4/core` for ordinary application code.
- Sync parsing examples when the schema clearly has async behavior.
- `zod/mini` examples unless the user explicitly needs Mini semantics.

## Fast triage

```txt
What does the user need?
├─ General schema validation or app code
│  └─ docs/basics.mdx -> docs/api.mdx
├─ Schema API lookup
│  └─ docs/api.mdx
├─ Error messages or issue formatting
│  └─ docs/error-customization.mdx -> docs/error-formatting.mdx
├─ Metadata, registries, or codegen
│  └─ docs/metadata.mdx
├─ JSON Schema conversion
│  └─ docs/json-schema.mdx
├─ Encode/decode or bidirectional transforms
│  └─ docs/codecs.mdx
├─ Package selection
│  └─ references/package-cheatsheet.md -> package doc
├─ Migration from Zod 3
│  └─ references/gotchas.md -> docs/v4/changelog.mdx -> docs/v4/versioning.mdx
└─ Library author or internals
   └─ docs/library-authors.mdx -> docs/packages/core.mdx
```

## Current API guidance

- Use root `zod` imports for current Zod 4 examples unless migration context requires otherwise.
- Use `safeParse()` at IO boundaries and branch on `result.success`.
- Reach for `z.input<typeof Schema>` and `z.output<typeof Schema>` when transforms or codecs make input and output differ.
- Use `.check()` when guiding users toward current refinement patterns.
- Mention `z.toJSONSchema()` and `z.fromJSONSchema()` with the correct stability expectations. `fromJSONSchema` is experimental.
- Treat `zod/mini` as an optimization tradeoff, not the default.
- Route package questions through [package-cheatsheet.md](references/package-cheatsheet.md) first.
- Route migration questions through [gotchas.md](references/gotchas.md) before deep-diving into vendored docs.

## End-to-end example

Use a single inbound schema at the request boundary, then pass parsed output deeper into the app.

```ts
import * as z from 'zod';

const AddressSchema = z.object({
	line1: z.string().min(1, { error: 'Address line is required' }),
	city: z.string().min(1, { error: 'City is required' }),
	country: z.string().length(2, { error: 'Use a 2-letter country code' }),
});

const CreateUserSchema = z.object({
	email: z.email({ error: 'Valid email required' }).transform((value) => value.toLowerCase()),
	age: z.coerce.number().int().min(18, { error: 'Must be 18 or older' }),
	plan: z.enum(['free', 'pro']).default('free'),
	marketingOptIn: z.coerce.boolean().default(false),
	address: AddressSchema,
	tags: z.array(z.string().min(1)).max(5).default([]),
	referralCode: z.string().trim().optional(),
	username: z
		.string()
		.min(3)
		.check(z.minLength(3), z.maxLength(20)),
});

const UserIdCodec = z.codec(
	z.string().uuid(),
	z.object({ value: z.string().uuid() }),
	{
		decode: (value) => ({ value }),
		encode: (value) => value.value,
	},
);

const RegistrationEnvelopeSchema = z.object({
	requestId: UserIdCodec,
	user: CreateUserSchema,
});

type RegistrationEnvelopeInput = z.input<typeof RegistrationEnvelopeSchema>;
type RegistrationEnvelope = z.output<typeof RegistrationEnvelopeSchema>;

async function saveUser(user: RegistrationEnvelope['user']) {
	return {
		id: crypto.randomUUID(),
		email: user.email,
		plan: user.plan,
	};
}

export async function handleRegistration(body: unknown) {
	const result = await RegistrationEnvelopeSchema.safeParseAsync(body);

	if (!result.success) {
		const formatted = z.treeifyError(result.error);
		return {
			status: 400,
			error: formatted,
		};
	}

	const data = result.data;
	const saved = await saveUser(data.user);

	return {
		status: 201,
		requestId: data.requestId.value,
		user: saved,
	};
}

const incoming: RegistrationEnvelopeInput = {
	requestId: '550e8400-e29b-41d4-a716-446655440000',
	user: {
		email: 'USER@EXAMPLE.COM',
		age: '21',
		address: {
			line1: '1 Main St',
			city: 'Amsterdam',
			country: 'NL',
		},
	},
};
```

How to talk about this example:

- Construction: the schema composes nested objects, coercion, defaults, enum choices, transforms, and a codec.
- Consumption: `safeParseAsync()` is used at the request boundary because async parsing is the safe default once schemas may evolve to async checks.
- Type flow: `RegistrationEnvelopeInput` is the incoming shape, while `RegistrationEnvelope` is the parsed output. They differ because `age` is coerced, `email` is transformed, and `requestId` is decoded through a codec.
- Error handling: use `z.treeifyError()` or the formatting utilities when returning structured validation errors.
- Downstream use: service-layer functions should consume parsed output, not raw request payloads.

If the user does not need codecs or async behavior, simplify the example rather than introducing them unnecessarily.

## Response workflow

1. Identify whether the question is app usage, migration, package choice, advanced feature, or library-author internals.
2. Default to current Zod 4 root-import examples.
3. Answer directly with the preferred API first.
4. Attach exact vendored doc paths for the topic.
5. If migration-related, mention replacement APIs and deprecated patterns explicitly.
6. If package-choice-related, explain why `zod` vs `zod/mini` vs `zod/v4/core` is the right lane.

## Reading Order

| Task                             | Files to read                                                                  |
| -------------------------------- | ------------------------------------------------------------------------------ |
| New to Zod 4                     | `SKILL.md` -> `docs/basics.mdx` -> `docs/api.mdx`                              |
| Validate request data            | `SKILL.md` -> `docs/basics.mdx`                                                |
| Look up schema APIs              | `docs/api.mdx`                                                                 |
| Customize errors                 | `docs/error-customization.mdx` -> `docs/error-formatting.mdx`                  |
| Work with metadata or registries | `docs/metadata.mdx`                                                            |
| Convert to/from JSON Schema      | `docs/json-schema.mdx`                                                         |
| Use codecs                       | `docs/codecs.mdx`                                                              |
| Choose a package                 | `references/package-cheatsheet.md`                                             |
| Migrate from Zod 3               | `references/gotchas.md` -> `docs/v4/changelog.mdx` -> `docs/v4/versioning.mdx` |
| Build on top of Zod              | `docs/library-authors.mdx` -> `docs/packages/core.mdx`                         |
| Check freshness or provenance    | `references/source-index.md`                                                   |

## In This Reference

| File                               | Purpose                                                               |
| ---------------------------------- | --------------------------------------------------------------------- |
| `references/routing-map.md`        | Topic to vendored doc path routing                                    |
| `references/gotchas.md`            | Current replacements, migration pitfalls, and high-frequency mistakes |
| `references/package-cheatsheet.md` | When to use `zod`, `zod/mini`, or `zod/v4/core`                       |
| `references/source-index.md`       | Provenance, version pin, sync date, and refresh instructions          |

## Scripts

| Script                 | Purpose                                                                         |
| ---------------------- | ------------------------------------------------------------------------------- |
| `scripts/sync-docs.sh` | Vendor docs from `colinhacks/zod`, then regenerate routing and provenance files |

## Vendored content

- `docs/` mirrors `packages/docs/content` from the upstream Zod docs repo.
- Vendored content is narrative/reference material. The skill-level recommendations above remain the default guidance for models.
- Excludes the docs site implementation, components, app code, public assets, and blog content.
