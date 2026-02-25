# Skill Review Checklist

Cross-validation checklist for reviewing skills. Dispatch a reviewer agent
(oracle or code-reviewer) after creating or significantly modifying a skill.

Source: [Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)

## Dispatching a Reviewer

After writing a skill, dispatch a reviewer agent with this prompt template:

```
Review this OpenCode skill against the best-practices checklist in
references/review-checklist.md (from the build-skill skill).

Skill location: <path-to-skill-dir>

Read SKILL.md and all reference files. For each checklist item, report
PASS/FAIL/N-A with a one-line rationale. End with concrete suggestions
ranked by impact.
```

Use the `oracle` agent for architecture/structure review, or `code-reviewer`
for skills with executable scripts.

## Core Quality

- [ ] Description is specific, includes key terms and activation triggers
- [ ] Description is third person ("Processes X" not "I process X")
- [ ] SKILL.md body under 200 lines (500 absolute max)
- [ ] Reference files under 200 lines each
- [ ] No time-sensitive information (dates, "before August 2025")
- [ ] Consistent terminology (one term per concept throughout)
- [ ] Examples are concrete, not abstract
- [ ] File references one level deep from SKILL.md (no chains)
- [ ] Progressive disclosure: SKILL.md has routing logic, details in refs
- [ ] Navigation tables present (Reading Order, In This Reference)

## Degrees of Freedom

Assess whether each instruction matches the task's fragility:

| Freedom | When to use                          | Style                    |
| ------- | ------------------------------------ | ------------------------ |
| High    | Multiple approaches valid            | Text guidelines          |
| Medium  | Preferred pattern, some variation ok | Pseudocode / templates   |
| Low     | Fragile ops, consistency critical    | Exact scripts, no params |

Review question: "Is any instruction over-specified (wasting flexibility) or
under-specified (risking errors)?"

## Token Efficiency

- [ ] Only includes information the model doesn't already know
- [ ] No verbose explanations of well-known concepts
- [ ] Large examples/templates in reference files, not SKILL.md
- [ ] Decision trees route to specific files (agent doesn't load everything)

## Workflows and Feedback Loops

- [ ] Multi-step processes have numbered steps
- [ ] Complex workflows include a copy-paste checklist
- [ ] Validation steps exist for critical operations (validate → fix → repeat)
- [ ] Decision points are explicit ("Creating new? → follow X. Editing? → follow Y")

## Scripts (if applicable)

- [ ] Scripts handle errors explicitly (don't punt to the agent)
- [ ] No magic constants (all values justified with comments)
- [ ] Required packages listed with install commands
- [ ] Clear intent: "Run script X" (execute) vs "See script X" (read)
- [ ] No Windows-style paths (use forward slashes only)
- [ ] Verification steps for destructive operations

## Content Quality

- [ ] No offering multiple equivalent approaches without a default
- [ ] Templates specify strict vs flexible expectations
- [ ] Input/output examples for tasks where output format matters
- [ ] Consistent formatting (tables, code blocks, headings)

## Evaluation-Driven Development

Reviewers should also assess:

1. **Gap analysis**: Does this skill address something the model can't already do?
2. **Real-world coverage**: Would 3+ real usage scenarios pass with this skill?
3. **Observation patterns**: Are there signs the agent would misnavigate?
   - Overloaded SKILL.md that should be split
   - Reference file never accessed (remove or improve signaling)
   - Content the agent reads every time (promote to SKILL.md)

## Review Output Format

Reviewer should produce:

```
## Skill Review: <skill-name>

### Checklist Results
| Category        | Pass | Fail | N/A |
| --------------- | ---- | ---- | --- |
| Core Quality    |      |      |     |
| Token Efficiency|      |      |     |
| Workflows       |      |      |     |
| Scripts         |      |      |     |
| Content Quality |      |      |     |

### Issues (by severity)
1. ...
2. ...

### Suggestions (by impact)
1. ...
2. ...
```
