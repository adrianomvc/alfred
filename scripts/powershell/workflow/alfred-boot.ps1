param(
  [string]$Root = ".",
  [string]$Model = "default",
  [string]$Cost = "n/a"
)

$ErrorActionPreference = "Stop"
$rootPath = Resolve-Path -LiteralPath $Root
$frameworkRoot = Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $PSScriptRoot))
$renderer = Join-Path $PSScriptRoot "render-toolbar.ps1"

function Get-Field {
  param(
    [string[]]$Lines,
    [string[]]$Names
  )

  foreach ($name in $Names) {
    $escaped = [regex]::Escape($name)
    foreach ($line in $Lines) {
      if ($line -match "^\s*-\s+$escaped\s*:\s*(.*?)\s*$") {
        return $Matches[1].Trim().Trim([char]96)
      }
    }
  }
  return ""
}

function Value-OrUnknown {
  param([string]$Value)
  if ($null -eq $Value -or $Value -eq "") {
    return "unknown"
  }
  return $Value
}

function Get-RepoKind {
  param([string]$Path)

  $hasFramework = (Test-Path -LiteralPath (Join-Path $Path "core/principles.md")) -and (Test-Path -LiteralPath (Join-Path $Path "rules/agents"))
  $hasHub = Test-Path -LiteralPath (Join-Path $Path "alfred-docs-hub")
  $hasApp = Test-Path -LiteralPath (Join-Path $Path ".alfred-docs-app")

  if ($hasFramework) { return "Framework" }
  if ($hasHub -and $hasApp) { return "HUB+APP" }
  if ($hasHub) { return "HUB" }
  if ($hasApp) { return "APP-only" }
  return "Unknown"
}

function Get-StateSummary {
  param([System.IO.FileInfo]$StateFile)

  $lines = Get-Content -LiteralPath $StateFile.FullName
  [pscustomobject]@{
    Path = $StateFile.FullName
    DemandId = Value-OrUnknown (Get-Field -Lines $lines -Names @("id"))
    InitiativeId = Value-OrUnknown (Get-Field -Lines $lines -Names @("initiative id", "id iniciativa"))
    Sigla = Value-OrUnknown (Get-Field -Lines $lines -Names @("sigla"))
    Lane = Value-OrUnknown (Get-Field -Lines $lines -Names @("lane", "modo"))
    Phase = Value-OrUnknown (Get-Field -Lines $lines -Names @("current phase", "fase atual"))
    Step = Value-OrUnknown (Get-Field -Lines $lines -Names @("current step", "etapa atual"))
    Next = Value-OrUnknown (Get-Field -Lines $lines -Names @("next step", "proximo passo", "próximo passo"))
    Status = Value-OrUnknown (Get-Field -Lines $lines -Names @("status"))
    LastActivity = Value-OrUnknown (Get-Field -Lines $lines -Names @("last activity", "ultima atividade", "última atividade"))
  }
}

function Is-OpenStatus {
  param([string]$Status)

  $normalized = $Status.ToLowerInvariant()
  if ($normalized -in @("closed", "fechado", "fechada", "concluida", "concluída", "done", "completed", "finalizada", "finalizado", "cancelada", "cancelado", "cancelled")) {
    return $false
  }
  return $true
}

function Get-ResumePriority {
  # Lower = suggest first: pending human checkpoint > in progress > blocked.
  param([string]$Status)
  $normalized = $Status.ToLowerInvariant()
  if ($normalized -match "checkpoint" -or $normalized -match "aguardando") { return 0 }
  if ($normalized -match "bloquead" -or $normalized -match "blocked") { return 2 }
  return 1
}

function Get-PriorityReason {
  param([string]$Status)
  switch (Get-ResumePriority -Status $Status) {
    0 { return "awaiting a human checkpoint" }
    2 { return "blocked - needs external input" }
    default { return "in progress" }
  }
}

$kind = Get-RepoKind -Path $rootPath
$version = "unknown"
$versionPath = Join-Path $frameworkRoot "VERSION"
if (Test-Path -LiteralPath $versionPath) {
  $version = (Get-Content -LiteralPath $versionPath -TotalCount 1).Trim()
}

Write-Output "ALFRED BOOT"
Write-Output "- root: $rootPath"
Write-Output "- detected: $kind"
Write-Output "- framework version: $version"

$searchRoots = @()
$hubPath = Join-Path $rootPath "alfred-docs-hub"
$appPath = Join-Path $rootPath ".alfred-docs-app"
if (Test-Path -LiteralPath $hubPath) { $searchRoots += $hubPath }
if (Test-Path -LiteralPath $appPath) { $searchRoots += $appPath }
if ($kind -eq "Framework") {
  $examplesPath = Join-Path $rootPath "examples"
  if (Test-Path -LiteralPath $examplesPath) { $searchRoots += $examplesPath }
}

if ($searchRoots.Count -eq 0) {
  Write-Output "- open demands: not detected"
  Write-Output "- next: ask the human for HUB/App path or start a new demand"
  exit 0
}

$states = @()
foreach ($searchRoot in $searchRoots) {
  $states += Get-ChildItem -Path $searchRoot -Recurse -Filter "001-state.md" -Force | ForEach-Object {
    Get-StateSummary -StateFile $_
  }
}

if ($states.Count -eq 0) {
  Write-Output "- open demands: none found"
  Write-Output "- next: start a new demand using docs/quickstart-real-demand.md"
  exit 0
}

$openStates = @($states | Where-Object { Is-OpenStatus -Status $_.Status } | Sort-Object @{Expression = { Get-ResumePriority -Status $_.Status }}, LastActivity, Sigla, InitiativeId, DemandId)

Write-Output "- states found: $($states.Count)"
Write-Output "- open demands: $($openStates.Count)"

foreach ($state in $openStates) {
  $relativePath = "$($state.Path)".Replace("$rootPath\", "")
  Write-Output "  - $($state.Sigla) | $($state.InitiativeId) | $($state.DemandId) | $($state.Lane) | $($state.Phase) | $($state.Status) | next: $($state.Next)"
  Write-Output "    state: $relativePath"
}

if ($openStates.Count -gt 0) {
  $first = $openStates[0]
  Write-Output ""
  Write-Output "Suggested next: $($first.DemandId) ($(Get-PriorityReason -Status $first.Status)) - the human chooses; this is only an ordering hint."
  Write-Output "Resume preview:"
  if (Test-Path -LiteralPath $renderer) {
    & $renderer -StatePath $first.Path -Model $Model -Cost $Cost
  } else {
    Write-Output "ALFRED | SIGLA:$($first.Sigla) | #$($first.DemandId) | $($first.Lane) | $($first.Phase) | next: $($first.Next)"
  }
  Write-Output ""
  Write-Output "Next: choose a demand to resume, start a new demand, or run validate-demand on the selected state folder."
}
