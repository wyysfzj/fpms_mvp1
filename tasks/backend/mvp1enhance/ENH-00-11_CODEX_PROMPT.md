# Universal Atomic Execution Prompt (v2) — ENH-00-11

You are a coding agent executing **one and only one** atomic task.

## Task ID
ENH-00-11

## Goal
Implement Route A for POST /cases input validation:
- Use Pydantic input model so missing required fields trigger **422**
- Use **409** for duplicate `case_no` conflicts
- Keep everything else unchanged

## Authoritative task file
tasks/backend/mvp1enhance/ENH-00-11.md

## Hard Rules (Must Follow)
- Execute ONLY this task.
- Do NOT expand scope.
- Do NOT refactor unrelated code.
- Do NOT change DB schema/migrations/seed.
- Do NOT change auth/RBAC model.
- Permission injection MUST be a function parameter:
  `_perm: None = Depends(require_perm("Case.Create"))`
- Do NOT rewire routers.
- Follow AGENTS.md strictly.

## Allowed Changes (Strict Allowlist)
- `backend/app/modules/cases/api.py` (or the existing cases module api file containing the route)
- `backend/app/modules/cases/schemas.py` (create only if needed for the input model)
- `backend/tests/` (only if adding a minimal test)

If you need to touch any other file, STOP and report.

## Required Steps
1) Implement `CaseCreateIn` Pydantic v2 model with required `case_no` + optional fields.
2) Update route signature to accept `payload: CaseCreateIn`.
3) Change duplicate conflict to `HTTPException(409, ...)`.
4) Keep defaults and response body unchanged.
5) Run ruff + py_compile as per task.

## Evidence (Mandatory)
- Provide curl outputs proving:
  - 422 for `{"invalid":"data"}` with valid auth token
  - 409 for duplicate `case_no`
- Provide lint outputs (or logs)
- Provide `git diff` limited to allowlisted files

## Completion Rule
Task is DONE only if Acceptance is satisfied and evidence is provided.

## STOP Contract
STOP if:
- You need router rewiring
- You need schema changes
- You cannot get 422 without changing beyond allowlist
