---
name: working-with-claude
description: Delegates bounded implementation, investigation, and review tasks to Claude, then verifies the returned work against current repository state. Use when Claude should act as a focused collaborator or adversarial second engineer, not for general repository maintenance.
disable-model-invocation: true
---

# Work effectively with Claude

Use Claude as a delegated collaborator, not as the authority on completion. A
delegation does not expand the user's authorization: report-only work stays
report-only, and repository or remote mutations must already be in scope.

## Choose a bounded assignment

Delegate when Claude can own a concrete question or outcome with an observable
stopping point. Suitable assignments include:

- implementing a scoped change while preserving a named invariant;
- investigating a reproducible failure and reporting evidence;
- reviewing a current diff against specific risks;
- trying to falsify an earlier conclusion;
- running a targeted experiment that distinguishes competing explanations.

Do not use a vague prompt such as "review this repository". Do not start an
overlapping run that can mutate the same worktree, branch, issue, or pull request
while an earlier run is active.

## Establish the assignment contract

Before delegating, capture only the state needed to make the assignment
unambiguous:

1. Name the exact repository and, when relevant, worktree, branch, issue, pull
   request, or head commit.
2. State whether Claude may only report findings or may also edit, commit, push,
   comment, or open/update an artifact. Omit permissions the user has not
   granted.
3. Describe the desired outcome, the property to preserve or prove, relevant
   files or subsystem, and explicit non-goals.
4. Specify the evidence expected: focused tests, a reproduction, measurements,
   a diff review, or a concise explanation tied to code.
5. Allow Claude to conclude that the premise or proposed solution is wrong.
6. Give a stopping condition and require a return that separates changes,
   evidence, and unresolved blockers.

Use the Claude interface available in the current environment or explicitly
named by the user. Do not silently substitute another agent when no Claude
integration is available.

For non-interactive Claude Code delegation, invoke `claude -p` with
`--name <repo>:<task>` and `--permission-mode bypassPermissions`. Every
delegated invocation must have a short, stable name; reuse it when continuing
the same assignment. Bypassing permission prompts does not expand the user's
authorization. Keep the exact allowed mutations and remote actions explicit in
the assignment.

Claude can be thorough and slow. When the calling harness imposes a timeout,
prefer disabling it or setting it to the maximum permitted duration. Otherwise,
launch Claude through a durable background mechanism that survives the caller,
capture its output in a known log, and retain its process and session identity.
A caller timeout makes completion unknown; it does not prove the Claude run
stopped. Before retrying, inspect the existing process, log, named session, and
repository state. Never blindly start a duplicate run: the likely result is
wasted work and an additional expensive invocation.

For reusable prompt shapes, structured or streaming runs, session lifecycle,
and higher-confidence review patterns, read
[collaboration-patterns.md](references/collaboration-patterns.md).

## Track the work against current state

Record the relevant starting state before delegation, such as the worktree
status or pull-request head commit. When Claude returns:

1. confirm that the run actually completed;
2. re-read the current local and remote state rather than trusting the run
   summary;
3. compare the current branch, head, commits, diff, comments, and checks with the
   recorded starting state as applicable;
4. inspect Claude's delta yourself;
5. rerun or independently verify the evidence in proportion to the risk.

A successful run is not proof that a requested edit, push, comment, or workflow
change landed. Conversely, a failed or restricted run may still have produced
useful findings or local changes. Report the actual end state.

## Increase scrutiny when it buys evidence

For correctness-sensitive work, ask for an adversarial second pass or a targeted
mutation test when it can answer a concrete question. Claude may temporarily
instrument or break local code only when that experiment is within scope; it
must restore temporary changes before handing back unless they belong in the
requested result.

Do not recursively delegate every adjacent cleanup Claude notices. Follow-up
work should be independently real, meaningfully scoped, and worth the additional
coordination.

## Report the handoff

Summarize the target and starting point, Claude's completion state, actual
changes found, evidence independently checked, and any remaining blocker. Keep
Claude's claims distinct from verified repository state.
