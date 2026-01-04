# MVP1 Enhancement Tasks - Complete Index

**Generated**: 2026-01-03  
**Based on**: Comprehensive code review of FPMS backend MVP1

## Document References
- [Review Report](./mvp1_backend_review_report.md) - Detailed findings and analysis
- [Enhancement Checklist](./mvp1_enhancement_checklist.md) - Quick reference
- [Execution Guide](./README.md) - Phase order and rules

---

## Phase 1: Core Infrastructure (P0) - 6 tasks

### ENH-00 Series: Cross-cutting Utilities
- [x] **ENH-00-01** — Create `app/core/errors.py` (BusinessError, ErrorResponse)
- [x] **ENH-00-02** — Register exception handlers in `main.py`
- [x] **ENH-00-03** — Create `app/core/pagination.py` (PageParams, PageResult)
- [x] **ENH-00-04** — Create `app/db/mixins.py` (UUID, Audit mixins)
- [x] **ENH-00-05** — Create `app/core/security.py` (JWT + password hashing)
- [x] **ENH-00-06** — Create `app/core/storage.py` (safe file operations)

**Status**: 6/6 task files created  
**Estimate**: 2-3 days

---

## Phase 2: Authentication & RBAC (P0) - 8+ tasks

### ENH-01 Series: Auth Implementation
- [x] **ENH-01-01** — Add `T_RolePerm` model to `rbac/models.py`
- [ ] **ENH-01-02** — Create Alembic migration for `T_RolePerm` table
- [ ] **ENH-01-03** — Implement `get_user_permissions()` in `rbac/service.py`
- [ ] **ENH-01-04** — Implement `seed_default_roles_perms()` in `rbac/service.py`
- [ ] **ENH-01-05** — Create auth schemas (`LoginRequest`, `TokenResponse`, `MeResponse`)
- [ ] **ENH-01-06** — Implement `authenticate_user()` in `auth/service.py`
- [ ] **ENH-01-07** — Implement `POST /auth/login` endpoint
- [ ] **ENH-01-08** — Implement `GET /auth/me` endpoint
- [ ] **ENH-01-09** — Update `require_perm()` in `api/deps.py` for real RBAC
- [ ] **ENH-01-10** — Create `scripts/seed_dev.py` (roles + admin user)

**Status**: 1/10 task files created  
**Estimate**: 3-4 days

---

## Phase 3: Service Layer & Schemas (P0)

### ENH-02 Series: Cases Module (10 tasks)
- [ ] **ENH-02-01** — Create case enums (`CaseType`, `FlowDir`, `PatentCategory`)
- [ ] **ENH-02-02** — Add `T_CaseApplicant` model
- [ ] **ENH-02-03** — Add `T_CaseInventor` model
- [ ] **ENH-02-04** — Add `T_Priority` model
- [ ] **ENH-02-05** — Create case schemas (CaseCreate, CaseUpdate, CaseDetail, etc.)
- [ ] **ENH-02-06** — Implement `validate_applicants()` service function
- [ ] **ENH-02-07** — Implement `list_cases()` service function
- [ ] **ENH-02-08** — Implement `create_case()` service function
- [ ] **ENH-02-09** — Implement `update_case_full()` service function
- [ ] **ENH-02-10** — Implement `update_case_limited()` service function

**Estimate**: 2 days

### ENH-03 Series: Billing Module (10 tasks)
- [ ] **ENH-03-01** — Create billing schemas (all endpoints)
- [ ] **ENH-03-02** — Implement `validate_single_client()` helper
- [ ] **ENH-03-03** — Implement `validate_currency_match()` helper
- [ ] **ENH-03-04** — Implement `generate_bill_from_drafts()` service
- [ ] **ENH-03-05** — Implement `create_payment()` service
- [ ] **ENH-03-06** — Implement `create_offset()` service
- [ ] **ENH-03-07** — Implement `update_bill_balance()` helper
- [ ] **ENH-03-08** — Implement `update_case_receipt()` service
- [ ] **ENH-03-09** — Add Payment Line model/concept
- [ ] **ENH-03-10** — Implement bill status transitions

**Estimate**: 2 days

### ENH-04 Series: Documents Module (7 tasks)
- [ ] **ENH-04-01** — Create document schemas
- [ ] **ENH-04-02** — Implement `list_documents()` service
- [ ] **ENH-04-03** — Implement `create_document()` service
- [ ] **ENH-04-04** — Implement `add_attachment()` service with file validation
- [ ] **ENH-04-05** — Add document enums (direction, types)
- [ ] **ENH-04-06** — Implement document-case linking
- [ ] **ENH-04-07** — Implement document search/filter

**Estimate**: 1.5 days

### ENH-05 Series: Tasks Module (8 tasks)
- [ ] **ENH-05-01** — Create task schemas
- [ ] **ENH-05-02** — Add `T_TaskLog` model
- [ ] **ENH-05-03** — Implement task service layer (CRUD)
- [ ] **ENH-05-04** — Implement `GET /tasks/today` endpoint
- [ ] **ENH-05-05** — Implement `POST /tasks/{id}/close` endpoint
- [ ] **ENH-05-06** — Implement `POST /tasks/{id}/reopen` endpoint
- [ ] **ENH-05-07** — Implement `POST /tasks/{id}/assign` endpoint
- [ ] **ENH-05-08** — Implement task status transition validation

**Estimate**: 1.5 days

### ENH-06 Series: Fees Module (7 tasks)
- [ ] **ENH-06-01** — Create fee schemas
- [ ] **ENH-06-02** — Implement fee draft service layer
- [ ] **ENH-06-03** — Add FeeType enum (GOV/SERVICE/MISC)
- [ ] **ENH-06-04** — Implement draft locking mechanism
- [ ] **ENH-06-05** — Implement `POST /fees/drafts/{id}/lock` endpoint
- [ ] **ENH-06-06** — Implement `POST /fees/drafts/{id}/unlock` endpoint
- [ ] **ENH-06-07** — Implement fee item CRUD

**Estimate**: 1 day

### ENH-07 Series: Clients Module (4 tasks)
- [ ] **ENH-07-01** — Create client schemas (proper types, no dict)
- [ ] **ENH-07-02** — Implement client service layer
- [ ] **ENH-07-03** — Add client code uniqueness validation
- [ ] **ENH-07-04** — Fix addresses/contacts as proper schemas

**Estimate**: 1 day

**Phase 3 Total**: 46 tasks, 9-10 days

---

## Phase 4: Database Enhancements (P0) - 5 tasks

### ENH-08 Series: Database
- [ ] **ENH-08-01** — Create comprehensive initial migration (or consolidate existing)
- [ ] **ENH-08-02** — Add database indexes per spec
- [ ] **ENH-08-03** — Add foreign key constraints
- [ ] **ENH-08-04** — Create database seeding script
- [ ] **ENH-08-05** — Update models to use mixins

**Estimate**: 1-2 days

---

## Phase 5: API Refactoring (P0) - ~20 tasks

### ENH-09 Series: Refactor APIs to Use Service Layer
All existing API endpoints must be refactored to:
1. Use Pydantic schemas (no `dict[str, Any]`)
2. Call service layer (no direct DB access in API)
3. Use BusinessError for failures

Specific tasks (one per module):
- [ ] **ENH-09-01** — Refactor cases API endpoints
- [ ] **ENH-09-02** — Refactor billing API endpoints
- [ ] **ENH-09-03** — Refactor documents API endpoints
- [ ] **ENH-09-04** — Refactor tasks API endpoints
- [ ] **ENH-09-05** — Refactor fees API endpoints
- [ ] **ENH-09-06** — Refactor clients API endpoints
- [ ] **ENH-09-07** — Fix CSV export (currently returns JSON)

**Estimate**: 3-4 days

---

## Phase 6: Business Logic & Validation (P1) - ~15 tasks

### ENH-10 Series: Business Rules
- [ ] **ENH-10-01** — Cases: Priority date auto-calculation
- [ ] **ENH-10-02** — Cases: Enforce limited edit whitelist
- [ ] **ENH-10-03** — Billing: Bill balance calculation on offset
- [ ] **ENH-10-04** — Billing: Auto-update case receipts
- [ ] **ENH-10-05** — Tasks: Auto-create task log on status change
- [ ] **ENH-10-06** — Fees: Prevent editing locked drafts
- [ ] ... (more as needed)

**Estimate**: 4-5 days

---

## Phase 7: Testing & Documentation (P1) - ~25 tasks

### ENH-11 Series: Testing
- [ ] **ENH-11-01** — Set up pytest structure and conftest.py
- [ ] **ENH-11-02** — Create test fixtures (DB, users, clients)
- [ ] **ENH-11-03** — Unit tests for service layer (all modules)
- [ ] **ENH-11-04** — Integration tests for key user flows
- [ ] **ENH-11-05** — Add test coverage reporting
- [ ] **ENH-11-06** — CI/CD pipeline configuration

**Estimate**: 5-7 days

### ENH-12 Series: Documentation
- [ ] **ENH-12-01** — Add docstrings to all endpoints
- [ ] **ENH-12-02** — Create API usage guide
- [ ] **ENH-12-03** — Document environment variables
- [ ] **ENH-12-04** — Create deployment runbook
- [ ] **ENH-12-05** — Document error codes
- [ ] **ENH-12-06** — Create database schema diagram (Mermaid)

**Estimate**: 2-3 days

---

## Summary Statistics

| Phase | Tasks | Task Files Created | Estimate |
|-------|-------|-------------------|----------|
| Phase 1: Core Infrastructure | 6 | 6/6 (100%) | 2-3 days |
| Phase 2: Auth & RBAC | 10 | 1/10 (10%) | 3-4 days |
| Phase 3: Service & Schemas | 46 | 0/46 (0%) | 9-10 days |
| Phase 4: Database | 5 | 0/5 (0%) | 1-2 days |
| Phase 5: API Refactoring | 7+ | 0/7 (0%) | 3-4 days |
| Phase 6: Business Logic | 15+ | 0/15 (0%) | 4-5 days |
| Phase 7: Testing & Docs | 25+ | 0/25 (0%) | 7-10 days |
| **TOTAL** | **~120** | **7/120 (6%)** | **40-53 days** |

---

## Quick Start

### 1. Execute Phase 1 (Core Infrastructure)
```bash
# In order:
# ENH-00-01, ENH-00-02, ENH-00-03, ENH-00-04, ENH-00-05, ENH-00-06
```

### 2. Execute Phase 2 (Auth & RBAC)
```bash
# Complete authentication system
# Then seed admin user and permissions
```

### 3. Continue through remaining phases
See [README.md](./README.md) for detailed execution order.

---

## Notes
- ✅ Task file exists and is ready for execution
- ☐ Task file not yet created (TOD)
- Task files follow AGENTS.md atomic task rules
- Each task is self-contained and executable independently within its phase
- Prerequisites are clearly documented in each task file

---

**Last Updated**: 2026-01-03  
**Next Step**: Create remaining task files for Phases 2-7 (ongoing)
