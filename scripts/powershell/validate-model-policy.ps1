param(
  [string]$Root = "."
)

$ErrorActionPreference = "Stop"
$rootPath = Resolve-Path -LiteralPath $Root
$policyPath = Join-Path $rootPath "core/model-policy.md"

if (-not (Test-Path -LiteralPath $policyPath)) {
  throw "Missing model policy: $policyPath"
}

$content = Get-Content -LiteralPath $policyPath -Raw

function Assert-HeadingContains {
  param([string]$Text)

  $escaped = [regex]::Escape($Text)
  if ($content -notmatch "(?im)^##\s+.*$escaped.*$") {
    throw "Model policy is missing required heading containing: $Text"
  }
  Write-Output "OK heading $Text"
}

function Assert-Pattern {
  param(
    [string]$Pattern,
    [string]$Label
  )

  if ($content -notmatch $Pattern) {
    throw "Model policy is missing or changed: $Label"
  }
  Write-Output "OK policy $Label"
}

Assert-HeadingContains "Selection rule"
Assert-HeadingContains "Floor per lane"
Assert-HeadingContains "Adjustment per step"
Assert-HeadingContains "Tier"
Assert-HeadingContains "real model"
Assert-HeadingContains "Mechanism"
Assert-HeadingContains "User override"
Assert-HeadingContains "In the toolbar"

$requiredFloors = @{
  "FAST" = "cheap"
  "Standard" = "medium"
  "SAFE" = "strong"
}

foreach ($lane in $requiredFloors.Keys) {
  $tier = $requiredFloors[$lane]
  Assert-Pattern -Pattern "(?im)^\|\s*$lane\s*\|\s*$tier\s*\|" -Label "$lane floor = $tier"
}

foreach ($tier in @("cheap", "medium", "strong")) {
  Assert-Pattern -Pattern "(?im)^\|\s*$tier\s*\|" -Label "tier map includes $tier"
}

Assert-Pattern -Pattern "(?im)Design.*spec-design.*\+1 tier" -Label "Design/spec-design can rise above floor"
Assert-Pattern -Pattern "(?im)Execution.*boilerplate.*keep floor" -Label "Execution boilerplate keeps floor"
Assert-Pattern -Pattern "(?im)Validate.*reviewer.*keep / \+1 if risk" -Label "Validate reviewer adjustment is explicit"
Assert-Pattern -Pattern "(?im)Decisions / architecture \(SAFE\).*\|\s*strongest\s*\|" -Label "SAFE architecture decisions use strongest"
Assert-Pattern -Pattern "(?im)below the risk floor.*warns? the trade-off" -Label "override below floor warns human"
Assert-Pattern -Pattern '(?im)record[s]? it in `state`/`audit`' -Label "override is recorded"
Assert-Pattern -Pattern "(?im)toolbar shows the \*\*current model\*\*" -Label "toolbar declares current model"

Write-Output "Model policy validation completed."
