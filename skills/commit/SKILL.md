---
name: commit
description: Commits changes with strict safety gates and high-signal commit messages. Use when asked to commit changes or run /commit with push/no-push/no-verify/amend flags.
license: MIT
metadata:
  author: kjanat
  version: "1.0"
---

# commit

One-shot commit flow. Strict mutation limits. No implicit history rewrite.

Git-only skill. If `.jj/` exists, do not run this flow.

## Usage

```text
/commit [push|no-push|no-verify|amend] [context...]
```

## Hard Safety Gates

- If any rule conflicts, this section wins.
- Max mutation budget: one commit, plus at most one message-only amend exception.
- Never run `git commit --amend` unless `amend` was explicit.
- Only amend exception: immediate message-only self-fix for malformed message the agent created in this same run.
- Never use `--no-verify` unless `no-verify` was explicit.
- If both `push` and `no-push` are present, `no-push` wins.
- Staging gate:
  - If anything already staged, never run `git add`.
  - `git add -A` allowed only if both true: nothing staged and no args/flags.
  - Any free-text context counts as args; auto-stage disabled.
- Push gate:
  - If `push` present: push after successful commit.
  - If `no-push`/`nopush` present: do not push.
  - Default: do not push.
  - After one push for this invocation, never push again unless user re-requests.
- Post-commit stop rule:
  - Run `git log -1 --format=%B` and `git status --short --branch`.
  - If repo is dirty for any reason, stop and report.
  - Do not run add/amend/fixup/follow-up commit unless user asks in a new instruction.
- Never rewrite history implicitly.

## Commit Message Rules

- Prefer WHY (user impact), not WHAT (file churn).
- Avoid vague messages: `improved ux`, `addressed feedback`.
- If repo uses conventional commits:
  - Subject max 50 chars.
  - Body lines max 72 chars.
  - Prefer multiline unless subject is fully self-explanatory.
- Subject-only form:

```bash
git commit -m "type(scope): subject"
```

- Multiline form must use heredoc with `-F -`.
- Never encode newlines as `\n`.
- Never combine `-m` with `-F`.

## Heredoc Safety Rules

- Closing delimiter must be exactly `EOF` on its own line.
- Never append anything on the `EOF` line.

Good:

```bash
git commit -F - <<'EOF'
feat(parser): tighten svg filter constraints

Reject invalid filter primitive/type combinations and keep valid
defs + text-link structures parseable so AST consumers can trust
structure for linting and transforms.
EOF
git log -1 --format=%B
git status --short --branch
```

Bad:

```bash
git commit -F - <<'EOF'
...
EOF && git log -1 --format=%B
```

## Execution Flow (Must Follow)

1. Check VCS guard:

```bash
test -d .jj && echo "jj repo detected; stop and use jj flow"
```

2. Parse args/flags: `push|no-push|no-verify|amend`.
3. Inspect repo state:

```bash
git --no-pager status --short --branch
git --no-pager diff --numstat
git --no-pager diff --staged --numstat
git --no-pager log -10 --pretty=medium
```

4. Apply staging gate exactly.
5. Create one commit action:
   - Normal path: one non-amend commit.
   - Amend path: only if explicit `amend` arg.
   - Message-fix-only amend: no staging.
6. Verify:

```bash
git log -1 --format=%B
git status --short --branch
```

- If malformed message was just created by agent in this run, do one immediate message-only amend via heredoc.
- Otherwise stop/report. No extra mutation.

## Operational Notes

- If `amend` is used and message changes, write message for full final commit intent (not delta).
- Do not make unrelated code edits before committing.
- Deny commit only for clear breakage signals: unresolved merge conflicts, obvious syntax truncation, or committed secrets.

## Reading Order

| Task                    | Read                                                         |
| ----------------------- | ------------------------------------------------------------ |
| Run `/commit` safely    | `SKILL.md` (`Hard Safety Gates` -> `Execution Flow`)         |
| Write better message    | `SKILL.md` (`Commit Message Rules` + `Heredoc Safety Rules`) |
| Handle amend/push flags | `SKILL.md` (`Hard Safety Gates` + `Operational Notes`)       |

## In This Reference

| File       | Purpose                                        |
| ---------- | ---------------------------------------------- |
| `SKILL.md` | Complete commit workflow, gates, message rules |
