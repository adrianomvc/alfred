import ast
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))


class SharedBoundaryTests(unittest.TestCase):
    def test_shared_does_not_import_entrypoints_or_common_shim(self):
        forbidden_exact = {"_common"}
        forbidden_prefixes = ("workflow.", "metrics.", "validators.", "adapters.")

        offenders = []
        for path in (SCRIPTS / "shared").rglob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8-sig"))
            for node in ast.walk(tree):
                imports = []
                if isinstance(node, ast.Import):
                    imports.extend(alias.name for alias in node.names)
                elif isinstance(node, ast.ImportFrom):
                    imports.append(node.module or "")
                for imported in imports:
                    if imported in forbidden_exact or imported.startswith(forbidden_prefixes):
                        offenders.append(f"{path.relative_to(ROOT)} -> {imported}")

        self.assertEqual([], offenders)


if __name__ == "__main__":
    unittest.main()
