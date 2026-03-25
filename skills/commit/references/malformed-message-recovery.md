# Malformed Message Recovery

Use only when the agent just created a malformed commit message in this same run.

Examples: literal `\n` in message, heredoc terminator mistake, accidental shell text in commit body.

## Rules

- This is a message-only self-fix path.
- No file edits. No `git add`. No scope expansion.
- One immediate amend max.
- Requires clean worktree before amend (`git status --short` must be empty).
- If `HEAD` is already on any remote branch, stop and report; do not force-push implicitly.

## Flow

1. Inspect latest message:

```bash
git log -1 --format=%B
git --no-pager status --short
git --no-pager branch -r --contains HEAD
```

2. If `git status --short` output is non-empty, stop and report.
3. If `git branch -r --contains HEAD` output is non-empty, stop and report.
4. Rewrite message via message-only amend:

```bash
git commit --amend -F - <<'EOF'
type(scope): subject

Explain the intended user impact with real newlines.
EOF
```

5. Verify:

```bash
git log -1 --format=%B
git status --short --branch
```

6. Stop. No extra mutation in this invocation.

## Do Not Use For

- General commit polishing in later runs.
- Amending content/scope changes (use `references/amend.md`).
- Rewriting already-pushed history.
