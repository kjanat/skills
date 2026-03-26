# LIGHTNING KNOWLEDGE BASE

Domain-heavy skill: lightning physics references + small computational scripts.

## STRUCTURE

```tree
lightning/
├── SKILL.md
├── references/                 # topical physics docs
├── scripts/                    # stdlib Python calculators/demos
└── Rakov ... libgen.li.pdf     # source text snapshot
```

## WHERE TO LOOK

| Task                    | Location                                                      | Notes                       |
| ----------------------- | ------------------------------------------------------------- | --------------------------- |
| Find topic quickly      | `SKILL.md` Reading Order table                                | Canonical topic -> file map |
| Quantitative values     | `references/detailed-statistical-tables.md`                   | Cross-study stats           |
| Protection or grounding | `references/protection-standards.md`                          | Engineering focus           |
| Field/current modeling  | `scripts/leader_fields.py`, `scripts/return_stroke_models.py` | Equation-backed helpers     |
| Thunder/acoustics       | `scripts/thunder.py`                                          | Few-based calculations      |

## LOCAL CONVENTIONS

- Treat `references/` as primary response source; scripts are support tools.
- Keep outputs in SI-style units and explicit assumptions.
- Python scripts use stdlib only and include runnable demo blocks.

## ANTI-PATTERNS

- Do not cite numbers without a reference file path.
- Do not edit source PDF; it is a static source artifact.
- Do not present script outputs as universal truth without model limits.
