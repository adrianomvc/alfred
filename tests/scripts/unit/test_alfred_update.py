import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))

from shared.cli.git_service import revision, update, update_lock  # noqa: E402


def git(cwd, *args):
    subprocess.run(["git", "-C", str(cwd), *args], check=True, capture_output=True, text=True)


class AlfredUpdateTests(unittest.TestCase):
    def make_repos(self, base):
        remote = base / "remote.git"
        source = base / "source"
        install = base / "install"
        subprocess.run(["git", "init", "--bare", "--initial-branch=main", str(remote)], check=True, capture_output=True)
        subprocess.run(["git", "clone", str(remote), str(source)], check=True, capture_output=True)
        git(source, "config", "user.email", "test@example.com")
        git(source, "config", "user.name", "Test")
        gate = source / "scripts" / "validators" / "validate-framework.py"
        gate.parent.mkdir(parents=True)
        gate.write_text("raise SystemExit(0)\n", encoding="utf-8")
        (source / "VERSION").write_text("2.0.0\n", encoding="utf-8")
        git(source, "add", "."); git(source, "commit", "-m", "initial"); git(source, "push", "origin", "main")
        subprocess.run(["git", "clone", str(remote), str(install)], check=True, capture_output=True)
        return source, install

    def test_valid_candidate_fast_forwards_single_installation(self):
        with tempfile.TemporaryDirectory() as tmp:
            source, install = self.make_repos(Path(tmp))
            (source / "marker.txt").write_text("new\n", encoding="utf-8")
            git(source, "add", "."); git(source, "commit", "-m", "valid"); git(source, "push")
            expected = revision(source)
            result = update(install, sync_hosts=False)
            actual = revision(install)
        self.assertEqual("ok", result.status, result.message + repr(result.data))
        self.assertTrue(result.changed)
        self.assertEqual(expected, actual)

    def test_invalid_candidate_is_blocked_and_current_commit_is_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            source, install = self.make_repos(Path(tmp))
            before = revision(install)
            gate = source / "scripts" / "validators" / "validate-framework.py"
            gate.write_text("raise SystemExit(1)\n", encoding="utf-8")
            git(source, "add", "."); git(source, "commit", "-m", "invalid"); git(source, "push")
            result = update(install, sync_hosts=False)
            after = revision(install)
        self.assertEqual("blocked", result.status)
        self.assertEqual(before, after)

    def test_dirty_installation_is_blocked(self):
        with tempfile.TemporaryDirectory() as tmp:
            _source, install = self.make_repos(Path(tmp))
            (install / "VERSION").write_text("dirty\n", encoding="utf-8")
            result = update(install, sync_hosts=False)
        self.assertEqual("blocked", result.status)
        self.assertIn("alteracoes locais", result.message)

    def test_concurrent_lock_times_out(self):
        with tempfile.TemporaryDirectory() as tmp:
            runtime = Path(tmp)
            with update_lock(runtime):
                with self.assertRaises(TimeoutError):
                    with update_lock(runtime, timeout=0):
                        pass

    def test_local_framework_without_git_degrades_as_not_verified(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = update(tmp, sync_hosts=False)
        self.assertEqual("ok", result.status)
        self.assertFalse(result.data["verified"])


if __name__ == "__main__":
    unittest.main()
