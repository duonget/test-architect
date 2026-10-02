#!/usr/bin/env bash
# demo-simulation.sh
# Realistic terminal simulation script for recording 15s social media demos (MP4/GIF).

set -euo pipefail

# ANSI Colors
BOLD="\033[1m"
CYAN="\033[36m"
GREEN="\033[32m"
MAGENTA="\033[35m"
DIM="\033[2m"
RESET="\033[0m"

type_text() {
  local text="$1"
  local delay="${2:-0.03}"
  for ((i=0; i<${#text}; i++)); do
    echo -n "${text:$i:1}"
    sleep "$delay"
  done
  echo ""
}

clear
sleep 0.5

echo -n "$ "
type_text "curl -fsSL https://raw.githubusercontent.com/duonget/test-architect/main/install.sh | bash" 0.02
sleep 0.4

echo -e "${CYAN}[INFO]${RESET} Installed skill across: Antigravity, Cursor, Claude Code, Copilot, Cline"
echo -e "${GREEN}[PASS]${RESET} Universal AGENTS.md and .cursor/rules configured successfully."
sleep 0.8

echo ""
echo -n "> "
type_text 'agent "Write unit tests for src/services/payment.ts using test-architect"' 0.025
sleep 0.6

echo ""
echo -e "${CYAN}${BOLD}[Test Architect Activated]${RESET}"
sleep 0.4
echo -e "├── Phase 1: Discovered Test Runner -> ${BOLD}Vitest (v2.1)${RESET}"
sleep 0.4
echo -e "├── Phase 2: Formulated 5-D Matrix (Happy, Boundary, Null, Failure, Concurrency)"
sleep 0.4
echo -e "├── Phase 3: Authored payment.test.ts (Strict AAA + Minimum Viable Mocking)"
sleep 0.6
echo -e "├── Phase 4: Autonomous Run -> ${GREEN}${BOLD}11 passed (100% GREEN)${RESET}"
sleep 0.5
echo -e "├── Phase 5: Mutation Sanity Check -> ${MAGENTA}${BOLD}[KILLED]${RESET} 2 injected mutants defeated"
sleep 0.5
echo ""
echo -e "${GREEN}${BOLD}[SUCCESS] All 11 tests verified bulletproof. Ready to commit!${RESET}"
echo ""
sleep 1
