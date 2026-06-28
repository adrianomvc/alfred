param(
  [Parameter(Mandatory = $true)]
  [string]$InputPath,

  [string]$OutputPath = "",

  [switch]$Append
)

$ErrorActionPreference = "Stop"
$inputFullPath = Resolve-Path -LiteralPath $InputPath
$frameworkVersion = "unknown"
$versionPath = Join-Path (Get-Location) "VERSION"
if (Test-Path -LiteralPath $versionPath) {
  $frameworkVersion = (Get-Content -LiteralPath $versionPath -TotalCount 1).Trim()
}

function Value-OrDefault {
  param($Value, [string]$Default)
  if ($null -eq $Value -or "$Value" -eq "") {
    return $Default
  }
  return "$Value"
}

$events = @()
$lineNumber = 0
Get-Content -LiteralPath $inputFullPath | ForEach-Object {
  $lineNumber += 1
  if ($_.Trim().Length -gt 0) {
    $record = $_ | ConvertFrom-Json
    $eventId = "usage-$lineNumber"
    if ($record.event_id) {
      $eventId = "usage-$($record.event_id)"
    }

    $event = [ordered]@{
      schema_version = "alfred.observability.v1"
      alfred = [ordered]@{
        version = $frameworkVersion
        framework_ref = "local"
        framework_commit = $null
        schema_version = "alfred.observability.v1"
      }
      ts = (Value-OrDefault $record.ts "unknown")
      event_id = $eventId
      trace_id = (Value-OrDefault $record.trace_id "unknown")
      session_id = (Value-OrDefault $record.session_id "unknown")
      interaction_id = (Value-OrDefault $record.interaction_id "unknown")
      sequence = $lineNumber
      initiative_id = (Value-OrDefault $record.initiative_id "unknown")
      demand_id = (Value-OrDefault $record.demand_id "unknown")
      event_type = "usage_attributed"
      phase = (Value-OrDefault $record.phase "operation")
      lane = (Value-OrDefault $record.lane "unknown")
      actor_type = "system"
      actor_id = "usage-cost-adapter"
      action = "attribute_usage"
      status = "recorded"
      step = [ordered]@{
        id = "usage-cost"
        name = "Usage and cost attribution"
        sequence = $lineNumber
        goal = "Normalize host usage into Alfred observability"
      }
      artifacts_used = @(
        [ordered]@{
          path = "$inputFullPath"
          role = "source_usage_export"
          action = "read"
        }
      )
      duration_ms = $null
      tokens_input = $record.tokens_input
      tokens_output = $record.tokens_output
      cost_usd = $record.cost_usd
      retry_count = 0
      input = [ordered]@{
        source = (Value-OrDefault $record.source "host_usage_export")
        source_line = $lineNumber
      }
      derivation = [ordered]@{
        rules_applied = @("connectors/usage-cost.md", "metrics/metrics.md")
        method = "field mapping without rewriting previous events"
      }
      output = [ordered]@{
        model = $record.model
        tokens_input = $record.tokens_input
        tokens_output = $record.tokens_output
        cost_usd = $record.cost_usd
      }
      model = $record.model
      tool = "scripts/normalize-usage-cost.ps1"
      parent_event_id = $record.parent_event_id
      artifacts = @()
      files_changed = @()
      validation = [ordered]@{
        source_record_parse = "ok"
      }
      risk = $null
      blocker = $null
      error = $null
      state_transition = $null
      actions = @(
        [ordered]@{
          type = "normalize"
          status = "completed"
          source_line = $lineNumber
        }
      )
      questions_open = @()
      assumptions = @()
      metric_impact = [ordered]@{
        usage_attribution = "added"
      }
      next = @()
      metadata = [ordered]@{
        connector_type = "usage-cost"
      }
    }

    $events += ($event | ConvertTo-Json -Depth 20 -Compress)
  }
}

if ($OutputPath -ne "") {
  if ($Append) {
    Add-Content -LiteralPath $OutputPath -Value $events
  } else {
    Set-Content -LiteralPath $OutputPath -Value $events
  }
  Write-Output "Wrote usage attribution events to $OutputPath"
} else {
  $events
}
