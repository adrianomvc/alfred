from dataclasses import dataclass
import re
import subprocess
from pathlib import Path

from shared.common.text_files import read_lines
from shared.validation.models import Severity, ValidationIssue, ValidationReport


UNAVAILABLE = ("not-git", "unknown", "a confirmar")


@dataclass(frozen=True)
class ReverseEngStalenessResult:
    report: ValidationReport
    output: tuple[str, ...]
    failure_message: str = ""


def get_recorded_commit(lines):
    patterns = [
        r"^\s*-\s+commit\s*:\s*(not-git|unknown|a confirmar)\s*$",
        r"^\s*-\s+app commit\s*:\s*(not-git|unknown|a confirmar)\s*$",
        r"^\s*-\s+commit\s*:\s*`?([A-Fa-f0-9]{7,40})`?\s*$",
        r"^\s*-\s+app commit\s*:\s*`?([A-Fa-f0-9]{7,40})`?\s*$",
    ]
    for line in lines:
        for pattern in patterns:
            match = re.match(pattern, line)
            if match:
                return match.group(1)
    for line in lines:
        match = re.search(r"\b([A-Fa-f0-9]{40})\b", line)
        if match:
            return match.group(1)
    return ""


def validate_reverse_eng_staleness(
    reverse_eng_path,
    *,
    app_repo_path="",
    current_commit="",
    strict=False,
    git_runner=subprocess.run,
):
    output = []
    issues = []
    reverse_eng = Path(reverse_eng_path)
    if not reverse_eng.exists():
        message = f"Reverse-eng artifact not found: {reverse_eng}"
        return ReverseEngStalenessResult(
            report=ValidationReport((
                ValidationIssue("reverse_eng_staleness.missing_artifact", Severity.ERROR, message),
            )),
            output=(),
            failure_message=message,
        )

    recorded = get_recorded_commit(read_lines(reverse_eng))

    if recorded == "":
        message = "Reverse-eng artifact does not record an app commit."
        issue = ValidationIssue("reverse_eng_staleness.missing_commit", Severity.WARNING, message)
        if strict:
            issue = ValidationIssue(issue.code, Severity.ERROR, issue.message)
            return ReverseEngStalenessResult(
                report=ValidationReport((issue,)),
                output=(),
                failure_message=message,
            )
        issues.append(issue)
        output.append(f"WARN missing_commit: {message}")
        return ReverseEngStalenessResult(ValidationReport(tuple(issues), tuple(output)), tuple(output))

    if recorded in UNAVAILABLE:
        output.append(f"OK reverse-eng staleness explicitly unavailable: recorded={recorded}")
        return ReverseEngStalenessResult(ValidationReport((), tuple(output)), tuple(output))

    current = current_commit
    if current == "":
        if app_repo_path == "":
            output.append(f"OK recorded commit {recorded}")
            message = "provide -AppRepoPath or -CurrentCommit to check staleness"
            issues.append(ValidationIssue("reverse_eng_staleness.current_commit_unknown", Severity.WARNING, message))
            output.append(f"WARN current_commit_unknown: {message}")
            return ReverseEngStalenessResult(ValidationReport(tuple(issues), tuple(output)), tuple(output))
        if not (Path(app_repo_path) / ".git").exists():
            message = f"AppRepoPath is not a git repository: {app_repo_path}"
            issue = ValidationIssue("reverse_eng_staleness.app_repo_not_git", Severity.WARNING, message)
            if strict:
                issue = ValidationIssue(issue.code, Severity.ERROR, issue.message)
                return ReverseEngStalenessResult(
                    report=ValidationReport((issue,)),
                    output=(),
                    failure_message=message,
                )
            issues.append(issue)
            output.append(f"OK recorded commit {recorded}")
            output.append(f"WARN app_repo_not_git: {message}")
            return ReverseEngStalenessResult(ValidationReport(tuple(issues), tuple(output)), tuple(output))
        current = git_runner(
            ["git", "-C", app_repo_path, "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()

    if current == "":
        message = "Could not determine current app commit."
        return ReverseEngStalenessResult(
            report=ValidationReport((
                ValidationIssue("reverse_eng_staleness.current_commit_missing", Severity.ERROR, message),
            )),
            output=(),
            failure_message=message,
        )

    recorded_prefix = recorded.lower()
    current_prefix = current.lower()
    if current_prefix.startswith(recorded_prefix) or recorded_prefix.startswith(current_prefix):
        output.append(f"OK reverse-eng fresh: recorded={recorded} current={current}")
        return ReverseEngStalenessResult(ValidationReport((), tuple(output)), tuple(output))

    message = f"Reverse-eng stale: recorded={recorded} current={current}"
    issue = ValidationIssue("reverse_eng_staleness.stale", Severity.WARNING, message)
    if strict:
        issue = ValidationIssue(issue.code, Severity.ERROR, issue.message)
        return ReverseEngStalenessResult(
            report=ValidationReport((issue,)),
            output=(),
            failure_message=message,
        )
    issues.append(issue)
    output.append(f"WARN reverse_eng_stale: {message}")
    return ReverseEngStalenessResult(ValidationReport(tuple(issues), tuple(output)), tuple(output))
