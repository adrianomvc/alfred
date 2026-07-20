"""Adversarial and end-to-end tests for the governance gates the audits flagged.

Covers: typed acceptance, lane evidence, phase transitions, App overwrite
guard, state single-source, budget fail-loud, telemetry sanitization, and a
CLI-only FAST lifecycle that closes without any manual markdown edit.
"""

import importlib.util
import io
import contextlib
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))

import shared.cli.parser as parser_mod  # noqa: E402
from shared.cli.demand import (_derive_sigla, checkpoint, close_readiness, draft,  # noqa: E402
                               start)
from shared.cli.git_service import _validate_candidate  # noqa: E402
from shared.cli.parser import run  # noqa: E402
from shared.common import find_duplicate_keys, read_state_fields, write_state_fields  # noqa: E402


def load_hyphenated(name, rel_path):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


EMAIL = load_hyphenated("mcp_email_server", "scripts/adapters/mcp-email-server.py")
HYGIENE = load_hyphenated("obs_hygiene", "scripts/validators/validate-observability-hygiene.py")
ROLLUP = load_hyphenated("metrics_rollup", "scripts/metrics/generate-metrics-rollup.py")

FAST_ANSWERS = ["iniciativa-001-e2e", "001-e2e", "Ana", "Entrega pequena",
                "Fora: resto", "nenhum", "A", "A",
                "A", "A", "A", "A", "A",
                "A", "A", "A", "A", "A",
                "A", "nenhum"]
STANDARD_ANSWERS = ["iniciativa-001-std", "001-std", "Ana", "Entrega media",
                    "Fora: resto", "nenhum", "A", "A",
                    "B", "B", "B", "B", "A",
                    "A", "A", "A", "A", "A",
                    "A", "nenhum"]


def fill_answers(req, answers):
    text = req.read_text(encoding="utf-8")
    answer_iter = iter(answers)
    text = re.sub(r"(?m)^\[Resposta\]:$",
                  lambda _m: f"[Resposta]: {next(answer_iter)}", text)
    req.write_text(text, encoding="utf-8")


def answer_field(req, field, value):
    text = req.read_text(encoding="utf-8")
    pattern = re.compile(r"(field: " + re.escape(field) + r";.*?\[Resposta\]:)\s*$",
                         re.S | re.M)
    text = pattern.sub(lambda m: m.group(1) + " " + value, text, count=1)
    req.write_text(text, encoding="utf-8")


class GovernanceGateTests(unittest.TestCase):
    def _fast_demand(self, tmp):
        hub = Path(tmp) / "alfred-docs-hub"
        hub.mkdir(exist_ok=True)
        created = draft(hub, ROOT, "E2E", "draft-e2e")
        fill_answers(Path(created.data["requirements"]), FAST_ANSWERS)
        result = start(created.data["draft"], ROOT, confirmed_by="Ana")
        self.assertEqual("ok", result.status, result.message)
        state = Path(result.data["state"])
        problem = state.parent / "01-inception" / "002-problem.md"
        problem.write_text(problem.read_text(encoding="utf-8")
                           + "\nProblema real: ajustar a entrega pequena do exemplo.\n",
                           encoding="utf-8")
        return state

    def test_fast_lifecycle_closes_via_cli_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = self._fast_demand(tmp)
            demand_dir = state.parent
            req = demand_dir / "01-inception" / "003-requirements.md"
            for phase, next_phase in (("Inception", "Design"), ("Design", "Execution"),
                                      ("Execution", "Validate"), ("Validate", "Operation")):
                result = checkpoint(state, ROOT, {"current phase": next_phase},
                                    complete=phase)
                self.assertEqual("ok", result.status, result.message)
            # 1st close: acceptance question appended (governed Q&A, not chat)
            readiness, _ = close_readiness(state, ROOT)
            self.assertEqual("blocked", readiness.status)
            answer_field(req, "final_acceptance", "A")
            # 2nd close: summary stub created and must be filled
            readiness, _ = close_readiness(state, ROOT)
            self.assertEqual("blocked", readiness.status)
            summary = demand_dir / "05-operation" / "009-summary.md"
            summary.write_text(summary.read_text(encoding="utf-8")
                               + "\nResumo real da entrega concluida.\n", encoding="utf-8")
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                code = run(["--alfred-home", str(ROOT), "demand", "close",
                            "--state", str(state)])
            self.assertEqual(0, code, output.getvalue())
            fields = read_state_fields(state)
            self.assertEqual("concluida", fields["status"])
            self.assertEqual("Operation", fields["current phase"])
            self.assertEqual([], find_duplicate_keys(state))
            log = demand_dir / "05-operation" / "011-observability-log.jsonl"
            events = [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()]
            self.assertTrue(all(e["schema_version"] == "alfred.observability.v1" for e in events))
            self.assertIn("checkpoint", {e["event_type"] for e in events})
            issues = HYGIENE.check_log(log, require_distinct_timestamps=False)
            self.assertEqual([], issues)

    def test_rejected_acceptance_never_closes_as_done(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = self._fast_demand(tmp)
            req = state.parent / "01-inception" / "003-requirements.md"
            close_readiness(state, ROOT)  # appends the acceptance question
            answer_field(req, "final_acceptance", "B")  # Rejeitar a entrega
            readiness, acceptance = close_readiness(state, ROOT)
            self.assertEqual("blocked", readiness.status)
            self.assertEqual("", acceptance)
            self.assertEqual("rejeitada", read_state_fields(state)["status"])

    def test_changes_requested_keeps_demand_open(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = self._fast_demand(tmp)
            req = state.parent / "01-inception" / "003-requirements.md"
            close_readiness(state, ROOT)
            answer_field(req, "final_acceptance", "C")  # Solicitar ajustes
            readiness, _ = close_readiness(state, ROOT)
            self.assertEqual("blocked", readiness.status)
            self.assertEqual("active", read_state_fields(state)["status"])

    def test_standard_close_requires_lane_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            hub = Path(tmp) / "alfred-docs-hub"; hub.mkdir()
            created = draft(hub, ROOT, "Std", "draft-std")
            req = Path(created.data["requirements"])
            fill_answers(req, STANDARD_ANSWERS)
            first = start(created.data["draft"], ROOT, confirmed_by="Ana")
            self.assertEqual("blocked", first.status)
            answer_field(req, "lane_confirm", "A")
            result = start(created.data["draft"], ROOT, confirmed_by="Ana")
            self.assertEqual("ok", result.status, result.message)
            state = Path(result.data["state"])
            new_req = state.parent / "01-inception" / "003-requirements.md"
            close_readiness(state, ROOT)
            answer_field(new_req, "final_acceptance", "A")
            readiness, _ = close_readiness(state, ROOT)
            self.assertEqual("blocked", readiness.status)
            self.assertIn("close_pr_url", readiness.message)
            self.assertIn("field: close_pr_url", new_req.read_text(encoding="utf-8"))

    def _standard_demand(self, tmp):
        hub = Path(tmp) / "alfred-docs-hub"
        hub.mkdir(exist_ok=True)
        created = draft(hub, ROOT, "Std", "draft-std-e2e")
        req = Path(created.data["requirements"])
        fill_answers(req, STANDARD_ANSWERS)
        first = start(created.data["draft"], ROOT, confirmed_by="Ana")
        self.assertEqual("blocked", first.status)  # derived lane awaits confirmation
        answer_field(req, "lane_confirm", "A")
        result = start(created.data["draft"], ROOT, confirmed_by="Ana")
        self.assertEqual("ok", result.status, result.message)
        state = Path(result.data["state"])
        self.assertEqual("Standard", read_state_fields(state)["lane"])
        return state

    def _fill_sdd_artifacts(self, demand_dir):
        """Real content beyond the template mold, as the SDD gate demands."""
        for relative, extra in (
            ("01-inception/002-problem.md",
             "Problema real: o rollout do dry-run nao avisa a squad."),
            ("01-inception/005-tech-inception.md",
             "Levantamento tecnico: o adapter le a config em ~/.alfred-email.json."),
            ("02-design/006-decisions.md",
             "| 2026-07-19 | Manter dry-run como padrao | Ana | evita envio acidental |"),
            ("03-execution/012-execution-plan.md",
             "Passo 1: ajustar o modo padrao. Passo 2: cobrir com teste."),
        ):
            path = demand_dir / relative
            path.write_text(path.read_text(encoding="utf-8") + f"\n{extra}\n",
                            encoding="utf-8")

    def test_standard_lifecycle_closes_with_lane_evidence_and_rolls_up(self):
        """The full Standard path the audit plan asked for: draft -> start ->
        --complete per phase (SDD gate on Execution) -> close with evidence ->
        rollup, with no manual markdown edit outside the artifacts themselves."""
        with tempfile.TemporaryDirectory() as tmp:
            state = self._standard_demand(tmp)
            demand_dir = state.parent
            req = demand_dir / "01-inception" / "003-requirements.md"

            # Entering Execution without the Design artifacts must be refused.
            self.assertEqual("ok", checkpoint(state, ROOT, {"current phase": "Design"},
                                              complete="Inception").status)
            blocked = checkpoint(state, ROOT, {"current phase": "Execution"},
                                 complete="Design")
            self.assertEqual("blocked", blocked.status)
            self.assertIn("SDD gate", blocked.message)

            self._fill_sdd_artifacts(demand_dir)
            for phase, next_phase in (("Design", "Execution"), ("Execution", "Validate"),
                                      ("Validate", "Operation")):
                result = checkpoint(state, ROOT, {"current phase": next_phase},
                                    complete=phase)
                self.assertEqual("ok", result.status, result.message)

            close_readiness(state, ROOT)  # appends the acceptance question
            answer_field(req, "final_acceptance", "A")
            blocked, _ = close_readiness(state, ROOT)  # lane evidence still missing
            self.assertEqual("blocked", blocked.status)
            answer_field(req, "close_pr_url", "https://git.example.com/pr/42")
            answer_field(req, "close_merge_state", "mesclado em main, commit abc1234")
            answer_field(req, "close_reviewer", "Bruno (revisor independente)")
            readiness, _ = close_readiness(state, ROOT)
            self.assertEqual("blocked", readiness.status)  # summary stub created
            summary = demand_dir / "05-operation" / "009-summary.md"
            summary.write_text(summary.read_text(encoding="utf-8")
                               + "\nResumo real da entrega Standard concluida.\n",
                               encoding="utf-8")

            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                code = run(["--alfred-home", str(ROOT), "demand", "close",
                            "--state", str(state)])
            self.assertEqual(0, code, output.getvalue())

            # State is the single source of truth and agrees with itself.
            fields = read_state_fields(state)
            self.assertEqual("concluida", fields["status"])
            self.assertEqual("Operation", fields["current phase"])
            self.assertEqual([], find_duplicate_keys(state))

            # The lane evidence reached the audit trail.
            audit = (demand_dir / "05-operation" / "007-audit.md").read_text(encoding="utf-8")
            self.assertIn("Aceite final registrado", audit)
            self.assertIn("https://git.example.com/pr/42", audit)

            # Events are v1, survive hygiene, and carry the checkpoints.
            log = demand_dir / "05-operation" / "011-observability-log.jsonl"
            events = [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()]
            self.assertTrue(all(e["schema_version"] == "alfred.observability.v1"
                                for e in events))
            self.assertIn("checkpoint", {e["event_type"] for e in events})
            self.assertEqual([], HYGIENE.check_log(log, require_distinct_timestamps=False))

            # Rollup: no cost events observed means "nao coletado", never US$ 0.
            summary = ROLLUP.summarize(ROLLUP.read_events(demand_dir))
            rollup = ROLLUP.render(summary, str(demand_dir), demand_dir)
            self.assertIn("- cost usd: nao coletado", rollup)
            self.assertNotIn("US$ 0.0000", rollup)

    def test_start_never_overwrites_existing_app_demand(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            hub = root / "alfred-docs-hub"; hub.mkdir()
            app = root / "app"; app.mkdir()
            existing = app / ".alfred-docs-app" / "iniciativa-001-e2e" / "001-e2e"
            existing.mkdir(parents=True)
            sentinel = existing / "005-audit.md"
            sentinel.write_text("historico precioso\n", encoding="utf-8")
            created = draft(hub, ROOT, "E2E", "draft-app-guard")
            answers = list(FAST_ANSWERS)
            answers[5] = str(app)
            fill_answers(Path(created.data["requirements"]), answers)
            result = start(created.data["draft"], ROOT, confirmed_by="Ana")
            self.assertEqual("blocked", result.status)
            self.assertIn("nao sera sobrescrita", result.message)
            self.assertEqual("historico precioso\n", sentinel.read_text(encoding="utf-8"))
            self.assertTrue(Path(created.data["draft"]).exists())  # draft preserved

    def test_phase_jump_requires_force_and_is_audited(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = self._fast_demand(tmp)
            blocked = checkpoint(state, ROOT, {"current phase": "Operation"})
            self.assertEqual("blocked", blocked.status)
            forced = checkpoint(state, ROOT, {"current phase": "Operation"},
                                force_reason="incidente critico aprovado pelo humano")
            self.assertEqual("ok", forced.status)
            audit = (state.parent / "05-operation" / "007-audit.md").read_text(encoding="utf-8")
            self.assertIn("Transicao forcada: incidente critico", audit)

    def test_advance_requires_completed_checklist(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = self._fast_demand(tmp)
            blocked = checkpoint(state, ROOT, {"current phase": "Design"})
            self.assertEqual("blocked", blocked.status)
            self.assertIn("--complete", blocked.message)

    def test_write_state_fields_heals_duplicates(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = Path(tmp) / "001-state.md"
            state.write_text("## Demand\n- status: stale\n\n## Progress\n- status: active\n",
                             encoding="utf-8")
            self.assertEqual(["status"], find_duplicate_keys(state))
            write_state_fields(state, {"status": "blocked"}, section="Progress")
            self.assertEqual([], find_duplicate_keys(state))
            self.assertEqual("blocked", read_state_fields(state)["status"])

    def test_budget_monitor_failure_warns_instead_of_silence(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = Path(tmp) / "001-state.md"
            state.write_text("## Progress\n- status: active\n", encoding="utf-8")
            failing = parser_mod.CommandResult("budget status", "blocked", message="boom")
            with mock.patch.object(parser_mod, "run_command", return_value=failing):
                measured, warnings, blocked = parser_mod._budget_gate(ROOT, state)
        self.assertIsNone(blocked)
        self.assertTrue(any("orcamento nao verificado" in w for w in warnings))

    def test_budget_warn_mode_does_not_block(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = Path(tmp) / "001-state.md"
            state.write_text("## Budget\n- budget on limit: warn\n", encoding="utf-8")
            exceeded = parser_mod.CommandResult("budget status", "ok",
                                                data={"result": {"status": "exceeded"}})
            with mock.patch.object(parser_mod, "run_command", return_value=exceeded):
                _measured, warnings, blocked = parser_mod._budget_gate(ROOT, state)
        self.assertIsNone(blocked)
        self.assertTrue(any("warn" in w for w in warnings))

    def test_budget_pause_mode_blocks_before_mutation(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = Path(tmp) / "001-state.md"
            state.write_text("## Budget\n- budget on limit: pause-and-ask\n", encoding="utf-8")
            exceeded = parser_mod.CommandResult("budget status", "ok",
                                                data={"result": {"status": "exceeded"}})
            with mock.patch.object(parser_mod, "run_command", return_value=exceeded):
                _measured, _warnings, blocked = parser_mod._budget_gate(ROOT, state)
        self.assertIsNotNone(blocked)
        self.assertEqual("blocked", blocked.status)

    def test_validate_candidate_survives_none_stdout(self):
        completed = mock.Mock(stdout=None, stderr="erro", returncode=1)
        git_ok = mock.Mock(returncode=0, stdout="", stderr="")
        with mock.patch("shared.cli.git_service.run_git", return_value=git_ok), \
             mock.patch("shared.cli.git_service.subprocess.run", return_value=completed):
            valid, evidence = _validate_candidate(ROOT, Path("ignored"))
        self.assertFalse(valid)
        self.assertEqual("erro", evidence)

    def test_title_containing_dry_run_is_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            hub = Path(tmp) / "alfred-docs-hub"; hub.mkdir()
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                code = run(["--alfred-home", str(ROOT), "demand", "draft",
                            "--hub", str(hub), "--title", "ajustar o --dry-run flag"])
            state = hub / "000-drafts"
            drafts = list(state.iterdir())
        self.assertEqual(0, code, output.getvalue())
        self.assertEqual(1, len(drafts))  # created for real, not silently dry-run

    def test_sigla_derived_from_itau_pattern(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "itau-sq9-modules-x"
            hub = repo / "alfred-docs-hub"
            hub.mkdir(parents=True)
            self.assertEqual("sq9", _derive_sigla(hub))

    def test_email_attachment_outside_roots_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            allowed = Path(tmp) / "allowed"; allowed.mkdir()
            outside = Path(tmp) / "outside"; outside.mkdir()
            secret = outside / "secrets.md"
            secret.write_text("conteudo\n", encoding="utf-8")
            problems = EMAIL.check_attachments({"attach_roots": [allowed.resolve()]},
                                               [str(secret)])
        self.assertEqual(1, len(problems))
        self.assertIn("fora das raizes permitidas", problems[0])

    def test_active_send_aborts_when_audit_cannot_persist(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            attachment_root = base / "demand"; attachment_root.mkdir()
            cfg = {
                "mode": "active", "default_to": "org@example.com", "telemetry_to": "",
                "allowlist": ["org@example.com"], "outbox": base / "outbox",
                # a directory as the audit path forces the append to fail
                "audit": base, "config_path": None, "secret_in_file": False,
                "attach_roots": [attachment_root.resolve()], "sender_alias": "",
                "smtp": {"host": "smtp.example.com", "port": 587, "user": "",
                         "password": "", "sender": "alfred@example.com"},
            }
            result = EMAIL.tool_send_email(cfg, {"subject": "x", "body": "y",
                                                 "to": "org@example.com"})
        self.assertTrue(result["isError"])
        self.assertIn("audit trail", result["content"][0]["text"])

    def test_telemetry_sanitization_drops_secrets_and_extra_fields(self):
        clean = EMAIL.sanitize_telemetry_event({
            "event_type": "checkpoint", "ts": "2026-07-19T00:00:00Z",
            "hostname": "machine-01", "cwd": "C:/Users/someone/project",
            "artifacts_used": [{"path": "C:/abs/path/001-state.md",
                                "artifact_type": "demand_artifact",
                                "operation": "update", "observed_by": "cli"}],
        })
        self.assertNotIn("hostname", clean)
        self.assertNotIn("cwd", clean)
        self.assertEqual("001-state.md", clean["artifacts_used"][0]["path"])
        secret = EMAIL.sanitize_telemetry_event({"event_type": "x",
                                                 "step": "password=hunter2"})
        self.assertIsNone(secret)


if __name__ == "__main__":
    unittest.main()
