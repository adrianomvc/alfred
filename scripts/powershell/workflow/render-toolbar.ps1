param(
  [Parameter(Mandatory = $true)]
  [string]$StatePath,

  [string]$Model = "default",
  [string]$Cost = "n/a",

  [ValidateSet("text", "rich", "web")]
  [string]$Profile = "text",

  # numeric cost so far (USD); enables the linear total-cost forecast
  [string]$CostUsd = ""
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

# --- shared vocabulary (borderless design, owner-approved 2026-07-07) ---
$laneColors = @{ fast = "32"; standard = "33"; safe = "31" }   # green / amber / red
$laneIcons = @{ fast = "🟢"; standard = "🟡"; safe = "🔴" }
$aliasText = @{ Inception = "O que"; Design = "Como"; Execution = "Fazer";
                Validate = "Validar"; Operation = "Operar" }
$aliasRich = @{ Inception = "O quê"; Design = "Como"; Execution = "Fazer";
                Validate = "Validar"; Operation = "Operar" }

function Get-ForecastTotal {
  # Linear extrapolation of the total demand cost from recorded cost + progress.
  # Estimate, never a fact: labeled with '~' and omitted whenever the recorded
  # cost is not numeric or progress is 0/100 (no inventing — supreme law).
  param(
    [string]$CostUsd,
    [double]$Progress
  )

  $value = 0.0
  $inv = [System.Globalization.CultureInfo]::InvariantCulture
  if (-not [double]::TryParse(($CostUsd -replace ",", "."), [System.Globalization.NumberStyles]::Float, $inv, [ref]$value)) {
    return ""
  }
  if ($value -le 0 -or $Progress -le 0 -or $Progress -ge 100) {
    return ""
  }
  return "~US$ " + ($value * 100.0 / $Progress).ToString("F2", $inv)
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
  $markers += $marker
}

$progress = [Math]::Min(100, [Math]::Round(($completed / 5) * 100))
$forecast = Get-ForecastTotal -CostUsd $CostUsd -Progress $progress

# rich-cli profile (optional): ANSI color + bar + icons; helper-rendered.
if ($Profile -eq "rich") {
  [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
  $e = [char]27
  function Ansi($code, $s) { "$e[${code}m$s$e[0m" }
  $col = $laneColors[$lane.ToLowerInvariant()]; if (-not $col) { $col = "36" }
  $icon = $laneIcons[$lane.ToLowerInvariant()]; if (-not $icon) { $icon = "⚪" }
  $head = "🎩 $(Ansi '1' 'ALFRED') · $sigla · #$id · $icon $(Ansi $col $lane.ToUpperInvariant())"
  if ($lane.ToLowerInvariant() -eq "fast") {
    $alias = $aliasRich[$phase]; if (-not $alias) { $alias = $phase }
    Write-Output "$head · $alias ▶ · custo: $Cost · $(Ansi '2' '→') $(Shorten $next 56)"
    exit 0
  }
  $filled = [int][Math]::Round($progress / 10)
  $bar = (Ansi $col ("▰" * $filled)) + (Ansi '2' ("▱" * (10 - $filled)))
  $trackParts = @()
  for ($i = 0; $i -lt [Math]::Min(5, $markers.Count); $i++) {
    $name = $aliasRich[$phases[$i]]; if (-not $name) { $name = $phases[$i] }
    $mk = if ($markers[$i] -eq "x") { Ansi '32' "✓" } elseif ($markers[$i] -eq ">") { Ansi '36' "▶" } else { Ansi '2' "◻" }
    $trackParts += "$name $mk"
  }
  $track = $trackParts -join " · "
  $costPart = "custo: $Cost"
  if ($forecast) { $costPart += " · previsão total: $forecast" }
  Write-Output $head
  Write-Output "$bar $progress% $(Ansi '2' '│') $track"
  Write-Output "⏸ HITL: $(Shorten $checkpoint 44) $(Ansi '2' '│') modelo: $Model $(Ansi '2' '│') $costPart"
  Write-Output "$(Ansi '2' '→') Próximo: $(Shorten $next 76)"
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

# text floor: borderless ASCII (no box = nothing to misalign; degrades anywhere)
$forecastPart = ""
if ($forecast) { $forecastPart = " | est. total: $forecast" }

if ($lane.ToLowerInvariant() -eq "fast") {
  Write-Output "ALFRED | $sigla | #$id | FAST | $phase | model: $Model | cost: $Cost$forecastPart | next: $(Shorten $next 48)"
  exit 0
}

$barFilled = [int][Math]::Round($progress / 5)
$bar = "[" + ("#" * $barFilled) + ("." * (20 - $barFilled)) + "]"
$trackParts = @()
for ($i = 0; $i -lt [Math]::Min(5, $markers.Count); $i++) {
  $name = $aliasText[$phases[$i]]; if (-not $name) { $name = $phases[$i] }
  $trackParts += "$name[$($markers[$i])]"
}
$track = $trackParts -join " -> "

Write-Output "ALFRED | $sigla | #$id | $($lane.ToUpperInvariant())"
Write-Output "$bar $progress% | $track"
Write-Output "HITL: $(Shorten $checkpoint 52) | model: $Model | cost: $Cost$forecastPart"
Write-Output "Next: $(Shorten $next 76)"
