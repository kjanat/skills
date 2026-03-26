# GITHUB-SCRIPT KNOWLEDGE BASE

Guidance for secure `actions/github-script@v8` workflow steps and reusable ESM
helper modules.

## STRUCTURE

```tree
github-script/
├── SKILL.md
├── references/
│   ├── security.md
│   ├── inputs-outputs-retries.md
│   ├── runtime-and-migrations.md
│   ├── external-files.md
│   └── examples.md
└── assets/
    ├── check-stubs-version-job.yml
    ├── check-uv-version-job.yml
    ├── package.json
    └── tsconfig.json
```

## WHERE TO LOOK

| Task                    | Location                               | Notes                                  |
| ----------------------- | -------------------------------------- | -------------------------------------- |
| Security baseline       | `references/security.md`               | Read first for any script authoring    |
| I/O and retries         | `references/inputs-outputs-retries.md` | Output model + retry knobs             |
| External module pattern | `references/external-files.md`         | Preferred architecture                 |
| Runtime changes         | `references/runtime-and-migrations.md` | v5-v8 behavior                         |
| Reusable job snippets   | `assets/*.yml`                         | Template fragments, not full workflows |

## LOCAL CONVENTIONS

- Pin action usage to `actions/github-script@v8`.
- Keep inline `with.script` minimal; move logic to ESM files.
- Typecheck helper modules using local `assets/tsconfig.json` setup.

## ANTI-PATTERNS

- Never inline `${{ ... }}` inside script body.
- Do not default to CommonJS (`require`) in new examples.
- Do not treat `assets/check-*.yml` as complete workflow files.
