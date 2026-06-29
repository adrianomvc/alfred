param(
  [string]$Root = "."
)

# Validate internal Markdown references in the Alfred framework.
# PowerShell mirror of scripts/python/validate-links.py. Optional helper (D3):
# Alfred still works manually through Markdown if it cannot run. It catches
# broken cross-references after files are moved or renamed.
#
# Checks two reference styles:
# - Markdown links [text](target) - resolved relative to the file, then root.
# - Inline code paths `top-dir/...` (start with a framework top folder) -
#   resolved relative to root, then the file.
# URLs, mailto:, pure #anchor links, and glob patterns (*) are skipped.
# CHANGELOG.md is excluded: it is a historical ledger with point-in-time paths.

$ErrorActionPreference = "Stop"
$rootPath = (Resolve-Path -LiteralPath $Root).Path

$scanDirs = @("core", "rules", "skills", "connectors", "metrics", "knowledge", "templates", "docs", "install")
$rootFiles = @("README.md")
$inlinePathPattern = '^(core|rules|skills|connectors|metrics|knowledge|templates|docs|scripts|examples|install)/[\w./-]+$'

function Test-Reference {
  param([string[]]$Candidates)
  foreach ($cand in $Candidates) {
    if (Test-Path -LiteralPath $cand) { return $true }
  }
  return $false
}

$files = 0
$checked = 0
$broken = 0

$mdFiles = New-Object System.Collections.Generic.List[string]
foreach ($rel in $rootFiles) {
  $p = Join-Path $rootPath $rel
  if (Test-Path -LiteralPath $p) { $mdFiles.Add($p) }
}
foreach ($dir in $scanDirs) {
  $base = Join-Path $rootPath $dir
  if (Test-Path -LiteralPath $base) {
    Get-ChildItem -Path $base -Recurse -Filter *.md -File | ForEach-Object { $mdFiles.Add($_.FullName) }
  }
}

foreach ($file in $mdFiles) {
  $files += 1
  $dir = Split-Path -Parent $file
  $text = Get-Content -LiteralPath $file -Raw -Encoding UTF8

  $refs = New-Object System.Collections.Generic.List[object]

  foreach ($m in [regex]::Matches($text, '\[[^\]]*\]\(([^)]+)\)')) {
    $target = ($m.Groups[1].Value -split '\s+')[0]
    $target = ($target -split '#')[0].Trim()
    if (-not $target) { continue }
    if ($target -match '://' -or $target.StartsWith('mailto:') -or $target.Contains('*')) { continue }
    $refs.Add([pscustomobject]@{ Kind = "link"; Target = $target })
  }

  foreach ($m in [regex]::Matches($text, '`([^`]+)`')) {
    $token = $m.Groups[1].Value.Trim()
    if ($token.Contains('*') -or $token.Contains(' ') -or ($token -notmatch $inlinePathPattern)) { continue }
    $refs.Add([pscustomobject]@{ Kind = "inline"; Target = $token })
  }

  foreach ($ref in $refs) {
    $checked += 1
    if ($ref.Kind -eq "link") {
      $candidates = @((Join-Path $dir $ref.Target), (Join-Path $rootPath $ref.Target))
    } else {
      $candidates = @((Join-Path $rootPath $ref.Target), (Join-Path $dir $ref.Target))
    }
    if (-not (Test-Reference -Candidates $candidates)) {
      $broken += 1
      $rel = $file.Substring($rootPath.Length).TrimStart('\', '/')
      Write-Output "BROKEN $rel -> $($ref.Target) ($($ref.Kind))"
    }
  }
}

Write-Output "Link validation completed. files=$files refs=$checked broken=$broken"
if ($broken -gt 0) { exit 1 }
