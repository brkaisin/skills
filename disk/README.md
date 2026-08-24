# Disk-space skills

Three agent skills for **macOS and Linux** that work together:

| Skill | Role | Deletes? |
|---|---|---|
| **disk-doctor** | Entry point: detects OS and disk pressure, runs the whole pipeline (audit → your choice → cleanup → report), offers optional recurring re-audits | Orchestrates only |
| **disk-audit** | Scans caches, app data, logs and dev-tool folders; finds leftovers from uninstalled apps; classifies into risk tiers; presents a visual report | Never |
| **disk-clean** | Executes the selection from the audit with a safety protocol (app-running checks, native cleaners, no-touch list, before/after measurement) | Only what you chose |

The separation is the safety model: analysis is always free to run; deletion requires an audit plus your explicit choice. Automated/scheduled runs never delete.

## Install (Claude Code)

Use the repo installer (installs all categories): `../install.sh` — or copy just these three folders into `~/.claude/skills/`. Then in any session:

```
/disk-doctor         # the one command: diagnose → audit → choose → clean → report
```

`/disk-audit` (analysis only) and `/disk-clean` (after an audit) also work standalone. Natural language works too: "my disk is full" triggers disk-doctor.

## Layout

```
disk-doctor/
  SKILL.md                  the pipeline: diagnose → audit → choose (gate) → clean →
                            report → optional automation
disk-audit/
  SKILL.md                  workflow: scan → detect leftovers → tier → report → ask
  scripts/scan.sh           fast read-only scans (hotspots / breakdown / recency),
                            macOS + Linux paths, BSD/GNU-portable
  references/common.md      cross-platform: dev caches, version-stacking apps, browsers
  references/macos.md       Library roots, Xcode, Homebrew, .DS_Store quirks, no-go zones
  references/linux.md       XDG roots, package managers, flatpak/snap, /var caches, sudo notes
disk-clean/
  SKILL.md                  deletion protocol, native cleaners per OS, hard limits, verification
```

## The tier model

1. **Dead weight** — data of uninstalled apps, caches unused 12+ months → delete, zero risk
2. **Stale archives** — old installers, superseded versions → delete, zero risk
3. **Rebuildable** — dependency caches in active use → free space now, re-download later
4. **Keep** — user data, profiles, current app state → never proposed
