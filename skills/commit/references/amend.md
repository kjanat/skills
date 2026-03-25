# Amend Flow

Use only when user explicitly requests `amend`.

If `amend` was not explicit, do not amend.

## Rules

- One amend action max for this invocation.
- Message must describe final full commit intent, not just the delta.
- Never use `--no-verify` unless `no-verify` was explicit.
- Never run `git add` if anything is already staged.
- If `HEAD` is already on any remote branch, stop and report. Do not rewrite history implicitly.
- If this amend creates a malformed message in this same run, allow one immediate message-only recovery amend via `references/malformed-message-recovery.md`.

## Flow

1. Inspect repo state:

```bash
git --no-pager status --short --branch
git --no-pager diff --numstat
git --no-pager diff --staged --numstat
git --no-pager log -10 --pretty=medium
```

2. Check pushed-state guard:

```bash
git --no-pager branch -r --contains HEAD
```

If output is non-empty, stop and report.

3. Apply staging gate from `SKILL.md`.
4. Draft full-scope commit message.
5. Run exactly one amend action.

Subject-only:

```bash
git commit --amend -m "type(scope): subject"
```

Multiline:

```bash
git commit --amend -F - <<'EOF'
type(scope): subject

Explain user impact and intent of full final commit.
EOF
```

If explicit `no-verify` was requested, add `--no-verify` to the amend command.

6. Verify:

```bash
git log -1 --format=%B
git status --short --branch
```

7. If repo is dirty after verify, stop and report. No follow-up mutation.

## Guardrails

- Do not chain extra commands after heredoc `EOF` line.
- Do not run a second amend unless it is same-run malformed-message recovery from `references/malformed-message-recovery.md`.
