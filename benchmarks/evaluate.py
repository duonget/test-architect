#!/usr/bin/env python3
"""Evaluate trusted unittest submissions in fresh directories, without editing fixtures."""
import argparse
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent


def run(source, tests, timeout):
    with tempfile.TemporaryDirectory(prefix="test-architect-bench-") as directory:
        workspace = Path(directory)
        for test in tests.glob("test_*.py"):
            shutil.copy2(test, workspace / test.name)
        (workspace / "solution.py").write_text(source, encoding="utf-8")
        shutil.copy2(ROOT / "worker.py", workspace / "_benchmark_worker.py")
        process = subprocess.Popen(
            [sys.executable, "-B", "_benchmark_worker.py"], cwd=workspace,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
            start_new_session=True,
        )
        try:
            output, _ = process.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            output, _ = process.communicate()
            return {"status": "timeout", "output": output}
        status = {0: "pass", 1: "assertion_failure"}.get(process.returncode, "error")
        return {"status": status, "output": output}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tests", type=Path, required=True,
                        help="Directory containing pricing/, payment/, pagination/ candidate tests")
    parser.add_argument("--timeout", type=float, default=10)
    parser.add_argument("--require-all", action="store_true", help="Fail unless all seeded bugs are caught")
    args = parser.parse_args()
    if args.timeout <= 0:
        parser.error("timeout must be positive")
    mutants = json.loads((ROOT / "mutants.json").read_text())
    report = {"schema_version": 1, "cases": {}, "caught": 0, "total": 0}
    valid = True
    for case, variants in mutants.items():
        source = (ROOT / "cases" / case / "solution.py").read_text()
        tests = args.tests.resolve() / case
        baseline = run(source, tests, args.timeout)
        entry = {"baseline": baseline, "mutants": {}}
        report["cases"][case] = entry
        if baseline["status"] != "pass":
            valid = False
        for variant in variants:
            if variant["before"] not in source:
                raise ValueError(f"Stale mutant: {case}/{variant['id']}")
            mutated = source.replace(variant["before"], variant["after"], 1)
            compile(mutated, "solution.py", "exec")
            report["total"] += 1
            if baseline["status"] != "pass":
                entry["mutants"][variant["id"]] = {"status": "not_scored"}
                continue
            outcome = run(mutated, tests, args.timeout)
            if outcome["status"] == "assertion_failure":
                report["caught"] += 1
            elif outcome["status"] != "pass":
                valid = False
            entry["mutants"][variant["id"]] = outcome
    report["valid"] = valid
    print(json.dumps(report, indent=2))
    return 0 if valid and (not args.require_all or report["caught"] == report["total"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
