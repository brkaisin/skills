# My agent skills

Personal collection of [agent skills](https://docs.claude.com/en/docs/claude-code/skills) for Claude Code, organized by category.

## Layout

```
<category>/               one folder per topic (disk, git, deploy, …)
  README.md               what the category's skills do, how they relate
  <skill-name>/           one folder per skill — this is what gets installed
    SKILL.md              required: frontmatter (name, description) + instructions
    scripts/              optional: helper scripts the skill calls
    references/           optional: docs the skill loads on demand
_template/                starting point for new skills
install.sh                installs every skill into ~/.claude/skills
```

Categories are for humans browsing the repo; Claude Code sees a flat list, so **skill names must be unique across the whole repo** (kebab-case, e.g. `disk-audit`).

## Install

```bash
./install.sh          # symlinks every skill into ~/.claude/skills (edits here apply immediately)
./install.sh --copy   # copies instead, for a machine where this repo won't stay
```

Existing non-symlink folders in `~/.claude/skills` are never overwritten. To use skills in a single project instead, point the installer there: `CLAUDE_SKILLS_DIR=path/to/project/.claude/skills ./install.sh`.

## Adding a new skill

1. Pick or create a category folder.
2. `cp -R _template <category>/<skill-name>` and edit `SKILL.md`.
3. Frontmatter rules: `name` = folder name, lowercase-kebab, unique; `description` says **what it does and when to use it** — that's what triggers it, so include the phrases a user would actually say.
4. Keep `SKILL.md` under ~150 lines; push details into `references/` (loaded only when needed) and repeatable shell work into `scripts/`.
5. Re-run `./install.sh`.

## Categories

| Category | Skills | Purpose |
|---|---|---|
| [disk](disk/) | `disk-doctor`, `disk-audit`, `disk-clean` | Disk-space analysis and safe cleanup (macOS + Linux) |
