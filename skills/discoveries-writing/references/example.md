# DISCOVERIES.md Example

Use this as a default template, then adapt section names to the repo.

## Minimal Template

```markdown
# Discoveries

> Non-obvious gotchas, surprising behaviors, and hard-won lessons from this
> codebase. For autonomous agents: consult this file before debugging
> unexpected behavior or repeating patterns already known to be tricky.

## Build & Tooling

- `tree-sitter generate` must run before `npm install` in this repo because the
  install step expects generated parser sources to already exist.

## Framework

- `useTask` must be called during component initialization, not inside an
  effect. Registering it later silently misses the framework's setup phase.

## Testing

- `bun test` bypasses the compilation path this project needs. Use
  `bun run test` so the framework plugin pipeline is active.
```

## Longer Incident-Style Example

Use this when one migration or subsystem produced multiple connected findings.

```markdown
# Discoveries

## RustCrypto Generation Bump

Upgrading this stack requires an atomic version jump across the shared trait
ecosystem.

### Dependency cascade forces atomic upgrade

Partial upgrades duplicate core traits across crate generations, producing
errors that look like incorrect types even when the names match.

### `OsRng` is gone

- `rand_core` removed `OsRng`; use the replacement pattern already adopted in
  this repo instead of trying to restore the old import shape.
```

## Heuristics

- Prefer bullets when the lesson fits in one pass
- Prefer subsections when symptom, cause, and fix all matter
- Use exact identifiers when the discovery depends on them
- Keep the conclusion; cut the play-by-play

## Decision Test

Add the note only if at least one of these is true:

- A competent agent would likely make the same wrong assumption
- The failure mode is expensive to rediscover
- The fix is unintuitive but reliable
- The behavior differs from common ecosystem expectations

Do not add the note if it is just:

- a changelog item
- a task log
- a design preference with no trap attached
- a fact already obvious from reading the file being edited
