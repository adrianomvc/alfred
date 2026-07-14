from pathlib import Path
from typing import Sequence

from shared.common import read_lines
from shared.toolbar.state import get_first_field


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


def local_framework_value(framework_root, kind):
    if kind == "version":
        version_path = Path(framework_root) / "VERSION"
        if version_path.exists():
            return version_path.read_text(encoding="utf-8-sig").splitlines()[0].strip()
    return "unknown"


def resolve_path(raw, state_path, cwd=None):
    raw = str(raw or "").strip().strip("`")
    if raw == "":
        return None
    candidate = Path(raw)
    if candidate.is_absolute():
        return candidate
    current = Path(cwd).resolve() if cwd else Path.cwd()
    state = Path(state_path).resolve()
    bases = [current, state.parent]
    bases.extend(state.parents)
    for base in bases:
        resolved = (base / raw).resolve()
        if resolved.exists():
            return resolved
    return (current / raw).resolve()


def read_app_commit(state_path, content: Sequence[str], explicit_app_commit="", app_demand_path="", cwd=None):
    if explicit_app_commit:
        return short_commit(explicit_app_commit)

    state_value = get_first_field(content, ["app commit", "current app commit", "captured app commit"])
    if state_value:
        return short_commit(state_value)

    paths = []
    if app_demand_path:
        paths.append(resolve_path(app_demand_path, state_path, cwd=cwd))
    app_artifacts = get_first_field(content, ["app artifacts"])
    if app_artifacts:
        paths.append(resolve_path(app_artifacts, state_path, cwd=cwd))

    for app_path in (path for path in paths if path):
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


def resolve_framework_display(framework_root, stamped_version="", stamped_commit=""):
    if stamped_version or stamped_commit:
        framework_version = stamped_version or "unknown"
        framework_commit = stamped_commit or "unknown"
    else:
        framework_version = local_framework_value(framework_root, "version")
        framework_commit = local_framework_value(framework_root, "commit")
    return format_framework(framework_version, framework_commit)
