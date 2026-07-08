param(
  [Parameter(Mandatory = $true)]
  [string]$HubDemandPath,

  [string]$AppDemandPath = "",

  # Forwarded to the reverse-eng staleness check when provided.
  [string]$AppRepoPath = "",
  [string]$AppCurrentCommit = "",

  [switch]$Strict
)

$ErrorActionPreference = "Stop"
$issues = @()

function Add-Issue {
  param(
    [string]$Severity,
    [string]$Code,
    [string]$Message
  )

  $script:issues += [pscustomobject]@{
    Severity = $Severity
    Code = $Code
    Message = $Message
  }
}

function Assert-Path {
  param(
    [string]$Root,
    [string]$RelativePath,
    [string]$Severity = "ERROR"
  )

  $fullPath = Join-Path $Root $RelativePath
  if (-not (Test-Path -LiteralPath $fullPath)) {
    Add-Issue -Severity $Severity -Code "missing_path" -Message "Missing $RelativePath"
    return $false
  }

  Write-Output "OK path $RelativePath"
  return $true
}

function Assert-Jsonl {
  param(
    [string]$FilePath,
    [string]$Label
  )

  if (-not (Test-Path -LiteralPath $FilePath)) {
    Add-Issue -Severity "ERROR" -Code "missing_jsonl" -Message "Missing $Label"
    return
  }

  $lineNumber = 0
  Get-Content -LiteralPath $FilePath | ForEach-Object {
    $lineNumber += 1
    if ($_.Trim().Length -gt 0) {
      try {
        $_ | ConvertFrom-Json | Out-Null
      } catch {
        Add-Issue -Severity "ERROR" -Code "invalid_jsonl" -Message "$Label has invalid JSON at line $lineNumber"
      }
    }
  }

  Write-Output "OK jsonl $Label"
}

function Read-JsonlEvents {
  param(
    [string]$FilePath,
    [string]$Label
  )

  $events = @()
  if (-not (Test-Path -LiteralPath $FilePath)) {
    return $events
  }

  $lineNumber = 0
  Get-Content -LiteralPath $FilePath | ForEach-Object {
    $lineNumber += 1
    if ($_.Trim().Length -gt 0) {
      try {
        $event = $_ | ConvertFrom-Json
        $event | Add-Member -NotePropertyName "_line" -NotePropertyValue $lineNumber -Force
        $events += $event
      } catch {
        Add-Issue -Severity "ERROR" -Code "invalid_jsonl" -Message "$Label has invalid JSON at line $lineNumber"
      }
    }
  }

  return $events
}

function Test-MarkdownHasOperationalContent {
  param(
    [string]$FilePath,
    [string]$Label
  )

  if (-not (Test-Path -LiteralPath $FilePath)) {
    return
  }

  $lines = Get-Content -LiteralPath $FilePath
  $useful = $lines | Where-Object {
    $line = $_.Trim()
    $line -ne "" -and
    $line -notmatch "^#" -and
    $line -notmatch "^>" -and
    $line -notmatch "^\|[-\s|]+\|$" -and
    $line -notmatch "^\|\s*(Time|Actor|Phase|Action|Model|Result|Responsible human|Date|Decision|Owner|Rationale|Impact)" -and
    $line -notmatch "^-\s*[A-Za-z /]+:\s*$"
  }

  if (($useful | Measure-Object).Count -eq 0) {
    Add-Issue -Severity "WARN" -Code "empty_operational_artifact" -Message "$Label has no operational content: $FilePath"
  } else {
    Write-Output "OK content $Label"
  }
}

function Normalize-Phase {
  param([string]$Value)

  $normalized = "$Value".ToLowerInvariant()
  if ($normalized -like "*inception*") { return "inception" }
  if ($normalized -like "*design*") { return "design" }
  if ($normalized -like "*execution*") { return "execution" }
  if ($normalized -like "*validate*" -or $normalized -like "*validation*") { return "validate" }
  if ($normalized -like "*operation*") { return "operation" }
  return $normalized
}

function Test-ObservabilityConsistency {
  param(
    [object[]]$Events,
    [string]$ExpectedDemandId,
    [string]$ExpectedInitiativeId,
    [string]$ExpectedPhase,
    [string]$ExpectedSchema,
    [string]$ExpectedFrameworkVersion
  )

  if ($Events.Count -eq 0) {
    Add-Issue -Severity "ERROR" -Code "empty_observability_log" -Message "HUB observability log has no events"
    return
  }

  $ordered = $Events | Sort-Object _line
  $last = $ordered[-1]
  $legacyMissingArtifactsUsed = 0

  foreach ($event in $Events) {
    if ($ExpectedDemandId -ne "" -and "$($event.demand_id)" -ne $ExpectedDemandId) {
      Add-Issue -Severity "ERROR" -Code "observability_demand_mismatch" -Message "Event line $($event._line) demand_id '$($event.demand_id)' differs from state id '$ExpectedDemandId'"
    }
    if ($ExpectedInitiativeId -ne "" -and "$($event.initiative_id)" -ne $ExpectedInitiativeId) {
      Add-Issue -Severity "WARN" -Code "observability_initiative_mismatch" -Message "Event line $($event._line) initiative_id '$($event.initiative_id)' differs from state initiative '$ExpectedInitiativeId'"
    }
    if ($ExpectedSchema -ne "" -and "$($event.schema_version)" -ne $ExpectedSchema) {
      Add-Issue -Severity "ERROR" -Code "observability_schema_mismatch" -Message "Event line $($event._line) schema '$($event.schema_version)' differs from state schema '$ExpectedSchema'"
    }
    if ($ExpectedFrameworkVersion -ne "" -and $null -ne $event.alfred -and "$($event.alfred.version)" -ne "" -and "$($event.alfred.version)" -ne $ExpectedFrameworkVersion) {
      Add-Issue -Severity "WARN" -Code "observability_version_mismatch" -Message "Event line $($event._line) Alfred version '$($event.alfred.version)' differs from state version '$ExpectedFrameworkVersion'"
    }
    if ($null -eq $event.artifacts_used -and $event._line -eq $last._line) {
      Add-Issue -Severity "WARN" -Code "observability_missing_artifacts_used" -Message "Event line $($event._line) does not record artifacts_used"
    } elseif ($null -eq $event.artifacts_used) {
      $legacyMissingArtifactsUsed += 1
    }
  }

  if ($legacyMissingArtifactsUsed -gt 0) {
    Write-Output "OK observability legacy events without artifacts_used $legacyMissingArtifactsUsed"
  }

  $eventPhase = "$($last.phase)"
  if ($null -ne $last.state_transition -and $null -ne $last.state_transition.to -and "$($last.state_transition.to.phase)" -ne "") {
    $eventPhase = "$($last.state_transition.to.phase)"
  }

  if ((Normalize-Phase $eventPhase) -ne (Normalize-Phase $ExpectedPhase)) {
    Add-Issue -Severity "WARN" -Code "observability_phase_mismatch" -Message "Latest event phase '$eventPhase' differs from state phase '$ExpectedPhase'"
  } else {
    Write-Output "OK observability latest phase $eventPhase"
  }

  Write-Output "OK observability events $($Events.Count)"
}

function Get-StateField {
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

function Get-PhaseNumber {
  param([string]$Phase)

  $normalized = $Phase.ToLowerInvariant()
  if ($normalized -like "*inception*") { return 1 }
  if ($normalized -like "*design*") { return 2 }
  if ($normalized -like "*execution*") { return 3 }
  if ($normalized -like "*validate*" -or $normalized -like "*validation*") { return 4 }
  if ($normalized -like "*operation*") { return 5 }
  return 0
}

function Test-StateField {
  param(
    [string]$Value,
    [string]$Name,
    [string]$Severity = "WARN"
  )

  if ($Value -eq "") {
    Add-Issue -Severity $Severity -Code "missing_state_field" -Message "Missing state field: $Name"
  } else {
    Write-Output "OK field $Name = $Value"
  }
}

$hubRoot = Resolve-Path -LiteralPath $HubDemandPath
$hub = "$hubRoot"

Assert-Path -Root $hub -RelativePath "001-state.md" | Out-Null
$statePath = Join-Path $hub "001-state.md"
if (-not (Test-Path -LiteralPath $statePath)) {
  throw "Cannot validate demand without 001-state.md"
}

$stateLines = Get-Content -LiteralPath $statePath

$demandId = Get-StateField -Lines $stateLines -Names @("id")
$initiativeId = Get-StateField -Lines $stateLines -Names @("initiative id", "id iniciativa")
$sigla = Get-StateField -Lines $stateLines -Names @("sigla")
$lane = Get-StateField -Lines $stateLines -Names @("lane", "modo")
$phase = Get-StateField -Lines $stateLines -Names @("current phase", "fase atual")
$status = Get-StateField -Lines $stateLines -Names @("status")
$frameworkVersion = Get-StateField -Lines $stateLines -Names @("framework version", "versao framework", "versão framework")
$observabilitySchema = Get-StateField -Lines $stateLines -Names @("observability schema", "schema observability")

Test-StateField -Value $demandId -Name "id" -Severity "ERROR"
Test-StateField -Value $initiativeId -Name "initiative id" -Severity "WARN"
Test-StateField -Value $sigla -Name "sigla" -Severity "WARN"
Test-StateField -Value $lane -Name "lane/modo" -Severity "ERROR"
Test-StateField -Value $phase -Name "current phase/fase atual" -Severity "ERROR"
Test-StateField -Value $status -Name "status" -Severity "WARN"
Test-StateField -Value $frameworkVersion -Name "framework version" -Severity "WARN"

$phaseNumber = Get-PhaseNumber -Phase $phase
if ($phaseNumber -eq 0) {
  Add-Issue -Severity "WARN" -Code "unknown_phase" -Message "Current phase is not one of the canonical phases: $phase"
}

$requiredFolders = @(
  "01-inception",
  "02-design",
  "03-execution",
  "04-validate",
  "05-operation"
)
foreach ($folder in $requiredFolders) {
  Assert-Path -Root $hub -RelativePath $folder | Out-Null
}

$alwaysRequired = @(
  "01-inception/002-problem.md",
  "01-inception/004-risk.md",
  "05-operation/007-audit.md",
  "05-operation/008-metrics.md",
  "05-operation/011-observability-log.jsonl"
)
foreach ($path in $alwaysRequired) {
  Assert-Path -Root $hub -RelativePath $path | Out-Null
}

if ($lane.ToLowerInvariant() -in @("standard", "safe")) {
  Assert-Path -Root $hub -RelativePath "01-inception/003-requirements.md" -Severity "WARN" | Out-Null
  Assert-Path -Root $hub -RelativePath "02-design/006-decisions.md" -Severity "WARN" | Out-Null
}

if ($phaseNumber -ge 2) {
  Assert-Path -Root $hub -RelativePath "01-inception/005-tech-inception.md" -Severity "WARN" | Out-Null
}
if ($phaseNumber -ge 3) {
  Assert-Path -Root $hub -RelativePath "03-execution/012-execution-plan.md" -Severity "WARN" | Out-Null
}
if ($phaseNumber -ge 4) {
  Assert-Path -Root $hub -RelativePath "04-validate/013-validation-evidence.md" -Severity "WARN" | Out-Null
}

if ($phaseNumber -ge 3) {
  $sddGateScript = Join-Path $PSScriptRoot "validate-sdd-gate.ps1"
  if (Test-Path -LiteralPath $sddGateScript) {
    $sddArgs = @{
      HubDemandPath = $hub
    }
    if ($AppDemandPath -ne "") {
      $sddArgs.AppDemandPath = $AppDemandPath
    }
    $sddOutput = & $sddGateScript @sddArgs
    foreach ($line in $sddOutput) {
      Write-Output $line
      if ($line -like "ERROR *") {
        Add-Issue -Severity "ERROR" -Code "sdd_gate" -Message $line
      } elseif ($line -like "WARN *") {
        Add-Issue -Severity "WARN" -Code "sdd_gate" -Message $line
      }
    }
  }
}

$closedStatuses = @("closed", "concluida", "concluída", "done", "finalizada", "completed")
if ($closedStatuses -contains $status.ToLowerInvariant()) {
  Assert-Path -Root $hub -RelativePath "05-operation/009-summary.md" -Severity "WARN" | Out-Null
  $checklist = ($stateLines | Where-Object { $_ -match "^\s*-\s+\[[xX ]\]" })
  $openItems = ($checklist | Where-Object { $_ -match "^\s*-\s+\[\s\]" }).Count
  if ($openItems -gt 0) {
    Add-Issue -Severity "WARN" -Code "open_checklist_on_closed" -Message "Demand is closed but checklist has $openItems open item(s)"
  }
}

$stateText = $stateLines -join [Environment]::NewLine
if ($stateText -notmatch "(?im)^##\s+Active Skills\s*$" -and $stateText -notmatch "(?im)^##\s+Skills ativos\s*$") {
  Add-Issue -Severity "WARN" -Code "missing_active_skills" -Message "State does not declare active skills"
}
if ($stateText -notmatch "(?im)^##\s+Host Adapters\s*$" -and $stateText -notmatch "(?im)^##\s+Adapters de host\s*$") {
  Add-Issue -Severity "WARN" -Code "missing_host_adapters" -Message "State does not declare host adapter readiness"
}
if ($observabilitySchema -eq "") {
  Add-Issue -Severity "WARN" -Code "missing_observability_schema" -Message "State does not declare observability schema"
}

Assert-Jsonl -FilePath (Join-Path $hub "05-operation/011-observability-log.jsonl") -Label "HUB observability log"
Test-MarkdownHasOperationalContent -FilePath (Join-Path $hub "05-operation/007-audit.md") -Label "HUB audit"
Test-MarkdownHasOperationalContent -FilePath (Join-Path $hub "05-operation/008-metrics.md") -Label "HUB metrics"
$hubEvents = Read-JsonlEvents -FilePath (Join-Path $hub "05-operation/011-observability-log.jsonl") -Label "HUB observability log"
Test-ObservabilityConsistency -Events $hubEvents -ExpectedDemandId $demandId -ExpectedInitiativeId $initiativeId -ExpectedPhase $phase -ExpectedSchema $observabilitySchema -ExpectedFrameworkVersion $frameworkVersion

if ($AppDemandPath -ne "") {
  $appRoot = Resolve-Path -LiteralPath $AppDemandPath
  $app = "$appRoot"
  Assert-Path -Root $app -RelativePath "001-index.md" | Out-Null
  $hasReverseEng = Assert-Path -Root $app -RelativePath "01-inception/002-reverse-eng.md" -Severity "WARN"
  Assert-Path -Root $app -RelativePath "05-operation/005-audit.md" -Severity "WARN" | Out-Null
  Assert-Path -Root $app -RelativePath "05-operation/006-metrics.md" -Severity "WARN" | Out-Null
  Assert-Jsonl -FilePath (Join-Path $app "05-operation/008-observability-log.jsonl") -Label "App observability log"

  if ($hasReverseEng) {
    $stalenessScript = Join-Path $PSScriptRoot "validate-reverse-eng-staleness.ps1"
    if (Test-Path -LiteralPath $stalenessScript) {
      $stalenessExtra = @{}
      if ($AppCurrentCommit -ne "") { $stalenessExtra["CurrentCommit"] = $AppCurrentCommit }
      elseif ($AppRepoPath -ne "") { $stalenessExtra["AppRepoPath"] = $AppRepoPath }
      $stalenessOutput = & $stalenessScript -ReverseEngPath (Join-Path $app "01-inception/002-reverse-eng.md") @stalenessExtra
      foreach ($line in $stalenessOutput) {
        Write-Output $line
        if ($line -like "WARN *") {
          Add-Issue -Severity "WARN" -Code "reverse_eng_staleness" -Message $line
        }
      }
    }
  }
}

$warnings = ($issues | Where-Object { $_.Severity -eq "WARN" })
$errors = ($issues | Where-Object { $_.Severity -eq "ERROR" })

foreach ($issue in $issues) {
  Write-Output "$($issue.Severity) $($issue.Code): $($issue.Message)"
}

if ($errors.Count -gt 0 -or ($Strict -and $warnings.Count -gt 0)) {
  throw "Demand validation failed. errors=$($errors.Count), warnings=$($warnings.Count), strict=$Strict"
}

Write-Output "Demand validation completed. errors=$($errors.Count), warnings=$($warnings.Count), strict=$Strict"
