#!/usr/bin/env bash
# install.sh
# Universal Installer for Test Architect Skill across AI Coding Agents
# Supports: Antigravity, Cursor, Claude Code, GitHub Copilot, Windsurf, Cline / Roo Code.

set -euo pipefail

SKILL_NAME="test-architect"
SCRIPT_SOURCE="${BASH_SOURCE[0]:-}"
SCRIPT_DIR=""
if [ -n "$SCRIPT_SOURCE" ] && [ -f "$SCRIPT_SOURCE" ]; then
  SCRIPT_DIR="$(cd "$(dirname "$SCRIPT_SOURCE")" && pwd)"
fi
TARGET_ROOT="${1:-.}"
REPOSITORY="${TEST_ARCHITECT_REPOSITORY:-duonget/test-architect}"
REF="${TEST_ARCHITECT_REF:-main}"
TEMP_DIR=""

cleanup() {
  if [ -n "$TEMP_DIR" ] && [ -d "$TEMP_DIR" ]; then
    rm -rf "$TEMP_DIR"
  fi
}

trap cleanup EXIT

# A script streamed through stdin has no adjacent repository payload. Download
# the requested revision first, then install from that isolated copy.
if [ -n "${TEST_ARCHITECT_SOURCE_DIR:-}" ]; then
  SCRIPT_DIR="$(cd "$TEST_ARCHITECT_SOURCE_DIR" && pwd)"
elif [ -z "$SCRIPT_DIR" ] || [ ! -f "$SCRIPT_DIR/SKILL.md" ] || [ ! -d "$SCRIPT_DIR/scripts" ] || [ ! -d "$SCRIPT_DIR/templates" ]; then
  TEMP_DIR="$(mktemp -d "${TMPDIR:-/tmp}/test-architect.XXXXXX")"
  ARCHIVE_URL="${TEST_ARCHITECT_ARCHIVE_URL:-https://github.com/$REPOSITORY/archive/$REF.tar.gz}"

  command -v curl >/dev/null 2>&1 || { echo "Error: curl is required for streamed installation." >&2; exit 1; }
  command -v tar >/dev/null 2>&1 || { echo "Error: tar is required for streamed installation." >&2; exit 1; }

  echo "Downloading Test Architect revision '$REF'..."
  curl --fail --silent --show-error --location "$ARCHIVE_URL" \
    | tar -xz --strip-components=1 -C "$TEMP_DIR"
  SCRIPT_DIR="$TEMP_DIR"
fi

for required_path in SKILL.md AGENTS.md scripts templates; do
  if [ ! -e "$SCRIPT_DIR/$required_path" ]; then
    echo "Error: installation payload is missing '$required_path'." >&2
    exit 1
  fi
done

echo ""
echo "Test Architect: Universal Agent Skill Installer"
echo "========================================================"
echo "Inspecting target repository: $TARGET_ROOT"
echo ""

INSTALLED_AGENTS=()

# 1. Antigravity Skill Integration (.agents/skills/)
mkdir -p "$TARGET_ROOT/.agents/skills/$SKILL_NAME/scripts"
mkdir -p "$TARGET_ROOT/.agents/skills/$SKILL_NAME/templates"
cp "$SCRIPT_DIR/SKILL.md" "$TARGET_ROOT/.agents/skills/$SKILL_NAME/SKILL.md"
cp -r "$SCRIPT_DIR/scripts/"* "$TARGET_ROOT/.agents/skills/$SKILL_NAME/scripts/"
cp -r "$SCRIPT_DIR/templates/"* "$TARGET_ROOT/.agents/skills/$SKILL_NAME/templates/"
chmod +x "$TARGET_ROOT/.agents/skills/$SKILL_NAME/scripts/"*.sh "$TARGET_ROOT/.agents/skills/$SKILL_NAME/scripts/"*.py 2>/dev/null || true
INSTALLED_AGENTS+=("Google Antigravity (.agents/skills/$SKILL_NAME)")

# 2. Universal AGENTS.md
if [ ! -f "$TARGET_ROOT/AGENTS.md" ]; then
  cp "$SCRIPT_DIR/AGENTS.md" "$TARGET_ROOT/AGENTS.md"
  INSTALLED_AGENTS+=("Universal AGENTS.md (Root context)")
else
  # Append notice if not already present
  if ! grep -q "Test Architect" "$TARGET_ROOT/AGENTS.md"; then
    printf '\n\n---\n' >> "$TARGET_ROOT/AGENTS.md"
    cat "$SCRIPT_DIR/AGENTS.md" >> "$TARGET_ROOT/AGENTS.md"
    INSTALLED_AGENTS+=("Universal AGENTS.md (Appended)")
  fi
fi

# 3. Cursor Rules Integration (.cursor/rules/)
mkdir -p "$TARGET_ROOT/.cursor/rules"
cat << 'EOF' > "$TARGET_ROOT/.cursor/rules/test-architect.mdc"
---
description: Test Architect - Senior Quality Engineering & Automated Testing Guidelines
globs: **/*.test.*,**/*.spec.*,**/tests/**,**/test/**
---

# Test Architect Guidelines
When writing or refactoring unit, integration, or regression tests:
1. Always formulate the 5-Dimensional Test Matrix (Happy Path, Boundary, Nullability, Failure Modes, Concurrency).
2. Strictly follow AAA Pattern (Arrange, Act, Assert).
3. Minimum Viable Mocking (MVM): Only mock external I/O (Network, DB). NEVER mock internal business logic.
4. Zero Tautology: Never write tests that cannot fail (e.g. expect(true).toBe(true)).
5. For full guidelines, inspect .agents/skills/test-architect/SKILL.md or AGENTS.md.
EOF
INSTALLED_AGENTS+=("Cursor (.cursor/rules/test-architect.mdc)")

# 4. GitHub Copilot Instructions (.github/copilot-instructions.md)
mkdir -p "$TARGET_ROOT/.github"
if [ ! -f "$TARGET_ROOT/.github/copilot-instructions.md" ]; then
  cat << 'EOF' > "$TARGET_ROOT/.github/copilot-instructions.md"
# GitHub Copilot Instructions: Test Architect Quality Gate

When generating unit or integration tests:
- Apply the 5-Dimensional Test Matrix (Happy Path, Boundary, Nullability, Failure Modes, Concurrency).
- Follow AAA (Arrange, Act, Assert) structure.
- Never mock internal business logic or system under test; only mock external boundary APIs.
- Refer to AGENTS.md for full testing guidelines.
EOF
  INSTALLED_AGENTS+=("GitHub Copilot (.github/copilot-instructions.md)")
fi

# 5. Claude Code / Windsurf / Cline Rules
if [ ! -f "$TARGET_ROOT/CLAUDE.md" ]; then
  cat << 'EOF' > "$TARGET_ROOT/CLAUDE.md"
# CLAUDE.md

## Testing Standards (Test Architect)
When authoring or updating tests:
- Always cover 5 dimensions: Happy Path, Boundary, Nullability, Failure Modes, Concurrency.
- Never mock internal domain logic; mock only external network/DB boundaries.
- Run tests via terminal and self-heal any failures before concluding.
- Reference: AGENTS.md and .agents/skills/test-architect/SKILL.md
EOF
  INSTALLED_AGENTS+=("Claude Code (CLAUDE.md)")
fi

if [ ! -f "$TARGET_ROOT/.clinerules" ]; then
  cat << 'EOF' > "$TARGET_ROOT/.clinerules"
# Cline / Roo Code Rules: Test Architect
Follow the 5-Dimensional Test Matrix and Minimum Viable Mocking rules defined in AGENTS.md when writing test suites.
EOF
  INSTALLED_AGENTS+=("Cline / Roo Code (.clinerules)")
fi

if [ ! -f "$TARGET_ROOT/.windsurfrules" ]; then
  cat << 'EOF' > "$TARGET_ROOT/.windsurfrules"
# Windsurf Rules: Test Architect
Follow the 5-Dimensional Test Matrix and Minimum Viable Mocking rules defined in AGENTS.md when writing test suites.
EOF
  INSTALLED_AGENTS+=("Windsurf (.windsurfrules)")
fi

echo "Installation Complete! Configured for:"
for agent in "${INSTALLED_AGENTS[@]}"; do
  echo "  + $agent"
done

echo ""
echo "Ready to use! Simply prompt your agent:"
echo "   'Write tests for <filename> using test-architect'"
echo ""
