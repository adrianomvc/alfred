# Connector - Notification Email

## type
`notification`

## activation
Destination and triggers are configured in `knowledge/notification.md`. Transport may be SMTP, Graph, SES, MCP, or manual.

## operations
- `send(destination, subject, attachments)` sends strategic notifications only.

## degradation
Without a sender, Alfred prepares the subject, body, and attachment list, then reminds the human to send manually.

## guardrail
Auto-send is allowed only for configured destination + trigger + standard content. Anything outside config requires human confirmation and an audit entry.

## audit fields
destination, trigger, subject, attachment list, send mode, approval reference, result, failure reason.
