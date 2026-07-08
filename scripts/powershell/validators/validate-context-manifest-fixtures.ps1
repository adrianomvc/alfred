param(
  [string]$Root = "."
)

$ErrorActionPreference = "Stop"
$rootPath = Resolve-Path -LiteralPath $Root
$manifestScript = Join-Path $rootPath "scripts/powershell/workflow/context-manifest.ps1"

if (-not (Test-Path -LiteralPath $manifestScript)) {
  throw "Missing context-manifest helper: $manifestScript"
}

$cases = @(
  @{
    Name = "standard-product-design"
    Phase = "Design"
    Lane = "Standard"
    DemandType = "product"
    Agent = "spec-design"
    SubActivity = "functional-design"
    Expected = "examples/context-manifest-fixtures/standard-product-design.txt"
  },
  @{
    Name = "fast-operational-execution"
    Phase = "Execution"
    Lane = "FAST"
    DemandType = "operational"
    Agent = "orchestrator"
    SubActivity = "workflow-planning"
    Expected = "examples/context-manifest-fixtures/fast-operational-execution.txt"
  },
  @{
    Name = "safe-engineering-inception"
    Phase = "Inception"
    Lane = "SAFE"
    DemandType = "engineering"
    Agent = "discovery"
    SubActivity = "risk-mode-proposal"
    Expected = "examples/context-manifest-fixtures/safe-engineering-inception.txt"
  }
)

foreach ($case in $cases) {
  $expectedPath = Join-Path $rootPath $case.Expected
  if (-not (Test-Path -LiteralPath $expectedPath)) {
    throw "Missing context-manifest fixture for $($case.Name): $expectedPath"
  }

  $actual = (& $manifestScript `
      -Root $rootPath `
      -Phase $case.Phase `
      -Lane $case.Lane `
      -DemandType $case.DemandType `
      -Agent $case.Agent `
      -SubActivity $case.SubActivity) -join [Environment]::NewLine
  $expected = Get-Content -LiteralPath $expectedPath -Raw

  $actualNormalized = ($actual -replace "`r`n", "`n").TrimEnd()
  $expectedNormalized = ($expected -replace "`r`n", "`n").TrimEnd()
  if ($actualNormalized -ne $expectedNormalized) {
    throw "Context manifest fixture drift: $($case.Name). Regenerate or update expected output intentionally."
  }

  Write-Output "OK context manifest fixture $($case.Name)"
}

Write-Output "Context manifest fixture validation completed."
