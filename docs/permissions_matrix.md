# Permissions Matrix (Phase 3 API Tasks) — Unified v4

This matrix maps each endpoint to a unified permission code aligned with `docs/02_permissions_rbac.md` naming style. It does not define role grants; those live in `docs/02_permissions_rbac.md` and the runtime seed in `backend/app/modules/rbac/service.py`.


## Convention
- Read/Create/Edit/Delete/Action/Print/Export/Attach/EditLimited
Note (MVP1): permission codes use `Title.Action` naming and must stay consistent.


## Matrix

- `GET /clients` → `Client.Read`  (task: `BE-APIv4-001_clients_get_clients`)
- `POST /clients` → `Client.Create`  (task: `BE-APIv4-002_clients_post_clients`)
- `PUT /clients/{id}` → `Client.Edit`  (task: `BE-APIv4-003_clients_put_clients_id`)
- `PUT /clients/{id}/deactivate` → `Client.Action`  (task: `BE-APIv4-004_clients_put_clients_id_deactivate`)
- `GET /cases` → `Case.Read`  (task: `BE-APIv4-005_cases_get_cases`)
- `POST /cases` → `Case.Create`  (task: `BE-APIv4-006_cases_post_cases`)
- `GET /cases/{case_id}` → `Case.Read`  (task: `BE-APIv4-007_cases_get_cases_case_id`)
- `PUT /cases/{case_id}` → `Case.Edit`  (task: `BE-APIv4-008_cases_put_cases_case_id`)
- `POST /cases/{case_id}/limited-edit` → `Case.EditLimited`  (task: `BE-APIv4-009_cases_post_cases_case_id_limited-edit`)
- `GET /cases/export` → `Case.Export`  (task: `BE-APIv4-010_cases_get_cases_export`)
- `GET /documents` → `Doc.Read`  (task: `BE-APIv4-011_documents_get_documents`)
- `POST /documents` → `Doc.Create`  (task: `BE-APIv4-012_documents_post_documents`)
- `GET /documents/{id}` → `Doc.Read`  (task: `BE-APIv4-013_documents_get_documents_id`)
- `PUT /documents/{id}` → `Doc.Edit`  (task: `BE-APIv4-014_documents_put_documents_id`)
- `POST /documents/{id}/attachments` → `Doc.Attach`  (task: `BE-APIv4-015_documents_post_documents_id_attachments`)
- `GET /documents/{id}/attachments/{att_id}/download` → `Doc.Attach`  (task: `BE-APIv4-016_documents_get_documents_id_attachments_att_id_download`)
- `GET /tasks` → `Task.Read`  (task: `BE-APIv4-017_tasks_get_tasks`)
- `POST /tasks` → `Task.Create`  (task: `BE-APIv4-018_tasks_post_tasks`)
- `GET /tasks/{id}` → `Task.Read`  (task: `BE-APIv4-019_tasks_get_tasks_id`)
- `PUT /tasks/{id}` → `Task.Edit`  (task: `BE-APIv4-020_tasks_put_tasks_id`)
- `POST /tasks/{id}/close` → `Task.Action`  (task: `BE-APIv4-021_tasks_post_tasks_id_close`)
- `POST /tasks/{id}/reopen` → `Task.Action`  (task: `BE-APIv4-022_tasks_post_tasks_id_reopen`)
- `POST /tasks/{id}/cancel` → `Task.Action`  (task: `BE-APIv4-023_tasks_post_tasks_id_cancel`)
- `GET /tasks/today?as=worker|supervisor` → `Task.Read`  (task: `BE-APIv4-024_tasks_get_tasks_today?as=worker|supervisor`)
- `GET /fees/drafts` → `Fee.Draft.Read`  (task: `BE-APIv4-025_fees_get_fees_drafts`)
- `POST /fees/drafts` → `Fee.Draft.Create`  (task: `BE-APIv4-026_fees_post_fees_drafts`)
- `GET /fees/drafts/{id}` → `Fee.Draft.Read`  (task: `BE-APIv4-027_fees_get_fees_drafts_id`)
- `PUT /fees/drafts/{id}` → `Fee.Draft.Edit`  (task: `BE-APIv4-028_fees_put_fees_drafts_id`)
- `POST /fees/drafts/{id}/lock` → `Fee.Draft.Action`  (task: `BE-APIv4-029_fees_post_fees_drafts_id_lock`)
- `POST /fees/drafts/{id}/unlock` → `Fee.Draft.Action`  (task: `BE-APIv4-030_fees_post_fees_drafts_id_unlock`)
- `POST /fees/drafts/{id}/items` → `Fee.Item.Create`  (task: `BE-APIv4-031_fees_post_fees_drafts_id_items`)
- `PUT /fees/items/{item_id}` → `Fee.Item.Edit`  (task: `BE-APIv4-032_fees_put_fees_items_item_id`)
- `DELETE /fees/items/{item_id}` → `Fee.Item.Delete`  (task: `BE-APIv4-033_fees_delete_fees_items_item_id`)
- `GET /fees/rates` → `Fee.Rate.Read`  (task: `BE-APIv4-034_fees_get_fees_rates`)
- `POST /fees/rates` → `Fee.Rate.Create`  (task: `BE-APIv4-035_fees_post_fees_rates`)
- `PUT /fees/rates/{id}` → `Fee.Rate.Edit`  (task: `BE-APIv4-036_fees_put_fees_rates_id`)
- `GET /bills` → `Bill.Read`  (task: `BE-APIv4-037_billing_get_bills`)
- `POST /bills/from-drafts` → `Bill.Create`  (task: `BE-APIv4-038_billing_post_bills_from-drafts`)
- `POST /bills/manual` → `Bill.Create`  (task: `BE-APIv4-039_billing_post_bills_manual`)
- `GET /bills/{id}` → `Bill.Read`  (task: `BE-APIv4-040_billing_get_bills_id`)
- `GET /bills/{id}/print` → `Bill.Print`  (task: `BE-APIv4-041_billing_get_bills_id_print`)
- `GET /payments` → `Payment.Read`  (task: `BE-APIv4-042_billing_get_payments`)
- `POST /payments` → `Payment.Create`  (task: `BE-APIv4-043_billing_post_payments`)
- `GET /payments/{id}` → `Payment.Read`  (task: `BE-APIv4-044_billing_get_payments_id`)
- `POST /offsets` → `Payment.Create`  (task: `BE-APIv4-045_billing_post_offsets`)
- `POST /offsets/{id}/reverse` → `Payment.Create`  (task: `BE-APIv4-046_billing_post_offsets_id_reverse`)
- `GET /cases/{case_id}/receipts` → `CaseReceipt.Read`  (task: `BE-APIv4-047_billing_get_cases_case_id_receipts`)

- `GET /admin/users` → `AdminUser.Read`  (task: `BE-APIX-01-01_admin_users_list`)
- `POST /admin/users` → `AdminUser.Create`  (task: `BE-APIX-01-02_admin_users_create`)
- `PUT /admin/users/{user_id}` → `AdminUser.Edit`  (task: `BE-APIX-01-03_admin_users_update`)
- `GET /system/params` → `SystemParam.Read`  (task: `BE-APIX-02-01_system_params_get`)
- `PUT /system/params/{param_key}` → `SystemParam.Edit`  (task: `BE-APIX-02-02_system_params_update`)
- `POST /templates` → `Template.Create`  (task: `BE-APIX-03-01_templates_upload`)
- `GET /templates` → `Template.Read`  (task: `BE-APIX-03-02_templates_list`)
- `POST /letterheads` → `LetterHead.Create`  (task: `BE-APIX-04-01_letterheads_create`)
- `GET /letterheads` → `LetterHead.Read`  (task: `BE-APIX-04-02_letterheads_list`)
- `GET /tasks/{id}/print` → `Task.Read`  (task: `BL-DOC-05_add_task_print_endpoint`)

## Post-enhancement Domain Matrix (Wave 02 Contract)

As of 2026-02-28, these routes are planned by post-enhancement task files and may not be wired yet.
Permission codes below are the runtime contract to keep `ROLE_PERMISSIONS` and API enforcement consistent.

### Annuity
- `GET /annuity/tasks` → `AnnuityTask.Read`  (task: `PE-BE-AN-02`)
- `PUT /annuity/tasks/{task_id}/instruction` → `AnnuityTask.Action`  (task: `PE-BE-AN-03`)
- `POST /annuity/tasks/generate-drafts` → `AnnuityTask.Action`  (task: `PE-BE-AN-05`)
- `GET /pay-lists` → `PayList.Read`  (task: `FRFE04-BE-02`)
- `GET /pay-lists/{id}` → `PayList.Read`  (next planned slice: `FRFE04-BE-03`)
- `POST /pay-lists/{id}/export` → `PayList.Export`  (task: `FRFE04-BE-RBAC-02`)
- `POST /pay-lists/from-fee-items` → `PayList.Create`  (task: `PE-BE-AN-06`)
- `POST /gov-payments` → `GovPayment.Create`  (task: `PE-BE-AN-07`)

### Collections (Dunning / Bad Debt)
- `POST /dunning` → `Dunning.Create`  (task: `PE-BE-CL-02`)
- `GET /dunning` → `Dunning.Read`  (task: `PE-BE-CL-03`)
- `POST /bills/{bill_id}/bad-debt` → `BadDebt.Action`  (task: `PE-BE-CL-04`)
- `POST /bills/{bill_id}/bad-debt/restore` → `BadDebt.Action`  (task: `PE-BE-CL-05`)

### Commission
- `POST /commission/rules` → `CommissionRule.Create`  (task: `PE-BE-COM-01`)
- `GET /commission/rules` → `CommissionRule.Read`  (task: `PE-BE-COM-02`)
- `PUT /commission/rules/{rule_id}` → `CommissionRule.Edit`  (task: `PE-BE-COM-03`)
- `GET /commission` → `Commission.Read`  (task: `PE-BE-COM-07`)
- `POST /commission/settlements` → `CommissionSettlement.Create`  (task: `PE-BE-COM-08`)
- `POST /commission/settlements/{id}/generate-lines` → `CommissionSettlement.Action`  (task: `PE-BE-COM-09`)
- `GET /commission/reports/settlement` → `CommissionReport.Read`  (task: `PE-BE-COM-10`)

### Consulting / Search / Expense
- `POST /consulting/cases` → `ConsultingCase.Create`  (task: `PE-BE-CS-01`)
- `POST /consulting/fee-drafts` → `ConsultingFeeDraft.Create`  (task: `PE-BE-CS-05`)
- `POST /expenses` → `Expense.Create`  (task: `PE-BE-CS-02`)
- `GET /expenses` → `Expense.Read`  (task: `PE-BE-CS-03`)
