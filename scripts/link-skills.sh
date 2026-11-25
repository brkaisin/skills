#!/usr/bin/env bash
# DEV ONLY, for working on this repo. Not an installer: users install via their
# agent's plugin system or `npx skills` (see README).
#
# Symlinks every skill into the global skill dirs so repo edits apply live:
#   ~/.claude/skills   Claude Code
#   ~/.agents/skills   Codex, Pi, and other Agent Skills harnesses
# Pass other dirs as arguments to override. Existing non-symlinks are left alone.
set -euo pipefail

repo="$(cd "$(dirname "$0")/.." && pwd)"
[ $# -gt 0 ] || set -- "$HOME/.claude/skills" "$HOME/.agents/skills"

for dest in "$@"; do
  mkdir -p "$dest"
  for skill in "$repo"/*/*/SKILL.md; do
    src="$(dirname "$skill")"
    link="$dest/$(basename "$src")"
    if [ -e "$link" ] && [ ! -L "$link" ]; then
      echo "skip  $link (exists, not a symlink)"
      continue
    fi
    ln -sfn "$src" "$link"
    echo "link  $link"
  done
done
