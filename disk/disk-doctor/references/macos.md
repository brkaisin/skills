# macOS catalog

## The three parallel roots

Most app data stacks in three sibling trees — always check all three for the same app:

| Location | Contains | Typical verdict |
|---|---|---|
| `~/Library/Caches/<App>` | Rebuildable caches | Tier 1 if app uninstalled, Tier 3 otherwise |
| `~/Library/Application Support/<App>` | App state and settings — **often mixes user data with cache** | Break down before judging |
| `~/Library/Logs/<App>` | Logs | Tier 1/2, safe |

## Orphan detection

An app is "installed" if found in `/Applications`, `~/Applications`, via `mdfind "kMDItemFSName == '<App>*.app'"`, or running (`pgrep`). CLI tools: `command -v <tool>`, `brew list`.

## Other hotspots

| Location | Contains | Notes |
|---|---|---|
| `~/Library/Developer/Xcode/DerivedData` | Xcode build products | Tier 3 |
| `~/Library/Developer/CoreSimulator` | iOS simulators | `xcrun simctl delete unavailable` for the Tier 2 part |
| `~/Library/Developer/Xcode/iOS DeviceSupport` | Symbols per iOS version ever attached | Old versions Tier 2 |
| `~/Library/Containers` | Sandboxed app data (often huge: Docker VM disk lives here) | Per-app judgement; Docker's file shrinks via `docker system prune` + Docker Desktop settings, not `rm` |
| `~/Library/Caches/Homebrew` + old kegs | Homebrew downloads and versions | `brew cleanup --prune=all` |
| `~/Library/Caches/install4j` | Installer-framework update cache | Tier 2 |
| `~/.Trash` | Deleted files | Report size only; user empties it |

## macOS quirks

- **`.DS_Store` pollution**: Finder constantly touches `.DS_Store`, making dead folders look freshly used — always exclude it from recency checks (scan.sh does). It also recreates them *during* deletion, causing `rm -rf` to fail with "Directory not empty" — just re-run the `rm`.
- **Purgeable space**: `df` may undercount what's actually free; APFS local snapshots (`tmutil listlocalsnapshots /`) can hold GBs after big deletions and clear themselves over time.

## Out of scope — report but don't touch manually

`/private/var/folders`, `/System/Volumes`, `~/Library/Group Containers`, iCloud `~/Library/Mobile Documents`, `~/Library/Mail`, `Photos Library.photoslibrary`.
