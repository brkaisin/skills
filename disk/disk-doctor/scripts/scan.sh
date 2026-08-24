#!/usr/bin/env bash
# scan.sh — read-only helpers for the disk-audit skill.
#
# usage:
#   scan.sh hotspots              sizes of known cache/data/log locations, largest first
#   scan.sh breakdown <dir> [n]   sizes of <dir>'s children, largest first (default top 25)
#   scan.sh recency <dir>...      date of newest real file per dir (ignores .DS_Store)
set -uo pipefail

newest_mtime() { # portable: BSD stat on macOS, GNU stat elsewhere
  if stat -f '%m' /dev/null >/dev/null 2>&1; then
    find "$1" -type f ! -name '.DS_Store' -print0 2>/dev/null | xargs -0 stat -f '%m' 2>/dev/null | sort -rn | head -1
  else
    find "$1" -type f ! -name '.DS_Store' -printf '%T@\n' 2>/dev/null | sort -rn | head -1 | cut -d. -f1
  fi
}

fmt_date() {
  if date -r 0 '+%Y' >/dev/null 2>&1; then date -r "$1" '+%Y-%m-%d'; else date -d "@$1" '+%Y-%m-%d'; fi
}

case "${1:-help}" in
  hotspots)
    dirs=(
      # macOS
      "$HOME/Library/Caches"
      "$HOME/Library/Application Support"
      "$HOME/Library/Logs"
      "$HOME/Library/Developer"          # Xcode: DerivedData, simulators, archives
      "$HOME/Library/Android"            # Android SDK
      "$HOME/Library/Containers"
      "$HOME/.Trash"
      # cross-platform dev-tool caches in $HOME
      "$HOME/.cache"
      "$HOME/.gradle" "$HOME/.m2" "$HOME/.ivy2" "$HOME/.sbt"
      "$HOME/.npm" "$HOME/.yarn" "$HOME/.pnpm-store" "$HOME/.bun"
      "$HOME/.cargo" "$HOME/.rustup"
      "$HOME/.android" "$HOME/.docker" "$HOME/.minikube"
      "$HOME/.cocoapods" "$HOME/.nuget" "$HOME/.conda" "$HOME/.pyenv" "$HOME/.nvm"
      # user files: report only, never tier
      "$HOME/Downloads"
      # Linux (XDG roots, sandboxed apps, system caches — /var sizes need sudo for accuracy)
      "$HOME/.local/share" "$HOME/.local/state" "$HOME/.var/app" "$HOME/snap"
      "$HOME/.local/share/Trash" "$HOME/.mozilla"
      "/var/cache/apt" "/var/cache/dnf" "/var/cache/pacman/pkg"
      "/var/log" "/var/lib/snapd/snaps" "/var/lib/flatpak" "/var/lib/docker"
    )
    for d in "${dirs[@]}"; do [ -e "$d" ] && du -sh "$d" 2>/dev/null; done | sort -rh
    ;;
  breakdown)
    [ -n "${2:-}" ] || { echo "usage: scan.sh breakdown <dir> [n]" >&2; exit 1; }
    du -sh "$2"/* "$2"/.[!.]* 2>/dev/null | sort -rh | head -"${3:-25}"
    ;;
  recency)
    shift
    for d in "$@"; do
      m=$(newest_mtime "$d")
      if [ -n "${m:-}" ]; then echo "$(fmt_date "$m")  $d"; else echo "no-files    $d"; fi
    done | sort -r
    ;;
  *)
    sed -n '2,7p' "$0"
    ;;
esac
