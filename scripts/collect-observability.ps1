param(
  [string]$Root = "examples",
  [string]$OutputPath = ""
)

$ErrorActionPreference = "Stop"
$rootPath = Resolve-Path -LiteralPath $Root
$events = @()

$files = Get-ChildItem -Path $rootPath -Recurse -Filter "*observability-log.jsonl" -Force
foreach ($file in $files) {
  $lineNumber = 0
  Get-Content -LiteralPath $file.FullName | ForEach-Object {
    $lineNumber += 1
    if ($_.Trim().Length -gt 0) {
      $event = $_ | ConvertFrom-Json
      $event | Add-Member -NotePropertyName "_source_file" -NotePropertyValue $file.FullName -Force
      $event | Add-Member -NotePropertyName "_source_line" -NotePropertyValue $lineNumber -Force
      $events += $event
    }
  }
}

if ($OutputPath -ne "") {
  $events |
    Sort-Object ts, sequence |
    ForEach-Object { $_ | ConvertTo-Json -Compress -Depth 20 } |
    Set-Content -LiteralPath $OutputPath
  Write-Output "Wrote $($events.Count) events to $OutputPath"
} else {
  $events |
    Sort-Object ts, sequence |
    Select-Object ts, initiative_id, demand_id, event_type, phase, lane, status, _source_file, _source_line
}

