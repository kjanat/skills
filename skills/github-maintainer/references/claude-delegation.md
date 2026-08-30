# Claude delegation and review behavior

Claude is useful as both an implementer and an adversarial second engineer, but
its GitHub behavior has several maintainer-specific consequences.

## Treat every return as a potentially new head

A Claude review can push commits to the PR it is reviewing. A comment that says
"reviewed" may therefore also mean "reviewed, changed, and pushed".

Before dispatch, note the current head SHA. After Claude returns:

1. re-fetch the PR and head SHA;
2. inspect any new commits or diff introduced by Claude;
3. re-check relevant workflow/test state for the new head;
4. review that delta yourself before approving or merging.

Never assume that "Claude reviewed head X" means head X is still current.

## Prefer properties over generic review prompts

Claude performs better when asked to verify or preserve a concrete property.
Examples:

- preserve both reviewed behaviors while rebasing onto current trunk;
- prove a failure path cannot recurse;
- verify the original exception still propagates unchanged;
- prove a documented status is pinned against the live handler;
- determine whether a proposed failure mode is actually reachable.

Ask for the evidence that would falsify the claim, not merely confirmation that
the diff looks reasonable.

## Use adversarial second passes

A second pass can be valuable even when Claude authored or reviewed the first
one. Explicitly ask it to attack its own assumptions and correct its earlier
reasoning if measurement disagrees.

Useful instructions include:

- "Try to prove your previous conclusion wrong."
- "Mutation-test the invariant you claim this test protects."
- "Measure this failure mode rather than inferring it from the control flow."
- "Re-review the current head, including any commits you pushed last time."

Self-correction is useful evidence, but the maintainer still owns the final
judgment.

## Mutation-test important regression claims

Coverage does not prove that a test notices the bug. For important correctness
properties, ask Claude to temporarily mutate the implementation and show that the
new test fails.

Examples include replacing a positive retry hint with zero, removing a floor,
weakening an authorization branch, or changing the documented/live status
relationship. Restore the correct implementation before committing.

Mutation testing should be targeted. Do not turn every maintenance task into a
full mutation-testing campaign.

## Let Claude falsify the ticket

Tell Claude it may conclude that the issue premise, requested implementation, or
maintainer hypothesis is wrong. Ask it to determine what concrete behavior is
needed before editing code.

Without that permission, coding agents tend to treat the existence of a ticket
as evidence that its proposed solution should be implemented.

## Separate agent completion from repository state

Claude workflow state is not authoritative repository state.

- A completed Claude run does not prove the requested push or workflow edit
  landed.
- A useful Claude return may coexist with an approval-only `action_required`
  workflow result.
- A failed or restricted mutation may still leave useful comments, patches, or
  independently verified test results.

Use the actual current head, commits, diff, comments, review threads, and relevant
checks as the source of truth.

## Use Claude as an experimental instrument

When useful, authorize temporary local experiments rather than static reasoning
alone. Claude can instrument timing, deliberately break an implementation,
inspect dependency/import graphs, or test a candidate merge with current trunk.

Require it to report what was measured and to remove temporary instrumentation
before pushing unless that instrumentation belongs in the final change.

## Guard concurrency per thread

Do not dispatch another Claude run on the same issue or PR while an earlier one
is still working. Independent threads can proceed concurrently.

After a return, confirm that the earlier run has actually completed before
re-dispatching on that thread.

## Avoid recursive micro-follow-ups

Claude is good at spotting the next nearby defect. That does not mean every
finding deserves a new issue immediately.

Promote an adjacent finding only when it is real, scoped, and worth maintaining.
Prefer existing issues. Do not create chains of tiny cleanup tickets merely
because each review can find one more polish opportunity.
