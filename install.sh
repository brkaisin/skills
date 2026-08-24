#!/usr/bin/env bash
# Install skills from this repo into a skills directory.
#
#   ./install.sh                     interactive: lists skills, asks which to install
#   ./install.sh disk                install a whole category
#   ./install.sh disk-audit ...      install specific skills (mix with categories freely)
#   ./install.sh --all               install everything (no questions — for scripts/CI)
#
# Options:
#   --copy          copy instead of symlink (default: symlink, repo edits apply immediately)
#   --dir <path>    target directory (default: $SKILLS_DIR or $CLAUDE_SKILLS_DIR
#                   or ~/.claude/skills — the Claude Code personal skills dir)
#
# Skills are the folders containing a SKILL.md (repo layout: <category>/<skill>/SKILL.md).
# Existing non-symlink folders in the target are never overwritten.
set -euo pipefail

REPO="$(cd "$(dirname "$0")" && pwd)"
DEST="${SKILLS_DIR:-${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}}"
MODE="link"
ALL="no"
WANTED=()
while [ $# -gt 0 ]; do
  case "$1" in
    --copy) MODE="copy"; shift ;;
    --dir)  DEST="${2:?--dir needs a path}"; shift 2 ;;
    --all)  ALL="yes"; shift ;;
    --help|-h) sed -n '2,16p' "$0"; exit 0 ;;
    --*) echo "unknown option: $1 (see --help)" >&2; exit 1 ;;
    *) WANTED+=("$1"); shift ;;
  esac
done

# Collect skills as "category/name", checking name uniqueness.
NAMES=() CATS=() DIRS=()
while IFS= read -r skill_md; do
  dir="$(dirname "$skill_md")"
  case "$dir" in "$REPO/_template"*) continue ;; esac
  name="$(basename "$dir")"
  cat="$(basename "$(dirname "$dir")")"
  [ "$cat" = "$(basename "$REPO")" ] && cat="."   # uncategorized skill at repo root
  for n in "${NAMES[@]:-}"; do
    [ "$n" = "$name" ] && { echo "ERROR: duplicate skill name '$name' — names must be unique" >&2; exit 1; }
  done
  NAMES+=("$name"); CATS+=("$cat"); DIRS+=("$dir")
done < <(find "$REPO" -mindepth 2 -maxdepth 3 -name SKILL.md | sort)
[ ${#NAMES[@]} -gt 0 ] || { echo "no skills found in $REPO" >&2; exit 1; }

# No selection given: ask interactively (in a terminal), otherwise install all.
if [ "$ALL" = "no" ] && [ ${#WANTED[@]} -eq 0 ]; then
  if [ -t 0 ]; then
    echo "Available skills:"
    for i in "${!NAMES[@]}"; do printf '  %-12s %s\n' "[${CATS[$i]}]" "${NAMES[$i]}"; done
    echo
    read -r -p "Install which? (skill/category names, space-separated; empty = all) " line || line=""
    # shellcheck disable=SC2206
    WANTED=($line)
  fi
fi

selected() { # skill is selected if --all, no selection, or its name/category was asked for
  [ "$ALL" = "yes" ] && return 0
  [ ${#WANTED[@]} -eq 0 ] && return 0
  for w in "${WANTED[@]}"; do
    [ "$w" = "$1" ] || [ "$w" = "$2" ] && return 0
  done
  return 1
}

# Warn about selection terms that matched nothing (typo protection).
for w in "${WANTED[@]:-}"; do
  [ -z "$w" ] && continue
  hit="no"
  for i in "${!NAMES[@]}"; do
    { [ "$w" = "${NAMES[$i]}" ] || [ "$w" = "${CATS[$i]}" ]; } && hit="yes" && break
  done
  [ "$hit" = "no" ] && echo "  warn: '$w' matches no skill or category — skipping it" >&2
done

mkdir -p "$DEST"
installed=0 skipped=0
for i in "${!NAMES[@]}"; do
  name="${NAMES[$i]}"
  selected "$name" "${CATS[$i]}" || continue
  target="$DEST/$name"
  if [ -e "$target" ] && [ ! -L "$target" ]; then
    echo "  skip     $name (already exists in $DEST and is not a symlink)"
    skipped=$((skipped + 1))
    continue
  fi
  rm -f "$target"                      # safe: only reached for symlinks or nothing
  if [ "$MODE" = "copy" ]; then
    cp -R "${DIRS[$i]}" "$target"
  else
    ln -s "${DIRS[$i]}" "$target"
  fi
  echo "  install  $name  ->  $target  ($MODE)"
  installed=$((installed + 1))
done

echo
echo "Done: $installed installed, $skipped skipped. Skills dir: $DEST"
