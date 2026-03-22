# SPEC 2.0 Technical Risk Mitigation Plan

## Executive Summary

**Objective**: Resolve dirty worktree risk and ensure SPEC 2.0 non-document-generation scope is production-ready.

**Scope**:
- Clean up modified files in git worktree
- Verify all Batch 1-5A changes are committed with proper audit trail
- Ensure no unintended changes leak into production
- Validate database migration integrity

**Out of Scope**: Document generation implementation, consulting/search modules

**Timeline**: 2-3 hours execution + 1 hour validation

---

## Current Risk Assessment

### Risk 1: Dirty Worktree (HIGH)

**Evidence** (from git status):
```
M AGENTS.md
M backend/app/modules/annuity/service.py
M backend/app/modules/billing/api.py
... (85+ modified files)
?? backend/alembic/versions/pe_be_db_cm_02_case_ext_fields.py
?? docs/BATCH_EXECUTION_*.md
?? tasks/postenhancement/
```

**Impact**:
- Cannot distinguish intentional changes from accidental edits
- Risk of committing debug code, incomplete features, or broken logic
- Merge conflicts if multiple branches exist
- Audit trail broken for Batch 1-5A execution

**Root Cause**:
- Batch 1-5A execution completed but changes not committed atomically per batch
- Planning/manifest documents added but not committed
- Migration file generated but not committed

---

## Mitigation Strategy

### Phase 1: Inventory & Classification (30 min)

#### Step 1.1: Generate Full Diff Report
```bash
cd /Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic

# Generate comprehensive diff
git diff --stat > /tmp/fpms_diff_stat.txt
git diff > /tmp/fpms_diff_full.txt

# List untracked files
git ls-files --others --exclude-standard > /tmp/fpms_untracked.txt
```

#### Step 1.2: Classify Changes by Batch

Create classification matrix:

| File Pattern | Expected Batch | Verification Method |
|--------------|----------------|---------------------|
| `backend/app/modules/cases/*` | Batch 1 | Check against `artifacts/PE-BE-CM-*/` |
| `frontend/src/modules/cases/*` | Batch 1 | Check against `artifacts/PE-FE-CM-*/` |
| `backend/app/modules/documents/*` | Batch 2 | Check against `artifacts/PE-BE-WD-*/` |
| `backend/app/modules/tasks/*` | Batch 2 | Check against `artifacts/PE-BE-DL-*/` |
| `backend/app/modules/fees/*` | Batch 3 | Check against `artifacts/PE-BE-FE-*/` |
| `backend/app/modules/annuity/*` | Batch 3 | Check against `artifacts/PE-BE-AN-*/` |
| `backend/app/modules/billing/*` | Batch 4 | Check against `artifacts/PE-BE-BL-*/` |
| `backend/app/modules/collections/*` | Batch 4 | Check against `artifacts/PE-BE-DL-*/` |
| `backend/app/modules/commission/*` | Batch 5A | Check against `artifacts/PE-BE-COM-*/` |
| `frontend/src/modules/commission/*` | Batch 5A | Check against `artifacts/PE-FE-COM-*/` |
| `backend/alembic/versions/pe_be_db_cm_02_*` | Batch 1 | Check against `PE-BE-DB-CM-02.md` |
| `docs/BATCH_EXECUTION_*.md` | Planning | Safe to commit |
| `tasks/postenhancement/` | Planning | Safe to commit |
| `AGENTS.md` | Process | Review diff for unintended changes |

#### Step 1.3: Identify Anomalies

Run automated checks:
```bash
# Check for debug statements
grep -r "console.log\|print(\|debugger\|pdb.set_trace" \
  backend/app/modules/ frontend/src/modules/ \
  --include="*.py" --include="*.ts" --include="*.vue"

# Check for TODO/FIXME
grep -r "TODO\|FIXME\|XXX\|HACK" \
  backend/app/modules/ frontend/src/modules/ \
  --include="*.py" --include="*.ts" --include="*.vue"

# Check for hardcoded credentials
grep -ri "password\|secret\|api_key\|token" \
  backend/app/modules/ frontend/src/modules/ \
  --include="*.py" --include="*.ts" --include="*.vue" \
  | grep -v "password_hash\|get_password\|require.*token"
```

---

### Phase 2: Validation Against Artifacts (45 min)

#### Step 2.1: Backend Module Validation

For each modified backend file, verify against task artifacts:

```bash
# Example: Validate cases module changes
cd backend

# Extract changed functions/classes
git diff app/modules/cases/service.py | grep "^[+-]def \|^[+-]class "

# Cross-reference with artifacts
cat /Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/artifacts/PE-BE-CM-01/review_report.md
cat /Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/artifacts/PE-BE-CM-02/review_report.md
```

**Validation Checklist per Module**:
- [ ] All changes documented in corresponding `PE-BE-*` task file
- [ ] No changes outside task scope
- [ ] Review report exists and shows PASS
- [ ] Test coverage exists in `backend/tests/test_*.py`

#### Step 2.2: Frontend Module Validation

```bash
# Example: Validate cases module changes
cd frontend

# Extract changed components
git diff src/modules/cases/ --name-only

# Cross-reference with artifacts
cat /Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/artifacts/PE-FE-CM-01/review_report.md
cat /Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/artifacts/PE-FE-CM-02/review_report.md
```

**Validation Checklist per Module**:
- [ ] All changes documented in corresponding `PE-FE-*` task file
- [ ] No changes outside task scope
- [ ] TypeScript types updated in `src/api/*.types.ts`
- [ ] No lint/typecheck errors

#### Step 2.3: Database Migration Validation

```bash
cd backend

# Verify migration file matches task spec
cat alembic/versions/pe_be_db_cm_02_case_ext_fields.py

# Cross-reference with task
cat /Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/tasks/postenhancement/backend/PE-BE-DB-CM-02.md

# Test migration on fresh DB
rm -f fpms_dev.db
alembic upgrade head
python scripts/seed_dev.py

# Verify schema
sqlite3 fpms_dev.db ".schema t_case"
```

**Migration Validation Checklist**:
- [ ] Migration file name matches task ID
- [ ] All columns from task spec present
- [ ] Uses `batch_alter_table` for SQLite compatibility
- [ ] No `downgrade()` implementation (forward-only)
- [ ] Fresh DB migration succeeds
- [ ] Seed script succeeds

---

### Phase 3: Commit Strategy (45 min)

#### Step 3.1: Atomic Commits by Batch

**Commit Order** (respects dependency):
1. Planning documents (no code dependency)
2. Database migration (Batch 1 dependency)
3. Batch 1 backend (depends on migration)
4. Batch 1 frontend (depends on Batch 1 backend API)
5. Batch 2 backend
6. Batch 2 frontend
7. Batch 3 backend
8. Batch 3 frontend
9. Batch 4 backend
10. Batch 4 frontend
11. Batch 5A backend
12. Batch 5A frontend
13. Process documents (AGENTS.md, etc.)

#### Step 3.2: Commit Template

```bash
# Commit 1: Planning documents
git add docs/BATCH_EXECUTION_*.md \
        docs/FPMS_Batch*_Scope_Adjustment_*.md \
        docs/Batch_Execution_Improvement_Plan_*.md \
        tasks/postenhancement/

git commit -m "docs: add Batch 1-5A planning and manifest documents

- BATCH_EXECUTION_QA_LEDGER_TEMPLATE_20260318.md
- BATCH_EXECUTION_TAKEOVER_RULES_20260318.md
- BATCH_EXECUTION_TASK_TEMPLATE_20260318.md
- Batch_Execution_Improvement_Plan_20260316.md
- FPMS_Batch1_Scope_Adjustment_20260315.md
- FPMS_Batch5_Scope_Adjustment_20260321.md
- FPMS_Final_Enhancement_execution_summary_20260315.md
- tasks/postenhancement/ (all atomic task files)

Ref: FPMS_Final_Enhancement_Plan_Native_20260315.md"

# Commit 2: Database migration
git add backend/alembic/versions/pe_be_db_cm_02_case_ext_fields.py

git commit -m "feat(db): add case extended fields migration (PE-BE-DB-CM-02)

- Add case_source, case_category, case_subcategory
- Add internal_deadline, external_deadline
- Add estimated_amount, actual_amount
- Add is_urgent, urgency_level, urgency_reason
- Add related_case_id, relation_type

Task: PE-BE-DB-CM-02
Batch: 1
Artifact: artifacts/PE-BE-DB-CM-02/
Test: pytest tests/test_case_fields.py -v"

# Commit 3: Batch 1 backend
git add backend/app/modules/cases/api.py \
        backend/app/modules/cases/models.py \
        backend/app/modules/cases/schemas.py \
        backend/app/modules/cases/service.py \
        backend/app/modules/cases/enums.py \
        backend/tests/test_case_fields.py

git commit -m "feat(cases): implement Batch 1 case enhancements (PE-BE-CM-01, PE-BE-CM-02)

Backend changes:
- PE-BE-CM-01: Extended case fields with validation
- PE-BE-CM-02: Case relationship and cross-field validation

Modified:
- api.py: Add extended field endpoints
- models.py: Add T_Case extended columns
- schemas.py: Add CaseExtended request/response schemas
- service.py: Add cross-field validation logic
- enums.py: Add CaseSource, CaseCategory, RelationType

Tests:
- test_case_fields.py: 15 test cases covering extended fields

Batch: 1
Artifacts: artifacts/PE-BE-CM-01/, artifacts/PE-BE-CM-02/
QA: PE-QA-CM-01 PASS"

# Commit 4: Batch 1 frontend
git add frontend/src/modules/cases/pages/CaseCreate.vue \
        frontend/src/modules/cases/pages/CaseEdit.vue \
        frontend/src/modules/cases/pages/CaseDetail.vue \
        frontend/src/api/cases.ts \
        frontend/src/api/cases.types.ts \
        frontend/src/constants/workflow.ts

git commit -m "feat(cases): implement Batch 1 case UI enhancements (PE-FE-CM-01, PE-FE-CM-02, PE-FE-CM-03)

Frontend changes:
- PE-FE-CM-01: Extended case form fields
- PE-FE-CM-02: Case relationship UI
- PE-FE-CM-03: Cross-field validation feedback

Modified:
- CaseCreate.vue: Add extended field form groups
- CaseEdit.vue: Add extended field editing
- CaseDetail.vue: Display extended fields
- cases.ts: Add extended field API calls
- cases.types.ts: Add CaseExtended TypeScript types
- workflow.ts: Add case source/category constants

Batch: 1
Artifacts: artifacts/PE-FE-CM-01/, artifacts/PE-FE-CM-02/, artifacts/PE-FE-CM-03/
QA: PE-QA-CM-03 PASS
Lint: PASS
Typecheck: PASS"

# Repeat pattern for Batch 2-5A...
```

#### Step 3.3: Commit Validation Gate

Before each commit:
```bash
# Backend commits
cd backend
ruff check --fix .
ruff format .
pytest -q tests/test_*.py

# Frontend commits
cd frontend
npm run lint
npm run typecheck
npm run build
```

---

### Phase 4: Final Verification (30 min)

#### Step 4.1: Clean Slate Test

```bash
# Simulate fresh clone
cd /tmp
git clone /Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic fpms_clean_test
cd fpms_clean_test

# Backend setup
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env

# Database setup
rm -f fpms_dev.db
alembic upgrade head
python scripts/seed_dev.py

# Run tests
pytest -q

# Start server (background)
uvicorn app.main:app --reload --port 8000 &
SERVER_PID=$!

# Frontend setup
cd ../frontend
npm install
cp .env.example .env

# Quality gates
npm run lint
npm run typecheck
npm run build

# Cleanup
kill $SERVER_PID
```

#### Step 4.2: Regression Test Suite

```bash
cd backend

# Run all Batch test files
pytest -v \
  tests/test_case_fields.py \
  tests/test_b2_reply_chain.py \
  tests/test_task_template.py \
  tests/test_b3_fee_linking.py \
  tests/test_b5_billing_polish.py \
  tests/test_annuity_e2e.py \
  tests/test_collections_e2e.py \
  tests/test_commission_e2e.py

# Expected: All tests PASS
```

#### Step 4.3: API Contract Verification

```bash
# Start backend
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000 &
SERVER_PID=$!

# Wait for startup
sleep 5

# Test critical endpoints
curl -X GET http://localhost:8000/healthz
curl -X GET http://localhost:8000/docs

# Login and get token
TOKEN=$(curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' \
  | jq -r '.access_token')

# Test Batch 1-5A endpoints
curl -X GET http://localhost:8000/api/v1/cases \
  -H "Authorization: Bearer $TOKEN"

curl -X GET http://localhost:8000/api/v1/documents \
  -H "Authorization: Bearer $TOKEN"

curl -X GET http://localhost:8000/api/v1/tasks \
  -H "Authorization: Bearer $TOKEN"

curl -X GET http://localhost:8000/api/v1/fees/rates \
  -H "Authorization: Bearer $TOKEN"

curl -X GET http://localhost:8000/api/v1/billing/bills \
  -H "Authorization: Bearer $TOKEN"

curl -X GET http://localhost:8000/api/v1/commission/records \
  -H "Authorization: Bearer $TOKEN"

# Cleanup
kill $SERVER_PID
```

---

## Risk Mitigation Checklist

### Pre-Commit Checklist
- [ ] All modified files classified by batch
- [ ] All changes cross-referenced with task artifacts
- [ ] No debug code (console.log, print, debugger)
- [ ] No TODO/FIXME/HACK comments
- [ ] No hardcoded credentials
- [ ] All changes within approved SPEC 2.0 scope
- [ ] No document generation code added

### Commit Quality Checklist
- [ ] Atomic commits per batch
- [ ] Commit messages follow template
- [ ] Each commit references task ID and artifact path
- [ ] Backend commits pass: ruff + pytest
- [ ] Frontend commits pass: lint + typecheck + build

### Post-Commit Checklist
- [ ] Clean slate test passes
- [ ] All regression tests pass
- [ ] API contract verification passes
- [ ] Git log shows clear audit trail
- [ ] No uncommitted changes remain

---

## Rollback Plan

If validation fails at any phase:

### Rollback Strategy
```bash
# Create safety branch before starting
git checkout -b backup/pre-cleanup-$(date +%Y%m%d)
git checkout master

# If Phase 2 validation fails
git reset --hard backup/pre-cleanup-YYYYMMDD

# If Phase 3 commit fails
git reset --soft HEAD~1  # Undo last commit, keep changes
# Fix issues, re-commit

# If Phase 4 verification fails
git revert <commit-hash>  # Revert specific commit
```

### Emergency Contacts
- Technical Lead: Review `artifacts/*/review_report.md` for original acceptance criteria
- QA Lead: Review `tasks/postenhancement/backend/PE-QA-*.md` for test evidence

---

## Success Criteria

### Technical Criteria
- [ ] Zero uncommitted changes in worktree
- [ ] All Batch 1-5A changes committed with audit trail
- [ ] All tests pass on clean clone
- [ ] Backend: `pytest -q` → all PASS
- [ ] Frontend: `npm run lint && npm run typecheck && npm run build` → all PASS
- [ ] API endpoints return expected responses

### Business Criteria
- [ ] All SPEC 2.0 non-document-generation scope implemented
- [ ] No consulting/search module code present
- [ ] No document generation code present
- [ ] All changes traceable to approved task files

### Audit Criteria
- [ ] Git log shows clear batch progression
- [ ] Each commit references task ID and artifact
- [ ] Commit messages explain business value
- [ ] No "WIP" or "fix" commits without context

---

## Execution Timeline

| Phase | Duration | Owner | Blocker Risk |
|-------|----------|-------|--------------|
| Phase 1: Inventory | 30 min | Tech Lead | Low |
| Phase 2: Validation | 45 min | Tech Lead + QA | Medium (anomalies found) |
| Phase 3: Commit | 45 min | Tech Lead | Medium (test failures) |
| Phase 4: Verification | 30 min | QA | Low |
| **Total** | **2.5 hours** | | |

**Recommended Execution Window**: Off-peak hours, with rollback buffer

---

## Appendix A: Quick Reference Commands

```bash
# Generate diff report
git diff --stat > /tmp/fpms_diff_stat.txt
git diff > /tmp/fpms_diff_full.txt

# Check for debug code
grep -r "console.log\|print(\|debugger" backend/ frontend/ --include="*.py" --include="*.ts" --include="*.vue"

# Validate backend
cd backend && ruff check --fix . && ruff format . && pytest -q

# Validate frontend
cd frontend && npm run lint && npm run typecheck && npm run build

# Fresh DB test
cd backend && rm -f fpms_dev.db && alembic upgrade head && python scripts/seed_dev.py

# Create safety branch
git checkout -b backup/pre-cleanup-$(date +%Y%m%d)
```

---

## Appendix B: File Classification Matrix

See Phase 1, Step 1.2 for full matrix.

---

**Document Version**: 1.0
**Last Updated**: 2026-03-22
**Owner**: Technical Lead
**Approver**: Project Architect
