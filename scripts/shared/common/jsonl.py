"""JSONL reading helpers."""

import json
from pathlib import Path
from typing import Iterator

from shared.common.text_files import read_lines


def iter_jsonl(path) -> Iterator[tuple[int, object | None, str]]:
    """Yield ``(line_number, parsed_or_None, raw)`` for each non-empty line."""
    line_number = 0
    for raw in read_lines(Path(path)):
        line_number += 1
        if raw.strip() == "":
            continue
        try:
            yield line_number, json.loads(raw), raw
        except json.JSONDecodeError:
            yield line_number, None, raw
