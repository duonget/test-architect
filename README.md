<p align="center">
  <h1 align="center">🏛️ Test Architect</h1>
  <p align="center">
    <strong>The Open-Source Quality Engineering Skill for AI Coding Agents.</strong><br>
    <em>Stop AI agents from writing shallow "happy path" tests and mocking away your bugs.</em>
  </p>
  <p align="center">
    <a href="./LICENSE"><img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License" /></a>
    <img src="https://img.shields.io/badge/Agent-Antigravity%20|%20Claude%20Code%20|%20Cursor%20|%20Cline-blue.svg" alt="Compatibility" />
    <img src="https://img.shields.io/badge/Languages-TS%20|%20Python%20|%20Go%20|%20Rust-orange.svg" alt="Languages" />
    <a href="https://github.com/your-username/test-architect/pulls"><img src="https://img.shields.io/badge/PRs-welcome-purple.svg" alt="PRs Welcome" /></a>
  </p>
</p>

---

## 💥 The Problem with AI-Generated Tests

When developers ask modern coding agents (Cursor, Claude, Devin, Copilot) to *"write unit tests"*, agents notoriously fail in 4 ways:

1. **Happy Path Myopia**: They write 1–2 tests for when everything goes right and call it a day.
2. **Over-Mocking**: They mock out internal classes, helpers, and business logic until the test passes while production code is completely broken.
3. **Zero Boundary Awareness**: They ignore empty arrays, negative numbers, numeric overflows, and race conditions.
4. **Tautological Assertions**: They generate assertions that cannot fail (e.g. asserting mocked return values).

---

## 🛡️ The Solution: Test Architect Skill

**Test Architect** is an **Agent-Native Skill** (`SKILL.md`) that injects senior test engineering rigor into your AI coding agent. When mounted, your agent automatically executes like a Senior QA Lead.

```
       [ Developer Prompt: "Write tests for payment.ts" ]
                               │
                               ▼
        ┌──────────────────────────────────────────────┐
        │  1. Automated Discovery                      │
        │  Runs detect-runner.sh to identify Vitest,   │
        │  Jest, Pytest, Go test, or Cargo.            │
        └──────────────────────┬───────────────────────┘
                               ▼
        ┌──────────────────────────────────────────────┐
        │  2. The 5-Dimensional Test Matrix            │
        │  Formulates explicit matrix: Happy Path,     │
        │  Boundary, Nullability, Failures, Concurrency│
        └──────────────────────┬───────────────────────┘
                               ▼
        ┌──────────────────────────────────────────────┐
        │  3. AAA & Minimum Viable Mocking (MVM)       │
        │  Authors tests mocking ONLY external I/O     │
        │  (never mock business logic!).               │
        └──────────────────────┬───────────────────────┘
                               ▼
        ┌──────────────────────────────────────────────┐
        │  4. Autonomous Execution & Self-Healing      │
        │  Runs suite in terminal -> reads failures -> │
        │  repairs code/tests until 100% GREEN.        │
        └──────────────────────┬───────────────────────┘
                               ▼
        ┌──────────────────────────────────────────────┐
        │  5. Mutation Sanity Check                    │
        │  Inverts code logic to prove test suite      │
        │  genuinely catches bugs (kills mutations).   │
        └──────────────────────────────────────────────┘
```

---

## ⚡ Quick Start (1-Minute Setup)

### Option 1: Automatic 1-Line Install into your Project

Run this command inside your project repository root:

```bash
curl -fsSL https://raw.githubusercontent.com/your-username/test-architect/main/install.sh | bash
```

### Option 2: Mount into your favorite AI Agent

*   **Google Antigravity**:
    Copy this repo into `.agents/skills/test-architect/` inside your project or `~/.gemini/config/skills/test-architect/` globally.
*   **Claude Code**:
    Reference `SKILL.md` in your project's `CLAUDE.md`.
*   **Cursor / Cline / Roo Code**:
    Add the instructions in `SKILL.md` to your `.cursorrules` or `.clinerules`.

---

## 🏛️ The 5 Golden Disciplines Enforced by the Skill

| Discipline | Rule | What It Prevents |
| :--- | :--- | :--- |
| **1. 5-D Test Matrix** | Happy Path + Boundary + Nulls + Failure Modes + Concurrency | Shallow 1-line tests |
| **2. Minimum Viable Mocking (MVM)** | Only mock external network/DB; **NEVER** mock business logic | False-confidence tests that pass broken code |
| **3. Strict AAA Pattern** | Every test has clear Arrange, Act, and Assert blocks | Messy, unreadable spaghetti tests |
| **4. Zero Tautology** | Reject `expect(true).toBe(true)` and circular mocks | "Fake" tests written just to boost line coverage |
| **5. Mutation Sanity** | If flipping `>` to `>=` doesn't break tests, the test is defective | Undetected regression bugs in production |

---

## 📂 Repository Structure

```
test-architect/
├── SKILL.md                 # Core Skill specification (YAML frontmatter + instructions)
├── README.md                # Documentation & Quickstart
├── LICENSE                  # MIT License
├── install.sh               # 1-line installer script
├── scripts/
│   ├── detect-runner.sh     # Auto-detects Vitest, Jest, PyTest, Go test, Cargo
│   └── mutation-check.py    # Injects logic mutations to verify test strength
├── templates/               # Production-grade AAA test templates
│   ├── typescript-vitest.ts
│   ├── python-pytest.py
│   └── go-testing.go
└── examples/
    └── payment-workflow/    # Complete real-world PaymentService example
        ├── payment.ts       # Source code under test
        ├── test-matrix.md   # 5-D Matrix generated by the Agent
        └── payment.test.ts  # Robust, architect-level test suite
```

---

## 🔬 Mutation Sanity Check in Action

Test Architect includes `scripts/mutation-check.py` to prevent "fake tests":

```bash
python3 scripts/mutation-check.py \
  --target src/services/payment.ts \
  --test "npx vitest run src/services/payment.test.ts"
```

**Output:**
```text
🛡️  [Test Architect] Running baseline test before mutation...
✓ Baseline tests PASS cleanly.

🔬 Testing up to 3 logic mutations in payment.ts...
  ✓  MUTATION KILLED: Invert strict inequality ( > to >= )
      Tests correctly FAILED when logic was altered. Strong assertion detected!
  ✓  MUTATION KILLED: Invert equality ( == to != )
      Tests correctly FAILED when logic was altered. Strong assertion detected!

=======================================================
Mutation Sanity Summary: 2 Killed, 0 Survived.
🎉 Excellent! Your test suite successfully caught all injected logic mutations.
=======================================================
```

---

## 🤝 Contributing

We welcome contributions! You can:
1. Add new test runner detectors in `scripts/detect-runner.sh` (e.g. JUnit, RSpec, Elixir).
2. Add new framework templates in `templates/` (e.g. NestJS, FastAPI, Spring Boot).
3. Improve mutation operators in `scripts/mutation-check.py`.

---

## 📄 License

[MIT License](./LICENSE) © 2025-2026 Test Architect Contributors.
