# Claude collaboration patterns

Use these patterns when a plain bounded assignment needs more structure. Adapt
the fields to the task; do not invent permissions or repository state.

## Base assignment prompt

Run non-interactive assignments with:

```bash
claude -p \
  --name '<repo>:<task>' \
  --permission-mode bypassPermissions \
  --output-format text \
  '<prompt>'
```

`bypassPermissions` is an execution setting, not authorization for extra work.
The prompt must still name every allowed local or remote mutation.

```text
Target: <repository, worktree, branch, thread, or commit>
Mode: <report-only | edit | edit-and-commit | explicitly authorized remote work>

Objective:
<one concrete outcome or question>

Preserve or prove:
- <invariant or failure mode>
- <behavior that must remain intact>

Scope:
- Relevant: <files or subsystem>
- Non-goals: <explicit exclusions>

Evidence required:
- <test, reproduction, measurement, or diff-based proof>

You may conclude that the premise or proposed solution is wrong. Stop when
<observable stopping condition>. Return changes, evidence, and blockers as
separate sections.
```

Use a narrower mode than the user authorized when mutation is unnecessary. A
request for findings does not authorize edits, and permission to edit does not
imply permission to commit, push, comment, or open a pull request.

## Choose the output mode

Keep `--output-format text` for a simple one-shot handoff. When another process
must consume Claude's return reliably, use `--output-format json` with
`--json-schema`:

```bash
claude -p \
  --name '<repo>:<task>' \
  --permission-mode bypassPermissions \
  --output-format json \
  --json-schema '{
    "type": "object",
    "properties": {
      "changes": { "type": "array", "items": { "type": "string" } },
      "evidence": { "type": "array", "items": { "type": "string" } },
      "blockers": { "type": "array", "items": { "type": "string" } }
    },
    "required": ["changes", "evidence", "blockers"],
    "additionalProperties": false
  }' \
  '<prompt>'
```

For a long-running assignment whose progress must be observed as it arrives,
use streaming output:

```bash
claude -p \
  --name '<repo>:<task>' \
  --permission-mode bypassPermissions \
  --output-format stream-json \
  --include-partial-messages \
  '<prompt>'
```

Partial messages are progress events, not the authoritative handoff. Wait for
the final result and still verify the repository's actual end state.

Use `--input-format stream-json` only when the caller needs to send realtime
streaming input and already implements Claude Code's stream-JSON protocol. It
works only with `--print`; pair it with `--output-format stream-json` when the
caller also needs realtime output. A normal static assignment should keep the
default text input.

## Protect long-running invocations

Claude may take longer than the surrounding agent harness expects. Use a
timeout-free call or the largest supported timeout. If that is still too short,
use a durable process, terminal session, task runner, or supervisor independent
of the timed call. Log stdout and stderr, and record the process ID, stable
`--name`, and session ID once available.

Plain shell backgrounding is insufficient when the harness kills the process
group, container, or execution session. Verify that the launcher survives that
behavior. A harness timeout interrupts observation; it does not prove Claude
failed or stopped.

Before retrying, check the original process, log, named session, and repository
state; recover or resume it when possible. Replace it only after proving it
stopped or is unrecoverable and deciding another paid run is warranted. Blind
retries can cause concurrent mutations and charge twice for one assignment.

## Manage the session lifecycle

Always set `--name <repo>:<task>` on a delegated invocation. Choose a short,
stable name that identifies the repository and task without putting secrets in
process arguments or session metadata. Reuse the same name when continuing the
assignment.

Use `--model <model>` when the user requests a model or the assignment has a
clear model requirement. Otherwise, preserve Claude Code's configured default.

Continue an existing conversation deliberately:

- Prefer `--resume <session_id>` when the exact session is known.
- Use `--continue` only when the most recent conversation in the current
  directory is unambiguously the intended one.
- Restate the current target, allowed mutations, and stopping condition after
  resuming. Earlier permission in the conversation does not authorize new work,
  and its recorded branch or head may be stale.

Use `--cloud <description>` to create cloud-hosted work, or pass its exact
session ID or `claude.ai/code` URL to attach to an existing cloud session. Add
`--environment <environment_id>` only when the user or environment provides the
specific self-hosted environment; do not guess or create one as a convenience.

The normal unattended local pattern uses
`--permission-mode bypassPermissions`. The stronger
`--dangerously-skip-permissions` flag bypasses all permission checks directly;
use it only for an intentionally isolated sandbox where that risk is acceptable.
Neither option authorizes additional edits, remote actions, or scope beyond the
assignment.

## Investigation

Ask Claude to distinguish observations from hypotheses and to reproduce the
behavior before proposing a fix when practical.

```text
Determine whether <failure mode> is reachable in <subsystem>. Do not edit files.
Try to falsify the issue premise. Return the reproduction steps, observed
behavior, relevant code paths, and the smallest justified next action.
```

## Implementation

Name the behavioral contract instead of dictating an unverified patch.

```text
Implement <outcome> in <scope> while preserving <invariant>. Add focused
regression evidence that fails without the fix. Do not change <non-goal>.
Report the files changed, commands run, results, and anything left unresolved.
```

If the task is correctness-sensitive, ask Claude to temporarily reintroduce the
bug or weaken the protected behavior and show that the new test fails, then
restore the correct implementation. Keep the mutation targeted.

## Review

Anchor the review to an immutable starting point when possible.

```text
Review <commit or current head> for <named risks>. Inspect the implementation and
tests, and try to prove the claimed invariant false. Report only actionable
findings tied to concrete code and explain the failure scenario. Do not edit or
push.
```

A Claude review may change the branch or pull-request head when mutation was
authorized. After return, compare the new head and diff with the recorded start
before accepting the review result.

## Adversarial second pass

Use a second pass when independent challenge is worth the extra coordination:

- "Try to prove your previous conclusion wrong."
- "Measure this failure mode instead of inferring it from control flow."
- "Mutation-test the invariant this regression test claims to protect."
- "Re-review the current head, including any commits added after the first
  pass."

Self-correction is useful evidence, but the delegating agent still owns the
final judgment and end-state verification.

## Concurrent assignments

Independent read-only questions can run concurrently. Mutating assignments may
run concurrently only when their targets are already isolated and the user has
authorized that setup. Never create an extra worktree, branch, or remote artifact
merely to enable concurrency unless that action is separately authorized.
