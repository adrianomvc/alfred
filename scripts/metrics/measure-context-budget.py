#!/usr/bin/env python3
"""Measure the estimated context cost of each budgeted scenario.

Reads `metrics/context-budgets.json`, rebuilds each scenario's JIT manifest, and
prints the estimated tokens (chars/4) next to its budget. Advisory by default;
`validate-context-budget.py` is the gate.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from shared.context_budget import measure_scenario  # noqa: E402
from shared.context_manifest import ContextManifestError  # noqa: E402


def load_budgets(root):
    path = Path(root) / "metrics" / "context-budgets.json"
    if not path.exists():
        raise SystemExit(f"Missing budgets file: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", "-Root", dest="root", default=".")
    parser.add_argument("--json", dest="as_json", action="store_true")
    args = parser.parse_args()
    root = Path(args.root).resolve()

    budgets = load_budgets(root)
    results = {}
    for name, spec in budgets.get("scenarios", {}).items():
        try:
            estimated, files = measure_scenario(root, spec["params"])
        except ContextManifestError as exc:
            raise SystemExit(f"{name}: {exc}") from exc
        results[name] = {
            "estimated_tokens": estimated,
            "max_estimated_tokens": spec.get("max_estimated_tokens"),
            "files": len(files),
        }

    if args.as_json:
        print(json.dumps(results, indent=2))
    else:
        for name, r in results.items():
            cap = r["max_estimated_tokens"]
            flag = "" if cap is None or r["estimated_tokens"] <= cap else "  OVER BUDGET"
            print(f"{name}: ~{r['estimated_tokens']} tk (cap {cap}, {r['files']} files){flag}")
    print("Context budget measurement completed.")


if __name__ == "__main__":
    main()
