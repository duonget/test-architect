"""Exercise the real evaluator subprocess boundary, never mock its scoring."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("benchmark_evaluator", ROOT / "benchmarks/evaluate.py")
evaluator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(evaluator)


class BenchmarkTests(unittest.TestCase):
    def test_classification_and_isolation(self):
        scenarios = [
            ("", "error"),
            ("import nonexistent_benchmark_dependency", "error"),
            ("import time; time.sleep(30)", "timeout"),
            ("import unittest\nclass T(unittest.TestCase):\n"
             "    def test_value(self):\n"
             "        from solution import value\n"
             "        self.assertEqual(value, 2)\n", "assertion_failure"),
            ("import unittest\nclass T(unittest.TestCase):\n"
             "    def test_value(self):\n"
             "        from solution import value\n"
             "        self.assertEqual(value, 1)\n", "pass"),
        ]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            test = root / "test_candidate.py"
            for content, expected in scenarios:
                with self.subTest(expected=expected):
                    test.write_text(content)
                    outcome = evaluator.run("value = 1\n", root, 0.5)
                    self.assertEqual(outcome["status"], expected, outcome["output"])
                    self.assertEqual(test.read_text(), content)
                    self.assertFalse((root / "solution.py").exists())

    def test_skipped_suite_is_not_a_passing_baseline(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "test_skip.py").write_text(
                "import unittest\n@unittest.skip('disabled')\n"
                "class T(unittest.TestCase):\n    def test_disabled(self): pass\n"
            )
            self.assertEqual(evaluator.run("value = 1", root, 5)["status"], "error")
