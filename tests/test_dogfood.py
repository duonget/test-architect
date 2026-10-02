#!/usr/bin/env python3
"""Self-verification suite for the public Test Architect tooling."""

import io
import os
import subprocess
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path


class TestArchitectSelfAudit(unittest.TestCase):
    def setUp(self):
        self.repo_root = Path(__file__).resolve().parent.parent
        self.detect_script = self.repo_root / "scripts" / "detect-runner.sh"
        self.mutation_script = self.repo_root / "scripts" / "mutation-check.py"

    def run_detector(self, root: Path, check: bool = True):
        result = subprocess.run(
            ["bash", str(self.detect_script), str(root)],
            capture_output=True,
            text=True,
            check=check,
            timeout=5,
        )
        values = {}
        for line in result.stdout.splitlines():
            key, value = line.split("=", 1)
            values[key] = value
        return result, values

    def run_mutation(self, target: Path, test_command: str, *extra: str):
        return subprocess.run(
            [
                sys.executable,
                str(self.mutation_script),
                "--target",
                str(target),
                "--test",
                test_command,
                *extra,
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )

    def test_runner_detection_vitest_with_pnpm_uses_local_binary(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "package.json").write_text(
                '{"devDependencies": {"vitest": "^2.0.0"}}', encoding="utf-8"
            )
            (root / "pnpm-lock.yaml").write_text("lockfileVersion: 9", encoding="utf-8")

            _, values = self.run_detector(root)

            self.assertEqual(values["FRAMEWORK"], "vitest")
            self.assertEqual(values["RUN_ALL_CMD"], "pnpm exec vitest run")
            self.assertEqual(values["RUN_SINGLE_CMD"], "pnpm exec vitest run <file>")

    def test_runner_detection_jest_with_yarn(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "package.json").write_text(
                '{"devDependencies": {"jest": "^30.0.0"}}', encoding="utf-8"
            )
            (root / "yarn.lock").write_text("", encoding="utf-8")

            _, values = self.run_detector(root)

            self.assertEqual(values["FRAMEWORK"], "jest")
            self.assertEqual(values["RUN_ALL_CMD"], "yarn jest")

    def test_runner_detection_requires_explicit_pytest_evidence(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "tests").mkdir()
            (root / "pyproject.toml").write_text(
                '[project]\nname = "unittest-project"\n', encoding="utf-8"
            )

            result, values = self.run_detector(root, check=False)

            self.assertEqual(result.returncode, 1)
            self.assertEqual(values["FRAMEWORK"], "unknown")

    def test_runner_detection_pytest_from_pyproject(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "pyproject.toml").write_text(
                '[tool.pytest.ini_options]\ntestpaths = ["tests"]\n', encoding="utf-8"
            )

            _, values = self.run_detector(root)

            self.assertEqual(values["FRAMEWORK"], "pytest")
            self.assertEqual(values["RUN_ALL_CMD"], "pytest -v")

    def test_runner_detection_pytest_from_tox(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "tox.ini").write_text(
                "[testenv]\ncommands = pytest -v\n", encoding="utf-8"
            )

            _, values = self.run_detector(root)

            self.assertEqual(values["FRAMEWORK"], "pytest")

    def test_runner_detection_pytest_from_test_import(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            tests = root / "tests"
            tests.mkdir()
            (tests / "test_api.py").write_text(
                "import pytest\n\ndef test_api():\n    assert True\n", encoding="utf-8"
            )

            _, values = self.run_detector(root)

            self.assertEqual(values["FRAMEWORK"], "pytest")

    def test_runner_detection_go_uses_package_command(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "go.mod").write_text("module example.com/app\n\ngo 1.22\n", encoding="utf-8")

            _, values = self.run_detector(root)

            self.assertEqual(values["FRAMEWORK"], "gotest")
            self.assertEqual(values["RUN_SINGLE_CMD"], "go test -v <package> -run '<test-name>'")

    def test_runner_detection_rust(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "Cargo.toml").write_text('[package]\nname = "sample"\n', encoding="utf-8")

            _, values = self.run_detector(root)

            self.assertEqual(values["FRAMEWORK"], "cargo-test")

    def test_mutation_killed_restores_source_and_leaves_no_sibling_backup(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            source = root / "calc.py"
            original = "def is_positive(x):\n    return x > 0\n"
            source.write_text(original, encoding="utf-8")
            (root / "test_calc.py").write_text(
                "import unittest\nfrom calc import is_positive\n\n"
                "class TestCalc(unittest.TestCase):\n"
                "    def test_boundary(self):\n"
                "        self.assertFalse(is_positive(0))\n\n",
                encoding="utf-8",
            )
            command = f'cd "{root}" && "{sys.executable}" -m unittest test_calc.py'

            result = self.run_mutation(source, command, "--max-mutations", "1")

            self.assertEqual(result.returncode, 0, result.stdout)
            self.assertIn("1 Killed, 0 Survived", result.stdout)
            self.assertEqual(source.read_text(encoding="utf-8"), original)
            self.assertFalse((root / "calc.py.bak").exists())
            self.assertFalse((root / ".calc.py.mutation.lock").exists())

    def test_mutation_survivor_returns_nonzero(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            source = Path(tmpdir) / "calc.py"
            source.write_text("def is_positive(x):\n    return x > 0\n", encoding="utf-8")

            result = self.run_mutation(source, f'"{sys.executable}" -c "pass"', "--max-mutations", "1")

            self.assertEqual(result.returncode, 2)
            self.assertIn("1 Survived", result.stdout)

    def test_mutation_rejects_zero_limit_and_no_candidates(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            source = Path(tmpdir) / "constant.py"
            source.write_text("VALUE = 42\n", encoding="utf-8")
            passing = f'"{sys.executable}" -c "pass"'

            zero = self.run_mutation(source, passing, "--max-mutations", "0")
            none = self.run_mutation(source, passing)

            self.assertEqual(zero.returncode, 1)
            self.assertIn("must be at least 1", zero.stdout)
            self.assertEqual(none.returncode, 1)
            self.assertIn("No valid mutation", none.stdout)

    def test_mutation_baseline_timeout_is_an_error(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            source = Path(tmpdir) / "calc.py"
            source.write_text("def compare(x):\n    return x > 0\n", encoding="utf-8")
            command = f'"{sys.executable}" -c "import time; time.sleep(1)"'

            result = self.run_mutation(source, command, "--timeout", "0.05")

            self.assertEqual(result.returncode, 1)
            self.assertIn("baseline test did not pass (timeout)", result.stdout.lower())

    def test_streamed_installer_downloads_payload(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            archive = root / "source.tar.gz"
            target = root / "target"
            target.mkdir()
            (target / "SKILL.md").write_text("unrelated target file", encoding="utf-8")
            (target / "scripts").mkdir()
            (target / "templates").mkdir()
            script = (self.repo_root / "install.sh").read_text(encoding="utf-8")

            with tarfile.open(archive, "w:gz") as tar:
                for relative in ("SKILL.md", "AGENTS.md", "scripts", "templates"):
                    tar.add(self.repo_root / relative, arcname=f"test-architect-main/{relative}")

            environment = os.environ.copy()
            environment["TEST_ARCHITECT_ARCHIVE_URL"] = archive.as_uri()
            result = subprocess.run(
                ["bash"],
                input=script,
                cwd=target,
                env=environment,
                capture_output=True,
                text=True,
                timeout=10,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((target / ".agents/skills/test-architect/SKILL.md").is_file())
            self.assertNotEqual(
                (target / ".agents/skills/test-architect/SKILL.md").read_text(encoding="utf-8"),
                "unrelated target file",
            )
            self.assertTrue((target / "AGENTS.md").is_file())
            self.assertTrue((target / ".cursor/rules/test-architect.mdc").is_file())


if __name__ == "__main__":
    unittest.main()
