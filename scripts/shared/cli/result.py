"""Stable CLI result envelope and rendering."""

from dataclasses import dataclass, field
import json


@dataclass
class CommandResult:
    command: str
    status: str = "ok"
    changed: bool = False
    message: str = ""
    data: dict = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    next_steps: list[str] = field(default_factory=list)

    @property
    def exit_code(self):
        return 0 if self.status == "ok" else 2 if self.status == "blocked" else 1

    def as_dict(self):
        return {
            "schema_version": "alfred.cli.v1",
            "command": self.command,
            "status": self.status,
            "changed": self.changed,
            "message": self.message,
            "data": self.data,
            "warnings": self.warnings,
            "next": self.next_steps,
        }


def render(result, as_json=False):
    if as_json:
        return json.dumps(result.as_dict(), ensure_ascii=False, indent=2)
    lines = [result.message or f"{result.command}: {result.status}"]
    lines.extend(f"Aviso: {item}" for item in result.warnings)
    lines.extend(f"Proximo: {item}" for item in result.next_steps)
    return "\n".join(lines)
