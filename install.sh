#!/usr/bin/env bash
# install.sh
# Installs the Test Architect skill into the target project or global Agent configuration.

set -euo pipefail

SKILL_NAME="test-architect"
TARGET_DIR="${1:-.agents/skills/$SKILL_NAME}"

echo "🏛️  Installing Test Architect Skill into: $TARGET_DIR ..."

mkdir -p "$TARGET_DIR/scripts"
mkdir -p "$TARGET_DIR/templates"

# Copy core skill and assets
cp SKILL.md "$TARGET_DIR/SKILL.md"
cp -r scripts/* "$TARGET_DIR/scripts/"
cp -r templates/* "$TARGET_DIR/templates/"

# Make scripts executable
chmod +x "$TARGET_DIR/scripts/"*.sh "$TARGET_DIR/scripts/"*.py 2>/dev/null || true

echo "✅ Test Architect Skill successfully installed!"
echo ""
echo "🚀 How to activate with your AI Agent:"
echo "  • Antigravity: Already active! Simply prompt: 'Write tests for <file> using test-architect'"
echo "  • Claude Code: Mounts via standard skills or reference in CLAUDE.md"
echo "  • Cursor / Cline: Symlink or reference in .cursorrules / .clinerules"
echo ""
