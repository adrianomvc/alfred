param(
  [Parameter(Mandatory = $true)]
  [string]$StatePath,

  [string]$Model = "default",
  [string]$Cost = "n/a"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path -LiteralPath $StatePath)) {
  throw "State file not found: $StatePath"
}

$content = Get-Content -LiteralPath $StatePath

function Get-Field {
  param(
    [string[]]$Lines,
    [string]$Name
  )

  $escaped = [regex]::Escape($Name)
  foreach ($line in $Lines) {
    if ($line -match "^\s*-\s+$escaped\s*:\s*(.+?)\s*$") {
      return $Matches[1].Trim().Trim([char]96)
    }
  }
  return ""
}

function Get-FirstField {
  param(
    [string[]]$Lines,
    [string[]]$Names
  )

  foreach ($name in $Names) {
    $value = Get-Field -Lines $Lines -Name $name
    if ($value -ne "") {
      return $value
    }
  }
  return ""
}

function Get-ChecklistStatus {
  param(
    [string[]]$Lines,
    [string]$Phase
  )

  foreach ($line in $Lines) {
    if ($line -match "^\s*-\s+\[(x|X| )\]\s+$Phase\b") {
      return $Matches[1]
    }
  }
  return " "
}

function Shorten {
  param(
    [string]$Value,
    [int]$Max = 64
  )

  if ($null -eq $Value) {
    return ""
  }
  if ($Value.Length -le $Max) {
    return $Value
  }
  return $Value.Substring(0, $Max - 3) + "..."
}

$id = Get-Field -Lines $content -Name "id"
$sigla = Get-Field -Lines $content -Name "sigla"
$lane = Get-FirstField -Lines $content -Names @("lane", "modo")
$phase = Get-FirstField -Lines $content -Names @("current phase", "fase atual")
$step = Get-FirstField -Lines $content -Names @("current step", "etapa atual")
$next = Get-FirstField -Lines $content -Names @("next step", "proximo passo", "próximo passo")
$checkpoint = Get-Field -Lines $content -Name "checkpoint"

if ($id -eq "") { $id = "unknown" }
if ($sigla -eq "") { $sigla = "unknown" }
if ($lane -eq "") { $lane = "unknown" }
if ($phase -eq "") { $phase = "unknown" }
if ($step -eq "") { $step = "unknown" }
if ($next -eq "") { $next = "unknown" }
if ($checkpoint -eq "") { $checkpoint = "n/a" }

$timeMode = Get-FirstField -Lines $content -Names @("tempo", "time mode")
$checklistText = ($content | Where-Object { $_ -match "^\s*-\s+\[[xX ]\]" }) -join "`n"
$isExecutionFirst = ($phase.ToLowerInvariant() -like "*execution-first*") -or ($timeMode.ToLowerInvariant() -like "*execution-first*") -or ($checklistText.ToLowerInvariant() -like "*execution-first stabilization*")

if ($isExecutionFirst) {
  $phases = @("Execution-first stabilization", "Inception posterior", "Design posterior", "Validate posterior", "Operation / post-mortem")
} else {
  $phases = @("Inception", "Design", "Execution", "Validate", "Operation")
}
$completed = 0
$phaseParts = @()

foreach ($item in $phases) {
  $status = Get-ChecklistStatus -Lines $content -Phase $item
  if ($status -match "x|X") {
    $completed += 1
    $marker = "x"
  } elseif ($item.ToLowerInvariant() -eq $phase.ToLowerInvariant()) {
    $marker = ">"
  } else {
    $marker = " "
  }
  $phaseParts += "$item [$marker]"
}

$progress = [Math]::Min(100, [Math]::Round(($completed / 5) * 100))
$track = $phaseParts -join " -> "

if ($lane.ToLowerInvariant() -eq "fast") {
  Write-Output "ALFRED | SIGLA:$sigla | #$id | FAST | $phase | model: $Model | cost: $Cost | next: $(Shorten $next 48)"
  exit 0
}

$line = "+-- ALFRED ------------------------------- SIGLA:$sigla | #$id --+"
$footer = "+" + ("-" * ([Math]::Max(64, $line.Length - 2))) + "+"

Write-Output $line
Write-Output "| Lane: $($lane.ToUpperInvariant()) | Model: $Model | Progress: $progress% |"
Write-Output "| Cost: $Cost |"
Write-Output "| $track |"
Write-Output "| Step : $(Shorten $step 72) |"
Write-Output "| HITL : $(Shorten $checkpoint 72) |"
Write-Output "| Next : $(Shorten $next 72) |"
Write-Output $footer
