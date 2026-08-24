# Linux catalog

## The XDG roots

| Location | Contains | Typical verdict |
|---|---|---|
| `~/.cache/<app>` | Rebuildable caches (XDG_CACHE_HOME) | Tier 1 if app gone, Tier 3 otherwise |
| `~/.config/<app>` | Settings — small but orphans linger | Tier 1 if app gone |
| `~/.local/share/<app>` | App data — **mixes user data with cache**, break down first | Per app |
| `~/.local/state/<app>` | Logs/state | Tier 1/2 |
| `~/.local/share/Trash` | Trash | Report size only; user empties it |

Legacy apps still use bare dotfolders in `$HOME` (`~/.mozilla`, `~/.thunderbird` — these contain **profiles → Keep**).

## Orphan detection

An app is "installed" if it appears in the package manager or as a binary:

- Debian/Ubuntu: `dpkg -l | grep -i <name>` — Fedora: `rpm -qa | grep -i <name>` — Arch: `pacman -Q | grep -i <name>`
- Sandboxed: `flatpak list`, `snap list`
- CLI tools / manual installs: `command -v <tool>`, check `~/.local/bin`, `/opt`, `/usr/local`

## System-level hotspots (need `sudo` for accurate sizes; propose, don't assume)

| Location | Contains | Native cleaner |
|---|---|---|
| `/var/cache/apt` | Downloaded .debs | `sudo apt clean` |
| `/var/cache/dnf` or `/var/cache/yum` | RPM cache | `sudo dnf clean all` |
| `/var/cache/pacman/pkg` | Package cache | `sudo pacman -Sc` (keeps installed versions) |
| `/var/log` + journal | Logs | `sudo journalctl --vacuum-size=200M` |
| `/var/lib/snapd/snaps` + `~/snap` | Snap revisions (keeps 2-3 old ones per app) | `snap set system refresh.retain=2`; remove old revisions via `snap remove --revision` |
| `/var/lib/flatpak` + `~/.local/share/flatpak` | Flatpak runtimes | `flatpak uninstall --unused` |
| `/var/lib/docker` | Images, volumes, build cache | `docker system prune -a` (ask first) |
| old kernels | `/boot` pressure on small partitions | `apt autoremove` / distro tool — never delete kernels manually |

## Linux quirks

- `du` silently under-reports on root-owned paths — re-run with `sudo du` before presenting system-level numbers, or label them "at least".
- Thumbnail cache (`~/.cache/thumbnails`) grows unbounded — always Tier 3.
- Flatpak/snap apps duplicate runtimes; the cleaners above are the only safe way to prune them.

## Out of scope — report but don't touch manually

`/proc`, `/sys`, `/run`, swapfiles, `/var/lib/dpkg|rpm` databases, anything under another user's `$HOME`.
