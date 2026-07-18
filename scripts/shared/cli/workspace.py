"""Workspace detection and HUB initialization."""

from pathlib import Path
import shutil

from shared.cli.result import CommandResult


def detect(root):
    root = Path(root).expanduser().resolve()
    if (root / "core" / "principles.md").exists() and (root / "rules" / "agents").is_dir():
        return CommandResult("workspace detect", message="Workspace detectado: Framework",
                             data={"kind": "Framework", "root": str(root), "hub": "", "app": ""})
    hub = root if root.name == "alfred-docs-hub" else root / "alfred-docs-hub"
    app = root if root.name == ".alfred-docs-app" else root / ".alfred-docs-app"
    if not hub.is_dir():
        hub = next((parent for parent in root.parents if parent.name == "alfred-docs-hub"), hub)
    if not app.is_dir():
        app = next((parent for parent in root.parents if parent.name == ".alfred-docs-app"), app)
    has_hub, has_app = hub.is_dir(), app.is_dir()
    kind = "HUB+APP" if has_hub and has_app else "HUB" if has_hub else "APP-only" if has_app else "Unknown"
    return CommandResult("workspace detect", message=f"Workspace detectado: {kind}", data={
        "kind": kind, "root": str(root), "hub": str(hub) if has_hub else "", "app": str(app) if has_app else "",
    })


def init_hub(root, framework_root, sigla="", dry_run=False):
    root = Path(root).expanduser().resolve()
    hub = root if root.name == "alfred-docs-hub" else root / "alfred-docs-hub"
    if hub.exists() and (hub / "001-index.md").exists():
        return CommandResult("sigla init", message=f"HUB ja inicializado em {hub}", data={"hub": str(hub)})
    if dry_run:
        return CommandResult("sigla init", message=f"HUB seria criado em {hub}", data={"hub": str(hub), "sigla": sigla})
    hub.mkdir(parents=True, exist_ok=True)
    templates = Path(framework_root) / "templates" / "hub"
    shutil.copyfile(templates / "index.md", hub / "001-index.md")
    shutil.copyfile(templates / "metrics-rollup.md", hub / "002-metrics-rollup.md")
    shutil.copyfile(templates / "insights.md", hub / "003-insights.md")
    (hub / "000-drafts").mkdir(exist_ok=True)
    if sigla:
        text = (hub / "001-index.md").read_text(encoding="utf-8")
        (hub / "001-index.md").write_text(text.replace("<sigla>", sigla), encoding="utf-8")
    return CommandResult("sigla init", changed=True, message=f"HUB criado em {hub}", data={"hub": str(hub), "sigla": sigla})
