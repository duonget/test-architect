#!/usr/bin/env python3
"""Lightweight mutation sanity checker for boundary and boolean assertions."""

import argparse
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path


EXIT_ERROR = 1
EXIT_SURVIVED = 2
EXIT_INVALID = 3

MUTATION_RULES = [
    (r"(?<![=<>!])<=(?!=)", "<", "Shift inclusive lower boundary ( <= to < )"),
    (r"(?<![=<>!])>=(?!=)", ">", "Shift inclusive upper boundary ( >= to > )"),
    (r"(?<![=<>!])>(?![=<>])", ">=", "Shift strict upper boundary ( > to >= )"),
    (r"(?<![=<>!])<(?![=<>])", "<=", "Shift strict lower boundary ( < to <= )"),
    (r"!==", "===", "Invert strict inequality ( !== to === )"),
    (r"===", "!==", "Invert strict equality ( === to !== )"),
    (r"(?<![!=])==(?!=)", "!=", "Invert equality ( == to != )"),
    (r"\btrue\b", "false", "Flip boolean constant ( true to false )"),
    (r"\bfalse\b", "true", "Flip boolean constant ( false to true )"),
    (r"\bTrue\b", "False", "Flip boolean constant ( True to False )"),
    (r"\bFalse\b", "True", "Flip boolean constant ( False to True )"),
]


@dataclass
class CommandResult:
    status: str
    returncode: int | None
    output: str


def run_command(cmd: str, timeout: float) -> CommandResult:
    """Run a trusted project command with a hard timeout and captured output."""
    process = subprocess.Popen(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        start_new_session=True,
    )
    try:
        output, _ = process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGTERM)
        try:
            output, _ = process.communicate(timeout=2)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            output, _ = process.communicate()
        return CommandResult("timeout", None, output)

    status = "passed" if process.returncode == 0 else "failed"
    if process.returncode in (126, 127) or process.returncode < 0:
        status = "error"
    return CommandResult(status, process.returncode, output)


def executable_code(line: str) -> str:
    """Mask quoted text and inline comments before locating mutation sites."""
    result = []
    quote = None
    escaped = False
    index = 0

    while index < len(line):
        char = line[index]
        next_char = line[index + 1] if index + 1 < len(line) else ""

        if quote:
            result.append(" ")
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = None
            index += 1
            continue

        if char in ('"', "'", "`"):
            quote = char
            result.append(" ")
        elif char == "#" or (char == "/" and next_char == "/"):
            result.extend(" " * (len(line) - index))
            break
        else:
            result.append(char)
        index += 1

    return "".join(result)


def is_executable_line(code: str) -> bool:
    """Avoid declarations and prose where lexical operators are usually syntax."""
    stripped = code.strip()
    if not stripped or stripped.startswith(("/*", "*", "//", "#")):
        return False
    if re.fullmatch(r"[<>][\s\w{},;()[\]]*", stripped):
        return False
    if re.search(r"\b(Promise|Map|Set|Array|Record)<", stripped):
        return False
    declaration = re.match(
        r"^(export\s+)?(interface|type|class|enum|import|from|package|func\s+\w+|def\s+\w+)\b",
        stripped,
    )
    return declaration is None


def find_candidates(content: str):
    lines = content.splitlines(keepends=True)
    for line_idx, line in enumerate(lines):
        code = executable_code(line)
        if not is_executable_line(code):
            continue
        for pattern, replacement, description in MUTATION_RULES:
            match = re.search(pattern, code)
            if match:
                yield lines, line_idx, match.span(), replacement, description


def print_diagnostics(result: CommandResult):
    if result.output.strip():
        print("      Command output:")
        for line in result.output.strip().splitlines()[-8:]:
            print(f"        {line}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Test Architect Mutation Sanity Checker")
    parser.add_argument("--target", required=True, help="Path to source code file to mutate")
    parser.add_argument("--test", required=True, help="Trusted shell command that runs the target tests")
    parser.add_argument(
        "--validate",
        help="Optional trusted shell command that validates syntax/types before tests",
    )
    parser.add_argument("--max-mutations", type=int, default=3, help="Maximum valid mutations to test")
    parser.add_argument("--timeout", type=float, default=120, help="Seconds allowed per command")
    args = parser.parse_args()

    target_path = Path(args.target).resolve()
    if not target_path.is_file():
        print(f"[ERROR] Target file '{args.target}' does not exist or is not a file.")
        return EXIT_ERROR
    if args.max_mutations < 1:
        print("[ERROR] --max-mutations must be at least 1.")
        return EXIT_ERROR
    if args.timeout <= 0:
        print("[ERROR] --timeout must be greater than zero.")
        return EXIT_ERROR

    lock_path = target_path.with_name(f".{target_path.name}.mutation.lock")
    try:
        lock_fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        print(f"[ERROR] Another mutation check appears to be running for '{target_path}'.")
        return EXIT_ERROR

    backup_path = None
    backup_complete = False
    try:
        print("[Test Architect] Running baseline test before mutation...")
        baseline = run_command(args.test, args.timeout)
        if baseline.status != "passed":
            print(f"[ERROR] Baseline test did not pass ({baseline.status}).")
            print_diagnostics(baseline)
            return EXIT_ERROR
        print("[PASS] Baseline tests pass cleanly.\n")

        with tempfile.NamedTemporaryFile(
            prefix=f"{target_path.name}.", suffix=".mutation-backup", delete=False
        ) as backup:
            backup_path = Path(backup.name)
        shutil.copy2(target_path, backup_path)
        backup_complete = True
        original = backup_path.read_text(encoding="utf-8")

        valid_count = 0
        killed_count = 0
        survived_count = 0
        invalid_count = 0

        print(f"[INFO] Testing up to {args.max_mutations} valid mutations in {target_path.name}...")
        for lines, line_idx, span, replacement, description in find_candidates(original):
            if valid_count >= args.max_mutations:
                break

            start, end = span
            mutated_lines = list(lines)
            line = mutated_lines[line_idx]
            mutated_lines[line_idx] = line[:start] + replacement + line[end:]
            target_path.write_text("".join(mutated_lines), encoding="utf-8")

            if args.validate:
                validation = run_command(args.validate, args.timeout)
                if validation.status != "passed":
                    invalid_count += 1
                    print(f"  [INVALID] {description} (line {line_idx + 1})")
                    print_diagnostics(validation)
                    target_path.write_text(original, encoding="utf-8")
                    continue

            valid_count += 1
            result = run_command(args.test, args.timeout)
            target_path.write_text(original, encoding="utf-8")

            if result.status == "passed":
                survived_count += 1
                print(f"  [SURVIVED] {description} (line {line_idx + 1})")
            elif result.status == "failed":
                killed_count += 1
                print(f"  [KILLED] {description} (line {line_idx + 1})")
            else:
                invalid_count += 1
                valid_count -= 1
                print(f"  [INVALID] Test command {result.status} for {description} (line {line_idx + 1})")
                print_diagnostics(result)

        print("\n" + "=" * 60)
        print(
            f"Mutation Summary: {killed_count} Killed, {survived_count} Survived, "
            f"{invalid_count} Invalid."
        )
        if valid_count == 0:
            print("[ERROR] No valid mutation was tested; the result is inconclusive.")
            return EXIT_INVALID if invalid_count else EXIT_ERROR
        if survived_count:
            print("[FAIL] Add assertions that cover the survived behavior changes.")
            return EXIT_SURVIVED
        if invalid_count:
            print("[WARN] Invalid mutations were skipped; valid mutants still passed the gate.")
        print("[SUCCESS] All valid mutations were killed by the test suite.")
        return 0
    finally:
        try:
            if backup_complete and backup_path and backup_path.exists():
                shutil.copy2(backup_path, target_path)
            if backup_path and backup_path.exists():
                backup_path.unlink()
        finally:
            os.close(lock_fd)
            lock_path.unlink(missing_ok=True)


if __name__ == "__main__":
    sys.exit(main())
