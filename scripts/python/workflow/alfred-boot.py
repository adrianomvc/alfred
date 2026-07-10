#!/usr/bin/env python3
"""Boot helper: detect the Alfred context and list resumable demands."""

import argparse
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from _common import get_field, read_lines, value_or  # noqa: E402

FRAMEWORK_ROOT = HERE.parent.parent.parent

CLOSED = (
    "closed", "fechado", "fechada", "concluida", "concluída", "done",
    "completed", "finalizada", "finalizado", "cancelada", "cancelado", "cancelled",
)


def load_renderer():
    spec = importlib.util.spec_from_file_location("render_toolbar", HERE / "render-toolbar.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.render


def get_repo_kind(path):
    has_framework = (path / "core/principles.md").exists() and (path / "rules/agents").exists()
    has_hub = (path / "alfred-docs-hub").exists()
    has_app = (path / ".alfred-docs-app").exists()
    if has_framework:
        return "Framework"
    if has_hub and has_app:
        return "HUB+APP"
    if has_hub:
        return "HUB"
    if has_app:
        return "APP-only"
    return "Unknown"


def state_summary(state_file):
    lines = read_lines(state_file)
    return {
        "Path": str(state_file),
        "DemandId": value_or(get_field(lines, ["id"]), "unknown"),
        "InitiativeId": value_or(get_field(lines, ["initiative id", "id iniciativa"]), "unknown"),
        "Sigla": value_or(get_field(lines, ["sigla"]), "unknown"),
        "Lane": value_or(get_field(lines, ["lane", "modo"]), "unknown"),
        "Phase": value_or(get_field(lines, ["current phase", "fase atual"]), "unknown"),
        "Step": value_or(get_field(lines, ["current step", "etapa atual"]), "unknown"),
        "Next": value_or(get_field(lines, ["next step", "proximo passo", "próximo passo"]), "unknown"),
        "Status": value_or(get_field(lines, ["status"]), "unknown"),
        "LastActivity": value_or(get_field(lines, ["last activity", "ultima atividade", "última atividade"]), "unknown"),
    }


def is_open(status):
    return status.lower() not in CLOSED


def resume_priority(state):
    """Lower = suggest first: pending human checkpoint > in progress > blocked."""
    status = state["Status"].lower()
    if "checkpoint" in status or "aguardando" in status:
        return 0
    if "bloquead" in status or "blocked" in status:
        return 2
    return 1


def priority_reason(state):
    return {0: "awaiting a human checkpoint",
            1: "in progress",
            2: "blocked - needs external input"}[resume_priority(state)]


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    parser = argparse.ArgumentParser()
    parser.add_argument("--root", "-Root", dest="root", default=".")
    parser.add_argument("--model", "-Model", dest="model", default="default")
    parser.add_argument("--cost", "-Cost", dest="cost", default="n/a")
    args = parser.parse_args()

    root_path = Path(args.root).resolve()
    kind = get_repo_kind(root_path)

    version = "unknown"
    version_path = FRAMEWORK_ROOT / "VERSION"
    if version_path.exists():
        version = version_path.read_text(encoding="utf-8-sig").splitlines()[0].strip()

    print("ALFRED BOOT")
    print(f"- root: {root_path}")
    print(f"- detected: {kind}")
    print(f"- framework version: {version}")

    search_roots = []
    if (root_path / "alfred-docs-hub").exists():
        search_roots.append(root_path / "alfred-docs-hub")
    if (root_path / ".alfred-docs-app").exists():
        search_roots.append(root_path / ".alfred-docs-app")
    if kind == "Framework" and (root_path / "examples").exists():
        search_roots.append(root_path / "examples")

    if not search_roots:
        print("- open demands: not detected")
        print("- next: ask the human for HUB/App path or start a new demand")
        return

    states = []
    for search_root in search_roots:
        for state_file in sorted(search_root.rglob("001-state.md")):
            states.append(state_summary(state_file))

    if not states:
        print("- open demands: none found")
        print("- next: start a new demand using docs/quickstart-real-demand.md")
        return

    open_states = sorted(
        (s for s in states if is_open(s["Status"])),
        key=lambda s: (resume_priority(s), s["LastActivity"], s["Sigla"], s["InitiativeId"], s["DemandId"]),
    )

    print(f"- states found: {len(states)}")
    print(f"- open demands: {len(open_states)}")

    for state in open_states:
        relative = state["Path"].replace(str(root_path) + "\\", "")
        print(f"  - {state['Sigla']} | {state['InitiativeId']} | {state['DemandId']} | "
              f"{state['Lane']} | {state['Phase']} | {state['Status']} | next: {state['Next']}")
        print(f"    state: {relative}")

    if open_states:
        first = open_states[0]
        print("")
        print(f"Suggested next: {first['DemandId']} ({priority_reason(first)}) - the human chooses; this is only an ordering hint.")
        print("Resume preview:")
        renderer = HERE / "render-toolbar.py"
        if renderer.exists():
            render = load_renderer()
            for line in render(first["Path"], args.model, args.cost):
                print(line)
        else:
            print(f"ALFRED | SIGLA:{first['Sigla']} | #{first['DemandId']} | "
                  f"{first['Lane']} | {first['Phase']} | next: {first['Next']}")
        print("")
        print("Next: choose a demand to resume, start a new demand, or run validate-demand on the selected state folder.")


if __name__ == "__main__":
    main()
