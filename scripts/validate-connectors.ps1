param(
  [string]$Root = "."
)

$ErrorActionPreference = "Stop"
$rootPath = Resolve-Path -LiteralPath $Root
$connectorsPath = Join-Path $rootPath "connectors"
$examplesPath = Join-Path $rootPath "examples/connectors"

function Test-Section {
  param(
    [string]$Content,
    [string]$Section,
    [string]$Label
  )

  $escaped = [regex]::Escape($Section)
  if ($Content -notmatch "(?im)^##\s+$escaped\s*$") {
    throw "$Label is missing required section: $Section"
  }
}

function Test-ConnectorContract {
  param([System.IO.FileInfo]$File)

  $content = Get-Content -LiteralPath $File.FullName -Raw
  $requiredSections = @(
    "type",
    "activation",
    "operations",
    "degradation",
    "audit fields"
  )

  foreach ($section in $requiredSections) {
    Test-Section -Content $content -Section $section -Label $File.Name
  }

  Write-Output "OK connector $($File.Name)"
}

function Test-AdapterShape {
  param(
    [System.IO.FileInfo]$File,
    [switch]$RequireConcreteStatus
  )

  $content = Get-Content -LiteralPath $File.FullName -Raw
  $requiredSections = @(
    "identity",
    "activation",
    "operations",
    "inputs",
    "outputs",
    "audit fields",
    "observability event",
    "degradation",
    "safety checks",
    "fixture"
  )

  foreach ($section in $requiredSections) {
    Test-Section -Content $content -Section $section -Label $File.Name
  }

  if ($RequireConcreteStatus -and $content -notmatch "(?im)^\s*-\s+status:\s*(contract|handoff|dry-run|active|disabled)\s*$") {
    throw "$($File.Name) must declare a valid adapter status"
  }

  Write-Output "OK adapter $($File.Name)"
}

if (-not (Test-Path -LiteralPath $connectorsPath)) {
  throw "Missing connectors directory: $connectorsPath"
}

$contractFiles = Get-ChildItem -LiteralPath $connectorsPath -Filter "*.md" |
  Where-Object { $_.Name -notin @("connectors.md", "adapter-template.md") }

if ($contractFiles.Count -eq 0) {
  throw "No connector contract files found."
}

foreach ($file in $contractFiles) {
  Test-ConnectorContract -File $file
}

Test-AdapterShape -File (Get-Item -LiteralPath (Join-Path $connectorsPath "adapter-template.md"))

if (Test-Path -LiteralPath $examplesPath) {
  $adapterExamples = Get-ChildItem -LiteralPath $examplesPath -Filter "*adapter*.md"
  foreach ($file in $adapterExamples) {
    Test-AdapterShape -File $file -RequireConcreteStatus
  }
}

Write-Output "Connector validation completed."
