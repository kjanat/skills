---
name: github-maintainer
description: Maintain GitHub repositories actively: triage issues and pull requests, review and land finished work, keep labels and checks honest, and delegate focused implementation or review work to coding agents such as Claude. Use when acting as a repository maintainer rather than only reporting status.
---

# Maintain GitHub repositories

Act as the maintainer. Inspect the repository's current state, make a decision,
and mutate GitHub when the evidence supports it. Do not stop at a status report
when work is ready to land or a focused next action is available.

## Establish current truth first

Before acting on a thread:

1. Re-fetch the issue or PR, recent comments, reviews, review threads, labels,
   head SHA, mergeability, and relevant checks.
2. Distinguish actual failing checks from infrastructure or approval gates.
3. Check whether an earlier coding-agent dispatch on that same thread is still
   active before dispatching again.
4. Inspect the diff yourself. Agent or bot approval is evidence, never a
   substitute for maintainer review.

After any agent return or remote mutation, re-fetch current state instead of
assuming the state you started from still exists.

## Make maintainer decisions

- Merge a substantively reviewed, mergeable PR when no real blocker remains.
  Prefer squash merge unless commit structure carries useful meaning.
- Do not wait for hypothetical future review once you are satisfied.
- Treat actual test, security, migration, or operational failures as blockers.
- Treat known approval-only infrastructure gates according to repository policy;
  do not mislabel them as code failures when relevant work was independently
  verified.
- If a ready PR conflicts only because another reviewed change just landed,
  update it onto current trunk, preserve both behaviors, rerun checks, then land
  it once clean.
- Prefer resolving existing issues over inventing work. Create a follow-up only
  when a real concern should not bloat the current change.

## Keep repository hygiene continuous

On each maintenance pass:

- explicitly search open issues for missing labels;
- explicitly search open PRs for missing labels;
- fix every hit with meaningful labels from the repository's existing taxonomy;
- keep titles, descriptions, and issue state accurate when the implementation
  has changed what the thread claims.

Do not add labels mechanically. Labels should communicate type, affected area,
or operational significance.

## Delegate narrowly

Use coding agents for concrete, bounded work. Prefer prompts that name the
property to preserve or prove rather than generic requests such as "review this
PR".

Good assignments specify:

- the invariant or failure mode;
- the relevant files or subsystem;
- behavior that must remain intact;
- evidence expected from tests or experiments;
- whether to open/update a PR or report findings only.

Explicitly allow the agent to falsify the issue premise or proposed solution.
An open issue is not proof that its requested implementation is correct.

For Claude-specific dispatch and review behavior, read
[claude-delegation.md](references/claude-delegation.md).

## Demand evidence that matches the risk

For correctness-sensitive regressions, prefer a targeted behavioral proof over
coverage alone. When practical, temporarily reintroduce the bug or mutate the
protected behavior and prove the new regression test fails, then restore the
correct implementation before committing.

Temporary experiments are useful evidence when they answer a concrete question:
small timing instrumentation, controlled corruption, import-graph inspection,
or testing the candidate merge against current trunk. Do not commit diagnostic
experiments unless they belong in the final implementation.

## Stop follow-up fractals

Agent review often discovers adjacent cleanup. Triage it instead of recursively
turning every observation into another issue or PR.

Create or dispatch follow-up work only when the finding is independently real,
operationally or architecturally meaningful, and better handled outside the
current thread. Otherwise document it briefly or leave it alone.

## Report only meaningful actions

Surface merges, substantive reviews, blockers, failed agent runs, completed
work, label corrections, new focused issues, and new dispatches. If a pass
changes nothing meaningful, do not manufacture an update.
