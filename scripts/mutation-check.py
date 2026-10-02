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
    (r"\b>\b", ">=", "Invert strict inequality ( > to >= )"),
    (r"\b<\b", "<=", "Invert strict inequality ( < to <= )"),
    (r"\b===\b", "!==", "Invert strict equality ( === to !== )"),
    (r"\b==\b", "!=", "Invert equality ( == to != )"),
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

    print(f"🛡️  [Test Architect] Running baseline test before mutation...")
    if not run_test(args.test):
        print(f"❌ Baseline test failed! Fix existing tests before running mutation sanity check.")
        sys.exit(1)
    print(f"✓ Baseline tests PASS cleanly.\n")

    # Create backup
    backup_path = target_path.with_suffix(target_path.suffix + ".bak")
    shutil.copy2(target_path, backup_path)

    try:
        content = backup_path.read_text(encoding="utf-8")
        mutations_tested = 0
        survived_count = 0
        killed_count = 0

        print(f"🔬 Testing up to {args.max_mutations} logic mutations in {target_path.name}...")

        for pattern, replacement, desc in MUTATION_RULES:
            if mutations_tested >= args.max_mutations:
                break

            matches = list(re.finditer(pattern, content))
            if not matches:
                continue

            # Mutate first occurrence
            match = matches[0]
            start, end = match.span()
            mutated_content = content[:start] + replacement + content[end:]

            target_path.write_text(mutated_content, encoding="utf-8")
            mutations_tested += 1

            # Run test on mutated code
            passed = run_test(args.test)
            if passed:
                survived_count += 1
                print(f"  ⚠️  MUTATION SURVIVED: {desc}")
                print(f"      Tests still PASSED despite changing logic! Your test suite may lack edge-case coverage.")
            else:
                killed_count += 1
                print(f"  ✓  MUTATION KILLED: {desc}")
                print(f"      Tests correctly FAILED when logic was altered. Strong assertion detected!")

        print("\n" + "=" * 55)
        print(f"Mutation Sanity Summary: {killed_count} Killed, {survived_count} Survived.")
        if survived_count > 0:
            print("⚠️  Action required: Add assertions covering the survived boundary conditions.")
        else:
            print("🎉 Excellent! Your test suite successfully caught all injected logic mutations.")
        print("=" * 55 + "\n")

    finally:
        # Restore original file
        if backup_path.exists():
            shutil.copy2(backup_path, target_path)
            backup_path.unlink()

if __name__ == "__main__":
    main()
