param(
  [Parameter(Mandatory = $true)]
  [string]$HubDemandPath,

  [string]$AppDemandPath = "",

  [switch]$Strict
)

$ErrorActionPreference = "Stop"
$issues = @()

function Add-Issue {
  param([string]$Severity, [string]$Code, [string]$Message)
  $script:issues += [pscustomobject]@{
    Severity = $Severity
    Code = $Code
    Message = $Message
  }
}

function Test-File {
  param([string]$Path, [string]$Code, [string]$Severity = "ERROR")
  if (-not (Test-Path -LiteralPath $Path)) {
    Add-Issue -Severity $Severity -Code $Code -Message "Missing $Path"
    return $false
  }
  Write-Output "OK file $Path"
  return $true
}

function Test-HasUsefulContent {
  param([string]$Path, [string]$Label, [string]$Severity = "ERROR")

  if (-not (Test-Path -LiteralPath $Path)) {
    Add-Issue -Severity $Severity -Code "missing_$Label" -Message "Missing $Label at $Path"
    return
  }

  $content = Get-Content -LiteralPath $Path
  $useful = $content | Where-Object {
    $line = $_.Trim()
    $line -ne "" -and
    $line -notmatch "^#" -and
    $line -notmatch "^>" -and
    $line -notmatch "^\|[-\s|]+\|$" -and
    $line -notmatch "^-\s*[A-Za-z /]+:\s*$" -and
    $line -notmatch "^\[Resposta\]:\s*$"
  }

  if (($useful | Measure-Object).Count -eq 0) {
    Add-Issue -Severity $Severity -Code "empty_$Label" -Message "$Label has no useful content: $Path"
  } else {
    Write-Output "OK content $Label"
  }
}

function Test-Section {
  param([string]$Path, [string]$Section, [string]$Severity = "WARN")

  if (-not (Test-Path -LiteralPath $Path)) {
    Add-Issue -Severity $Severity -Code "missing_section_file" -Message "Cannot check section $Section because file is missing: $Path"
    return
  }

  $content = Get-Content -LiteralPath $Path -Raw
  $escaped = [regex]::Escape($Section)
  if ($content -notmatch "(?im)^##\s+$escaped\s*$") {
    Add-Issue -Severity $Severity -Code "missing_section" -Message "Missing section '$Section' in $Path"
  } else {
    Write-Output "OK section $Section"
  }
}

$hub = "$((Resolve-Path -LiteralPath $HubDemandPath))"

$problem = Join-Path $hub "01-inception/002-problem.md"
$requirements = Join-Path $hub "01-inception/003-requirements.md"
$risk = Join-Path $hub "01-inception/004-risk.md"
$techInception = Join-Path $hub "01-inception/005-tech-inception.md"
$decisions = Join-Path $hub "02-design/006-decisions.md"
$executionPlan = Join-Path $hub "03-execution/012-execution-plan.md"

Test-HasUsefulContent -Path $problem -Label "problem"
Test-HasUsefulContent -Path $requirements -Label "requirements"
Test-HasUsefulContent -Path $risk -Label "risk" -Severity "WARN"
Test-HasUsefulContent -Path $techInception -Label "tech_inception" -Severity "WARN"
Test-HasUsefulContent -Path $decisions -Label "decisions" -Severity "WARN"
Test-HasUsefulContent -Path $executionPlan -Label "execution_plan"

if (Test-Path -LiteralPath $executionPlan) {
  Test-Section -Path $executionPlan -Section "Plano" -Severity "ERROR"
  Test-Section -Path $executionPlan -Section "Sequencia" -Severity "WARN"
  Test-Section -Path $executionPlan -Section "Evidencias esperadas" -Severity "WARN"
}

if ($AppDemandPath -ne "") {
  $app = "$((Resolve-Path -LiteralPath $AppDemandPath))"
  $spec = Join-Path $app "02-design/003-spec.md"
  if (Test-File -Path $spec -Code "missing_app_spec" -Severity "WARN") {
    Test-HasUsefulContent -Path $spec -Label "app_spec" -Severity "WARN"
    Test-Section -Path $spec -Section "Technical solution" -Severity "WARN"
    Test-Section -Path $spec -Section "Acceptance criteria" -Severity "WARN"
    Test-Section -Path $spec -Section "Test plan" -Severity "WARN"
  }
}

$warnings = ($issues | Where-Object { $_.Severity -eq "WARN" })
$errors = ($issues | Where-Object { $_.Severity -eq "ERROR" })

foreach ($issue in $issues) {
  Write-Output "$($issue.Severity) $($issue.Code): $($issue.Message)"
}

if ($errors.Count -gt 0 -or ($Strict -and $warnings.Count -gt 0)) {
  throw "SDD gate failed. errors=$($errors.Count), warnings=$($warnings.Count), strict=$Strict"
}

Write-Output "SDD gate completed. errors=$($errors.Count), warnings=$($warnings.Count), strict=$Strict"
