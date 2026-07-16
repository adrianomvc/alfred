"""Estimate the context cost of a JIT manifest, reproducibly.

This is a planning estimate, not a host tokenizer: it sums the characters of the
files a `context-manifest` scenario would load and divides by a fixed ratio. It
exists so `metrics/context-budgets.json` can gate regressions (a scenario growing
past its budget), degrading to plain counts on any host (D3).
"""

from pathlib import Path

from shared.common import read_text
from shared.context_manifest import build_manifest

# Documented reproducible ratio. Not a real tokenizer; keep it fixed so budgets
# are comparable across runs. Replace only with an explicit owner decision.
CHARS_PER_TOKEN = 4


def estimate_tokens_for_files(root, files):
    root = Path(root)
    total_chars = 0
    for rel in files:
        total_chars += len(read_text(root / rel))
    return total_chars // CHARS_PER_TOKEN


def measure_scenario(root, params):
    """Return (estimated_tokens, files) for a build_manifest param set."""
    files = build_manifest(root, **params)
    return estimate_tokens_for_files(root, files), files
