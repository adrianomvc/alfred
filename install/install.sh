#!/usr/bin/env bash
# Install Alfred for the DEVIN CLI on macOS/Linux.
#
# Clones (or updates) the Alfred framework into ~/.alfred and installs the
# /alfred skill into the DEVIN CLI global skills directory on POSIX
# (~/.config/devin/skills/alfred/SKILL.md — the documented path).
#
# Usage:
#   bash install/install.sh
#   curl -fsSL https://raw.githubusercontent.com/adrianomvc/alfred/refs/heads/main/install/install.sh | bash
#   # corporate: pass ALFRED_FRAMEWORK_URL=... (internal mirror) or uncomment the
#   # CORPORATE profile below.
set -euo pipefail

# ============================================================================
# ENVIRONMENT PROFILES — two sets of source URLs. PERSONAL is active by
# default; CORPORATE is kept commented right below it. To prepare the corporate
# machine/image, comment the three PERSONAL lines and uncomment the three
# CORPORATE ones (or just pass ALFRED_FRAMEWORK_URL / ALFRED_RTK_URL /
# ALFRED_NPM_REGISTRY, which override either profile).
#
# Notes that apply to both profiles:
# - RTK: PERSONAL assumes `rtk` is already on PATH (installed via cargo/manual
#   download). The installer detects it and only runs `rtk init -g`; it does not
#   `npm install rtk`, because the public npm `rtk` is a DIFFERENT tool (Rust
#   Type Kit) — see the name-collision note in RTK.md. On CORPORATE, the zip is
#   fetched from the internal Artifactory mirror.
# - npm registry: PERSONAL uses public npm (empty = registry.npmjs.org).
#   CORPORATE uses the Artifactory npm-remote; proxy/SSL come from ~/.npmrc,
#   never hardcoded here. `ccusage` is confirmed available on both.
# - `codebase-memory-mcp` stays NOT installed by default on both: its npm
#   postinstall pulls a binary from GitHub Releases, blocked by the corporate
#   proxy/SWG (verified 2026-07-13). Opt in via ALFRED_CODEBASE_MEMORY_PACKAGE
#   once an approved path exists. See `connectors/codebase-memory.md`.
# ============================================================================

# --- PERSONAL (public GitHub + public npm; rtk already on PATH) — ACTIVE ---
DEFAULT_FRAMEWORK_URL="https://github.com/adrianomvc/alfred.git"
DEFAULT_RTK_URL=""              # empty: rtk is on PATH; installer skips download and runs `rtk init -g`
DEFAULT_NPM_REGISTRY=""         # empty: public npm (registry.npmjs.org)

# --- CORPORATE (internal mirror + Artifactory) — uncomment on the corp image ---
# DEFAULT_FRAMEWORK_URL="https://github.com/itau-corp/itau-sq9-modules-alfred-v2.git"
# DEFAULT_RTK_URL="https://artifactory.prod.aws.cloud.ihf/artifactory/generic-github-remote/rtk-ai/rtk/releases/download/v0.43.0/rtk-x86_64-pc-windows-msvc.zip"
# DEFAULT_NPM_REGISTRY="https://artifactory.prod.aws.cloud.ihf/artifactory/api/npm/npm-remote/"

DEFAULT_CCUSAGE_PACKAGE="ccusage"
DEFAULT_CODEBASE_MEMORY_PACKAGE=""

FRAMEWORK_URL="${ALFRED_FRAMEWORK_URL:-$DEFAULT_FRAMEWORK_URL}"
INSTALL_DIR="${ALFRED_INSTALL_DIR:-$HOME/.alfred}"
BRANCH="${ALFRED_BRANCH:-}"
VERSION="${ALFRED_VERSION:-}"   # e.g. v0.2.0 — pin a reproducible release tag
SKILLS_DIR="${ALFRED_SKILLS_DIR:-$HOME/.config/devin/skills}"   # DEVIN CLI documented global skills path (POSIX)
RTK_URL="${ALFRED_RTK_URL:-$DEFAULT_RTK_URL}"    # empty on PERSONAL (rtk on PATH); Artifactory zip on CORPORATE
SKIP_RTK="${ALFRED_SKIP_RTK:-0}"
NPM_REGISTRY="${ALFRED_NPM_REGISTRY:-$DEFAULT_NPM_REGISTRY}"
CCUSAGE_PACKAGE="${ALFRED_CCUSAGE_PACKAGE:-$DEFAULT_CCUSAGE_PACKAGE}"
CODEBASE_MEMORY_PACKAGE="${ALFRED_CODEBASE_MEMORY_PACKAGE:-$DEFAULT_CODEBASE_MEMORY_PACKAGE}"
SKIP_NPM_TOOLS="${ALFRED_SKIP_NPM_TOOLS:-0}"
SKIP_AI_STACK_CHECK="${ALFRED_SKIP_AI_STACK_CHECK:-0}"

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

normalize_git_url() {
  printf '%s' "$1" | sed -e 's#\.git/*$##' -e 's#/*$##' | tr '[:upper:]' '[:lower:]'
}

# 1. Clone or update the framework into ~/.alfred
# Guard against a stale clone left over from a different repo/mirror (old
# fork, a personal remote, a migrated internal URL, ...): fetching/pulling
# from the wrong origin would silently keep the wrong framework installed.
# When the remote does not match FRAMEWORK_URL, wipe and re-clone fresh.
if [ -d "$INSTALL_DIR/.git" ]; then
  CURRENT_REMOTE="$(git -C "$INSTALL_DIR" remote get-url origin 2>/dev/null || true)"
  if [ -n "$CURRENT_REMOTE" ] && [ "$(normalize_git_url "$CURRENT_REMOTE")" != "$(normalize_git_url "$FRAMEWORK_URL")" ]; then
    info "Existing install at $INSTALL_DIR points to a different remote ('$CURRENT_REMOTE' != '$FRAMEWORK_URL'). Removing and re-cloning."
    rm -rf "$INSTALL_DIR"
  fi
fi

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

# 2. Install the /alfred skill for the DEVIN CLI at the documented global path
# (~/.config/devin/skills on POSIX). ~/.agents/skills is NOT a Devin skills
# location — agents_standard imports rules from AGENTS.md, not skills.
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

# 4. RTK terminal hook (DEVIN CLI only) — optional token-control layer.
# No URL means no download; Alfred falls back to bounded native commands.
if [ "$SKIP_RTK" != "1" ]; then
  if ! command -v rtk >/dev/null 2>&1 && [ -n "$RTK_URL" ]; then
    RTK_DIR="$HOME/.local/bin"
    RTK_TMP="$(mktemp -d)"
    mkdir -p "$RTK_DIR"
    info "Downloading RTK from configured RTK URL..."
    if command -v curl >/dev/null 2>&1; then
      curl -fsSL "$RTK_URL" -o "$RTK_TMP/rtk-download"
    else
      info "curl not found; install RTK manually, then run 'rtk init -g'."
    fi

    if [ -f "$RTK_TMP/rtk-download" ]; then
      case "$RTK_URL" in
        *.zip)
          if command -v unzip >/dev/null 2>&1; then
            unzip -q "$RTK_TMP/rtk-download" -d "$RTK_TMP/unpacked"
            # Artifactory zip may name the binary rtk or rtk.exe; accept either.
            CANDIDATE="$(find "$RTK_TMP/unpacked" -type f \( -name rtk -o -name rtk.exe \) -perm -u+x 2>/dev/null | head -n1)"
            [ -n "$CANDIDATE" ] || CANDIDATE="$(find "$RTK_TMP/unpacked" -type f \( -name rtk -o -name rtk.exe \) 2>/dev/null | head -n1)"
            [ -n "$CANDIDATE" ] && cp "$CANDIDATE" "$RTK_DIR/rtk"
          else
            info "unzip not found; install RTK manually, then run 'rtk init -g'."
          fi
          ;;
        *.tar.gz|*.tgz)
          tar -xzf "$RTK_TMP/rtk-download" -C "$RTK_TMP"
          CANDIDATE="$(find "$RTK_TMP" -type f -name rtk -perm -u+x 2>/dev/null | head -n1)"
          [ -n "$CANDIDATE" ] || CANDIDATE="$(find "$RTK_TMP" -type f -name rtk 2>/dev/null | head -n1)"
          [ -n "$CANDIDATE" ] && cp "$CANDIDATE" "$RTK_DIR/rtk"
          ;;
        *)
          cp "$RTK_TMP/rtk-download" "$RTK_DIR/rtk"
          ;;
      esac
      [ -f "$RTK_DIR/rtk" ] && chmod +x "$RTK_DIR/rtk"
      export PATH="$RTK_DIR:$PATH"
    fi
    rm -rf "$RTK_TMP"
  fi

  if command -v rtk >/dev/null 2>&1; then
    if rtk init -g >/dev/null 2>&1; then
      info "RTK initialized globally for DEVIN CLI terminal sessions."
    else
      info "RTK found, but 'rtk init -g' did not complete. Run it manually when ready."
    fi
  else
    info "RTK setup skipped: configure ALFRED_RTK_URL if the default is unavailable."
  fi
fi

# 5. Optional npm tools (corporate Artifactory path): ccusage today; other
# packages may be added via ALFRED_CODEBASE_MEMORY_PACKAGE (empty by default,
# see COMPANY SETTINGS above). Best-effort: these tools improve usage
# attribution, but Alfred still works without them.
install_npm_tool() {
  local pkg="$1"
  [ -n "$pkg" ] || return 0
  if [ -n "$NPM_REGISTRY" ]; then
    if npm install -g "$pkg" --registry "$NPM_REGISTRY" >/dev/null 2>&1; then
      info "npm tool installed/updated: $pkg"
    else
      info "Could not install npm tool '$pkg'. Check Artifactory/npm access; Alfred will degrade."
    fi
  else
    if npm install -g "$pkg" >/dev/null 2>&1; then
      info "npm tool installed/updated: $pkg"
    else
      info "Could not install npm tool '$pkg'. Check npm access; Alfred will degrade."
    fi
  fi
}

if [ "$SKIP_NPM_TOOLS" != "1" ]; then
  if command -v npm >/dev/null 2>&1; then
    install_npm_tool "$CCUSAGE_PACKAGE"
    install_npm_tool "$CODEBASE_MEMORY_PACKAGE"
  else
    info "npm not found; skipping optional npm tools (ccusage)."
  fi
fi

# 6. AI Stack CLI availability (best-effort) — powers skills/ai-stack-finder.
# There is no "AI Stack MCP server" to register: `@ai-stack/cli` is a plain CLI
# (like ccusage) invoked on demand via `npx`, never installed globally here.
# This step only checks the npm `@ai-stack` scope and warms the npx cache so
# the first real search is not slowed down by the download.
if [ "$SKIP_AI_STACK_CHECK" != "1" ]; then
  if command -v npm >/dev/null 2>&1; then
    AI_STACK_SCOPE_REGISTRY="$(npm config get @ai-stack:registry 2>/dev/null || true)"
    if [ -n "$AI_STACK_SCOPE_REGISTRY" ] && [ "$AI_STACK_SCOPE_REGISTRY" != "undefined" ]; then
      info "Warming up AI Stack CLI (npx @ai-stack/cli)..."
      if npx -y @ai-stack/cli@latest --version >/dev/null 2>&1; then
        info "AI Stack CLI available: skills/ai-stack-finder can search the internal catalog (npx @ai-stack/cli)."
      else
        info "AI Stack CLI (npx @ai-stack/cli) did not run. skills/ai-stack-finder will degrade to the next catalog in the order (see knowledge/external-catalogs.md)."
      fi
    else
      info "npm scope '@ai-stack' is not configured (.npmrc); skills/ai-stack-finder will degrade to the next catalog. See knowledge/external-catalogs.md."
    fi
  else
    info "npm not found; skipping AI Stack CLI check. skills/ai-stack-finder will degrade to the next catalog."
  fi
fi

# 7. Notification adapter (MCP e-mail) — owner decision: channel is MCP + Python.
# Registers the destination (~/.alfred-email.json, dry-run by default) and the MCP
# server in Claude Code when available. Fully non-interactive (no prompt, ever):
# the destination defaults to the org telemetry address in knowledge/notification.md
# so every runner's logs reach it regardless of the machine the install runs on.
# Skip entirely with ALFRED_SKIP_EMAIL=1. Best-effort: failures never break the install.
if [ "${ALFRED_SKIP_EMAIL:-}" != "1" ]; then
  EMAIL_CONFIG="$HOME/.alfred-email.json"
  EMAIL="${ALFRED_EMAIL:-}"
  if [ -f "$EMAIL_CONFIG" ]; then
    info "E-mail config already registered at $EMAIL_CONFIG (kept as is)."
  else
    # Org telemetry destination: from ALFRED_TELEMETRY_TO or knowledge/notification.md
    # (aggregates every runner's observability logs — provisional until the telemetry API, D45).
    TELEMETRY_TO="${ALFRED_TELEMETRY_TO:-}"
    if [ -z "$TELEMETRY_TO" ] && [ -f "$INSTALL_DIR/knowledge/notification.md" ]; then
      TELEMETRY_TO="$(sed -n 's/^- telemetry_to: *`\{0,1\}\([^` ]*\)`\{0,1\}.*/\1/p' "$INSTALL_DIR/knowledge/notification.md" | head -n1)"
    fi
    # No prompt: default_to falls back to the org telemetry address when no
    # explicit ALFRED_EMAIL override is given, so logs always land somewhere
    # without asking the operator.
    [ -z "$EMAIL" ] && [ -n "$TELEMETRY_TO" ] && EMAIL="$TELEMETRY_TO"
    if [ -n "$EMAIL" ] || [ -n "$TELEMETRY_TO" ]; then
      ALLOW=""
      [ -n "$EMAIL" ] && ALLOW="\"$EMAIL\""
      if [ -n "$TELEMETRY_TO" ] && [ "$TELEMETRY_TO" != "$EMAIL" ]; then
        [ -n "$ALLOW" ] && ALLOW="$ALLOW, "
        ALLOW="$ALLOW\"$TELEMETRY_TO\""
      fi
      cat > "$EMAIL_CONFIG" <<JSON
{
  "mode": "auto",
  "default_to": "$EMAIL",
  "telemetry_to": "$TELEMETRY_TO",
  "allowlist": [$ALLOW],
  "smtp": {"host": "", "port": 587, "user": "", "password": "", "sender": ""}
}
JSON
      info "E-mail registered at $EMAIL_CONFIG (mode: auto — sends via the local Outlook desktop client when available (Windows), otherwise falls back to dry-run; fill smtp{} and set mode: active to force SMTP instead)."
      [ -n "$TELEMETRY_TO" ] && info "Telemetry destination: $TELEMETRY_TO (observability batches; provisional e-mail transport, D45)."
    else
      info "E-mail setup skipped. Register later: create $EMAIL_CONFIG (see connectors/notification-email.md)."
    fi
  fi

  MCP_SERVER="$INSTALL_DIR/scripts/adapters/mcp-email-server.py"
  PYTHON_BIN="$(command -v python3 || command -v python || true)"

  # pywin32 (optional; best-effort; Windows/Git Bash only) — only what
  # `mode: auto`/`outlook-com` needs to drive the local Outlook desktop
  # client. The adapter itself stays stdlib-only: it degrades to dry-run
  # when this is missing or the OS is not Windows.
  case "$(uname -s 2>/dev/null || true)" in
    MINGW*|MSYS*|CYGWIN*)
      if [ -n "$PYTHON_BIN" ]; then
        if ! "$PYTHON_BIN" -c "import win32com.client" >/dev/null 2>&1; then
          if "$PYTHON_BIN" -m pip install --user --quiet pywin32 >/dev/null 2>&1; then
            info "pywin32 installed: mode 'auto'/'outlook-com' can drive the local Outlook desktop client."
          else
            info "pywin32 not installed (pip failed); e-mail 'auto' mode will use dry-run until it is available."
          fi
        fi
      fi
      ;;
  esac

  if command -v claude >/dev/null 2>&1 && [ -n "$PYTHON_BIN" ] && [ -f "$MCP_SERVER" ]; then
    if claude mcp get alfred-email >/dev/null 2>&1; then
      info "MCP 'alfred-email' already registered in Claude Code."
    elif claude mcp add --scope user alfred-email -- "$PYTHON_BIN" "$MCP_SERVER" >/dev/null 2>&1; then
      info "MCP 'alfred-email' registered in Claude Code (user scope)."
    else
      info "Could not register the MCP automatically. Manual: claude mcp add --scope user alfred-email -- $PYTHON_BIN \"$MCP_SERVER\""
    fi
  else
    [ -z "$PYTHON_BIN" ] && info "Python 3 not found; the MCP e-mail server needs it."
    command -v claude >/dev/null 2>&1 || info "Claude Code CLI not found; for other MCP hosts register: python \"$MCP_SERVER\" (stdio)."
  fi
  info "DEVIN projects: MCP servers (alfred-email + Context7) are per-repo — on first boot the /alfred skill offers to create .devin/config.local.json from $INSTALL_DIR/hosts/devin-cli/config.local.template.json (after human confirmation), resolving \${env:ALFRED_HOME}/\${env:CONTEXT7_API_KEY}. AI Stack MCPs (Figma, ServiceNow, Atlan, ...) get added dynamically by skills/ai-stack-finder when installed."
fi

info "Done. Open a repo and type /alfred in the DEVIN CLI."