<p align="center">
  <h1 align="center">Test Architect</h1>
  <p align="center">
    <strong>Vendor-neutral testing skills and tools for AI coding agents.</strong><br>
    <em>Stop AI agents from writing shallow "happy path" tests and mocking away your bugs.</em>
  </p>
  <p align="center">
    <a href="./LICENSE"><img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License" /></a>
    <a href="#agent-compatibility-matrix"><img src="https://img.shields.io/badge/Agents-Multi--platform-blue.svg" alt="Multi-platform agent integrations" /></a>
    <img src="https://img.shields.io/badge/Languages-TypeScript%20|%20Python%20|%20Go%20|%20Rust-orange.svg" alt="Languages" />
    <a href="https://github.com/duonget/test-architect/actions/workflows/ci.yml"><img src="https://github.com/duonget/test-architect/actions/workflows/ci.yml/badge.svg" alt="CI Status" /></a>
    <a href="https://github.com/duonget/test-architect/pulls"><img src="https://img.shields.io/badge/PRs-welcome-purple.svg" alt="PRs Welcome" /></a>
  </p>
  <p align="center">
    <img src="./assets/demo.svg" alt="Test Architect Terminal Demo" width="820" />
  </p>
</p>

---

## The "AI Testing Pandemic"

During rapid AI-assisted coding sessions, generated tests can create a **false sense of security**, regardless of the agent or model provider:

```
The Naive AI Testing Trap:
   • 1 single "Happy Path" test case.
   • Mocks out internal classes and domain logic until the test passes.
   • Ignores edge-cases, nullability, negative numbers, and race conditions.
   • Generates tautological assertions like `expect(true).toBe(true)` to fool CI.
   Result: 100% test pass rate in CI, but immediate crash in production.
```

**Test Architect** helps coding agents design tests that catch real bugs, not just pass. It combines testing instructions with lightweight verification tools; results depend on the agent, project and assertions produced.

The workflow is **vendor-neutral and model-agnostic**: no provider API key, model
subscription or hosted service is required by these scripts. Use your agent's existing
model setup. Integrations cover Claude Code, Cline/Roo Code, Cursor, GitHub Copilot,
Google Antigravity, OpenAI Codex, OpenCode and Windsurf. Other agents can read
`AGENTS.md` or load `SKILL.md` explicitly. Integration methods differ; effectiveness
across agents and models must be evaluated rather than assumed.

---

## The Showdown: Naive AI vs. Test Architect

| Dimension | Naive AI Agent (Default Behavior) | AI Agent + Test Architect Skill |
| :--- | :--- | :--- |
| **Test Matrix** | Writes 1 arbitrary happy-path test | Enforces **5-D Matrix**: Happy, Boundary, Null, Failure, Concurrency |
| **Mocking Discipline** | Mocks everything (helpers, DB, domain logic) | **Minimum Viable Mocking (MVM)**: Mocks only external network/DB |
| **Assertion Rigor** | Tautological mocks or `expect(val).toBeDefined()` | Strict **AAA Pattern** testing exact business mutations |
| **Bug Detection** | Tests pass even when logic has subtle bugs | **Mutation Resistant**: Kills inverted comparison operators |
| **Self-Healing** | Writes file and stops (hopes it works) | **Autonomous Loop**: Runs terminal, auto-fixes until 100% green |

---

## 1-Minute Universal Quickstart

Install Test Architect into your current repository with a single command:

```bash
curl -fsSL https://raw.githubusercontent.com/duonget/test-architect/main/install.sh | bash
```

The installer downloads the repository payload when streamed, installs a shared
skill under `.agents/skills/test-architect/`, and creates project instruction files
for the integrations listed [below](#agent-compatibility-matrix).

Now, simply prompt your agent:
> *"Write unit tests for `src/services/payment.ts` using the test-architect skill."*

### Use with your agent

Open the target repository in your agent and use the prompt above. For agents with
native skill discovery, select `test-architect`; for instruction-based integrations,
ask the agent to follow `AGENTS.md` and the installed `SKILL.md`.
See the platform-specific notes in the compatibility table.

The installer creates missing instruction files; existing Claude Code, Copilot,
Cline/Roo Code and Windsurf instruction files are preserved. When those files already
exist, add a reference to `AGENTS.md` and `.agents/skills/test-architect/SKILL.md` yourself.
The installer appends Test Architect instructions to `AGENTS.md` when absent and
replaces its own Cursor rule file. Global model settings and agent permissions are
not configured by this installer.

---

## Live Terminal Simulation

```text
User: "Write unit tests for payment.ts using test-architect"

[Test Architect Agent Activated]
├── Phase 1: Discovered Test Runner -> Vitest (v2.1)
├── Phase 2: Formulated 5-Dimensional Test Matrix:
│   ├── Happy Path: TC-01 (USD valid charge), TC-02 (EUR/VND currencies)
│   ├── Boundary:   TC-03 (1 cent min), TC-04 (0 cent reject), TC-06 ($10k max limit)
│   ├── Nullability:TC-08 (empty idempotency key), TC-09 (unsupported currency)
│   ├── Failure:    TC-10 (downstream gateway timeout handling)
│   └── Concurrency:TC-11 (overlapping duplicate requests), TC-12 (key conflict)
├── Phase 3: Authored payment.test.ts (Strict AAA + MVM)
├── Phase 4: Autonomous Run & Self-Healing Loop:
│   └── Running: npx vitest run src/services/payment.test.ts
│   └── Result: all cases passed (100% GREEN)
└── Phase 5: Mutation Sanity Check:
    └── Inverted `amountCents <= 0` to `< 0` -> Tests FAILED (Mutation Killed)
    └── Inverted `amountCents > 1000000` to `>=` -> Tests FAILED (Mutation Killed)
All tests and mutation checks passed. Ready to commit!
```

---

## The 5 Golden Disciplines

```
              [ Target Function / Module ]
                            │
                            ▼
     ┌──────────────────────────────────────────────┐
     │  1. The 5-Dimensional Test Matrix            │
     │  Happy Path • Boundary • Nulls • Failures    │
     │  Concurrency & Idempotency                   │
     └──────────────────────┬───────────────────────┘
                            ▼
     ┌──────────────────────────────────────────────┐
     │  2. Minimum Viable Mocking (MVM)             │
     │  Only mock external I/O (Network/DB).        │
     │  NEVER mock internal business logic.         │
     └──────────────────────┬───────────────────────┘
                            ▼
     ┌──────────────────────────────────────────────┐
     │  3. Strict AAA Pattern                       │
     │  Arrange • Act • Assert cleanly separated.   │
     └──────────────────────┬───────────────────────┘
                            ▼
     ┌──────────────────────────────────────────────┐
     │  4. Autonomous Self-Healing Loop             │
     │  Execute runner in terminal -> diagnose      │
     │  failures -> patch code/test until 100% green│
     └──────────────────────┬───────────────────────┘
                            ▼
     ┌──────────────────────────────────────────────┐
     │  5. Mutation Sanity Check                    │
     │  Prove tests catch subtle logic defects.     │
     └──────────────────────────────────────────────┘
```

---

## Mutation Sanity Check in Action

This helper uses lexical mutations, not an AST or a complete mutation-testing engine.
Use `--validate` to reject compile/type-invalid candidates. Without validation,
a nonzero test exit can include compilation failures rather than assertion failures.
It temporarily edits the target in place: run it sequentially, without other tests,
editors or mutation jobs operating on that target. The benchmark evaluator below
instead uses fresh temporary copies.

To expose weak boundary assertions, Test Architect includes a zero-dependency Python script (`scripts/mutation-check.py`) that temporarily mutates executable comparisons and boolean constants. It restores the source after every run, fails when a mutant survives, and reports invalid mutations separately:

```bash
python3 scripts/mutation-check.py \
  --target src/services/payment.ts \
  --validate "npm run typecheck" \
  --test "npx vitest run src/services/payment.test.ts"
```

```text
[Test Architect] Running baseline test before mutation...
[PASS] Baseline tests PASS cleanly.

[INFO] Testing up to 3 logic mutations in payment.ts...
  [KILLED] MUTATION KILLED: Invert strict inequality ( > to >= )
      Tests correctly FAILED when logic was altered. Strong assertion detected!
  [KILLED] MUTATION KILLED: Invert equality ( == to != )
      Tests correctly FAILED when logic was altered. Strong assertion detected!

=======================================================
Mutation Summary: 2 Killed, 0 Survived, 0 Invalid.
[SUCCESS] All valid mutations were killed by the test suite.
=======================================================
```

---

## Agent Compatibility Matrix

Platforms are listed alphabetically, not by preference. These are installation
adapters, not a claim of identical behavior or measured performance on every agent.

| AI Platform | Integration files | Usage / discovery |
| :--- | :--- | :--- |
| **Claude Code** | `CLAUDE.md` → `AGENTS.md` and shared skill | Ask to follow Test Architect testing instructions. |
| **Cline / Roo Code** | `.clinerules` → `AGENTS.md` | Ask to read the rules; adapt their reference to your client's supported rule layout if needed. |
| **Cursor** | `.cursor/rules/test-architect.mdc` | Project rule targets test files; reference Test Architect explicitly when generating new tests. |
| **GitHub Copilot** | `.github/copilot-instructions.md` | Use repository instructions when asking Copilot to write tests. |
| **Google Antigravity** | `.agents/skills/test-architect/SKILL.md` | Ask to use the `test-architect` skill. |
| **OpenAI Codex** | `.agents/skills/test-architect/SKILL.md`, `AGENTS.md` | Select via `/skills` or prompt `$test-architect Write tests for <file>`. Restart if absent. |
| **OpenCode** | `.agents/skills/test-architect/SKILL.md`, `AGENTS.md` | Restart after installation, then ask to load `test-architect`. Existing skill permissions apply. |
| **Windsurf** | `.windsurfrules` → `AGENTS.md` | Ask Cascade to follow Test Architect testing instructions. |
| **Other agents** | `AGENTS.md` / `SKILL.md` | Explicitly load the instructions if automatic discovery is unavailable. |

Native discovery references: [Codex](https://developers.openai.com/codex/skills),
[OpenCode](https://opencode.ai/docs/skills/). Both use the shared skill payload;
no additional `.opencode/skills/` copy is needed.

## Topics

Core: [#agent-skills](https://github.com/topics/agent-skills)
[#ai-agents](https://github.com/topics/ai-agents)
[#software-testing](https://github.com/topics/software-testing)
[#test-automation](https://github.com/topics/test-automation)
[#mutation-testing](https://github.com/topics/mutation-testing)
[#quality-engineering](https://github.com/topics/quality-engineering)

Integrations: [#claude-code](https://github.com/topics/claude-code)
[#cline](https://github.com/topics/cline)
[#cursor](https://github.com/topics/cursor)
[#github-copilot](https://github.com/topics/github-copilot)
[#google-antigravity](https://github.com/topics/google-antigravity)
[#codex](https://github.com/topics/codex)
[#opencode](https://github.com/topics/opencode)
[#roo-code](https://github.com/topics/roo-code)
[#windsurf](https://github.com/topics/windsurf)

---

## Contributing

### Reproducible benchmark

The [benchmark](benchmarks/README.md) includes three contract-based Python examples,
nine seeded bugs and an isolated evaluator. Run the hand-written reference checks:

```bash
python3 benchmarks/evaluate.py --tests benchmarks/reference --require-all
```

These checks validate the fixtures, not AI effectiveness. The benchmark guide defines
a controlled with/without-skill experiment; measured AI comparison results are not yet available.

We welcome community contributions! You can help expand Test Architect by:
1. Adding new language templates (`templates/`) for C# .NET, Kotlin, Rust, Elixir, PHP Pest.
2. Expanding runner detection in `scripts/detect-runner.sh`.
3. Adding new mutation operators in `scripts/mutation-check.py`.

Check out our [Contributing Guide](CONTRIBUTING.md) to get started in 15 minutes!

---

## License

[MIT License](./LICENSE) © 2025-2026 Test Architect Contributors.
