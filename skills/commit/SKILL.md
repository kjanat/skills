---
name: commit
description: Commits changes with strict safety gates and high-signal commit messages. Use when asked to commit changes or run /commit with push/no-push/no-verify/amend flags.
license: MIT
metadata:
  author: kjanat
  version: "1.3"
---

# commit

Safe `/commit` workflow for git repos.
Primary flow stays here. Edge-case playbooks live in `references/`.

Git-only skill. If `.jj/` exists, do not run this flow.

## Usage

```text
/commit [push|no-push|no-verify|amend] [context...]
```

## Route Edge Cases

| Situation                                         | Read                                         |
| ------------------------------------------------- | -------------------------------------------- |
| Asked to amend                                    | [`references/amend.md`]                      |
| Just created malformed commit message in this run | [`references/malformed-message-recovery.md`] |

## Hard Safety Gates (Always On)

- If any rule conflicts, this section wins.
- Max mutation budget: one commit, plus at most one message-only amend exception.
- Never run `git commit --amend` unless `amend` was explicit.
- Only amend exception: immediate message-only self-fix for malformed message the agent created in this same run.
- Never use `--no-verify` unless `no-verify` was explicit.
- Message-interpretation gate:
  - Direct user corrections about commit-message wording or formatting override generic defaults.
  - If a commit-message file is created for the flow, treat that file as the commit-message source of truth.
  - Infer commit-message formatting from recent repo history.
  - Use backticks for code-ish literals when consistent with repo history.
  - Prefer backticks for identifiers, commands, flags, paths, env vars, and similar literals.
  - Style inference never overrides the hard limits for subject/body length.
- If both `push` and `no-push` are present, `no-push` wins.
- Staging gate:
  - If anything already staged, never run `git add`.
  - `git add -A` allowed only if both true: nothing staged and no args/flags.
  - If nothing is staged and any flags/context are present, stop and report. Do not auto-stage.
- Push gate:
  - If `push` present: push after successful commit.
  - If `no-push`/`nopush` present: do not push.
  - Default: do not push.
  - After one push for this invocation, never push again unless user re-requests.
- Post-commit stop rule:
  - Run `git log -1 --format=%B` and `git status --short --branch`.
  - If repo is dirty, stop local mutation and report.
  - Do not run add/amend/fixup/follow-up commit unless user asks in a new instruction.
- Never rewrite history implicitly.

## Standard Flow

1. Check VCS guard:

   ```bash
   test -d .jj && echo "jj repo detected; stop and use jj flow"
   ```

2. Parse args/flags: `push|no-push|no-verify|amend`.
3. If `amend` present, follow [`references/amend.md`].
4. Inspect repo state:

   ```bash
   git --no-pager status --short --branch
   git --no-pager diff --numstat
   git --no-pager diff --staged --numstat
   git --no-pager log -10 --pretty=medium
   ```

5. Apply staging gate exactly.
6. Write commit message using `Commit Message Forms`.
7. If the user corrected commit-message wording/format in this conversation, restate the exact intended commit artifact before mutating.

8. Create one non-amend commit action.
9. Verify:

   ```bash
   git log -1 --format=%B
   git status --short --branch
   ```

10. If malformed message was just created in this run and worktree is clean, follow [`references/malformed-message-recovery.md`].
11. Push only if `push` present and `no-push` absent.

## Commit Message Forms

- Prefer WHY (user impact), not WHAT (file churn).
- Avoid vague messages: `improved ux`, `addressed feedback`.
- Direct user corrections about commit-message content/format win over these defaults.
- Infer message formatting conventions from recent repo history before drafting.
- Use backticks for code-ish literals when consistent with repo history.
- Prefer backticks for identifiers, commands, flags, paths, env vars, and similar literals.
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
- Policy for this skill: if chaining after heredoc, ALWAYS use grouping.
- Never place `&&`/`||` on heredoc opener line in this skill.
- Never start a fresh line with `&&`/`||` after `EOF`.

Use this exact template when chaining after a heredoc commit:

```bash
{
  git commit -F - <<'EOF'
<type>[optional scope]: <description>

<body>

[optional footer(s)]
EOF
} && git push
```

Good:

```bash
{
  git commit -F - <<'EOF'
feat(parser): tighten svg filter constraints

Reject invalid filter primitive/type combinations and keep valid
defs + text-link structures parseable so AST consumers can trust
structure for linting and transforms.
EOF
} && git log -1 --format=%B && git status --short --branch
```

Bad:

```bash
git commit -F - <<'EOF'
...
EOF && git log -1 --format=%B
```

```bash
git commit -F - <<'EOF'
...
EOF
&& git push
```

```bash
git commit -F - <<'EOF' && git push
...
EOF
```

## Operational Notes

- If `amend` is used and message changes, write message for full final commit intent (not delta).
- Do not make unrelated code edits before committing.
- Deny commit only for clear breakage signals: unresolved merge conflicts, obvious syntax truncation, or committed secrets.

## Reading Order

| Task                    | Read                                                           |
| ----------------------- | -------------------------------------------------------------- |
| Run default commit flow | [`SKILL.md`] (`Hard Safety Gates`, then `Standard Flow`)       |
| Asked to amend          | [`references/amend.md`]                                        |
| Fix malformed message   | [`references/malformed-message-recovery.md`]                   |
| Write better message    | [`SKILL.md`] (`Commit Message Forms` + `Heredoc Safety Rules`) |

## In This Reference

| File                                         | Purpose                                      |
| -------------------------------------------- | -------------------------------------------- |
| [`SKILL.md`]                                 | Primary flow, global safety gates            |
| [`references/amend.md`]                      | Explicit amend workflow and constraints      |
| [`references/malformed-message-recovery.md`] | Same-run malformed-message recovery playbook |

[`SKILL.md`]: SKILL.md
[`references/amend.md`]: references/amend.md
[`references/malformed-message-recovery.md`]: references/malformed-message-recovery.md
