# Backend Atomic Tasks (MVP1) — 1 file / 1 class / 1 endpoint per task
> DB prerequisite: see `backend/docs/db_migrations_overview.md`  
> Run `cd backend && alembic upgrade head` before backend tasks.

> Target stack: **FastAPI + SQLAlchemy 2.x + Pydantic 2.x** under `backend/`.
>
> Atomic rule (to reduce Copilot drift):
> - Each task MUST change **only the listed file** (or create exactly **one** new file).
> - Each task MUST implement **only the named class / function / endpoint**.
> - Follow the design contracts in:
>   - `docs/*`
>   - `backend/app/modules/**/docs/*`

---

## BE-00 Bootstrap & Cross-cutting

### BE-00-01 (docs/04_backend_architecture.md) — Create consistent error response models
**File:** `backend/app/core/errors.py` (new)

**Prompt**
Create `app/core/errors.py` implementing a stable API error envelope:
- Pydantic models:
  - `ErrorDetail { code:str, message:str, details:dict|None }`
  - `ErrorResponse { error: ErrorDetail }`
- Exception class `BusinessError(Exception)` with fields: `code`, `message`, `details:dict|None`, `status_code:int=400`
- Helper `raise_business_error(code, message, details=None, status_code=400)` that raises `BusinessError`
- Helper `to_error_response(code, message, details=None) -> dict` returning the JSON structure required by docs.
Constraints:
- Do NOT add any other files.
- Keep model names exactly as above.

### BE-00-02 (docs/04_backend_architecture.md) — Register exception handlers
**File:** `backend/app/main.py`

**Prompt**
Update `app/main.py` ONLY:
- import `BusinessError` and `ErrorResponse` from `app.core.errors`
- register FastAPI exception handlers:
  - `BusinessError` -> returns JSON `{"error":{...}}` with `status_code` from exception
  - `RequestValidationError` -> returns `{"error":{"code":"VALIDATION_ERROR","message":"Invalid request","details":{...}}}` with 422
- keep `/healthz` and router mount `/api/v1` as-is.
Constraints:
- Do NOT modify other files.

### BE-00-03 (docs/04_backend_architecture.md) — Add pagination helpers
**File:** `backend/app/core/pagination.py` (new)

**Prompt**
Create `app/core/pagination.py` with minimal pagination primitives used by list endpoints:
- Pydantic model `PageParams` with fields: `page:int=1`, `page_size:int=20`, `sort_by:str|None=None`, `sort_dir:Literal['asc','desc']='desc'`
- Function `offset_limit(page:int, page_size:int) -> tuple[int,int]` returning (offset, limit)
- Pydantic generic-ish container (non-generic is OK) `PageResult` with: `items:list`, `page:int`, `page_size:int`, `total:int`
Constraints:
- Do NOT touch other files.

### BE-00-04 (docs/03_database_mvp1_subset.md) — Add DB mixins for UUID + audit
**File:** `backend/app/db/mixins.py` (new)

**Prompt**
Create `app/db/mixins.py` containing SQLAlchemy mixins:
- `UUIDPrimaryKeyMixin` providing `id` column (string UUID) as PK with default `uuid4` string
- `AuditMixin` providing:
  - `created_at`, `updated_at` as timezone-aware datetimes with defaults
  - `created_by`, `updated_by` as nullable string UUIDs (FK not enforced in MVP1)
Constraints:
- Use SQLAlchemy 2.x `Mapped` / `mapped_column` style.
- Do NOT add additional files.

### BE-00-05 (docs/04_backend_architecture.md) — Add JWT + password helpers
**File:** `backend/app/core/security.py` (new)

**Prompt**
Create `app/core/security.py`:
- password helpers using passlib bcrypt:
  - `get_password_hash(password:str)->str`
  - `verify_password(plain:str, hashed:str)->bool`
- JWT helpers using `python-jose`:
  - `create_access_token(subject:str, secret:str, expires_minutes:int=60)->str`
  - `decode_access_token(token:str, secret:str)->dict` (raise on invalid)
- token payload convention: `sub` contains user_id (string)
Constraints:
- No DB access in this file.

### BE-00-06 (docs/04_backend_architecture.md) — Add local storage path helpers
**File:** `backend/app/core/storage.py` (new)

**Prompt**
Create `app/core/storage.py` implementing safe local storage utilities for MVP1:
- `ensure_dir(path:str)->None`
- `safe_join(base_dir:str, *parts:str)->str` preventing path traversal (raise ValueError)
- `save_upload_file(upload_file, dest_path:str)->tuple[str,int]` saving a FastAPI UploadFile to dest_path and returning (mime_type,size)
Constraints:
- Use standard library only (plus FastAPI UploadFile typing if needed).
- Do NOT implement S3/OSS.

---

## BE-01 Auth + RBAC (MVP1)
Doc refs:
- `backend/app/modules/auth/docs/auth_00_overview.md`
- `backend/app/modules/rbac/docs/rbac_00_overview.md`
- `docs/02_permissions_rbac.md`

### BE-01-01 (auth_00_overview) — Implement model `T_User`
**File:** `backend/app/modules/auth/models.py`

**Prompt**
Implement ONLY `class T_User` in `auth/models.py`:
- Table name: `T_User`
- Columns (MVP1):
  - `id` (UUID string PK)
  - `username` (unique, indexed)
  - `display_name`
  - `password_hash`
  - `is_active` (bool, default True)
  - audit fields from `AuditMixin`
Constraints:
- Use `Base` from `app.db.base` and mixins from `app.db.mixins`.
- Do NOT implement other models in this task.

### BE-01-02 (rbac_00_overview) — Implement model `T_Role`
**File:** `backend/app/modules/rbac/models.py`

**Prompt**
In `rbac/models.py`, implement ONLY `class T_Role`:
- Table: `T_Role`
- Columns:
  - `id` (UUID string PK)
  - `code` (unique, indexed; e.g., Admin/Formalities/Agent/Finance)
  - `name` (human readable)
  - audit fields
Constraints:
- Do NOT implement other classes.

### BE-01-03 (rbac_00_overview) — Implement model `T_UserRole`
**File:** `backend/app/modules/rbac/models.py`

**Prompt**
In `rbac/models.py`, implement ONLY `class T_UserRole`:
- Table: `T_UserRole`
- Columns:
  - `id` (UUID string PK)
  - `user_id` (indexed)
  - `role_id` (indexed)
- Add uniqueness constraint on (user_id, role_id)
Constraints:
- Keep FK constraints optional for MVP1 (string ids ok).

### BE-01-04 (rbac_00_overview + docs/02_permissions_rbac.md) — Implement model `T_RolePerm`
**File:** `backend/app/modules/rbac/models.py`

**Prompt**
In `rbac/models.py`, implement ONLY `class T_RolePerm`:
- Table: `T_RolePerm`
- Columns:
  - `id` (UUID string PK)
  - `role_id` (indexed)
  - `perm_code` (indexed; stores permission code like `Case.Read`)
- Uniqueness constraint on (role_id, perm_code)

### BE-01-05 (auth_00_overview) — Add schema `LoginRequest`
**File:** `backend/app/modules/auth/schemas.py`

**Prompt**
In `auth/schemas.py`, implement ONLY `class LoginRequest(BaseModel)`:
- fields: `username:str`, `password:str`
- minimal validation: strip whitespace for username
Constraints:
- Pydantic v2 style.

### BE-01-06 (auth_00_overview) — Add schema `TokenResponse`
**File:** `backend/app/modules/auth/schemas.py`

**Prompt**
In `auth/schemas.py`, implement ONLY `class TokenResponse(BaseModel)`:
- fields: `access_token:str`, `token_type:str='bearer'`

### BE-01-07 (auth_00_overview) — Add schema `MeResponse`
**File:** `backend/app/modules/auth/schemas.py`

**Prompt**
In `auth/schemas.py`, implement ONLY `class MeResponse(BaseModel)`:
- fields:
  - `user: dict` containing at least `id`, `username`, `display_name`
  - `roles: list[str]` (role codes)
  - `permissions: list[str]` (permission codes)
Constraints:
- Keep structure stable; frontend will use `permissions`.

### BE-01-08 (auth_00_overview) — Implement service `get_user_by_username`
**File:** `backend/app/modules/auth/service.py`

**Prompt**
In `auth/service.py`, implement ONLY function `get_user_by_username(db, username:str)`:
- Query `T_User` by username
- Return user or None
Constraints:
- Do not implement login yet.

### BE-01-09 (auth_00_overview) — Implement service `authenticate_user`
**File:** `backend/app/modules/auth/service.py`

**Prompt**
In `auth/service.py`, implement ONLY function `authenticate_user(db, username:str, password:str)`:
- Use `get_user_by_username`
- Check `is_active`
- Verify password with `app.core.security.verify_password`
- Return user or None

### BE-01-10 (docs/02_permissions_rbac.md) — Implement RBAC service `get_user_permissions`
**File:** `backend/app/modules/rbac/service.py`

**Prompt**
In `rbac/service.py`, implement ONLY function `get_user_permissions(db, user_id:str) -> set[str]`:
- Load user roles via `T_UserRole`
- Load perm codes via `T_RolePerm`
- Return a set of permission codes
Constraints:
- Do not hardcode role->perm mapping here (DB is source of truth).

### BE-01-11 (docs/02_permissions_rbac.md) — Implement RBAC service `seed_default_roles_perms`
**File:** `backend/app/modules/rbac/service.py`

**Prompt**
In `rbac/service.py`, implement ONLY function `seed_default_roles_perms(db) -> None`:
- Ensure roles exist: Admin, Formalities, Agent, Finance
- Seed `T_RolePerm` rows based on permission codes and menu-role matrix in `docs/02_permissions_rbac.md`
- Idempotent: running twice must not duplicate
Constraints:
- Keep permission code strings exactly as `docs/02_permissions_rbac.md`.

### BE-01-12 (auth_00_overview) — Implement endpoint `POST /auth/login`
**File:** `backend/app/modules/auth/api.py`

**Prompt**
In `auth/api.py`, implement ONLY endpoint `POST /auth/login`:
- Accept `LoginRequest`
- Authenticate via `auth.service.authenticate_user`
- On success return `TokenResponse(access_token=...)` using `create_access_token(subject=user.id, secret=settings.jwt_secret)`
- On failure raise `BusinessError(code='AUTH_INVALID', message='Invalid username or password', status_code=401)`
Constraints:
- Ensure router exists as `router = APIRouter()`.
- Do NOT implement `/auth/me` in this task.

### BE-01-13 (auth_00_overview) — Implement endpoint `GET /auth/me`
**File:** `backend/app/modules/auth/api.py`

**Prompt**
In `auth/api.py`, implement ONLY endpoint `GET /auth/me`:
- Use dependency `get_current_user` from `app.api.deps`
- Return `MeResponse` containing:
  - user basic profile
  - role codes
  - permission codes (from `rbac.service.get_user_permissions`)
Constraints:
- Do NOT implement other endpoints.

### BE-01-14 — Wire auth router into main API router
**File:** `backend/app/api/router.py`

**Prompt**
Update `app/api/router.py` ONLY:
- include `auth.router` under prefix `/auth`, tags `["auth"]`
- keep existing structure

### BE-01-15 — Implement request dependencies `get_current_user` and `require_perm`
**File:** `backend/app/api/deps.py`

**Prompt**
Implement `app/api/deps.py` to support MVP1 auth + RBAC:
- `get_current_user(db=Depends(get_db), token=Depends(oauth2_scheme))`:
  - read Bearer token
  - decode with `settings.jwt_secret`
  - load `T_User` by `id` and ensure `is_active`
  - on failure raise `BusinessError(code='AUTH_REQUIRED', message='Authentication required', status_code=401)`
- `require_perm(code:str)`:
  - dependency that loads current user and checks `code in get_user_permissions(db, user.id)`
  - on failure raise `BusinessError(code='FORBIDDEN', message='Permission denied', details={'perm':code}, status_code=403)`
Constraints:
- Do NOT implement other helpers.

### BE-01-16 — Implement dev seed script (roles + admin)
**File:** `backend/scripts/seed_dev.py`

**Prompt**
Implement `backend/scripts/seed_dev.py` ONLY:
- Connect DB using `app.db.session.get_engine()` and SQLAlchemy Session
- Call `seed_default_roles_perms(db)`
- Create default Admin user if not exists:
  - username: `admin`
  - password: `admin123` (hash it)
  - display_name: `Administrator`
- Assign Admin role to admin user via `T_UserRole`
- Idempotent: safe to rerun

---

## BE-02 Master Data — Clients (MVP1)
Doc ref: `backend/app/modules/masterdata/clients/docs/client_00_overview.md`

### BE-02-01 (client_00_overview) — Implement model `T_Client`
**File:** `backend/app/modules/masterdata/clients/models.py`

**Prompt**
In `masterdata/clients/models.py`, implement ONLY `class T_Client`:
- Table: `T_Client`
- Columns:
  - `id` (UUID string PK)
  - `client_code` (unique, indexed)
  - `name_cn`, `name_en` (nullable)
  - `is_active` (bool, default True)
  - audit fields

### BE-02-02 (client_00_overview) — Implement model `T_ClientAddress`
**File:** `backend/app/modules/masterdata/clients/models.py`

**Prompt**
In `masterdata/clients/models.py`, implement ONLY `class T_ClientAddress`:
- Table: `T_ClientAddress`
- Columns:
  - `id` (UUID string PK)
  - `client_id` (indexed)
  - `address_line1`, `address_line2` (nullable)
  - `city`, `province`, `country`, `postal_code` (nullable)
  - `is_default_billing` (bool, default False)
  - `is_default_mailing` (bool, default False)
  - audit fields

### BE-02-03 (client_00_overview) — Implement model `T_ClientContact`
**File:** `backend/app/modules/masterdata/clients/models.py`

**Prompt**
In `masterdata/clients/models.py`, implement ONLY `class T_ClientContact`:
- Table: `T_ClientContact`
- Columns:
  - `id` (UUID string PK)
  - `client_id` (indexed)
  - `name`, `email`, `phone` (nullable)
  - `is_primary` (bool, default False)
  - audit fields

### BE-02-04 — Add schema `ClientCreate`
**File:** `backend/app/modules/masterdata/clients/schemas.py`

**Prompt**
In `masterdata/clients/schemas.py`, implement ONLY `class ClientCreate(BaseModel)`:
- fields: `client_code:str`, `name_cn:str|None=None`, `name_en:str|None=None`
- optional arrays:
  - `addresses:list[dict]=[]`
  - `contacts:list[dict]=[]`
Constraints:
- Keep nested items as dict for now (MVP1 speed). Do NOT add more schema classes.

### BE-02-05 — Add schema `ClientUpdate`
**File:** `backend/app/modules/masterdata/clients/schemas.py`

**Prompt**
In `masterdata/clients/schemas.py`, implement ONLY `class ClientUpdate(BaseModel)`:
- updatable fields: `name_cn`, `name_en`, `is_active` (optional)
- optional addresses/contacts replacement arrays as list[dict]

### BE-02-06 — Add schema `ClientOut`
**File:** `backend/app/modules/masterdata/clients/schemas.py`

**Prompt**
In `masterdata/clients/schemas.py`, implement ONLY `class ClientOut(BaseModel)`:
- fields: `id`, `client_code`, `name_cn`, `name_en`, `is_active`
- include `addresses:list[dict]=[]`, `contacts:list[dict]=[]`

### BE-02-07 — Implement service `list_clients`
**File:** `backend/app/modules/masterdata/clients/service.py`

**Prompt**
In `masterdata/clients/service.py`, implement ONLY function `list_clients(db, q:str|None, page:int, page_size:int)`:
- search by `client_code` or name (CN/EN) if q provided
- return `(items, total)` where items are `T_Client` rows
- apply offset/limit

### BE-02-08 — Implement service `create_client`
**File:** `backend/app/modules/masterdata/clients/service.py`

**Prompt**
In `masterdata/clients/service.py`, implement ONLY function `create_client(db, payload:ClientCreate, actor_id:str|None)`:
- validate unique `client_code` (raise BusinessError `CLIENT_CODE_DUPLICATE`)
- create `T_Client` + optional addresses/contacts rows
- set audit fields using actor_id when provided

### BE-02-09 — Implement service `update_client`
**File:** `backend/app/modules/masterdata/clients/service.py`

**Prompt**
In `masterdata/clients/service.py`, implement ONLY function `update_client(db, client_id:str, payload:ClientUpdate, actor_id:str|None)`:
- update base fields
- for MVP1: replace addresses/contacts by delete+insert if provided

### BE-02-10 — Implement service `deactivate_client`
**File:** `backend/app/modules/masterdata/clients/service.py`

**Prompt**
In `masterdata/clients/service.py`, implement ONLY function `deactivate_client(db, client_id:str, actor_id:str|None)`:
- set `is_active=False`

### BE-02-11 — Implement endpoint `GET /clients`
**File:** `backend/app/modules/masterdata/clients/api.py`

**Prompt**
In `masterdata/clients/api.py`, implement ONLY endpoint `GET /clients`:
- permission: `Client.Manage` (Admin/Formalities)
- query: `q`, `page`, `page_size`
- call `list_clients`
- return `PageResult` envelope from `app.core.pagination`

### BE-02-12 — Implement endpoint `POST /clients`
**File:** `backend/app/modules/masterdata/clients/api.py`

**Prompt**
In `masterdata/clients/api.py`, implement ONLY endpoint `POST /clients`:
- permission: `Client.Manage`
- body: `ClientCreate`
- actor from `get_current_user`
- return `ClientOut`

### BE-02-13 — Implement endpoint `PUT /clients/{id}`
**File:** `backend/app/modules/masterdata/clients/api.py`

**Prompt**
In `masterdata/clients/api.py`, implement ONLY endpoint `PUT /clients/{id}`:
- permission: `Client.Manage`
- body: `ClientUpdate`
- return `ClientOut`

### BE-02-14 — Implement endpoint `PUT /clients/{id}/deactivate`
**File:** `backend/app/modules/masterdata/clients/api.py`

**Prompt**
In `masterdata/clients/api.py`, implement ONLY endpoint `PUT /clients/{id}/deactivate`:
- permission: `Client.Manage`
- return `{status:'ok'}`

### BE-02-15 — Wire clients router
**File:** `backend/app/api/router.py`

**Prompt**
Update `app/api/router.py` ONLY:
- include `masterdata.clients.router` under prefix `/clients`, tags `["clients"]`

---

## BE-03 Case Maintenance (MVP1)
Doc refs:
- `backend/app/modules/cases/docs/case_00_overview.md`
- `backend/app/modules/cases/docs/case_01_db.md`
- `backend/app/modules/cases/docs/case_02_api.md`
- `backend/app/modules/cases/docs/case_03_rules.md`

### BE-03-00 — Create enums for Case domain
**File:** `backend/app/modules/cases/enums.py` (new)

**Prompt**
Create `cases/enums.py` defining Python Enums (string values):
- `CaseType`: only `NORMAL` for MVP1
- `PatentCategory`: `INV`, `UM`, `DESIGN`
- `FlowDir`: `CN_IN`, `CN_OUT`, `CN_DOMESTIC`
- `CaseStatus`: minimal subset for MVP1: `OPEN`, `CLOSED` (do not invent more)
Constraints:
- Keep enums importable by models and schemas.

### BE-03-01 (case_01_db:T_Case) — Implement model `T_Case`
**File:** `backend/app/modules/cases/models.py`

**Prompt**
In `cases/models.py`, implement ONLY `class T_Case` per `case_01_db.md`:
- Table: `T_Case`
- Columns: CaseNo(unique), CaseType, PatentCategory, FlowDir, ClientID, Title_CN, Title_EN, AppNo(index), Status, RecvDate, FilingDate, PrioDate, PrimaryAgentID(optional), Description
- Include audit fields
- Add indexes: unique CaseNo; index AppNo; index ClientID
Constraints:
- Use string enums (store enum value strings).
- Do NOT implement other tables.

### BE-03-02 (case_01_db:T_CaseApplicant) — Implement model `T_CaseApplicant`
**File:** `backend/app/modules/cases/models.py`

**Prompt**
In `cases/models.py`, implement ONLY `class T_CaseApplicant`:
- Table: `T_CaseApplicant`
- Columns: CaseID(indexed), ApplicantID(nullable), Name(text fallback), IsFirst(bool)
Constraints:
- Enforce "at most one first" via service-level validation (no partial unique in DB for MVP1).

### BE-03-03 (case_01_db:T_CaseInventor) — Implement model `T_CaseInventor`
**File:** `backend/app/modules/cases/models.py`

**Prompt**
In `cases/models.py`, implement ONLY `class T_CaseInventor`:
- Table: `T_CaseInventor`
- Columns: CaseID(indexed), Name, Country(nullable), SequenceNo

### BE-03-04 (case_01_db:T_Priority) — Implement model `T_Priority`
**File:** `backend/app/modules/cases/models.py`

**Prompt**
In `cases/models.py`, implement ONLY `class T_Priority`:
- Table: `T_Priority`
- Columns: CaseID(indexed), PrioNo, PrioDate, Country

### BE-03-05 — Add schema `CasePartyInput` (Applicants)
**File:** `backend/app/modules/cases/schemas.py`

**Prompt**
In `cases/schemas.py`, implement ONLY `class CaseApplicantIn(BaseModel)`:
- fields: `applicant_id:str|None=None`, `name:str|None=None`, `is_first:bool=False`
Constraints:
- Do NOT add other schemas.

### BE-03-06 — Add schema `CaseInventorIn`
**File:** `backend/app/modules/cases/schemas.py`

**Prompt**
In `cases/schemas.py`, implement ONLY `class CaseInventorIn(BaseModel)`:
- fields: `name:str`, `country:str|None=None`, `sequence_no:int=1`

### BE-03-07 — Add schema `PriorityIn`
**File:** `backend/app/modules/cases/schemas.py`

**Prompt**
In `cases/schemas.py`, implement ONLY `class PriorityIn(BaseModel)`:
- fields: `prio_no:str`, `prio_date:date`, `country:str`

### BE-03-08 — Add schema `CaseCreate`
**File:** `backend/app/modules/cases/schemas.py`

**Prompt**
In `cases/schemas.py`, implement ONLY `class CaseCreate(BaseModel)` per `case_00_overview.md`:
- required: `case_no`, `client_id`, `patent_category`, `flow_dir`
- optional: `title_cn`, `title_en`, `app_no`, `recv_date`, `filing_date`, `description`, `primary_agent_id`
- lists: `applicants:list[CaseApplicantIn]`, `inventors:list[CaseInventorIn]=[]`, `priorities:list[PriorityIn]=[]`
- `case_type` defaults to `NORMAL`

### BE-03-09 — Add schema `CaseUpdateFull`
**File:** `backend/app/modules/cases/schemas.py`

**Prompt**
In `cases/schemas.py`, implement ONLY `class CaseUpdateFull(BaseModel)`:
- same fields as CaseCreate but all optional
- includes applicants/inventors/priorities optional lists

### BE-03-10 — Add schema `CaseUpdateLimited`
**File:** `backend/app/modules/cases/schemas.py`

**Prompt**
In `cases/schemas.py`, implement ONLY `class CaseUpdateLimited(BaseModel)` per `case_03_rules.md`:
- allow only: `title_cn`, `title_en`, `description`, `inventors:list[CaseInventorIn]`
- do NOT include status/client/flowdir/patentcategory

### BE-03-11 — Add schema `CaseListItem`
**File:** `backend/app/modules/cases/schemas.py`

**Prompt**
In `cases/schemas.py`, implement ONLY `class CaseListItem(BaseModel)`:
- fields: `id`, `case_no`, `client_id`, `title_cn`, `title_en`, `app_no`, `status`, `flow_dir`, `patent_category`, `recv_date`, `filing_date`, `prio_date`

### BE-03-12 — Add schema `CaseDetail`
**File:** `backend/app/modules/cases/schemas.py`

**Prompt**
In `cases/schemas.py`, implement ONLY `class CaseDetail(BaseModel)`:
- include `CaseListItem` fields
- plus arrays: `applicants:list[dict]`, `inventors:list[dict]`, `priorities:list[dict]`
Constraints:
- Use dict for nested outputs (MVP1 speed).

### BE-03-13 (case_03_rules) — Implement service helper `validate_applicants`
**File:** `backend/app/modules/cases/service.py`

**Prompt**
In `cases/service.py`, implement ONLY function `validate_applicants(applicants:list[CaseApplicantIn]) -> None`:
- raise BusinessError `CASE_APPLICANT_REQUIRED` if empty
- raise BusinessError `CASE_FIRST_APPLICANT_INVALID` if not exactly 1 has is_first=True

### BE-03-14 (case_02_api#1) — Implement service `list_cases`
**File:** `backend/app/modules/cases/service.py`

**Prompt**
In `cases/service.py`, implement ONLY function `list_cases(db, filters:dict, page:int, page_size:int, sort_by:str|None, sort_dir:str)`:
- filters per `case_02_api.md` endpoint 1: q, case_no, app_no, client_id, status, date_from, date_to
- q searches in case_no/title/app_no
- return `(items, total)`

### BE-03-15 (case_02_api#2) — Implement service `create_case`
**File:** `backend/app/modules/cases/service.py`

**Prompt**
In `cases/service.py`, implement ONLY function `create_case(db, payload:CaseCreate, actor_id:str|None)`:
- validate unique CaseNo (BusinessError `CASE_NO_DUPLICATE`)
- call `validate_applicants`
- insert T_Case + sub tables (applicants/inventors/priorities)
- set `T_Case.PrioDate = MIN(priorities.prio_date)` if provided

### BE-03-16 (case_02_api#3) — Implement service `get_case_detail`
**File:** `backend/app/modules/cases/service.py`

**Prompt**
In `cases/service.py`, implement ONLY function `get_case_detail(db, case_id:str)`:
- load T_Case and related applicants/inventors/priorities
- if not found raise BusinessError `CASE_NOT_FOUND` (404)
- return a dict or tuple suitable for `CaseDetail`

### BE-03-17 (case_02_api#4) — Implement service `update_case_full`
**File:** `backend/app/modules/cases/service.py`

**Prompt**
In `cases/service.py`, implement ONLY function `update_case_full(db, case_id:str, payload:CaseUpdateFull, actor_id:str|None)`:
- update allowed fields
- if applicants list provided -> validate and replace
- if inventors/priorities provided -> replace
- recompute PrioDate

### BE-03-18 (case_02_api#5) — Implement service `update_case_limited`
**File:** `backend/app/modules/cases/service.py`

**Prompt**
In `cases/service.py`, implement ONLY function `update_case_limited(db, case_id:str, payload:CaseUpdateLimited, actor_id:str|None)`:
- enforce whitelist per `case_03_rules.md`
- must NOT change status, client, flowdir, patentcategory
- replace inventors if provided

### BE-03-19 (case_02_api#6) — Implement service `export_cases_csv`
**File:** `backend/app/modules/cases/service.py`

**Prompt**
In `cases/service.py`, implement ONLY function `export_cases_csv(db, filters:dict) -> str`:
- reuse filtering rules of list_cases (no pagination)
- return CSV string with header row (case_no, client_id, title_cn, app_no, status)

### BE-03-20 (case_02_api#1) — Implement endpoint `GET /cases`
**File:** `backend/app/modules/cases/api.py`

**Prompt**
In `cases/api.py`, implement ONLY endpoint `GET /cases`:
- permission: `Case.Read`
- query params per `case_02_api.md` #1
- call `list_cases`
- return `PageResult` with items mapped to `CaseListItem`

### BE-03-21 (case_02_api#2) — Implement endpoint `POST /cases`
**File:** `backend/app/modules/cases/api.py`

**Prompt**
In `cases/api.py`, implement ONLY endpoint `POST /cases`:
- permission: `Case.Create`
- body: `CaseCreate`
- return `CaseDetail` (or at least created case id + case_no)

### BE-03-22 (case_02_api#3) — Implement endpoint `GET /cases/{case_id}`
**File:** `backend/app/modules/cases/api.py`

**Prompt**
In `cases/api.py`, implement ONLY endpoint `GET /cases/{case_id}`:
- permission: `Case.Read`
- return `CaseDetail`

### BE-03-23 (case_02_api#4) — Implement endpoint `PUT /cases/{case_id}`
**File:** `backend/app/modules/cases/api.py`

**Prompt**
In `cases/api.py`, implement ONLY endpoint `PUT /cases/{case_id}`:
- permission: `Case.Edit`
- body: `CaseUpdateFull`
- return `CaseDetail`

### BE-03-24 (case_02_api#5) — Implement endpoint `POST /cases/{case_id}/limited-edit`
**File:** `backend/app/modules/cases/api.py`

**Prompt**
In `cases/api.py`, implement ONLY endpoint `POST /cases/{case_id}/limited-edit`:
- permission: `Case.EditLimited`
- body: `CaseUpdateLimited`
- return `CaseDetail`

### BE-03-25 (case_02_api#6) — Implement endpoint `GET /cases/export`
**File:** `backend/app/modules/cases/api.py`

**Prompt**
In `cases/api.py`, implement ONLY endpoint `GET /cases/export`:
- permission: `Case.Export`
- call `export_cases_csv`
- return `StreamingResponse` with `text/csv`

### BE-03-26 — Wire cases router
**File:** `backend/app/api/router.py`

**Prompt**
Update `app/api/router.py` ONLY:
- include `cases.router` under prefix `/cases`, tags `["cases"]`

---

## BE-04 Documents & Attachments (MVP1)
Doc refs:
- `backend/app/modules/documents/docs/doc_00_overview.md`
- `backend/app/modules/documents/docs/doc_01_db.md`
- `backend/app/modules/documents/docs/doc_02_api.md`

### BE-04-01 (doc_01_db:T_DocTemplate) — Implement model `T_DocTemplate`
**File:** `backend/app/modules/documents/models.py`

**Prompt**
In `documents/models.py`, implement ONLY `class T_DocTemplate`:
- Table: `T_DocTemplate`
- Columns: code(unique), name, direction(IN/OUT), enabled(bool)
- audit fields

### BE-04-02 (doc_01_db:T_Document) — Implement model `T_Document`
**File:** `backend/app/modules/documents/models.py`

**Prompt**
In `documents/models.py`, implement ONLY `class T_Document`:
- Table: `T_Document`
- Columns: case_id(index), doc_template_id(nullable), direction, doc_date, title, ref_no(nullable)
- audit fields

### BE-04-03 (doc_01_db:T_DocAttachment) — Implement model `T_DocAttachment`
**File:** `backend/app/modules/documents/models.py`

**Prompt**
In `documents/models.py`, implement ONLY `class T_DocAttachment`:
- Table: `T_DocAttachment`
- Columns: document_id(index), file_name, file_path, mime_type, size
- audit fields (uploaded_by/at can map to created_by/at)

### BE-04-04 — Add schema `DocumentCreate`
**File:** `backend/app/modules/documents/schemas.py`

**Prompt**
In `documents/schemas.py`, implement ONLY `class DocumentCreate(BaseModel)`:
- fields: `case_id:str`, `doc_template_id:str|None=None`, `direction:str`, `doc_date:date`, `title:str`, `ref_no:str|None=None`

### BE-04-05 — Add schema `DocumentOut`
**File:** `backend/app/modules/documents/schemas.py`

**Prompt**
In `documents/schemas.py`, implement ONLY `class DocumentOut(BaseModel)`:
- fields: `id`, `case_id`, `direction`, `doc_date`, `title`, `ref_no`, `attachments:list[dict]=[]`

### BE-04-06 (doc_02_api) — Implement service `list_documents`
**File:** `backend/app/modules/documents/service.py`

**Prompt**
In `documents/service.py`, implement ONLY function `list_documents(db, filters:dict, page:int, page_size:int)`:
- filters: q, direction, type(template), date range, case_id
- return `(items,total)`

### BE-04-07 (doc_02_api) — Implement service `create_document`
**File:** `backend/app/modules/documents/service.py`

**Prompt**
In `documents/service.py`, implement ONLY function `create_document(db, payload:DocumentCreate, actor_id:str|None)`:
- insert T_Document
- no attachment in this function

### BE-04-08 (doc_02_api) — Implement service `add_attachment`
**File:** `backend/app/modules/documents/service.py`

**Prompt**
In `documents/service.py`, implement ONLY function `add_attachment(db, document_id:str, upload_file, storage_dir:str, actor_id:str|None)`:
- ensure document exists
- save file under `{storage_dir}/attachments/{document_id}/...` using `safe_join` and `save_upload_file`
- create T_DocAttachment row
- return attachment metadata

### BE-04-09 (doc_02_api) — Implement endpoint `GET /documents`
**File:** `backend/app/modules/documents/api.py`

**Prompt**
In `documents/api.py`, implement ONLY endpoint `GET /documents`:
- permission: `Doc.Read`
- call `list_documents`
- return `PageResult`

### BE-04-10 (doc_02_api) — Implement endpoint `POST /documents`
**File:** `backend/app/modules/documents/api.py`

**Prompt**
In `documents/api.py`, implement ONLY endpoint `POST /documents`:
- permission: `Doc.Create`
- body: `DocumentCreate`
- return `DocumentOut`

### BE-04-11 (doc_02_api) — Implement endpoint `POST /documents/{id}/attachments`
**File:** `backend/app/modules/documents/api.py`

**Prompt**
In `documents/api.py`, implement ONLY endpoint `POST /documents/{id}/attachments`:
- permission: `Doc.Attach`
- accept multipart UploadFile field name `file`
- call `add_attachment` with `settings.storage_dir`
- return attachment dict

### BE-04-12 — Wire documents router
**File:** `backend/app/api/router.py`

**Prompt**
Update `app/api/router.py` ONLY:
- include `documents.router` under prefix `/documents`, tags `["documents"]`

---

## BE-05 Tasks / Docket (MVP1)
Doc refs:
- `backend/app/modules/tasks/docs/task_00_overview.md`
- `backend/app/modules/tasks/docs/task_01_db.md`
- `backend/app/modules/tasks/docs/task_02_api.md`

### BE-05-01 (task_01_db:T_TaskTemplate) — Implement model `T_TaskTemplate`
**File:** `backend/app/modules/tasks/models.py`

**Prompt**
In `tasks/models.py`, implement ONLY `class T_TaskTemplate`:
- Table: `T_TaskTemplate`
- Columns: code(unique), name
- audit fields

### BE-05-02 (task_01_db:T_Task) — Implement model `T_Task`
**File:** `backend/app/modules/tasks/models.py`

**Prompt**
In `tasks/models.py`, implement ONLY `class T_Task`:
- Table: `T_Task`
- Columns: case_id(index), task_template_id(nullable), title, content_summary(nullable)
- dates: official_date(nullable), internal_due_date(nullable), due_date
- worker_id, supervisor_id (nullable)
- status (OPEN/DONE/CANCELLED)
- done_at/by nullable
- audit fields

### BE-05-03 (task_01_db:T_TaskLog) — Implement model `T_TaskLog`
**File:** `backend/app/modules/tasks/models.py`

**Prompt**
In `tasks/models.py`, implement ONLY `class T_TaskLog`:
- Table: `T_TaskLog`
- Columns: task_id(index), action, from_status, to_status, remark(nullable)
- audit fields

### BE-05-04 — Add schema `TaskCreate`
**File:** `backend/app/modules/tasks/schemas.py`

**Prompt**
In `tasks/schemas.py`, implement ONLY `class TaskCreate(BaseModel)`:
- fields: `case_id:str|None=None`, `title:str`, `due_date:date`, `worker_id:str|None=None`, `supervisor_id:str|None=None`, `content_summary:str|None=None`

### BE-05-05 (task_02_api) — Implement service `list_tasks`
**File:** `backend/app/modules/tasks/service.py`

**Prompt**
In `tasks/service.py`, implement ONLY function `list_tasks(db, filters:dict, page:int, page_size:int)`:
- filters: status, due date range, worker, supervisor, case
- return `(items,total)`

### BE-05-06 (task_02_api) — Implement endpoint `GET /tasks`
**File:** `backend/app/modules/tasks/api.py`

**Prompt**
In `tasks/api.py`, implement ONLY endpoint `GET /tasks`:
- permission: `Task.Read`
- call `list_tasks`
- return `PageResult`

### BE-05-07 — Wire tasks router
**File:** `backend/app/api/router.py`

**Prompt**
Update `app/api/router.py` ONLY:
- include `tasks.router` under prefix `/tasks`, tags `["tasks"]`

---

## BE-06 Fees (MVP1)
Doc refs:
- `backend/app/modules/fees/docs/fee_00_overview.md`
- `backend/app/modules/fees/docs/fee_01_db.md`
- `backend/app/modules/fees/docs/fee_02_api.md`

### BE-06-01 (fee_01_db:T_FeeRate) — Implement model `T_FeeRate`
**File:** `backend/app/modules/fees/models.py`

**Prompt**
In `fees/models.py`, implement ONLY `class T_FeeRate`:
- Table: `T_FeeRate`
- Columns: group(nullable), fee_code(index), fee_name, fee_type(GOV/SERVICE/MISC), currency, default_amount, enabled
- audit fields

### BE-06-02 (fee_01_db:T_FeeDraft) — Implement model `T_FeeDraft`
**File:** `backend/app/modules/fees/models.py`

**Prompt**
In `fees/models.py`, implement ONLY `class T_FeeDraft`:
- Table: `T_FeeDraft`
- Columns: case_id(index), client_id(index), type(default GENERIC), currency, status(OPEN/LOCKED)
- totals: total_gov, total_service, total_misc, amount
- audit fields

### BE-06-03 (fee_01_db:T_FeeItem) — Implement model `T_FeeItem`
**File:** `backend/app/modules/fees/models.py`

**Prompt**
In `fees/models.py`, implement ONLY `class T_FeeItem`:
- Table: `T_FeeItem`
- Columns: draft_id(index), case_id(nullable), fee_code, fee_name, fee_type, year_no(nullable), quantity(nullable), unit_price(nullable), amount, remark(nullable)
- audit fields

### BE-06-04 (fee_02_api) — Implement endpoint `GET /fees/drafts`
**File:** `backend/app/modules/fees/api.py`

**Prompt**
In `fees/api.py`, implement ONLY endpoint `GET /fees/drafts`:
- permission: `Fee.Read`
- filters: case_id, client_id, status
- return `PageResult`
Constraints:
- If service layer missing, implement minimal query inline for MVP1.

### BE-06-05 — Wire fees router
**File:** `backend/app/api/router.py`

**Prompt**
Update `app/api/router.py` ONLY:
- include `fees.router` under prefix `/fees`, tags `["fees"]`

---

## BE-07 Billing (MVP1)
Doc refs:
- `backend/app/modules/billing/docs/bill_00_overview.md`
- `backend/app/modules/billing/docs/bill_01_db.md`
- `backend/app/modules/billing/docs/bill_02_api.md`

### BE-07-01 (bill_01_db:T_Bill) — Implement model `T_Bill`
**File:** `backend/app/modules/billing/models.py`

**Prompt**
In `billing/models.py`, implement ONLY `class T_Bill` per `bill_01_db.md`:
- bill_no unique
- totals + balance fields
- status: UNSETTLED/PARTIALLY_SETTLED/SETTLED
- audit fields

### BE-07-02 — Wire billing router
**File:** `backend/app/api/router.py`

**Prompt**
Update `app/api/router.py` ONLY:
- include `billing.router` under prefix `/billing`, tags `["billing"]`

---

## BE-08 Templates & Rendering (MVP1)
Doc ref: `backend/app/modules/templates/docs/tpl_00_overview.md`

### BE-08-01 — Implement bill render endpoint `GET /billing/bills/{id}/print`
**File:** `backend/app/modules/billing/api.py`

**Prompt**
In `billing/api.py`, implement ONLY endpoint `GET /bills/{id}/print` (mounted under `/api/v1/billing`):
- permission: `Bill.Print`
- for MVP1: return a placeholder `.docx` file generated with docxtpl using a sample template under `storage/templates/sample/`
Constraints:
- Do NOT add other endpoints.
- If template engine not ready, implement minimal docx with python-docx as fallback.

---

## BE-09 Migrations metadata wiring

### BE-09-01 — Import all models into Alembic metadata
**File:** `backend/app/db/base.py`

**Prompt**
Update `app/db/base.py` ONLY:
- keep `Base` definition
- add imports at bottom to load all `models.py` modules so Alembic sees tables:
  - auth.models
  - rbac.models
  - masterdata.clients.models
  - cases.models
  - documents.models
  - tasks.models
  - fees.models
  - billing.models
  - templates.models
Constraints:
- Do NOT create circular imports; only import modules, not symbols.

---

## TODO (items that need product decisions)
- Define a complete MVP1 enum set for `CaseStatus` (current tasks keep minimal OPEN/CLOSED).
- Decide whether to store UUIDs as native Postgres UUID type in prod (currently string).
- Decide attachment filename policy (preserve original vs generated) and retention.
- Decide whether RBAC is DB-only (current design) or allow code mapping override.
