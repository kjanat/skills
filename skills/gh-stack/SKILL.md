---
name: gh-stack
description: Manage stacked branches and dependent pull requests with the GitHub `gh stack` CLI extension. Use for planning, creating, adopting, pushing, submitting, inspecting, navigating, rebasing, syncing, restructuring, checking out, linking, or merging stacked diffs and linear branch chains, including conflict recovery and incremental review workflows.
---

# Manage GitHub PR stacks

Use `gh stack` to manage a linear chain in which every branch builds on the branch below it and maps to a PR whose base is that lower branch. Treat the branch nearest trunk as the bottom and the furthest branch as the top.

## Inspect before changing

1. Confirm the repository, worktree status, current branch, remotes, and authentication.
2. Run `gh stack view --json` when local stack state exists. Never run the interactive view.
3. Determine the trunk and order branches from foundational changes at the bottom to dependent changes at the top.
4. Preserve unrelated working-tree changes. Use ordinary `git add <paths>` and `git commit` to keep each layer deliberate.

Install the extension only when missing:

```bash
gh extension install github/gh-stack
```

Prevent prompts before stack operations:

```bash
git config rerere.enabled true
git config remote.pushDefault origin
```

If the repository uses another push remote, configure that actual remote instead. For commands supporting `--remote`, prefer passing the resolved remote explicitly when multiple remotes exist.

## Keep every invocation non-interactive

- Supply branch names to `gh stack init` and `gh stack add`.
- Supply a branch, PR URL/number, or stack number to `gh stack checkout`.
- Always run `gh stack submit --auto`; add `--open` only when PRs should be ready rather than drafts.
- Always run `gh stack view --json`; never use `view`, `view --short`, or its TUI.
- Run `gh stack merge --yes` and explicitly select `--squash`, `--rebase`, or `--merge` when the desired merge method is known.
- Do not use `gh pr merge` for a stack.
- Never invoke a command that can prompt and then wait for it. If no non-interactive path exists, stop and explain the blocker.

`push`, `submit`, `sync`, `rebase`, and `link` accept `--remote`. `checkout`, `trunk`, and `modify` do not; they rely on `remote.pushDefault`.

## Plan and build a stack

Keep one cohesive story per stack. Put shared models, schemas, APIs, and utilities lower than their consumers, UI, integration tests, or documentation. Create a separate stack for unrelated work.

For a new stack:

```bash
gh stack init --base main models
git add src/models
git commit -m "Add shared models"

gh stack add api
git add src/api
git commit -m "Add API endpoints"

gh stack add ui
git add src/ui
git commit -m "Add UI"

gh stack submit --auto
gh stack view --json
```

Resolve the actual trunk rather than assuming `main`. Existing branches may be adopted by passing them bottom-to-top to `init`.

## Change a lower layer

When work on a higher branch reveals a lower-layer change:

1. Navigate to the branch where the change logically belongs with `down`, `bottom`, or `checkout <branch>`.
2. Edit, stage, test, and commit there.
3. Run `gh stack rebase --upstack` to replay dependent branches.
4. Return to the original layer and continue.
5. Push or submit the updated stack.

Do not hide lower-layer changes in an upper PR.

## Synchronize and recover

Use `gh stack sync` for routine fetch/rebase/push/PR-state synchronization. Add `--prune` only when deleting local branches for merged PRs is intended.

If a rebase exits with code 3:

1. Inspect reported paths and conflict markers.
2. Resolve each conflict without discarding unrelated edits.
3. Stage resolved files with `git add <paths>`.
4. Run `gh stack rebase --continue`.
5. Repeat or run `gh stack rebase --abort` to restore the pre-rebase state.

If local and GitHub stack compositions diverge, non-interactive `sync` may print `Sync aborted` while exiting successfully. Treat that message as failure, inspect both chains, then deliberately rebuild tracking rather than assuming success.

If checkout would trigger an unbypassable local/remote composition prompt, run `gh stack unstack --local` first, then retry the explicit checkout. This retains the GitHub stack.

## Restructure, link, and merge

- To remove, reorder, or rename layers, use `gh stack unstack`, make the branch changes, then recreate the chain with `gh stack init --base <trunk> <bottom...top>`.
- To keep external tooling such as jj or Sapling in control of local branches, use `gh stack link <bottom...top>`; it creates no local stack tracking.
- To append to an existing remote stack, use `gh stack link <stack-number> <new-pr-or-branch...>`.
- Merge bottom-to-top atomically with `gh stack merge [stack-or-pr] --yes --<method>`. If merge requirements fail, no PR is merged. With a merge queue, the queue controls the merge method and may land PRs in separate groups.

## Handle safety and errors

- Branches shared by multiple stacks cause exit code 6. Check out a non-shared branch before retrying.
- Exit code 8 means another stack process holds the lock; retry after the short lock timeout.
- Exit code 9 means stacked PRs are unavailable for the repository; report that stacks must be enabled.
- Exit code 10 means interrupted `modify` recovery; run `gh stack modify --abort` because this workflow does not use `modify`.
- Treat partial pushes as partial remote mutation. Inspect state and safely rerun rather than assuming atomicity.
- Never delete branches or PRs merely to repair stack metadata unless the user explicitly requests deletion.

## Load detailed reference only when needed

Read [references/commands.md](references/commands.md) for exact command forms, flags, JSON fields, exit codes, output behavior, limitations, and recovery notes when executing or diagnosing a specific `gh stack` operation.
