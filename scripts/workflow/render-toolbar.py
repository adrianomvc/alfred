#!/usr/bin/env python3
"""Render the Alfred process toolbar from a demand state file."""

import argparse
import sys
from pathlib import Path

SCRIPTS_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS_ROOT))
from _common import read_lines  # noqa: E402
from shared.toolbar.active_demand import register_active_demand  # noqa: E402
from shared.toolbar.service import render_toolbar  # noqa: E402

FRAMEWORK_ROOT = Path(__file__).resolve().parents[2]


def render(state_path, model="default", cost="n/a", profile="rich", cost_usd="",
           app_commit="", app_demand_path="", write_usage_summary=False):
    try:
        return render_toolbar(
            state_path,
            framework_root=FRAMEWORK_ROOT,
            model=model,
            cost=cost,
            profile=profile,
            cost_usd=cost_usd,
            app_commit=app_commit,
            app_demand_path=app_demand_path,
            write_usage_summary=write_usage_summary,
        )
    except FileNotFoundError as exc:
        raise SystemExit(str(exc)) from exc


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")   # rich profile uses Unicode
    except Exception:
        pass
    parser = argparse.ArgumentParser(description="Render the Alfred process toolbar.")
    parser.add_argument("--state-path", "-StatePath", dest="state_path", required=True)
    parser.add_argument("--model", "-Model", dest="model", default="default")
    parser.add_argument("--cost", "-Cost", dest="cost", default="n/a")
    parser.add_argument("--profile", "-Profile", dest="profile", default="rich",
                        choices=["text", "rich", "web"])
    parser.add_argument("--allow-text-fallback", "-AllowTextFallback",
                        dest="allow_text_fallback", action="store_true",
                        help="permit --profile text when the host cannot render Unicode/emoji")
    parser.add_argument("--cost-usd", "-CostUsd", dest="cost_usd", default="",
                        help="numeric cost observed so far (USD); forecast still requires demand-scoped cost")
    parser.add_argument("--app-commit", "-AppCommit", dest="app_commit", default="",
                        help="current or recorded app commit to show in the toolbar")
    parser.add_argument("--app-demand-path", "-AppDemandPath", dest="app_demand_path", default="",
                        help="optional app demand artifact path used to read current/captured app commit")
    parser.add_argument("--register-active", "-RegisterActive", dest="register_active", action="store_true",
                        help="record this state as the active demand for host hooks (active-demand.json)")
    parser.add_argument("--write-usage-summary", "-WriteUsageSummary",
                        dest="write_usage_summary", action="store_true",
                        help="persist 001-usage-summary.json while rendering")
    args = parser.parse_args()

    if args.profile == "text" and not args.allow_text_fallback:
        raise SystemExit(
            "--profile text is the degraded fallback. In capable hosts, omit "
            "--profile or use --profile rich. If the host cannot render "
            "Unicode/emoji, rerun with --profile text --allow-text-fallback."
        )

    if args.register_active:
        register_active_demand(args.state_path, read_lines(args.state_path))

    for line in render(args.state_path, args.model, args.cost, args.profile,
                       args.cost_usd, args.app_commit, args.app_demand_path,
                       args.write_usage_summary):
        print(line)


if __name__ == "__main__":
    main()
