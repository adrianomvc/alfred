param(
  [string]$Root = "."
)

$ErrorActionPreference = "Stop"
$rootPath = Resolve-Path -LiteralPath $Root
$renderer = Join-Path $rootPath "scripts/powershell/render-toolbar.ps1"

if (-not (Test-Path -LiteralPath $renderer)) {
  throw "Missing toolbar renderer: $renderer"
}

$cases = @(
  @{
    Name = "fast"
    State = "examples/sq9-pilot/alfred-docs-hub/iniciativa-001-piloto/002-simulado-fast/001-state.md"
    Expected = "examples/toolbar-fixtures/fast.txt"
  },
  @{
    Name = "safe"
    State = "examples/sq9-pilot/alfred-docs-hub/iniciativa-001-piloto/003-simulado-safe/001-state.md"
    Expected = "examples/toolbar-fixtures/safe.txt"
  },
  @{
    Name = "execution-first"
    State = "examples/sq9-pilot/alfred-docs-hub/iniciativa-001-piloto/004-execution-first/001-state.md"
    Expected = "examples/toolbar-fixtures/execution-first.txt"
  },
  @{
    Name = "standard-parallel-units"
    State = "examples/sq9-pilot/alfred-docs-hub/iniciativa-001-piloto/005-parallel-units/001-state.md"
    Expected = "examples/toolbar-fixtures/standard-parallel-units.txt"
  }
)

foreach ($case in $cases) {
  $statePath = Join-Path $rootPath $case.State
  $expectedPath = Join-Path $rootPath $case.Expected

  if (-not (Test-Path -LiteralPath $statePath)) {
    throw "Missing toolbar fixture state for $($case.Name): $statePath"
  }
  if (-not (Test-Path -LiteralPath $expectedPath)) {
    throw "Missing toolbar fixture expected output for $($case.Name): $expectedPath"
  }

  $actual = (& $renderer -StatePath $statePath -Model "GPT-5" -Cost "n/a") -join [Environment]::NewLine
  $expected = Get-Content -LiteralPath $expectedPath -Raw

  if ($actual.TrimEnd() -ne $expected.TrimEnd()) {
    throw "Toolbar fixture drift: $($case.Name). Regenerate or update expected output intentionally."
  }

  Write-Output "OK toolbar fixture $($case.Name)"
}

Write-Output "Toolbar fixture validation completed."
