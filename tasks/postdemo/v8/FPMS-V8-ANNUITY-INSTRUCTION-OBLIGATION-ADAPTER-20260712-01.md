# FPMS-V8-ANNUITY-INSTRUCTION-OBLIGATION-ADAPTER-20260712-01

Status: READY FOR HIGH / ULTRA CONTRACT FROZEN 2026-07-15 / NOT STARTED
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `12. Wave 4 — fee-obligation module and fixed rules`
Catalog ordinal: `121`
Executor role: Backend Developer / worker

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- Source catalog line: `558`
- Expected manifest phase: `foundation`
- Customer gate requirement: `None`

## Story Shape Classification

- `shared_file_density`: high
- `prereq_dependency_density`: low
- `be_fe_coupling`: low
- `evidence_cost`: medium
- `chosen_runbook`: `P0-single-lane-story`

## Task Contract Profile

Task Contract Profile: `TC-ADAPTER`

- RED expectation: Exact adapter test proves the old direct write/missing activity/premature state.
- GREEN expectation: Exact adapter test plus listed inherited regressions pass; only the named entrypoint changes.

## Exact Closure Slice

Existing annuity instruction action records instruction on the exact yearly obligation.

## Explicit Non-Closure

No change to the underlying deep-module rule, no second entrypoint and no unrelated refactor. Do not absorb another V8 catalog row, a second closure slice, an unresolved customer policy or unrelated cleanup.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-FO-CLIENT-INSTRUCTION-20260712-01`

### External, gate and inherited prerequisites

- None

- Approved source dependency cell (verbatim): client instruction

### Shared ownership serialization

- `backend/app/modules/annuity/service.py` order key `2`; project this order only across owners present in the active manifest.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-ANNUITY-INSTRUCTION-OBLIGATION-ADAPTER-20260712-01.md`
- `backend/app/modules/annuity/service.py`
- `backend/tests/test_v8_annuity_instruction_obligation_adapter.py`
- `artifacts/FPMS-V8-ANNUITY-INSTRUCTION-OBLIGATION-ADAPTER-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.
- Reuse deep-module activity identity; the existing financial action must not append a duplicate activity.

## Verification Commands

- RED command: `cd backend && .venv/bin/pytest -q tests/test_v8_annuity_instruction_obligation_adapter.py`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `cd backend && .venv/bin/pytest -q tests/test_v8_annuity_instruction_obligation_adapter.py`
- `cd backend && .venv/bin/ruff check --fix app/modules/annuity/service.py tests/test_v8_annuity_instruction_obligation_adapter.py && .venv/bin/ruff format app/modules/annuity/service.py tests/test_v8_annuity_instruction_obligation_adapter.py && .venv/bin/ruff check app/modules/annuity/service.py tests/test_v8_annuity_instruction_obligation_adapter.py`
- `git diff --check -- backend/app/modules/annuity/service.py backend/tests/test_v8_annuity_instruction_obligation_adapter.py tasks/postdemo/v8/FPMS-V8-ANNUITY-INSTRUCTION-OBLIGATION-ADAPTER-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-ANNUITY-INSTRUCTION-OBLIGATION-ADAPTER-20260712-01`
- Evidence validation: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-ANNUITY-INSTRUCTION-OBLIGATION-ADAPTER-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-ANNUITY-INSTRUCTION-OBLIGATION-ADAPTER-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted change makes the exact GREEN and targeted regressions pass; task-scoped lint/format/scope checks pass; shared files and SQLite verification were serialized; dirty-baseline and baseline-subtracted diff evidence exist; an independent reviewer approves the exact closure and non-closure; atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-ANNUITY-INSTRUCTION-OBLIGATION-ADAPTER-20260712-01` pass. Only then may this task be reported PASS.

## Delta-4 Ultra Contract Freeze — 2026-07-15

### Latest-wins authority and prerequisites

- Authority: `docs/superpowers/specs/2026-07-15-fpms-v8-ultra-contract-freeze-delta-4.md`
  lines 643–660 and supplemental batch row `24 / M4-F / H4-5`.
- Risk is `HIGH`; `chosen_runbook: P0-prereq-heavy-story` is latest-wins. The inherited
  body remains history, and the existing Allowed Files list is unchanged.
- Exact `backend/app/modules/annuity/service.py` execution order is D4-11 carrier PASS →
  Task 133 `FPMS-V8-FUTURE-ANNUITY-OBLIGATION-20260712-01` PASS → this Task 121.
- D4-11 is exactly `FPMS-V8-ANNUITY-TASK-OBLIGATION-LINEAGE-CARRIER-20260715-01`; the
  accepted `FPMS-V8-FO-CLIENT-INSTRUCTION-20260712-01` deep service must also PASS.
- No owner may overlap `annuity/service.py`; SQLite-writing verification remains globally
  serialized with maximum writer one.

### Exact obligation-instruction adapter closure

- Implement only `record_annuity_task_instruction(command, transaction)` with command
  fields exactly `annuity_task_id`, `instruction`, `actor_id`, `idempotency_key`.
- Accepted instruction mapping is identity-preserving and exhaustive: `PAY` → `PAY`,
  `HOLD` → `HOLD`, and `ABANDON` → `ABANDON`. `DEFER` is invalid 400 and must never map
  to `HOLD`; missing, unknown, coerced or legacy values are not accepted.
- Resolve only the named persisted annuity task and its exact `fee_obligation_id`; never
  select latest, infer from case/year/source, inspect legacy `client_instruction`, or
  create an obligation.
- Require the D4-11 carrier's six fields all non-null and mutually consistent:
  `source_activity_id`, `source_document_id`, `source_evidence_version_id`,
  `source_evidence_content_hash`, `fee_obligation_id`, and `grant_fee_year_key`.
- The linked obligation, recognition activity and document evidence must be exactly the
  same-case Task 133 facts: obligation type `FUTURE_ANNUITY`, matching fee year, exact
  source activity/document/version/hash, and full lowercase `sha256:<64-hex>` hash.
- Zero/multiple/missing links use the accepted 404; cross-case, wrong obligation type/year,
  partial carrier, malformed hash, mismatched source/evidence or contradictory identity
  uses the accepted 409. Every failure occurs before delegation or durable mutation.
- Delegate exactly once to `record_client_instruction()` with the resolved obligation ID,
  exact mapped instruction, unchanged nonblank authenticated `actor_id`, and unchanged
  `idempotency_key`; do not synthesize actor, evidence, timestamp or another key.
- The accepted deep service's empty instruction evidence tuple remains exact. Its unique
  recognition source activity, actor and append-only `FEE_CLIENT_INSTRUCTION_RECORDED`
  activity are the audit facts; this adapter adds no attachment or evidence reference.

### Replay, transaction and fail-closed boundary

- Exact replay of the same task/link/obligation/instruction/actor/key delegates to the deep
  replay contract, reuses the original activity/result and writes nothing.
- Same key with changed task, obligation, instruction, actor, lineage, source/evidence or
  activity facts is 409. A new key targeting the current instruction remains the accepted
  same-state 409; no conflict is remapped to success.
- The caller owns one transaction. The adapter and delegated service perform no internal
  commit or outer rollback; caller rollback removes every instruction header/activity/
  revision effect, and no partial or duplicate activity survives.
- Never mutate legacy `client_instruction`, annuity source/rate/lineage, obligation facts
  other than the accepted instruction header, case lifecycle/status, draft, payment,
  evidence, document, PayList or fee calculation state.

### Materialization non-closure

- This materialization changes only Status and this EOF appendix. No adapter/product/test,
  migration, evidence bundle, allowlist, prior task bytes or dependency implementation is
  edited or initialized.
- Only atomic `check-task` runs now; TDD, targeted tests/lint, Evidence 1.1, independent
  review, task gates and all product execution remain deferred to High.
