# Summary Index: Remaining Task Files To Create

This file documents the remaining 90+ task files that need to be created to complete the full MVP1 enhancement task set.

## Status: 26/120 Created (22%)

### ✅ COMPLETED MODULES
- Phase 1: Infrastructure (ENH-00-01 to ENH-00-06) - 6 files
- Phase 2: Auth/RBAC (ENH-01-01 to ENH-01-10) - 10 files  
- Phase 3a: Cases Module (ENH-02-01 to ENH-02-10) - 10 files

### 📝 REMAINING TO CREATE

#### Phase 3b: Billing Module (ENH-03 series) - 10 files
- ENH-03-01: Create billing schemas (all endpoints)
- ENH-03-02: Implement validate_single_client helper
- ENH-03-03: Implement validate_currency_match helper
- ENH-03-04: Implement generate_bill_from_drafts service
- ENH-03-05: Implement create_payment service
- ENH-03-06: Implement create_offset service
- ENH-03-07: Implement update_bill_balance helper
- ENH-03-08: Implement update_case_receipt service
- ENH-03-09: Add Payment Line model/concept
- ENH-03-10: Implement bill status transitions

#### Phase 3c: Documents Module (ENH-04 series) - 7 files
- ENH-04-01: Create document schemas
- ENH-04-02: Implement list_documents service
- ENH-04-03: Implement create_document service
- ENH-04-04: Implement add_attachment service with validation
- ENH-04-05: Add document enums (direction, types)
- ENH-04-06: Implement document-case linking
- ENH-04-07: Implement document search/filter service

#### Phase 3d: Tasks Module (ENH-05 series) - 8 files
- ENH-05-01: Create task schemas
- ENH-05-02: Add T_TaskLog model
- ENH-05-03: Implement task service layer (CRUD)
- ENH-05-04: Implement GET /tasks/today logic
- ENH-05-05: Implement close task service
- ENH-05-06: Implement reopen task service  
- ENH-05-07: Implement assign task service
- ENH-05-08: Implement task status transition validation

#### Phase 3e: Fees Module (ENH-06 series) - 7 files
- ENH-06-01: Create fee schemas
- ENH-06-02: Implement fee draft service layer
- ENH-06-03: Add FeeType enum (GOV/SERVICE/MISC)
- ENH-06-04: Implement draft locking mechanism
- ENH-06-05: Implement lock draft service
- ENH-06-06: Implement unlock draft service
- ENH-06-07: Implement fee item CRUD services

#### Phase 3f: Clients Module (ENH-07 series) - 4 files
- ENH-07-01: Create client schemas (proper types, no dict)
- ENH-07-02: Implement client service layer
- ENH-07-03: Add client code uniqueness validation
- ENH-07-04: Fix addresses/contacts as proper schemas

#### Phase 4: Database Enhancements (ENH-08 series) - 5 files
- ENH-08-01: Create comprehensive initial migration
- ENH-08-02: Add database indexes per spec
- ENH-08-03: Add foreign key constraints
- ENH-08-04: Create database seeding script
- ENH-08-05: Update existing models to use mixins

#### Phase 5: API Refactoring (ENH-09 series) - 7 files
- ENH-09-01: Refactor cases API to use service layer
- ENH-09-02: Refactor billing API to use service layer
- ENH-09-03: Refactor documents API to use service layer
- ENH-09-04: Refactor tasks API to use service layer
- ENH-09-05: Refactor fees API to use service layer
- ENH-09-06: Refactor clients API to use service layer
- ENH-09-07: Fix CSV export (returns JSON currently)

#### Phase 6: Business Logic & Validation (ENH-10 series) - 15 files
- ENH-10-01: Cases - Priority date auto-calculation
- ENH-10-02: Cases - Enforce limited edit whitelist
- ENH-10-03: Billing - Bill balance calculation on offset
- ENH-10-04: Billing - Auto-update case receipts
- ENH-10-05: Tasks - Auto-create task log on status change
- ENH-10-06: Fees - Prevent editing locked drafts
- ENH-10-07: Billing - Single-client validation
- ENH-10-08: Billing - Currency consistency check
- ENH-10-09: Billing - Payment offset validation
- ENH-10-10: Cases - Case number uniqueness enforcement
- ENH-10-11: Tasks - Status transition rules
- ENH-10-12: Fees - Fee item validation
- ENH-10-13: Documents - Attachment file type validation
- ENH-10-14: Cases - Applicant first flag validation
- ENH-10-15: Documents - Template path security check

#### Phase 7a: Testing (ENH-11 series) - 6 files
- ENH-11-01: Set up pytest structure and conftest.py
- ENH-11-02: Create test fixtures (DB, users, clients)
- ENH-11-03: Unit tests for auth and RBAC services
- ENH-11-04: Unit tests for cases services
- ENH-11-05: Integration tests for key user flows
- ENH-11-06: Add test coverage reporting config

#### Phase 7b: Documentation (ENH-12 series) - 6 files
- ENH-12-01: Add docstrings to all endpoints
- ENH-12-02: Create API usage guide
- ENH-12-03: Document environment variables
- ENH-12-04: Create deployment runbook
- ENH-12-05: Document error codes
- ENH-12-06: Create database schema diagram (Mermaid)

## Total Remaining: 94 files

## Creation Strategy
Due to the large volume, the remaining files will be created systematically:
1. Complete all P0 module service/schema tasks first (Phases 3b-3f)
2. Create database and API refactoring tasks (Phases 4-5)
3. Add business logic validation tasks (Phase 6)
4. Finish with testing and documentation tasks (Phase 7)

**Note**: This is a tracking file. Individual task files still need to be created following the established format.


## Auto-generated tasks completed on 2026-01-03
- ENH-03-01
- ENH-03-02
- ENH-03-03
- ENH-03-04
- ENH-03-05
- ENH-03-06
- ENH-03-07
- ENH-03-08
- ENH-03-09
- ENH-03-10
- ENH-04-01
- ENH-04-02
- ENH-04-03
- ENH-04-04
- ENH-04-05
- ENH-04-06
- ENH-04-07
- ENH-05-01
- ENH-05-02
- ENH-05-03
- ENH-05-04
- ENH-05-05
- ENH-05-06
- ENH-05-07
- ENH-05-08
- ENH-06-01
- ENH-06-02
- ENH-06-03
- ENH-06-04
- ENH-06-05
- ENH-06-06
- ENH-06-07
- ENH-07-01
- ENH-07-02
- ENH-07-03
- ENH-07-04
- ENH-08-01
- ENH-08-02
- ENH-08-03
- ENH-08-04
- ENH-08-05
- ENH-09-01
- ENH-09-02
- ENH-09-03
- ENH-09-04
- ENH-09-05
- ENH-09-06
- ENH-09-07
- ENH-10-01
- ENH-10-02
- ENH-10-03
- ENH-10-04
- ENH-10-05
- ENH-10-06
- ENH-10-07
- ENH-10-08
- ENH-10-09
- ENH-10-10
- ENH-10-11
- ENH-10-12
- ENH-10-13
- ENH-10-14
- ENH-10-15
- ENH-11-01
- ENH-11-02
- ENH-11-03
- ENH-11-04
- ENH-11-05
- ENH-11-06
- ENH-12-01
- ENH-12-02
- ENH-12-03
- ENH-12-04
- ENH-12-05
- ENH-12-06
