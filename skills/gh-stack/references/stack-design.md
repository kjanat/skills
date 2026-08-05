# Stack design and decomposition

Read this before creating a stack, splitting an existing change, or changing
layer boundaries. Stack metadata describes branch relationships; it does not
move commits or files between branches.

## Plan the dependency chain

Write one sentence for each proposed layer: “This PR introduces X so the next
PR can add Y.” Order layers from foundations to consumers:

```text
(trunk) <- shared types <- service/API <- UI <- integration/docs
```

Good lower layers are independently reviewable and establish contracts used by
higher layers. Avoid placing a dependency above its consumer or spreading one
concept across several layers without a review benefit.

Use one stack for one cohesive story. Put unrelated work in a separate stack.
A tiny incidental correction may ride with its owning layer when separating it
would create more review cost than value.

## Name related branches consistently

Follow repository and user conventions first. If none exist, use a stable topic
plus a layer concern, for example:

```text
runner/version-core
runner/version-cli
runner/version-docs
```

## Create new work bottom-to-top

Prefer creating the layer before writing its changes:

```bash
gh stack init --base <trunk> <topic>/<foundation>
# implement, stage exact paths, test, commit
gh stack add <topic>/<consumer>
# implement, stage exact paths, test, commit
```

This makes ownership clear and reduces later history surgery. Multiple commits
inside a layer are fine when they help development; the PR boundary is the
branch range, not a requirement for one commit.

Use deliberate staging. `gh stack add -Am` is convenient but broad; ordinary
`git add <paths>` and `git commit` are safer when the worktree contains user
changes or more than one layer's edits.

## Adopt an existing linear chain

Before adopting branches, verify their actual ancestry and order:

```bash
git log --graph --decorate --oneline --all
git merge-base --is-ancestor <lower> <higher>
gh stack init --base <trunk> <bottom> <middle> <top>
```

Pass branches bottom-to-top. `init` records the chain and checks out the final
branch; it does not make non-linear history linear. Rebase or otherwise rewrite
commits first when ancestry is wrong, and do so only within the user's requested
scope.

## Split one branch into layers

For existing work concentrated on one branch:

1. Confirm the desired layer boundaries and preserve the current branch name.
2. Identify commit or file ownership for each layer.
3. Save boundary commit IDs before rewriting history.
4. Create or adopt the bottom branch at the foundational boundary.
5. Create subsequent branches at later boundaries, preserving bottom-to-top
   ancestry.
6. Verify each diff against its parent with `git diff <parent>...<branch>`.
7. Initialize or link the resulting chain only after ancestry is correct.

If the work is not already separable by commits, use the least destructive Git
rewrite compatible with the user's workspace. Do not silently discard, unstage,
or redistribute uncommitted changes.

## Extend an existing stack

Navigate to the top before adding a locally tracked layer:

```bash
gh stack top
gh stack add <topic>/<new-concern>
```

`add` exits 5 from any non-top branch. To append remote-only layers or keep
another tool in charge of local branches, use `gh stack link <stack-number>
<new-items...>` instead.

## Place fixes in the owning layer

When a higher layer exposes a lower-layer bug:

1. Inspect which layer introduced the affected contract or path.
2. Use `git log --all -- <path>` and parent-relative diffs when ownership is
   unclear.
3. Navigate to that layer, make and commit the smallest complete correction.
4. Rebase upward and rerun relevant checks on affected descendants.

Avoid duplicate fixes in multiple branches and avoid moving foundational work
upward merely to keep the current checkout unchanged.

## Decide between tracked and linked stacks

Use locally tracked stacks when `gh stack` should own navigation, rebasing, and
sync. Use `link` when jj, Sapling, worktrees, or another workflow owns local
ancestry and only GitHub stack metadata is needed.

`link` is additive and creates no local tracking. `unstack` removes grouping or
tracking but does not delete PRs or branches. If the goal is restructuring,
rewrite ancestry first and then rebuild metadata; changing metadata alone
cannot change the commit graph.

## Pre-publication checklist

- Every layer has one clear review purpose.
- Each branch contains its parent plus only that layer's intended delta.
- Dependencies point upward, never downward.
- Branch names follow user or repository conventions.
- Relevant tests pass at the layers where their prerequisites exist.
- The intended trunk, remote, draft state, PR titles, and PR bodies are known.
- Branch rules have been inspected and no bypass is planned.
- If `submit` would create PRs, the generated-footer behavior is acceptable or
  the PRs will be pre-created explicitly.
