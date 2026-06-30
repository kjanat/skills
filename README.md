# Skills

Collection of [Agent Skills] for AI coding agents.

## Available Skills

| Skill                       | Purpose                                                        |
| --------------------------- | -------------------------------------------------------------- |
| `build-skill`               | How to author new skills — format, conventions, validation     |
| `changelog-writing`         | Keep a Changelog convention for CHANGELOG.md                   |
| `commit`                    | Safe commit workflow with quality gates and clear messages     |
| `discoveries-writing`       | Agent memory files for repo-specific gotchas in DISCOVERIES.md |
| `dprint-plugin-creator`     | Scaffold dprint formatter plugins                              |
| `ezelsbruggen-schrijven`    | Write short Dutch mnemonics and recall hooks                   |
| `github-docker-action`      | Docker container GitHub Actions — Dockerfile, action.yml       |
| `github-script`             | Secure `actions/github-script@v8` workflow steps               |
| `github-service-containers` | Docker sidecar services (Redis, Postgres) in GitHub Actions CI |
| `index-knowledge`           | Generate hierarchical AGENTS.md knowledge bases                |
| `lightning`                 | Lightning physics reference corpus                             |
| `statute-proxy`             | Go config-as-code reverse proxy DSL — explain/scaffold/review  |
| `threlte`                   | Threlte (Svelte + three.js) docs routing and examples          |
| `twoslash`                  | Twoslash docs snippets and notation authoring                  |
| `uv-versioning`             | Version bumping workflows for uv Python projects               |
| `xstate`                    | XState v5 docs and API types routing                           |
| `zed-extension-creator`     | Scaffold, implement, and ship Zed editor extensions            |
| `zod`                       | Zod v4 docs routing and schema/API guidance                    |

## Install with the [`skills` CLI](https://github.com/vercel-labs/skills)

Works with Claude Code, Cursor, Codex, OpenCode, GitHub Copilot, and
[35+ more agents](https://github.com/vercel-labs/skills#supported-agents).

```sh
# Install all skills from this repo
npx skills add kjanat/skills

# Install a specific skill only
npx skills add kjanat/skills --skill github-script

# Install globally (available across all projects)
npx skills add kjanat/skills -g

# Install to specific agents
npx skills add kjanat/skills -a claude-code -a cursor

# List available skills without installing
npx skills add kjanat/skills --list
```

## Manual installation

```sh
# Claude Code (project-local, committed with repo)
cp -r skills/github-script .claude/skills/

# Claude Code (global, available everywhere)
cp -r skills/github-script ~/.claude/skills/

# Cursor
cp -r skills/github-script ~/.cursor/skills/

# OpenCode
cp -r skills/github-script ~/.config/opencode/skills/
```

## License

[MIT]

<!--links-start-->

[MIT]: LICENSE
[Agent Skills]: https://agentskills.io/
