#!/usr/bin/env bash
# Install Alfred for the DEVIN CLI on macOS/Linux.
#
# Clones (or updates) the Alfred framework into ~/.alfred and installs the
# /alfred skill into the DEVIN CLI user skills directory
# (~/.agents/skills/alfred/SKILL.md).
#
# Usage:
#   bash install/install.sh
#   curl -fsSL https://raw.githubusercontent.com/adrianomvc/alfred/main/install/install.sh | bash
set -euo pipefail

FRAMEWORK_URL="${ALFRED_FRAMEWORK_URL:-https://github.com/adrianomvc/alfred.git}"
INSTALL_DIR="${ALFRED_INSTALL_DIR:-$HOME/.alfred}"
BRANCH="${ALFRED_BRANCH:-}"
SKILLS_DIR="${ALFRED_SKILLS_DIR:-$HOME/.agents/skills}"

info() { echo "[alfred] $*"; }

command -v git >/dev/null 2>&1 || { echo "git is required but not found on PATH." >&2; exit 1; }

# 1. Clone or update the framework into ~/.alfred
if [ -d "$INSTALL_DIR/.git" ]; then
  info "Updating existing framework at $INSTALL_DIR"
  git -C "$INSTALL_DIR" fetch --quiet origin
  [ -n "$BRANCH" ] && git -C "$INSTALL_DIR" checkout --quiet "$BRANCH"
  git -C "$INSTALL_DIR" pull --quiet --ff-only
elif [ -e "$INSTALL_DIR" ]; then
  echo "$INSTALL_DIR exists but is not a git repo. Move or remove it, then re-run." >&2
  exit 1
else
  info "Cloning framework into $INSTALL_DIR"
  if [ -n "$BRANCH" ]; then
    git clone --quiet --branch "$BRANCH" "$FRAMEWORK_URL" "$INSTALL_DIR"
  else
    git clone --quiet "$FRAMEWORK_URL" "$INSTALL_DIR"
  fi
fi

# 2. Install the /alfred skill for the DEVIN CLI
SKILL_SOURCE="$INSTALL_DIR/install/devin/alfred/SKILL.md"
[ -f "$SKILL_SOURCE" ] || { echo "Skill source not found: $SKILL_SOURCE" >&2; exit 1; }
SKILL_TARGET="$SKILLS_DIR/alfred"
mkdir -p "$SKILL_TARGET"
cp -f "$SKILL_SOURCE" "$SKILL_TARGET/SKILL.md"
info "Installed skill at $SKILL_TARGET/SKILL.md"

# 3. Verify (best-effort) if the DEVIN CLI is available
if command -v devin >/dev/null 2>&1; then
  info "Verifying with DEVIN CLI..."
  if devin skills list 2>&1 | grep -q "/alfred"; then
    info "OK: /alfred is registered."
  else
    info "Skill copied, but '/alfred' did not appear in 'devin skills list'. Check 'devin skills paths'."
  fi
else
  info "DEVIN CLI not found on PATH; skill files are installed. Run 'devin skills list' to confirm."
fi

info "Done. Open a repo and type /alfred in the DEVIN CLI."
