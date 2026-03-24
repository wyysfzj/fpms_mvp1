# Wave 40 Task Plan

## Scope
- Atomic task: `PE-BE-QA-02`
- Task file: `tasks/postenhancement/backend/PE-BE-QA-02.md`
- Type: `service`
- Allowlist:
  - `backend/app/modules/*/api.py` (list endpoint page_size params only)

## Roles
- Architect: freeze global page_size cap contract.
- Backend: enforce `page_size <= 100` across list endpoints.
- Tester: run task gate and required verification.
- Reviewer: independent sign-off.

## Constraints
- Follow `AGENTS.md` strict atomic rules.
- Only pagination params changes; no behavior drift beyond cap.
