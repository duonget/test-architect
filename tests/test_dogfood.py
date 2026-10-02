#!/usr/bin/env python3
"""
tests/test_dogfood.py
Self-verification suite for test-architect scripts.
Tests detect-runner.sh and mutation-check.py against simulated projects.
"""

import os
import subprocess
import tempfile
import unittest
from pathlib import Path

class TestArchitectSelfAudit(unittest.TestCase):
    def setUp(self):
        self.repo_root = Path(__file__).resolve().parent.parent
        self.detect_script = self.repo_root / "scripts" / "detect-runner.sh"
        self.mutation_script = self.repo_root / "scripts" / "mutation-check.py"

    def test_runner_detection_vitest(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            pkg_json = Path(tmpdir) / "package.json"
            pkg_json.write_text('{"devDependencies": {"vitest": "^2.0.0"}}', encoding="utf-8")

            res = subprocess.run(
                ["bash", str(self.detect_script), tmpdir],
                capture_output=True,
                text=True,
                check=True
            )
            self.assertIn("FRAMEWORK=vitest", res.stdout)
            self.assertIn("vitest run", res.stdout)

    def test_runner_detection_pnpm(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "package.json").write_text('{"devDependencies": {"vitest": "^2.0.0"}}', encoding="utf-8")
            (Path(tmpdir) / "pnpm-lock.yaml").write_text('lockfileVersion: 5.4', encoding="utf-8")

            res = subprocess.run(
                ["bash", str(self.detect_script), tmpdir],
                capture_output=True,
                text=True,
                check=True
            )
            self.assertIn("pnpm dlx vitest run", res.stdout)

    def test_runner_detection_pytest(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "pytest.ini").write_text("[pytest]\n", encoding="utf-8")

            res = subprocess.run(
                ["bash", str(self.detect_script), tmpdir],
                capture_output=True,
                text=True,
                check=True
            )
            self.assertIn("FRAMEWORK=pytest", res.stdout)
            self.assertIn("pytest -v", res.stdout)

    def test_runner_detection_golang(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "go.mod").write_text("module example.com/app\n\ngo 1.22\n", encoding="utf-8")

            res = subprocess.run(
                ["bash", str(self.detect_script), tmpdir],
                capture_output=True,
                text=True,
                check=True
            )
            self.assertIn("FRAMEWORK=gotest", res.stdout)
            self.assertIn("go test -v ./...", res.stdout)

    def test_mutation_check_kills_mutation(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            src_file = Path(tmpdir) / "calc.py"
            src_file.write_text("def is_positive(x):\n    return x > 0\n", encoding="utf-8")

            test_file = Path(tmpdir) / "test_calc.py"
            test_file.write_text(
                "import unittest\nfrom calc import is_positive\n\n"
                "class TestCalc(unittest.TestCase):\n"
                "    def test_zero(self):\n"
                "        self.assertFalse(is_positive(0))\n"
                "    def test_positive(self):\n"
                "        self.assertTrue(is_positive(1))\n\n"
                "if __name__ == '__main__':\n"
                "    unittest.main()\n",
                encoding="utf-8"
            )

            test_cmd = f"python3 -m unittest {test_file.name}"
            res = subprocess.run(
                [
                    "python3",
                    str(self.mutation_script),
                    "--target",
                    str(src_file),
                    "--test",
                    f"cd {tmpdir} && {test_cmd}"
                ],
                capture_output=True,
                text=True
            )
            self.assertEqual(res.returncode, 0)
            self.assertIn("[KILLED] MUTATION KILLED", res.stdout)
            self.assertIn("0 Survived", res.stdout)

if __name__ == "__main__":
    unittest.main()
