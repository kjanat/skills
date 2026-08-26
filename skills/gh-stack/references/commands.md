# `gh stack` command reference

Use this reference for exact command forms and side effects. Prefer explicit
targets and remotes in automation.

Behavioral baseline: [`github/gh-stack` commit `14fc42ed9b6c376a53b2f999f138d3bd26dac546`](https://github.com/github/gh-stack/tree/14fc42ed9b6c376a53b2f999f138d3bd26dac546).
Check the installed command's `--help` when its version differs.

## Command map

| Task                                 | Command                                                 |
| ------------------------------------ | ------------------------------------------------------- |
| Create or adopt a stack              | `gh stack init [--base <trunk>] <bottom> ... <top>`     |
| Add a top branch                     | `gh stack add <branch>`                                 |
| Add, stage all, and commit           | `gh stack add -Am "message" <branch>`                   |
| Push branches                        | `gh stack push [--remote <name>]`                       |
| Create or update draft PRs           | `gh stack submit --auto [--remote <name>]`              |
| Mark PRs ready                       | `gh stack submit --auto --open [--remote <name>]`       |
| Inspect machine-readable state       | `gh stack view --json`                                  |
| Inspect compact human-readable state | `gh stack view --short`                                 |
| Synchronize                          | `gh stack sync [--remote <name>] [--prune]`             |
| Rebase all                           | `gh stack rebase [--remote <name>]`                     |
| Rebase current through top           | `gh stack rebase --upstack`                             |
| Rebase trunk through current         | `gh stack rebase --downstack`                           |
| Rebase without updating trunk        | `gh stack rebase --no-trunk`                            |
| Continue or abort a rebase           | `gh stack rebase --continue` / `--abort`                |
| Navigate                             | `gh stack up [n]`, `down [n]`, `top`, `bottom`, `trunk` |
| Explicit checkout                    | `gh stack checkout <stack-or-pr-or-branch>`             |
| Remove current stack grouping        | `gh stack unstack`                                      |
| Remove remote stack grouping         | `gh stack unstack <stack-number>`                       |
| Remove local tracking only           | `gh stack unstack --local`                              |
| Link without local tracking          | `gh stack link [--base <trunk>] <bottom> ... <top>`     |
| Append to a remote stack             | `gh stack link <stack-number> <new-items...>`           |
| Merge through a target               | `gh stack merge <target> --yes --<method>`              |

## Initialize and add branches

`init` creates missing branches, adopts existing branches, records the chain
bottom-to-top, checks out the final branch, and enables Git rerere. Always pass
at least one branch in automation. Existing ancestry should already match the
declared order; stack metadata does not rewrite commits.

`add` creates a branch above the current top layer. It exits 5 from a non-top
branch. Without `-A` or `-u`, working-tree changes carry onto the new branch.
`-A` and `-u` require `-m` and are mutually exclusive. Prefer ordinary `git
add <paths>` and `git commit` when precise layer ownership matters.

## Push behavior

`push` updates active, non-merged, non-queued branches with per-branch
force-with-lease protection. The operation is not atomic across the whole
stack: some refs may update before a later ref fails. Inspect remote refs before
retrying.

Use `--remote <name>` when the remote is ambiguous. Commands without that flag
use `remote.pushDefault`.

## Submit behavior

`submit --auto` can:

1. Push active branches sequentially.
2. Create missing PRs.
3. Correct each PR base to the branch below it.
4. Link the PRs as a GitHub stack.

New PRs are drafts unless `--open` is passed; `--open` also marks existing draft
PRs ready. A single-commit branch derives title and body from that commit. A
multi-commit branch derives its title from the branch name. The first PR targets
the first non-merged ancestor. If all earlier PRs are merged, remaining work is
forked into a new stack rooted at trunk.

Submission is not atomic. A failure can leave pushed branches or created PRs.
Afterward, verify PR existence, draft state, bases, and stack membership rather
than assuming rollback. Exit 9 means stacked PRs are unavailable in the
repository.

### Avoid the generated attribution footer

When `submit` creates a PR and no non-empty default PR template is available,
its generated body path appends a GitHub Stacks CLI attribution footer. The
inspected implementation provides no `--no-footer` option. It preserves bodies
of existing PRs.

For exact PR bodies:

```bash
gh stack push --remote <remote>
gh pr create --base <parent> --head <branch> --title <title> --body-file <path>
# Repeat bottom-to-top for every branch that lacks a PR.
gh stack submit --auto --remote <remote>
```

Use the actual trunk as the bottom PR's parent. For later layers, use the branch
immediately below. Add `--open` only if all stack PRs should be ready for review.
A non-empty repository PR template also skips the generated-body/footer path,
but the new PR body then starts from that template rather than commit text.

## Link behavior

Pass items bottom-to-top. Each item may be a branch or PR number. If the first
numeric argument matches a stack number, `link` selects that stack and appends
later items. Branch inputs are pushed without force; missing PRs are created and
incorrect bases are corrected.

`link` creates no local stack tracking and is additive: it does not remove
existing PRs. Use it when another tool owns local branch ancestry or when
appending layers to an existing GitHub stack.

## Synchronization order

`sync` performs the following logical sequence:

1. Fetch remote state.
2. Reconcile the remote stack locally.
3. Fast-forward trunk when possible.
4. Cascade-rebase active layers when trunk moved.
5. Push active branches.
6. Refresh PR state.
7. Create or update the GitHub stack object when at least two PRs exist.
8. Prune merged local branches only with explicit `--prune` in automation.

On rebase conflict, `sync` restores all branches and exits 3. To resolve it, run
`gh stack rebase` to recreate the conflict, then resolve, stage, and continue.
On local/remote composition divergence, non-interactive sync may print `Sync
aborted` without changes and still exit 0; inspect output text.

## Rebase behavior

`--upstack` rebases current-to-top; `--downstack` rebases trunk-to-current;
`--no-trunk` skips fetching and rebasing against trunk. Merged and squash-merged
lower PRs are detected and remaining commits are replayed with `--onto`. Rerere
can reuse recorded conflict resolutions.

A direct rebase conflict leaves the rebase active. Resolve files, stage them,
and run `gh stack rebase --continue`; repeat as needed. Use `--abort` to restore
the pre-rebase state.

## View and navigation

`view --json` writes structured state to stdout and status diagnostics to
stderr. The object includes `trunk`, `currentBranch`, and `branches`; each branch
includes its name, head/base commits, current/merged/queued/rebase flags, and an
optional PR object. PR state is `OPEN`, `MERGED`, or `QUEUED`. `view` may perform
a best-effort refresh before rendering, so do not treat it as guaranteed
network-free.

`view --short` is non-interactive but human-formatted. Bare `view` opens the
interactive view. Navigation clamps at stack bounds and skips merged layers.

## Checkout and unstack

A numeric checkout target resolves as stack number, then PR number, then branch.
Stack number, PR number, and PR URL targets fetch remote stack state. A branch
name resolves against local tracking. Always supply a target in automation.

`unstack` removes grouping or tracking; it does not delete PRs or branches. With
no argument it targets the active stack locally and remotely. A stack number
targets GitHub directly. `--local` retains GitHub stack state.

## Merge behavior

Use `gh stack merge`, not `gh pr merge`, for an authorized stack merge. Scope it
with a PR number to merge through that layer or a stack number to merge a remote
stack. Supply `--yes` and one of `--squash`, `--rebase`, `--merge`, or
`--merge-method <method>`.

The direct operation is all-or-nothing and checks that PRs are open and not
drafts. It cannot bypass merge requirements. Under merge queue, method flags
are ignored and queued PRs may land in separate groups. Do not run merge merely
because checks pass; explicit authorization is required, and stricter governing
instructions may reserve all merging for the user.

## Exit codes

| Code | Meaning                          | Recovery                                         |
| ---: | -------------------------------- | ------------------------------------------------ |
|    0 | Success                          | Also inspect output for an aborted sync.         |
|    1 | Git or operation error           | Read diagnostics and inspect local/remote state. |
|    2 | Not in a stack or unknown target | Initialize, check out, or correct target.        |
|    3 | Rebase conflict                  | Use command-specific recovery described above.   |
|    4 | GitHub API failure               | Check `gh auth status`; retry only when safe.    |
|    5 | Invalid invocation or state      | Correct arguments or navigate to the top.        |
|    6 | Ambiguous shared branch          | Check out a branch belonging to one stack.       |
|    7 | Rebase already active            | Continue or abort it.                            |
|    8 | Stack lock held                  | Retry after the short lock timeout.              |
|    9 | Stacked PRs unavailable          | Report that stacks must be enabled.              |
|   10 | Interrupted `modify`             | Run `gh stack modify --abort`.                   |
