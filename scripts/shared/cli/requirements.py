"""Requirements-file parsing and governed question persistence."""

from pathlib import Path
import re

from shared.cli.result import CommandResult

FIELD = re.compile(r"<!--\s*field:\s*([a-z0-9_]+)\s*;\s*required:\s*(true|false)\s*-->", re.I)
ANSWER = re.compile(r"^\[Resposta\]:\s*(.*)$", re.I)
OPTION = re.compile(r"^-\s+([A-Z])\)\s+(.+)$", re.I)
CHECK_OPTION = re.compile(r"^-\s+\[([ xX])\]\s+(.+)$")


def parse(path):
    path = Path(path)
    values, required, choices, checked = {}, [], {}, {}
    current = None
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        marker = FIELD.search(line)
        if marker:
            current = marker.group(1).lower()
            choices[current] = {}
            checked[current] = []
            if marker.group(2).lower() == "true":
                required.append(current)
            continue
        option = OPTION.match(line.strip())
        if option and current:
            label = re.sub(r"\s*\(Recomendada\)\s*", "", option.group(2), flags=re.I).strip()
            choices[current][option.group(1).upper()] = label
            continue
        checkbox = CHECK_OPTION.match(line.strip())
        if checkbox and current:
            label = re.sub(r"\s*\(Recomendada\)\s*", "", checkbox.group(2), flags=re.I).strip()
            if checkbox.group(1).lower() == "x":
                checked[current].append(label)
            continue
        answer = ANSWER.match(line.strip())
        if answer and current:
            raw = answer.group(1).strip()
            selected = [item.strip().upper() for item in re.split(r"[,;+]", raw)]
            if raw and all(item in choices[current] for item in selected):
                values[current] = "; ".join(choices[current][item] for item in selected)
            elif not raw and checked[current]:
                values[current] = "; ".join(checked[current])
            else:
                values[current] = raw
            current = None
    missing = [name for name in required if not values.get(name)]
    return values, required, missing


def resolve_path(*, draft="", state=""):
    if draft:
        return Path(draft) / "01-inception" / "003-requirements.md"
    if state:
        return Path(state).resolve().parent / "01-inception" / "003-requirements.md"
    raise ValueError("informe --draft ou --state")


def status(path):
    path = Path(path)
    if not path.exists():
        return CommandResult("requirements status", "blocked", message=f"Requirements nao encontrado: {path}")
    values, required, missing = parse(path)
    state = "blocked" if missing else "ok"
    message = f"Requirements: {len(required) - len(missing)}/{len(required)} respostas obrigatorias preenchidas."
    return CommandResult("requirements status", state, message=message, data={
        "path": str(path), "answered": sorted(values), "missing": missing, "semantic_review_required": not missing,
    }, next_steps=[f"Preencha as respostas em {path}" if missing else "Revise semanticamente e execute demand start --draft."])


def append_question(path, question, field_name, options=None, recommended="", multiple=False):
    path = Path(path)
    safe = re.sub(r"[^a-z0-9_]+", "_", field_name.lower()).strip("_")
    text = path.read_text(encoding="utf-8")
    if f"field: {safe};" in text:
        return False
    with path.open("a", encoding="utf-8") as handle:
        handle.write(f"\n### {question} <!-- field: {safe}; required: true -->\n")
        if options:
            handle.write("[Alternativas]:\n")
            for index, option in enumerate(options):
                letter = chr(65 + index)
                is_recommended = (recommended.upper() == letter or recommended == option) if recommended else index == 0
                marker = " (Recomendada)" if is_recommended else ""
                prefix = "[ ]" if multiple else f"{letter})"
                handle.write(f"- {prefix} {option}{marker}\n")
        handle.write("[Resposta]:\n")
    return True
