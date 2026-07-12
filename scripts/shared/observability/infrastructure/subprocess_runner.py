import subprocess
from typing import Sequence

from shared.observability.application.ports.command_runner import CommandResult


class SubprocessCommandRunner:
    def run(self, command: Sequence[str]) -> CommandResult:
        result = subprocess.run(command, capture_output=True, text=True, check=False)
        return CommandResult(result.returncode, result.stdout, result.stderr)

