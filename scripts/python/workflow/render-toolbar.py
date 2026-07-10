#!/usr/bin/env python3
"""Render the Alfred process toolbar from a demand state file."""

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from _common import get_field, read_lines  # noqa: E402


def get_first_field(lines, names):
    return get_field(lines, names)


def get_checklist_status(lines, phase):
    pattern = re.compile(r"^\s*-\s+\[(x|X| )\]\s+" + re.escape(phase) + r"\b")
    for line in lines:
        match = pattern.match(line)
        if match:
            return match.group(1)
    return " "


def shorten(value, maximum=64):
    if value is None:
        return ""
    if len(value) <= maximum:
        return value
    return value[: maximum - 3] + "..."


# --- shared vocabulary ---
_ESC = "\033"
_LANE_COLOR = {"fast": "32", "standard": "33", "safe": "31"}   # green / amber / red
_LANE_ICON = {"fast": "🟢", "standard": "🟡", "safe": "🔴"}
_ALIAS_TEXT = {"Inception": "O que", "Design": "Como", "Execution": "Fazer",
               "Validate": "Validar", "Operation": "Operar"}
_ALIAS_RICH = {"Inception": "O quê", "Design": "Como", "Execution": "Fazer",
               "Validate": "Validar", "Operation": "Operar"}
_STATUS_TEXT = {"x": "ok", ">": "agora", " ": "pendente"}
_STATUS_RICH = {"x": "✓", ">": "▶", " ": "○"}
_RICH_WIDTH = 72


def _c(code, s):
    return f"{_ESC}[{code}m{s}{_ESC}[0m"


def _box_top(width=_RICH_WIDTH):
    return "╭" + "─" * (width - 2) + "╮"


def _box_sep(width=_RICH_WIDTH):
    return "├" + "─" * (width - 2) + "┤"


def _box_bottom(width=_RICH_WIDTH):
    return "╰" + "─" * (width - 2) + "╯"


def _box_line(text="", width=_RICH_WIDTH):
    inner = width - 4
    text = shorten(str(text), inner)
    return "│ " + text.ljust(inner) + " │"


def _rich_bar(progress):
    filled = round(progress / 10)
    return "█" * filled + "░" * (10 - filled)


def forecast_total(cost_usd, progress):
    """Linear extrapolation of the total demand cost from recorded cost + progress.

    Estimate, never a fact: labeled with '~' and omitted whenever the recorded
    cost is not numeric or progress is 0/100 (no inventing — supreme law)."""
    try:
        value = float(str(cost_usd).replace(",", "."))
    except (TypeError, ValueError):
        return ""
    if value <= 0 or progress <= 0 or progress >= 100:
        return ""
    return f"~US$ {value * 100.0 / progress:.2f}"


def format_cost_usd(cost_usd):
    try:
        value = float(str(cost_usd).replace(",", "."))
    except (TypeError, ValueError):
        return ""
    if value <= 0:
        return ""
    return f"US$ {value:.2f}"


def normalize_cost(cost, cost_usd="", usage_cost=""):
    cost_text = str(cost or "").strip()
    missing = {"", "n/a", "na", "none", "unknown", "not collected",
               "nao coletado", "não coletado", "not available"}
    if cost_text.lower() not in missing:
        return cost_text

    numeric = format_cost_usd(cost_usd)
    if numeric:
        return numeric

    usage = str(usage_cost or "").strip()
    if usage:
        return shorten(f"nao coletado ({usage})", 42)
    return "nao coletado"


def _render_rich(sigla, demand_id, lane, phase, nxt, checkpoint,
                 model, cost, progress, markers, forecast):
    icon = _LANE_ICON.get(lane.lower(), "⚪")
    track = " · ".join(
        _ALIAS_RICH.get(name, name)
        + " " + _STATUS_RICH.get(m, "·")
        for name, m in markers[:5]
    )
    cost_part = f"Custo: {cost}" + (f" · previsão total: {forecast}" if forecast else "")
    lines = [
        _box_top(),
        _box_line(f"🎩  A L F R E D · {sigla} · #{demand_id} · {icon} {lane.upper()}"),
        _box_sep(),
        _box_line(f"Progresso: {progress}%  {_rich_bar(progress)}"),
        _box_line(cost_part),
    ]
    if lane.lower() != "fast":
        lines.append(_box_line(f"Fases: {track}"))
        lines.append(_box_line(f"HITL: {shorten(checkpoint, 36)} · Modelo: {model}"))
    else:
        alias = _ALIAS_RICH.get(phase, phase)
        lines.append(_box_line(f"Fase: {alias} · Modelo: {model}"))
    return [
        *lines,
        _box_line(f"Próximo: {nxt}"),
        _box_bottom(),
    ]


# --- web profile (optional): self-contained SVG of the state, helper-rendered ---
_WEB_LANE = {
    "fast": ("#eaf6e9", "#2f6b1f", "#639922"),
    "standard": ("#fdf3df", "#8a5a08", "#ba7517"),
    "safe": ("#fbe9e9", "#a32d2d", "#e24b4a"),
}


def _esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def _render_web(sigla, demand_id, lane, nxt, step, progress, markers):
    fill, txt, bar = _WEB_LANE.get(lane.lower(), ("#eef0f2", "#444", "#888"))
    bar_w = round(360 * progress / 100)
    circles = []
    cx = [44, 138, 232, 326, 420]
    for i, (_, m) in enumerate(markers[:5]):
        if m == "x":
            cf, cs, ct, lbl = "#eaf6e9", "#639922", "#2f6b1f", "✓"
        elif m == ">":
            cf, cs, ct, lbl = "#e6f1fb", "#378add", "#185fa5", str(i + 1)
        else:
            cf, cs, ct, lbl = "#f1f3f5", "#d0d7de", "#8a8f98", str(i + 1)
        circles.append(
            f'<circle cx="{cx[i]}" cy="86" r="13" fill="{cf}" stroke="{cs}"/>'
            f'<text x="{cx[i]}" y="91" text-anchor="middle" font-size="13" fill="{ct}">{lbl}</text>'
        )
    conns = "".join(
        f'<line x1="{cx[i]+14}" y1="86" x2="{cx[i+1]-14}" y2="86" stroke="#d0d7de"/>'
        for i in range(4)
    )
    return ['<svg width="520" viewBox="0 0 520 132" role="img" '
            'font-family="-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif" '
            'xmlns="http://www.w3.org/2000/svg">'
            f'<title>Alfred · {_esc(sigla)} · {_esc(demand_id)}</title>'
            '<rect x="0.5" y="0.5" width="519" height="131" rx="12" fill="#ffffff" stroke="#e1e4e8"/>'
            f'<text x="20" y="30" font-size="14" fill="#24292f"><tspan font-weight="600">ALFRED</tspan>'
            f'<tspan fill="#57606a">  ·  SIGLA:{_esc(sigla)} · #{_esc(demand_id)}</tspan></text>'
            f'<rect x="416" y="16" width="88" height="22" rx="6" fill="{fill}"/>'
            f'<text x="460" y="31" text-anchor="middle" font-size="12" font-weight="600" fill="{txt}">{_esc(lane.upper())}</text>'
            '<rect x="20" y="50" width="360" height="8" rx="4" fill="#e1e4e8"/>'
            f'<rect x="20" y="50" width="{bar_w}" height="8" rx="4" fill="{bar}"/>'
            f'<text x="392" y="58" font-size="12" fill="#57606a">{progress}%</text>'
            f'{conns}{"".join(circles)}'
            f'<text x="20" y="120" font-size="12" fill="#57606a">→ {_esc(shorten(nxt, 72))}</text>'
            '</svg>']


def render(state_path, model="default", cost="n/a", profile="rich", cost_usd=""):
    if not Path(state_path).exists():
        raise SystemExit(f"State file not found: {state_path}")

    content = read_lines(state_path)

    demand_id = get_field(content, "id") or "unknown"
    sigla = get_field(content, "sigla") or "unknown"
    lane = get_first_field(content, ["lane", "modo"]) or "unknown"
    phase = get_first_field(content, ["current phase", "fase atual"]) or "unknown"
    step = get_first_field(content, ["current step", "etapa atual"]) or "unknown"
    nxt = get_first_field(content, ["next step", "proximo passo", "próximo passo"]) or "unknown"
    checkpoint = get_field(content, "checkpoint") or "n/a"
    usage_cost = get_first_field(content, ["usage-cost", "usage cost", "custo", "cost"])

    time_mode = get_first_field(content, ["tempo", "time mode"])
    checklist_text = "\n".join(
        line for line in content if re.match(r"^\s*-\s+\[[xX ]\]", line)
    )
    is_execution_first = (
        "execution-first" in phase.lower()
        or "execution-first" in time_mode.lower()
        or "execution-first stabilization" in checklist_text.lower()
    )

    if is_execution_first:
        phases = [
            "Execution-first stabilization",
            "Inception posterior",
            "Design posterior",
            "Validate posterior",
            "Operation / post-mortem",
        ]
    else:
        phases = ["Inception", "Design", "Execution", "Validate", "Operation"]

    completed = 0
    phase_parts = []
    markers = []
    for item in phases:
        status = get_checklist_status(content, item)
        if status in ("x", "X"):
            completed += 1
            marker = "x"
        elif item.lower() == phase.lower():
            marker = ">"
        else:
            marker = " "
        phase_parts.append(f"{item} [{marker}]")
        markers.append((item, marker))

    progress = min(100, round((completed / 5) * 100))
    forecast = forecast_total(cost_usd, progress)
    cost_display = normalize_cost(cost, cost_usd, usage_cost)

    if profile == "rich":
        return _render_rich(sigla, demand_id, lane, phase, nxt,
                            checkpoint, model, cost_display, progress, markers, forecast)
    if profile == "web":
        return _render_web(sigla, demand_id, lane, nxt, step, progress, markers)

    # text floor: ASCII fallback (no Unicode dependency; degrades anywhere)
    forecast_part = f" | est. total: {forecast}" if forecast else ""
    cost_part = f"custo: {cost_display}{forecast_part}"
    if lane.lower() == "fast":
        return [
            f"ALFRED | {sigla} | #{demand_id} | FAST | {phase} | {progress}% | "
            f"{cost_part} | modelo: {model} | proximo: {shorten(nxt, 48)}"
        ]

    track = " | ".join(
        f"{_ALIAS_TEXT.get(name, name)}:{_STATUS_TEXT.get(m, 'pendente')}" for name, m in markers[:5]
    )
    return [
        f"ALFRED | {sigla} | #{demand_id} | {lane.upper()} | {progress}% | {cost_part}",
        f"Fases: {track}",
        f"HITL: {shorten(checkpoint, 52)} | modelo: {model} | etapa: {shorten(step, 44)}",
        f"Proximo: {shorten(nxt, 76)}",
    ]


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
    parser.add_argument("--cost-usd", "-CostUsd", dest="cost_usd", default="",
                        help="numeric cost so far (USD); enables the linear total-cost forecast")
    args = parser.parse_args()

    for line in render(args.state_path, args.model, args.cost, args.profile, args.cost_usd):
        print(line)


if __name__ == "__main__":
    main()
