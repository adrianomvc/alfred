param(
  [string]$Root = "examples",
  [string]$OutputPath = ""
)

$ErrorActionPreference = "Stop"
$rootPath = Resolve-Path -LiteralPath $Root
$rootPrefix = "$rootPath\"
$events = @()

$files = Get-ChildItem -Path $rootPath -Recurse -Filter "*observability-log.jsonl" -Force
foreach ($file in $files) {
  $lineNumber = 0
  Get-Content -LiteralPath $file.FullName | ForEach-Object {
    $lineNumber += 1
    if ($_.Trim().Length -gt 0) {
      $event = $_ | ConvertFrom-Json
      $event | Add-Member -NotePropertyName "_source_file" -NotePropertyValue $file.FullName -Force
      $event | Add-Member -NotePropertyName "_source_line" -NotePropertyValue $lineNumber -Force
      $events += $event
    }
  }
}

function Value-OrUnknown {
  param($Value)
  if ($null -eq $Value -or "$Value" -eq "") {
    return "unknown"
  }
  return "$Value"
}

$byDemand = $events | Group-Object demand_id
$byLane = $events | Group-Object lane
$byPhase = $events | Group-Object phase

$totalTokensInput = ($events | Where-Object { $null -ne $_.tokens_input } | Measure-Object -Property tokens_input -Sum).Sum
$totalTokensOutput = ($events | Where-Object { $null -ne $_.tokens_output } | Measure-Object -Property tokens_output -Sum).Sum
$totalCost = ($events | Where-Object { $null -ne $_.cost_usd } | Measure-Object -Property cost_usd -Sum).Sum

if ($null -eq $totalTokensInput) { $totalTokensInput = 0 }
if ($null -eq $totalTokensOutput) { $totalTokensOutput = 0 }
if ($null -eq $totalCost) { $totalCost = 0 }

$lines = @()
$lines += "# Generated Metrics Rollup"
$lines += ""
$lines += "Generated from observability JSONL under ``$Root`` = ``$rootPath``."
$lines += ""
$lines += "## Summary"
$lines += "- events: $($events.Count)"
$lines += "- demands: $($byDemand.Count)"
$lines += "- tokens input: $totalTokensInput"
$lines += "- tokens output: $totalTokensOutput"
$lines += "- cost usd: $totalCost"
$lines += ""
$lines += "## By Demand"
$lines += "| Demand | Initiative | Lane | Events | Last phase | Last status | Source |"
$lines += "|---|---|---|---:|---|---|---|"

foreach ($group in ($byDemand | Sort-Object Name)) {
  $ordered = $group.Group | Sort-Object ts, _source_file, _source_line
  $last = $ordered[-1]
  $first = $ordered[0]
  $source = "$($last._source_file)".Replace($rootPrefix, "")
  $lines += "| $(Value-OrUnknown $group.Name) | $(Value-OrUnknown $first.initiative_id) | $(Value-OrUnknown $last.lane) | $($group.Count) | $(Value-OrUnknown $last.phase) | $(Value-OrUnknown $last.status) | ``$source`` |"
}

$lines += ""
$lines += "## By Lane"
$lines += "| Lane | Events |"
$lines += "|---|---:|"
foreach ($group in ($byLane | Sort-Object Name)) {
  $lines += "| $(Value-OrUnknown $group.Name) | $($group.Count) |"
}

$lines += ""
$lines += "## By Phase"
$lines += "| Phase | Events |"
$lines += "|---|---:|"
foreach ($group in ($byPhase | Sort-Object Name)) {
  $lines += "| $(Value-OrUnknown $group.Name) | $($group.Count) |"
}

$lines += ""
$lines += "## Gaps"
if ($totalTokensInput -eq 0 -and $totalTokensOutput -eq 0) {
  $lines += "- tokens are not automatically collected in these events"
}
if ($totalCost -eq 0) {
  $lines += "- cost is not automatically collected in these events"
}
$missingModel = ($events | Where-Object { $null -eq $_.model -or $_.model -eq "" }).Count
if ($missingModel -gt 0) {
  $lines += "- events without model: $missingModel"
}

$rendered = $lines -join [Environment]::NewLine

if ($OutputPath -ne "") {
  Set-Content -LiteralPath $OutputPath -Value $rendered
  Write-Output "Wrote metrics rollup to $OutputPath"
} else {
  Write-Output $rendered
}
