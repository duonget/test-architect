# Contributing to Test Architect

Thank you for your interest in contributing to **Test Architect**! Our goal is to make AI Coding Agents worldwide write reliable, bulletproof tests instead of shallow, over-mocked tests.

---

## How to Add a New Framework Template (15-Minute Guide)

We are actively expanding our language and framework coverage (e.g. C# .NET, Kotlin, Swift, Elixir, PHP Pest, Ruby RSpec).

### Step 1: Add a Detection Rule in `scripts/detect-runner.sh`
Add a block checking for your framework's config file (e.g., `mix.exs`, `*.csproj`, `Gemfile`):
```bash
if [ -f "$CWD/mix.exs" ]; then
  echo "FRAMEWORK=exunit"
  echo "RUN_ALL_CMD=mix test"
  echo "RUN_SINGLE_CMD=mix test <file>"
  echo "COVERAGE_CMD=mix test --cover"
  echo "FILE_EXTENSION=_test.exs"
  return 0
fi
```

### Step 2: Add a Production Template in `templates/`
Create `templates/<language>-<framework>.<ext>` demonstrating:
1. Clear AAA (Arrange - Act - Assert) separation.
2. Parameterized or table-driven test cases for boundary values.
3. Minimal Viable Mocking (only mock external boundaries; never mock domain logic).
4. Idiomatic error/exception assertion.

### Step 3: Test Locally & Open a PR
1. Run `./scripts/detect-runner.sh <your-test-dir>` to ensure it identifies your project.
2. Run `./install.sh <sandbox-dir>` to verify files copy properly.
3. Submit a Pull Request using our [PR Template](.github/PULL_REQUEST_TEMPLATE.md).

---

## Development Conventions

- **POSIX Portability**: All `.sh` scripts must remain POSIX-compliant (`set -euo pipefail`) and avoid non-standard bashisms so they run cleanly on Alpine Linux, macOS, and Ubuntu.
- **Zero Heavy Dependencies**: Helper scripts should remain zero-dependency (relying only on standard tools like Python 3 standard library and Bash).

---

## Community & Discussions

Have questions or ideas? Open an issue or join our GitHub Discussions!
