# Disk-space skills

One skill, **disk-doctor**, for macOS and Linux: a full checkup-and-cleanup pipeline with a hard safety gate in the middle.

```
diagnose → audit (read-only) → USER CHOOSES → clean (only the selection) → report
```

It ships as a single skill on purpose: the analysis, the choice gate, and the cleanup are inseparable — you can't install or invoke the destructive part on its own. The phases live inside the skill as documents the agent loads when each step starts:

```
disk-doctor/
  SKILL.md                  the entry point and pipeline (the only invocable skill)
  AUDIT.md                  analysis phase: scan → detect leftovers → tier → visual report
  CLEAN.md                  deletion phase: safety protocol, native cleaners, hard limits
  scripts/scan.sh           fast read-only scans (hotspots / breakdown / recency),
                            macOS + Linux paths, BSD/GNU-portable
  references/common.md      cross-platform: dev caches, version-stacking apps, browsers
  references/macos.md       Library roots, Xcode, Homebrew, .DS_Store quirks, no-go zones
  references/linux.md       XDG roots, package managers, flatpak/snap, /var caches, sudo notes
```

## Install

Claude Code: `/plugin install disk --marketplace brkaisin/skills`. Codex / Copilot: the `disk@brkaisin` plugin. Any other agent: `npx skills add brkaisin/skills -s disk-doctor`. Details in the [repo README](../README.md#install). Then ask your agent:

> "my disk is full" / "what can I clean?"

## The tier model

1. **Dead weight** — data of uninstalled apps, caches unused 12+ months → delete, zero risk
2. **Stale archives** — old installers, superseded versions → delete, zero risk
3. **Rebuildable** — dependency caches in active use → free space now, re-download later
4. **Keep** — user data, profiles, current app state → never proposed

## Safety model

Analysis is always read-only. Deletion happens only after the user picks tiers/items from the report, never touches the no-go list (profiles, documents, keys, projects…), checks apps aren't running first, prefers tool-native cleaners over `rm`, and measures before/after. Automated/scheduled runs stop after the audit and never delete.
