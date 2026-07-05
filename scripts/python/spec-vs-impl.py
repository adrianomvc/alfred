#!/usr/bin/env python3
"""Compare spec acceptance criteria against validation evidence (W8.2).

Python mirror of ``scripts/powershell/spec-vs-impl.ps1``. Optional helper (D3).
Heuristic, not a judge: it flags acceptance criteria that have no textual echo in
the validation evidence so the Reviewer/human looks at them — it never approves.

Sources:
- criteria: app spec ``02-design/003-spec.md`` (``## Acceptance criteria`` bullets)
  and/or HUB evidence table rows' first column;
- evidence: HUB ``04-validate/013-validation-evidence.md`` full text.

Exit 0 always unless ``--strict`` and there are uncovered criteria.
"""

import argparse
import re
import sys
from pathlib import Path

STOP = {"a", "o", "os", "as", "de", "do", "da", "dos", "das", "e", "em", "no", "na",
        "com", "para", "the", "of", "and", "to", "in", "is", "are", "be", "por", "um", "uma"}


def tokens(text):
    return {t for t in re.findall(r"[\w.]+", text.lower()) if len(t) > 2 and t not in STOP}


def read(path):
    return Path(path).read_text(encoding="utf-8-sig") if Path(path).is_file() else ""


def criteria_from_spec(spec_text):
    match = re.search(r"(?ims)^##\s+Acceptance criteria\s*$(.*?)(?=^##\s|\Z)", spec_text)
    if not match:
        return []
    return [line.strip("- ").strip() for line in match.group(1).splitlines()
            if line.strip().startswith("-") and len(line.strip()) > 4]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--hub-demand-path", "-HubDemandPath", dest="hub", required=True)
    parser.add_argument("--app-demand-path", "-AppDemandPath", dest="app", default="")
    parser.add_argument("--threshold", "-Threshold", dest="threshold", type=float, default=0.5)
    parser.add_argument("--strict", "-Strict", dest="strict", action="store_true")
    args = parser.parse_args()

    evidence_path = Path(args.hub) / "04-validate/013-validation-evidence.md"
    evidence = read(evidence_path)
    if not evidence:
        print(f"ERROR missing_evidence: {evidence_path} not found or empty")
        return 1

    criteria = []
    if args.app:
        criteria = criteria_from_spec(read(Path(args.app) / "02-design/003-spec.md"))
    if not criteria:
        # fall back to the evidence table's own criteria column (first cell per row)
        for line in evidence.splitlines():
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) >= 2 and cells[0] and not set(cells[0]) <= {"-", " "} \
               and cells[0].lower() not in ("criterio", "criterion"):
                criteria.append(cells[0])
    if not criteria:
        print("ERROR no_criteria: no acceptance criteria found in app spec or evidence table")
        return 1

    evidence_tokens = tokens(evidence)
    uncovered = 0
    for criterion in criteria:
        ctok = tokens(criterion)
        overlap = (len(ctok & evidence_tokens) / len(ctok)) if ctok else 0.0
        if overlap >= args.threshold:
            print(f"OK covered ({overlap:.0%}): {criterion}")
        else:
            uncovered += 1
            print(f"GAP uncovered ({overlap:.0%}): {criterion}")

    print(f"Spec-vs-impl completed. criteria={len(criteria)} uncovered={uncovered} "
          f"threshold={args.threshold:.0%} (heuristic — a human/Reviewer decides)")
    if uncovered and args.strict:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
