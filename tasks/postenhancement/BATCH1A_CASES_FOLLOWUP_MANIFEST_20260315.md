# Batch 1A Cases Follow-up Manifest (2026-03-15)

Status: Ready for execution

Purpose:
- complete the remaining feasible Batch 1 Case-domain work without violating no-schema constraints
- keep all execution inside adjusted `Batch 1A`
- explicitly defer still-blocked `FR-CM-05` special-attribute scope

## Covered Scope

- `US-CM-03` partial follow-up
- `FR-CM-03` partial follow-up
- frontend evidence normalization for adjusted `Batch 1A`

## Deferred Scope

The following scope remains blocked and is NOT authorized by this manifest:
- `FR-CM-05` bacteria deposit attributes
- `FR-CM-05` PCT international / national phase special attributes beyond already-supported fields
- `FR-CM-05` invalidation-specific attributes
- any schema/model/migration expansion
- any `Batch 2+` work

## Atomic Task Mapping

| Follow-up ID | Atomic Task File Path | Owner Role | Notes |
|---|---|---|---|
| `FE-Enh-001A` | `tasks/postenhancement/frontend/PE-FE-CM-02.md` | `worker` | Applicant selection / quick-create / backfill and FE close evidence |
| `QA-Enh-001A` | `tasks/postenhancement/backend/PE-QA-CM-02.md` | `monitor` | Adjusted Batch 1A validation and close audit |

## Shared Ownership Decision

Frontend shared ownership files:
- `frontend/src/modules/cases/pages/CaseCreate.vue`
- `frontend/src/modules/cases/pages/CaseEdit.vue`
- `frontend/src/api/cases.ts`
- `frontend/src/api/cases.types.ts`
- `frontend/src/api/clients.ts`

Conflict decision:
- execution must remain serialized
- `PE-QA-CM-02` must run only after `PE-FE-CM-02` completes

## Execution Waves

### Wave 1

- Role: `worker`
- Task file: `tasks/postenhancement/frontend/PE-FE-CM-02.md`
- Mode: serialized

### Wave 2

- Role: `monitor`
- Task file: `tasks/postenhancement/backend/PE-QA-CM-02.md`
- Mode: serialized

## Stop Rule

- This manifest only authorizes adjusted `Batch 1A`
- It does not authorize `Batch 2`
