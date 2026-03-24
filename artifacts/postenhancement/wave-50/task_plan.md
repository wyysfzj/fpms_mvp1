# Wave 50 Task Plan

## Scope
- Atomic task: `PE-FE-QA-02`
- Task file: `tasks/postenhancement/frontend/PE-FE-QA-02.md`
- Type: `service`
- Allowlist:
  - `frontend/src/modules/**/pages/*.vue` (only new pages)
  - `frontend/src/styles/*.css` (minimal required)

- Atomic task: `PE-FE-QA-03`
- Task file: `tasks/postenhancement/frontend/PE-FE-QA-03.md`
- Type: `doc`
- Allowlist:
  - `docs/frontend_smoke_flows.md`
  - `docs/FPMS_Frontend_Manual_Test_User_Guide.md`

## Roles
- Architect: freeze a11y/responsive acceptance and smoke-doc coverage matrix.
- Frontend: implement one atomic task per worker.
- Tester: run gates and final FE verification.
- Reviewer: independent final sign-off.

## Constraints
- Follow `AGENTS.md` strict atomic rules.
- All UI text MUST be Simplified Chinese.
