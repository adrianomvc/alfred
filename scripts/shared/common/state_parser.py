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


def _line_key(line):
    stripped = line.strip()
    if not stripped.startswith("- ") or ":" not in stripped:
        return None
    return stripped[2:].split(":", 1)[0].strip().lower()


def find_duplicate_keys(path):
    """Return the state keys that appear on more than one ``- key:`` line."""
    seen, duplicates = set(), set()
    path = Path(path)
    if not path.exists():
        return []
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        key = _line_key(line)
        if key is None:
            continue
        if key in seen:
            duplicates.add(key)
        seen.add(key)
    return sorted(duplicates)


def write_state_fields(path, updates, section="Host Adapters"):
    """Update ``- key: value`` lines in a state file, inserting missing keys.

    A key that already exists anywhere in the file is updated in place at its
    last occurrence (the one last-wins readers observe) and earlier duplicate
    occurrences of that key are removed, so each updated key keeps a single
    source of truth. Keys not present anywhere are appended to the end of
    ``section`` (created if absent). Returns the number of keys written.
    """
    path = Path(path)
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    pending = {key.lower(): (key, value) for key, value in updates.items()}

    last_index = {}
    for index, line in enumerate(lines):
        key = _line_key(line)
        if key in pending:
            last_index[key] = index
    to_insert = {key: pending[key] for key in pending if key not in last_index}

    target = f"## {section}".lower()
    output = []
    in_section = False
    inserted = False

    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("## "):
            if in_section and not inserted:
                for _, (key, value) in list(to_insert.items()):
                    output.append(f"- {key}: {value}")
                inserted = True
            in_section = stripped.lower() == target

        key = _line_key(line)
        if key in last_index:
            if index == last_index[key]:
                original_key, value = pending[key]
                output.append(f"- {original_key}: {value}")
            # earlier duplicates of an updated key are dropped (single source)
            continue

        output.append(line)

    if to_insert and not inserted:
        if not in_section:
            output.extend(["", f"## {section}"])
        for _, (key, value) in list(to_insert.items()):
            output.append(f"- {key}: {value}")

    path.write_text("\n".join(output) + "\n", encoding="utf-8")
    return len(updates)
