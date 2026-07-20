#!/usr/bin/env python3
"""Validate one Alfred demand across HUB (and optional App) artifacts."""

import argparse
from dataclasses import dataclass
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from _common import (  # noqa: E402
    get_field, iter_jsonl, normalize_phase, phase_number, read_lines,
)
from shared.cli.demand import PHASES  # noqa: E402
from shared.cli.requirements import parse as parse_requirements  # noqa: E402
from shared.common import find_duplicate_keys  # noqa: E402
from shared.sdd_gate import run as run_sdd_gate  # noqa: E402
from shared.validation import Severity, ValidationIssue, ValidationReport  # noqa: E402
from shared.validation.reverse_eng_staleness import validate_reverse_eng_staleness  # noqa: E402

# Lifecycle states a demand may report (rules/common/session-continuity.md) plus
# the values the CLI writes. Kept as a check, not a rewrite: the human owns the word.
DEMAND_STATUSES = ("draft", "active", "em andamento", "em espera", "bloqueada",
                   "aguardando checkpoint", "concluida", "concluída", "rejeitada",
                   "replanejada", "cancelada")


CLOSED_STATUSES = ("closed", "concluida", "concluída", "done", "finalizada", "completed")
OPERATIONAL_LABEL = re.compile(
    r"^\|\s*(Time|Actor|Phase|Action|Model|Result|Responsible human|Date|Decision|Owner|Rationale|Impact)"
)


@dataclass(frozen=True)
class DemandValidationResult:
    report: ValidationReport
    output: tuple[str, ...]
    failure_message: str = ""


class Validator:
    def __init__(self, strict=False):
        self.issues = []
        self.output = []
        self.strict = strict

    def add(self, severity, code, message):
        level = Severity.ERROR if severity == "ERROR" else Severity.WARNING
        self.issues.append(ValidationIssue(code=code, severity=level, message=message))

    def ok(self, message):
        self.output.append(message)

    def assert_path(self, root, rel, severity="ERROR"):
        full = Path(root) / rel
        if not full.exists():
            self.add(severity, "missing_path", f"Missing {rel}")
            return False
        self.ok(f"OK path {rel}")
        return True

    def assert_jsonl(self, file_path, label):
        if not Path(file_path).exists():
            self.add("ERROR", "missing_jsonl", f"Missing {label}")
            return
        for line_number, parsed, _ in iter_jsonl(file_path):
            if parsed is None:
                self.add("ERROR", "invalid_jsonl", f"{label} has invalid JSON at line {line_number}")
        self.ok(f"OK jsonl {label}")

    def read_events(self, file_path, label):
        events = []
        if not Path(file_path).exists():
            return events
        for line_number, parsed, _ in iter_jsonl(file_path):
            if parsed is None:
                self.add("ERROR", "invalid_jsonl", f"{label} has invalid JSON at line {line_number}")
            else:
                parsed["_line"] = line_number
                events.append(parsed)
        return events

    def md_has_operational_content(self, file_path, label):
        if not Path(file_path).exists():
            return
        skip = [
            re.compile(r"^#"),
            re.compile(r"^>"),
            re.compile(r"^\|[-\s|]+\|$"),
            re.compile(r"^-\s*[A-Za-z /]+:\s*$"),
        ]
        useful = 0
        for raw in read_lines(file_path):
            line = raw.strip()
            if line == "":
                continue
            if any(rx.match(line) for rx in skip) or OPERATIONAL_LABEL.match(line):
                continue
            useful += 1
        if useful == 0:
            self.add("WARN", "empty_operational_artifact",
                     f"{label} has no operational content: {file_path}")
        else:
            self.ok(f"OK content {label}")

    def test_state_field(self, value, name, severity="WARN"):
        if value == "":
            self.add(severity, "missing_state_field", f"Missing state field: {name}")
        else:
            self.ok(f"OK field {name} = {value}")

    def observability_consistency(self, events, demand_id, initiative_id, phase, schema, version):
        if not events:
            self.add("ERROR", "empty_observability_log", "HUB observability log has no events")
            return
        ordered = sorted(events, key=lambda e: e["_line"])
        last = ordered[-1]
        legacy_missing = 0
        for event in events:
            if demand_id and str(event.get("demand_id")) != demand_id:
                self.add("ERROR", "observability_demand_mismatch",
                         f"Event line {event['_line']} demand_id '{event.get('demand_id')}' differs from state id '{demand_id}'")
            if initiative_id and str(event.get("initiative_id")) != initiative_id:
                self.add("WARN", "observability_initiative_mismatch",
                         f"Event line {event['_line']} initiative_id '{event.get('initiative_id')}' differs from state initiative '{initiative_id}'")
            if schema and str(event.get("schema_version")) != schema:
                self.add("ERROR", "observability_schema_mismatch",
                         f"Event line {event['_line']} schema '{event.get('schema_version')}' differs from state schema '{schema}'")
            alfred = event.get("alfred")
            if version and alfred and str(alfred.get("version", "")) != "" and str(alfred.get("version")) != version:
                self.add("WARN", "observability_version_mismatch",
                         f"Event line {event['_line']} Alfred version '{alfred.get('version')}' differs from state version '{version}'")
            if "artifacts_used" not in event or event.get("artifacts_used") is None:
                if event["_line"] == last["_line"]:
                    self.add("WARN", "observability_missing_artifacts_used",
                             f"Event line {event['_line']} does not record artifacts_used")
                else:
                    legacy_missing += 1

        if legacy_missing > 0:
            self.ok(f"OK observability legacy events without artifacts_used {legacy_missing}")

        event_phase = str(last.get("phase", ""))
        st = last.get("state_transition")
        if st and st.get("to") and str(st["to"].get("phase", "")) != "":
            event_phase = str(st["to"]["phase"])

        if normalize_phase(event_phase) != normalize_phase(phase):
            self.add("WARN", "observability_phase_mismatch",
                     f"Latest event phase '{event_phase}' differs from state phase '{phase}'")
        else:
            self.ok(f"OK observability latest phase {event_phase}")

        self.ok(f"OK observability events {len(events)}")

    def finish(self, label):
        warnings = [i for i in self.issues if i.severity == Severity.WARNING]
        errors = [i for i in self.issues if i.severity == Severity.ERROR]
        lines = list(self.output)
        for issue in self.issues:
            lines.append(f"{severity_label(issue)} {issue.code}: {issue.message}")
        report = ValidationReport(tuple(self.issues), tuple(self.output))
        failure = ""
        if errors or (self.strict and warnings):
            failure = f"{label} failed. errors={len(errors)}, warnings={len(warnings)}, strict={self.strict}"
        else:
            lines.append(f"{label} completed. errors={len(errors)}, warnings={len(warnings)}, strict={self.strict}")
        return DemandValidationResult(report=report, output=tuple(lines), failure_message=failure)


def severity_label(issue):
    return "ERROR" if issue.severity == Severity.ERROR else "WARN"


def validate_demand(args):
    v = Validator(strict=args.strict)
    hub = Path(args.hub_demand_path).resolve()

    v.assert_path(hub, "001-state.md")
    state_path = hub / "001-state.md"
    if not state_path.exists():
        result = v.finish("Demand validation")
        return DemandValidationResult(
            report=result.report,
            output=result.output,
            failure_message="Cannot validate demand without 001-state.md",
        )

    state_lines = read_lines(state_path)

    duplicates = find_duplicate_keys(state_path)
    if duplicates:
        v.add("ERROR", "duplicate_state_key",
              "State has duplicated field keys (writer/reader would diverge): "
              + ", ".join(duplicates))

    # The CLI writes fields with section="Demand"/"Opening Framing"/"Progress".
    # A state carrying translated headings (## Demanda, ## Progresso) parses for
    # reading but the writer will not find the section and appends a second one —
    # the same writer/reader divergence as a duplicated key, arriving as data
    # instead of code. Structure stays English; content is pt-BR (D47).
    headings = {line.strip()[3:].strip() for line in state_lines if line.startswith("## ")}
    for required in ("Demand", "Progress"):
        if required not in headings:
            translated = {"Demand": "Demanda", "Progress": "Progresso"}[required]
            hint = f" (found `## {translated}`)" if translated in headings else ""
            v.add("ERROR", "state_section_not_canonical",
                  f"State has no `## {required}` section{hint}; the CLI writes into it "
                  f"and would append a duplicate instead. Headings are English, content pt-BR (D47).")


    demand_id = get_field(state_lines, ["id"])
    initiative_id = get_field(state_lines, ["initiative id", "id iniciativa"])
    sigla = get_field(state_lines, ["sigla"])
    lane = get_field(state_lines, ["lane", "modo"])
    phase = get_field(state_lines, ["current phase", "fase atual"])
    status = get_field(state_lines, ["status"])
    framework_version = get_field(state_lines, ["framework version", "versao framework", "versão framework"])
    observability_schema = get_field(state_lines, ["observability schema", "schema observability"])
    framing_status = get_field(state_lines, ["framing status", "status enquadramento"])
    framing_confirmed_by = get_field(state_lines, ["framing confirmed by", "enquadramento confirmado por"])
    framing_confirmed_at = get_field(state_lines, ["framing confirmed at", "enquadramento confirmado em"])

    # `status` and `current phase` are different axes. A phase name parked in
    # `status` means the demand reports no lifecycle state at all — and it reads
    # as plausible, so nothing downstream complains.
    if status and status.strip().lower() in {phase_name.lower() for phase_name in PHASES}:
        v.add("ERROR", "status_is_a_phase",
              f"`status: {status}` is a phase name, not a demand status. "
              f"Use one of: {', '.join(DEMAND_STATUSES)}.")

    v.test_state_field(demand_id, "id", "ERROR")
    v.test_state_field(initiative_id, "initiative id", "WARN")
    v.test_state_field(sigla, "sigla", "WARN")
    v.test_state_field(lane, "lane/modo", "ERROR")
    v.test_state_field(phase, "current phase/fase atual", "ERROR")
    v.test_state_field(status, "status", "WARN")
    v.test_state_field(framework_version, "framework version", "WARN")
    v.test_state_field(framing_status, "framing status", "WARN")
    v.test_state_field(framing_confirmed_by, "framing confirmed by", "WARN")
    v.test_state_field(framing_confirmed_at, "framing confirmed at", "WARN")

    if framing_status and framing_status.lower() not in (
        "confirmed", "confirmado", "not applicable", "n/a", "nao aplicavel", "não aplicável",
    ):
        v.add("WARN", "opening_framing_not_confirmed",
              f"Opening framing status is not confirmed: {framing_status}")

    pnum = phase_number(phase)
    if pnum == 0:
        v.add("WARN", "unknown_phase", f"Current phase is not one of the canonical phases: {phase}")

    for folder in ("01-inception", "02-design", "03-execution", "04-validate", "05-operation"):
        v.assert_path(hub, folder)

    for path in (
        "01-inception/002-problem.md",
        "01-inception/004-risk.md",
        "05-operation/007-audit.md",
        "05-operation/008-metrics.md",
        "05-operation/011-observability-log.jsonl",
    ):
        v.assert_path(hub, path)

    if lane.lower() in ("standard", "safe"):
        v.assert_path(hub, "01-inception/003-requirements.md", "WARN")
        v.assert_path(hub, "02-design/006-decisions.md", "WARN")

    requirements_path = hub / "01-inception/003-requirements.md"
    if requirements_path.exists():
        answers, required, missing = parse_requirements(requirements_path)
        if missing:
            v.add("WARN", "unanswered_required_questions",
                  "Requirements has unanswered required questions: " + ", ".join(missing))
        elif required:
            v.ok(f"OK requirements answers {len(required)}/{len(required)}")

    # FAST folds Design into Execution (inline spec in the PR): the separate
    # tech-inception/decisions/execution-plan/evidence artifacts are not
    # required for that lane (rules/lanes/fast.md, design.md depth-by-mode).
    if lane.lower() != "fast":
        if pnum >= 2:
            v.assert_path(hub, "01-inception/005-tech-inception.md", "WARN")
        if pnum >= 3:
            v.assert_path(hub, "03-execution/012-execution-plan.md", "WARN")
        if pnum >= 4:
            v.assert_path(hub, "04-validate/013-validation-evidence.md", "WARN")

    if pnum >= 3:
        output, errors, warnings, _ = run_sdd_gate(
            str(hub), args.app_demand_path if args.app_demand_path else "", False,
            lane=lane,
        )
        for line in output:
            v.output.append(line)
            if line.startswith("ERROR "):
                v.add("ERROR", "sdd_gate", line)
            elif line.startswith("WARN "):
                v.add("WARN", "sdd_gate", line)

    if status.lower() in CLOSED_STATUSES:
        v.assert_path(hub, "05-operation/009-summary.md", "WARN")
        open_items = sum(1 for line in state_lines if re.match(r"^\s*-\s+\[\s\]", line))
        if open_items > 0:
            v.add("WARN", "open_checklist_on_closed",
                  f"Demand is closed but checklist has {open_items} open item(s)")

    state_text = "\n".join(state_lines)
    if not re.search(r"(?im)^##\s+Active Skills\s*$", state_text) and \
       not re.search(r"(?im)^##\s+Skills ativos\s*$", state_text):
        v.add("WARN", "missing_active_skills", "State does not declare active skills")
    if not re.search(r"(?im)^##\s+Host Adapters\s*$", state_text) and \
       not re.search(r"(?im)^##\s+Adapters de host\s*$", state_text):
        v.add("WARN", "missing_host_adapters", "State does not declare host adapter readiness")
    if observability_schema == "":
        v.add("WARN", "missing_observability_schema", "State does not declare observability schema")

    v.assert_jsonl(hub / "05-operation/011-observability-log.jsonl", "HUB observability log")
    v.md_has_operational_content(hub / "05-operation/007-audit.md", "HUB audit")
    v.md_has_operational_content(hub / "05-operation/008-metrics.md", "HUB metrics")
    hub_events = v.read_events(hub / "05-operation/011-observability-log.jsonl", "HUB observability log")
    v.observability_consistency(hub_events, demand_id, initiative_id, phase,
                                observability_schema, framework_version)

    if args.app_demand_path:
        app = Path(args.app_demand_path).resolve()
        v.assert_path(app, "001-index.md")
        has_reverse_eng = v.assert_path(app, "01-inception/002-reverse-eng.md", "WARN")
        v.assert_path(app, "05-operation/005-audit.md", "WARN")
        v.assert_path(app, "05-operation/006-metrics.md", "WARN")
        v.assert_jsonl(app / "05-operation/008-observability-log.jsonl", "App observability log")

        if has_reverse_eng:
            staleness = validate_reverse_eng_staleness(
                app / "01-inception/002-reverse-eng.md",
                app_repo_path=args.app_repo_path,
                current_commit=args.app_current_commit,
                strict=False,
            )
            for line in staleness.output:
                v.output.append(line)
                if line.startswith("WARN "):
                    v.add("WARN", "reverse_eng_staleness", line)

    return v.finish("Demand validation")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--hub-demand-path", "-HubDemandPath", dest="hub_demand_path", required=True)
    parser.add_argument("--app-demand-path", "-AppDemandPath", dest="app_demand_path", default="")
    parser.add_argument("--app-repo-path", "-AppRepoPath", dest="app_repo_path", default="",
                        help="app repo path forwarded to the reverse-eng staleness check")
    parser.add_argument("--app-current-commit", "-AppCurrentCommit", dest="app_current_commit", default="",
                        help="current app commit forwarded to the reverse-eng staleness check")
    parser.add_argument("--strict", "-Strict", dest="strict", action="store_true")
    args = parser.parse_args()

    result = validate_demand(args)
    for line in result.output:
        print(line)
    if result.failure_message:
        raise SystemExit(result.failure_message)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
