param(
  [string]$Root = "."
)

$ErrorActionPreference = "Stop"
$rootPath = Resolve-Path -LiteralPath $Root
$knowledgePath = Join-Path $rootPath "knowledge"

function Assert-Path {
  param([string]$RelativePath)

  $path = Join-Path $rootPath $RelativePath
  if (-not (Test-Path -LiteralPath $path)) {
    throw "Missing knowledge path: $RelativePath"
  }
  Write-Output "OK path $RelativePath"
}

function Assert-Section {
  param(
    [string]$Content,
    [string]$Section,
    [string]$Label
  )

  $escaped = [regex]::Escape($Section)
  if ($Content -notmatch "(?im)^##\s+$escaped\s*$") {
    throw "$Label is missing required section: $Section"
  }
  Write-Output "OK section $Label / $Section"
}

function Test-PolicyShape {
  param(
    [string]$Path,
    [switch]$RequireConcreteStatus
  )

  $content = Get-Content -LiteralPath $Path -Raw
  $label = Resolve-Path -LiteralPath $Path -Relative
  $requiredPolicySections = @(
    "identity",
    "applies to",
    "rule",
    "rationale",
    "enforcement",
    "exceptions",
    "audit evidence",
    "related artifacts"
  )

  foreach ($section in $requiredPolicySections) {
    Assert-Section -Content $content -Section $section -Label $label
  }

  if ($RequireConcreteStatus -and $content -notmatch "(?im)^\s*-\s+status:\s*(draft|active|deprecated)\s*$") {
    throw "$label must define a concrete policy status"
  }

  Write-Output "OK policy $label"
}

Assert-Path "knowledge/README.md"
Assert-Path "knowledge/notification.md"
Assert-Path "knowledge/policy-template.md"
Assert-Path "docs/knowledge-governance.md"

$readme = Get-Content -LiteralPath (Join-Path $knowledgePath "README.md") -Raw
Assert-Section -Content $readme -Section "Scopes" -Label "knowledge/README.md"
Assert-Section -Content $readme -Section "Rule" -Label "knowledge/README.md"

$notification = Get-Content -LiteralPath (Join-Path $knowledgePath "notification.md") -Raw
Assert-Section -Content $notification -Section "destination" -Label "knowledge/notification.md"
Assert-Section -Content $notification -Section "default triggers" -Label "knowledge/notification.md"
Assert-Section -Content $notification -Section "guardrails" -Label "knowledge/notification.md"

$policyTemplatePath = Join-Path $knowledgePath "policy-template.md"
$policyTemplate = Get-Content -LiteralPath $policyTemplatePath -Raw
Test-PolicyShape -Path $policyTemplatePath

if ($policyTemplate -notmatch "(?im)status:\s*.*draft.*active.*deprecated") {
  throw "knowledge/policy-template.md must define policy status values"
}

$examplePolicyFiles = Get-ChildItem -Path (Join-Path $rootPath "examples") -Recurse -Filter "*.md" -Force |
  Where-Object {
    $_.FullName -match "\\knowledge\\" -and
    $_.Name -notin @("README.md")
  }

foreach ($file in $examplePolicyFiles) {
  Test-PolicyShape -Path $file.FullName -RequireConcreteStatus
}

Write-Output "Knowledge validation completed."
