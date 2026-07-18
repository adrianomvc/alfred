#!/usr/bin/env python3
"""Gate: each scenario's estimated context must stay within its budget.

Reads `metrics/context-budgets.json`, rebuilds each scenario's JIT manifest, and
fails if the estimated tokens exceed `max_estimated_tokens`. This is the
regression guard the earlier string-only token validator could not provide: it
checks cost, not wording. Estimate method is chars/4 (see context_budget.py).
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from shared.context_budget import measure_scenario  # noqa: E402
from shared.context_manifest import ContextManifestError  # noqa: E402


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", "-Root", dest="root", default=".")
    args = parser.parse_args()
    root = Path(args.root).resolve()

    path = root / "metrics" / "context-budgets.json"
    if not path.exists():
        raise SystemExit(f"Missing budgets file: {path}")
    budgets = json.loads(path.read_text(encoding="utf-8"))

    errors = []
    for name, spec in budgets.get("scenarios", {}).items():
        cap = spec.get("max_estimated_tokens")
        baseline = spec.get("baseline_estimated_tokens")
        growth = spec.get("max_growth_percent")
        if not cap:
            errors.append(f"{name}: no max_estimated_tokens set")
            continue
        if not baseline or growth is None:
            errors.append(f"{name}: baseline_estimated_tokens and max_growth_percent are required")
            continue
        try:
            estimated, _ = measure_scenario(root, spec["params"])
        except ContextManifestError as exc:
            errors.append(f"{name}: {exc}")
            continue
        if estimated > cap:
            errors.append(
                f"{name}: estimated {estimated} tk exceeds budget {cap} tk. "
                "Reduce the scenario's context or raise the budget with an owner decision."
            )
        growth_cap = round(baseline * (1 + growth / 100))
        if estimated > growth_cap:
            errors.append(
                f"{name}: estimated {estimated} tk exceeds growth cap {growth_cap} tk "
                f"(baseline {baseline}, max growth {growth}%)."
            )
        else:
            print(f"OK budget {name}: {estimated} <= {cap} tk")

    if errors:
        for message in errors:
            print(f"ERROR {message}", file=sys.stderr)
        raise SystemExit(f"Context budget validation failed: {len(errors)} error(s)")
    print("Context budget validation completed.")


if __name__ == "__main__":
    main()
