# My agent skills

Personal collection of agent skills, organized by category. Each skill follows the open [Agent Skills](https://docs.claude.com/en/docs/claude-code/skills) convention — a folder with a `SKILL.md` (YAML frontmatter + markdown instructions), plus optional scripts and reference docs — but the content is plain markdown and bash, usable by **any agent that can read files and run shell commands**.

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
```

Categories are for humans browsing the repo; harnesses usually see a flat list, so **skill names must be unique across the whole repo** (kebab-case, e.g. `disk-audit`).

## Install

Nothing from this repo runs at install time: your agent's own plugin system, or the `skills` CLI, copies the skill folders. Pick **one** method per agent, or you'll get every skill twice. Each category (`disk`, `wine`, …) is a separate plugin, so take only what you want.

**Claude Code** (updates itself)

```
/plugin marketplace add brkaisin/skills
/plugin install disk@brkaisin
```

**Codex** (updates at startup)

```bash
codex plugin marketplace add brkaisin/skills
codex plugin add disk@brkaisin
```

**GitHub Copilot CLI**

```bash
copilot plugin marketplace add brkaisin/skills
copilot plugin install disk@brkaisin
```

**Any other agent: Pi, Cursor, Gemini CLI, OpenCode, …** (75+ agents, via [`skills`](https://github.com/vercel-labs/skills))

```bash
npx skills add brkaisin/skills                         # interactive: pick skills and agents
npx skills add brkaisin/skills -s disk-doctor -a pi -g # one skill, one agent, global
npx skills update                                      # update later
```

These copy plain files, so you can read every skill before you use it. Restart a running agent session to pick up new skills.

**Agents without skill support** (plain chat, older tools): paste the relevant `SKILL.md` into context, plus its `references/` files when it says to read them (`npx skills use brkaisin/skills@disk-doctor` prints it as a prompt). Or clone the repo and add one line to `AGENTS.md` or a rule file: *"Skills live in `./skills/`. When a task matches a skill's description (see its `SKILL.md` frontmatter), read that file and follow it."* Skills that call helper scripts need shell access; without it, the agent can follow the workflow manually.

Skills reference each other by name ("invoke the disk-audit skill"): in harnesses without native skill invocation, that simply means "read that skill's `SKILL.md` and follow it". Optional niceties (structured question dialogs, HTML reports) are written with plain-text fallbacks.

## Developing

`scripts/link-skills.sh` symlinks every skill into `~/.claude/skills` and `~/.agents/skills` (Codex, Pi, …), so repo edits apply immediately. It's for working on this repo only; don't also install the plugins on that machine, or skills load twice.

## Adding a new skill

1. Pick or create a category folder.
2. `mkdir <category>/<skill-name> && cp _template/SKILL.template.md <category>/<skill-name>/SKILL.md`, then edit it.
3. Frontmatter rules: `name` = folder name, lowercase-kebab, unique; `description` says **what it does and when to use it**. That's what triggers it, so include the phrases a user would actually say.
4. Keep `SKILL.md` under ~150 lines; push details into `references/` (loaded only when needed) and repeatable shell work into `scripts/`. Keep instructions harness-neutral: name capabilities ("a structured question tool, if available"), not specific tool brands.
   For a multi-step workflow that must stay atomic (one entry point, parts never installed or invoked separately), make it ONE skill with phase documents inside (see `disk/disk-doctor`: `SKILL.md` + `AUDIT.md` + `CLEAN.md`) rather than several skills.
5. Register it: add `"./<skill-name>"` to `<category>/.claude-plugin/plugin.json` → `skills`. For a **new category**, also create that `plugin.json` (copy `disk/`'s), add an entry to `.claude-plugin/marketplace.json`, and add `"./<category>"` to `skills.sh.json` → `paths`.
6. Bump `version` in the category's `plugin.json` whenever its skills change. Plugin installs only update when the version changes.
7. Check: `claude plugin validate .` and `npx skills add ./ --list` should both show the skill.

## Categories

| Category (plugin) | Skills | Purpose |
|---|---|---|
| [disk](disk/) | `disk-doctor` | Disk-space analysis and safe cleanup (macOS + Linux) |
| [wine](wine/) | `wine-tasting-sheets` | Printable tasting sheets (PDF) for a list of wines, with maps, in any language |
