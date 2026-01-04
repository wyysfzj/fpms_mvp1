# Backend Tasks (MVP1) — Copilot/Codex-ready prompts
> DB prerequisite: see `backend/docs/db_migrations_overview.md`  
> Run `cd backend && alembic upgrade head` before backend tasks.

> Assumption: You are implementing in `backend/` with FastAPI + SQLAlchemy 2.x + Pydantic 2.x.
> Follow module docs under `backend/app/modules/**/docs/`.

## BE-00 Bootstrap
### BE-00-01 Create base app wiring
**Files**
- `backend/app/main.py`
- `backend/app/api/router.py`
- `backend/app/core/config.py`
- `backend/app/db/session.py`

**Prompt**
Implement a FastAPI app skeleton:
- load settings via pydantic-settings from env
- CORS origins from settings
- include API router under `/api/v1`
- health endpoint `/healthz`
- DB session dependency using SQLAlchemy 2.0
- ensure SQLite works in dev and Postgres in prod via DATABASE_URL
- return JSON error model as defined in docs/04_backend_architecture.md

### BE-00-02 Auth + RBAC skeleton
**Files**
- `backend/app/modules/auth/*`
- `backend/app/modules/rbac/*`
- `backend/app/api/deps.py`

**Prompt**
Implement minimal JWT auth and RBAC:
- T_User, T_Role, T_UserRole models
- password hashing (passlib bcrypt)
- login endpoint returns access token
- `/auth/me` returns user profile + permissions list
- dependency `require_perm("...")` enforces permission codes
- seed default roles: Admin, Formalities, Agent, Finance with permissions matrix from docs/02_permissions_rbac.md

## BE-01 Master data
### BE-01-01 Client CRUD
**Files**
- `backend/app/modules/masterdata/clients/*`
**Prompt**
Implement Client master data CRUD:
- tables: T_Client, T_ClientAddress, T_ClientContact
- endpoints: list/search, create, update, deactivate
- validations: unique client code, at least one address optional in MVP1
- include pagination + sorting

## BE-02 Case module
### BE-02-01 Case models & schemas (MVP1)
**Files**
- `backend/app/modules/cases/models.py`
- `backend/app/modules/cases/schemas.py`
**Prompt**
Implement MVP1 case entities per `backend/app/modules/cases/docs/case_01_db.md`:
- T_Case + sub tables (CaseApplicant, CaseInventor, Priority)
- include audit fields
- define enums CaseType, FlowDir, PatentCategory, Status (MVP1 subset)
- Pydantic schemas for create/update/detail/list

### BE-02-02 Case APIs
**Files**
- `backend/app/modules/cases/api.py`
- `backend/app/modules/cases/service.py`
**Prompt**
Implement case endpoints per `case_02_api.md`:
- POST /cases, GET /cases, GET /cases/{id}, PUT /cases/{id}
- POST /cases/{id}/limited-edit (permission Case.EditLimited)
- GET /cases/export (CSV)
- enforce CaseNo unique

## BE-03 Documents
### BE-03-01 Document register + attachments
**Files**
- `backend/app/modules/documents/*`
**Prompt**
Implement document module MVP1:
- T_Document, T_DocAttachment, minimal T_DocTemplate
- upload attachment via multipart, store file under storage/ with safe path
- list/search docs
- link to case
- basic access control (Doc.Read/Doc.Create)

## BE-04 Tasks (Docket)
### BE-04-01 Task models + APIs
**Files**
- `backend/app/modules/tasks/*`
**Prompt**
Implement docket task management MVP1:
- T_TaskTemplate, T_Task, T_TaskLog
- create/edit/close/reopen/cancel task, log all operations
- today reminders endpoint: /tasks/today?as=worker|supervisor

## BE-05 Fees
### BE-05-01 Fee draft CRUD
**Files**
- `backend/app/modules/fees/*`
**Prompt**
Implement fee drafts MVP1:
- T_FeeRate, T_FeeDraft, T_FeeItem
- endpoints: list drafts, create draft, add/update/delete items, lock/unlock draft
- support FeeType GOV/SERVICE/MISC

## BE-06 Billing
### BE-06-01 Bill generation from fee draft
**Files**
- `backend/app/modules/billing/*`
**Prompt**
Implement billing MVP1:
- T_Bill, T_BillItem, T_Payment, T_PaymentLine, T_Offset, T_CaseReceipt
- generate bill from selected drafts (single client & currency validation)
- payment register
- offset payments to bills; update balances and statuses
- update case receipt summary from offsets

## BE-07 Template rendering
### BE-07-01 docxtpl render endpoint
**Files**
- `backend/app/modules/templates/*`
**Prompt**
Implement template rendering MVP1:
- T_Template, T_LetterHead metadata
- endpoint: render bill to docx using docxtpl template (from file path)
- output as streaming response with correct content-type
- include sample templates in backend/storage/templates/sample/
