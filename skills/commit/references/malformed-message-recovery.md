# Malformed Message Recovery

Use only when the agent just created a malformed commit message in this same run.

Examples: literal `\n` in message, heredoc terminator mistake, accidental shell text in commit body, or wrong message formatting/content caused by the agent misreading a user correction in this same run.

## Rules

- This is a message-only self-fix path.
- No file edits. No `git add`. No scope expansion.
- One immediate amend max.
- Requires clean worktree before amend (`git status --short` must be empty).
- If `HEAD` is already on any remote branch, stop and report; do not force-push implicitly.
- If upstream already contains the intended message and local `HEAD` is the malformed rewrite, restore local to upstream instead of creating another amend.
- Shell-specific message forms from `SKILL.md` are highest priority.
- Do not use `git commit --amend -F -`; use `-m` with the shell-specific forms from `SKILL.md`.
- Never chain on the Bash/zsh heredoc opener line or after the `EOF` line.
- Closing delimiter must be exactly `EOF` with no trailing text.
- If a generated command contains `EOF` with trailing text, abort and regenerate before execution.
- Run verification and push commands in separate shell calls only.

## Flow

1. Inspect latest message:

   ```bash
   git log -1 --format=%B
   git --no-pager status --short
   git --no-pager branch -r --contains HEAD
   ```

2. If `git status --short` output is non-empty, stop and report.
3. If `git branch -r --contains HEAD` output is non-empty, stop and report.
4. If upstream already has the intended message, restore local to upstream and stop.
5. Otherwise rewrite message via message-only amend using the shell-specific message forms from `SKILL.md`.

   Bash/zsh:

   ```bash
   git commit --amend -m "$(cat <<'EOF'
   type(scope): subject

   Explain the intended user impact with real newlines.
   EOF
   )"
   ```

   PowerShell:

   ```powershell
   $msg = @'
   type(scope): subject

   Explain the intended user impact with real newlines.
   '@

   git commit --amend -m "$msg"
   ```

6. Verify:

   ```bash
   git log -1 --format=%B
   git status --short --branch
   ```

7. Stop. No extra mutation in this invocation.

## Do Not Use For

- General commit polishing in later runs.
- Amending content/scope changes (use `references/amend.md`).
- Rewriting already-pushed history.
