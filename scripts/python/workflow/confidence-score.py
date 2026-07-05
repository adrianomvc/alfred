#!/usr/bin/env python3
"""Pre-Execution confidence score for a demand (W8.1).

Python mirror of ``scripts/powershell/workflow/confidence-score.ps1``. Optional helper (D3).
Composes signals Alfred already records into one number the SDD gate can read:
below the floor, the recommendation is the escalation rule (stop and ask), never
"proceed anyway". The score informs; the human decides.

Signals (penalties):
- unanswered questions in ``01-inception/003-requirements.md`` (-15 each, max -45)
- lane not confirmed by a human in ``01-inception/004-risk.md``           (-20)
- missing Design clarity artifacts for the lane (decisions/plan, Std/SAFE) (-15 each)
- reverse-eng without a recorded app commit (when the app path is given)   (-15)
Verdict: >=80 proceed · 50-79 review with the human · <50 stop and escalate (D27).
"""

import argparse
import re
import sys
from pathlib import Path


def read(path):
    return Path(path).read_text(encoding="utf-8-sig") if Path(path).is_file() else ""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--hub-demand-path", "-HubDemandPath", dest="hub", required=True)
    parser.add_argument("--app-demand-path", "-AppDemandPath", dest="app", default="")
    args = parser.parse_args()
    hub = Path(args.hub)

    score = 100
    reasons = []

    requirements = read(hub / "01-inception/003-requirements.md")
    if requirements:
        unanswered = 0
        for line in requirements.splitlines():
            match = re.match(r"^\s*\[(Resposta|Answer)\]:\s*(.*)$", line, re.IGNORECASE)
            if match and not match.group(2).strip():
                unanswered += 1
        if unanswered:
            penalty = min(unanswered * 15, 45)
            score -= penalty
            reasons.append(f"-{penalty}: {unanswered} unanswered question(s) in requirements")
    else:
        score -= 15
        reasons.append("-15: no requirements artifact (acceptable only in FAST)")

    risk = read(hub / "01-inception/004-risk.md")
    lane = ""
    confirmed = re.search(r"(?im)^-\s*(modo confirmado|confirmed lane)\s*:\s*(.+)$", risk)
    if confirmed and confirmed.group(2).strip().strip("`"):
        lane = confirmed.group(2).strip().strip("`").lower()
    else:
        score -= 20
        reasons.append("-20: lane not confirmed by a human in 004-risk.md")
        proposed = re.search(r"(?im)^-\s*(modo proposto|proposed lane)\s*:\s*(.+)$", risk)
        lane = (proposed.group(2).strip().strip("`").lower() if proposed else "")

    if lane in ("standard", "safe"):
        for rel, label in [("02-design/006-decisions.md", "decisions"),
                           ("03-execution/012-execution-plan.md", "execution plan")]:
            if not (hub / rel).is_file():
                score -= 15
                reasons.append(f"-15: missing {label} for lane {lane}")

    if args.app:
        reverse = read(Path(args.app) / "01-inception/002-reverse-eng.md")
        if not re.search(r"(?im)^-\s*commit\s*:\s*`?\w{7,40}`?", reverse):
            score -= 15
            reasons.append("-15: reverse-eng without a recorded app commit (staleness unknown)")

    score = max(score, 0)
    if score >= 80:
        verdict = "PROCEED (clarity floor met; DoD still applies)"
    elif score >= 50:
        verdict = "REVIEW WITH HUMAN before Execution (clarity gaps above)"
    else:
        verdict = "STOP AND ESCALATE (escalation rule; do not enter Execution)"

    print(f"confidence score: {score}/100 (lane: {lane or 'unknown'})")
    for reason in reasons:
        print("  " + reason)
    print(f"verdict: {verdict}")
    print("note: the score informs; the human decides (human-in-control).")
    return 0 if score >= 80 else 1


if __name__ == "__main__":
    sys.exit(main())
