#!/usr/bin/env python3
"""Validate decision-oriented observability behavior and fixtures."""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PY = sys.executable


def run(args, *, stdin="", env=None, cwd=ROOT, expect=0):
    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)
    result = subprocess.run(
        [PY, *[str(item) for item in args]],
        input=stdin,
        capture_output=True,
        text=True,
        cwd=cwd,
        env=merged_env,
    )
    if result.returncode != expect:
        print(result.stdout)
        print(result.stderr, file=sys.stderr)
        raise SystemExit(f"Command failed ({result.returncode}): {' '.join(map(str, args))}")
    return result


def write_jsonl(path, records):
    Path(path).write_text("\n".join(json.dumps(record, separators=(",", ":")) for record in records) + "\n", encoding="utf-8")


def transcript_record(record_type, ts, **kwargs):
    base = {
        "type": record_type,
        "timestamp": ts,
        "sessionId": "session-fixture",
        "uuid": kwargs.pop("uuid", f"uuid-{ts}"),
        "cwd": "D:/Projetos/alfred",
        "gitBranch": "feature/test",
    }
    base.update(kwargs)
    return base


def user(ts, prompt_id=None, uuid=None):
    return transcript_record(
        "user",
        ts,
        uuid=uuid or f"user-{prompt_id or ts}",
        promptId=prompt_id,
        message={"role": "user", "content": "redacted"},
    )


def assistant(ts, request_id, model="gpt-example", input_tokens=100, output_tokens=20,
              cache_creation=10, cache_read=30, tool=None):
    content = []
    if tool:
        content.append({"type": "tool_use", "id": tool.get("id", "tool-1"), "name": tool["name"], "input": tool.get("input", {})})
    return transcript_record(
        "assistant",
        ts,
        uuid=f"assistant-{request_id}",
        requestId=request_id,
        message={
            "role": "assistant",
            "model": model,
            "content": content,
            "usage": {
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "cache_creation_input_tokens": cache_creation,
                "cache_read_input_tokens": cache_read,
            },
        },
    )


def parse_lines(stdout):
    return [json.loads(line) for line in stdout.splitlines() if line.strip().startswith("{")]


def assert_true(condition, message):
    if not condition:
        raise SystemExit(message)


def validate_transcript_attribution(tmp):
    transcript = tmp / "one.jsonl"
    write_jsonl(transcript, [user("2026-07-12T10:00:00Z", "prompt-1"), assistant("2026-07-12T10:00:01Z", "req-1")])
    result = run([ROOT / "scripts/metrics/attribute-usage-transcript.py", "-TranscriptPath", transcript, "-NoAppend"])
    events = parse_lines(result.stdout)
    assert_true(len(events) == 1, "one request transcript should emit one request usage event")
    event = events[0]
    assert_true(event["event_scope"] == "request", "usage event must be request scoped")
    assert_true(event["request_id"] == "req-1", "request_id must be preserved")
    assert_true(event["interaction_id"] == "prompt-1", "promptId must be used as interaction_id")
    assert_true(event["interaction_confidence"] == "exact", "promptId correlation must be exact")

    multi = tmp / "multi.jsonl"
    write_jsonl(multi, [user("2026-07-12T10:00:00Z", "prompt-2"), assistant("2026-07-12T10:00:01Z", "req-2"), assistant("2026-07-12T10:00:02Z", "req-3")])
    result = run([ROOT / "scripts/metrics/attribute-usage-transcript.py", "-TranscriptPath", multi, "-NoAppend", "-EmitInteractions"])
    events = parse_lines(result.stdout)
    assert_true(sum(1 for e in events if e.get("event_type") == "usage_attributed") == 2, "multi request interaction should emit two request events")
    aggregate = [e for e in events if e.get("event_type") == "interaction_completed"][0]
    assert_true(aggregate["request_count"] == 2, "interaction aggregate must count requests")

    repeated = tmp / "repeated.jsonl"
    write_jsonl(repeated, [user("2026-07-12T10:00:00Z", "prompt-3"), assistant("2026-07-12T10:00:01Z", "req-4", input_tokens=1), assistant("2026-07-12T10:00:02Z", "req-4", input_tokens=9)])
    events = parse_lines(run([ROOT / "scripts/metrics/attribute-usage-transcript.py", "-TranscriptPath", repeated, "-NoAppend"]).stdout)
    assert_true(len(events) == 1 and events[0]["tokens_input"] == 9, "repeated requestId must deduplicate and keep final usage")

    two = tmp / "two.jsonl"
    write_jsonl(two, [user("2026-07-12T10:00:00Z", "prompt-a"), assistant("2026-07-12T10:00:01Z", "req-a"), user("2026-07-12T10:01:00Z", "prompt-b"), assistant("2026-07-12T10:01:01Z", "req-b")])
    events = parse_lines(run([ROOT / "scripts/metrics/attribute-usage-transcript.py", "-TranscriptPath", two, "-NoAppend"]).stdout)
    assert_true({e["interaction_id"] for e in events} == {"prompt-a", "prompt-b"}, "two user prompts must produce two interaction ids")

    no_user = tmp / "nouser.jsonl"
    write_jsonl(no_user, [assistant("2026-07-12T10:00:01Z", "req-no-user")])
    event = parse_lines(run([ROOT / "scripts/metrics/attribute-usage-transcript.py", "-TranscriptPath", no_user, "-NoAppend"]).stdout)[0]
    assert_true(event["interaction_id"] is None and event["interaction_confidence"] == "unavailable", "missing user boundary must not fake interaction id")

    # Interaction telemetry must be populated (not the former all-null block) so
    # the log supports efficiency analysis.
    tooled = tmp / "tooled.jsonl"
    write_jsonl(tooled, [
        user("2026-07-12T10:00:00Z", "prompt-tooled"),
        assistant("2026-07-12T10:00:01Z", "req-tooled", tool={"name": "Read", "input": {"file_path": "rules/common/x.md"}}),
    ])
    events = parse_lines(run([ROOT / "scripts/metrics/attribute-usage-transcript.py", "-TranscriptPath", tooled, "-NoAppend", "-EmitInteractions"]).stdout)
    interaction = [e for e in events if e.get("event_type") == "interaction_completed"][0]
    assert_true(interaction["tool_call_count"] == 1, "interaction must count tool calls")
    assert_true(interaction["context"]["unique_artifacts_read"] == 1, "interaction context must count unique reads")
    assert_true(interaction["context"]["framework_rules_read"] == 1, "interaction context must classify framework reads")


def validate_cursor_and_hook(tmp):
    transcript = tmp / "cursor.jsonl"
    write_jsonl(transcript, [user("2026-07-12T10:00:00Z", "prompt-c"), assistant("2026-07-12T10:00:01Z", "req-c1")])
    cursor = tmp / "cursor.json"
    output = tmp / "obs.jsonl"
    run([ROOT / "scripts/metrics/attribute-usage-transcript.py", "-TranscriptPath", transcript, "-OutputPath", output, "-CursorPath", cursor])
    first_count = len(output.read_text(encoding="utf-8").splitlines())
    run([ROOT / "scripts/metrics/attribute-usage-transcript.py", "-TranscriptPath", transcript, "-OutputPath", output, "-CursorPath", cursor])
    assert_true(len(output.read_text(encoding="utf-8").splitlines()) == first_count, "cursor/idempotence must avoid duplicate requests")

    cursor.write_text("{bad json", encoding="utf-8")
    events = parse_lines(run([ROOT / "scripts/metrics/attribute-usage-transcript.py", "-TranscriptPath", transcript, "-NoAppend", "-CursorPath", cursor, "-NoCursorUpdate"]).stdout)
    assert_true(events, "corrupt cursor must degrade by rereading safely")

    cursor.write_text(json.dumps({"transcript_path": str(transcript.resolve()), "last_byte_offset": 999999}), encoding="utf-8")
    events = parse_lines(run([ROOT / "scripts/metrics/attribute-usage-transcript.py", "-TranscriptPath", transcript, "-NoAppend", "-CursorPath", cursor, "-NoCursorUpdate"]).stdout)
    assert_true(events, "truncated/rotated transcript must reset cursor safely")

    hook = ROOT / "scripts/metrics/claude-code-usage-hook.py"
    run([hook], stdin="{}", expect=0)

    raw_log = tmp / "raw.jsonl"
    run([hook], stdin=json.dumps({"transcript_path": str(transcript)}), env={"AI_OBS_RAW_LOG": str(raw_log), "AI_OBS_MODE": "raw", "AI_OBS_CURSOR_DIR": str(tmp / "raw-cursors")})
    assert_true(raw_log.exists() and raw_log.read_text(encoding="utf-8").strip(), "raw-only hook must write raw log")

    alfred_log = tmp / "alfred.jsonl"
    run([hook], stdin=json.dumps({"transcript_path": str(transcript)}), env={"ALFRED_OBS_LOG": str(alfred_log), "AI_OBS_MODE": "alfred", "AI_OBS_CURSOR_DIR": str(tmp / "alfred-cursors")})
    assert_true(alfred_log.exists() and "usage_attributed" in alfred_log.read_text(encoding="utf-8"), "alfred-only hook must write Alfred log")

    both_raw = tmp / "both-raw.jsonl"
    both_alfred = tmp / "both-alfred.jsonl"
    run([hook], stdin=json.dumps({"transcript_path": str(transcript)}), env={"AI_OBS_RAW_LOG": str(both_raw), "ALFRED_OBS_LOG": str(both_alfred), "AI_OBS_MODE": "both", "AI_OBS_CURSOR_DIR": str(tmp / "both-cursors")})
    assert_true(both_raw.exists() and both_alfred.exists(), "both mode must write raw and Alfred logs")

    before = len(both_alfred.read_text(encoding="utf-8").splitlines())
    run([hook], stdin=json.dumps({"transcript_path": str(transcript)}), env={"AI_OBS_RAW_LOG": str(both_raw), "ALFRED_OBS_LOG": str(both_alfred), "AI_OBS_MODE": "both", "AI_OBS_CURSOR_DIR": str(tmp / "both-cursors")})
    assert_true(len(both_alfred.read_text(encoding="utf-8").splitlines()) == before, "hook cursor must be idempotent")

    # Manual flush fallback: run the transcript attribution directly without a hook event.
    flush = parse_lines(run([ROOT / "scripts/metrics/attribute-usage-transcript.py", "-TranscriptPath", transcript, "-NoAppend"]).stdout)
    assert_true(flush, "manual flush must remain available when SessionEnd is unsupported")


def validate_artifacts_cost_rollup_and_insights(tmp):
    sensitive = tmp / ".env"
    sensitive.write_text("SECRET=redacted\n", encoding="utf-8")
    transcript = tmp / "tools.jsonl"
    write_jsonl(
        transcript,
        [
            user("2026-07-12T10:00:00Z", "prompt-tools"),
            assistant("2026-07-12T10:00:01Z", "req-tool", tool={"name": "Read", "input": {"file_path": str(sensitive)}}),
            assistant("2026-07-12T10:00:02Z", "req-tool-2", tool={"name": "Edit", "input": {"file_path": "src/app.py"}}),
        ],
    )
    raw = tmp / "tool-raw.jsonl"
    run([ROOT / "scripts/metrics/claude-code-usage-hook.py"], stdin=json.dumps({"transcript_path": str(transcript)}), env={"AI_OBS_RAW_LOG": str(raw), "AI_OBS_MODE": "raw", "AI_OBS_CURSOR_DIR": str(tmp / "tool-cursors")})
    raw_events = [json.loads(line) for line in raw.read_text(encoding="utf-8").splitlines()]
    assert_true(any((artifact.get("path_redacted") for event in raw_events for artifact in event.get("artifacts", []))), "sensitive paths must be redacted")
    assert_true(any((artifact.get("operation") == "update" for event in raw_events for artifact in event.get("artifacts", []))), "modified artifact operation must be captured")

    usage_log = tmp / "usage-observability-log.jsonl"
    usage_events = parse_lines(run([ROOT / "scripts/metrics/attribute-usage-transcript.py", "-TranscriptPath", transcript, "-NoAppend"]).stdout)
    write_jsonl(usage_log, usage_events)
    rate_card = ROOT / "examples/connectors/usage-rate-card.json"
    run([ROOT / "scripts/metrics/apply-usage-rate-card.py", "-InputPath", usage_log, "-RateCardPath", rate_card])
    combined = [json.loads(line) for line in usage_log.read_text(encoding="utf-8").splitlines()]
    assert_true(any(e.get("event_type") == "usage_cost_attributed" for e in combined), "rate card must append cost events")

    missing_card = tmp / "missing-rate-card.json"
    missing_card.write_text(
        json.dumps({
            "schema_version": "alfred.usage-rate-card.v1",
            "currency": "USD",
            "source": "missing-model-fixture",
            "approved_by": "Alfred fixture",
            "effective_from": "2026-01-01",
            "confidence": "rated",
            "models": {"other-model": {"input_per_1m": 1, "output_per_1m": 1}},
        }),
        encoding="utf-8",
    )
    missing = run([ROOT / "scripts/metrics/apply-usage-rate-card.py", "-InputPath", usage_log, "-RateCardPath", missing_card, "-NoAppend"], expect=1)
    assert_true("Missing rate card models" in missing.stderr or "Missing rate card models" in missing.stdout, "missing model must fail safely")

    demand = tmp / "demand"
    log_dir = demand / "05-operation"
    log_dir.mkdir(parents=True)
    target_log = log_dir / "011-observability-log.jsonl"
    write_jsonl(
        target_log,
        [
            {
                "schema_version": "alfred.observability.v1",
                "ts": "2026-07-12T10:00:00Z",
                "event_id": "read-1",
                "trace_id": "trace",
                "session_id": "session",
                "interaction_id": "prompt-tools",
                "event_type": "artifact_accessed",
                "phase": "design",
                "lane": "standard",
                "actor_id": "claude_hook",
                "artifacts_used": {"read": ["001-state.md"]},
                "model": "gpt-example",
                "tokens_input": None,
                "tokens_output": None,
                "cost_usd": None,
            },
            *combined,
        ],
    )
    rollup = run([ROOT / "scripts/metrics/generate-metrics-rollup.py", "-Root", demand]).stdout
    assert_true("tokens cache read:" in rollup, "rollup must include cache tokens")
    assert_true("cost events:" in rollup, "rollup must separate cost events")
    assert_true("legacy usage events with inline cost ignored" not in rollup, "new cost events should avoid legacy double count warning")
    assert_true("cache reuse ratio:" in rollup, "rollup must include cache reuse ratio")
    assert_true("`001-state.md`" in rollup, "legacy artifacts_used object must be readable")

    insights = run([ROOT / "scripts/metrics/generate-metrics-insights.py", "-Root", demand]).stdout
    assert_true("Human decision: pending" in insights, "insights must require human decision")
    before = (ROOT / "core/model-policy.md").read_text(encoding="utf-8")
    run([ROOT / "scripts/metrics/generate-metrics-insights.py", "-Root", demand, "-OutputPath", tmp / "insights.md"])
    after = (ROOT / "core/model-policy.md").read_text(encoding="utf-8")
    assert_true(before == after, "insight generator must not alter policies")


def main():
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp = Path(tmp_dir)
        validate_transcript_attribution(tmp)
        validate_cursor_and_hook(tmp)
        validate_artifacts_cost_rollup_and_insights(tmp)
    print("Observability intelligence validation completed.")


if __name__ == "__main__":
    main()
