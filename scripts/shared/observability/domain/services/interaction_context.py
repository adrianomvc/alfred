"""Derive interaction context/efficiency metrics from host tool observations.

Pure domain service: turns the tool_use/tool_result observations of one
interaction into the ``context`` and tool counters the observability schema
already declares (today emitted as ``null``). Reuses ``classify_artifact`` so the
read breakdown matches the rest of the pipeline. Fields the host does not expose
(byte counts, compression) stay ``None`` rather than being invented.
"""

from .artifact_classifier import classify_artifact

# Host tools that read context (not mutations/execution).
READ_TOOLS = {"Read", "Grep", "Glob", "NotebookRead"}


def _read_path(obs):
    tool = obs.get("tool_name")
    if tool not in READ_TOOLS:
        return None
    data = obs.get("input") or {}
    if not isinstance(data, dict):
        return None
    return data.get("file_path") or data.get("path") or data.get("notebook_path")


def _rtk_used(tool_obs):
    for obs in tool_obs:
        if obs.get("tool_name") != "Bash":
            continue
        command = (obs.get("input") or {}).get("command") if isinstance(obs.get("input"), dict) else None
        if isinstance(command, str) and "rtk" in command:
            return True
    return False


def interaction_context(tool_obs):
    """Return the ``context`` metrics dict for one interaction's tool observations.

    ``tool_obs`` items look like ``{tool_name, is_error, input}``. Unknown/absent
    signals stay ``None`` (never fabricated)."""
    tool_obs = list(tool_obs or [])
    reads = [path for path in (_read_path(obs) for obs in tool_obs) if path]
    unique = list(dict.fromkeys(reads))
    counts = {"framework_rules_read": 0, "skills_loaded": 0, "source_files_read": 0, "logs_read": 0}
    for path in unique:
        artifact_type = classify_artifact(path)
        if artifact_type == "framework_skill":
            counts["skills_loaded"] += 1
        elif artifact_type.startswith("framework_"):
            counts["framework_rules_read"] += 1
        elif artifact_type in ("source_code", "test"):
            counts["source_files_read"] += 1
        elif artifact_type == "log":
            counts["logs_read"] += 1
    return {
        "unique_artifacts_read": len(unique),
        "framework_rules_read": counts["framework_rules_read"],
        "skills_loaded": counts["skills_loaded"],
        "source_files_read": counts["source_files_read"],
        "logs_read": counts["logs_read"],
        "repeated_reads": len(reads) - len(unique),
        "total_bytes_read": None,
        "compression_used": None,
        "rtk_used": _rtk_used(tool_obs),
    }


def tool_counters(tool_obs):
    """Return (tool_call_count, tool_failure_count) for the interaction."""
    tool_obs = list(tool_obs or [])
    failures = sum(1 for obs in tool_obs if obs.get("is_error"))
    return len(tool_obs), failures
