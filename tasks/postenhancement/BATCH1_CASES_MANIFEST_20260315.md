# Batch 1 Cases Manifest (2026-03-15)

Status: Execution Freeze -> Manifest Ready

Purpose:
- Convert Batch 1 from plan-level logical IDs into AGENTS-compliant atomic task file paths.
- Enable legal real multi-agent execution without violating file ownership rules.

## Covered Batch

- Batch: `Batch 1`
- Domain: `Cluster C1 Cases`
- Covered `Partially Implemented` items:
  - `US-CM-01`
  - `US-CM-02`
  - `US-CM-03`
  - `FR-CM-02`
  - `FR-CM-03`
  - `FR-CM-04`
  - `FR-CM-05`

## Logical-to-Atomic Mapping

| Logical ID | Atomic Task File Path | Owner Role | Notes |
|---|---|---|---|
| `BE-Enh-001` | `tasks/postenhancement/backend/PE-BE-CM-01.md` | `worker` | Backend-only implementation for Batch 1 Cases |
| `FE-Enh-001` | `tasks/postenhancement/frontend/PE-FE-CM-01.md` | `worker` | Frontend-only implementation for Batch 1 Cases |
| `QA-Enh-001` (Batch 1 scoped) | `tasks/postenhancement/backend/PE-QA-CM-01.md` | `monitor` | Batch 1 validation and scope audit only |

## Ownership / Shared File Decision

### Backend shared ownership files

- `backend/app/modules/cases/api.py`
- `backend/app/modules/cases/service.py`
- `backend/app/modules/cases/schemas.py`
- `backend/app/modules/cases/enums.py`
- `backend/app/modules/documents/service.py`

### Frontend shared ownership files

- `frontend/src/api/cases.ts`
- `frontend/src/api/cases.types.ts`
- `frontend/src/api/clients.ts`

### Conflict decision

- `PE-BE-CM-01` and `PE-FE-CM-01` do not share writable product files across backend/frontend boundaries.
- `PE-QA-CM-01` must run after implementation waves; it is not allowed to overlap with implementation write ownership.
- Because backend task touches backend shared ownership files internally, backend execution must remain single-owner serialized.
- Because frontend task touches shared API client/types files, frontend execution must remain single-owner serialized.

## Recommended Execution Waves

### Wave 1

- Agent Role: `worker`
- Task File: `tasks/postenhancement/backend/PE-BE-CM-01.md`
- Mode: serialized
- Reason:
  - touches backend shared ownership files
  - must complete backend contract before FE integration is verified

### Wave 2

- Agent Role: `worker`
- Task File: `tasks/postenhancement/frontend/PE-FE-CM-01.md`
- Mode: serialized
- Reason:
  - touches frontend shared ownership files
  - depends on backend contract after Wave 1

### Wave 3

- Agent Role: `monitor`
- Task File: `tasks/postenhancement/backend/PE-QA-CM-01.md`
- Mode: serialized
- Reason:
  - validation-only
  - must audit completed implementation outputs

## Entry Condition For Real Implementation

Batch 1 may now legally enter real multi-agent execution because:
- each execution unit has one exact task file path
- each execution unit has an allowlist
- each execution unit has a verification set
- waves and ownership conflicts are explicit

## Stop Rule

- This manifest only authorizes `Batch 1`
- No `Batch 2+` execution is authorized by this file
