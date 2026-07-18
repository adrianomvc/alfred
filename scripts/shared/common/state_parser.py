"""Demand state Markdown parsing helpers."""

from pathlib import Path


def read_state_fields(path):
    """Parse a state markdown file into a ``{lowercased key: value}`` dict."""
    fields = {}
    path = Path(path) if path else None
    if not path or not path.exists():
        return fields
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        stripped = line.strip()
        if not stripped.startswith("- ") or ":" not in stripped:
            continue
        key, value = stripped[2:].split(":", 1)
        fields[key.strip().lower()] = value.strip()
    return fields


def write_state_fields(path, updates, section="Host Adapters"):
    """Update ``- key: value`` lines in a state file, inserting missing keys.

    An existing key is replaced wherever it appears. Keys not found are appended
    to the end of ``section`` (created if absent). Mirrors the Host Adapters
    updater so several scripts write state the same way. Returns the number of
    keys written.
    """
    path = Path(path)
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    pending = {key.lower(): (key, value) for key, value in updates.items()}
    target = f"## {section}".lower()
    output = []
    in_section = False
    inserted = False

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("## "):
            if in_section and not inserted:
                for _, (key, value) in list(pending.items()):
                    output.append(f"- {key}: {value}")
                inserted = True
            in_section = stripped.lower() == target

        if stripped.startswith("- ") and ":" in stripped:
            key = stripped[2:].split(":", 1)[0].strip().lower()
            if key in pending:
                original_key, value = pending.pop(key)
                output.append(f"- {original_key}: {value}")
                continue

        output.append(line)

    if pending and not inserted:
        if not in_section:
            output.extend(["", f"## {section}"])
        for _, (key, value) in list(pending.items()):
            output.append(f"- {key}: {value}")

    path.write_text("\n".join(output) + "\n", encoding="utf-8")
    return len(updates)
