# W0-CFG-MIGRATION-DECISION-01

## Story Shape Classification

- shared_file_density: low
- prereq_dependency_density: high
- be_fe_coupling: medium
- evidence_cost: low

## chosen_runbook

P0-prereq-heavy-story

## Exact Closure Slice

Decide whether the promoted W0 parameter-configuration cases require a database schema migration before backend, frontend, pytest, or Playwright implementation continues.

## Decision

No migration is required for `TC-W0-CFG-001` through `TC-W0-CFG-015` at this point.

The promoted cases can be represented with existing tables and columns:

- `t_system_param`: `param_key`, `param_value`, `value_type`, `description`, `is_secret`, `updated_at`
- `t_fee_rate`: `fee_code`, `fee_name`, `fee_type`, `currency`, `default_amount`, `enabled`, `rate_group`, `country_code`, `case_type`, `patent_category`, `calc_mode`, `calc_params`, `allow_reduction`, effective dates
- `t_commission_rule`: scope fields, `s1_rate`, `s2_rate`, fixed amounts, `wait_pay`, `force_settle`, effective dates
- `t_commission` and `t_case_agent_split`: generated commission rows and agent split ratios
- `t_task_template`: deadline base, day/month offsets, reminder offsets, daily reminder, default worker/supervisor fields
- `t_doc_template`: status effects, deadline template code, fee draft type, fee item JSON, input fields JSON, reply template linkage
- `t_template`: template group/language/file path metadata
- `t_letter_head`: locale, header/footer/address/contact fields, default marker
- `t_country`, `t_department`, `t_client`, `t_applicant`: referenced master data
- `t_role`, `t_role_perm`, `t_user_role`: RBAC seed/enforcement surface

Current gaps discovered by the cases are API/UI/seed/readiness gaps, not schema blockers:

- System parameter list API omits some metadata in the list response even though `t_system_param` already stores it.
- `bill_template_path`, fee rates, commission rules, templates, letterheads, countries, and departments are missing from the current seed-only database, but their tables exist.
- Template repository frontend routing/upload behavior is incomplete, but `t_template` already stores the required metadata.
- Letterhead frontend edit behavior is incomplete, but `t_letter_head` already stores the required fields.
- Fee `calc_mode` support is partial business logic behavior, not a schema absence.

## Explicit Non-Closure Statement

This task does not create or edit Alembic migrations, does not modify ORM models, does not modify backend/frontend product code, and does not implement handlers. If a future implementation task proves an unavoidable schema gap, that task must stop and create a separate DB task before changing schema.

## Remaining Follow-Up Task IDs

- `tasks/postenhancement/backend/W0-CFG-BE-SYSTEM-PARAM-METADATA-01.md`
- `tasks/postenhancement/backend/W0-CFG-BE-SEED-READINESS-01.md`
- `tasks/postenhancement/frontend/W0-CFG-FE-SYSTEM-PARAMS-01.md`
- `tasks/postenhancement/frontend/W0-CFG-FE-TEMPLATE-ROUTE-01.md`
- `tasks/automation/W0-CFG-PY-SYSTEM-PARAMS-01.md`
- `tasks/automation/W0-CFG-PY-FEE-RATES-01.md`
- `tasks/automation/W0-CFG-PY-COMMISSION-01.md`
- `tasks/automation/W0-CFG-PY-TEMPLATES-01.md`
- `tasks/automation/W0-CFG-PY-RBAC-SEED-UI-01.md`
- `tasks/automation/W0-CFG-PW-CONFIG-PAGES-01.md`
- `tasks/automation/W0-CFG-QA-CLOSE-01.md`

## Allowed Files

- `tasks/automation/W0-CFG-MIGRATION-DECISION-01.md`
- `artifacts/W0-CFG-MIGRATION-DECISION-01/**`

## Verification Commands

```bash
rg -n "class SystemParam|class FeeRate|class CommissionRule|class TaskTemplate|class DocTemplate|class Template|class LetterHead|class Country|class Department|class Applicant|class T_Role|__tablename__" backend/app/models backend/app/modules -S
rg -n "description|updated_at|bill_template_path|task_sheet_template_path|calc_mode|rate_group|s1_rate|s2_rate|wait_pay|force_settle|deadline_base|remind_1_offset_days|fee_item_list|input_fields|is_default" backend/app/modules backend/app/models -S
./scripts/task_validate.sh W0-CFG-MIGRATION-DECISION-01
```

## Evidence Path

- `artifacts/W0-CFG-MIGRATION-DECISION-01/results.jsonl`
- `artifacts/W0-CFG-MIGRATION-DECISION-01/summary.md`
- `artifacts/W0-CFG-MIGRATION-DECISION-01/git/diff.patch`
