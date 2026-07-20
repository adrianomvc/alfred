import contextlib
import io
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))

from shared.cli.demand import checkpoint, close_readiness, draft, start  # noqa: E402
from shared.cli.parser import run  # noqa: E402
from shared.cli.requirements import append_question, parse, status  # noqa: E402
from shared.cli.result import CommandResult  # noqa: E402
from shared.cli.workspace import detect  # noqa: E402


class AlfredCliTests(unittest.TestCase):
    def test_result_exit_codes_are_stable(self):
        self.assertEqual(0, CommandResult("x").exit_code)
        self.assertEqual(2, CommandResult("x", "blocked").exit_code)
        self.assertEqual(1, CommandResult("x", "error").exit_code)

    def test_json_envelope_has_schema(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = run(["--alfred-home", str(ROOT), "doctor", "--json"])
        payload = json.loads(output.getvalue())
        self.assertEqual(0, code)
        self.assertEqual("alfred.cli.v1", payload["schema_version"])
        self.assertEqual("doctor", payload["command"])

    def test_workspace_detects_framework_repo(self):
        result = detect(ROOT)
        self.assertEqual("Framework", result.data["kind"])

    def test_draft_is_idempotent_and_only_creates_two_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            hub = Path(tmp) / "alfred-docs-hub"
            hub.mkdir()
            first = draft(hub, ROOT, "Corrigir relatorio", "draft-001")
            second = draft(hub, ROOT, "Corrigir relatorio", "draft-001")
            files = sorted(path.relative_to(hub / "000-drafts" / "draft-001").as_posix()
                           for path in (hub / "000-drafts" / "draft-001").rglob("*") if path.is_file())
        self.assertTrue(first.changed)
        self.assertFalse(second.changed)
        self.assertEqual(["001-state.md", "01-inception/003-requirements.md"], files)

    def test_draft_proposes_choices_without_prefilling_answers(self):
        with tempfile.TemporaryDirectory() as tmp:
            hub = Path(tmp) / "alfred-docs-hub"; hub.mkdir()
            result = draft(hub, ROOT, "Nova integracao", "draft-002")
            text = Path(result.data["requirements"]).read_text(encoding="utf-8")
        self.assertIn("(Recomendada)", text)
        self.assertIn("001-nova-integracao", text)
        self.assertNotIn("[Resposta]: A", text)

    def test_requirements_status_blocks_missing_answers(self):
        with tempfile.TemporaryDirectory() as tmp:
            hub = Path(tmp) / "alfred-docs-hub"; hub.mkdir()
            created = draft(hub, ROOT, "Teste", "draft-003")
            result = status(created.data["requirements"])
        self.assertEqual("blocked", result.status)
        self.assertIn("initiative_id", result.data["missing"])

    def test_letter_answer_resolves_to_proposed_value(self):
        with tempfile.TemporaryDirectory() as tmp:
            hub = Path(tmp) / "alfred-docs-hub"; hub.mkdir()
            created = draft(hub, ROOT, "Minha demanda", "draft-choice")
            req = Path(created.data["requirements"])
            text = req.read_text(encoding="utf-8")
            text = re.sub(r"(?m)^\[Resposta\]:", "[Resposta]: A", text, count=1)
            req.write_text(text, encoding="utf-8")
            values, _required, _missing = parse(req)
        self.assertEqual("iniciativa-001-minha-demanda", values["initiative_id"])

    def test_additional_question_supports_multiple_selection(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "003-requirements.md"
            path.write_text("# Requirements\n", encoding="utf-8")
            append_question(path, "Quais canais?", "channels", ["Email", "Chat", "Arquivo"], "B", True)
            text = path.read_text(encoding="utf-8")
        self.assertIn("- [ ] Chat (Recomendada)", text)
        self.assertNotIn("Recomendacao Alfred:", text)

    def test_checked_multiple_choices_count_as_answer(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "003-requirements.md"
            path.write_text("# Requirements\n", encoding="utf-8")
            append_question(path, "Quais canais?", "channels", ["Email", "Chat"], "A", True)
            text = path.read_text(encoding="utf-8").replace("- [ ] Email", "- [x] Email")
            path.write_text(text, encoding="utf-8")
            values, _required, missing = parse(path)
        self.assertEqual("Email", values["channels"])
        self.assertEqual([], missing)

    # Answer order mirrors templates/hub/draft-requirements.md. Risk criteria
    # B,B,B,B,A sum to risk=4 -> Standard proposal, confirmed in a second pass.
    STANDARD_ANSWERS = ["iniciativa-001-teste", "001-demanda", "Ana", "Entregar teste",
                        "Mudancas externas", "nenhum", "A", "A",
                        "B", "B", "B", "B", "A",
                        "A", "A", "A", "A", "A",
                        "A", "nenhum"]

    @staticmethod
    def _fill_answers(req, answers):
        text = req.read_text(encoding="utf-8")
        answer_iter = iter(answers)
        text = re.sub(r"(?m)^\[Resposta\]:$",
                      lambda _match: f"[Resposta]: {next(answer_iter)}", text)
        req.write_text(text, encoding="utf-8")

    def _start_standard(self, draft_data, lane_answer="A"):
        first = start(draft_data["draft"], ROOT)
        self.assertEqual("blocked", first.status)
        self.assertIn("lane_confirm", first.message)
        self._fill_answers(Path(draft_data["requirements"]), [lane_answer])
        return start(draft_data["draft"], ROOT)

    def test_start_moves_completed_draft_to_canonical_demand(self):
        with tempfile.TemporaryDirectory() as tmp:
            hub = Path(tmp) / "alfred-docs-hub"; hub.mkdir()
            created = draft(hub, ROOT, "Teste", "draft-004")
            req = Path(created.data["requirements"])
            self._fill_answers(req, self.STANDARD_ANSWERS)
            result = self._start_standard(created.data)
            target = Path(result.data["demand"])
            log = target / "05-operation" / "011-observability-log.jsonl"
            draft_exists = Path(created.data["draft"]).exists()
            log_exists = log.exists()
            plan_exists = (target / "03-execution" / "012-execution-plan.md").exists()
            events = [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()]
        self.assertEqual("ok", result.status)
        self.assertEqual("Standard", result.data["lane"])
        self.assertFalse(draft_exists)
        self.assertTrue(log_exists)
        self.assertTrue(plan_exists)
        self.assertEqual("alfred.observability.v1", events[0]["schema_version"])
        self.assertEqual("demand_started", events[0]["event_type"])
        self.assertTrue(events[0]["ts"])

    def test_start_creates_app_artifacts_for_approved_local_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            hub = root / "alfred-docs-hub"; hub.mkdir()
            app = root / "app"; app.mkdir()
            created = draft(hub, ROOT, "Teste App", "draft-app")
            answers = list(self.STANDARD_ANSWERS)
            answers[0], answers[1], answers[5] = "iniciativa-001-app", "001-app", str(app)
            self._fill_answers(Path(created.data["requirements"]), answers)
            result = self._start_standard(created.data)
            app_target = app / ".alfred-docs-app" / "iniciativa-001-app" / "001-app"
            index_exists = (app_target / "001-index.md").exists()
            spec_exists = (app_target / "02-design" / "003-spec.md").exists()
        self.assertEqual("ok", result.status)
        self.assertTrue(index_exists)
        self.assertTrue(spec_exists)

    def test_checkpoint_persists_question_only_in_requirements(self):
        with tempfile.TemporaryDirectory() as tmp:
            demand_root = Path(tmp)
            state = demand_root / "001-state.md"
            req = demand_root / "01-inception" / "003-requirements.md"
            req.parent.mkdir(parents=True)
            state.write_text((ROOT / "templates/hub/state.md").read_text(encoding="utf-8"), encoding="utf-8")
            req.write_text("# Requirements\n", encoding="utf-8")
            result = checkpoint(state, ROOT, {}, "Qual estrategia?", "strategy", ["A", "B"], "A")
            text = req.read_text(encoding="utf-8")
        self.assertEqual("blocked", result.status)
        self.assertIn("Qual estrategia?", text)

    def test_close_records_acceptance_question_in_requirements(self):
        with tempfile.TemporaryDirectory() as tmp:
            demand_root = Path(tmp)
            state = demand_root / "001-state.md"
            req = demand_root / "01-inception" / "003-requirements.md"
            req.parent.mkdir(parents=True)
            state.write_text((ROOT / "templates/hub/state.md").read_text(encoding="utf-8"), encoding="utf-8")
            req.write_text("# Requirements\n", encoding="utf-8")
            result, acceptance = close_readiness(state, ROOT)
            text = req.read_text(encoding="utf-8")
        self.assertEqual("blocked", result.status)
        self.assertEqual("", acceptance)
        self.assertIn("field: final_acceptance", text)
        self.assertIn("Aceitar a entrega (Recomendada)", text)


if __name__ == "__main__":
    unittest.main()
