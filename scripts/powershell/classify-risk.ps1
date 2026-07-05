param(
  [Parameter(Mandatory = $true)][ValidateSet(0, 1, 2)][int]$Reversibility,
  [Parameter(Mandatory = $true)][ValidateSet(0, 1, 2)][int]$BlastRadius,
  [Parameter(Mandatory = $true)][ValidateSet(0, 1, 2)][int]$SensitiveData,
  [Parameter(Mandatory = $true)][ValidateSet(0, 1, 2)][int]$CustomerImpact,
  [Parameter(Mandatory = $true)][ValidateSet(0, 1, 2)][int]$Cost,
  [Parameter(Mandatory = $true)][ValidateSet(0, 1, 2)][int]$Components,
  [Parameter(Mandatory = $true)][ValidateSet(0, 1, 2)][int]$Novelty,
  [Parameter(Mandatory = $true)][ValidateSet(0, 1, 2)][int]$Ambiguity,
  [Parameter(Mandatory = $true)][ValidateSet(0, 1, 2)][int]$Integrations,
  [Parameter(Mandatory = $true)][ValidateSet(0, 1, 2)][int]$Effort,
  [switch]$ArchitecturalChange,
  [switch]$MultiSquad
)

# Propose a Risk Mode lane from the objective checklist (core/risk-mode.md).
# PowerShell mirror of scripts/python/classify-risk.py. Optional helper (D3):
# the checklist in core/risk-mode.md is the source of truth and Alfred still
# classifies manually when this cannot run. The AI proposes, the human confirms
# (Standard/SAFE) - this helper only computes and explains the proposal.

$ErrorActionPreference = "Stop"

function Get-LaneFromScore {
  param([int]$Score)
  if ($Score -le 3) { return "FAST" }
  if ($Score -le 6) { return "Standard" }
  return "SAFE"
}

function Get-MaxLane {
  param([string]$A, [string]$B)
  $order = @("FAST", "Standard", "SAFE")
  if ($order.IndexOf($A) -ge $order.IndexOf($B)) { return $A }
  return $B
}

$risk = $Reversibility + $BlastRadius + $SensitiveData + $CustomerImpact + $Cost
$complexity = $Components + $Novelty + $Ambiguity + $Integrations + $Effort
$baseScore = [Math]::Max($risk, $complexity)
$lane = Get-LaneFromScore -Score $baseScore

$overrides = New-Object System.Collections.Generic.List[string]
$fired = New-Object System.Collections.Generic.List[string]
if ($SensitiveData -eq 2) { $fired.Add("sensitive/regulated data = 2") }
if ($Reversibility -eq 2) { $fired.Add("hard/irreversible = 2") }
if ($CustomerImpact -eq 2) { $fired.Add("direct customer impact = 2") }
if ($fired.Count -ge 2) {
  $overrides.Add("2+ critical risk criteria -> SAFE (" + ($fired -join "; ") + ")")
  $lane = Get-MaxLane -A $lane -B "SAFE"
} elseif ($fired.Count -eq 1) {
  $overrides.Add($fired[0] + " -> minimum Standard")
  $lane = Get-MaxLane -A $lane -B "Standard"
}
if ($ArchitecturalChange) {
  $overrides.Add("architectural change -> SAFE")
  $lane = Get-MaxLane -A $lane -B "SAFE"
}
if ($MultiSquad) {
  $overrides.Add("multi-squad -> SAFE")
  $lane = Get-MaxLane -A $lane -B "SAFE"
}

Write-Output "risk axis      : $risk/10"
Write-Output "complexity axis: $complexity/10"
Write-Output ("base score     : {0} -> {1}" -f $baseScore, (Get-LaneFromScore -Score $baseScore))
foreach ($item in $overrides) { Write-Output "hard override  : $item" }
Write-Output "PROPOSED LANE  : $lane  (AI proposes, human confirms - Standard/SAFE)"
if ($lane -eq "SAFE") {
  Write-Output "anti-SAFE brake: record the justification (which override/score fired) in 02-design/006-decisions.md or it drops to Standard."
}

Write-Output ""
Write-Output "--- paste into 01-inception/004-risk.md (pt-BR) ---"
Write-Output "## Classificacao"
Write-Output "- score de risco: $risk/10"
Write-Output "- score de complexidade: $complexity/10"
Write-Output "- modo proposto: $lane"
Write-Output "- modo confirmado: <humano confirma>"
Write-Output ""
Write-Output "## Overrides"
if ($overrides.Count -gt 0) {
  foreach ($item in $overrides) { Write-Output "- $item" }
} else {
  Write-Output "- nenhum"
}
