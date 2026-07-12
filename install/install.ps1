<#
.SYNOPSIS
  Install Alfred for the DEVIN CLI on Windows.

.DESCRIPTION
  Clones (or updates) the Alfred framework into the user folder (~/.alfred) and
  installs the `/alfred` skill into the DEVIN CLI user skills directory
  (%APPDATA%\devin\skills\alfred\SKILL.md).

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File install/install.ps1

.EXAMPLE
  irm https://raw.githubusercontent.com/adrianomvc/alfred/main/install/install.ps1 | iex

.EXAMPLE
  # Pin a specific framework version (reproducible)
  powershell -ExecutionPolicy Bypass -File install/install.ps1 -Version v0.2.0
#>
param(
  # ==========================================================================
  # COMPANY SETTINGS - edit these defaults when preparing the installer for a
  # corporate machine/image.
  #
  # 1) Alfred framework repository:
  #    Replace the default below when the company uses an internal Git mirror.
  #
  # 2) RTK package URL:
  #    The default is the public Windows zip placeholder because most company
  #    usage is Windows/Git Bash and the future Artifactory package is also zip.
  #    Replace it with the internal Artifactory zip when available.
  #
  # Temporary alternative:
  #    Keep this file unchanged and pass -FrameworkUrl / -RtkUrl at install time.
  # ==========================================================================
  [string]$FrameworkUrl = "https://github.com/adrianomvc/alfred.git",
  [string]$InstallDir = (Join-Path $HOME ".alfred"),
  [string]$Branch = "",
  [string]$Version = "",
  [string]$SkillsDir = (Join-Path $env:APPDATA "devin/skills"),
  [string]$Email = "",        # notification destination; prompts interactively when omitted
  [switch]$SkipEmail,          # skip the e-mail/MCP notification setup entirely
  [string]$RtkUrl = "https://github.com/rtk-ai/rtk/releases/download/v0.43.0/rtk-x86_64-pc-windows-msvc.zip",        # public zip placeholder; replace with corporate Artifactory URL
  [switch]$SkipRtk,             # skip RTK terminal hook setup entirely
  [string]$NpmRegistry = "",    # optional corporate npm registry / Artifactory URL
  [string]$CcusagePackage = "ccusage",
  [string]$CodebaseMemoryPackage = "codebase-memory",
  [switch]$SkipNpmTools,        # skip npm tool setup entirely
  [switch]$List,
  [switch]$Rollback
)

$ErrorActionPreference = "Stop"

function Info($m) { Write-Host "[alfred] $m" }

# 1. Preconditions
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
  throw "git is required but was not found on PATH."
}

# Version-management modes operate on an existing install and exit (they do not
# touch the installed skill). Use these to inspect or roll back the framework.
if ($List -or $Rollback) {
  if (-not (Test-Path -LiteralPath (Join-Path $InstallDir ".git"))) {
    throw "No framework install found at $InstallDir. Run the installer first."
  }
  git -C $InstallDir fetch --quiet --tags origin
  $tags = @(git -C $InstallDir tag --sort=-v:refname)   # descending: newest first
  $current = (git -C $InstallDir describe --tags 2>$null)

  if ($List) {
    Info "Installed: $current"
    Info "Available versions (newest first):"
    foreach ($t in $tags) {
      $mark = if ($current -like "$t*") { " <- current" } else { "" }
      Write-Host "  $t$mark"
    }
    return
  }

  # Rollback one version: the tag immediately below the current one.
  $currentTag = (git -C $InstallDir describe --tags --abbrev=0 2>$null)
  $idx = [array]::IndexOf($tags, $currentTag)
  if ($idx -lt 0) {
    $previous = $tags | Select-Object -First 1          # on an untagged commit -> latest tag
  } elseif ($idx + 1 -lt $tags.Count) {
    $previous = $tags[$idx + 1]
  } else {
    throw "Already at the oldest version ($currentTag); nothing to roll back to."
  }
  Info "Rolling back: $currentTag -> $previous"
  git -C $InstallDir checkout --quiet $previous
  Info "Now on $previous. Re-run the installer without -Rollback to return to latest."
  return
}

# $Version (a release tag, e.g. v0.2.0) pins a reproducible version; it takes
# precedence over $Branch. With neither, the default branch (latest) is used.
$ref = if ($Version -ne "") { $Version } else { $Branch }

# 2. Clone or update the framework into ~/.alfred
if (Test-Path -LiteralPath (Join-Path $InstallDir ".git")) {
  Info "Updating existing framework at $InstallDir"
  git -C $InstallDir fetch --quiet --tags origin
  if ($Version -ne "") {
    git -C $InstallDir checkout --quiet $Version   # pinned tag (detached); no pull
  } elseif ($Branch -ne "") {
    git -C $InstallDir checkout --quiet $Branch
    git -C $InstallDir pull --quiet --ff-only
  } else {
    # Return to the latest on the default branch. This also recovers from a
    # pinned/rolled-back (detached) state, where a bare `pull` would fail.
    git -C $InstallDir remote set-head origin --auto | Out-Null
    $default = (git -C $InstallDir symbolic-ref --quiet --short refs/remotes/origin/HEAD)
    if ($default) { $default = $default -replace '^origin/', '' } else { $default = "main" }
    git -C $InstallDir checkout --quiet $default
    git -C $InstallDir pull --quiet --ff-only
  }
} elseif (Test-Path -LiteralPath $InstallDir) {
  throw "$InstallDir exists but is not a git repo. Move or remove it, then re-run."
} else {
  Info "Cloning framework into $InstallDir"
  # core.longpaths handles deep example paths beyond the Windows MAX_PATH limit.
  git -c core.longpaths=true clone --quiet $FrameworkUrl $InstallDir
  if ($ref -ne "") { git -C $InstallDir checkout --quiet $ref }
}

$installedVersion = "unknown"
if (Test-Path -LiteralPath (Join-Path $InstallDir "VERSION")) {
  $installedVersion = (Get-Content -LiteralPath (Join-Path $InstallDir "VERSION") -TotalCount 1).Trim()
}
Info "Framework version: $installedVersion$(if ($Version -ne '') { " (pinned $Version)" })"

# 3. Install the /alfred skill for the DEVIN CLI
$skillSource = Join-Path $InstallDir "hosts/devin-cli/SKILL.md"
if (-not (Test-Path -LiteralPath $skillSource)) {
  throw "Skill source not found: $skillSource"
}
$skillTarget = Join-Path $SkillsDir "alfred"
New-Item -ItemType Directory -Force -Path $skillTarget | Out-Null
Copy-Item -LiteralPath $skillSource -Destination (Join-Path $skillTarget "SKILL.md") -Force
Info "Installed skill at $skillTarget\SKILL.md"

# 4. Verify (best-effort) if the DEVIN CLI is available
$devin = Get-Command devin -ErrorAction SilentlyContinue
if ($devin) {
  Info "Verifying with DEVIN CLI..."
  $listed = & $devin.Source skills list 2>&1 | Select-String "/alfred"
  if ($listed) {
    Info "OK: $($listed.ToString().Trim())"
  } else {
    Info "Skill copied, but '/alfred' did not appear in 'devin skills list'. Check 'devin skills paths'."
  }
} else {
  Info "DEVIN CLI not found on PATH; skill files are installed. Run 'devin skills list' to confirm."
}

# 5. RTK terminal hook (DEVIN CLI only) — optional token-control layer.
# No URL means no download; Alfred falls back to bounded native commands.
if (-not $SkipRtk) {
  try {
    if ($RtkUrl -eq "" -and $env:ALFRED_RTK_URL) { $RtkUrl = $env:ALFRED_RTK_URL }

    $rtk = Get-Command rtk -ErrorAction SilentlyContinue
    if (-not $rtk -and $RtkUrl -ne "") {
      $rtkRoot = Join-Path $HOME ".alfred-tools/rtk"
      New-Item -ItemType Directory -Force -Path $rtkRoot | Out-Null
      $leaf = Split-Path ([Uri]$RtkUrl).AbsolutePath -Leaf
      if ($leaf -eq "") { $leaf = "rtk.exe" }
      $download = Join-Path $rtkRoot $leaf
      Info "Downloading RTK from configured RTK URL..."
      Invoke-WebRequest -Uri $RtkUrl -OutFile $download

      if ($download.ToLowerInvariant().EndsWith(".zip")) {
        Expand-Archive -LiteralPath $download -DestinationPath $rtkRoot -Force
        $candidate = Get-ChildItem -LiteralPath $rtkRoot -Recurse -File |
          Where-Object { $_.Name -in @("rtk.exe", "rtk") } |
          Select-Object -First 1
        if ($candidate) { Copy-Item -LiteralPath $candidate.FullName -Destination (Join-Path $rtkRoot "rtk.exe") -Force }
      } else {
        if ((Split-Path $download -Leaf) -ne "rtk.exe") {
          Copy-Item -LiteralPath $download -Destination (Join-Path $rtkRoot "rtk.exe") -Force
        }
      }

      $userPath = [Environment]::GetEnvironmentVariable("Path", "User")
      if ($userPath -notlike "*$rtkRoot*") {
        [Environment]::SetEnvironmentVariable("Path", "$userPath;$rtkRoot", "User")
        Info "Added RTK directory to the user PATH: $rtkRoot"
      }
      $env:Path = "$env:Path;$rtkRoot"
      $rtk = Get-Command rtk -ErrorAction SilentlyContinue
    }

    if ($rtk) {
      & $rtk.Source init -g *> $null
      if ($LASTEXITCODE -eq 0) { Info "RTK initialized globally for DEVIN CLI terminal sessions." }
      else { Info "RTK found, but 'rtk init -g' did not complete. Run it manually when ready." }
    } else {
      Info "RTK setup skipped: configure -RtkUrl or ALFRED_RTK_URL if the default is unavailable."
    }
  } catch {
    Info "RTK setup skipped ($($_.Exception.Message)). Alfred will use bounded native commands."
  }
}

# 6. Optional npm tools (corporate Artifactory path): ccusage + codebase-memory.
# Best-effort: these tools improve usage attribution and brownfield discovery,
# but Alfred still works without them.
if (-not $SkipNpmTools) {
  try {
    if ($NpmRegistry -eq "" -and $env:ALFRED_NPM_REGISTRY) { $NpmRegistry = $env:ALFRED_NPM_REGISTRY }
    if ($env:ALFRED_CCUSAGE_PACKAGE) { $CcusagePackage = $env:ALFRED_CCUSAGE_PACKAGE }
    if ($env:ALFRED_CODEBASE_MEMORY_PACKAGE) { $CodebaseMemoryPackage = $env:ALFRED_CODEBASE_MEMORY_PACKAGE }

    $npm = Get-Command npm -ErrorAction SilentlyContinue
    if (-not $npm) {
      Info "npm not found; skipping optional npm tools (ccusage/codebase-memory)."
    } else {
      foreach ($pkg in @($CcusagePackage, $CodebaseMemoryPackage)) {
        if ($pkg -eq "") { continue }
        $args = @("install", "-g", $pkg)
        if ($NpmRegistry -ne "") { $args += @("--registry", $NpmRegistry) }
        & $npm.Source @args *> $null
        if ($LASTEXITCODE -eq 0) { Info "npm tool installed/updated: $pkg" }
        else { Info "Could not install npm tool '$pkg'. Check Artifactory/npm access; Alfred will degrade." }
      }
    }
  } catch {
    Info "npm tool setup skipped ($($_.Exception.Message)). Alfred works without it."
  }
}

# 7. Notification adapter (MCP e-mail) — owner decision: channel is MCP + Python.
# Registers the destination (~/.alfred-email.json, dry-run by default) and the MCP
# server in Claude Code when available. Best-effort: failures never break the install.
if (-not $SkipEmail) {
  try {
    $emailConfig = Join-Path $HOME ".alfred-email.json"
    if (Test-Path -LiteralPath $emailConfig) {
      Info "E-mail config already registered at $emailConfig (kept as is)."
    } else {
      if ($Email -eq "" -and $env:ALFRED_EMAIL) { $Email = $env:ALFRED_EMAIL }
      if ($Email -eq "" -and [Environment]::UserInteractive) {
        $Email = Read-Host "[alfred] E-mail para notificacoes/relatorios (Enter para pular)"
      }
      # Org telemetry destination: from ALFRED_TELEMETRY_TO or knowledge/notification.md
      # (aggregates every runner's observability logs — provisional until the telemetry API, D45).
      $telemetryTo = $env:ALFRED_TELEMETRY_TO
      if (-not $telemetryTo) {
        $knowledgeFile = Join-Path $InstallDir "knowledge/notification.md"
        if (Test-Path -LiteralPath $knowledgeFile) {
          $match = Select-String -LiteralPath $knowledgeFile -Pattern 'telemetry_to:\s*`?([^`\s]+)`?' | Select-Object -First 1
          if ($match) { $telemetryTo = $match.Matches[0].Groups[1].Value }
        }
      }
      if ($Email -ne "" -or $telemetryTo) {
        $allow = @()
        if ($Email -ne "") { $allow += $Email }
        if ($telemetryTo -and $allow -notcontains $telemetryTo) { $allow += $telemetryTo }
        @{
          mode        = "dry-run"
          default_to  = $Email
          telemetry_to = "$telemetryTo"
          allowlist   = $allow
          smtp        = @{ host = ""; port = 587; user = ""; password = ""; sender = "" }
        } | ConvertTo-Json -Depth 3 | Set-Content -LiteralPath $emailConfig -Encoding UTF8
        Info "E-mail registered at $emailConfig (mode: dry-run — fill smtp{} and set mode: active to really send)."
        if ($telemetryTo) { Info "Telemetry destination: $telemetryTo (observability batches; provisional e-mail transport, D45)." }
      } else {
        Info "E-mail setup skipped. Register later: create $emailConfig (see connectors/notification-email.md)."
      }
    }

    $mcpServer = Join-Path $InstallDir "scripts/adapters/mcp-email-server.py"
    $claude = Get-Command claude -ErrorAction SilentlyContinue
    $python = Get-Command python -ErrorAction SilentlyContinue
    if ($claude -and $python -and (Test-Path -LiteralPath $mcpServer)) {
      & $claude.Source mcp get alfred-email *> $null
      if ($LASTEXITCODE -eq 0) {
        Info "MCP 'alfred-email' already registered in Claude Code."
      } else {
        & $claude.Source mcp add --scope user alfred-email -- python $mcpServer *> $null
        if ($LASTEXITCODE -eq 0) { Info "MCP 'alfred-email' registered in Claude Code (user scope)." }
        else { Info "Could not register the MCP automatically. Manual: claude mcp add --scope user alfred-email -- python `"$mcpServer`"" }
      }
    } else {
      if (-not $python) { Info "Python 3 not found; the MCP e-mail server needs it. Install Python, then: claude mcp add --scope user alfred-email -- python `"$mcpServer`"" }
      elseif (-not $claude) { Info "Claude Code CLI not found; for other MCP hosts register: python `"$mcpServer`" (stdio)." }
    }
    Info "DEVIN projects: MCP servers (alfred-email + Context7) are per-repo — the /alfred skill offers to create .devin/config.local.json from hosts/devin-cli/config.local.template.json on first boot."
  } catch {
    Info "E-mail/MCP setup skipped ($($_.Exception.Message)). The framework works without it (manual handoff)."
  }
}

Info "Done. Open a repo and type /alfred in the DEVIN CLI."
