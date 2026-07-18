"""Markdown-first memory metadata shared by index and query commands."""

import math
from pathlib import Path

REQUIRED = ("id", "type", "title", "trigger", "source-demand", "date")
VALID_TYPES = {"decision", "gotcha"}


def parse_frontmatter(path):
    lines = Path(path).read_text(encoding="utf-8-sig").splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError(f"Missing frontmatter: {path}")
    data = {}
    for line in lines[1:]:
        if line.strip() == "---":
            return data
        if line.strip() and ":" in line:
            key, value = line.split(":", 1)
            data[key.strip().lower()] = value.strip()
    raise ValueError(f"Unclosed frontmatter: {path}")


def load_observations(hub):
    memory_dir = Path(hub) / "memory"
    paths = sorted(memory_dir.glob("*.md")) if memory_dir.exists() else []
    observations = []
    seen = set()
    for path in paths:
        if path.name == "README.md":
            continue
        data = parse_frontmatter(path)
        missing = [key for key in REQUIRED if not data.get(key)]
        if missing:
            raise ValueError(f"{path} missing frontmatter keys: {', '.join(missing)}")
        kind = data["type"].lower()
        if kind not in VALID_TYPES:
            raise ValueError(f"{path} invalid type: {data['type']}")
        if data["id"] in seen:
            raise ValueError(f"Duplicate memory id: {data['id']}")
        seen.add(data["id"])
        data["type"] = kind
        data["path"] = path
        data["estimated_tokens"] = math.ceil(len(path.read_text(encoding="utf-8-sig")) / 4)
        observations.append(data)
    return observations


def escape_cell(value):
    return str(value or "-").replace("|", "\\|").replace("\r", " ").replace("\n", " ")


def searchable_text(observation):
    keys = ("id", "type", "title", "trigger", "tags", "files", "source-demand")
    return " ".join(str(observation.get(key, "")) for key in keys).lower()
