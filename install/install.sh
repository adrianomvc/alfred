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
VERSION="${ALFRED_VERSION:-}"
# DEVIN CLI documented global skills path: %APPDATA%\devin\skills on Windows
# (Git Bash sets $APPDATA, e.g. C:\Users\<you>\AppData\Roaming), ~/.config/devin/
# skills on Linux/macOS. Same signal (APPDATA presence) as sync-host-shims.py.
# Convert the Windows path to a Unix form MSYS mkdir/cp accept — do NOT use
# ${APPDATA//\\//}, which does not replace backslashes reliably under MSYS bash.
if [ -n "${APPDATA:-}" ]; then
  if command -v cygpath >/dev/null 2>&1; then
    APPDATA_UNIX="$(cygpath -u "$APPDATA")"
  else
    APPDATA_UNIX="$(printf '%s' "$APPDATA" | tr '\\' '/')"
  fi
  SKILLS_DIR="${ALFRED_SKILLS_DIR:-$APPDATA_UNIX/devin/skills}"
else
  SKILLS_DIR="${ALFRED_SKILLS_DIR:-$HOME/.config/devin/skills}"
fi
RTK_URL="${ALFRED_RTK_URL:-$DEFAULT_RTK_URL}"    # empty on PERSONAL (rtk on PATH); Artifactory zip on CORPORATE
RTK_SHA256="${ALFRED_RTK_SHA256:-}"
SKIP_RTK="${ALFRED_SKIP_RTK:-0}"
NPM_REGISTRY="${ALFRED_NPM_REGISTRY:-$DEFAULT_NPM_REGISTRY}"
CCUSAGE_PACKAGE="${ALFRED_CCUSAGE_PACKAGE:-$DEFAULT_CCUSAGE_PACKAGE}"
CODEBASE_MEMORY_PACKAGE="${ALFRED_CODEBASE_MEMORY_PACKAGE:-$DEFAULT_CODEBASE_MEMORY_PACKAGE}"
SKIP_NPM_TOOLS="${ALFRED_SKIP_NPM_TOOLS:-0}"
SKIP_AI_STACK_CHECK="${ALFRED_SKIP_AI_STACK_CHECK:-0}"

info() { echo "[alfred] $*"; }

command -v git >/dev/null 2>&1 || { echo "git is required but not found on PATH." >&2; exit 1; }
PYTHON_BIN="$(command -v python3 || command -v python || true)"
[ -n "$PYTHON_BIN" ] || { echo "Python is required but not found on PATH." >&2; exit 1; }

# Mode: install only. Alfred keeps one global installation on origin/main.
MODE="${1:-install}"

[ "$MODE" = "install" ] || { echo "Only install mode is supported; Alfred always follows origin/main." >&2; exit 2; }
[ -z "$BRANCH" ] || { echo "ALFRED_BRANCH is no longer supported; Alfred always follows origin/main." >&2; exit 2; }
[ -z "$VERSION" ] || { echo "ALFRED_VERSION is no longer supported; Alfred always follows origin/main." >&2; exit 2; }

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
  if [ -f "$INSTALL_DIR/scripts/alfred.py" ]; then
    # A blocked update (exit 2 — e.g. local changes in ~/.alfred) must not
    # abort the whole re-install: the current framework keeps working.
    UPDATE_RC=0
    "$PYTHON_BIN" "$INSTALL_DIR/scripts/alfred.py" --alfred-home "$INSTALL_DIR" framework update || UPDATE_RC=$?
    if [ "$UPDATE_RC" = "2" ]; then
      info "Framework update was blocked (see message above); keeping the current version and continuing the install."
    elif [ "$UPDATE_RC" != "0" ]; then
      echo "Framework update failed (exit $UPDATE_RC)." >&2
      exit "$UPDATE_RC"
    fi
  else
    # One-time bootstrap from installations created before the canonical CLI.
    git -C "$INSTALL_DIR" fetch --quiet origin main
    git -C "$INSTALL_DIR" checkout --quiet main
    git -C "$INSTALL_DIR" merge --quiet --ff-only origin/main
    "$PYTHON_BIN" "$INSTALL_DIR/scripts/validators/validate-framework.py" --quiet
  fi
elif [ -e "$INSTALL_DIR" ]; then
  # A non-git ~/.alfred is almost always an older install: a copied tree, an
  # unzipped release, or a clone whose .git was lost. Refusing to proceed forced
  # a manual cleanup on every machine, so an install that recognises Alfred is
  # removed and re-cloned — the same call the wrong-remote branch above makes.
  # The framework carries no user data (demands live in the HUB repo), so there
  # is nothing here a fresh clone does not restore.
  #
  # A directory with none of Alfred's markers is someone else's data, not a
  # stale install, and is left untouched: ALFRED_FORCE_INSTALL=1 overrides that
  # deliberately.
  LOOKS_LIKE_ALFRED=0
  for marker in core/boot.md VERSION scripts/alfred.py; do
    if [ -e "$INSTALL_DIR/$marker" ]; then LOOKS_LIKE_ALFRED=1; break; fi
  done
  if [ "$LOOKS_LIKE_ALFRED" = "0" ]; then
    # The markers above assume a stale *complete* install, but the most common
    # non-git ~/.alfred is not one: `framework update` does
    # `runtime.mkdir(parents=True)` before any install exists, so a machine
    # where the skill ran first ends up with a ~/.alfred holding only
    # `runtime/`. That is Alfred's own generated state, not user data — and
    # refusing it left the install permanently stuck.
    if [ -z "$(find "$INSTALL_DIR" -mindepth 1 -maxdepth 1 \
                 ! -name runtime ! -name '.DS_Store' -print -quit 2>/dev/null)" ]; then
      LOOKS_LIKE_ALFRED=1
    fi
  fi
  if [ "$LOOKS_LIKE_ALFRED" = "1" ] || [ "${ALFRED_FORCE_INSTALL:-0}" = "1" ]; then
    info "Existing non-git install at $INSTALL_DIR; removing it and installing fresh."
    rm -rf "$INSTALL_DIR"
  else
    echo "$INSTALL_DIR exists, is not a git repo, and does not look like an Alfred install." >&2
    echo "Nothing was changed. Move it aside, or re-run with ALFRED_FORCE_INSTALL=1 to replace it." >&2
    exit 1
  fi
fi

if [ ! -e "$INSTALL_DIR" ]; then
  CANDIDATE_DIR="${INSTALL_DIR}.candidate.$$"
  info "Cloning framework candidate into $CANDIDATE_DIR"
  git clone --quiet --branch main "$FRAMEWORK_URL" "$CANDIDATE_DIR"
  if "$PYTHON_BIN" "$CANDIDATE_DIR/scripts/validators/validate-framework.py" --quiet; then
    mv "$CANDIDATE_DIR" "$INSTALL_DIR"
  else
    rm -rf "$CANDIDATE_DIR"
    echo "Framework candidate failed validation; installation was not changed." >&2
    exit 2
  fi
fi

INSTALLED_VERSION="unknown"
[ -f "$INSTALL_DIR/VERSION" ] && INSTALLED_VERSION="$(head -n1 "$INSTALL_DIR/VERSION" | tr -d '[:space:]')"
info "Framework version: $INSTALLED_VERSION (origin/main)"

# 2. Install the /alfred skill for the DEVIN CLI at the documented global path
# (~/.config/devin/skills on POSIX). ~/.agents/skills is NOT a Devin skills
# location — agents_standard imports rules from AGENTS.md, not skills.
SKILL_SOURCE="$INSTALL_DIR/hosts/devin-cli/SKILL.md"
[ -f "$SKILL_SOURCE" ] || { echo "Skill source not found: $SKILL_SOURCE" >&2; exit 1; }
SKILL_TARGET="$SKILLS_DIR/alfred"
mkdir -p "$SKILL_TARGET"
cp -f "$SKILL_SOURCE" "$SKILL_TARGET/SKILL.md"
info "Installed skill at $SKILL_TARGET/SKILL.md"

# Install a thin launcher; Python logic remains canonical in scripts/alfred.py.
BIN_DIR="${ALFRED_BIN_DIR:-$HOME/.local/bin}"
mkdir -p "$BIN_DIR"
cp -f "$INSTALL_DIR/install/alfred" "$BIN_DIR/alfred"
chmod +x "$BIN_DIR/alfred"
info "Installed CLI launcher at $BIN_DIR/alfred"

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
  if ! command -v rtk >/dev/null 2>&1 && [ -n "$RTK_URL" ] && [ -z "$RTK_SHA256" ]; then
    info "RTK download skipped: ALFRED_RTK_SHA256 is required for an approved artifact."
  elif ! command -v rtk >/dev/null 2>&1 && [ -n "$RTK_URL" ]; then
    RTK_DIR="$HOME/.local/bin"
    RTK_TMP="$(mktemp -d)"
    mkdir -p "$RTK_DIR"
    info "Downloading RTK from configured RTK URL..."
    if command -v curl >/dev/null 2>&1; then
      curl -fsSL "$RTK_URL" -o "$RTK_TMP/rtk-download"
      if command -v sha256sum >/dev/null 2>&1; then
        RTK_ACTUAL_SHA256="$(sha256sum "$RTK_TMP/rtk-download" | awk '{print $1}')"
      elif command -v shasum >/dev/null 2>&1; then
        RTK_ACTUAL_SHA256="$(shasum -a 256 "$RTK_TMP/rtk-download" | awk '{print $1}')"
      else
        rm -rf "$RTK_TMP"
        echo "No SHA-256 tool available; RTK artifact was not installed." >&2
        exit 1
      fi
      if [ "$(printf '%s' "$RTK_ACTUAL_SHA256" | tr '[:upper:]' '[:lower:]')" != "$(printf '%s' "$RTK_SHA256" | tr '[:upper:]' '[:lower:]')" ]; then
        rm -rf "$RTK_TMP"
        echo "RTK SHA-256 mismatch; artifact was not installed." >&2
        exit 1
      fi
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
    # `rtk init -g` only knows Claude Code (plus --opencode/--gemini); `rtk hook`
    # has no Devin target at all. On a Devin-only machine it has nothing to
    # configure and fails — which is expected, not a problem to chase. Devin is
    # covered by Alfred's own PreToolUse bridge, installed right below.
    RTK_INIT_OUT=""
    if RTK_INIT_OUT="$(rtk init -g 2>&1)"; then
      info "RTK initialized globally (Claude Code config)."
    else
      info "'rtk init -g' did not complete — expected when Claude Code is absent, since it configures Claude Code/OpenCode/Gemini, not Devin."
      info "The DEVIN CLI path does not depend on it; the hook below is what matters. RTK said:"
      printf '%s\n' "$RTK_INIT_OUT" | sed 's/^/    /' | head -5
    fi
    # RTK ships no Devin preset (its stock hook matches Claude's `Bash` tool, not
    # Devin's `exec`), so install Alfred's PreToolUse->rtk bridge into the DEVIN
    # CLI user config. Idempotent; safe to re-run.
    RTK_PYTHON="$(command -v python3 || command -v python || true)"
    if [ -n "$RTK_PYTHON" ]; then
      if "$RTK_PYTHON" "$INSTALL_DIR/scripts/workflow/sync-host-shims.py" -Host devin-cli -InstallHooks -AlfredHome "$INSTALL_DIR" >/dev/null 2>&1; then
        info "DEVIN CLI rtk PreToolUse hook installed (transparent rewrite for exec)."
        info Verify hook capability with /hooks and rtk gain.
      else
        info "Could not install the DEVIN rtk hook automatically; run: python \"$INSTALL_DIR/scripts/workflow/sync-host-shims.py\" -Host devin-cli -InstallHooks"
      fi
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
      RESOLVED="$(npm list -g --depth=0 "$pkg" 2>/dev/null | grep -o "$pkg@[^ ]*" | head -n1)"
      info "npm tool installed/updated: ${RESOLVED:-$pkg} (registry: $NPM_REGISTRY)"
    else
      info "Could not install npm tool '$pkg'. Check Artifactory/npm access; Alfred will degrade."
    fi
  else
    if npm install -g "$pkg" >/dev/null 2>&1; then
      RESOLVED="$(npm list -g --depth=0 "$pkg" 2>/dev/null | grep -o "$pkg@[^ ]*" | head -n1)"
      info "npm tool installed/updated: ${RESOLVED:-$pkg} (registry: public npm)"
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
      # The adapter implements dry-run | active | disabled only; dry-run is the
      # safe default (composes to the outbox, never sends until a human
      # switches to active with SMTP configured).
      cat > "$EMAIL_CONFIG" <<JSON
{
  "mode": "dry-run",
  "default_to": "$EMAIL",
  "telemetry_to": "$TELEMETRY_TO",
  "allowlist": [$ALLOW],
  "smtp": {"host": "", "port": 587, "user": "", "sender": ""}
}
JSON
      info "E-mail registered at $EMAIL_CONFIG (mode: dry-run — composes to the outbox without sending; fill smtp{} and set mode: active to really send)."
      [ -n "$TELEMETRY_TO" ] && info "Telemetry destination: $TELEMETRY_TO (observability batches; provisional e-mail transport, D45)."
    else
      info "E-mail setup skipped. Register later: create $EMAIL_CONFIG (see connectors/notification-email.md)."
    fi
  fi

  MCP_SERVER="$INSTALL_DIR/scripts/adapters/mcp-email-server.py"
  PYTHON_BIN="$(command -v python3 || command -v python || true)"

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
