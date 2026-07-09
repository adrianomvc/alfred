#!/usr/bin/env python3
"""Validate Alfred's JIT tool discovery guardrails."""

import argparse
import importlib.util
import re
from pathlib import Path


MAX_TOOLS_PER_ADAPTER = 8
MAX_TOOL_DESCRIPTION_WORDS = 60
MAX_PROPERTY_DESCRIPTION_WORDS = 24


def read(path):
    return Path(path).read_text(encoding="utf-8-sig")


def require_text(path, expected):
    content = read(path)
    if expected not in content:
        raise SystemExit(f"Missing required text in {path}: {expected}")
    print(f"OK text {path} / {expected}")


def word_count(value):
    return len(re.findall(r"\S+", str(value or "")))


def load_email_tools(root):
    script = root / "scripts/python/adapters/mcp-email-server.py"
    spec = importlib.util.spec_from_file_location("mcp_email_server", script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.TOOLS


def validate_tool_descriptions(root):
    tools = load_email_tools(root)
    if len(tools) > MAX_TOOLS_PER_ADAPTER:
        raise SystemExit(
            f"Too many MCP tools in mcp-email-server.py: {len(tools)} > {MAX_TOOLS_PER_ADAPTER}. "
            "Split or discover tools JIT instead of exposing a broad surface."
        )

    for tool in tools:
        name = tool.get("name", "<unnamed>")
        description_words = word_count(tool.get("description", ""))
        if description_words > MAX_TOOL_DESCRIPTION_WORDS:
            raise SystemExit(
                f"Tool description too long for {name}: "
                f"{description_words} > {MAX_TOOL_DESCRIPTION_WORDS} words"
            )

        properties = tool.get("inputSchema", {}).get("properties", {})
        for prop_name, schema in properties.items():
            prop_words = word_count(schema.get("description", ""))
            if prop_words > MAX_PROPERTY_DESCRIPTION_WORDS:
                raise SystemExit(
                    f"Property description too long for {name}.{prop_name}: "
                    f"{prop_words} > {MAX_PROPERTY_DESCRIPTION_WORDS} words"
                )
    print(f"OK MCP tool descriptions {len(tools)} tools")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", "-Root", dest="root", default=".")
    args = parser.parse_args()
    root = Path(args.root).resolve()

    require_text(root / "rules/common/tool-discovery-policy.md", "Do not load every skill")
    require_text(root / "rules/README.md", "tool-discovery-policy")
    require_text(root / "connectors/connectors.md", "## Tool discovery / JIT tools")
    require_text(root / "hosts/_template/shim.md", "## JIT tools")

    for rel in [
        "hosts/devin-cli/SKILL.md",
        "hosts/claude-code/SKILL.md",
        "hosts/codex/AGENTS.md",
        "hosts/github-copilot/copilot-instructions.md",
    ]:
        require_text(root / rel, "## JIT tools")
        require_text(root / rel, "tool-discovery-policy.md")

    validate_tool_descriptions(root)
    print("Tool discovery policy validation completed.")


if __name__ == "__main__":
    main()
