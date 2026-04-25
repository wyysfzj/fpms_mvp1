# PRODUCT-A-BATCH1-RULE-CONTRACT-01

## Background

Batch 1 is blocked because TC-A-006 and TC-A-008 require business rules that automation cannot safely infer.

Prior evidence established:

- TC-A-006 is P0 and requires applicant list rules plus applicant kind mismatch handling.
- The backend already enforces basic applicant list rules:
  - CASE_APPLICANT_REQUIRED
  - CASE_FIRST_APPLICANT_REQUIRED
  - CASE_DUPLICATE_FIRST_APPLICANT
  - CASE_DUPLICATE_APPLICANT_SEQ
- The real Applicant model currently has no persisted applicant type field. Its available fields are id, code, name_cn, name_en, and is_active.
- TC-A-008 is P0 and requires status/date/number rules that are not currently available as stable backend service-layer semantics.

This document freezes the minimum product and backend rule contract so later backend tasks can implement real rules before pytest automation closes TC-A-006 and TC-A-008.

## Data Source

Skeleton data remains the testcase semantic source of truth:

- TC-A-006: applicant list rules, P0, Unhappy and Boundary.
- TC-A-008: date and number consistency, P0, Unhappy and Boundary.
- DS-AP-001 is the legal-entity applicant seed.
- DS-AP-002 is the natural-person applicant seed.

The real backend schema determines implementation field shape only. It must not override skeleton testcase intent.

## TC-A-006 Rule Contract

### Applicant Type Data Model

Applicant type must become real backend data, not a rule inferred from names, skeleton-only metadata, or seed ids.

Recommended field:

- applicant_type

Recommended values:

- INDIVIDUAL
- ENTITY
- UNIV, optional extension
- GOV, optional extension

Seed mapping required by the data-model task:

- DS-AP-001 / 法人 maps to ENTITY.
- DS-AP-002 / 自然人 maps to INDIVIDUAL.

Open product decision:

- `product_decision_required`: decide whether master data should store only INDIVIDUAL and ENTITY, or store UNIV and GOV as applicant_type values too. Until decided, UNIV and GOV should be accepted as case applicant_kind values but do not need to be master applicant types.

### ApplicantKind Mapping

The case applicant_kind field is interpreted as:

- INDIVIDUAL means natural-person first applicant.
- ENTITY, UNIV, and GOV mean organization-like first applicant.

Compatibility decision:

- Null or empty applicant_kind remains allowed for now.
- Applicant kind mismatch validation runs only when applicant_kind is provided and the first applicant type is known.
- This avoids breaking existing case creation paths while still allowing TC-A-006 to cover the explicit mismatch branch.

Open product decision:

- `product_decision_required`: decide whether applicant_kind should become required when applicants exist in a later strict mode.

### Backend Rule

After existing applicant list validation passes:

- If the first applicant is INDIVIDUAL, case applicant_kind must be INDIVIDUAL.
- If the first applicant is organization-like, case applicant_kind must be one of ENTITY, UNIV, or GOV.
- If applicant_kind is null or empty, skip mismatch validation under the compatibility rule.
- If the first applicant type is unknown, do not guess. Return a data-quality error only if the data-model task makes applicant_type required; otherwise skip mismatch validation and record the compatibility behavior in backend summary.

Existing applicant list errors must remain unchanged:

- CASE_APPLICANT_REQUIRED
- CASE_FIRST_APPLICANT_REQUIRED
- CASE_DUPLICATE_FIRST_APPLICANT
- CASE_DUPLICATE_APPLICANT_SEQ

New stable error semantics:

- HTTP status: 400
- code: CASE_APPLICANT_KIND_MISMATCH
- details:

```json
{
  "applicant_kind": "...",
  "first_applicant_type": "...",
  "first_applicant_id": "..."
}
```

The backend rule must not use FastAPI enum validation, duplicate case number, missing unrelated field, or permission failure as a substitute for applicant kind mismatch.

## TC-A-008 Rule Contract

### Status Required Fields

For status PUBLISHED, the following fields are required:

- app_no
- filing_date
- pub_no
- pub_date

Stable error semantics:

- HTTP status: 400
- code: CASE_PUBLISHED_FIELDS_REQUIRED
- details:

```json
{
  "status": "PUBLISHED",
  "missing_fields": ["pub_no", "pub_date"]
}
```

For status GRANTED, the following fields are required:

- app_no
- filing_date
- pub_no
- pub_date
- grant_no
- grant_date
- first_annuity_year
- valid_until

Stable error semantics:

- HTTP status: 400
- code: CASE_GRANTED_FIELDS_REQUIRED
- details:

```json
{
  "status": "GRANTED",
  "missing_fields": ["grant_no", "grant_date", "first_annuity_year", "valid_until"]
}
```

Existing CASE_STATUS_REQUIRES_APPLICATION_FIELDS should be kept for generic non-NOT_FILED statuses that are not covered by the more specific PUBLISHED or GRANTED contracts. For PUBLISHED and GRANTED, backend automation should assert the specific error codes above to avoid ambiguous TC-A-008 assertions.

Open product decision:

- `product_decision_required`: decide whether every GRANTED case must already have publication fields, or whether special product flows may grant without publication. The recommended MVP contract requires publication fields for GRANTED.

### Filing Date And Priority Date

If priorities exist:

- filing_date must be greater than or equal to the earliest priority prio_date.
- filing_date earlier than the earliest priority date is rejected.
- filing_date equal to the earliest priority date is accepted.

Stable error semantics:

- HTTP status: 400
- code: CASE_FILING_BEFORE_PRIORITY
- details:

```json
{
  "filing_date": "2026-03-14",
  "earliest_priority_date": "2026-03-15"
}
```

The rule should run after priority rows are structurally valid, so CASE_PRIORITY_INCOMPLETE and CASE_DUPLICATE_PRIORITY_SEQ remain unchanged.

### Application Number Format

MVP app_no validation:

- Trim before validation.
- Reject empty or whitespace-only app_no when app_no is required by status.
- Keep length <= 64 as schema-level validation.
- Reject control-character values.
- For China domestic cases, allow common CN application number characters:
  - digits
  - dot
  - uppercase letters
  - slash
  - hyphen

Stable error semantics:

- HTTP status: 400
- code: CASE_APP_NO_INVALID
- details:

```json
{
  "app_no": "..."
}
```

Open product decision:

- `product_decision_required`: strict jurisdiction-specific app_no regex is not frozen in this task. Do not block backend implementation on a full legal-format regex. Implement the MVP rule above first, and split strict jurisdiction formatting into a later product-confirmed task.

## Backend Task Split

Recommended backend sequence:

1. BE-A-APPLICANT-DATA-MODEL-01
   - Add applicant_type to real Applicant model, schema, API, seed support, and tests.
   - Preserve SQLite compatibility.
   - Do not implement case applicant mismatch rule in this task unless explicitly scoped.
2. BE-A-APPLICANT-KIND-RULE-01
   - Add service-layer CASE_APPLICANT_KIND_MISMATCH after applicant_type exists.
   - Preserve existing applicant list errors.
   - Cover create and full update paths if those paths can change applicant_kind or applicants.
3. BE-A-DATE-NUMBER-RULES-01
   - Add TC-A-008 service-layer rules:
     - CASE_PUBLISHED_FIELDS_REQUIRED
     - CASE_GRANTED_FIELDS_REQUIRED
     - CASE_FILING_BEFORE_PRIORITY
     - CASE_APP_NO_INVALID
   - Preserve existing priority structural errors and generic status application-field error.

## Automation Task Split

Recommended automation sequence after backend tasks pass:

1. A-AUTO-PY-A-APPLICANT-RULES-P0-02
   - Implement TC-A-006 pytest handler.
   - Assert CASE_APPLICANT_REQUIRED, CASE_DUPLICATE_FIRST_APPLICANT, CASE_APPLICANT_KIND_MISMATCH, and corrected applicant kind success.
   - Pre-scan stale skeleton-state expectations and include affected test files in the allowlist.
2. A-AUTO-PY-A-DATE-NUMBER-RULES-P0-01
   - Implement TC-A-008 pytest handler.
   - Assert the four stable TC-A-008 error codes and the filing_date equals priority_date positive boundary.
   - Use fresh FPMS_RUN_ID and explicit FPMS_DB_DSN= for real smoke.

## Open Product Decisions

- TC-A-006: whether Applicant.applicant_type should support only INDIVIDUAL and ENTITY or also UNIV and GOV.
- TC-A-006: whether case applicant_kind should remain optional permanently or become required when applicants exist.
- TC-A-008: whether GRANTED always requires prior publication fields in MVP.
- TC-A-008: strict jurisdiction-specific app_no regex remains product_decision_required and is out of scope for the MVP rule.

## Non-Closure

This contract does not implement backend code, frontend UI, pytest automation, migrations, seed edits, YAML edits, JSON edits, schema edits, Playwright updates, or real smoke. It only freezes the product rule contract and follow-up task split.
