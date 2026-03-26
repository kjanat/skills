# BUILD-SKILL KNOWLEDGE BASE

Meta-skill for creating and validating skills. This directory defines canonical
format rules used by the whole repo.

## STRUCTURE

```tree
build-skill/
├── SKILL.md
├── references/
│   ├── anatomy.md
│   ├── frontmatter.md
│   ├── progressive-disclosure.md
│   ├── bundled-resources.md
│   ├── patterns.md
│   ├── gotchas.md
│   └── review-checklist.md
└── scripts/
    ├── init_skill.sh
    ├── validate_skill.sh
    └── package_skill.sh
```

## WHERE TO LOOK

| Task                       | Location                    | Notes                        |
| -------------------------- | --------------------------- | ---------------------------- |
| Understand required layout | `references/anatomy.md`     | Source of structural truth   |
| Frontmatter format rules   | `references/frontmatter.md` | Name regex + required fields |
| Validate a skill           | `scripts/validate_skill.sh` | Run before commit            |
| Scaffold new skill         | `scripts/init_skill.sh`     | Standard templates           |
| Package distributable zip  | `scripts/package_skill.sh`  | Includes validation gate     |

## LOCAL CONVENTIONS

- `SKILL.md` is overview and routing only; details stay in `references/`.
- Validation is script-enforced, not manual checklist only.
- Keep examples short and agent-agnostic unless explicitly tool-specific.

## ANTI-PATTERNS

- Do not bypass `validate_skill.sh` when editing skill structure.
- Do not put long implementation detail directly into `SKILL.md`.
- Do not add frontmatter fields that violate `name`/description rules.
