# Connector - Telemetry API

## type
`telemetry`

## activation
Future optional backend for sending Alfred event batches. Not required for the framework to work.

## operations
- `send_events(batch)` sends audit/metrics events and returns acknowledgement.

## degradation
Events remain in markdown `audit` and `metrics`; rollups can be produced from files.

## audit fields
batch id, event count, destination, acknowledgement, failure reason.

