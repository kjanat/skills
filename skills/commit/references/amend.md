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
- If the branch has an upstream, compare local `HEAD` with upstream after amend before taking any follow-up action.

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

7. If branch has an upstream, compare local vs upstream state:

   ```bash
   git rev-list --left-right --count HEAD...@{u}
   git log -1 --format=%B HEAD
   git log -1 --format=%B @{u}
   ```

8. If repo is dirty after verify, stop and report. No follow-up mutation.

9. If comparison shows `ahead 1, behind 1`, stop and inspect message mismatch before any more mutation.

10. If upstream already has the intended message and local `HEAD` is the accidental rewrite, restore local to upstream and stop.

## Guardrails

- Heredoc hard-stop override from `SKILL.md` is highest priority.
- If `git commit --amend -F - <<'EOF'` is used, run it in an isolated shell call only.
- Never chain on the heredoc opener line or after the `EOF` line.
- Closing delimiter must be exactly `EOF` with no trailing text.
- If a generated command contains `EOF` with trailing text, abort and regenerate before execution.
- Run verification and push commands in separate shell calls only.
- Do not run a second amend unless it is same-run malformed-message recovery from `references/malformed-message-recovery.md`.
- Do not improvise another amend when local/upstream comparison shows the intended message is already on upstream.
