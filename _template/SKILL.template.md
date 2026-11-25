---
name: my-skill-name
description: One or two sentences saying WHAT this skill does and WHEN to use it. This text is how the agent decides to trigger the skill, so include the phrases a user would actually say ("use when the user asks to X, mentions Y, or wants Z"). If the skill is dangerous or depends on another skill, say so here too.
---

# Skill title

One line stating the goal and any hard boundary (e.g. "read-only", "never touches user data").

## Workflow

### 1. First step

What to check or gather before acting. Prefer commands the agent can run verbatim:

```bash
some --command
```

### 2. Next step

Keep steps short and imperative. Link supporting material instead of inlining it:
read `references/details.md` when X; run `scripts/helper.sh` for Y.

### 3. Present / confirm

If the skill does anything irreversible, define the gate explicitly: what must be
shown to the user, and what counts as consent.

## Notes

- Edge cases, known quirks, and what to do when something fails.
- What is out of scope for this skill (and which skill covers it instead).

<!--
Checklist before shipping a skill:
- [ ] folder name == frontmatter `name`, unique across the repo
- [ ] description contains trigger phrases, not just a summary
- [ ] SKILL.md < ~150 lines; details moved to references/, shell to scripts/
- [ ] scripts are executable (chmod +x) and pass `bash -n`
- [ ] delete this comment, and the scripts/ or references/ dirs if unused
-->
