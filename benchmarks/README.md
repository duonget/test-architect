# Reproducible bug-detection benchmark

This benchmark measures **seeded bugs caught**, not coverage or generated test count.
It contains three small Python standard-library cases and nine independently applied
bugs: discount/shipping thresholds and rounding, payment duplication/conflicts/retry,
and pagination empty-page handling/deduplication/partial failure.

## Verify the fixtures

Requires Python 3.11+ on Linux or macOS:

```bash
python3 benchmarks/evaluate.py --tests benchmarks/reference --require-all
```

Reference tests are hand-written contract checks. Their score verifies the benchmark
fixtures; **it is not evidence of improvement from AI or from Test Architect**.
No measured AI A/B results are published yet.

## Run a controlled A/B trial

1. Record the repository commit, exact model version, agent version, sampling settings,
   token/time budget and tool permissions. Use one model and identical budgets.
2. Create fresh external workspaces for each case and trial. Copy only that case's
   `SPEC.md` and `solution.py`. Do not expose this repository, reference tests,
   mutant definitions, evaluator output or previous runs to the generation agent.
3. In condition A, use the agent's default environment with no Test Architect rules.
   In condition B, provide the same environment plus the pinned `SKILL.md` and its
   required supporting files. Record exactly what was added; avoid global rules
   contaminating condition A. The benchmark's tests-only constraint applies to both.
4. Use the same prompt below. Run at least three independent trials per condition
   per case (18 generations total). Alternate A/B execution order.
5. Export only `test_*.py` files into `submissions/<condition>/<trial>/<case>/`.
   Keep the source immutable. Evaluate only after test generation is complete:

```bash
python3 benchmarks/evaluate.py --tests submissions/A/1
python3 benchmarks/evaluate.py --tests submissions/B/1
```

Prompt:

> Write Python unittest tests for solution.py against SPEC.md. Only create or modify
> test_*.py files. Do not modify the implementation or specification. Mock only external
> I/O boundaries. Run your tests against the supplied implementation and report the
> command and result. You have the same stated time/token budget as the other trials.

Save full JSON evaluator output, prompts, generated tests and agent transcripts.
Record elapsed time and tokens from actual agent logs; mark unavailable fields as
unknown. Manually review internal mocking and source-reading tricks before comparing
scores. Report every trial, invalid baselines and variation, not just the best runs.
Do not feed evaluation results back into generation for the primary comparison.

## Scoring and limitations

- A correct-source baseline must pass with at least one test and no skipped tests.
- A mutant is caught only by assertion failures without unittest errors. Unexpected
  exceptions, import errors, timeouts and empty suites are inconclusive, not kills.
  This conservative rule may undercount genuine exception-based detection; retain logs.
- Each baseline/mutant uses a fresh temporary directory. Fixtures are never edited.
- Only top-level `test_*.py` submissions using the standard library are supported.
- Temporary directories provide filesystem isolation, **not a security sandbox**.
  Execute trusted tests only. Candidate code must not inspect source or this benchmark.
- Small public fixtures can be overfit. Results do not establish production reliability
  or universal superiority across models, languages or repositories.
- A funded/model-backed A/B run must be performed separately; fixture verification alone
  must never be presented as an AI benchmark result.
