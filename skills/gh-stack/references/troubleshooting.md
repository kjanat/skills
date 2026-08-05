# Troubleshooting `gh stack`

Use this reference for conflicts, divergent stack composition, interrupted
operations, and restructuring. Preserve the worktree and gather evidence before
rewriting history or changing remote state.

## First-response checklist

1. Record `git status --short --branch` and `gh stack view --json`.
2. Identify whether the failing command mutated local branches, remote refs,
   PRs, or stack metadata before failing.
3. Preserve user changes and save important boundary commit IDs.
4. Read the full diagnostic output; do not infer success from exit code alone.
5. Choose the command-specific recovery below.

## Direct rebase conflict: exit 3

A failed `gh stack rebase` leaves a rebase in progress:

1. Inspect conflicted paths and markers.
2. Resolve without discarding unrelated edits.
3. Stage only resolved paths with `git add <paths>`.
4. Run `gh stack rebase --continue`.
5. Repeat until complete, then inspect every affected layer.

Use `gh stack rebase --abort` to restore the pre-rebase stack. Exit 7 means a
rebase is already active; continue or abort it instead of starting another.

## Sync conflict: exit 3

A failed `gh stack sync` behaves differently: it restores all branches before
returning. There is no sync-specific conflict state to continue.

1. Confirm the stack was restored.
2. Run `gh stack rebase [--remote <name>]` to recreate the conflict.
3. Resolve, stage, and use `gh stack rebase --continue`.
4. Rerun sync only after the rebase and checks succeed.

Do not run `rebase --continue` immediately after a failed sync unless Git proves
a rebase is active.

## Local and GitHub composition diverged

Non-interactive sync can print `Sync aborted` while exiting 0. Treat that text
as failure. Compare:

- local ancestry and local `gh stack view --json`;
- GitHub PR bases and stack membership;
- remote branch heads.

Then choose deliberately:

- GitHub is authoritative: unstack local tracking only, then explicitly check
  out the remote stack.
- Local ancestry is authoritative: correct the commit graph, then recreate or
  relink stack metadata.
- Both contain required work: preserve boundary SHAs and reconcile history
  before changing either stack description.

If explicit checkout would prompt over the mismatch, `gh stack unstack --local`
retains GitHub state while removing local tracking. This is a metadata change,
not a branch deletion.

## Restructure, remove, or reorder layers

Before rewriting, save each old layer boundary:

```bash
git rev-parse <branch>
git merge-base <lower> <higher>
```

Then:

1. Remove only the obsolete stack grouping with `unstack` if needed.
2. Rewrite, rename, create, or reorder branches using normal Git operations.
3. Verify ancestry with `git merge-base --is-ancestor` and parent-relative
   diffs.
4. Recreate tracking with `init` or remote-only metadata with `link`.
5. Inspect PR bases before submitting updates.

Metadata cannot repair incorrect ancestry. Never delete branches or PRs as a
shortcut unless the user explicitly requested deletion.

## Squash-merged lower PR

When a lower PR was squash-merged, descendant branches still contain the old
individual commits even though trunk has a new squash commit. `gh stack rebase`
detects merged and squash-merged lower PRs and replays remaining commits with an
appropriate `--onto` boundary.

Before manually dropping commits, let the stack rebase inspect merged state.
Afterward verify descendant diffs against their new parents so already-merged
changes do not reappear.

## Partial push or submit

`push` and `submit` can update some branches or create some PRs before a later
step fails. Do not blindly rerun.

1. Compare local and remote heads for each layer.
2. List PRs by head branch and inspect their bases and draft state.
3. Inspect current stack membership.
4. Retry only the idempotent remaining operation.

If an unwanted attribution footer was created, do not assume submit can remove
it. With explicit authorization, edit the affected existing PR body using
`gh pr edit`; for future PRs, pre-create them before submit as described in
[commands.md](commands.md).

## Shared branch: exit 6

A branch shared by multiple stacks makes active-stack resolution ambiguous.
Check out a branch unique to the intended stack, or provide an explicit stack
or PR target where supported. Do not detach or delete the shared branch simply
to silence the error.

## Another process holds the lock: exit 8

Wait for the short lock timeout and verify no live `gh stack` process still owns
the operation. Retry only after the owner finishes. Do not remove lock state
manually without proving it is stale and understanding the recovery format.

## Interrupted `modify`: exit 10

`modify` is TUI-only and unsupported for non-interactive automation. If an old
session left recovery state, run:

```bash
gh stack modify --abort
```

Then use explicit Git operations plus `init`, `link`, or `rebase` to perform the
intended change.

## External ancestry tools and worktrees

When jj, Sapling, worktrees, or another system owns local branches, avoid
competing local stack metadata. Use `gh stack link` to describe the remote PR
chain without local tracking. Continue to pass items bottom-to-top and verify
PR bases independently.

## Other exit codes

| Code | Meaning | Next action |
| ---: | --- | --- |
| 1 | Generic Git or operation error | Inspect diagnostics and mutation scope. |
| 2 | Unknown target or not in a stack | Correct target, initialize, or checkout. |
| 4 | GitHub API failure | Check auth and remote state before retrying. |
| 5 | Invalid invocation or state | Correct flags or navigate to the top. |
| 9 | Stacked PRs unavailable | Report that repository stacks must be enabled. |

After recovery, rerun relevant tests and verify local ancestry, remote refs, PR
bases, draft state, and stack membership. Recovery is complete only when all of
those agree.
