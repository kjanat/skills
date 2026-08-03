# `gh stack` command reference

Use this reference when exact flags or behavior matter. Commands are non-interactive unless a warning says otherwise.

## Command map

| Task                          | Command                                                 |
| ----------------------------- | ------------------------------------------------------- |
| Create/adopt a stack          | `gh stack init [--base trunk] <bottom...top>`           |
| Add a top branch              | `gh stack add <branch>`                                 |
| Add, stage all, commit        | `gh stack add -Am "message" <branch>`                   |
| Push branches                 | `gh stack push [--remote name]`                         |
| Create/update draft PRs       | `gh stack submit --auto [--remote name]`                |
| Mark PRs ready                | `gh stack submit --auto --open`                         |
| Inspect state                 | `gh stack view --json`                                  |
| Routine synchronization       | `gh stack sync [--remote name] [--prune]`               |
| Rebase all                    | `gh stack rebase [--remote name]`                       |
| Rebase current and above      | `gh stack rebase --upstack`                             |
| Rebase trunk through current  | `gh stack rebase --downstack`                           |
| Rebase branches without trunk | `gh stack rebase --no-trunk`                            |
| Continue/abort conflict       | `gh stack rebase --continue` / `--abort`                |
| Navigate                      | `gh stack up [n]`, `down [n]`, `top`, `bottom`, `trunk` |
| Explicit checkout             | `gh stack checkout <stack                               |
| Remove current stack grouping | `gh stack unstack`                                      |
| Remove remote stack grouping  | `gh stack unstack <stack-number>`                       |
| Remove local tracking only    | `gh stack unstack --local`                              |
| Link without local tracking   | `gh stack link [--base trunk] <bottom...top>`           |
| Append to remote stack        | `gh stack link <stack-number> <new-items...>`           |
| Merge current stack           | `gh stack merge --yes --squash`                         |
| Merge through a PR            | `gh stack merge <pr-number> --yes --squash`             |
| Merge remote stack            | `gh stack merge <stack-number> --yes --squash`          |

## Initialization and adding branches

`init` creates missing branches, adopts existing branches, checks out the final branch, and enables rerere. Names are used verbatim, including slashes. Always provide at least one branch.

`add` creates a branch above the current top layer. It exits with code 5 if run from a non-top branch. Without `-A` or `-u`, working-tree changes carry to the new branch. `-A` and `-u` require `-m` and are mutually exclusive. Prefer ordinary Git staging for precise layers.

## Push and submit behavior

`push` updates active non-merged, non-queued branches using per-branch force-with-lease checks. The multi-ref operation may be partially successful.

`submit --auto` pushes active branches, creates missing PRs, corrects bases, and links PRs as a GitHub stack. New PRs are drafts unless `--open` is passed. A single-commit branch uses its commit subject/body; a multi-commit branch derives its title from the branch name. Edit metadata afterward with `gh pr edit` if needed.

If stacked PRs are disabled, non-interactive submit exits 9. If all prior PRs are merged, unmerged branches are forked into a new stack rooted at trunk.

## Linking behavior

Provide arguments bottom-to-top. Each may be a branch or PR number. A first numeric argument matching a stack number selects that stack and appends later items. Branches are pushed atomically without force; missing PRs are created and incorrect PR bases are corrected. `link` does not create local tracking and is additive: it never removes existing PRs.

## Synchronization order

`sync` performs:

1. Fetch remote state.
2. Reconcile the remote stack locally.
3. Fast-forward trunk when possible.
4. Cascade-rebase active layers when trunk moved.
5. Push active branches.
6. Refresh PR state.
7. Create/update the GitHub stack object when at least two PRs exist.
8. Prune merged local branches only with explicit `--prune` in non-interactive use.

On rebase conflict, it restores all branches and exits 3. On local/remote stack divergence, non-interactive mode may abort without changes but exit 0; inspect stderr for `Sync aborted`.

## Rebase behavior

`--upstack` rebases current-to-top; `--downstack` rebases trunk-to-current; `--no-trunk` skips fetching and rebasing against trunk. Merged and squash-merged lower PRs are detected and remaining commits are replayed with `--onto`. Rerere reuses recorded conflict resolutions.

## JSON inspection

`gh stack view --json` writes data to stdout and status to stderr. Its shape is:

```json
{
  "trunk": "main",
  "currentBranch": "api",
  "branches": [
    {
      "name": "models",
      "head": "abc123",
      "base": "def456",
      "isCurrent": false,
      "isMerged": false,
      "isQueued": false,
      "needsRebase": false,
      "pr": { "number": 42, "url": "https://github.com/o/r/pull/42", "state": "OPEN" }
    }
  ]
}
```

`pr` is omitted when none exists. PR state is `OPEN`, `MERGED`, or `QUEUED`. Use `2>/dev/null` only when deliberately discarding diagnostic status.

## Checkout and unstack

A bare checkout number resolves as stack number, then PR number, then branch. Stack/PR/URL checkout fetches remote stack state; branch-name checkout uses local tracking only. Always supply an argument.

`unstack` removes grouping/tracking but does not delete PRs or branches. No argument targets the active stack locally and remotely; a stack number targets GitHub directly; `--local` retains GitHub state.

## Merge behavior

Use `gh stack merge`, not `gh pr merge`. `--yes` makes intent explicit. Scope with a PR number to merge through that layer or a stack number to merge a remote stack. Select `--squash`, `--rebase`, `--merge`, or `--merge-method <method>`. The direct operation is all-or-nothing and checks that PRs are open and not drafts. It cannot bypass merge requirements. Under merge queue, method flags are ignored and queued PRs may land in separate groups.

## Exit codes

| Code | Meaning                         | Recovery                                                  |
| ---: | ------------------------------- | --------------------------------------------------------- |
|    0 | Success                         | Also inspect status text for a deliberately aborted sync. |
|    1 | Generic Git/operation error     | Read stderr and inspect local/remote state.               |
|    2 | Not in a stack / unknown target | Initialize, checkout, or correct the target.              |
|    3 | Rebase conflict                 | Resolve, stage, and continue; otherwise abort.            |
|    4 | GitHub API failure              | Check `gh auth status`, then retry safely.                |
|    5 | Invalid invocation/state        | Correct arguments or navigate to the top.                 |
|    6 | Ambiguous shared branch         | Check out a branch belonging to one stack.                |
|    7 | Rebase already active           | Continue or abort it.                                     |
|    8 | Stack lock held                 | Retry after the five-second timeout.                      |
|    9 | Stacked PRs unavailable         | Ask for stacks to be enabled on the repository.           |
|   10 | Interrupted modify              | Run `gh stack modify --abort`.                            |

## Limitations

- Stacks are strictly linear; use separate stacks for parallel children.
- Shared branches can make stack resolution ambiguous.
- Multiple remotes require `remote.pushDefault` for commands lacking `--remote`.
- Remote checkout needs a stack number, PR number, or PR URL; branch names resolve locally only.
- Submit cannot set custom PR titles/bodies directly.
- Push and submit may update some branches before another branch fails.
