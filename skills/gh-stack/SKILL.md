---
name: gh-stack
description: Manages linear branch stacks and dependent pull requests with the GitHub `gh stack` CLI extension. Use when planning, creating, adopting, splitting, inspecting, navigating, editing, pushing, submitting, syncing, rebasing, restructuring, linking, checking out, or diagnosing stacked PRs, or whenever the user mentions stack layers, dependent PRs, or `gh stack`.
compatibility: Requires Git, GitHub CLI, and the `github/gh-stack` extension.
---

# Manage GitHub PR stacks

Use `gh stack` for a linear chain in which each branch builds on the branch
below it and each PR targets that lower branch.

```text
(trunk) <- models <- api <- ui
            bottom          top
```

`up` moves toward the top; `down` moves toward trunk. A stack is linear, so
parallel children require separate stacks.

## Inspect before changing

1. Confirm the repository, worktree status, current branch, remotes, and
   `gh auth status`.
2. Preserve staged and unstaged user changes. Do not clean, unstage, or rewrite
   them unless explicitly requested.
3. Run `gh stack view --json` when local stack state exists. Treat it as the
   canonical machine-readable view.
4. Resolve the actual trunk and push remote rather than assuming `main` and
   `origin`.
5. Before any push or submit, inspect applicable branch rules and the exact
   branches and PRs that will change.

Install the extension only when missing:

```bash
gh extension install github/gh-stack
```

When multiple remotes exist, pass `--remote <name>` where supported or set the
repository's intended push remote:

```bash
git config remote.pushDefault <name>
```

## Keep automation non-interactive

| Operation  | Automation-safe form                                |
| ---------- | --------------------------------------------------- |
| Inspect    | `gh stack view --json` (preferred) or `--short`     |
| Initialize | `gh stack init --base <trunk> <bottom> ... <top>`   |
| Add        | `gh stack add <branch>`                             |
| Submit     | `gh stack submit --auto [--open] [--remote <name>]` |
| Checkout   | `gh stack checkout <stack-or-pr-or-branch>`         |
| Merge      | `gh stack merge <target> --yes --<method>`          |

Bare `view`, argumentless `init`, `add`, or `checkout`, and `submit` without
`--auto` may prompt. `modify` is a TUI-only workflow and has no non-interactive
mode. Never launch an interactive command and leave it waiting for input.

## Route the task

| Task                                                | Read first                                          |
| --------------------------------------------------- | --------------------------------------------------- |
| Plan a new stack or split existing work             | [stack-design.md](references/stack-design.md)       |
| Execute or verify a command                         | [commands.md](references/commands.md)               |
| Resolve conflicts, divergence, or interrupted state | [troubleshooting.md](references/troubleshooting.md) |

Read only the references needed for the task. For restructuring, read both
stack design and troubleshooting before changing ancestry or metadata.

## Build and edit deliberately

For new work, create the intended layer before writing it when practical:

```bash
gh stack init --base <trunk> <bottom-branch>
# edit, stage exact paths, test, commit
gh stack add <next-branch>
# edit, stage exact paths, test, commit
```

Put shared types, schemas, APIs, and utilities below their consumers. Keep one
cohesive story per stack and put unrelated work in another stack.

When a higher layer needs a lower-layer correction:

1. Determine the owning layer. If unclear, inspect `git log --all -- <path>`.
2. Navigate to it with `down`, `bottom`, or `checkout <branch>`.
3. Edit, stage exact paths, test, and commit there.
4. Run `gh stack rebase --upstack` to replay dependent layers.
5. Return to the previous layer, verify the stack, then push or submit.

Do not hide a foundational change in an upper PR merely to avoid a rebase.

## Control generated PR bodies

`gh stack submit` can add a GitHub Stacks CLI attribution footer when it creates
a PR without a non-empty repository PR template, and the inspected CLI has no
opt-out flag. If the footer is unacceptable or the user wants full control of
every PR body:

1. Push the stack with `gh stack push --remote <name>`.
2. Create each missing PR explicitly with `gh pr create`, using the parent
   branch as `--base` and the layer branch as `--head`.
3. Run `gh stack submit --auto --remote <name>` to link and update those
   existing PRs.

A non-empty default PR template also prevents the generated footer path, but it
replaces the generated commit-derived body. Pre-creating PRs is the explicit,
predictable option. See [commands.md](references/commands.md) for details.

## Synchronize and recover safely

Use `gh stack sync --remote <name>` for routine fetch, rebase, push, and PR-state
reconciliation. Add `--prune` only when local deletion of merged branches is
explicitly intended.

Exit code 3 needs different handling by command:

- Failed `rebase`: resolve, stage, then `gh stack rebase --continue`, or abort.
- Failed `sync`: sync already restores all branches. Run `gh stack rebase` to
  recreate the conflict, then resolve and continue.

If local and GitHub stack compositions diverge, non-interactive `sync` can print
`Sync aborted` while exiting 0. Inspect output as well as the exit code.

## Respect mutation boundaries

- `push`, `submit`, `sync`, `link`, and `merge` can mutate remote state; run only
  the operation the user authorized and verify the resulting state.
- `submit` is not status-only: it may push branches, create PRs, correct bases,
  and update stack metadata. Preflight it accordingly.
- A request to commit, push, submit, publish, or fix checks does not authorize a
  merge, merge queue, or auto-merge. Run `gh stack merge` only when governing
  instructions permit it and the user explicitly requests that exact action.
- Never bypass branch protection or required workflows. Treat a reported bypass
  as failure and stop further remote mutation.
- Never delete branches or PRs merely to repair stack metadata unless deletion
  is explicitly requested.
- Push and submit are not transactionally all-or-nothing. After failure, inspect
  local branches, remote refs, PR bases, and stack state before retrying.

After any remote mutation, verify independently with `gh stack view --json` and
targeted `gh pr view` or `gh pr list` queries.
