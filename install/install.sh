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
VERSION="${ALFRED_VERSION:-}"   # e.g. v0.2.0 — pin a reproducible release tag
SKILLS_DIR="${ALFRED_SKILLS_DIR:-$HOME/.agents/skills}"

info() { echo "[alfred] $*"; }

command -v git >/dev/null 2>&1 || { echo "git is required but not found on PATH." >&2; exit 1; }

# Mode: install (default) | list | rollback. e.g. `bash install.sh rollback`.
MODE="${1:-install}"

# Version-management modes operate on an existing install and exit (they do not
# touch the installed skill).
if [ "$MODE" = "list" ] || [ "$MODE" = "rollback" ]; then
  [ -d "$INSTALL_DIR/.git" ] || { echo "No framework install found at $INSTALL_DIR. Run the installer first." >&2; exit 1; }
  git -C "$INSTALL_DIR" fetch --quiet --tags origin
  CURRENT="$(git -C "$INSTALL_DIR" describe --tags 2>/dev/null || true)"
  # tags newest-first
  mapfile -t TAGS < <(git -C "$INSTALL_DIR" tag --sort=-v:refname)

  if [ "$MODE" = "list" ]; then
    info "Installed: $CURRENT"
    info "Available versions (newest first):"
    for t in "${TAGS[@]}"; do
      case "$CURRENT" in "$t"*) echo "  $t <- current";; *) echo "  $t";; esac
    done
    exit 0
  fi

  CURRENT_TAG="$(git -C "$INSTALL_DIR" describe --tags --abbrev=0 2>/dev/null || true)"
  PREV=""
  for i in "${!TAGS[@]}"; do
    if [ "${TAGS[$i]}" = "$CURRENT_TAG" ]; then
      PREV="${TAGS[$((i+1))]:-}"
      break
    fi
  done
  [ -z "$CURRENT_TAG" ] && PREV="${TAGS[0]:-}"   # untagged commit -> latest tag
  [ -n "$PREV" ] || { echo "Already at the oldest version ($CURRENT_TAG); nothing to roll back to." >&2; exit 1; }
  info "Rolling back: $CURRENT_TAG -> $PREV"
  git -C "$INSTALL_DIR" checkout --quiet "$PREV"
  info "Now on $PREV. Re-run the installer without 'rollback' to return to latest."
  exit 0
fi

# VERSION (a tag) takes precedence over BRANCH; with neither, default branch (latest).
REF="${VERSION:-$BRANCH}"

# 1. Clone or update the framework into ~/.alfred
if [ -d "$INSTALL_DIR/.git" ]; then
  info "Updating existing framework at $INSTALL_DIR"
  git -C "$INSTALL_DIR" fetch --quiet --tags origin
  if [ -n "$VERSION" ]; then
    git -C "$INSTALL_DIR" checkout --quiet "$VERSION"   # pinned tag (detached); no pull
  elif [ -n "$BRANCH" ]; then
    git -C "$INSTALL_DIR" checkout --quiet "$BRANCH"
    git -C "$INSTALL_DIR" pull --quiet --ff-only
  else
    # Return to the latest on the default branch. This also recovers from a
    # pinned/rolled-back (detached) state, where a bare `pull` would fail.
    git -C "$INSTALL_DIR" remote set-head origin --auto >/dev/null 2>&1 || true
    DEFAULT="$(git -C "$INSTALL_DIR" symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null | sed 's#^origin/##')"
    [ -n "$DEFAULT" ] || DEFAULT="main"
    git -C "$INSTALL_DIR" checkout --quiet "$DEFAULT"
    git -C "$INSTALL_DIR" pull --quiet --ff-only
  fi
elif [ -e "$INSTALL_DIR" ]; then
  echo "$INSTALL_DIR exists but is not a git repo. Move or remove it, then re-run." >&2
  exit 1
else
  info "Cloning framework into $INSTALL_DIR"
  git clone --quiet "$FRAMEWORK_URL" "$INSTALL_DIR"
  [ -n "$REF" ] && git -C "$INSTALL_DIR" checkout --quiet "$REF"
fi

INSTALLED_VERSION="unknown"
[ -f "$INSTALL_DIR/VERSION" ] && INSTALLED_VERSION="$(head -n1 "$INSTALL_DIR/VERSION" | tr -d '[:space:]')"
info "Framework version: $INSTALLED_VERSION${VERSION:+ (pinned $VERSION)}"

# 2. Install the /alfred skill for the DEVIN CLI
SKILL_SOURCE="$INSTALL_DIR/hosts/devin-cli/SKILL.md"
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
