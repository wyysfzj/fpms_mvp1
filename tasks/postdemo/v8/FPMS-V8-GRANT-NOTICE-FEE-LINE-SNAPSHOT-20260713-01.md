# FPMS-V8-GRANT-NOTICE-FEE-LINE-SNAPSHOT-20260713-01

Status: PASS
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01` (`V8`)
Wave: `M3 — foundation external prerequisites`
Phase: `foundation_external_prerequisite` (outside the immutable baseline)
Executor role: Backend Developer / worker

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-12-fpms-postdemo-three-lane-mitigation-design.md`
- `docs/superpowers/specs/2026-07-13-fpms-v8-ultra-contract-freeze-delta.md`
- `docs/superpowers/plans/2026-07-13-fpms-v8-ultra-contract-materialization.md`
- Materialization row: `09`
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

Task Contract Profile: `TC-SERVICE`

- RED expectation: The exact parser/DTO test fails because the frozen public seam is absent.
- GREEN expectation: The exact parser/DTO test passes and proves canonical, read-only extraction with strict rejection.

## Exact Closure Slice

Add one pure read-only service that extracts the exact `GrantFeeLines` member from one source `Document.extra_data`, validates its explicit ordered fee lines, binds them to the exact source document ID plus reviewed evidence-version ID/content hash, and returns one canonical `FPMS_GRANT_NOTICE_FEE_LINES_V1` snapshot and bare lowercase SHA-256 hash.

## Ultra Contract Freeze — 2026-07-13

This is the complete High implementation contract for this one closure slice.

### Frozen public Python interface

`backend/app/modules/documents/grant_fee_lines.py` defines exactly these public immutable DTOs and callable. Both dataclasses use `@dataclass(frozen=True, slots=True, kw_only=True)` and their field order and annotations are exact.

```python
@dataclass(frozen=True, slots=True, kw_only=True)
class GrantNoticeFeeLine:
    fee_name: str
    year: int
    amount: Decimal
    reduction_ratio: Decimal


@dataclass(frozen=True, slots=True, kw_only=True)
class GrantNoticeFeeLineSnapshot:
    schema: str
    source_document_id: str
    reviewed_evidence_version_id: str
    reviewed_evidence_content_hash: str
    lines: tuple[GrantNoticeFeeLine, ...]
    canonical_json: str
    snapshot_hash: str


def extract_grant_notice_fee_line_snapshot(
    *,
    document: Document,
    reviewed_evidence_version_id: str,
    expected_evidence_content_hash: str,
) -> GrantNoticeFeeLineSnapshot:
    ...
```

The result `schema` is exactly `FPMS_GRANT_NOTICE_FEE_LINES_V1`. No command DTO, service class, repository, `Session`, async variant, fallback parser or second public callable is authorized.

### Frozen source grammar and bindings

- `document` must be a `Document`; its `id` must be a nonblank string of at most 36 characters and is copied byte-for-byte to `source_document_id`.
- `reviewed_evidence_version_id` must be a nonblank string of at most 36 characters and is copied byte-for-byte.
- `expected_evidence_content_hash` must match exactly `sha256:[0-9a-f]{64}` and is copied byte-for-byte to `reviewed_evidence_content_hash`; uppercase, bare, shortened or whitespace-padded hashes are rejected.
- `document.extra_data` must be JSON text whose root is an object and which contains exactly one case-sensitive `GrantFeeLines` key. Unrelated top-level sibling members remain permitted because `extra_data` is an existing shared carrier; they are ignored and never copied into the snapshot.
- The `GrantFeeLines` value must be a nonempty JSON array. Array order is semantically significant, is preserved exactly and is never sorted.
- Every array item must be an object with exactly the keys `fee_name`, `year`, `amount`, and `reduction_ratio`; missing or extra item fields are rejected.
- `fee_name` must be an exact string, nonblank, equal to its own `strip()` value and contain no NUL.
- `year` must have exact runtime type `int` (boolean is rejected), be greater than zero and be unique across the array. A repeated year is rejected; fee-name repetition across different years is allowed.
- `amount` must be a JSON string in plain decimal notation, finite and greater than zero, with at most two fractional digits. Signs, exponent notation, leading/trailing whitespace, JSON numbers, booleans and null are rejected. It is parsed to `Decimal` and canonicalized to exactly two fractional digits.
- `reduction_ratio` must be a JSON string equal to exactly `0`, `0.7`, or `0.85`; JSON numbers and all other spellings are rejected. It is exposed as the corresponding exact `Decimal`.
- JSON parsing must reject duplicate object keys at every nesting level before normal object construction and reject `NaN`, `Infinity`, `-Infinity` or any other non-finite numeric value. It must not silently retain the first or last duplicate.

Shape/type/JSON failures raise the existing `DocumentExtraDataShapeError`; nonblank, positivity, uniqueness, decimal-scale and allowed-ratio failures raise the existing `DocumentExtraDataBusinessError`. The `.field` value identifies the argument or exact `GrantFeeLines[index].field` path. Validation order is document/type/ID, reviewed version ID, expected hash, JSON/root/member, then each line in array order with field-set, `fee_name`, `year`, `amount`, and `reduction_ratio` checks.

### Frozen canonical snapshot and hash

The canonical payload has exactly this logical shape and no additional keys:

```json
{
  "schema": "FPMS_GRANT_NOTICE_FEE_LINES_V1",
  "source_document_id": "<document.id>",
  "reviewed_evidence_version_id": "<reviewed evidence version id>",
  "reviewed_evidence_content_hash": "sha256:<64 lowercase hex>",
  "lines": [
    {
      "fee_name": "<exact validated name>",
      "year": 1,
      "amount": "900.00",
      "reduction_ratio": "0.85"
    }
  ]
}
```

Build `canonical_json` with exactly `json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)`. It has no BOM or trailing newline. Hash exactly `canonical_json.encode("utf-8")`; `snapshot_hash` is `hashlib.sha256(...).hexdigest()`, exactly 64 lowercase hexadecimal characters with no `sha256:` prefix. Object keys are sorted by the encoder while fee-line array order is preserved. Equivalent accepted amount spellings such as `900`, `900.0`, and `900.00` therefore canonicalize to the same `900.00`; no other field is trimmed, reordered, inferred or normalized.

### Frozen read-only boundary

- Read only `document.id` and `document.extra_data`; do not mutate the ORM object or its JSON text and do not issue SQL.
- No schema or migration, API/router, database write, activity append, lifecycle transition, OCR, PDF parsing, attachment read, rate lookup, fee-code inference, fee-reduction eligibility decision, obligation/draft/task creation or system-clock read.
- Do not verify current/FINAL/APPROVED state here. The follow-up lifecycle adapter owns that prerequisite check and copies this immutable canonical snapshot/hash into its activity fact; downstream grant-year logic consumes the activity fact and must not reread mutable `Document.extra_data`.

### Frozen RED / GREEN test matrix

`backend/tests/test_v8_grant_notice_fee_line_snapshot.py` proves through the public callable:

1. Exact frozen/slotted/keyword-only DTO names, ordered fields, annotations and callable signature.
2. One valid multi-line input preserves input order, binds the exact three provenance values, exposes exact `Decimal` values, and returns the exact canonical UTF-8 JSON and bare lowercase hash.
3. Accepted one- and two-decimal amount spellings normalize to two decimals and hash identically when all logical facts are identical.
4. Missing/null/non-object/non-array/empty `GrantFeeLines`, malformed JSON, duplicate keys at any depth, non-finite tokens, missing or extra line fields, and wrong JSON types are strictly rejected with the frozen exception class and field path.
5. Blank/trim-changing/NUL fee names; zero, negative, boolean or duplicate years; zero, negative, non-finite, exponent, signed or over-scale amounts; and every ratio outside exact string values `0`, `0.7`, `0.85` are rejected.
6. Wrong document/version/hash bindings, uppercase or bare hashes, and whitespace-padded values fail before line parsing.
7. Unrelated valid top-level `extra_data` siblings do not enter or alter the snapshot, while changing any bound fact or ordered line fact changes the hash.
8. A spy proves no SQL, ORM mutation, file/OCR/PDF access, rate or eligibility lookup, obligation/draft/task creation, activity append or clock access.

The RED is the missing frozen module/public seam. GREEN is only this parser and exact test.

## Explicit Non-Closure

No schema/migration, database write, API/router, OCR/PDF extraction, attachment parsing, rate lookup, fee-code inference, reduction eligibility, lifecycle activity, grant-notice state transition, fee obligation, draft or task creation. Do not validate current/FINAL/APPROVED evidence state here, reread this mutable carrier downstream, absorb the grant-notice lifecycle adapter or grant-year annuity closure, or change any existing source/test file.

## Dependencies

### Canonical V8 task dependencies

- `FPMS-V8-DE-REVIEW-SERVICE-20260712-01`

### External, gate and inherited prerequisites

- Dependency must be accepted `PASS` before implementation begins.
- Customer gate: `None`.

### Shared ownership serialization

- None. The task creates one new source file and one new exact test file.

## Remaining Follow-Up Task IDs

- `FPMS-V8-GRANT-NOTICE-LIFECYCLE-ADAPTER-20260712-01`
- `FPMS-V8-GRANT-YEAR-ANNUITY-OBLIGATION-20260712-01`

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-GRANT-NOTICE-FEE-LINE-SNAPSHOT-20260713-01.md`
- `backend/app/modules/documents/grant_fee_lines.py`
- `backend/tests/test_v8_grant_notice_fee_line_snapshot.py`
- `artifacts/FPMS-V8-GRANT-NOTICE-FEE-LINE-SNAPSHOT-20260713-01/**`

No other source, test, task, manifest, schema, migration, API, router or shared ownership file is authorized. Preserve the captured dirty baseline.

## Runtime Contracts

- Preserve AGENTS.md SQLite and caller-owned transaction rules; this closure is pure and read-only.
- No status code or response envelope is introduced because no API is owned.
- Strictly preserve source line order and exact provenance binding; fail closed rather than infer or default.

## Verification Commands

- RED: `cd backend && .venv/bin/pytest -q tests/test_v8_grant_notice_fee_line_snapshot.py`; run before implementation and preserve the expected missing-module/public-seam failure.
- GREEN: `cd backend && .venv/bin/pytest -q tests/test_v8_grant_notice_fee_line_snapshot.py`
- Scoped Ruff: `cd backend && .venv/bin/ruff check --fix app/modules/documents/grant_fee_lines.py tests/test_v8_grant_notice_fee_line_snapshot.py && .venv/bin/ruff format app/modules/documents/grant_fee_lines.py tests/test_v8_grant_notice_fee_line_snapshot.py && .venv/bin/ruff check app/modules/documents/grant_fee_lines.py tests/test_v8_grant_notice_fee_line_snapshot.py`
- Scoped diff: `git diff --check -- backend/app/modules/documents/grant_fee_lines.py backend/tests/test_v8_grant_notice_fee_line_snapshot.py tasks/postdemo/v8/FPMS-V8-GRANT-NOTICE-FEE-LINE-SNAPSHOT-20260713-01.md`
- Task gate: `./scripts/task_validate.sh FPMS-V8-GRANT-NOTICE-FEE-LINE-SNAPSHOT-20260713-01`
- Evidence gate: `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-GRANT-NOTICE-FEE-LINE-SNAPSHOT-20260713-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

Expected HTTP status codes: `N/A` — this task owns no HTTP endpoint.

## Evidence Path

- `artifacts/FPMS-V8-GRANT-NOTICE-FEE-LINE-SNAPSHOT-20260713-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, plus dirty-baseline artifacts when applicable.

## Done Definition

The exact RED is preserved; the minimum allowlisted source and test make the exact GREEN pass; scoped Ruff and diff checks pass; scope compliance confirms only the task/source/test/evidence allowlist changed; the exact closure and non-closure are independently reviewed; task and evidence gates pass. Only then may this implementation task be reported PASS.
