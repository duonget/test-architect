#!/usr/bin/env python3
"""
mutation-check.py
Lightweight mutation sanity checker to expose tautological or weak test suites.

Usage:
  python3 scripts/mutation-check.py --target src/service.ts --test "npx vitest run src/service.test.ts"
"""

import argparse
import subprocess
import sys
import shutil
import re
from pathlib import Path

MUTATION_RULES = [
    (r"(?<![=<>!])>(?![=<>])", ">=", "Invert strict inequality ( > to >= )"),
    (r"(?<![=<>!])<(?![=<>])", "<=", "Invert strict inequality ( < to <= )"),
    (r"===", "!==", "Invert strict equality ( === to !== )"),
    (r"(?<!=)==(?!=)", "!=", "Invert equality ( == to != )"),
    (r"\btrue\b", "false", "Flip boolean constant ( true to false )"),
    (r"\bfalse\b", "true", "Flip boolean constant ( false to true )"),
]

def run_test(cmd: str) -> bool:
    """Run test command, return True if tests PASS, False if tests FAIL."""
    try:
        res = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return res.returncode == 0
    except Exception:
        return False

def main():
    parser = argparse.ArgumentParser(description="Test Architect Mutation Sanity Checker")
    parser.add_argument("--target", required=True, help="Path to source code file to mutate")
    parser.add_argument("--test", required=True, help="Test command to run")
    parser.add_argument("--max-mutations", type=int, default=3, help="Max mutations to test")
    args = parser.parse_args()

    target_path = Path(args.target)
    if not target_path.exists():
        print(f"Error: Target file '{args.target}' does not exist.")
        sys.exit(1)

    print(f"[Test Architect] Running baseline test before mutation...")
    if not run_test(args.test):
        print(f"[ERROR] Baseline test failed! Fix existing tests before running mutation sanity check.")
        sys.exit(1)
    print(f"[PASS] Baseline tests PASS cleanly.\n")

    # Create backup
    backup_path = target_path.with_suffix(target_path.suffix + ".bak")
    shutil.copy2(target_path, backup_path)

    try:
        content = backup_path.read_text(encoding="utf-8")
        mutations_tested = 0
        survived_count = 0
        killed_count = 0

        print(f"[INFO] Testing up to {args.max_mutations} logic mutations in {target_path.name}...")

        lines = content.splitlines(keepends=True)
        mutated_lines = list(lines)

        for pattern, replacement, desc in MUTATION_RULES:
            if mutations_tested >= args.max_mutations:
                break

            applied = False
            for line_idx, line in enumerate(lines):
                stripped = line.strip()
                # Skip comments
                if stripped.startswith("//") or stripped.startswith("#") or stripped.startswith("*") or stripped.startswith("/*"):
                    continue

                if re.search(pattern, line):
                    mutated_line = re.sub(pattern, replacement, line, count=1)
                    mutated_lines[line_idx] = mutated_line
                    mutated_content = "".join(mutated_lines)
                    target_path.write_text(mutated_content, encoding="utf-8")
                    mutations_tested += 1
                    applied = True

                    # Run test on mutated code
                    passed = run_test(args.test)
                    if passed:
                        survived_count += 1
                        print(f"  [SURVIVED] MUTATION SURVIVED: {desc} (line {line_idx + 1})")
                        print(f"      Tests still PASSED despite changing logic! Your test suite may lack edge-case coverage.")
                    else:
                        killed_count += 1
                        print(f"  [KILLED] MUTATION KILLED: {desc} (line {line_idx + 1})")
                        print(f"      Tests correctly FAILED when logic was altered. Strong assertion detected!")

                    # Reset line back for next mutation rule
                    mutated_lines[line_idx] = line
                    break

        print("\n" + "=" * 55)
        print(f"Mutation Sanity Summary: {killed_count} Killed, {survived_count} Survived.")
        if survived_count > 0:
            print("[WARN] Action required: Add assertions covering the survived boundary conditions.")
        else:
            print("[SUCCESS] Excellent! Your test suite successfully caught all injected logic mutations.")
        print("=" * 55 + "\n")

    finally:
        # Restore original file
        if backup_path.exists():
            shutil.copy2(backup_path, target_path)
            backup_path.unlink()

if __name__ == "__main__":
    main()
