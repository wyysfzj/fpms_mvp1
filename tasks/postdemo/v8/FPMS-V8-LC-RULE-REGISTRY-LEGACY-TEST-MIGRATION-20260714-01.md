# FPMS-V8-LC-RULE-REGISTRY-LEGACY-TEST-MIGRATION-20260714-01

Status: PASS / INDEPENDENT REVIEW APPROVED / MAIN ACCEPTED 2026-07-14
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01` (`V8`)
Wave: `M5 — foundation external prerequisites (delta-2)`
Phase: `foundation_external_prerequisite` (delta-2; outside the immutable baseline)
Executor role: Tester / monitor

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/specs/2026-07-14-fpms-v8-ultra-contract-freeze-delta-2.md`
- `docs/superpowers/plans/2026-07-14-fpms-v8-ultra-contract-materialization-2.md`
- `tasks/postdemo/v8/FPMS-V8-LC-CASE-OPENED-20260712-01.md`
- Materialization row: `01`
- Expected manifest phase: `foundation_external_prerequisite`
- Immutable baseline membership: `outside`
- Customer gate requirement: `None`

## Story Shape Classification

- `shared_file_density`: low
- `prereq_dependency_density`: low
- `be_fe_coupling`: low
- `evidence_cost`: medium
- `chosen_runbook`: `P0-single-lane-story`

## Task Contract Profile

Task Contract Profile: `TC-QA`

- RED expectation: An exact static contract assertion fails while the unchanged accepted
  test file still contains the obsolete
  `get_lifecycle_rule("FILING_PREPARATION_STARTED") is None` literal.
- GREEN expectation: The same static assertion and targeted test file pass after the
  single assertion literal is migrated to a genuinely unregistered event, while every
  exact `CASE_OPENED` regression remains unchanged and green.

## Exact Closure Slice

Migrate one obsolete negative registry assertion in
`backend/tests/test_v8_lifecycle_case_opened.py`: replace only
`get_lifecycle_rule("FILING_PREPARATION_STARTED") is None` with
`get_lifecycle_rule("UNREGISTERED_EVENT") is None`, preserving all exact
`CASE_OPENED` tests and assertions.

## Ultra Contract Freeze — 2026-07-14

This is one test-semantic migration prerequisite, not a lifecycle product task.

### Exact one-line migration

- In `test_registry_resolves_only_exact_case_opened_with_frozen_signature`, change only
  the event literal in the obsolete negative assertion:

```python
assert module.get_lifecycle_rule("UNREGISTERED_EVENT") is None
```

- Do not rename the test, rewrite helpers or fixtures, reorder assertions, or change any
  other line in the test file.
- Preserve the exact `CASE_OPENED` callable, signature, decision, projection,
  `oa_sequence=None`, malformed-command, initialized-projection and zero-transaction
  interaction regressions.
- Preserve the existing negative checks for lowercase `case_opened`, `None` and the
  non-string list input. `UNREGISTERED_EVENT` is the one exact unknown-event sentinel.
- Do not make the inherited test aware of the implementation details of the second rule.

### Frozen RED / GREEN sequence

1. Confirm the accepted `CASE_OPENED` dependency and its existing PASS evidence.
2. Run the exact static contract assertion against the unchanged test file. It must fail
   because the obsolete `FILING_PREPARATION_STARTED is None` literal is still present.
3. Change only that assertion literal to `UNREGISTERED_EVENT`.
4. Rerun the same static assertion and the targeted pytest to GREEN, then run only
   task-scoped Ruff, diff, review, task and atomic-evidence gates.

The targeted pytest is not a RED before the downstream rule exists. RED is the static
contract check and must not be manufactured by changing lifecycle source. GREEN is only
the one-line test-semantic migration and does not authorize event registration.

## Explicit Non-Closure

No lifecycle source, rule implementation, event registration, registry behavior,
contract, service, API, schema, migration, seed, UI or other product work. Do not modify
the accepted `CASE_OPENED` semantics, implement `FILING_PREPARATION_STARTED`, absorb a
second lifecycle event, edit another test or perform unrelated cleanup.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-LC-CASE-OPENED-20260712-01` — accepted `PASS` before this migration.

### External, gate and inherited prerequisites

- This task is an external Foundation prerequisite introduced by the approved delta-2.
- Customer gate: `None`.

### Shared ownership serialization

- Never run concurrently with another owner editing
  `backend/tests/test_v8_lifecycle_case_opened.py`.
- Complete this migration before the follow-up registers the second lifecycle rule.

## Remaining Follow-Up Task IDs

- `FPMS-V8-LC-FILING-PREPARATION-STARTED-20260712-01`

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-LC-RULE-REGISTRY-LEGACY-TEST-MIGRATION-20260714-01.md`
- `backend/tests/test_v8_lifecycle_case_opened.py`
- `artifacts/FPMS-V8-LC-RULE-REGISTRY-LEGACY-TEST-MIGRATION-20260714-01/**`

No lifecycle source, other product file, other test, task, manifest or catalog file is
authorized. Preserve the captured dirty baseline.

## Runtime Contracts

- This task changes no runtime behavior and performs no database or network access.
- `get_lifecycle_rule("UNREGISTERED_EVENT")` must remain a no-rule observation; this
  task must not create that behavior in product source.
- The accepted `CASE_OPENED` public registry and rule contracts remain authoritative.

## Verification Commands

- Dependency gate: `./scripts/task_validate.sh FPMS-V8-LC-CASE-OPENED-20260712-01`
- RED static contract check: `python3 -c 'from pathlib import Path; text = Path("backend/tests/test_v8_lifecycle_case_opened.py").read_text(); obsolete = "assert module.get_lifecycle_rule(\"FILING_PREPARATION_STARTED\") is None"; assert obsolete not in text, obsolete'`; before editing, this exact command must exit nonzero because the obsolete literal is present.
- GREEN static contract check: rerun the exact RED command after the one-line migration;
  it must exit zero.
- GREEN targeted test: `cd backend && .venv/bin/pytest -q tests/test_v8_lifecycle_case_opened.py`
- Scoped Ruff: `cd backend && .venv/bin/ruff check --fix tests/test_v8_lifecycle_case_opened.py && .venv/bin/ruff format tests/test_v8_lifecycle_case_opened.py && .venv/bin/ruff check tests/test_v8_lifecycle_case_opened.py`
- Scoped diff: `git diff --check -- backend/tests/test_v8_lifecycle_case_opened.py tasks/postdemo/v8/FPMS-V8-LC-RULE-REGISTRY-LEGACY-TEST-MIGRATION-20260714-01.md`
- Task gate: `./scripts/task_validate.sh FPMS-V8-LC-RULE-REGISTRY-LEGACY-TEST-MIGRATION-20260714-01`
- Evidence gate: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-LC-RULE-REGISTRY-LEGACY-TEST-MIGRATION-20260714-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

Expected HTTP status codes: `None` (test-only registry migration; no endpoint).

## Evidence Path

- `artifacts/FPMS-V8-LC-RULE-REGISTRY-LEGACY-TEST-MIGRATION-20260714-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, plus
  `baseline_allowlist.diff` and `baseline_external_files.txt` because execution starts
  from a dirty worktree.

## Done Definition

The accepted dependency remains PASS; the exact static obsolete-literal check is captured
failing before the edit and passing after it; only the one event literal changes; the
targeted pytest is GREEN; every exact `CASE_OPENED` regression is preserved; task-scoped
Ruff and diff checks pass; dirty baseline and baseline-subtracted scope evidence prove no
lifecycle source or second closure changed; independent review, task gate and atomic
evidence validation pass. Only then may this implementation task be reported PASS.
