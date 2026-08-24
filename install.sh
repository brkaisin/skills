#!/usr/bin/env bash
# Install skills from this repo into a skills directory.
#
#   ./install.sh                     interactive picker: ↑/↓ move, space toggle,
#                                    a = all/none, enter = install, q = quit
#   ./install.sh disk                install a whole category
#   ./install.sh disk-audit ...      install specific skills (mix with categories freely)
#   ./install.sh --all               install everything (no questions — for scripts/CI)
#
# Options:
#   --copy          copy instead of symlink (default: symlink, repo edits apply immediately)
#   --dir <path>    target directory (default: $SKILLS_DIR or $CLAUDE_SKILLS_DIR
#                   or ~/.claude/skills — the Claude Code personal skills dir).
#                   For Claude Code project skills use <project>/.claude/skills.
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
    --help|-h) sed -n '2,18p' "$0"; exit 0 ;;
    --*) echo "unknown option: $1 (see --help)" >&2; exit 1 ;;
    *) WANTED+=("$1"); shift ;;
  esac
done

# ---------- collect skills as category/name, enforcing unique names ----------
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

# ---------- interactive picker (checkbox menu) ----------
pick_interactive() {
  local cursor=0 key rest i n=${#NAMES[@]} lines=$(( ${#NAMES[@]} + 2 ))
  local -a sel=()
  for i in "${!NAMES[@]}"; do sel[$i]=1; done            # start with everything selected
  printf '\033[?25l'                                      # hide cursor
  trap 'printf "\033[?25h"' EXIT
  # draw once, then redraw in place
  local first=1
  while :; do
    [ "$first" = 0 ] && printf '\033[%dA' "$lines"
    first=0
    printf '\r\033[2K%s\n' "Select skills to install into: $DEST"
    for i in "${!NAMES[@]}"; do
      local mark="[ ]"; [ "${sel[$i]}" = 1 ] && mark="[x]"
      if [ "$i" = "$cursor" ]; then
        printf '\r\033[2K  \033[7m%s %-20s %s\033[0m\n' "$mark" "${NAMES[$i]}" "(${CATS[$i]})"
      else
        printf '\r\033[2K  %s %-20s %s\n' "$mark" "${NAMES[$i]}" "(${CATS[$i]})"
      fi
    done
    printf '\r\033[2K  \033[2m↑/↓ move · space toggle · a all/none · enter install · q quit\033[0m\n'
    IFS= read -rsn1 key </dev/tty
    if [ "$key" = $'\x1b' ]; then
      IFS= read -rsn2 -t 0.05 rest </dev/tty || rest=""
      case "$rest" in
        '[A') cursor=$(( (cursor + n - 1) % n )) ;;      # up
        '[B') cursor=$(( (cursor + 1) % n )) ;;          # down
      esac
    else
      case "$key" in
        k) cursor=$(( (cursor + n - 1) % n )) ;;
        j) cursor=$(( (cursor + 1) % n )) ;;
        ' ') sel[$cursor]=$(( 1 - sel[$cursor] )) ;;
        a|A) local any=0; for i in "${!sel[@]}"; do [ "${sel[$i]}" = 1 ] && any=1; done
             for i in "${!sel[@]}"; do sel[$i]=$(( 1 - any )); done ;;
        q|Q) printf '\033[?25h'; echo "aborted — nothing installed"; exit 130 ;;
        '') break ;;                                     # enter
      esac
    fi
  done
  printf '\033[?25h'
  WANTED=()
  for i in "${!NAMES[@]}"; do [ "${sel[$i]}" = 1 ] && WANTED+=("${NAMES[$i]}"); done
  [ ${#WANTED[@]} -gt 0 ] || { echo "nothing selected — nothing installed"; exit 0; }
  ALL="no"
}

# No selection given: pick interactively in a terminal, otherwise install all.
if [ "$ALL" = "no" ] && [ ${#WANTED[@]} -eq 0 ] && [ -t 0 ] && [ -t 1 ]; then
  pick_interactive
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

# ---------- install ----------
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

# Claude Code only reads skills from ~/.claude/skills or <project>/.claude/skills —
# warn if the target is neither, and remind that running sessions need a restart.
case "$DEST" in
  "$HOME/.claude/skills"|*/.claude/skills) ;;
  *) echo "note: Claude Code won't discover skills here — use ~/.claude/skills (personal)"
     echo "      or <project>/.claude/skills (project). Other harnesses: see README." ;;
esac
[ "$installed" -gt 0 ] && echo "note: restart any running agent session to pick up new skills."
