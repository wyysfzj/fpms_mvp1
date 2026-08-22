# FPMS-V8-PCT-FEE-POLICY-20260712-01

Status: READY FOR HIGH / ULTRA CONTRACT FROZEN 2026-07-15 / NOT STARTED
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `12. Wave 4 — fee-obligation module and fixed rules`
Catalog ordinal: `135`
Executor role: Backend Developer / worker

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- Source catalog line: `577`
- Expected manifest phase: `foundation`
- Customer gate requirement: `None`

## Story Shape Classification

- `shared_file_density`: low
- `prereq_dependency_density`: low
- `be_fe_coupling`: low
- `evidence_cost`: medium
- `chosen_runbook`: `P0-single-lane-story`

## Task Contract Profile

Task Contract Profile: `TC-RULE`

- RED expectation: Exact public rule test fails on the named transition/calculation.
- GREEN expectation: Exact rule test passes every named success/boundary/fail-closed case.

## Exact Closure Slice

Implement the frozen CNIPA RO/search/report national-stage exemptions and per-fee domestic reduction; no whole-PCT flag.

## Explicit Non-Closure

No second event/rate/policy, persistence adapter, endpoint, seed or UI. Do not absorb another V8 catalog row, a second closure slice, an unresolved customer policy or unrelated cleanup.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-OFFICIAL-RATE-BOOK-SOURCE-ACTIVATION-20260712-01`

### External, gate and inherited prerequisites

- None

- Approved source dependency cell (verbatim): rate book

### Shared ownership serialization

- No shared ownership chain beyond the global serialized SQLite verification queue.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-PCT-FEE-POLICY-20260712-01.md`
- `backend/app/modules/fees/pct_policy.py`
- `backend/tests/test_v8_pct_fee_policy.py`
- `artifacts/FPMS-V8-PCT-FEE-POLICY-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.

## Verification Commands

- RED command: `cd backend && .venv/bin/pytest -q tests/test_v8_pct_fee_policy.py`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `cd backend && .venv/bin/pytest -q tests/test_v8_pct_fee_policy.py`
- `cd backend && .venv/bin/ruff check --fix app/modules/fees/pct_policy.py tests/test_v8_pct_fee_policy.py && .venv/bin/ruff format app/modules/fees/pct_policy.py tests/test_v8_pct_fee_policy.py && .venv/bin/ruff check app/modules/fees/pct_policy.py tests/test_v8_pct_fee_policy.py`
- `git diff --check -- backend/app/modules/fees/pct_policy.py backend/tests/test_v8_pct_fee_policy.py tasks/postdemo/v8/FPMS-V8-PCT-FEE-POLICY-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-PCT-FEE-POLICY-20260712-01`
- Evidence validation: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-PCT-FEE-POLICY-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-PCT-FEE-POLICY-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted change makes the exact GREEN and targeted regressions pass; task-scoped lint/format/scope checks pass; shared files and SQLite verification were serialized; dirty-baseline and baseline-subtracted diff evidence exist; an independent reviewer approves the exact closure and non-closure; atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-PCT-FEE-POLICY-20260712-01` pass. Only then may this task be reported PASS.

## Delta-4 Ultra Contract Freeze — 2026-07-15

### Latest-wins authority

- Authoritative contract: `docs/superpowers/specs/2026-07-15-fpms-v8-ultra-contract-freeze-delta-4.md`, Task 135 lines 661–715.
- Supplemental authority: row `26 / M4-G / H4-4` of `tasks/batches/FPMS-POSTDEMO-V8-ULTRA-CONTRACT-DELTA-4-20260715-01.md`.
- Risk remains `HIGH`; product work and evidence remain `NOT STARTED`.
- `chosen_runbook: P0-prereq-heavy-story` supersedes the historical runbook above for Delta-4 execution.
- This appendix is latest-wins only for the exact pure-policy contract below; every other inherited byte and the exact Allowed Files list remain binding.

### Exact pure callable and typed evidence manifest

- Implement only `evaluate_pct_national_stage_fee_policy(command: EvaluatePctNationalStageFeePolicyCommand) -> EvaluatePctNationalStageFeePolicyResult` for rule/source `CN_PCT_NATIONAL_STAGE_POLICY_594`, effective interval `[2024-08-06, None)`.
- The same module owns pure `validate_confirmed_pct_evidence_set(case_id, effective_on, evidence)`; no caller or unnamed upstream seam may bypass it.
- `ConfirmedPctEvidence` is frozen/slotted/keyword-only with exactly: `case_id`, `source_document_id`, `evidence_version_id`, `content_hash`, `lineage_key`, `current_identity_key`, `issuer`, `document_type`, `issued_on`, `role`, `state`, `review_state`, `creator_id`, `reviewer_id`, `reviewed_at`.
- Every evidence value must be same-case with nonblank identities, full lowercase `sha256:[0-9a-f]{64}`, `issuer="CNIPA"`, exact role `OFFICIAL_FINAL_PDF`, state `FINAL`, review state `APPROVED`, nonblank reviewer distinct from creator, naive non-null `reviewed_at`, exact `current_identity_key=f"{case_id}|{lineage_key}"`, and `issued_on <= effective_on`.
- Command fields are exactly `case_id`, `fee_code`, `full_amount`, `effective_on`, `evidence`, `reduction_context`; `evidence` is a tuple of exact `ConfirmedPctEvidence` values.

### Evidence cardinality and fee disposition

- Exactly one `CNIPA_RO_RECEIPT` plus one `CNIPA_ISR`, with no third item, exempts only `CN_INV_APPLICATION_FEE`, `CN_UM_APPLICATION_FEE`, `CN_EXCESS_CLAIM_FEE`, `CN_SPEC_PAGE_31_300_FEE`, and `CN_SPEC_PAGE_301_PLUS_FEE`.
- Exactly one `CNIPA_ISR` XOR one `CNIPA_IPRP` exempts only `CN_SUBSTANTIVE_EXAM_FEE`.
- Ordinary domestic per-fee reduction requires an empty evidence tuple and applies only to `CN_REEXAM_FEE_INV`, `CN_REEXAM_FEE_UM`, `CN_REEXAM_FEE_DES`, `CN_ANNUITY_FEE_INV`, `CN_ANNUITY_FEE_UM`, and `CN_ANNUITY_FEE_DES` through the accepted reduction validators.
- Duplicate evidence version/document/hash or document type, unknown/extra evidence, wrong cardinality, foreign/conflicting/late evidence, case type alone, unsupported or international-stage/WIPO fee keys, and out-of-scope reduction all fail closed. There is no whole-case or whole-PCT flag.
- Result carries the exact rule/source interval, disposition, evidence IDs, full amount, reduction ratio, payable ratio and payable amount.
- `full_amount` must be positive, finite and have scale at most 2. Exemption returns exact `0.00`; otherwise payable amount is `(full_amount * payable_ratio).quantize(0.01, ROUND_HALF_UP)`, with ratios exact to four places.

### Exact error and non-closure boundary

- Pure failures expose exactly one of: `PCT_POLICY_COMMAND_INVALID`, `PCT_POLICY_EFFECTIVE_DATE_UNSUPPORTED`, `PCT_POLICY_FEE_CODE_UNSUPPORTED`, `PCT_POLICY_EVIDENCE_MISSING`, `PCT_POLICY_EVIDENCE_INVALID`, `PCT_POLICY_EVIDENCE_CONFLICT`, `PCT_POLICY_REDUCTION_INVALID`.
- Future HTTP mapping remains outside this task. Add no DB access, transaction, HTTP, I/O, clock, mutation, rate activation, seed, persistence adapter, endpoint, UI, customer approval or second policy.
- Delta-4 dependencies are the accepted fee-reduction and annuity-reduction validators; this pure policy neither activates nor reads a rate book.

### Scoped TDD, evidence and gates

- RED through the exact public callable must prove missing strict DTO validation, each exact evidence/cardinality mode, exemptions, domestic reductions, Decimal boundaries and every fail-closed code; GREEN is the smallest allowlisted pure implementation.
- Existing task-local pytest, scoped Ruff/format/diff, serialized SQLite verification if activated, Evidence 1.1 initialization/finalization, independent review, repository task gate, atomic evidence validation and Done Definition remain binding for later High execution.
- This Ultra materialization performs no product/test edit or evidence initialization and runs only the atomic task-file check.
