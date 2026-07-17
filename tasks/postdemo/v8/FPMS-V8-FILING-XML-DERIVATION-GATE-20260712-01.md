# FPMS-V8-FILING-XML-DERIVATION-GATE-20260712-01

Status: READY FOR HIGH / ULTRA CONTRACT FROZEN 2026-07-14 / NOT STARTED
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `11. Wave 2C/3 — document evidence and existing workflow adapters`
Catalog ordinal: `64`
Executor role: Backend Developer / worker

## Ultra Contract Resolution — 2026-07-14

- Complete `FPMS-V8-FILING-FULL-WORD-READINESS-GATE-20260712-01` before this task;
  both tasks edit `backend/app/modules/documents/evidence_policy.py` and must not run
  concurrently.
- This task starts from the accepted full-Word readiness result, not from a previously
  rejected XML candidate. Product implementation remains NOT STARTED.

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/specs/2026-07-14-fpms-v8-ultra-contract-freeze-delta-2.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- Source catalog line: `450`
- Expected manifest phase: `foundation`
- Customer gate requirement: `None`

## Story Shape Classification

- `shared_file_density`: high
- `prereq_dependency_density`: high
- `be_fe_coupling`: low
- `evidence_cost`: medium
- `chosen_runbook`: `P0-prereq-heavy-story`

## Task Contract Profile

Task Contract Profile: `TC-RULE`

- RED expectation: Exact public rule test fails on the named transition/calculation.
- GREEN expectation: Exact rule test passes every named success/boundary/fail-closed case.

## Approved Delta-2 Callable Contract

The exact public callable is:

```python
def require_filing_xml_reviewed_word_source(
    *,
    case_id: str,
    source_word: DocumentEvidenceVersion,
    xml_evidence: DocumentEvidenceVersion,
    parent_xml_evidence: DocumentEvidenceVersion | None,
    source_derivation: DocumentEvidenceDerivation,
    submission_derivation: DocumentEvidenceDerivation | None,
) -> None:
```

- `EXTERNAL_XML_PACKAGE` has `parent_xml_evidence=None` and exactly one edge:
  `source_word -> xml_evidence` with `FORMAT_CONVERSION`.
- `SUBMITTED_XML` has a same-case, same-lineage `EXTERNAL_XML_PACKAGE` parent and exactly
  two ordered edges: `source_word -> parent_xml_evidence` with `FORMAT_CONVERSION`, then
  `parent_xml_evidence -> xml_evidence` with `EXTERNAL_SUBMISSION`.
- `source_word` must belong to `case_id`, be the same lineage as the target path, be the
  current `FILING_FULL_WORD`, and have `APPROVED` review status. Its reviewer must differ
  from its creator and `reviewed_at` must be a naive datetime.
- Every object, edge, case, lineage, parent identity and child identity must match the
  selected path exactly. No normalization, fallback path or rejected-candidate reuse is
  authorized.
- The frozen public error codes are exactly:

```text
FILING_XML_DERIVATION_INVALID_CONTEXT
FILING_XML_SOURCE_NOT_FILING_WORD
FILING_XML_SOURCE_NOT_CURRENT
FILING_XML_SOURCE_NOT_APPROVED
FILING_XML_SOURCE_NOT_INDEPENDENTLY_REVIEWED
FILING_XML_TARGET_NOT_XML
FILING_XML_DERIVATION_CASE_MISMATCH
FILING_XML_DERIVATION_LINEAGE_MISMATCH
FILING_XML_DERIVATION_PATH_SHAPE_MISMATCH
FILING_XML_DERIVATION_EDGE_MISMATCH
FILING_XML_DERIVATION_TYPE_MISMATCH
```

- Failures use `FilingXmlDerivationPolicyError(ValueError)` and expose `.code`.
- The callable is a pure read-only rule: no ORM query or write, XML parsing or generation,
  zip handling, clock access, transaction access or side effect.

## Exact Closure Slice

The pure read-only filing XML gate validates exactly one reviewed-current-Word lineage path
for `EXTERNAL_XML_PACKAGE` or `SUBMITTED_XML`; it performs no real XML generation.

## Explicit Non-Closure

No ORM query/write, XML parsing/generation, zip handling, clock or transaction side effect;
no second event/rate/policy, persistence adapter, endpoint, seed or UI. Do not absorb
another V8 catalog row, a second closure slice, an unresolved customer policy or unrelated
cleanup.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-FILING-FULL-WORD-READINESS-GATE-20260712-01`
- `FPMS-V8-DE-REGISTER-DERIVATION-20260712-01`

### External, gate and inherited prerequisites

- None

- Approved source dependency cell (verbatim): evidence derivation

### Shared ownership serialization

- `FPMS-V8-FILING-FULL-WORD-READINESS-GATE-20260712-01` owns
  `backend/app/modules/documents/evidence_policy.py` order key `1`; this task owns order key
  `2`. Complete key `1` before key `2`, and do not run the two owners concurrently.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-FILING-XML-DERIVATION-GATE-20260712-01.md`
- `backend/app/modules/documents/evidence_policy.py`
- `backend/tests/test_v8_filing_xml_derivation_gate.py`
- `artifacts/FPMS-V8-FILING-XML-DERIVATION-GATE-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.

## Verification Commands

- RED and GREEN execute only `backend/tests/test_v8_filing_xml_derivation_gate.py`; no
  inherited or broader regression suite is part of this task's RED/GREEN.
- RED command: `cd backend && .venv/bin/pytest -q tests/test_v8_filing_xml_derivation_gate.py`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `cd backend && .venv/bin/pytest -q tests/test_v8_filing_xml_derivation_gate.py`
- `cd backend && .venv/bin/ruff check --fix app/modules/documents/evidence_policy.py tests/test_v8_filing_xml_derivation_gate.py && .venv/bin/ruff format app/modules/documents/evidence_policy.py tests/test_v8_filing_xml_derivation_gate.py && .venv/bin/ruff check app/modules/documents/evidence_policy.py tests/test_v8_filing_xml_derivation_gate.py`
- `git diff --check -- backend/app/modules/documents/evidence_policy.py backend/tests/test_v8_filing_xml_derivation_gate.py tasks/postdemo/v8/FPMS-V8-FILING-XML-DERIVATION-GATE-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-FILING-XML-DERIVATION-GATE-20260712-01`
- Evidence validation: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-FILING-XML-DERIVATION-GATE-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-FILING-XML-DERIVATION-GATE-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact task-only RED is preserved; the minimum allowlisted change makes the exact
task-only GREEN and scoped Ruff checks pass; task-scoped scope checks pass; shared files
and SQLite verification were serialized; dirty-baseline and baseline-subtracted diff
evidence exist; an independent reviewer approves the exact closure and non-closure; atomic
evidence validation and
`./scripts/task_validate.sh FPMS-V8-FILING-XML-DERIVATION-GATE-20260712-01` pass. Only then
may this task be reported PASS.
