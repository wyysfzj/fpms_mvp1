# Frontend Tasks (MVP1) — Copilot/Codex-ready prompts
> DB prerequisite: see `backend/docs/db_migrations_overview.md`  
> Run `cd backend && alembic upgrade head` before backend tasks.

> Assumption: Vue 3 + TypeScript + Pinia + Element Plus + Vite in `frontend/`.

## FE-00 Bootstrap
### FE-00-01 Layout + router + auth guard
**Files**
- `frontend/src/router/index.ts`
- `frontend/src/layout/MainLayout.vue`
- `frontend/src/modules/auth/*`
**Prompt**
Implement SPA skeleton:
- login page, store token, fetch /auth/me
- route guard: require login + permission-based access
- main layout with left menu generated from permission list and IA in docs/01_information_architecture.md

## FE-01 Cases
### FE-01-01 Case list + search
**Files**
- `frontend/src/modules/cases/pages/CaseList.vue`
- `frontend/src/modules/cases/api.ts`
- `frontend/src/modules/cases/store.ts`
**Prompt**
Implement Case list:
- filters: CaseNo, AppNo, Client, Status, Date range
- table with pagination + sorting
- click row opens detail

### FE-01-02 Case detail tabs
**Files**
- `frontend/src/modules/cases/pages/CaseDetail.vue`
- components for tabs
**Prompt**
Implement Case detail with tabs:
- Overview, Parties, Documents, Tasks, Fees, Billing
- show “Limited Edit” button if permission Case.EditLimited

## FE-02 Documents
### FE-02-01 Document list + create
**Files**
- `frontend/src/modules/documents/pages/*`
**Prompt**
Implement document register UI:
- list/search by IN/OUT, type, date, case
- create doc form with attachment upload
- open doc detail with attachments list

## FE-03 Tasks
### FE-03-01 Task list + today reminders
**Files**
- `frontend/src/modules/tasks/pages/*`
**Prompt**
Implement docket task UI:
- list with filters status/due date/worker/supervisor
- today reminders page
- task close/reopen actions

## FE-04 Fees
### FE-04-01 Fee draft UI
**Files**
- `frontend/src/modules/fees/pages/*`
**Prompt**
Implement fee drafts:
- list drafts
- edit draft items grid (FeeCode/FeeType/Amount/YearNo etc)
- lock/unlock

## FE-05 Billing
### FE-05-01 Bills + payments + offset UI
**Files**
- `frontend/src/modules/billing/pages/*`
**Prompt**
Implement billing UI:
- bill list + detail
- payment register
- offset screen: select payment line + allocate amounts to bills

## FE-06 Settings
### FE-06-01 Client maintenance
**Files**
- `frontend/src/modules/settings/pages/ClientList.vue`
**Prompt**
Implement client CRUD pages with nested addresses/contacts.
