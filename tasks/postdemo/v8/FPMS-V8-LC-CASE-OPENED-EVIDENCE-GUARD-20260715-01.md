# FPMS-V8-LC-CASE-OPENED-EVIDENCE-GUARD-20260715-01

Status: PASS / INDEPENDENT REREVIEW APPROVED 2026-07-16
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `H4-0 / D4-01`
Risk tier: `HIGH`
Scope: `Foundation`
Contract state: `CONTRACT FROZEN`
Executor role: High implementation agent

## Authoritative Contract

- Delta-4 specification:
  `docs/superpowers/specs/2026-07-15-fpms-v8-ultra-contract-freeze-delta-4.md`
- Frozen specification SHA-256:
  `7c2a8c5947136be8434ba963616473c39158f25cbd2abb4a8fae23f0f6a4fff8`
- Supplemental batch manifest row: `01 / D4-01`
- Accepted predecessor: `FPMS-V8-LC-CASE-OPENED-20260712-01`

The frozen Delta-4 specification controls if this task text is read ambiguously. A hash
mismatch or non-Status drift fails closed and returns this task to Ultra contract review.

## Story Shape Classification

- `shared_file_density`: high
- `prereq_dependency_density`: high
- `be_fe_coupling`: none
- `evidence_cost`: high
- `chosen_runbook`: `P0-prereq-heavy-story`

## Exact Closure Slice

Close exactly one pure lifecycle service rule: `CASE_OPENED` accepts an evidence tuple only
when it contains exactly one same-case case-record evidence reference with:

- `kind = CASE_RECORD`;
- `object_type = Case`;
- the exact transitioning `case_id`;
- a nonblank evidence identity;
- a full lowercase `sha256:[0-9a-f]{64}` content hash; and
- a non-null naive capture timestamp.

Missing evidence, an empty tuple, a non-tuple carrier, zero or multiple case-record items,
an extra item, duplicate identity, wrong kind/object type/case, malformed hash, timezone-aware
or missing capture time must fail closed through the accepted lifecycle validation error
surface before any transition is accepted. Evidence ordering must not change the result.

The existing legal transition, actor, idempotency, event-time and lifecycle-state semantics
remain unchanged. This task changes only the `CASE_OPENED` evidence matrix and its direct
regression coverage.

## Explicit Non-Closure

- No case-create adapter or case creation service change; D4-02 owns supplying the evidence.
- No `FILING_PREPARATION_STARTED`, `FILING_EXTERNAL_SUBMISSION_RECORDED`,
  `FILING_RECEIPT_ARCHIVED`, OA, document, fee, deadline or other lifecycle rule.
- No API/router/schema/model/migration/seed/frontend change.
- No new evidence persistence, resolver, role, envelope, permission or status-code behavior.
- No refactor, adjacent cleanup, broad test rewrite, repo-wide verification, release gate,
  commit, push, reset, clean, stash or discard.

## Dependencies and Ownership

- Requires accepted `CASE_OPENED` lifecycle transition behavior and the hash-locked Delta-4
  contract above.
- Owns the shared `lifecycle_rules.py` only for this exact closure.
- Shared-source order is strictly D4-01 → D4-03 → D4-04. D4-03 or D4-04 must not edit or
  verify the shared source concurrently.
- D4-02 may start only after this task is independently accepted; it does not share this
  task's source/test ownership.
- No migration is owned. Any SQLite-writing verification must use
  `GLOBAL_SQLITE_SERIAL_QUEUE` with maximum writer one.

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-LC-CASE-OPENED-EVIDENCE-GUARD-20260715-01.md`
- `backend/app/modules/cases/lifecycle_rules.py`
- `backend/tests/test_v8_lifecycle_case_opened.py`
- `backend/tests/test_v8_lc_case_opened_evidence_guard.py`
- `artifacts/FPMS-V8-LC-CASE-OPENED-EVIDENCE-GUARD-20260715-01/**`

No other path is authorized. Preserve the dirty worktree and subtract the Evidence 1.1
captured allowlist baseline from this task's scoped diff.

## Verification Commands

### RED

Add one behavior at a time in
`backend/tests/test_v8_lc_case_opened_evidence_guard.py`, beginning with proof that the
accepted predecessor incorrectly permits a tuple that does not contain the exact single
`CASE_RECORD` / `Case` reference. Record a nonzero, expected RED before product edits:

```bash
cd backend && .venv/bin/pytest -q tests/test_v8_lc_case_opened_evidence_guard.py
```

### GREEN

Implement the smallest pure-rule correction, then run:

```bash
cd backend && .venv/bin/pytest -q \
  tests/test_v8_lc_case_opened_evidence_guard.py \
  tests/test_v8_lifecycle_case_opened.py
```

Coverage must include the exact positive tuple and every fail-closed class named in the
closure. Do not broaden into another lifecycle event.

### Scoped lint and format

```bash
cd backend && .venv/bin/ruff check --fix \
  app/modules/cases/lifecycle_rules.py \
  tests/test_v8_lifecycle_case_opened.py \
  tests/test_v8_lc_case_opened_evidence_guard.py
cd backend && .venv/bin/ruff format \
  app/modules/cases/lifecycle_rules.py \
  tests/test_v8_lifecycle_case_opened.py \
  tests/test_v8_lc_case_opened_evidence_guard.py
cd backend && .venv/bin/ruff check \
  app/modules/cases/lifecycle_rules.py \
  tests/test_v8_lifecycle_case_opened.py \
  tests/test_v8_lc_case_opened_evidence_guard.py
```

Do not run repo-wide Ruff, pytest, frontend build, Playwright or release gate.

## Evidence Path

- `artifacts/FPMS-V8-LC-CASE-OPENED-EVIDENCE-GUARD-20260715-01/**`

### Evidence and independent acceptance

- Initialize only through Evidence 1.1:
  `./scripts/evidence_init.sh FPMS-V8-LC-CASE-OPENED-EVIDENCE-GUARD-20260715-01 --task-file tasks/postdemo/v8/FPMS-V8-LC-CASE-OPENED-EVIDENCE-GUARD-20260715-01.md` with each allowlist path supplied explicitly.
- Record required latest nonzero RED and zero GREEN/lint/scope results and their logs under
  `artifacts/FPMS-V8-LC-CASE-OPENED-EVIDENCE-GUARD-20260715-01/**`.
- Produce dirty-baseline artifacts when applicable and a baseline-subtracted scoped
  `git/diff.patch` containing every tracked/untracked task change and no outside path.
- An independent domain reviewer must issue an evidence-backed APPROVED zero-finding verdict;
  the implementer cannot approve this task.
- Run the repository task gate and atomic evidence validation after the summary is PASS.

## Remaining Follow-Up Task IDs

Follow-up marker: not `None`; the exact remaining follow-up task IDs are:

- `FPMS-V8-CASE-CREATE-OPENED-EVIDENCE-ADAPTER-20260715-01`
- `FPMS-V8-LC-FILING-PREPARATION-EVIDENCE-GUARD-20260715-01`
- `FPMS-V8-LC-FILING-EXTERNAL-SUBMISSION-EVIDENCE-GUARD-20260715-01`

## Done Definition

- The exact `CASE_OPENED` evidence matrix is enforced fail closed through the accepted
  public lifecycle seam without changing legal transition semantics.
- Required RED and GREEN, targeted regression, scoped Ruff/format, scope validation,
  baseline-subtracted diff and Evidence 1.1 artifacts are present and latest.
- Independent review is APPROVED with zero findings.
- Repository task gate and atomic evidence validation PASS.
- The exact closure is complete, all non-closure boundaries and shared-source serialization
  are respected, and no follow-up closure was absorbed.
