# Telemetry Batch Example

Connector contract: `connectors/telemetry-api.md`

## Local Collection
Use the optional script:

```bash
python scripts/metrics/collect-observability.py -Root examples -OutputPath .tmp-observability-batch.jsonl
```

## Batch Shape
Each line remains one observability JSON object. The local collector adds:
- `_source_file`
- `_source_line`

## Degradation
If no telemetry API exists, the JSONL remains in HUB/App artifacts and metrics are computed locally or manually.

