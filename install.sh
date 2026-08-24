#!/usr/bin/env bash
# Install every skill in this repo into a skills directory.
#
#   ./install.sh                 symlink skills (default — repo edits apply immediately)
#   ./install.sh --copy          copy instead of symlink
#   ./install.sh --dir <path>    target directory (default: $SKILLS_DIR or
#                                $CLAUDE_SKILLS_DIR or ~/.claude/skills)
#
# Skills are the folders containing a SKILL.md (repo layout: <category>/<skill>/SKILL.md).
# Existing non-symlink folders in the target are never overwritten.
set -euo pipefail

REPO="$(cd "$(dirname "$0")" && pwd)"
DEST="${SKILLS_DIR:-${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}}"
MODE="link"
while [ $# -gt 0 ]; do
  case "$1" in
    --copy) MODE="copy"; shift ;;
    --dir)  DEST="${2:?--dir needs a path}"; shift 2 ;;
    *) echo "usage: $0 [--copy] [--dir <path>]" >&2; exit 1 ;;
  esac
done
mkdir -p "$DEST"

installed=0 skipped=0
declare -a seen=()

while IFS= read -r skill_md; do
  dir="$(dirname "$skill_md")"
  name="$(basename "$dir")"
  case "$dir" in "$REPO/_template"*) continue ;; esac

  for s in "${seen[@]:-}"; do
    if [ "$s" = "$name" ]; then
      echo "ERROR: duplicate skill name '$name' in the repo — names must be unique" >&2
      exit 1
    fi
  done
  seen+=("$name")

  target="$DEST/$name"
  if [ -e "$target" ] && [ ! -L "$target" ]; then
    echo "  skip     $name (already exists in $DEST and is not a symlink)"
    skipped=$((skipped + 1))
    continue
  fi

  rm -f "$target"                      # safe: only reached for symlinks or nothing
  if [ "$MODE" = "copy" ]; then
    cp -R "$dir" "$target"
  else
    ln -s "$dir" "$target"
  fi
  echo "  install  $name  ->  $target  ($MODE)"
  installed=$((installed + 1))
done < <(find "$REPO" -mindepth 2 -maxdepth 3 -name SKILL.md | sort)

echo
echo "Done: $installed installed, $skipped skipped. Skills dir: $DEST"
