"""Claude Code hook adapter: transcript records -> sanitized raw telemetry.

Owns the Claude-specific mapping that used to live in
``claude-code-usage-hook.py`` (``raw_events_from_transcript``,
``extract_tool_paths``, ``operation_for_tool``). Artifact/redaction/clock
helpers are injected so the shared package never imports the ``metrics`` command
package. Cursor and record iteration are the shared transcript primitives.
"""

from typing import Callable, Mapping

from shared.observability.domain.models import AdapterCapabilities
from shared.observability.infrastructure.adapters.claude.transcript import iter_records
from shared.observability.infrastructure.adapters.claude.transcript_cursor import TranscriptCursor

RAW_SCHEMA = "ai.agent.raw.v1"


def operation_for_tool(tool_name):
    if tool_name in ("Read", "Glob", "Grep", "LS"):
        return "read"
    if tool_name in ("Write",):
        return "create"
    if tool_name in ("Edit", "MultiEdit"):
        return "update"
    if tool_name in ("Bash", "Shell"):
        return "execute"
    return "use"


def extract_tool_paths(tool_name, tool_input):
    if not isinstance(tool_input, dict):
        return []
    candidates = []
    for key in ("file_path", "path", "notebook_path"):
        if tool_input.get(key):
            candidates.append(tool_input[key])
    if tool_name in ("Bash", "Shell") and tool_input.get("command"):
        candidates.append("command_output")
    return candidates


class ClaudeHookAdapter:
    def __init__(
        self,
        *,
        artifact_builder: Callable[..., dict],
        path_sanitizer: Callable[[object], object],
        now: Callable[[], str],
        cursor: TranscriptCursor | None = None,
    ) -> None:
        self._artifact = artifact_builder
        self._safe_path = path_sanitizer
        self._now = now
        self._cursor = cursor or TranscriptCursor()

    def capabilities(self) -> AdapterCapabilities:
        return AdapterCapabilities(request_tokens=True, session_usage=False, cost=False, artifacts=True, tools=True)

    def read_slice(self, transcript_path, cursor_path=None):
        return self._cursor.read_slice(transcript_path, cursor_path)

    def normalize_records(self, lines, provider):
        """Return (raw_events, last_request_id) from transcript lines.

        Byte-for-byte port of the legacy ``raw_events_from_transcript``.
        """
        events = []
        last_request_id = None
        current_prompt_id = None
        for record in iter_records(lines):
            ts = record.get("timestamp") or self._now()
            record_type = record.get("type")
            session_id = record.get("sessionId") or record.get("session_id")
            if record_type == "user":
                current_prompt_id = record.get("promptId") or current_prompt_id
                events.append(
                    {
                        "schema_version": RAW_SCHEMA,
                        "ts": ts,
                        "provider": provider,
                        "raw_event_type": "user_prompt",
                        "session_id": session_id,
                        "interaction_id": record.get("promptId"),
                        "message_uuid": record.get("uuid"),
                        "cwd": self._safe_path(record.get("cwd")),
                        "git_branch": record.get("gitBranch"),
                        "content_recorded": False,
                    }
                )
            elif record_type == "assistant":
                message = record.get("message") or {}
                request_id = record.get("requestId") or record.get("uuid")
                last_request_id = request_id or last_request_id
                usage = message.get("usage") or {}
                events.append(
                    {
                        "schema_version": RAW_SCHEMA,
                        "ts": ts,
                        "provider": provider,
                        "raw_event_type": "model_request",
                        "session_id": session_id,
                        "interaction_id": current_prompt_id,
                        "request_id": request_id,
                        "model": message.get("model"),
                        "tokens_input": usage.get("input_tokens"),
                        "tokens_output": usage.get("output_tokens"),
                        "tokens_cache_creation": usage.get("cache_creation_input_tokens"),
                        "tokens_cache_read": usage.get("cache_read_input_tokens"),
                        "content_recorded": False,
                    }
                )
                content = message.get("content")
                if isinstance(content, list):
                    for item in content:
                        if not isinstance(item, dict) or item.get("type") != "tool_use":
                            continue
                        tool_name = item.get("name")
                        tool_input = item.get("input") if isinstance(item.get("input"), dict) else {}
                        events.append(
                            {
                                "schema_version": RAW_SCHEMA,
                                "ts": ts,
                                "provider": provider,
                                "raw_event_type": "tool_use",
                                "session_id": session_id,
                                "interaction_id": current_prompt_id,
                                "request_id": request_id,
                                "tool_use_id": item.get("id"),
                                "tool_name": tool_name,
                                "operation": operation_for_tool(tool_name),
                                "input_keys": sorted(tool_input.keys()),
                                "artifacts": [
                                    self._artifact(
                                        path,
                                        operation_for_tool(tool_name),
                                        selection_reason="claude_tool_input",
                                        observed_by="claude_hook",
                                        ts=ts,
                                    )
                                    for path in extract_tool_paths(tool_name, tool_input)
                                ],
                                "content_recorded": False,
                            }
                        )
        return events, last_request_id
