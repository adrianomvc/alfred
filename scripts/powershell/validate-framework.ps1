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
  "core/presentation/README.md",
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
  "rules/common/workflow-changes.md",
  "rules/lifecycle/design/sub-activities/README.md",
  "rules/lifecycle/design/sub-activities/application-design.md",
  "rules/lifecycle/design/sub-activities/functional-design.md",
  "rules/lifecycle/design/sub-activities/nfr-design.md",
  "rules/lifecycle/design/sub-activities/infrastructure-design.md",
  "rules/lifecycle/design/sub-activities/user-stories.md",
  "rules/lifecycle/inception/sub-activities/README.md",
  "rules/lifecycle/inception/sub-activities/business-inception.md",
  "rules/lifecycle/inception/sub-activities/technical-inception.md",
  "rules/lifecycle/inception/sub-activities/requirements-elicitation.md",
  "rules/lifecycle/inception/sub-activities/risk-mode-proposal.md",
  "rules/lifecycle/execution/sub-activities/README.md",
  "rules/lifecycle/execution/sub-activities/workflow-planning.md",
  "rules/lifecycle/execution/sub-activities/unit-loop.md",
  "rules/lifecycle/execution/sub-activities/code-generation.md",
  "rules/lifecycle/execution/sub-activities/technical-review.md",
  "rules/lifecycle/validation/sub-activities/README.md",
  "rules/lifecycle/validation/sub-activities/unit-testing.md",
  "rules/lifecycle/validation/sub-activities/regression-testing.md",
  "rules/lifecycle/validation/sub-activities/integration-testing.md",
  "rules/lifecycle/validation/sub-activities/contract-testing.md",
  "rules/lifecycle/validation/sub-activities/e2e-testing.md",
  "rules/lifecycle/validation/sub-activities/performance-testing.md",
  "rules/lifecycle/validation/sub-activities/security-testing.md",
  "rules/lifecycle/operations/sub-activities/README.md",
  "rules/lifecycle/operations/sub-activities/metrics-collection.md",
  "rules/lifecycle/operations/sub-activities/baseline-drift-check.md",
  "rules/lifecycle/operations/sub-activities/closure-summary.md",
  "rules/lifecycle/operations/sub-activities/hub-sync.md",
  "rules/lifecycle/operations/sub-activities/strategic-notification.md",
  "rules/lifecycle/operations/sub-activities/followup-conversion.md",
  "templates/hub/execution-plan.md",
  "templates/hub/environment-parameters.md",
  "templates/hub/validation-evidence.md",
  "knowledge/README.md",
  "knowledge/policy-template.md",
  "docs/knowledge-governance.md",
  "docs/automation-fallback.md",
  "scripts/powershell/validate-knowledge.ps1",
  "scripts/python/validate-knowledge.py",
  "rules/demand-types/playbooks/README.md",
  "rules/demand-types/playbooks/migration.md",
  "install/README.md",
  "install/install.ps1",
  "install/install.sh",
  "install/devin/alfred/SKILL.md",
  "docs/implementation-status.md",
  "docs/layer-1-framework-closure.md"
  "docs/onboarding-sigla.md",
  "docs/framework-validation.md"
  "docs/host-adapter-readiness.md"
  "docs/version-adoption.md"
  "docs/release-governance.md"
  "CHANGELOG.md"
  "scripts/powershell/alfred-boot.ps1"
  "scripts/powershell/render-toolbar.ps1"
  "docs/skills-activation.md"
  "skills/lang-python.md"
  "skills/lang-sql.md"
  "skills/lang-terraform.md"
  "skills/platform-aws-data.md"
  "scripts/powershell/collect-observability.ps1"
  "scripts/powershell/generate-metrics-rollup.ps1"
  "scripts/powershell/normalize-usage-cost.ps1"
  "scripts/powershell/validate-demand.ps1"
  "scripts/powershell/validate-reverse-eng-staleness.ps1"
  "scripts/powershell/validate-sdd-gate.ps1"
  "scripts/powershell/validate-toolbar-fixtures.ps1"
  "scripts/powershell/validate-skills-registry.ps1"
  "scripts/powershell/validate-connectors.ps1"
  "scripts/powershell/validate-model-policy.ps1"
  "scripts/python/alfred-boot.py"
  "scripts/python/render-toolbar.py"
  "scripts/python/collect-observability.py"
  "scripts/python/generate-metrics-rollup.py"
  "scripts/python/normalize-usage-cost.py"
  "scripts/python/validate-framework.py"
  "scripts/python/validate-demand.py"
  "scripts/python/validate-reverse-eng-staleness.py"
  "scripts/python/validate-sdd-gate.py"
  "scripts/python/validate-toolbar-fixtures.py"
  "scripts/python/validate-skills-registry.py"
  "scripts/python/validate-connectors.py"
  "scripts/python/validate-model-policy.py"
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

& (Join-Path $rootPath "scripts/powershell/validate-toolbar-fixtures.ps1") -Root $rootPath
& (Join-Path $rootPath "scripts/powershell/validate-skills-registry.ps1") -Root $rootPath
& (Join-Path $rootPath "scripts/powershell/validate-connectors.ps1") -Root $rootPath
& (Join-Path $rootPath "scripts/powershell/validate-model-policy.ps1") -Root $rootPath
& (Join-Path $rootPath "scripts/powershell/validate-knowledge.ps1") -Root $rootPath
& (Join-Path $rootPath "scripts/powershell/validate-demand.ps1") -HubDemandPath (Join-Path $rootPath "examples/sq9-pilot/alfred-docs-hub/iniciativa-001-piloto/005-parallel-units")
& (Join-Path $rootPath "scripts/powershell/alfred-boot.ps1") -Root $rootPath | Out-Null
& (Join-Path $rootPath "scripts/powershell/validate-reverse-eng-staleness.ps1") -ReverseEngPath (Join-Path $rootPath "examples/staleness-fixtures/reverse-eng-fresh.md") -CurrentCommit "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
& (Join-Path $rootPath "scripts/powershell/validate-sdd-gate.ps1") -HubDemandPath (Join-Path $rootPath "examples/sq9-pilot/alfred-docs-hub/iniciativa-001-piloto/005-parallel-units")

Write-Output "Framework validation completed."
