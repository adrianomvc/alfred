param(
  [Parameter(Mandatory = $true)][string]$HubDemandPath,
  [string]$AppDemandPath = ""
)

# Pre-Execution confidence score for a demand (W8.1).
# PowerShell mirror of scripts/python/workflow/confidence-score.py. Optional helper (D3).
# Below the floor, the recommendation is the escalation rule (stop and ask),
# never "proceed anyway". The score informs; the human decides.

$ErrorActionPreference = "Stop"
$score = 100
$reasons = New-Object System.Collections.Generic.List[string]

function Read-IfExists {
  param([string]$Path)
  if (Test-Path -LiteralPath $Path) { return (Get-Content -LiteralPath $Path -Raw -Encoding UTF8) }
  return ""
}

$requirements = Read-IfExists (Join-Path $HubDemandPath "01-inception/003-requirements.md")
if ($requirements -ne "") {
  $unanswered = 0
  foreach ($line in $requirements -split "`n") {
    if ($line -match "^\s*\[(Resposta|Answer)\]:\s*(.*)$" -and $Matches[2].Trim() -eq "") { $unanswered += 1 }
  }
  if ($unanswered -gt 0) {
    $penalty = [Math]::Min($unanswered * 15, 45)
    $score -= $penalty
    $reasons.Add("-${penalty}: $unanswered unanswered question(s) in requirements")
  }
} else {
  $score -= 15
  $reasons.Add("-15: no requirements artifact (acceptable only in FAST)")
}

$risk = Read-IfExists (Join-Path $HubDemandPath "01-inception/004-risk.md")
$lane = ""
if ($risk -match "(?im)^-\s*(modo confirmado|confirmed lane)\s*:\s*(.+)$" -and $Matches[2].Trim().Trim([char]96) -ne "") {
  $lane = $Matches[2].Trim().Trim([char]96).ToLowerInvariant()
} else {
  $score -= 20
  $reasons.Add("-20: lane not confirmed by a human in 004-risk.md")
  if ($risk -match "(?im)^-\s*(modo proposto|proposed lane)\s*:\s*(.+)$") {
    $lane = $Matches[2].Trim().Trim([char]96).ToLowerInvariant()
  }
}

if ($lane -in @("standard", "safe")) {
  $needed = @(
    @{ Rel = "02-design/006-decisions.md"; Label = "decisions" },
    @{ Rel = "03-execution/012-execution-plan.md"; Label = "execution plan" }
  )
  foreach ($item in $needed) {
    if (-not (Test-Path -LiteralPath (Join-Path $HubDemandPath $item.Rel))) {
      $score -= 15
      $reasons.Add("-15: missing $($item.Label) for lane $lane")
    }
  }
}

if ($AppDemandPath -ne "") {
  $reverse = Read-IfExists (Join-Path $AppDemandPath "01-inception/002-reverse-eng.md")
  if ($reverse -notmatch "(?im)^-\s*commit\s*:\s*``?\w{7,40}``?") {
    $score -= 15
    $reasons.Add("-15: reverse-eng without a recorded app commit (staleness unknown)")
  }
}

if ($score -lt 0) { $score = 0 }
if ($score -ge 80) {
  $verdict = "PROCEED (clarity floor met; DoD still applies)"
} elseif ($score -ge 50) {
  $verdict = "REVIEW WITH HUMAN before Execution (clarity gaps above)"
} else {
  $verdict = "STOP AND ESCALATE (escalation rule; do not enter Execution)"
}

$laneLabel = if ($lane -ne "") { $lane } else { "unknown" }
Write-Output "confidence score: $score/100 (lane: $laneLabel)"
foreach ($reason in $reasons) { Write-Output "  $reason" }
Write-Output "verdict: $verdict"
Write-Output "note: the score informs; the human decides (human-in-control)."
if ($score -ge 80) { exit 0 } else { exit 1 }
