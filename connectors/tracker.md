# Connector - Tracker

## type
`tracker`

## activation
Configured by the sigla/HUB knowledge. The concrete tracker is intentionally unspecified.

## operations
- `get_demand(id)` returns title, description, type, priority, requester, links.
- `open_issue(data)` creates a follow-up demand or debt item.

## degradation
If no tracker exists, the human provides the demand id and description; Alfred records the source as manual.

## audit fields
tracker id, title, source URL, requester, fetch time.

