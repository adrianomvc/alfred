import unicodedata

from shared.toolbar.presenter import ToolbarViewModel


LANE_ICON = {"fast": "🟢", "standard": "🟡", "safe": "🔴"}
ALIAS_TEXT = {
    "Inception": "1 Inception",
    "Design": "2 Design",
    "Execution": "3 Execution",
    "Validate": "4 Validate",
    "Operation": "5 Operation",
}
ALIAS_RICH = {
    "Inception": "1 Inception",
    "Design": "2 Design",
    "Execution": "3 Execution",
    "Validate": "4 Validate",
    "Operation": "5 Operation",
}
STATUS_TEXT = {"x": "ok", ">": "agora", " ": "pendente"}
STATUS_RICH = {"x": "✅", ">": "▶", " ": "○"}
RICH_WIDTH = 92
WEB_LANE = {
    "fast": ("#eaf6e9", "#2f6b1f", "#639922"),
    "standard": ("#fdf3df", "#8a5a08", "#ba7517"),
    "safe": ("#fbe9e9", "#a32d2d", "#e24b4a"),
}


def shorten(value, maximum=64):
    if value is None:
        return ""
    if len(value) <= maximum:
        return value
    return value[: maximum - 3] + "..."


def display_width(text):
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


def shorten_display(text, maximum):
    text = str(text)
    if display_width(text) <= maximum:
        return text
    result = ""
    for char in text:
        next_result = result + char
        if display_width(next_result + "...") > maximum:
            break
        result = next_result
    return result + "..."


def pad_display(text, width):
    text = shorten_display(text, width)
    return text + " " * max(0, width - display_width(text))


def box_top(title="", width=RICH_WIDTH):
    if not title:
        return "╭" + "─" * (width - 2) + "╮"
    prefix = f"╭─ {title} "
    fill = max(0, width - display_width(prefix) - 1)
    return prefix + "─" * fill + "╮"


def box_sep(width=RICH_WIDTH):
    return "├" + "─" * (width - 2) + "┤"


def box_bottom(width=RICH_WIDTH):
    return "╰" + "─" * (width - 2) + "╯"


def box_line(text="", width=RICH_WIDTH):
    inner = width - 4
    return "│ " + pad_display(str(text), inner) + " │"


def rich_bar(progress):
    filled = round(progress / 10)
    return "▰" * filled + "▱" * (10 - filled)


def cost_line(view_model: ToolbarViewModel):
    if view_model.demand_cost_text:
        return f"Custo demanda: {view_model.demand_cost_text}"
    if view_model.session_cost_text:
        return f"Custo: {view_model.session_cost_text}"
    return f"Custo USD: indisponível · {view_model.cost_gap_text or 'fonte não configurada'}"


def usage_line(view_model: ToolbarViewModel):
    label = "Consumo" if (
        "ACU" in view_model.primary_usage_text
        or "crédito" in view_model.primary_usage_text
        or view_model.primary_usage_text.startswith("não coletado")
    ) else "Uso"
    return f"{label}: {view_model.primary_usage_text}"


def render_rich(sigla, demand_id, lane, phase, nxt, checkpoint, model, progress, markers, framework, app_commit, view_model):
    icon = LANE_ICON.get(lane.lower(), "⚪")
    track = " · ".join(
        ALIAS_RICH.get(name, name)
        + " " + STATUS_RICH.get(m, "·")
        for name, m in markers[:5]
    )
    title = f"🎩 ALFRED · {sigla} · #{demand_id}"
    summary = f"Modo: {icon} {lane.upper()}   Progresso: {progress}%  {rich_bar(progress)}"
    lines = [
        box_top(title),
        box_line(summary),
        box_line(cost_line(view_model)),
        box_line(usage_line(view_model)),
    ]
    if view_model.forecast_text:
        lines.append(box_line(f"Previsão demanda: {view_model.forecast_text}"))
    lines.append(box_line(f"Framework: {framework}        App: {app_commit}"))
    lines.append(box_sep())
    if lane.lower() != "fast":
        lines.append(box_line(track))
        # HITL and Modelo share one line only when both fit whole. The old fixed
        # 30-char cut plus an unbounded model string overflowed the box, and the
        # tail it dropped was the model's own "nao confirmado" qualifier — the
        # truncation turned an honest hedge into an apparent claim. Splitting
        # keeps both readable instead.
        hitl_text = f"HITL: {checkpoint}"
        model_text = f"Modelo: {model}"
        inner = RICH_WIDTH - 4
        if display_width(hitl_text) + 3 + display_width(model_text) <= inner:
            lines.append(box_line(f"{hitl_text}   {model_text}"))
        else:
            lines.append(box_line(shorten_display(hitl_text, inner)))
            lines.append(box_line(shorten_display(model_text, inner)))
    else:
        alias = ALIAS_RICH.get(phase, phase)
        lines.append(box_line(f"Fase: {alias} · Modelo: {model}"))
    return [
        *lines,
        box_line(f"Próximo: {nxt}"),
        box_bottom(),
    ]


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def render_web(sigla, demand_id, lane, nxt, step, progress, markers):
    fill, txt, bar = WEB_LANE.get(lane.lower(), ("#eef0f2", "#444", "#888"))
    bar_w = round(360 * progress / 100)
    circles = []
    cx = [44, 138, 232, 326, 420]
    for i, (_, marker) in enumerate(markers[:5]):
        if marker == "x":
            cf, cs, ct, lbl = "#eaf6e9", "#639922", "#2f6b1f", "✓"
        elif marker == ">":
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
            f'<title>Alfred · {esc(sigla)} · {esc(demand_id)}</title>'
            '<rect x="0.5" y="0.5" width="519" height="131" rx="12" fill="#ffffff" stroke="#e1e4e8"/>'
            f'<text x="20" y="30" font-size="14" fill="#24292f"><tspan font-weight="600">ALFRED</tspan>'
            f'<tspan fill="#57606a">  ·  SIGLA:{esc(sigla)} · #{esc(demand_id)}</tspan></text>'
            f'<rect x="416" y="16" width="88" height="22" rx="6" fill="{fill}"/>'
            f'<text x="460" y="31" text-anchor="middle" font-size="12" font-weight="600" fill="{txt}">{esc(lane.upper())}</text>'
            '<rect x="20" y="50" width="360" height="8" rx="4" fill="#e1e4e8"/>'
            f'<rect x="20" y="50" width="{bar_w}" height="8" rx="4" fill="{bar}"/>'
            f'<text x="392" y="58" font-size="12" fill="#57606a">{progress}%</text>'
            f'{conns}{"".join(circles)}'
            f'<text x="20" y="120" font-size="12" fill="#57606a">→ {esc(shorten(nxt, 72))}</text>'
            '</svg>']


def render_text(sigla, demand_id, lane, phase, nxt, step, checkpoint, model, progress, markers, framework, app_commit, view_model):
    forecast_part = f" | est. demanda: {view_model.forecast_text}" if view_model.forecast_text else ""
    cost_part = f"{cost_line(view_model)}{forecast_part} | {usage_line(view_model)}"
    if lane.lower() == "fast":
        return [
            f"ALFRED | {sigla} | #{demand_id} | FAST | {phase} | {progress}% | "
            f"{cost_part} | modelo: {model} | proximo: {shorten(nxt, 48)}",
            f"Framework: {framework} | App: {app_commit}",
        ]

    track = " | ".join(
        f"{ALIAS_TEXT.get(name, name)}:{STATUS_TEXT.get(marker, 'pendente')}" for name, marker in markers[:5]
    )
    return [
        f"ALFRED | {sigla} | #{demand_id} | {lane.upper()} | {progress}% | {cost_part}",
        f"Framework: {framework} | App: {app_commit}",
        f"Fases: {track}",
        f"HITL: {shorten(checkpoint, 52)} | modelo: {model} | etapa: {shorten(step, 44)}",
        f"Proximo: {shorten(nxt, 76)}",
    ]
