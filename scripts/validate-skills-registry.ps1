param(
  [string]$Root = "."
)

$ErrorActionPreference = "Stop"
$rootPath = Resolve-Path -LiteralPath $Root
$registryPath = Join-Path $rootPath "skills/skills.md"

if (-not (Test-Path -LiteralPath $registryPath)) {
  throw "Missing skills registry: $registryPath"
}

$requiredSections = @(
  "name",
  "purpose",
  "trigger",
  "inputs",
  "expected output",
  "link",
  "sections to load"
)

$registryLines = Get-Content -LiteralPath $registryPath
$skills = @()

foreach ($line in $registryLines) {
  if ($line -match '^\|\s*`([^`]+)`\s*\|\s*`([^`]+)`\s*\|') {
    $skills += [pscustomobject]@{
      Name = $Matches[1]
      Link = $Matches[2]
    }
  }
}

if ($skills.Count -eq 0) {
  throw "No skills found in registry table."
}

foreach ($skill in $skills) {
  $skillPath = Join-Path $rootPath $skill.Link
  if (-not (Test-Path -LiteralPath $skillPath)) {
    throw "Missing registered skill $($skill.Name): $($skill.Link)"
  }

  $content = Get-Content -LiteralPath $skillPath -Raw
  foreach ($section in $requiredSections) {
    $escaped = [regex]::Escape($section)
    if ($content -notmatch "(?im)^##\s+$escaped\s*$") {
      throw "Skill $($skill.Name) is missing required section: $section"
    }
  }

  Write-Output "OK skill $($skill.Name)"
}

Write-Output "Skills registry validation completed."
