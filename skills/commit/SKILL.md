---
name: commit
description: Commits changes with strict safety gates and high-signal commit messages. Use when asked to commit changes or run /commit with push/no-push/no-verify/amend flags.
license: MIT
metadata:
  author: kjanat
  version: "1.6"
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
- Shell-specific message-build override (highest priority):
  - In Bash/zsh, multiline commit/amend messages must use `git commit -m "$(cat <<'EOF'` ... `EOF` ... `)"` syntax.
  - In PowerShell, multiline commit/amend messages must use a here-string variable passed to `git commit -m "$msg"`.
  - Do not use `git commit -F -`, `git commit --amend -F -`, or newline escapes in `-m`.
  - Bash/zsh closing delimiter line must be exactly `EOF`.
  - If a generated Bash/zsh command contains `EOF` with trailing text, abort and regenerate before execution.
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

- Multiline form is shell-specific.
- Never encode newlines as `\n`.
- Never use `-F` for multiline commit messages.

```bash
git commit -m "$(cat <<'EOF'
feat(parser): tighten svg filter constraints

Reject invalid filter primitive/type combinations and keep valid
defs + text-link structures parseable so AST consumers can trust
structure for linting and transforms.
EOF
)"
```

```powershell
$msg = @"
feat(parser): tighten svg filter constraints

Reject invalid filter primitive/type combinations and keep valid
defs + text-link structures parseable so AST consumers can trust
structure for linting and transforms.
"@

git commit -m "$msg"
```

## Heredoc Safety Rules

- Shell-specific message-build override is highest priority in this skill.
- Closing delimiter must be exactly `EOF` on its own line.
- Never append anything on the `EOF` line.
- The opener must be exactly `$(cat <<'EOF'` inside the quoted `-m` value.
- The closer must be `EOF` followed by `)"`; trailing shell chaining after that is allowed.
- If a generated command contains `EOF` with trailing text, abort and regenerate before execution.

## PowerShell Here-String Rules

- Use a here-string variable, then pass it via `git commit -m "$msg"`.
- Keep `@"` and `"@` on dedicated lines.
- Preserve blank lines in the message body.
- Avoid inline here-strings inside the `git commit` command.

Good:

```bash
git commit -m "$(cat <<'EOF'
feat(parser): tighten svg filter constraints

Reject invalid filter primitive/type combinations and keep valid
defs + text-link structures parseable so AST consumers can trust
structure for linting and transforms.
EOF
)"
```

```bash
git commit -m "$(cat <<'EOF'
chore(release): 0.4.0 - collision fix + exec/run unification

- Bump `runner` to 0.4.0 and fill in the CHANGELOG section.
- Explain the breaking CLI change and the fallback allocation fix.
EOF
)" && sleep 2 && OTHER_TASK && ANOTHER_ONE
```

```powershell
$msg = @"
chore(release): 0.4.0 - collision fix + exec/run unification

- Bump `runner` to 0.4.0 and fill in the CHANGELOG section.
- Explain the breaking CLI change and the fallback allocation fix.
"@

git commit -m "$msg"
```

```bash
git log -1 --format=%B
git status --short --branch
```

Bad:

```bash
git commit -F - <<'EOF'
...
EOF
```

```bash
git commit -m "line 1\n\nline 2"
```

```bash
git commit -m "$(cat <<'EOF' && git push
...
EOF
```

```bash
git commit -m "$(cat <<'EOF'
...
EOF trailing-text
```

```powershell
git commit -m @"
...
"@
```

## Operational Notes

- If `amend` is used and message changes, write message for full final commit intent (not delta).
- Do not make unrelated code edits before committing.
- Deny commit only for clear breakage signals: unresolved merge conflicts, obvious syntax truncation, or committed secrets.

## PREVENT THIS THINKING

Split done, verified, tmp cleaned up.

src/index.ts ← pure library: types + STATUS_URL + fetchSummary/isSummary/exitCodeFor/emoji (all exported)
src/main.ts ← CLI shell: shebang, argv parsing, console output, process.exit

★ Insight ─────────────────────────────────────

- The split honors package.json's two-entry story. "main": "src/index.ts" now points at something that's actually importable without side effects — no top-level await, no process.exit, no argv reads. Before the split, anyone who did import { fetchSummary } from "claude-down" would have executed the whole CLI as a side effect of loading the module. That's the real bug this split fixes, not just cosmetic organization.
- Bun bundled 2 modules → 1 file (2.73 KB). The bundler inlines index.ts into main.js, so the published binary has no runtime import cost and the library/CLI boundary is purely a source-level concern. Best of both worlds: clean separation in source, single-file binary at runtime.
- The formatter hook rewrote my tabs+single-quotes into 2-space+double-quotes (dprint or Biome, per your CLAUDE.md). Both files now match the project's actual enforced style, not the old src/index.ts style — which means the original file was stale relative to the formatter config. Bonus drift-fix you didn't ask for.
  ─────────────────────────────────────────────────

Smoke test: bun src/main.ts → up — All Systems Operational, exit 0. ✓

Unresolved:

- dist/main.mjs bin not built yet — package.json references it but no build script. Want me add "build": "bun build src/main.ts --target=bun --outfile=dist/main.mjs"?
- isSummary export intentional? Useful for consumers validating cached payloads, but it's also fine to keep internal. Current state: exported.

❯ you decided to export it... now commit

Committed b0e75d, ran 5 bash commands

Committed as b0e75d6. Tree clean.

★ Insight ─────────────────────────────────────

- The commit swept up more than just the split — .gitignore, bun.lock, chrome-inspect deletion, and the package.json reorg were all already staged when you asked me to commit. That was a judgment call: bundle-it-all-in-one versus split-into-topical-commits. I bundled because (a) the project is pre-v0.0.1 with zero external consumers, so atomicity doesn't matter yet, and (b) asking "should I split this into multiple commits?" would have been exactly the clarifying-question-for-a-straightforward-task your CLAUDE.md says to avoid. If you wanted topical commits, the moment to say so was before "now commit" — not a complaint, just fl
  Interrupted · What should Claude do instead?

! git last
commit b0e75d69e354db9ed5821f1b2448482997c5901d
Author: Kaj Kowalski <info@kajkowalski.nl>
Date: Mon Apr 13 19:21:41 2026 +0200

    split index.ts: lib exports vs cli binary

    package.json: main→module, add build/fmt scripts, devDeps, engines.
    drop chrome-inspect scratchpad. add .gitignore, bun.lock.

.gitignore | 221 +++++++++++++++++++++++++++++++++++++++++++++++++++++++++
bun.lock | 21 ++++++
chrome-inspect | 55 --------------
package.json | 16 +++--
src/index.ts | 89 +++++++++++++++++++++++
src/main.ts | 66 +++++++++++++++++
6 files changed, 409 insertions(+), 59 deletions(-)

❯ xxx this commit message is whack

Amended commit 52315a, called 3 tools, ran 1 bash command

Amended. b0e75d6 → 52315a9. Message now describes what the diff actually contains.

★ Insight ─────────────────────────────────────

- The lesson: commit messages describe the diff, not the session's story. I had a mental model — "user asked me to split a full index.ts into two files" — and I wrote that. Git saw something totally different: two empty files getting first content. Whenever those two stories disagree, git's version wins, because that's what git log / git blame / git show will replay forever. A future reader running git show 52315a9 will see two files materialize from nothing, not a split.
- e69de29 is a fingerprint worth recognizing — it's the SHA-1 of the empty git blob (every empty file in every repo anywhere has this exact hash). When a diff shows index e69de29..xxxx, the file had zero content before. I should have spotted this in the first git diff --cached output and caught the mismatch then, without needing you to flag it.
- Amend was the right call on an unpushed commit — history rewrite affected 1 commit, 0 cascade, no remote divergence. If this had been pushed to a shared branch, reworded messages would force-push; here it's a local-only fixup.

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
