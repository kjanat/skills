# Skills

Collection of [Agent Skills](https://agentskills.io/) for AI coding agents.

## Available Skills

| Skill                      | Purpose                                                        |
| -------------------------- | -------------------------------------------------------------- |
| `build-skill`              | How to author new skills — format, conventions, validation     |
| `changelog-writing`        | Keep a Changelog convention for CHANGELOG.md                   |
| `github-docker-action`     | Docker container GitHub Actions — Dockerfile, action.yml       |
| `github-script`            | Secure `actions/github-script@v8` workflow steps               |
| `github-service-containers`| Docker sidecar services (Redis, Postgres) in GitHub Actions CI |
| `index-knowledge`          | Generate hierarchical AGENTS.md knowledge bases                |
| `uv-versioning`            | Version bumping workflows for uv Python projects               |

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

[MIT](LICENSE)
