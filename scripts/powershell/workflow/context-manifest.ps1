param(
  [string]$Root = ".",
  [Parameter(Mandatory = $true)][string]$Phase,
  [Parameter(Mandatory = $true)][string]$Lane,
  [Parameter(Mandatory = $true)][Alias("DemandType")][string]$DemandTypeValue,
  [Parameter(Mandatory = $true)][string]$Agent,
  [string]$SubActivity = ""
)

$ErrorActionPreference = "Stop"
$rootPath = Resolve-Path -LiteralPath $Root

function Normalize-Value {
  param([string]$Value)
  return ($Value.Trim().ToLowerInvariant())
}

function Normalize-Phase {
  param([string]$Value)
  $normalized = Normalize-Value $Value
  if ($normalized -eq "validate") { return "validation" }
  if ($normalized -eq "operation") { return "operations" }
  return $normalized
}

function Normalize-Slug {
  param([string]$Value)
  return ((Normalize-Value $Value).Replace("_", "-").Replace(" ", "-"))
}

function Read-RulesIndex {
  $indexPath = Join-Path $rootPath "rules/rules-index.md"
  if (-not (Test-Path -LiteralPath $indexPath)) {
    throw "Missing rules index: $indexPath"
  }

  $rows = @()
  foreach ($line in Get-Content -LiteralPath $indexPath) {
    if (-not $line.StartsWith("| ``")) {
      continue
    }
    $cells = $line.Trim().Trim("|").Split("|") | ForEach-Object { $_.Trim() }
    if ($cells.Count -ne 8) {
      continue
    }
    if ($cells[7] -notmatch "\(([^)]+)\)") {
      continue
    }
    $rows += [pscustomobject]@{
      Name = $cells[0].Trim("``")
      Load = $cells[1].Trim("``")
      Phase = $cells[2].Trim("``")
      Lane = $cells[3].Trim("``")
      DemandType = $cells[4].Trim("``")
      Agent = $cells[5].Trim("``")
      Path = $Matches[1]
    }
  }
  return $rows
}

function Find-One {
  param(
    [object[]]$Rows,
    [string]$Load,
    [string]$Field,
    [string]$Value
  )

  $wanted = Normalize-Slug $Value
  $matches = @($Rows | Where-Object {
    $_.Load -eq $Load -and (Normalize-Slug ([string]$_.($Field))) -eq $wanted
  })
  if ($matches.Count -eq 0) {
    throw "No $Load rule found for ${Field}=$Value"
  }
  return $matches[0].Path
}

function Find-SubActivity {
  param(
    [object[]]$Rows,
    [string]$PhaseValue,
    [string]$SubActivityValue
  )

  $wanted = Normalize-Slug $SubActivityValue
  $matches = @($Rows | Where-Object {
    $_.Load -eq "sub-activity" -and
    (Normalize-Phase $_.Phase) -eq $PhaseValue -and
    (
      (Normalize-Slug ($_.Name.Replace("sub-activity-", ""))) -eq $wanted -or
      (Normalize-Slug ([System.IO.Path]::GetFileNameWithoutExtension($_.Path))) -eq $wanted
    )
  })
  if ($matches.Count -eq 0) {
    throw "No sub-activity found for phase=$PhaseValue sub_activity=$SubActivityValue"
  }
  return $matches[0].Path
}

$phaseValue = Normalize-Phase $Phase
$laneValue = Normalize-Slug $Lane
$demandType = Normalize-Slug $DemandTypeValue
$agentValue = Normalize-Slug $Agent
$rows = Read-RulesIndex

$ordered = @(
  "core/principles.md",
  "rules/README.md",
  "rules/rules-index.md",
  (Find-One -Rows $rows -Load "always" -Field "Name" -Value "common-overconfidence"),
  (Find-One -Rows $rows -Load "lifecycle" -Field "Name" -Value "lifecycle"),
  (Find-One -Rows $rows -Load "demand-type" -Field "DemandType" -Value $demandType),
  (Find-One -Rows $rows -Load "lane" -Field "Lane" -Value $laneValue),
  (Find-One -Rows $rows -Load "phase" -Field "Phase" -Value $phaseValue),
  (Find-One -Rows $rows -Load "agent" -Field "Agent" -Value $agentValue)
)

if ($SubActivity.Trim().Length -gt 0) {
  $ordered += Find-SubActivity -Rows $rows -PhaseValue $phaseValue -SubActivityValue $SubActivity
}

$seen = @{}
foreach ($item in $ordered) {
  if (-not $seen.ContainsKey($item)) {
    $seen[$item] = $true
    Write-Output $item
  }
}
