param(
  [string]$Root = "."
)

$ErrorActionPreference = "Stop"
$rootPath = Resolve-Path -LiteralPath $Root

function Assert-Path {
  param([string]$RelativePath)

  $fullPath = Join-Path $rootPath $RelativePath
  if (-not (Test-Path -LiteralPath $fullPath)) {
    throw "Missing required path: $RelativePath"
  }
  Write-Output "OK path $RelativePath"
}

function Assert-Jsonl {
  param([string]$FilePath)

  $lineNumber = 0
  Get-Content -LiteralPath $FilePath | ForEach-Object {
    $lineNumber += 1
    if ($_.Trim().Length -gt 0) {
      $_ | ConvertFrom-Json | Out-Null
    }
  }
  Write-Output "OK jsonl $FilePath"
}

$requiredPaths = @(
  "core",
  "rules/common",
  "rules/demand-types",
  "rules/lanes",
  "rules/lifecycle",
  "rules/agents",
  "skills",
  "connectors",
  "metrics",
  "templates/hub",
  "templates/app",
  "docs",
  "examples",
  "rules/common/units.md",
  "rules/common/escalation-triggers.md",
  "templates/hub/execution-plan.md",
  "templates/hub/environment-parameters.md",
  "templates/hub/validation-evidence.md",
  "docs/implementation-status.md",
  "docs/layer-1-framework-closure.md"
  "docs/onboarding-sigla.md",
  "docs/framework-validation.md"
  "docs/host-adapter-readiness.md"
  "docs/version-adoption.md"
  "docs/release-governance.md"
  "CHANGELOG.md"
  "scripts/alfred-boot.ps1"
  "scripts/render-toolbar.ps1"
  "docs/skills-activation.md"
  "skills/lang-python.md"
  "skills/lang-sql.md"
  "skills/lang-terraform.md"
  "skills/platform-aws-data.md"
  "scripts/collect-observability.ps1"
  "scripts/generate-metrics-rollup.ps1"
  "scripts/normalize-usage-cost.ps1"
  "scripts/validate-demand.ps1"
  "scripts/validate-reverse-eng-staleness.ps1"
  "scripts/validate-sdd-gate.ps1"
  "scripts/validate-toolbar-fixtures.ps1"
  "scripts/validate-skills-registry.ps1"
  "scripts/validate-connectors.ps1"
  "scripts/validate-model-policy.ps1"
  "connectors/usage-cost.md"
  "connectors/adapter-template.md"
  "docs/adapter-implementation.md"
  "examples/connectors"
  "examples/connectors/vcs-git-dry-run-adapter.md"
  "examples/connectors/usage-export.jsonl"
  "examples/connectors/usage-attribution-events.jsonl"
  "examples/toolbar-fixtures/fast.txt"
  "examples/toolbar-fixtures/safe.txt"
  "examples/toolbar-fixtures/execution-first.txt"
  "examples/toolbar-fixtures/standard-parallel-units.txt"
  "examples/generated-metrics-rollup.md"
  "examples/generated-insights.md"
  "examples/staleness-fixtures/reverse-eng-fresh.md"
)

foreach ($path in $requiredPaths) {
  Assert-Path -RelativePath $path
}

$jsonlFiles = Get-ChildItem -Path (Join-Path $rootPath "examples") -Recurse -Filter "*observability-log.jsonl" -Force
foreach ($file in $jsonlFiles) {
  Assert-Jsonl -FilePath $file.FullName
}

Assert-Jsonl -FilePath (Join-Path $rootPath "examples/connectors/usage-export.jsonl")
Assert-Jsonl -FilePath (Join-Path $rootPath "examples/connectors/usage-attribution-events.jsonl")

& (Join-Path $rootPath "scripts/validate-toolbar-fixtures.ps1") -Root $rootPath
& (Join-Path $rootPath "scripts/validate-skills-registry.ps1") -Root $rootPath
& (Join-Path $rootPath "scripts/validate-connectors.ps1") -Root $rootPath
& (Join-Path $rootPath "scripts/validate-model-policy.ps1") -Root $rootPath
& (Join-Path $rootPath "scripts/validate-demand.ps1") -HubDemandPath (Join-Path $rootPath "examples/sq9-pilot/alfred-docs-hub/iniciativa-001-piloto/005-parallel-units")
& (Join-Path $rootPath "scripts/alfred-boot.ps1") -Root $rootPath | Out-Null
& (Join-Path $rootPath "scripts/validate-reverse-eng-staleness.ps1") -ReverseEngPath (Join-Path $rootPath "examples/staleness-fixtures/reverse-eng-fresh.md") -CurrentCommit "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
& (Join-Path $rootPath "scripts/validate-sdd-gate.ps1") -HubDemandPath (Join-Path $rootPath "examples/sq9-pilot/alfred-docs-hub/iniciativa-001-piloto/005-parallel-units")

Write-Output "Framework validation completed."
