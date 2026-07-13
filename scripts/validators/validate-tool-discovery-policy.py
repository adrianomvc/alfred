#!/usr/bin/env python3
"""Validate Alfred's JIT tool discovery guardrails."""

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from shared.email_tools import TOOLS  # noqa: E402
from shared.validation import Severity, ValidationIssue, ValidationReport  # noqa: E402

MAX_TOOLS_PER_ADAPTER = 8
MAX_TOOL_DESCRIPTION_WORDS = 60
MAX_PROPERTY_DESCRIPTION_WORDS = 24


def read(path):
    return Path(path).read_text(encoding="utf-8-sig")


def issue(code, message, path=None):
    return ValidationIssue(
        code=code,
        severity=Severity.ERROR,
        message=message,
        path=None if path is None else str(path),
    )


def require_text(path, expected, issues, successes):
    content = read(path)
    if expected not in content:
        issues.append(issue(
            "tool_discovery.text_missing",
            f"Missing required text in {path}: {expected}",
            path,
        ))
        return
    successes.append(f"OK text {path} / {expected}")


def word_count(value):
    return len(re.findall(r"\S+", str(value or "")))


def validate_tool_descriptions(tools, issues, successes):
    if len(tools) > MAX_TOOLS_PER_ADAPTER:
        issues.append(issue(
            "tool_discovery.too_many_tools",
            f"Too many MCP tools in mcp-email-server.py: {len(tools)} > {MAX_TOOLS_PER_ADAPTER}. "
            "Split or discover tools JIT instead of exposing a broad surface.",
        ))

    for tool in tools:
        name = tool.get("name", "<unnamed>")
        description_words = word_count(tool.get("description", ""))
        if description_words > MAX_TOOL_DESCRIPTION_WORDS:
            issues.append(issue(
                "tool_discovery.tool_description_too_long",
                f"Tool description too long for {name}: "
                f"{description_words} > {MAX_TOOL_DESCRIPTION_WORDS} words",
            ))

        properties = tool.get("inputSchema", {}).get("properties", {})
        for prop_name, schema in properties.items():
            prop_words = word_count(schema.get("description", ""))
            if prop_words > MAX_PROPERTY_DESCRIPTION_WORDS:
                issues.append(issue(
                    "tool_discovery.property_description_too_long",
                    f"Property description too long for {name}.{prop_name}: "
                    f"{prop_words} > {MAX_PROPERTY_DESCRIPTION_WORDS} words",
                ))
    successes.append(f"OK MCP tool descriptions {len(tools)} tools")


def validate_tool_discovery_policy(root) -> ValidationReport:
    root = Path(root).resolve()
    issues = []
    successes = []

    require_text(root / "rules/common/tool-discovery-policy.md", "Do not load every skill", issues, successes)
    require_text(root / "rules/README.md", "tool-discovery-policy", issues, successes)
    require_text(root / "connectors/connectors.md", "## Tool discovery / JIT tools", issues, successes)
    require_text(root / "hosts/_template/shim.md", "## JIT tools", issues, successes)

    for rel in [
        "hosts/devin-cli/SKILL.md",
        "hosts/claude-code/SKILL.md",
        "hosts/codex/AGENTS.md",
        "hosts/github-copilot/copilot-instructions.md",
    ]:
        require_text(root / rel, "## JIT tools", issues, successes)
        require_text(root / rel, "tool-discovery-policy.md", issues, successes)

    validate_tool_descriptions(TOOLS, issues, successes)
    return ValidationReport(tuple(issues), tuple(successes))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", "-Root", dest="root", default=".")
    args = parser.parse_args()

    report = validate_tool_discovery_policy(args.root)
    for message in report.successes:
        print(message)
    if not report.passed:
        for item in report.issues:
            print(f"ERROR {item.message}", file=sys.stderr)
        raise SystemExit(f"Tool discovery policy validation failed: {len(report.issues)} error(s)")

    print("Tool discovery policy validation completed.")


if __name__ == "__main__":
    main()
