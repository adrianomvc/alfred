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
#>
param(
  [string]$FrameworkUrl = "https://github.com/adrianomvc/alfred.git",
  [string]$InstallDir = (Join-Path $HOME ".alfred"),
  [string]$Branch = "",
  [string]$SkillsDir = (Join-Path $env:APPDATA "devin/skills")
)

$ErrorActionPreference = "Stop"

function Info($m) { Write-Host "[alfred] $m" }

# 1. Preconditions
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
  throw "git is required but was not found on PATH."
}

# 2. Clone or update the framework into ~/.alfred
if (Test-Path -LiteralPath (Join-Path $InstallDir ".git")) {
  Info "Updating existing framework at $InstallDir"
  git -C $InstallDir fetch --quiet origin
  if ($Branch -ne "") { git -C $InstallDir checkout --quiet $Branch }
  git -C $InstallDir pull --quiet --ff-only
} elseif (Test-Path -LiteralPath $InstallDir) {
  throw "$InstallDir exists but is not a git repo. Move or remove it, then re-run."
} else {
  Info "Cloning framework into $InstallDir"
  # core.longpaths handles deep example paths beyond the Windows MAX_PATH limit.
  if ($Branch -ne "") {
    git -c core.longpaths=true clone --quiet --branch $Branch $FrameworkUrl $InstallDir
  } else {
    git -c core.longpaths=true clone --quiet $FrameworkUrl $InstallDir
  }
}

# 3. Install the /alfred skill for the DEVIN CLI
$skillSource = Join-Path $InstallDir "install/devin/alfred/SKILL.md"
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

Info "Done. Open a repo and type /alfred in the DEVIN CLI."
