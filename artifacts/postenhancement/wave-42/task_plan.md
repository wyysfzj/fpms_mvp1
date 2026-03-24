# Wave 42 Task Plan

## Scope
- Atomic task: `PE-BE-TEST-01`
- Task file: `tasks/postenhancement/backend/PE-BE-TEST-01.md`
- Type: `doc+test`
- Allowlist:
  - `backend/tests/test_annuity_e2e.py`
  - `backend/tests/test_collections_e2e.py`
  - `backend/tests/test_commission_e2e.py`
  - `backend/tests/test_consulting_e2e.py`

## Roles
- Architect: freeze E2E critical path coverage contract.
- Backend/Test dev: implement tests.
- Tester: run task gate and required verification.
- Reviewer: independent sign-off.

## Constraints
- Follow `AGENTS.md` strict atomic rules.
- Touch only allowlisted test files.
