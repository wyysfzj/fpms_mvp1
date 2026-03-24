# B1 Batch — Task Plan

## Goal
Add SPEC 2.0 configuration fields to T_DocTemplate for automation. Provide CRUD API. Seed 5 templates.

## Team
| Role | Agent | Status |
|------|-------|--------|
| Architect | architect | PENDING |
| Backend Impl | backend-impl | PENDING |
| Test Impl | test-impl | PENDING |
| Reviewer | reviewer | PENDING |

## Execution Order
1. Architect → writes 01_Architect_Plan.md → waits for Lead approval
2. Backend Agent → implements migration, models, schemas, service, api, seed, perms
3. Test Agent → writes tests (test_doc_template.py)
4. Reviewer → reviews all, writes 04_Reviewer_Report.md

## Spec Reference
- Source: tasks/Claude_enhance.md lines 652-714
- 8 new columns on t_doc_template
- 4 new API endpoints (GET/POST /doc-templates, GET/PUT /doc-templates/{id})
- 3 new permissions (DocTemplate.Read, DocTemplate.Create, DocTemplate.Edit)
- 5 seed templates (OA_IN, OA_OUT, ACCEPTANCE_NOTICE, GRANT_NOTICE, CLIENT_IN)
