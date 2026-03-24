# Wave 01 Contract Freeze (Architect)

Date: 2026-02-28  
Scope: Wave 01 atomic tasks only (`PE-BE-00-01`, `PE-BE-00-03`, `PE-FE-00-01`, `PE-FE-00-03`)

## Freeze Rules (All 4 Tasks)
- Execute each atomic task in a separate run.
- Stay inside each task allowlist; no cross-scope edits.
- No DB schema/migration/router rewiring changes.
- Preserve existing response envelope and existing endpoint shapes.

## PE-BE-00-01
- Task: Extend `CaseType` / status validation mapping with `CONSULTING` and `SEARCH`.
- Allowed files:
  - `backend/app/modules/cases/enums.py`
  - `backend/app/modules/cases/schemas.py`
- Expected API/permission/error behavior impact:
  - API contract change: case create/update validation must accept new `case_type` values `CONSULTING` and `SEARCH`.
  - No new endpoint, no permission code change, no envelope change.
  - Invalid enum inputs continue to fail validation as `422`.
- Regression risks:
  - Existing defaults (`NORMAL`) accidentally changed.
  - Enum expansion not mirrored in schema typing, causing partial validation coverage.
  - Legacy `case_type` values regress in create/update flows.
- Acceptance checklist:
  - `CaseType` includes `CONSULTING` and `SEARCH`.
  - Case input schemas accept new values and still accept existing values.
  - Existing case create/update behavior remains unchanged for prior enum values.
  - No unrelated changes outside allowlist.

## PE-BE-00-03
- Task: Define unified API error semantics and response-envelope constraints for next tasks.
- Allowed files:
  - `docs/error_codes.md`
  - `docs/api_usage_guide.md`
- Expected API/permission/error behavior impact:
  - Runtime API behavior unchanged (doc-only task).
  - Documentation must clearly standardize `400/401/403/404/409/422` semantics and envelope usage.
  - Permission-related errors must remain documented as `403 FORBIDDEN` with actionable guidance.
- Regression risks:
  - Docs diverge from current implementation and mislead clients/testers.
  - Inconsistent examples across the two docs cause integration ambiguity.
- Acceptance checklist:
  - Added/updated domain error codes are complete and internally consistent.
  - Status-code semantics are explicit and aligned with current backend behavior.
  - Error envelope examples are present and consistent across docs.
  - Links/examples are readable and executable as written.

## PE-FE-00-01
- Task: Align frontend permission constants with backend `Title.Action` naming.
- Allowed files:
  - `frontend/src/constants/perms.ts`
  - `frontend/src/constants/menu.ts`
- Expected API/permission/error behavior impact:
  - Frontend permission string values must move away from legacy `module:action` style.
  - Menu permission checks must reference the updated constants only (no legacy literals).
  - No backend API/interface change; expected runtime error semantics remain unchanged.
- Regression risks:
  - Export names in `perms.ts` changed and break imports in router/components.
  - Wrong permission mapping causes false-positive/false-negative menu visibility when perms are loaded.
  - Mixed legacy/new permission literals remain in menu definitions.
- Acceptance checklist:
  - `perms.ts` permission values follow `Title.Action` style.
  - `menu.ts` uses constants consistently and no `cases:read`-style literals remain.
  - Existing constant export names remain stable to avoid broader frontend churn.
  - Frontend lint/typecheck pass for this scope.

## PE-FE-00-03
- Task: Add frontend-facing error-code/status handling reference.
- Allowed files:
  - `docs/FPMS_Frontend_Manual_Test_User_Guide.md`
- Expected API/permission/error behavior impact:
  - Runtime FE/BE behavior unchanged (doc-only task).
  - Manual-test documentation must define reusable handling paths for key statuses and error codes.
  - Guidance must stay consistent with backend envelope (`error.code`, `error.message`, `error.details`).
- Regression risks:
  - FE test guidance drifts from backend error semantics.
  - Missing mapping for common statuses leads to inconsistent UX handling during manual tests.
- Acceptance checklist:
  - Error/status handling mapping is explicitly documented and reusable by testers/devs.
  - Examples are aligned with current backend contracts and envelope shape.
  - No edits outside the single allowlist document.

## Cross-Task Coordination Notes
- `PE-FE-00-01` should be reviewed against backend permission codes currently used in APIs (e.g., `Case.Read`, `Doc.Read`, `Task.Read`, `Fee.Read`, `Bill.Read`, `Client.Read`, `SystemParam.Read`).
- `PE-BE-00-03` and `PE-FE-00-03` should stay semantically aligned to avoid backend/frontend documentation drift.
