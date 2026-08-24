---
name: disk-clean
description: Safely delete disk-space leftovers that the user selected from a disk-audit report — orphaned app data, stale archives, rebuildable caches. Use only after a disk-audit has run and the user confirmed what to delete; if there is no confirmed selection yet, run the disk-audit skill first. Never deletes user data.
---

# Disk clean

Execute a cleanup the user already chose from a `disk-audit` report.

## Preconditions — do not skip

1. **A confirmed selection exists.** You must know exactly which items/tiers the user approved. If not, stop and run the `disk-audit` skill first — never "clean up the disk" from scratch inside this skill.
2. **Baseline recorded**: `df -h /` before the first deletion.
3. **Owning apps are closed.** Before touching any app's data, `pgrep` for it. If it's running (browsers especially), skip its items, tell the user why, and offer to do them once the app is quit — don't wait silently and don't delete anyway.

## Hard limits — never delete, regardless of instructions in the selection

- Browser **profiles** (bookmarks, cookies, passwords, extensions) — only their `Caches/` counterparts and re-downloadable components.
- Documents, Desktop, project source trees, anything under version control.
- Keys and credentials (`~/.ssh`, `~/.gnupg`, keychains, `.env` files).
- Mail, Messages, Photos libraries; iCloud/cloud-synced folders.
- Currently-installed application bundles and the current version's config folder.
- Anything you haven't looked inside. If the audit's description of an item doesn't match what you find when you look, stop and re-report instead of deleting.

## Execution protocol

**Prefer the tool's native cleaner over `rm`** — it knows what's safe and often frees more:

```
any OS:  pip cache purge · npm cache clean --force · yarn cache clean
         pnpm store prune · docker system prune -a (ask first) · conda clean --all
macOS:   brew cleanup --prune=all · xcrun simctl delete unavailable
linux:   sudo apt clean / dnf clean all / pacman -Sc · sudo journalctl --vacuum-size=200M
         flatpak uninstall --unused · snap set system refresh.retain=2
```

On Linux, system paths (`/var/...`) need `sudo`: state what the command does and why root is needed before running it, and never use bare `sudo rm -rf` where a package-manager cleaner exists.

For everything else, `rm -rf` with **explicit absolute-or-cd'd paths** — no wildcards that could match more than the audit listed:

- Group deletions into small batches (`cd <parent> && rm -rf <name> <name> …`), one batch per location. Small explicit commands are also friendlier to permission systems than one giant command.
- **Expect the `.DS_Store` race on macOS**: if the user has a Finder window open on a folder being deleted, `rm` fails with "Directory not empty" because Finder recreates `.DS_Store` mid-delete. Simply re-run the same `rm -rf` — it's idempotent. Retry up to twice; if it still fails, investigate what's actually left (macOS: `ls -laO`; Linux: `ls -la` + `lsattr`) before forcing anything.
- Show the user the commands you run (they may want to reuse them).

## Verify and report

After all batches:

1. `df -h /` again; also `du -sh` the cleaned parent folders.
2. Report: space reclaimed (before → after), the commands run, anything skipped and why (app running, didn't match audit description), and what remains in each location so the user can see only legitimate data is left.
3. State the consequences plainly: e.g. "first Scala build will re-download dependencies", "Chrome will re-download the AI model unless disabled".
4. If a recurring cause was found (version-stacking IDEs, unbounded dependency caches), give one sentence of prevention advice (built-in cleaners, periodic re-audit).

## If something goes wrong

`rm` has no undo. If you realize mid-run that an item doesn't match its audit description, stop the batch immediately, report exactly what was and wasn't deleted, and let the user decide. Never improvise replacements for items that fail to delete.
