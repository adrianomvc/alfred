"""Claude Code transcript parsing (host format -> parsed request observations).

Owns the Claude-specific knowledge that used to live inside
``attribute-usage-transcript.py``: assistant/user record shapes, ``requestId``
dedup, ``promptId``/user-boundary interaction correlation, exact token usage,
and tool-use extraction. Alfred event assembly stays in the command driver.
"""

import json
from collections import defaultdict
from datetime import datetime, timezone
from decimal import Decimal
from typing import Mapping

from shared.observability.domain.enums import Confidence, UsageUnit
from shared.observability.domain.models import (
    AdapterCapabilities,
    AdapterContext,
    CanonicalEvent,
    Usage,
    UsageDimension,
)
from shared.observability.infrastructure.adapters.claude.transcript_cursor import TranscriptCursor


def parse_ts(raw):
    if not raw:
        return None
    text = str(raw).strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def iso(dt):
    if not isinstance(dt, datetime):
        return None
    return dt.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def iter_records(lines):
    for raw in lines:
        if not raw.strip():
            continue
        try:
            yield json.loads(raw)
        except json.JSONDecodeError:
            continue


def content_tool_uses(message):
    content = message.get("content") if isinstance(message, dict) else None
    if not isinstance(content, list):
        return []
    return [item for item in content if isinstance(item, dict) and item.get("type") == "tool_use"]


def request_tokens(record):
    message = record.get("message") or {}
    usage = message.get("usage") or {}
    return {
        "tokens_input": usage.get("input_tokens") or 0,
        "tokens_output": usage.get("output_tokens") or 0,
        "tokens_cache_creation": usage.get("cache_creation_input_tokens") or 0,
        "tokens_cache_read": usage.get("cache_read_input_tokens") or 0,
    }


class ClaudeTranscriptAdapter:
    """Parse a Claude Code transcript into ordered request observations."""

    def __init__(self, cursor: TranscriptCursor | None = None) -> None:
        self._cursor = cursor or TranscriptCursor()

    def capabilities(self) -> AdapterCapabilities:
        return AdapterCapabilities(request_tokens=True, session_usage=False, cost=False, artifacts=True, tools=True)

    def load_requests(self, transcript_path, cursor_path=None):
        """Return (ordered_requests, tools, start_offset, end_offset).

        Byte-for-byte port of the legacy ``load_transcript_requests`` so the
        command's event assembly is unchanged.
        """
        lines, start_offset, end_offset = self._cursor.read_slice(transcript_path, cursor_path)
        requests = {}
        tools = []
        current_interaction = None
        current_interaction_sequence = 0
        request_sequence_by_interaction = defaultdict(int)

        for record in iter_records(lines):
            ts = parse_ts(record.get("timestamp"))
            record_type = record.get("type")
            session_id = record.get("sessionId") or record.get("session_id")

            if record_type == "user":
                prompt_id = record.get("promptId")
                user_uuid = record.get("uuid")
                if prompt_id:
                    interaction_id = prompt_id
                    confidence = "exact"
                    method = "prompt_id"
                elif user_uuid:
                    interaction_id = f"derived-user-{user_uuid}"
                    confidence = "derived"
                    method = "transcript_user_boundary"
                else:
                    interaction_id = None
                    confidence = "unavailable"
                    method = "request_only"
                current_interaction_sequence += 1
                current_interaction = {
                    "interaction_id": interaction_id,
                    "interaction_sequence": current_interaction_sequence,
                    "interaction_confidence": confidence,
                    "correlation_method": method,
                    "ts": ts,
                    "session_id": session_id,
                }
                continue

            if record_type != "assistant":
                continue

            message = record.get("message") or {}
            request_id = record.get("requestId") or record.get("uuid")
            if not request_id:
                continue
            interaction = current_interaction or {
                "interaction_id": None,
                "interaction_sequence": None,
                "interaction_confidence": "unavailable",
                "correlation_method": "request_only",
                "ts": None,
                "session_id": session_id,
            }
            request_sequence_by_interaction[interaction["interaction_id"]] += 1
            payload = {
                "request_id": request_id,
                "uuid": record.get("uuid"),
                "ts": ts,
                "session_id": session_id or interaction.get("session_id"),
                "model": message.get("model"),
                "interaction_id": interaction.get("interaction_id"),
                "interaction_sequence": interaction.get("interaction_sequence"),
                "request_sequence": request_sequence_by_interaction[interaction["interaction_id"]],
                "interaction_confidence": interaction.get("interaction_confidence"),
                "correlation_method": interaction.get("correlation_method"),
                **request_tokens(record),
            }
            existing = requests.get(request_id)
            if existing is None:
                requests[request_id] = payload
            else:
                if ts and (existing["ts"] is None or ts < existing["ts"]):
                    existing["ts"] = ts
                existing.update({k: v for k, v in payload.items() if v is not None})
                existing.update(request_tokens(record))

            for item in content_tool_uses(message):
                tools.append(
                    {
                        "ts": ts,
                        "session_id": session_id,
                        "interaction_id": interaction.get("interaction_id"),
                        "request_id": request_id,
                        "tool_use_id": item.get("id"),
                        "tool_name": item.get("name"),
                        "input": item.get("input") if isinstance(item.get("input"), dict) else {},
                    }
                )

        ordered = [r for r in requests.values() if r["ts"] is not None]
        ordered.sort(key=lambda r: r["ts"])
        return ordered, tools, start_offset, end_offset

    def read_transcript(self, source: object, context: AdapterContext) -> list[CanonicalEvent]:
        """Protocol conformance: parsed requests as canonical usage events."""
        if isinstance(source, Mapping):
            cursor_path = source.get("cursor_path")
            transcript_path = source.get("transcript_path")
        else:
            cursor_path = None
            transcript_path = source
        requests, _tools, _start, _end = self.load_requests(transcript_path, cursor_path)
        return [self._to_canonical(request, context) for request in requests]

    def _to_canonical(self, request: Mapping[str, object], context: AdapterContext) -> CanonicalEvent:
        dimensions = []
        for key, unit in (
            ("tokens_input", UsageUnit.TOKEN_INPUT),
            ("tokens_output", UsageUnit.TOKEN_OUTPUT),
            ("tokens_cache_creation", UsageUnit.TOKEN_CACHE_CREATION),
            ("tokens_cache_read", UsageUnit.TOKEN_CACHE_READ),
        ):
            value = request.get(key)
            if value:
                dimensions.append(UsageDimension(unit=unit, value=Decimal(str(value)), confidence=Confidence.EXACT, source="host_transcript"))
        return CanonicalEvent(
            schema_version="alfred.observability.v1",
            event_id=f"usage-request-{request.get('request_id')}",
            event_type="usage_attributed",
            event_scope="request",
            timestamp=request.get("ts"),
            host=context.host,
            source_kind="host_transcript",
            session_id=request.get("session_id"),
            interaction_id=request.get("interaction_id"),
            request_id=request.get("request_id"),
            model=request.get("model"),
            usage=Usage(tuple(dimensions)),
            raw=dict(request),
        )
