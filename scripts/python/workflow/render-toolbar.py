#!/usr/bin/env python3
"""Render the Alfred process toolbar from a demand state file."""

import argparse
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from _common import get_field, read_lines  # noqa: E402

FRAMEWORK_ROOT = Path(__file__).resolve().parents[3]


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
_ALIAS_TEXT = {"Inception": "1 Inception", "Design": "2 Design", "Execution": "3 Execution",
               "Validate": "4 Validate", "Operation": "5 Operation"}
_ALIAS_RICH = {"Inception": "1 Inception", "Design": "2 Design", "Execution": "3 Execution",
               "Validate": "4 Validate", "Operation": "5 Operation"}
_STATUS_TEXT = {"x": "ok", ">": "agora", " ": "pendente"}
_STATUS_RICH = {"x": "✅", ">": "▶", " ": "○"}
_RICH_WIDTH = 92


def _c(code, s):
    return f"{_ESC}[{code}m{s}{_ESC}[0m"


def _display_width(text):
    width = 0
    for char in str(text):
        code = ord(char)
        if unicodedata.combining(char) or 0xFE00 <= code <= 0xFE0F:
            continue
        if unicodedata.east_asian_width(char) in ("F", "W") or 0x1F000 <= code <= 0x1FAFF:
            width += 2
        else:
            width += 1
    return width


def _shorten_display(text, maximum):
    text = str(text)
    if _display_width(text) <= maximum:
        return text
    result = ""
    for char in text:
        next_result = result + char
        if _display_width(next_result + "...") > maximum:
            break
        result = next_result
    return result + "..."


def _pad_display(text, width):
    text = _shorten_display(text, width)
    return text + " " * max(0, width - _display_width(text))


def _box_top(title="", width=_RICH_WIDTH):
    if not title:
        return "╭" + "─" * (width - 2) + "╮"
    prefix = f"╭─ {title} "
    fill = max(0, width - _display_width(prefix) - 1)
    return prefix + "─" * fill + "╮"


def _box_sep(width=_RICH_WIDTH):
    return "├" + "─" * (width - 2) + "┤"


def _box_bottom(width=_RICH_WIDTH):
    return "╰" + "─" * (width - 2) + "╯"


def _box_line(text="", width=_RICH_WIDTH):
    inner = width - 4
    return "│ " + _pad_display(str(text), inner) + " │"


def _rich_bar(progress):
    filled = round(progress / 10)
    return "▰" * filled + "▱" * (10 - filled)


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


def short_commit(value):
    value = str(value or "").strip().strip("`")
    if value == "" or value.lower() in {"unknown", "not-git", "a confirmar", "n/a"}:
        return "unknown"
    return value[:7]


def format_framework(version, commit):
    version = str(version or "unknown").strip().strip("`")
    if version and version != "unknown" and not version.lower().startswith("v"):
        version = f"v{version}"
    return f"{version} ({short_commit(commit)})"


def local_framework_value(kind):
    if kind == "version":
        version_path = FRAMEWORK_ROOT / "VERSION"
        if version_path.exists():
            return version_path.read_text(encoding="utf-8-sig").splitlines()[0].strip()
        return "unknown"
    try:
        result = subprocess.run(
            ["git", "-C", str(FRAMEWORK_ROOT), "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return "unknown"
    if result.returncode != 0:
        return "unknown"
    return result.stdout.strip() or "unknown"


def resolve_path(raw, state_path):
    raw = str(raw or "").strip().strip("`")
    if raw == "":
        return None
    candidate = Path(raw)
    if candidate.is_absolute():
        return candidate
    bases = [Path.cwd(), Path(state_path).resolve().parent]
    bases.extend(Path(state_path).resolve().parents)
    for base in bases:
        resolved = (base / raw).resolve()
        if resolved.exists():
            return resolved
    return (Path.cwd() / raw).resolve()


def read_app_commit(state_path, content, explicit_app_commit="", app_demand_path=""):
    if explicit_app_commit:
        return short_commit(explicit_app_commit)

    state_value = get_first_field(content, ["app commit", "current app commit", "captured app commit"])
    if state_value:
        return short_commit(state_value)

    paths = []
    if app_demand_path:
        paths.append(resolve_path(app_demand_path, state_path))
    app_artifacts = get_first_field(content, ["app artifacts"])
    if app_artifacts:
        paths.append(resolve_path(app_artifacts, state_path))

    for app_path in (p for p in paths if p):
        candidates = [
            app_path / "001-index.md",
            app_path / "01-inception" / "002-reverse-eng.md",
        ]
        for candidate in candidates:
            if candidate.exists():
                lines = read_lines(candidate)
                value = get_first_field(lines, [
                    "current commit", "captured commit", "app commit", "commit",
                ])
                if value:
                    return short_commit(value)

    return "unknown"


def _render_rich(sigla, demand_id, lane, phase, nxt, checkpoint,
                 model, cost, progress, markers, forecast, framework, app_commit):
    icon = _LANE_ICON.get(lane.lower(), "⚪")
    track = " · ".join(
        _ALIAS_RICH.get(name, name)
        + " " + _STATUS_RICH.get(m, "·")
        for name, m in markers[:5]
    )
    title = f"🎩 ALFRED · {sigla} · #{demand_id}"
    summary = f"Modo: {icon} {lane.upper()}   Progresso: {progress}%  {_rich_bar(progress)}   Custo: {cost}"
    lines = [
        _box_top(title),
        _box_line(summary),
    ]
    if forecast:
        lines.append(_box_line(f"Previsão: {forecast}"))
    lines.append(_box_line(f"Framework: {framework}        App: {app_commit}"))
    lines.append(
        _box_sep(),
    )
    if lane.lower() != "fast":
        lines.append(_box_line(track))
        lines.append(_box_line(f"HITL: {shorten(checkpoint, 30)}       Modelo: {model}"))
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


def render(state_path, model="default", cost="n/a", profile="rich", cost_usd="",
           app_commit="", app_demand_path=""):
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
    state_cost_usd = get_first_field(content, ["cost usd", "cost_usd", "custo usd"])
    effective_cost_usd = cost_usd or state_cost_usd or ""
    stamped_framework_version = get_first_field(
        content, ["framework version", "versao framework", "versão framework"]
    )
    stamped_framework_commit = get_first_field(content, ["framework commit"])
    if stamped_framework_version or stamped_framework_commit:
        framework_version = stamped_framework_version or "unknown"
        framework_commit = stamped_framework_commit or "unknown"
    else:
        framework_version = local_framework_value("version")
        framework_commit = local_framework_value("commit")
    framework = format_framework(framework_version, framework_commit)
    app_commit_display = read_app_commit(state_path, content, app_commit, app_demand_path)

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
    forecast = forecast_total(effective_cost_usd, progress)
    cost_display = normalize_cost(cost, effective_cost_usd, usage_cost)

    if profile == "rich":
        return _render_rich(sigla, demand_id, lane, phase, nxt,
                            checkpoint, model, cost_display, progress, markers, forecast,
                            framework, app_commit_display)
    if profile == "web":
        return _render_web(sigla, demand_id, lane, nxt, step, progress, markers)

    # text floor: ASCII fallback (no Unicode dependency; degrades anywhere)
    forecast_part = f" | est. total: {forecast}" if forecast else ""
    cost_part = f"custo: {cost_display}{forecast_part}"
    if lane.lower() == "fast":
        return [
            f"ALFRED | {sigla} | #{demand_id} | FAST | {phase} | {progress}% | "
            f"{cost_part} | modelo: {model} | proximo: {shorten(nxt, 48)}",
            f"Framework: {framework} | App: {app_commit_display}",
        ]

    track = " | ".join(
        f"{_ALIAS_TEXT.get(name, name)}:{_STATUS_TEXT.get(m, 'pendente')}" for name, m in markers[:5]
    )
    return [
        f"ALFRED | {sigla} | #{demand_id} | {lane.upper()} | {progress}% | {cost_part}",
        f"Framework: {framework} | App: {app_commit_display}",
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
    parser.add_argument("--allow-text-fallback", "-AllowTextFallback",
                        dest="allow_text_fallback", action="store_true",
                        help="permit --profile text when the host cannot render Unicode/emoji")
    parser.add_argument("--cost-usd", "-CostUsd", dest="cost_usd", default="",
                        help="numeric cost so far (USD); enables the linear total-cost forecast")
    parser.add_argument("--app-commit", "-AppCommit", dest="app_commit", default="",
                        help="current or recorded app commit to show in the toolbar")
    parser.add_argument("--app-demand-path", "-AppDemandPath", dest="app_demand_path", default="",
                        help="optional app demand artifact path used to read current/captured app commit")
    args = parser.parse_args()

    if args.profile == "text" and not args.allow_text_fallback:
        raise SystemExit(
            "--profile text is the degraded fallback. In capable hosts, omit "
            "--profile or use --profile rich. If the host cannot render "
            "Unicode/emoji, rerun with --profile text --allow-text-fallback."
        )

    for line in render(args.state_path, args.model, args.cost, args.profile,
                       args.cost_usd, args.app_commit, args.app_demand_path):
        print(line)


if __name__ == "__main__":
    main()
