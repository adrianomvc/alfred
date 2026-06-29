param(
  [Parameter(Mandatory = $true)]
  [string]$StatePath,

  [string]$Model = "default",
  [string]$Cost = "n/a",

  [ValidateSet("text", "rich", "web")]
  [string]$Profile = "text"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path -LiteralPath $StatePath)) {
  throw "State file not found: $StatePath"
}

$content = Get-Content -LiteralPath $StatePath

function Get-Field {
  param(
    [string[]]$Lines,
    [string]$Name
  )

  $escaped = [regex]::Escape($Name)
  foreach ($line in $Lines) {
    if ($line -match "^\s*-\s+$escaped\s*:\s*(.+?)\s*$") {
      return $Matches[1].Trim().Trim([char]96)
    }
  }
  return ""
}

function Get-FirstField {
  param(
    [string[]]$Lines,
    [string[]]$Names
  )

  foreach ($name in $Names) {
    $value = Get-Field -Lines $Lines -Name $name
    if ($value -ne "") {
      return $value
    }
  }
  return ""
}

function Get-ChecklistStatus {
  param(
    [string[]]$Lines,
    [string]$Phase
  )

  foreach ($line in $Lines) {
    if ($line -match "^\s*-\s+\[(x|X| )\]\s+$Phase\b") {
      return $Matches[1]
    }
  }
  return " "
}

function Shorten {
  param(
    [string]$Value,
    [int]$Max = 64
  )

  if ($null -eq $Value) {
    return ""
  }
  if ($Value.Length -le $Max) {
    return $Value
  }
  return $Value.Substring(0, $Max - 3) + "..."
}

$id = Get-Field -Lines $content -Name "id"
$sigla = Get-Field -Lines $content -Name "sigla"
$lane = Get-FirstField -Lines $content -Names @("lane", "modo")
$phase = Get-FirstField -Lines $content -Names @("current phase", "fase atual")
$step = Get-FirstField -Lines $content -Names @("current step", "etapa atual")
$next = Get-FirstField -Lines $content -Names @("next step", "proximo passo", "próximo passo")
$checkpoint = Get-Field -Lines $content -Name "checkpoint"

if ($id -eq "") { $id = "unknown" }
if ($sigla -eq "") { $sigla = "unknown" }
if ($lane -eq "") { $lane = "unknown" }
if ($phase -eq "") { $phase = "unknown" }
if ($step -eq "") { $step = "unknown" }
if ($next -eq "") { $next = "unknown" }
if ($checkpoint -eq "") { $checkpoint = "n/a" }

$timeMode = Get-FirstField -Lines $content -Names @("tempo", "time mode")
$checklistText = ($content | Where-Object { $_ -match "^\s*-\s+\[[xX ]\]" }) -join "`n"
$isExecutionFirst = ($phase.ToLowerInvariant() -like "*execution-first*") -or ($timeMode.ToLowerInvariant() -like "*execution-first*") -or ($checklistText.ToLowerInvariant() -like "*execution-first stabilization*")

if ($isExecutionFirst) {
  $phases = @("Execution-first stabilization", "Inception posterior", "Design posterior", "Validate posterior", "Operation / post-mortem")
} else {
  $phases = @("Inception", "Design", "Execution", "Validate", "Operation")
}
$completed = 0
$phaseParts = @()
$markers = @()

foreach ($item in $phases) {
  $status = Get-ChecklistStatus -Lines $content -Phase $item
  if ($status -match "x|X") {
    $completed += 1
    $marker = "x"
  } elseif ($item.ToLowerInvariant() -eq $phase.ToLowerInvariant()) {
    $marker = ">"
  } else {
    $marker = " "
  }
  $phaseParts += "$item [$marker]"
  $markers += $marker
}

$progress = [Math]::Min(100, [Math]::Round(($completed / 5) * 100))
$track = $phaseParts -join " -> "

# rich-cli profile (optional): ANSI color + bar + icons; helper-rendered.
if ($Profile -eq "rich") {
  [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
  $e = [char]27
  function Ansi($code, $s) { "$e[${code}m$s$e[0m" }
  $laneColors = @{ fast = "32"; standard = "33"; safe = "31" }
  $col = $laneColors[$lane.ToLowerInvariant()]; if (-not $col) { $col = "36" }
  $head = "$(Ansi '1' 'ALFRED') $(Ansi '2' "SIGLA:$sigla `u{00B7} #$id") $(Ansi $col "[$($lane.ToUpperInvariant())]")"
  if ($lane.ToLowerInvariant() -eq "fast") {
    Write-Output "$head $(Ansi '2' $phase)  $(Ansi '2' "`u{2192}") $(Shorten $next 56)"
    exit 0
  }
  $filled = [int][Math]::Round($progress / 10)
  $bar = (Ansi $col ([string]([char]0x2588) * $filled)) + (Ansi '2' ([string]([char]0x2591) * (10 - $filled)))
  $circled = @("`u{2460}", "`u{2461}", "`u{2462}", "`u{2463}", "`u{2464}")
  $trackR = ""
  for ($i = 0; $i -lt [Math]::Min(5, $markers.Count); $i++) {
    $mk = if ($markers[$i] -eq "x") { Ansi '32' "`u{2713}" } elseif ($markers[$i] -eq ">") { Ansi '36' "`u{25B6}" } else { Ansi '2' "`u{25FB}" }
    $trackR += "$($circled[$i])$mk "
  }
  Write-Output "$head  $bar $progress%"
  Write-Output "  $($trackR.TrimEnd())"
  Write-Output "  $(Ansi '2' 'etapa') $(Shorten $step 60)   $(Ansi '2' 'HITL') $(Shorten $checkpoint 40)"
  Write-Output "  $(Ansi '2' "`u{2192}") $(Shorten $next 60)   $(Ansi '2' "$Model `u{00B7} $Cost")"
  exit 0
}

# web profile (optional): self-contained SVG of the state, helper-rendered.
if ($Profile -eq "web") {
  [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
  function Esc($s) { ("$s" -replace '&', '&amp;' -replace '<', '&lt;' -replace '>', '&gt;') }
  $laneWeb = @{ fast = @('#eaf6e9', '#2f6b1f', '#639922'); standard = @('#fdf3df', '#8a5a08', '#ba7517'); safe = @('#fbe9e9', '#a32d2d', '#e24b4a') }
  $lw = $laneWeb[$lane.ToLowerInvariant()]; if (-not $lw) { $lw = @('#eef0f2', '#444', '#888') }
  $barW = [int][Math]::Round(360 * $progress / 100)
  $cx = @(44, 138, 232, 326, 420)
  $circles = ""
  for ($i = 0; $i -lt [Math]::Min(5, $markers.Count); $i++) {
    if ($markers[$i] -eq "x") { $cf = '#eaf6e9'; $cs = '#639922'; $ct = '#2f6b1f'; $lbl = [char]0x2713 }
    elseif ($markers[$i] -eq ">") { $cf = '#e6f1fb'; $cs = '#378add'; $ct = '#185fa5'; $lbl = $i + 1 }
    else { $cf = '#f1f3f5'; $cs = '#d0d7de'; $ct = '#8a8f98'; $lbl = $i + 1 }
    $circles += '<circle cx="' + $cx[$i] + '" cy="86" r="13" fill="' + $cf + '" stroke="' + $cs + '"/><text x="' + $cx[$i] + '" y="91" text-anchor="middle" font-size="13" fill="' + $ct + '">' + $lbl + '</text>'
  }
  $conns = ""
  for ($i = 0; $i -lt 4; $i++) { $conns += '<line x1="' + ($cx[$i] + 14) + '" y1="86" x2="' + ($cx[$i + 1] - 14) + '" y2="86" stroke="#d0d7de"/>' }
  $svg = '<svg width="520" viewBox="0 0 520 132" role="img" font-family="-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif" xmlns="http://www.w3.org/2000/svg">' +
    '<title>Alfred ' + [char]0x00B7 + ' ' + (Esc $sigla) + ' ' + [char]0x00B7 + ' ' + (Esc $id) + '</title>' +
    '<rect x="0.5" y="0.5" width="519" height="131" rx="12" fill="#ffffff" stroke="#e1e4e8"/>' +
    '<text x="20" y="30" font-size="14" fill="#24292f"><tspan font-weight="600">ALFRED</tspan><tspan fill="#57606a">  ' + [char]0x00B7 + '  SIGLA:' + (Esc $sigla) + ' #' + (Esc $id) + '</tspan></text>' +
    '<rect x="416" y="16" width="88" height="22" rx="6" fill="' + $lw[0] + '"/>' +
    '<text x="460" y="31" text-anchor="middle" font-size="12" font-weight="600" fill="' + $lw[1] + '">' + (Esc $lane.ToUpperInvariant()) + '</text>' +
    '<rect x="20" y="50" width="360" height="8" rx="4" fill="#e1e4e8"/>' +
    '<rect x="20" y="50" width="' + $barW + '" height="8" rx="4" fill="' + $lw[2] + '"/>' +
    '<text x="392" y="58" font-size="12" fill="#57606a">' + $progress + '%</text>' +
    $conns + $circles +
    '<text x="20" y="120" font-size="12" fill="#57606a">' + [char]0x2192 + ' ' + (Esc (Shorten $next 72)) + '</text></svg>'
  Write-Output $svg
  exit 0
}

if ($lane.ToLowerInvariant() -eq "fast") {
  Write-Output "ALFRED | SIGLA:$sigla | #$id | FAST | $phase | model: $Model | cost: $Cost | next: $(Shorten $next 48)"
  exit 0
}

$line = "+-- ALFRED ------------------------------- SIGLA:$sigla | #$id --+"
$footer = "+" + ("-" * ([Math]::Max(64, $line.Length - 2))) + "+"

Write-Output $line
Write-Output "| Lane: $($lane.ToUpperInvariant()) | Model: $Model | Progress: $progress% |"
Write-Output "| Cost: $Cost |"
Write-Output "| $track |"
Write-Output "| Step : $(Shorten $step 72) |"
Write-Output "| HITL : $(Shorten $checkpoint 72) |"
Write-Output "| Next : $(Shorten $next 72) |"
Write-Output $footer
