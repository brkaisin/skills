# Audit phase (disk-doctor step 2)

Analyze where disk space is going and what could safely be reclaimed. **This phase is strictly read-only.** Do not delete, move, or modify anything, even if the user says "just clean it" — finish the audit and the report first; deletion happens in `CLEAN.md` after the user has chosen.

## Workflow

### 1. Establish context

- Record free space now: `df -h /` (this is the baseline the cleanup will be measured against).
- Detect OS (`uname`) and read the matching catalog: `references/common.md` always, plus `references/macos.md` or `references/linux.md`.
- List installed applications (macOS: `ls /Applications ~/Applications`; Linux: `dpkg -l`/`rpm -qa`/`pacman -Q`, `flatpak list`, `snap list`).
- Note which relevant apps are currently running (`pgrep`) — affects what can be safely cleaned later.

### 2. Scan

Use the helper script for a fast, consistent first pass:

```bash
scripts/scan.sh hotspots            # sizes of all known cache/data/log locations
scripts/scan.sh breakdown <dir>     # children of a folder, largest first
scripts/scan.sh recency <dir>...    # last real use (ignores .DS_Store noise)
```

Deep-dive every hotspot over ~500 MB with `breakdown` until you understand *what the bytes actually are* (e.g. "4 GB of Chrome is an on-device AI model", not just "Chrome is 6.8 GB"). The `references/` catalogs explain known locations and what each one contains. On Linux, system paths (`/var/...`) under-report without root — label those sizes "at least" or re-check with `sudo du`.

### 3. Detect leftovers (the highest-value findings)

Cross-reference data folders against installed apps:

- **Orphans**: config/cache/log folders whose application is no longer installed. Verify absence properly before calling something an orphan — macOS: `/Applications`, `~/Applications`, `mdfind`, running processes; Linux: package manager, `flatpak list`, `snap list`, `command -v`; both: `pgrep`.
- **Version stacks**: many tools keep one folder per version (`AppName2024.1`, `AppName2025.2`, …) and never remove old ones. Find the *currently installed* version (build/version file inside the app bundle), then everything older is a leftover. The same app often stacks in three places at once: Application Support, Caches, and Logs.
- **Superseded installers/downloads**: update caches, `.dmg`/`.tar.gz` archives of things already installed.

### 4. Check recency

For anything not clearly orphaned, check when it was last really used with `scan.sh recency`. It excludes `.DS_Store` (macOS Finder touches those constantly and makes dead folders look active); on Linux, be similarly suspicious of `~/.cache/thumbnails`-style noise inside otherwise-dead trees. Unused for 12+ months → treat as dead weight.

### 5. Classify into tiers

| Tier | What | Risk |
|---|---|---|
| **1 — Dead weight** | Orphans of uninstalled apps; caches unused 12+ months | None |
| **2 — Stale archives** | Old installers, superseded versions, download caches of already-installed software | None |
| **3 — Rebuildable, active** | Dependency/build caches in current use (pip, npm, Coursier, Gradle, Docker…) | None lost, but next build re-downloads |
| **Keep** | User data (browser profiles, documents, projects, keys, mail, photos), current-app state, active tool binaries | Never propose |

When in doubt between Tier and Keep, put it in Keep and mention it in the report as "left alone, here's why".

### 6. Present the report visually

The user decides from this report, so make it genuinely readable:

- Lead with the headline: total reclaimable, split per tier.
- One table per tier: path, size, last used, what it is in plain words, and what happens if deleted.
- Explicitly list what you are **not** touching and why (builds trust).
- If your environment can publish an HTML page (e.g. an Artifact tool), also produce a visual report: a bar chart of space by location colored by tier, and the tier tables. Otherwise a clean markdown layout in the terminal is fine.

### 7. Let the user choose

Ask which tiers (or individual items) to clean — use a structured question tool (e.g. AskUserQuestion) if available, with your recommendation first: Tiers 1+2 are the no-brainer default; Tier 3 for maximum reclaim. Then proceed to `CLEAN.md` with the confirmed selection. Never start deleting inside this phase.

## Notes

- `du` on large trees is slow; run independent scans in parallel and be patient rather than sampling.
- System-managed locations are out of scope: report them if huge, but recommend OS-level tools instead of manual deletion. Each OS reference file lists its no-go zones.
- Downloads and Trash are user files: report their size, but only the user can decide item by item — never classify them into a tier.
