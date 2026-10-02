#!/usr/bin/env bash
# detect-runner.sh
# Detects the testing framework and runner commands in the current project repository.

set -euo pipefail

CWD="${1:-.}"

detect_runner() {
  # 1. Check Node.js / TypeScript Projects
  if [ -f "$CWD/package.json" ]; then
    PM="npx"
    TEST_EXEC="npm test"
    if [ -f "$CWD/pnpm-lock.yaml" ]; then
      PM="pnpm exec"
      TEST_EXEC="pnpm test"
    elif [ -f "$CWD/yarn.lock" ]; then
      PM="yarn"
      TEST_EXEC="yarn test"
    elif [ -f "$CWD/bun.lockb" ] || [ -f "$CWD/bun.lock" ]; then
      PM="bunx"
      TEST_EXEC="bun test"
    fi

    # Check Vitest
    if grep -q '"vitest"' "$CWD/package.json" || [ -f "$CWD/vitest.config.ts" ] || [ -f "$CWD/vitest.config.js" ]; then
      echo "FRAMEWORK=vitest"
      echo "RUN_ALL_CMD=$PM vitest run"
      echo "RUN_SINGLE_CMD=$PM vitest run <file>"
      echo "COVERAGE_CMD=$PM vitest run --coverage"
      echo "FILE_EXTENSION=.test.ts"
      return 0
    fi

    # Check Jest
    if grep -q '"jest"' "$CWD/package.json" || [ -f "$CWD/jest.config.js" ] || [ -f "$CWD/jest.config.ts" ]; then
      echo "FRAMEWORK=jest"
      echo "RUN_ALL_CMD=$PM jest"
      echo "RUN_SINGLE_CMD=$PM jest <file>"
      echo "COVERAGE_CMD=$PM jest --coverage"
      echo "FILE_EXTENSION=.test.ts"
      return 0
    fi

    # Check Bun test
    if [ -f "$CWD/bun.lockb" ] || [ -f "$CWD/bun.lock" ]; then
      echo "FRAMEWORK=bun"
      echo "RUN_ALL_CMD=bun test"
      echo "RUN_SINGLE_CMD=bun test <file>"
      echo "COVERAGE_CMD=bun test --coverage"
      echo "FILE_EXTENSION=.test.ts"
      return 0
    fi

    # Fallback to detected package manager test script
    echo "FRAMEWORK=npm-scripts"
    echo "RUN_ALL_CMD=$TEST_EXEC"
    echo "RUN_SINGLE_CMD=$TEST_EXEC -- <file>"
    echo "COVERAGE_CMD=$TEST_EXEC -- --coverage"
    echo "FILE_EXTENSION=.test.js"
    return 0
  fi

  # 2. Check Python Projects
  PYTEST_DETECTED=false
  if [ -f "$CWD/pytest.ini" ] \
    || { [ -f "$CWD/pyproject.toml" ] && grep -Eq '\[tool\.pytest|pytest' "$CWD/pyproject.toml"; } \
    || { [ -f "$CWD/setup.cfg" ] && grep -Eq '^\[tool:pytest\]' "$CWD/setup.cfg"; } \
    || { [ -f "$CWD/tox.ini" ] && grep -Eq 'pytest|\[pytest\]' "$CWD/tox.ini"; } \
    || { [ -d "$CWD/tests" ] && grep -REq '^[[:space:]]*(from[[:space:]]+pytest|import[[:space:]]+pytest)' "$CWD/tests"; }; then
    PYTEST_DETECTED=true
  fi
  for dependency_file in "$CWD"/requirements*.txt; do
    if [ -f "$dependency_file" ] && grep -Eq '^[[:space:]]*pytest([<=>~![:space:]]|$)' "$dependency_file"; then
      PYTEST_DETECTED=true
      break
    fi
  done

  if [ "$PYTEST_DETECTED" = true ]; then
    echo "FRAMEWORK=pytest"
    echo "RUN_ALL_CMD=pytest -v"
    echo "RUN_SINGLE_CMD=pytest -v <file>"
    echo "COVERAGE_CMD=pytest --cov=. tests/"
    echo "FILE_EXTENSION=_test.py"
    return 0
  fi

  # 3. Check Go Projects
  if [ -f "$CWD/go.mod" ]; then
    echo "FRAMEWORK=gotest"
    echo "RUN_ALL_CMD=go test -v ./..."
    echo "RUN_SINGLE_CMD=go test -v <package> -run '<test-name>'"
    echo "COVERAGE_CMD=go test -coverprofile=coverage.out ./..."
    echo "FILE_EXTENSION=_test.go"
    return 0
  fi

  # 4. Check Rust Projects
  if [ -f "$CWD/Cargo.toml" ]; then
    echo "FRAMEWORK=cargo-test"
    echo "RUN_ALL_CMD=cargo test"
    echo "RUN_SINGLE_CMD=cargo test --test <name>"
    echo "COVERAGE_CMD=cargo tarpaulin"
    echo "FILE_EXTENSION=.rs"
    return 0
  fi

  echo "FRAMEWORK=unknown"
  echo "RUN_ALL_CMD=unknown"
  echo "RUN_SINGLE_CMD=unknown"
  return 1
}

detect_runner
