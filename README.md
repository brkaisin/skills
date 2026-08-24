# My agent skills

Personal collection of agent skills, organized by category. Each skill follows the open [Agent Skills](https://docs.claude.com/en/docs/claude-code/skills) convention — a folder with a `SKILL.md` (YAML frontmatter + markdown instructions), plus optional scripts and reference docs — but the content is plain markdown and bash, usable by **any agent that can read files and run shell commands**.

## Layout

```
<category>/               one folder per topic (disk, git, deploy, …)
  README.md               what the category's skills do, how they relate
  <skill-name>/           one folder per skill — this is what gets installed
    SKILL.md              required: frontmatter (name, description) + instructions
    scripts/              optional: helper scripts the skill calls
    references/           optional: docs the skill loads on demand
_template/                starting point for new skills
install.sh                symlinks/copies every skill into a skills directory
```

Categories are for humans browsing the repo; harnesses usually see a flat list, so **skill names must be unique across the whole repo** (kebab-case, e.g. `disk-audit`).

## Install

```bash
./install.sh                     # symlink into ~/.claude/skills (Claude Code default)
./install.sh --dir <path>        # any other target directory
./install.sh --copy              # copy instead of symlink (for machines where this repo won't stay)
```

Symlinks mean edits in the repo apply immediately. Existing non-symlink folders in the target are never overwritten.

## Using with different harnesses

- **Claude Code / Claude API / Agent SDK** — native support: run `./install.sh` (personal) or `./install.sh --dir <project>/.claude/skills` (per-project). Skills auto-trigger from their descriptions; `/skill-name` invokes one explicitly.
- **Codex CLI and other AGENTS.md-based tools** — clone the repo next to your project and add one line to `AGENTS.md`: *"Skills live in `./skills/`. When a task matches a skill's description (see its `SKILL.md` frontmatter), read that file and follow it."*
- **Cursor / similar rule systems** — same one-liner as a rule (e.g. `.cursor/rules`), pointing at the repo path.
- **Any other agent, or a plain chat** — paste the relevant `SKILL.md` into context (plus its `references/` files when it says to read them). Skills that call helper scripts need shell access; without it, the agent can follow the workflow manually.

Skills reference each other by name ("invoke the disk-audit skill"): in harnesses without native skill invocation, that simply means "read that skill's `SKILL.md` and follow it". Optional niceties (structured question dialogs, HTML reports) are written with plain-text fallbacks.

## Adding a new skill

1. Pick or create a category folder.
2. `cp -R _template <category>/<skill-name>` and edit `SKILL.md`.
3. Frontmatter rules: `name` = folder name, lowercase-kebab, unique; `description` says **what it does and when to use it** — that's what triggers it, so include the phrases a user would actually say.
4. Keep `SKILL.md` under ~150 lines; push details into `references/` (loaded only when needed) and repeatable shell work into `scripts/`. Keep instructions harness-neutral: name capabilities ("a structured question tool, if available"), not specific tool brands.
5. Re-run `./install.sh`.

## Categories

| Category | Skills | Purpose |
|---|---|---|
| [disk](disk/) | `disk-doctor`, `disk-audit`, `disk-clean` | Disk-space analysis and safe cleanup (macOS + Linux) |
