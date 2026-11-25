# Contributing

## Layout

```
<category>/                     one folder per topic (disk, wine, …) = one installable plugin
  .claude-plugin/plugin.json    plugin manifest: version + the skill folders it ships
  README.md                     what the category's skills do, how they relate
  <skill-name>/                 one folder per skill
    SKILL.md                    required: frontmatter (name, description) + instructions
    scripts/                    optional: helper scripts the skill calls
    references/                 optional: docs the skill loads on demand
.claude-plugin/marketplace.json lists the category plugins (Claude Code, Codex, Copilot)
skills.sh.json                  tells `npx skills` where the skills live
_template/SKILL.template.md     starting point for new skills
scripts/link-skills.sh          dev only: symlink skills for live editing
docs/                           images for the README (not installed)
```

Categories are for humans browsing the repo. Agents usually see a flat list, so **skill names must be unique across the whole repo** (kebab-case, e.g. `disk-audit`).

## Working on the skills locally

`scripts/link-skills.sh` symlinks every skill into `~/.claude/skills` and `~/.agents/skills` (Codex, Pi, …), so your edits apply immediately. Pass other directories as arguments to link there instead. Don't also install the plugins on that machine, or every skill loads twice. Restart the agent session to pick up new skills.

## Adding a skill

1. Pick or create a category folder.
2. `mkdir <category>/<skill-name> && cp _template/SKILL.template.md <category>/<skill-name>/SKILL.md`, then edit it.
3. Frontmatter rules: `name` = folder name, lowercase-kebab, unique. `description` says **what it does and when to use it**. That's what triggers it, so include the phrases a user would actually say.
4. Keep `SKILL.md` under ~150 lines. Put details in `references/`, which the agent loads only when needed, and repeatable shell work in `scripts/`. Keep instructions agent-neutral: name capabilities ("a structured question tool, if available"), not specific tool brands. Give plain-text fallbacks for optional niceties such as question dialogs and HTML reports.
   For a multi-step workflow that must stay atomic (one entry point, parts never installed or invoked separately), make it ONE skill with phase documents inside, rather than several skills. See `disk/disk-doctor`: `SKILL.md` + `AUDIT.md` + `CLEAN.md`.
5. Register it: add `"./<skill-name>"` to `skills` in `<category>/.claude-plugin/plugin.json`. For a **new category**, also:
   - create that `plugin.json` (copy `disk/`'s);
   - add an entry to `.claude-plugin/marketplace.json`;
   - add `"./<category>"` to `paths` in `skills.sh.json`;
   - add the skill to the root `README.md`.
6. Bump `version` in the category's `plugin.json` whenever its skills change. Plugin installs only update when the version changes.
7. Check: `claude plugin validate .` and `npx skills add ./ --list` should both show the skill.

Skills can reference each other by name ("invoke the disk-audit skill"). In agents without native skill invocation, that means "read that skill's `SKILL.md` and follow it".
