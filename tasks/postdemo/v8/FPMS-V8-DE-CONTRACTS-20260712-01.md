# FPMS-V8-DE-CONTRACTS-20260712-01

Status: PASS — ULTRA CONTRACT FROZEN 2026-07-13
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Wave: `11. Wave 2C/3 — document evidence and existing workflow adapters`
Catalog ordinal: `42`
Executor role: Backend Developer / worker

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/plans/2026-07-12-fpms-postdemo-v8-mitigation-implementation.md`
- Source catalog line: `414`
- Expected manifest phase: `foundation`
- Customer gate requirement: `None`

## Story Shape Classification

- `shared_file_density`: low
- `prereq_dependency_density`: low
- `be_fe_coupling`: low
- `evidence_cost`: medium
- `chosen_runbook`: `P0-single-lane-story`

## Task Contract Profile

Task Contract Profile: `TC-INTERFACE`

- RED expectation: Exact contract test fails because the named type/enum/interface is absent.
- GREEN expectation: Exact contract test and task-scoped Ruff pass.

## Exact Closure Slice

Define evidence roles, states and version/derivation commands only.

## Explicit Non-Closure

No persistence, business adapter, endpoint or UI. Do not absorb another V8 catalog row, a second closure slice, an unresolved customer policy or unrelated cleanup.

## Ultra Contract Freeze — 2026-07-13

Execution stopped before RED because the canonical V8 design fixed the nine business
roles and the D1/D2 carriers, but did not freeze executable Python names or values.
This section resolves only that interface ambiguity. The closure slice, non-closure,
Story Shape Classification and `chosen_runbook=P0-single-lane-story` remain unchanged.

### Public enums and stable values

All enums inherit from `str, Enum`. Member names and values are identical. No alias,
`UNKNOWN`, customer-configurable value or additional member is authorized.

| Public enum | Exact members / machine values | Frozen meaning |
| --- | --- | --- |
| `EvidenceRole` | `FILING_FULL_WORD`, `TRACKED_REVISED_WORD`, `FILING_COMPONENT`, `EXTERNAL_XML_PACKAGE`, `OFFICIAL_SUBMISSION_LIST`, `OFFICIAL_FINAL_PDF`, `SUBMITTED_XML`, `OFFICIAL_RECEIPT`, `CLIENT_LETTER_WORD` | Respectively: internal complete confirmed Word; tracked revised Word; component split from a selected Word/PDF; externally converted XML/archive; official-site recognized submission list; official-site final PDF; XML actually submitted; official submission/acceptance receipt; client letter Word. These are nine distinct roles even when content hashes match. |
| `EvidenceVersionState` | `DRAFT`, `FINAL` | Working evidence versus a frozen final artifact. External submission does not add a third state; it is represented by `final_submitted_at`. |
| `EvidenceReviewState` | `PENDING`, `APPROVED`, `REJECTED` | No decision yet, independently approved, or independently rejected. |
| `EvidenceDerivationType` | `REVISION`, `COMPONENT_EXTRACTION`, `FORMAT_CONVERSION`, `OFFICIAL_RECOGNITION`, `EXTERNAL_SUBMISSION`, `RECEIPT_LINK`, `CUSTOMER_LETTER_RENDER` | Directed technical provenance only. Role-pair readiness and OA attachment policy remain in later policy/service tasks. |

### Frozen Python shapes

`evidence_contracts.py` must use `from __future__ import annotations`,
`@dataclass(frozen=True, slots=True)`, `datetime.datetime`, and the four enums above.
Field order is part of the contract. Every listed field is required and has no
dataclass default; `T | None` states nullability but the caller must still pass it.

```python
@dataclass(frozen=True, slots=True)
class RegisterEvidenceVersionCommand:
    case_id: str
    document_id: str
    attachment_id: str
    lineage_key: str
    role: EvidenceRole
    state: EvidenceVersionState
    creator_id: str
    content_hash: str


@dataclass(frozen=True, slots=True)
class EvidenceVersionResult:
    evidence_version_id: str
    case_id: str
    document_id: str
    attachment_id: str
    lineage_key: str
    role: EvidenceRole
    version_number: int
    state: EvidenceVersionState
    creator_id: str
    review_state: EvidenceReviewState
    reviewer_id: str | None
    reviewed_at: datetime | None
    final_submitted_at: datetime | None
    content_hash: str
    is_current: bool
    is_final: bool


@dataclass(frozen=True, slots=True)
class RegisterEvidenceDerivationCommand:
    case_id: str
    parent_evidence_version_id: str
    child_evidence_version_id: str
    derivation_type: EvidenceDerivationType
    actor_id: str
    derived_at: datetime
    source_snapshot: str


@dataclass(frozen=True, slots=True)
class EvidenceDerivationResult:
    evidence_derivation_id: str
    case_id: str
    parent_evidence_version_id: str
    child_evidence_version_id: str
    derivation_type: EvidenceDerivationType
    actor_id: str
    derived_at: datetime
    source_snapshot: str
```

The later service functions consume these exact commands and return these exact
results:

```python
register_evidence_version(
    command: RegisterEvidenceVersionCommand,
    transaction: Session,
) -> EvidenceVersionResult

register_evidence_derivation(
    command: RegisterEvidenceDerivationCommand,
    transaction: Session,
) -> EvidenceDerivationResult
```

`Session` documents the downstream caller-owned SQLAlchemy transaction boundary;
it is not exported or implemented by this pure-contract task.

### Frozen representation and encoding rules

- `version_number` is not caller input. The register-version service allocates the
  next positive integer within `(case_id, lineage_key)`, starting at `1`.
- A newly registered version starts with `review_state=PENDING`,
  `reviewer_id=None`, `reviewed_at=None` and `final_submitted_at=None`. The command
  cannot pre-approve, pre-reject or claim external submission.
- Currentness is not a version state and is not accepted by either command. The
  persisted representation is non-null
  `current_identity_key=f"{case_id}|{lineage_key}"` only for the current row;
  `EvidenceVersionResult.is_current` is exactly
  `current_identity_key is not None`. Switching it belongs only to
  `FPMS-V8-DE-CURRENT-VERSION-RULE-20260712-01`.
- Finality is `state is EvidenceVersionState.FINAL`;
  `EvidenceVersionResult.is_final` is exactly that predicate. A submitted version
  remains `FINAL`; `final_submitted_at` records submission separately. Receipt
  linkage and ordinary-replacement blocking remain later service behavior.
- `content_hash` is the immutable lowercase SHA-256 wire form
  `sha256:<64 lowercase hexadecimal characters>`. Contracts never read bytes or
  compute the digest.
- All command timestamps are UTC-normalized, timezone-naive `datetime` values
  (`tzinfo is None`) to match `DateTime(timezone=False)`. Persistence must not
  silently reinterpret local wall-clock time.
- `source_snapshot` is immutable canonical JSON object text: UTF-8 JSON produced
  with `ensure_ascii=False`, `sort_keys=True`, `separators=(",", ":")` and
  `allow_nan=False`. It must decode to an object, not an array or scalar. No
  customer-policy keys are required by this contract.

### Validation boundary and exact contract test

- `evidence_contracts.py` is a pure type module. It performs no database access,
  filesystem access, JSON parsing/serialization, hash computation, ID generation,
  version allocation, role-pair policy, transition, mutation or business-error
  mapping. Frozen dataclasses provide immutability only; they do not silently
  coerce values.
- The register-version service owns non-empty/length/enum/hash/time validation,
  UUID generation, positive monotonic version allocation, case/document/attachment
  ownership checks, `flush()` and result projection. It never `commit()`s.
- The register-derivation service owns non-empty/length/enum/time/canonical-JSON
  validation, row existence and the D2 invariant
  `parent.case_id == child.case_id == command.case_id` before `flush()`. It never
  `commit()`s. Cycle policy, allowed role pairs and filing/OA readiness are not
  invented here and remain outside this task.
- The exact RED/GREEN contract test must assert enum bases and exact ordered
  `(name, value)` pairs; dataclass frozen/slots configuration, exact ordered field
  names and resolved annotations; absence of defaults; construction/equality and
  mutation rejection; exact `__all__`; and that importing/constructing the module
  produces no persistence or I/O side effect. It must not test a downstream
  service rule in this TC-INTERFACE task.

The module's `__all__` is frozen in this exact order:

```python
__all__ = [
    "EvidenceRole",
    "EvidenceVersionState",
    "EvidenceReviewState",
    "EvidenceDerivationType",
    "RegisterEvidenceVersionCommand",
    "EvidenceVersionResult",
    "RegisterEvidenceDerivationCommand",
    "EvidenceDerivationResult",
]
```

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-W1-D1-DOCUMENT-EVIDENCE-VERSION-CARRIER-20260712-01`
- `FPMS-V8-W1-D2-DOCUMENT-EVIDENCE-DERIVATION-CARRIER-20260712-01`
- `FPMS-V8-W1-D3-WORK-PACKAGE-EVIDENCE-LINK-CARRIER-20260712-01`

### External, gate and inherited prerequisites

- None

- Approved source dependency cell (verbatim): D1–D3

### Shared ownership serialization

- No shared ownership chain beyond the global serialized SQLite verification queue.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-DE-CONTRACTS-20260712-01.md`
- `backend/app/modules/documents/evidence_contracts.py`
- `backend/tests/test_v8_document_evidence_contracts.py`
- `artifacts/FPMS-V8-DE-CONTRACTS-20260712-01/**`

No other source, test, task, manifest or shared ownership file is authorized. Inherited regression inputs are read-only unless explicitly listed above. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md permission injection, response-envelope, FastAPI status/body, SQLite and Simplified Chinese UI rules applicable to this closure.
- Use caller-owned transactions for business writes; no service-level commit unless the approved row explicitly owns it.
- All SQLite-writing tests and shared-file verification run through the global serialized queue.

## Verification Commands

- RED command: `cd backend && .venv/bin/pytest -q tests/test_v8_document_evidence_contracts.py`; run it before implementation and preserve the expected failure proving the named missing behavior.
- GREEN and scoped checks:
- `cd backend && .venv/bin/pytest -q tests/test_v8_document_evidence_contracts.py`
- `cd backend && .venv/bin/ruff check --fix app/modules/documents/evidence_contracts.py tests/test_v8_document_evidence_contracts.py && .venv/bin/ruff format app/modules/documents/evidence_contracts.py tests/test_v8_document_evidence_contracts.py && .venv/bin/ruff check app/modules/documents/evidence_contracts.py tests/test_v8_document_evidence_contracts.py`
- `git diff --check -- backend/app/modules/documents/evidence_contracts.py backend/tests/test_v8_document_evidence_contracts.py tasks/postdemo/v8/FPMS-V8-DE-CONTRACTS-20260712-01.md`
- `./scripts/task_validate.sh FPMS-V8-DE-CONTRACTS-20260712-01`
- Evidence validation: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-DE-CONTRACTS-20260712-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

## Evidence Path

- `artifacts/FPMS-V8-DE-CONTRACTS-20260712-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, and dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted change makes the exact GREEN and targeted regressions pass; task-scoped lint/format/scope checks pass; shared files and SQLite verification were serialized; dirty-baseline and baseline-subtracted diff evidence exist; an independent reviewer approves the exact closure and non-closure; atomic evidence validation and `./scripts/task_validate.sh FPMS-V8-DE-CONTRACTS-20260712-01` pass. Only then may this task be reported PASS.
