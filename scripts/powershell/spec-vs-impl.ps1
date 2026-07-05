param(
  [Parameter(Mandatory = $true)][string]$HubDemandPath,
  [string]$AppDemandPath = "",
  [double]$Threshold = 0.5,
  [switch]$Strict
)

# Compare spec acceptance criteria against validation evidence (W8.2).
# PowerShell mirror of scripts/python/spec-vs-impl.py. Optional helper (D3).
# Heuristic, not a judge: flags criteria with no textual echo in the evidence
# so the Reviewer/human looks at them - it never approves.

$ErrorActionPreference = "Stop"
$stop = @("a","o","os","as","de","do","da","dos","das","e","em","no","na","com","para","the","of","and","to","in","is","are","be","por","um","uma")

function Get-Tokens {
  param([string]$Text)
  $set = New-Object System.Collections.Generic.HashSet[string]
  foreach ($m in [regex]::Matches($Text.ToLowerInvariant(), "[\w.]+")) {
    $t = $m.Value
    if ($t.Length -gt 2 -and $stop -notcontains $t) { [void]$set.Add($t) }
  }
  return $set
}

$evidencePath = Join-Path $HubDemandPath "04-validate/013-validation-evidence.md"
if (-not (Test-Path -LiteralPath $evidencePath)) {
  Write-Output "ERROR missing_evidence: $evidencePath not found"
  exit 1
}
$evidence = Get-Content -LiteralPath $evidencePath -Raw -Encoding UTF8

$criteria = @()
if ($AppDemandPath -ne "") {
  $specPath = Join-Path $AppDemandPath "02-design/003-spec.md"
  if (Test-Path -LiteralPath $specPath) {
    $spec = Get-Content -LiteralPath $specPath -Raw -Encoding UTF8
    $m = [regex]::Match($spec, '(?ims)^##\s+Acceptance criteria\s*$(.*?)(?=^##\s|\z)')
    if ($m.Success) {
      foreach ($line in $m.Groups[1].Value -split "`n") {
        $t = $line.Trim()
        if ($t.StartsWith("-") -and $t.Length -gt 5) { $criteria += $t.TrimStart("-", " ") }
      }
    }
  }
}
if ($criteria.Count -eq 0) {
  foreach ($line in $evidence -split "`n") {
    $cells = @($line.Trim().Trim("|") -split "\|" | ForEach-Object { $_.Trim() })
    if ($cells.Count -ge 2 -and $cells[0] -and $cells[0] -notmatch "^[- ]+$" -and
        $cells[0].ToLowerInvariant() -notin @("criterio", "criterion")) {
      $criteria += $cells[0]
    }
  }
}
if ($criteria.Count -eq 0) {
  Write-Output "ERROR no_criteria: no acceptance criteria found in app spec or evidence table"
  exit 1
}

$evidenceTokens = Get-Tokens -Text $evidence
$uncovered = 0
foreach ($criterion in $criteria) {
  $ctok = Get-Tokens -Text $criterion
  $hit = 0
  foreach ($t in $ctok) { if ($evidenceTokens.Contains($t)) { $hit += 1 } }
  $overlap = if ($ctok.Count -gt 0) { $hit / $ctok.Count } else { 0 }
  $pct = "{0:P0}" -f $overlap
  if ($overlap -ge $Threshold) {
    Write-Output "OK covered ($pct): $criterion"
  } else {
    $uncovered += 1
    Write-Output "GAP uncovered ($pct): $criterion"
  }
}

$thresholdPct = "{0:P0}" -f $Threshold
Write-Output "Spec-vs-impl completed. criteria=$($criteria.Count) uncovered=$uncovered threshold=$thresholdPct (heuristic - a human/Reviewer decides)"
if ($uncovered -gt 0 -and $Strict) { exit 1 }
