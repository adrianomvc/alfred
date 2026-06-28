param(
  [Parameter(Mandatory = $true)]
  [string]$ReverseEngPath,

  [string]$AppRepoPath = "",

  [string]$CurrentCommit = "",

  [switch]$Strict
)

$ErrorActionPreference = "Stop"

function Get-RecordedCommit {
  param([string[]]$Lines)

  foreach ($line in $Lines) {
    if ($line -match "^\s*-\s+commit\s*:\s*(not-git|unknown|a confirmar)\s*$") {
      return $Matches[1]
    }
    if ($line -match "^\s*-\s+app commit\s*:\s*(not-git|unknown|a confirmar)\s*$") {
      return $Matches[1]
    }
    if ($line -match "^\s*-\s+commit\s*:\s*`?([A-Fa-f0-9]{7,40})`?\s*$") {
      return $Matches[1]
    }
    if ($line -match "^\s*-\s+app commit\s*:\s*`?([A-Fa-f0-9]{7,40})`?\s*$") {
      return $Matches[1]
    }
  }

  foreach ($line in $Lines) {
    if ($line -match "\b([A-Fa-f0-9]{40})\b") {
      return $Matches[1]
    }
  }

  return ""
}

if (-not (Test-Path -LiteralPath $ReverseEngPath)) {
  throw "Reverse-eng artifact not found: $ReverseEngPath"
}

$lines = Get-Content -LiteralPath $ReverseEngPath
$recordedCommit = Get-RecordedCommit -Lines $lines

if ($recordedCommit -eq "") {
  $message = "Reverse-eng artifact does not record an app commit."
  if ($Strict) { throw $message }
  Write-Output "WARN missing_commit: $message"
  exit 0
}

if ($recordedCommit -in @("not-git", "unknown", "a confirmar")) {
  Write-Output "OK reverse-eng staleness explicitly unavailable: recorded=$recordedCommit"
  exit 0
}

if ($CurrentCommit -eq "") {
  if ($AppRepoPath -eq "") {
    Write-Output "OK recorded commit $recordedCommit"
    Write-Output "WARN current_commit_unknown: provide -AppRepoPath or -CurrentCommit to check staleness"
    exit 0
  }

  if (-not (Test-Path -LiteralPath (Join-Path $AppRepoPath ".git"))) {
    $message = "AppRepoPath is not a git repository: $AppRepoPath"
    if ($Strict) { throw $message }
    Write-Output "OK recorded commit $recordedCommit"
    Write-Output "WARN app_repo_not_git: $message"
    exit 0
  }

  $CurrentCommit = (git -C $AppRepoPath rev-parse HEAD).Trim()
}

if ($CurrentCommit -eq "") {
  throw "Could not determine current app commit."
}

$recordedPrefix = $recordedCommit.ToLowerInvariant()
$currentPrefix = $CurrentCommit.ToLowerInvariant()
if ($currentPrefix.StartsWith($recordedPrefix) -or $recordedPrefix.StartsWith($currentPrefix)) {
  Write-Output "OK reverse-eng fresh: recorded=$recordedCommit current=$CurrentCommit"
  exit 0
}

$message = "Reverse-eng stale: recorded=$recordedCommit current=$CurrentCommit"
if ($Strict) {
  throw $message
}

Write-Output "WARN reverse_eng_stale: $message"
