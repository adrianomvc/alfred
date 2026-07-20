#!/usr/bin/env python3
"""Advisory invariants check (warnings only, always exits 0).

Surfaces drift against two AGENTS.md invariants that have no hard gate:
- "Keep files at ~1 screen" — framework markdown well past one screen;
- "Framework files in English" — pt-BR prose leaking into core/rules text
  (rendered-output examples are allowlisted; generated artifacts are pt-BR by
  design, D47, and are not scanned).

Warnings inform the maintainer; they never fail the canonical gate.
"""

import argparse
import re
import sys
from pathlib import Path

MAX_LINES = 120  # ~1 screen with margin; advisory only
SCAN_DIRS = ["core", "rules", "skills", "connectors", "metrics", "knowledge", "hosts"]
# Files whose body legitimately carries pt-BR: rendered-output examples the
# butler shows humans, and molds for pt-BR content.
PTBR_ALLOWLIST = {
    "core/welcome.md",
    "core/presentation/welcome-screen.md",
    "core/presentation/toolbar.md",
    "core/presentation/toolbar-quick.md",
    "rules/common/question-format.md",
    "rules/common/terminology.md",
    "core/glossary.md",
}
# Common pt-BR words that rarely appear in English prose.
PTBR_WORDS = re.compile(
    r"\b(?:nao|não|voce|você|entao|então|também|porem|porém|obrigatorio|"
    r"obrigatório|responda|preencha|demanda aberta|aguardando|humano responsavel)\b",
    re.IGNORECASE)


def scan(root):
    warnings = []
    for folder in SCAN_DIRS:
        base = root / folder
        if not base.exists():
            continue
        for path in sorted(base.rglob("*.md")):
            rel = path.relative_to(root).as_posix()
            text = path.read_text(encoding="utf-8-sig")
            lines = text.splitlines()
            if len(lines) > MAX_LINES:
                warnings.append(f"WARN one-screen: {rel} has {len(lines)} lines "
                                f"(> {MAX_LINES}); consider splitting (register in the entry index)")
            if rel in PTBR_ALLOWLIST or folder not in ("core", "rules"):
                continue
            hits = []
            in_fence = False
            for line in lines:
                if line.lstrip().startswith("```"):
                    in_fence = not in_fence
                    continue
                if in_fence or line.lstrip().startswith(">"):
                    continue  # fenced blocks/quotes often carry pt-BR output examples
                if PTBR_WORDS.search(line):
                    hits.append(line.strip()[:60])
            if len(hits) >= 3:  # conservative: isolated pt-BR strings are fine
                warnings.append(f"WARN language: {rel} has {len(hits)} pt-BR-looking prose "
                                f"lines (framework files are English; first: {hits[0]!r})")
    return warnings


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", "-Root", dest="root", default=".")
    args = parser.parse_args()
    warnings = scan(Path(args.root).resolve())
    for warning in warnings:
        print(warning)
    print(f"Invariants advisory completed. warnings={len(warnings)} (non-blocking)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
