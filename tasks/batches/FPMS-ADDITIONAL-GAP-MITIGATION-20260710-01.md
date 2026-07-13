# FPMS Additional GAP Mitigation Batch Manifest

Status: FROZEN / READY FOR EXECUTION
Program ID: `FPMS-ADDITIONAL-GAP-MITIGATION-20260710-01`
Goal: `019f4a1a-6f55-77a2-b558-b6555201415c`
Task count: 47

## Story Shape Classification and runbook

- `shared_file_density`: high
- `prereq_dependency_density`: high
- `be_fe_coupling`: high
- `evidence_cost`: high
- `chosen_runbook`: `P0-prereq-heavy-story`

The approved design and plan are:

- `docs/superpowers/specs/2026-07-10-fpms-additional-gap-mitigation-design.md`
- `docs/superpowers/plans/2026-07-10-fpms-additional-gap-mitigation.md`

## Execution rules

One row/section below is exactly one atomic task file and one executor. A task may edit only its exact allowlist. Before editing, capture dirty baseline evidence. Execute dependencies and recurring shared-file owners serially in the plan's frozen order. SQLite-writing tests run serially. Every implementation task follows RED → minimum GREEN → scoped checks → evidence → task gate. No product implementation begins before the Wave 0 contract-freeze task is PASS. No commit, push, PR, reset, clean, checkout, or overwrite of user changes is authorized.

Shared ownership serialization is authoritative in the approved plan; the exact source files in each item below are that task's ownership boundary. If execution reveals an unlisted shared prerequisite or a second closure slice, stop, update Story Shape Classification/runbook, and create a new task rather than stretching the current one.

## Atomic task entries

### 01 — `FPMS-ADDGAP-WIZARD-TEMPLATE-LIMIT-20260710-01`

- Task file: `tasks/additional_gaps/FPMS-ADDGAP-WIZARD-TEMPLATE-LIMIT-20260710-01.md`
- Wave: 1
- Owner role: Frontend Developer / worker
- Exact closure: DocumentWizard 请求启用模板时将 page_size 限制为 API 接受的最大值 100，消除真实页面路径上的确定性 422。
- Explicit non-closure: 不重做模板分页、搜索、缓存或其他 DocumentWizard 行为。
- Dependencies: Wave 0 planning gate
- Remaining follow-up task IDs: FPMS-ADDGAP-FINAL-REAL-PATH-E2E-20260710-01
- Shared ownership decision: only the source paths in the exact allowlist below; serialize any repeated path per approved plan.

Exact allowlist:

- `frontend/src/modules/documents/pages/DocumentWizard.vue`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/addgap-wizard-template-limit.spec.ts`
- `tasks/additional_gaps/FPMS-ADDGAP-WIZARD-TEMPLATE-LIMIT-20260710-01.md`
- `artifacts/FPMS-ADDGAP-WIZARD-TEMPLATE-LIMIT-20260710-01/**`

Runtime contracts:

- Permission: 沿用 DocTemplate.Read。
- Status codes/errors: GET 成功 200；本任务验证不再发送导致 422 的 page_size。
- Response envelope: 沿用现有模板列表响应包络。
- SQLite: N/A（前端只读请求）。
- Simplified Chinese UI: 触及页面，所有新增或变更可见文本必须为简体中文。

Required verification:

- RED/GREEN behavior: `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npx playwright test src/tests/addgap-wizard-template-limit.spec.ts --workers=1`
- Frontend checks: `cd frontend && npm run lint && npm run typecheck`
- Scope: `git diff --check -- frontend/src/modules/documents/pages/DocumentWizard.vue FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/addgap-wizard-template-limit.spec.ts`
- Evidence: initialize/finalize with `./scripts/evidence_run.sh FPMS-ADDGAP-WIZARD-TEMPLATE-LIMIT-20260710-01 <step> <command...>`, then run `./scripts/task_validate.sh FPMS-ADDGAP-WIZARD-TEMPLATE-LIMIT-20260710-01`.

Done definition: RED evidence exists where applicable; minimum implementation is GREEN; scoped lint/type/build/test and scope diff pass; required dirty-baseline and completion artifacts exist under `artifacts/FPMS-ADDGAP-WIZARD-TEMPLATE-LIMIT-20260710-01/`; `./scripts/task_validate.sh FPMS-ADDGAP-WIZARD-TEMPLATE-LIMIT-20260710-01` returns 0; exact closure is complete; explicit non-closure is respected. Otherwise status is FAIL or BLOCKED, never PASS.

### 02 — `FPMS-ADDGAP-DOCUMENT-CREATE-ATOMICITY-20260710-01`

- Task file: `tasks/additional_gaps/FPMS-ADDGAP-DOCUMENT-CREATE-ATOMICITY-20260710-01.md`
- Wave: 2
- Owner role: Backend Developer / worker
- Exact closure: 文档创建及其必需的任务/授权副作用在单一事务中全部提交或全部回滚。
- Explicit non-closure: 不改变副作用业务语义，不新增文档类型，不修复其他事务边界。
- Dependencies: Wave 0 planning gate
- Remaining follow-up task IDs: FPMS-ADDGAP-DOCUMENT-SEMANTICS-RESOLVER-20260710-01; FPMS-ADDGAP-DOCUMENT-DEADLINE-CREATE-API-20260710-01; FPMS-ADDGAP-GRANT-REPLACEMENT-SERVICE-20260710-01
- Shared ownership decision: only the source paths in the exact allowlist below; serialize any repeated path per approved plan.

Exact allowlist:

- `backend/app/modules/documents/service.py`
- `backend/app/modules/documents/api.py`
- `backend/tests/test_addgap_document_create_atomicity.py`
- `tasks/additional_gaps/FPMS-ADDGAP-DOCUMENT-CREATE-ATOMICITY-20260710-01.md`
- `artifacts/FPMS-ADDGAP-DOCUMENT-CREATE-ATOMICITY-20260710-01/**`

Runtime contracts:

- Permission: 沿用 Doc.Create，必须以函数参数 Depends 注入。
- Status codes/errors: 成功沿用 POST 201；业务/配置冲突 409 时不得残留文档或副作用。
- Response envelope: 沿用 DocumentOut 响应包络。
- SQLite: 短事务；不依赖 RETURNING；flush 后取主键。
- Simplified Chinese UI: N/A（不得引入 UI 文本）。

Required verification:

- RED/GREEN behavior: `cd backend && .venv/bin/pytest -q tests/test_addgap_document_create_atomicity.py`
- Scoped Ruff: `cd backend && .venv/bin/ruff check --fix app/modules/documents/service.py app/modules/documents/api.py tests/test_addgap_document_create_atomicity.py && .venv/bin/ruff format app/modules/documents/service.py app/modules/documents/api.py tests/test_addgap_document_create_atomicity.py && .venv/bin/ruff check app/modules/documents/service.py app/modules/documents/api.py tests/test_addgap_document_create_atomicity.py`
- Scope: `git diff --check -- backend/app/modules/documents/service.py backend/app/modules/documents/api.py backend/tests/test_addgap_document_create_atomicity.py`
- Evidence: initialize/finalize with `./scripts/evidence_run.sh FPMS-ADDGAP-DOCUMENT-CREATE-ATOMICITY-20260710-01 <step> <command...>`, then run `./scripts/task_validate.sh FPMS-ADDGAP-DOCUMENT-CREATE-ATOMICITY-20260710-01`.

Done definition: RED evidence exists where applicable; minimum implementation is GREEN; scoped lint/type/build/test and scope diff pass; required dirty-baseline and completion artifacts exist under `artifacts/FPMS-ADDGAP-DOCUMENT-CREATE-ATOMICITY-20260710-01/`; `./scripts/task_validate.sh FPMS-ADDGAP-DOCUMENT-CREATE-ATOMICITY-20260710-01` returns 0; exact closure is complete; explicit non-closure is respected. Otherwise status is FAIL or BLOCKED, never PASS.

### 03 — `FPMS-ADDGAP-DOCUMENT-SEMANTICS-RESOLVER-20260710-01`

- Task file: `tasks/additional_gaps/FPMS-ADDGAP-DOCUMENT-SEMANTICS-RESOLVER-20260710-01.md`
- Wave: 2
- Owner role: Backend Developer / worker
- Exact closure: 新增唯一 ResolvedDocumentSemantics resolver，并对缺失、冲突或畸形的执行元数据 fail-closed。
- Explicit non-closure: 不根据模板名称推断执行语义，不激活任何目录项，不改变持久化模型。
- Dependencies: 02
- Remaining follow-up task IDs: 04, 10, 13, 18–22, 27, 33–39
- Shared ownership decision: only the source paths in the exact allowlist below; serialize any repeated path per approved plan.

Exact allowlist:

- `backend/app/modules/documents/semantics.py`
- `backend/tests/test_addgap_document_semantics.py`
- `tasks/additional_gaps/FPMS-ADDGAP-DOCUMENT-SEMANTICS-RESOLVER-20260710-01.md`
- `artifacts/FPMS-ADDGAP-DOCUMENT-SEMANTICS-RESOLVER-20260710-01/**`

Runtime contracts:

- Permission: N/A（纯服务组件）。
- Status codes/errors: resolver 以领域异常表达 400/409 语义，具体 API 映射由消费者保持。
- Response envelope: N/A（纯内部值对象）。
- SQLite: N/A。
- Simplified Chinese UI: N/A。

Required verification:

- RED/GREEN behavior: `cd backend && .venv/bin/pytest -q tests/test_addgap_document_semantics.py`
- Scoped Ruff: `cd backend && .venv/bin/ruff check --fix app/modules/documents/semantics.py tests/test_addgap_document_semantics.py && .venv/bin/ruff format app/modules/documents/semantics.py tests/test_addgap_document_semantics.py && .venv/bin/ruff check app/modules/documents/semantics.py tests/test_addgap_document_semantics.py`
- Scope: `git diff --check -- backend/app/modules/documents/semantics.py backend/tests/test_addgap_document_semantics.py`
- Evidence: initialize/finalize with `./scripts/evidence_run.sh FPMS-ADDGAP-DOCUMENT-SEMANTICS-RESOLVER-20260710-01 <step> <command...>`, then run `./scripts/task_validate.sh FPMS-ADDGAP-DOCUMENT-SEMANTICS-RESOLVER-20260710-01`.

Done definition: RED evidence exists where applicable; minimum implementation is GREEN; scoped lint/type/build/test and scope diff pass; required dirty-baseline and completion artifacts exist under `artifacts/FPMS-ADDGAP-DOCUMENT-SEMANTICS-RESOLVER-20260710-01/`; `./scripts/task_validate.sh FPMS-ADDGAP-DOCUMENT-SEMANTICS-RESOLVER-20260710-01` returns 0; exact closure is complete; explicit non-closure is respected. Otherwise status is FAIL or BLOCKED, never PASS.

### 04 — `FPMS-ADDGAP-DOCUMENT-SEMANTIC-STATE-EFFECT-20260710-01`

- Task file: `tasks/additional_gaps/FPMS-ADDGAP-DOCUMENT-SEMANTIC-STATE-EFFECT-20260710-01.md`
- Wave: 2
- Owner role: Backend Developer / worker
- Exact closure: 文档 need-reply 与案件状态副作用只消费 resolver 输出，不直接读取原始字段或模板名称。
- Explicit non-closure: 不改变目录激活范围，不实现 OA 收据闭环，不修改任务期限规则。
- Dependencies: 03
- Remaining follow-up task IDs: 13, 17, 27, 33, 36
- Shared ownership decision: only the source paths in the exact allowlist below; serialize any repeated path per approved plan.

Exact allowlist:

- `backend/app/modules/documents/service.py`
- `backend/tests/test_addgap_document_semantic_state_effect.py`
- `tasks/additional_gaps/FPMS-ADDGAP-DOCUMENT-SEMANTIC-STATE-EFFECT-20260710-01.md`
- `artifacts/FPMS-ADDGAP-DOCUMENT-SEMANTIC-STATE-EFFECT-20260710-01/**`

Runtime contracts:

- Permission: 沿用调用方权限。
- Status codes/errors: 冲突语义 fail-closed 为 409；成功状态码保持调用端既有合同。
- Response envelope: 沿用调用端既有包络。
- SQLite: 保持 SQLite 兼容查询和短事务。
- Simplified Chinese UI: N/A。

Required verification:

- RED/GREEN behavior: `cd backend && .venv/bin/pytest -q tests/test_addgap_document_semantic_state_effect.py`
- Scoped Ruff: `cd backend && .venv/bin/ruff check --fix app/modules/documents/service.py tests/test_addgap_document_semantic_state_effect.py && .venv/bin/ruff format app/modules/documents/service.py tests/test_addgap_document_semantic_state_effect.py && .venv/bin/ruff check app/modules/documents/service.py tests/test_addgap_document_semantic_state_effect.py`
- Scope: `git diff --check -- backend/app/modules/documents/service.py backend/tests/test_addgap_document_semantic_state_effect.py`
- Evidence: initialize/finalize with `./scripts/evidence_run.sh FPMS-ADDGAP-DOCUMENT-SEMANTIC-STATE-EFFECT-20260710-01 <step> <command...>`, then run `./scripts/task_validate.sh FPMS-ADDGAP-DOCUMENT-SEMANTIC-STATE-EFFECT-20260710-01`.

Done definition: RED evidence exists where applicable; minimum implementation is GREEN; scoped lint/type/build/test and scope diff pass; required dirty-baseline and completion artifacts exist under `artifacts/FPMS-ADDGAP-DOCUMENT-SEMANTIC-STATE-EFFECT-20260710-01/`; `./scripts/task_validate.sh FPMS-ADDGAP-DOCUMENT-SEMANTIC-STATE-EFFECT-20260710-01` returns 0; exact closure is complete; explicit non-closure is respected. Otherwise status is FAIL or BLOCKED, never PASS.

### 05 — `FPMS-ADDGAP-WORKPKG-RESOLVE-KEY-SCHEMA-20260710-01`

- Task file: `tasks/additional_gaps/FPMS-ADDGAP-WORKPKG-RESOLVE-KEY-SCHEMA-20260710-01.md`
- Wave: 2
- Owner role: Backend Developer / worker
- Exact closure: Phase 0-EXT 增加并回填 OfficialWorkPackage.resolve_key，重复预检通过后建立唯一约束。
- Explicit non-closure: 不修改用户现有 migration，不创建 work package 服务/API/UI，不更改其他表。
- Dependencies: Wave 0；执行前重新确认当前 Alembic head
- Remaining follow-up task IDs: 06, 10, 14, 35
- Shared ownership decision: only the source paths in the exact allowlist below; serialize any repeated path per approved plan.

Exact allowlist:

- `backend/alembic/versions/addgap_workpkg_resolve_key.py`
- `backend/app/modules/official_workflows/models.py`
- `backend/tests/test_addgap_workpkg_resolve_key_schema.py`
- `tasks/additional_gaps/FPMS-ADDGAP-WORKPKG-RESOLVE-KEY-SCHEMA-20260710-01.md`
- `artifacts/FPMS-ADDGAP-WORKPKG-RESOLVE-KEY-SCHEMA-20260710-01/**`

Runtime contracts:

- Permission: N/A（schema）。
- Status codes/errors: N/A；migration 重复数据必须 fail-closed 并给出明确错误。
- Response envelope: N/A。
- SQLite: Integer/FK 对齐、CURRENT_TIMESTAMP、无 PG-only SQL；clean SQLite upgrade head。
- Simplified Chinese UI: N/A。

Required verification:

- RED/GREEN behavior: `cd backend && .venv/bin/pytest -q tests/test_addgap_workpkg_resolve_key_schema.py`
- Scoped Ruff: `cd backend && .venv/bin/ruff check --fix alembic/versions/addgap_workpkg_resolve_key.py app/modules/official_workflows/models.py tests/test_addgap_workpkg_resolve_key_schema.py && .venv/bin/ruff format alembic/versions/addgap_workpkg_resolve_key.py app/modules/official_workflows/models.py tests/test_addgap_workpkg_resolve_key_schema.py && .venv/bin/ruff check alembic/versions/addgap_workpkg_resolve_key.py app/modules/official_workflows/models.py tests/test_addgap_workpkg_resolve_key_schema.py`
- Migration gate: `cd backend && PYTHONPATH=. .venv/bin/alembic heads && PYTHONPATH=. .venv/bin/alembic upgrade head` on a clean temporary SQLite database.
- Scope: `git diff --check -- backend/alembic/versions/addgap_workpkg_resolve_key.py backend/app/modules/official_workflows/models.py backend/tests/test_addgap_workpkg_resolve_key_schema.py`
- Evidence: initialize/finalize with `./scripts/evidence_run.sh FPMS-ADDGAP-WORKPKG-RESOLVE-KEY-SCHEMA-20260710-01 <step> <command...>`, then run `./scripts/task_validate.sh FPMS-ADDGAP-WORKPKG-RESOLVE-KEY-SCHEMA-20260710-01`.

Done definition: RED evidence exists where applicable; minimum implementation is GREEN; scoped lint/type/build/test and scope diff pass; required dirty-baseline and completion artifacts exist under `artifacts/FPMS-ADDGAP-WORKPKG-RESOLVE-KEY-SCHEMA-20260710-01/`; `./scripts/task_validate.sh FPMS-ADDGAP-WORKPKG-RESOLVE-KEY-SCHEMA-20260710-01` returns 0; exact closure is complete; explicit non-closure is respected. Otherwise status is FAIL or BLOCKED, never PASS.

### 06 — `FPMS-ADDGAP-FILING-ENSURE-SERVICE-20260710-01`

- Task file: `tasks/additional_gaps/FPMS-ADDGAP-FILING-ENSURE-SERVICE-20260710-01.md`
- Wave: 2
- Owner role: Backend Developer / worker
- Exact closure: 按案件 resolve/create 一个初始化 filing package：先复用，仅 NOT_FILED 可新建，唯一键竞争后重读胜者。
- Explicit non-closure: 不新增 API 或页面入口，不创建 OA package，不更改 filing checklist 业务项。
- Dependencies: 05
- Remaining follow-up task IDs: 07
- Shared ownership decision: only the source paths in the exact allowlist below; serialize any repeated path per approved plan.

Exact allowlist:

- `backend/app/modules/official_workflows/service.py`
- `backend/tests/test_addgap_filing_ensure_service.py`
- `tasks/additional_gaps/FPMS-ADDGAP-FILING-ENSURE-SERVICE-20260710-01.md`
- `artifacts/FPMS-ADDGAP-FILING-ENSURE-SERVICE-20260710-01/**`

Runtime contracts:

- Permission: N/A（服务由 API 注入 OfficialWorkflow.Update）。
- Status codes/errors: 缺资源 404、状态不允许/身份冲突 409；成功返回既有 package。
- Response envelope: 返回既有 filing package schema 所需实体。
- SQLite: 依赖 DB 唯一键处理竞争；短事务，不依赖 RETURNING。
- Simplified Chinese UI: N/A。

Required verification:

- RED/GREEN behavior: `cd backend && .venv/bin/pytest -q tests/test_addgap_filing_ensure_service.py`
- Scoped Ruff: `cd backend && .venv/bin/ruff check --fix app/modules/official_workflows/service.py tests/test_addgap_filing_ensure_service.py && .venv/bin/ruff format app/modules/official_workflows/service.py tests/test_addgap_filing_ensure_service.py && .venv/bin/ruff check app/modules/official_workflows/service.py tests/test_addgap_filing_ensure_service.py`
- Scope: `git diff --check -- backend/app/modules/official_workflows/service.py backend/tests/test_addgap_filing_ensure_service.py`
- Evidence: initialize/finalize with `./scripts/evidence_run.sh FPMS-ADDGAP-FILING-ENSURE-SERVICE-20260710-01 <step> <command...>`, then run `./scripts/task_validate.sh FPMS-ADDGAP-FILING-ENSURE-SERVICE-20260710-01`.

Done definition: RED evidence exists where applicable; minimum implementation is GREEN; scoped lint/type/build/test and scope diff pass; required dirty-baseline and completion artifacts exist under `artifacts/FPMS-ADDGAP-FILING-ENSURE-SERVICE-20260710-01/`; `./scripts/task_validate.sh FPMS-ADDGAP-FILING-ENSURE-SERVICE-20260710-01` returns 0; exact closure is complete; explicit non-closure is respected. Otherwise status is FAIL or BLOCKED, never PASS.

### 07 — `FPMS-ADDGAP-FILING-RESOLVE-API-20260710-01`

- Task file: `tasks/additional_gaps/FPMS-ADDGAP-FILING-RESOLVE-API-20260710-01.md`
- Wave: 2
- Owner role: Backend Developer / worker
- Exact closure: 新增无 body 的 filing resolve POST，返回 existing-or-created package 的既有响应包络。
- Explicit non-closure: 不修改 service 规则，不新增 GET body，不增加路由重复 wiring。
- Dependencies: 06
- Remaining follow-up task IDs: 08
- Shared ownership decision: only the source paths in the exact allowlist below; serialize any repeated path per approved plan.

Exact allowlist:

- `backend/app/modules/official_workflows/api.py`
- `backend/app/modules/official_workflows/schemas.py`
- `backend/tests/test_addgap_filing_resolve_api.py`
- `tasks/additional_gaps/FPMS-ADDGAP-FILING-RESOLVE-API-20260710-01.md`
- `artifacts/FPMS-ADDGAP-FILING-RESOLVE-API-20260710-01/**`

Runtime contracts:

- Permission: OfficialWorkflow.Update，必须作为函数参数 Depends 注入。
- Status codes/errors: POST 200；404 案件不存在；409 状态/身份冲突；422 路径校验。
- Response envelope: 沿用 filing package 输出模型，不发明新 envelope。
- SQLite: N/A（调用 SQLite-safe service）。
- Simplified Chinese UI: N/A。

Required verification:

- RED/GREEN behavior: `cd backend && .venv/bin/pytest -q tests/test_addgap_filing_resolve_api.py`
- Scoped Ruff: `cd backend && .venv/bin/ruff check --fix app/modules/official_workflows/api.py app/modules/official_workflows/schemas.py tests/test_addgap_filing_resolve_api.py && .venv/bin/ruff format app/modules/official_workflows/api.py app/modules/official_workflows/schemas.py tests/test_addgap_filing_resolve_api.py && .venv/bin/ruff check app/modules/official_workflows/api.py app/modules/official_workflows/schemas.py tests/test_addgap_filing_resolve_api.py`
- Scope: `git diff --check -- backend/app/modules/official_workflows/api.py backend/app/modules/official_workflows/schemas.py backend/tests/test_addgap_filing_resolve_api.py`
- Evidence: initialize/finalize with `./scripts/evidence_run.sh FPMS-ADDGAP-FILING-RESOLVE-API-20260710-01 <step> <command...>`, then run `./scripts/task_validate.sh FPMS-ADDGAP-FILING-RESOLVE-API-20260710-01`.

Done definition: RED evidence exists where applicable; minimum implementation is GREEN; scoped lint/type/build/test and scope diff pass; required dirty-baseline and completion artifacts exist under `artifacts/FPMS-ADDGAP-FILING-RESOLVE-API-20260710-01/`; `./scripts/task_validate.sh FPMS-ADDGAP-FILING-RESOLVE-API-20260710-01` returns 0; exact closure is complete; explicit non-closure is respected. Otherwise status is FAIL or BLOCKED, never PASS.

### 08 — `FPMS-ADDGAP-FILING-PAGE-RESOLVE-20260710-01`

- Task file: `tasks/additional_gaps/FPMS-ADDGAP-FILING-PAGE-RESOLVE-20260710-01.md`
- Wave: 2
- Owner role: Frontend Developer / worker
- Exact closure: FilingPreparation 接收 case_id，调用 resolve API 获得 package_id，并以 replace 更新路由。
- Explicit non-closure: 不增加 CaseDetail 入口，不改 filing 业务表单，不重做前端 API 模块。
- Dependencies: 07
- Remaining follow-up task IDs: 09
- Shared ownership decision: only the source paths in the exact allowlist below; serialize any repeated path per approved plan.

Exact allowlist:

- `frontend/src/api/officialWorkflows.ts`
- `frontend/src/api/officialWorkflows.types.ts`
- `frontend/src/modules/cases/pages/FilingPreparation.vue`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/addgap-filing-page-resolve.spec.ts`
- `tasks/additional_gaps/FPMS-ADDGAP-FILING-PAGE-RESOLVE-20260710-01.md`
- `artifacts/FPMS-ADDGAP-FILING-PAGE-RESOLVE-20260710-01/**`

Runtime contracts:

- Permission: 消费 OfficialWorkflow.Update。
- Status codes/errors: 消费 POST 200；对 404/409/422 使用简体中文错误反馈。
- Response envelope: 消费既有 filing package 输出。
- SQLite: N/A。
- Simplified Chinese UI: 所有新增/触及的可见文本必须为简体中文。

Required verification:

- RED/GREEN behavior: `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npx playwright test src/tests/addgap-filing-page-resolve.spec.ts --workers=1`
- Frontend checks: `cd frontend && npm run lint && npm run typecheck`
- Scope: `git diff --check -- frontend/src/api/officialWorkflows.ts frontend/src/api/officialWorkflows.types.ts frontend/src/modules/cases/pages/FilingPreparation.vue FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/addgap-filing-page-resolve.spec.ts`
- Evidence: initialize/finalize with `./scripts/evidence_run.sh FPMS-ADDGAP-FILING-PAGE-RESOLVE-20260710-01 <step> <command...>`, then run `./scripts/task_validate.sh FPMS-ADDGAP-FILING-PAGE-RESOLVE-20260710-01`.

Done definition: RED evidence exists where applicable; minimum implementation is GREEN; scoped lint/type/build/test and scope diff pass; required dirty-baseline and completion artifacts exist under `artifacts/FPMS-ADDGAP-FILING-PAGE-RESOLVE-20260710-01/`; `./scripts/task_validate.sh FPMS-ADDGAP-FILING-PAGE-RESOLVE-20260710-01` returns 0; exact closure is complete; explicit non-closure is respected. Otherwise status is FAIL or BLOCKED, never PASS.

### 09 — `FPMS-ADDGAP-FILING-CASE-ENTRY-20260710-01`

- Task file: `tasks/additional_gaps/FPMS-ADDGAP-FILING-CASE-ENTRY-20260710-01.md`
- Wave: 2
- Owner role: Frontend Developer / worker
- Exact closure: CaseDetail 显示简体中文“申请前准备”动作，并携带当前 case_id 进入 filing 页面。
- Explicit non-closure: 不改 FilingPreparation 内部逻辑，不新增权限模型，不增加其他案件动作。
- Dependencies: 08
- Remaining follow-up task IDs: 46
- Shared ownership decision: only the source paths in the exact allowlist below; serialize any repeated path per approved plan.

Exact allowlist:

- `frontend/src/modules/cases/pages/CaseDetail.vue`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/addgap-filing-case-entry.spec.ts`
- `tasks/additional_gaps/FPMS-ADDGAP-FILING-CASE-ENTRY-20260710-01.md`
- `artifacts/FPMS-ADDGAP-FILING-CASE-ENTRY-20260710-01/**`

Runtime contracts:

- Permission: 沿用页面既有权限可见性；不得绕过后端 OfficialWorkflow.Update。
- Status codes/errors: N/A（导航）；目标页 API 状态由 Task 08 处理。
- Response envelope: N/A。
- SQLite: N/A。
- Simplified Chinese UI: 动作、错误和辅助文本必须为简体中文。

Required verification:

- RED/GREEN behavior: `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npx playwright test src/tests/addgap-filing-case-entry.spec.ts --workers=1`
- Frontend checks: `cd frontend && npm run lint && npm run typecheck`
- Scope: `git diff --check -- frontend/src/modules/cases/pages/CaseDetail.vue FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/addgap-filing-case-entry.spec.ts`
- Evidence: initialize/finalize with `./scripts/evidence_run.sh FPMS-ADDGAP-FILING-CASE-ENTRY-20260710-01 <step> <command...>`, then run `./scripts/task_validate.sh FPMS-ADDGAP-FILING-CASE-ENTRY-20260710-01`.

Done definition: RED evidence exists where applicable; minimum implementation is GREEN; scoped lint/type/build/test and scope diff pass; required dirty-baseline and completion artifacts exist under `artifacts/FPMS-ADDGAP-FILING-CASE-ENTRY-20260710-01/`; `./scripts/task_validate.sh FPMS-ADDGAP-FILING-CASE-ENTRY-20260710-01` returns 0; exact closure is complete; explicit non-closure is respected. Otherwise status is FAIL or BLOCKED, never PASS.

### 10 — `FPMS-ADDGAP-OA-ENSURE-SERVICE-20260710-01`

- Task file: `tasks/additional_gaps/FPMS-ADDGAP-OA-ENSURE-SERVICE-20260710-01.md`
- Wave: 2
- Owner role: Backend Developer / worker
- Exact closure: 每个可执行 IN 源文档 resolve/create 唯一 OA package，创建状态必须与 resolver 的 OA1/OA2 匹配。
- Explicit non-closure: 不新增 API/UI，不处理收据，不完成 OA 任务。
- Dependencies: 03, 05
- Remaining follow-up task IDs: 11, 17
- Shared ownership decision: only the source paths in the exact allowlist below; serialize any repeated path per approved plan.

Exact allowlist:

- `backend/app/modules/official_workflows/service.py`
- `backend/tests/test_addgap_oa_ensure_service.py`
- `tasks/additional_gaps/FPMS-ADDGAP-OA-ENSURE-SERVICE-20260710-01.md`
- `artifacts/FPMS-ADDGAP-OA-ENSURE-SERVICE-20260710-01/**`

Runtime contracts:

- Permission: N/A（服务由 API 注入 OfficialWorkflow.Update）。
- Status codes/errors: 404 文档不存在；400 方向错误；409 状态/语义/身份冲突。
- Response envelope: 返回 OaReplyPackageOut 所需实体。
- SQLite: 使用 resolve_key 唯一性；竞争后重读；短事务。
- Simplified Chinese UI: N/A。

Required verification:

- RED/GREEN behavior: `cd backend && .venv/bin/pytest -q tests/test_addgap_oa_ensure_service.py`
- Scoped Ruff: `cd backend && .venv/bin/ruff check --fix app/modules/official_workflows/service.py tests/test_addgap_oa_ensure_service.py && .venv/bin/ruff format app/modules/official_workflows/service.py tests/test_addgap_oa_ensure_service.py && .venv/bin/ruff check app/modules/official_workflows/service.py tests/test_addgap_oa_ensure_service.py`
- Scope: `git diff --check -- backend/app/modules/official_workflows/service.py backend/tests/test_addgap_oa_ensure_service.py`
- Evidence: initialize/finalize with `./scripts/evidence_run.sh FPMS-ADDGAP-OA-ENSURE-SERVICE-20260710-01 <step> <command...>`, then run `./scripts/task_validate.sh FPMS-ADDGAP-OA-ENSURE-SERVICE-20260710-01`.

Done definition: RED evidence exists where applicable; minimum implementation is GREEN; scoped lint/type/build/test and scope diff pass; required dirty-baseline and completion artifacts exist under `artifacts/FPMS-ADDGAP-OA-ENSURE-SERVICE-20260710-01/`; `./scripts/task_validate.sh FPMS-ADDGAP-OA-ENSURE-SERVICE-20260710-01` returns 0; exact closure is complete; explicit non-closure is respected. Otherwise status is FAIL or BLOCKED, never PASS.

### 11 — `FPMS-ADDGAP-OA-RESOLVE-API-20260710-01`

- Task file: `tasks/additional_gaps/FPMS-ADDGAP-OA-RESOLVE-API-20260710-01.md`
- Wave: 2
- Owner role: Backend Developer / worker
- Exact closure: 新增无 body 的 OA resolve POST，返回 OaReplyPackageOut。
- Explicit non-closure: 不更改 OA ensure 规则、不新增 GET body、不重接 router。
- Dependencies: 10
- Remaining follow-up task IDs: 12
- Shared ownership decision: only the source paths in the exact allowlist below; serialize any repeated path per approved plan.

Exact allowlist:

- `backend/app/modules/official_workflows/api.py`
- `backend/app/modules/official_workflows/schemas.py`
- `backend/tests/test_addgap_oa_resolve_api.py`
- `tasks/additional_gaps/FPMS-ADDGAP-OA-RESOLVE-API-20260710-01.md`
- `artifacts/FPMS-ADDGAP-OA-RESOLVE-API-20260710-01/**`

Runtime contracts:

- Permission: OfficialWorkflow.Update，函数参数 Depends 注入。
- Status codes/errors: POST 200；404 资源；400 方向；409 状态/语义/身份；422 路径。
- Response envelope: 既有 OaReplyPackageOut，不发明 envelope。
- SQLite: N/A。
- Simplified Chinese UI: N/A。

Required verification:

- RED/GREEN behavior: `cd backend && .venv/bin/pytest -q tests/test_addgap_oa_resolve_api.py`
- Scoped Ruff: `cd backend && .venv/bin/ruff check --fix app/modules/official_workflows/api.py app/modules/official_workflows/schemas.py tests/test_addgap_oa_resolve_api.py && .venv/bin/ruff format app/modules/official_workflows/api.py app/modules/official_workflows/schemas.py tests/test_addgap_oa_resolve_api.py && .venv/bin/ruff check app/modules/official_workflows/api.py app/modules/official_workflows/schemas.py tests/test_addgap_oa_resolve_api.py`
- Scope: `git diff --check -- backend/app/modules/official_workflows/api.py backend/app/modules/official_workflows/schemas.py backend/tests/test_addgap_oa_resolve_api.py`
- Evidence: initialize/finalize with `./scripts/evidence_run.sh FPMS-ADDGAP-OA-RESOLVE-API-20260710-01 <step> <command...>`, then run `./scripts/task_validate.sh FPMS-ADDGAP-OA-RESOLVE-API-20260710-01`.

Done definition: RED evidence exists where applicable; minimum implementation is GREEN; scoped lint/type/build/test and scope diff pass; required dirty-baseline and completion artifacts exist under `artifacts/FPMS-ADDGAP-OA-RESOLVE-API-20260710-01/`; `./scripts/task_validate.sh FPMS-ADDGAP-OA-RESOLVE-API-20260710-01` returns 0; exact closure is complete; explicit non-closure is respected. Otherwise status is FAIL or BLOCKED, never PASS.

### 12 — `FPMS-ADDGAP-OA-PAGE-RESOLVE-20260710-01`

- Task file: `tasks/additional_gaps/FPMS-ADDGAP-OA-PAGE-RESOLVE-20260710-01.md`
- Wave: 2
- Owner role: Frontend Developer / worker
- Exact closure: OAReplyPackage 从 DocumentDetail 的 document_id 上下文调用 resolve，并替换为 package_id 路由。
- Explicit non-closure: 不改变 OA reply checklist/上传业务，不新增文档详情入口。
- Dependencies: 11；与 08 串行编辑 shared frontend API
- Remaining follow-up task IDs: 46
- Shared ownership decision: only the source paths in the exact allowlist below; serialize any repeated path per approved plan.

Exact allowlist:

- `frontend/src/api/officialWorkflows.ts`
- `frontend/src/api/officialWorkflows.types.ts`
- `frontend/src/modules/documents/pages/OAReplyPackage.vue`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/addgap-oa-page-resolve.spec.ts`
- `tasks/additional_gaps/FPMS-ADDGAP-OA-PAGE-RESOLVE-20260710-01.md`
- `artifacts/FPMS-ADDGAP-OA-PAGE-RESOLVE-20260710-01/**`

Runtime contracts:

- Permission: 消费 OfficialWorkflow.Update。
- Status codes/errors: 消费 POST 200；404/400/409/422 显示简体中文反馈。
- Response envelope: 消费 OaReplyPackageOut。
- SQLite: N/A。
- Simplified Chinese UI: 所有新增/触及可见文本必须为简体中文。

Required verification:

- RED/GREEN behavior: `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npx playwright test src/tests/addgap-oa-page-resolve.spec.ts --workers=1`
- Frontend checks: `cd frontend && npm run lint && npm run typecheck`
- Scope: `git diff --check -- frontend/src/api/officialWorkflows.ts frontend/src/api/officialWorkflows.types.ts frontend/src/modules/documents/pages/OAReplyPackage.vue FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/addgap-oa-page-resolve.spec.ts`
- Evidence: initialize/finalize with `./scripts/evidence_run.sh FPMS-ADDGAP-OA-PAGE-RESOLVE-20260710-01 <step> <command...>`, then run `./scripts/task_validate.sh FPMS-ADDGAP-OA-PAGE-RESOLVE-20260710-01`.

Done definition: RED evidence exists where applicable; minimum implementation is GREEN; scoped lint/type/build/test and scope diff pass; required dirty-baseline and completion artifacts exist under `artifacts/FPMS-ADDGAP-OA-PAGE-RESOLVE-20260710-01/`; `./scripts/task_validate.sh FPMS-ADDGAP-OA-PAGE-RESOLVE-20260710-01` returns 0; exact closure is complete; explicit non-closure is respected. Otherwise status is FAIL or BLOCKED, never PASS.

### 13 — `FPMS-ADDGAP-OA-OUT-KEEPS-TASK-OPEN-20260710-01`

- Task file: `tasks/additional_gaps/FPMS-ADDGAP-OA-OUT-KEEPS-TASK-OPEN-20260710-01.md`
- Wave: 3
- Owner role: Backend Developer / worker
- Exact closure: OA_OUT 仅记录内部答复日期，不改变 OA task 或 case state；普通非 OA reply 行为保持原范围。
- Explicit non-closure: 不校验收据、不 archive package、不关闭任务、不恢复 SUB_EXAM。
- Dependencies: 03, 04
- Remaining follow-up task IDs: 17
- Shared ownership decision: only the source paths in the exact allowlist below; serialize any repeated path per approved plan.

Exact allowlist:

- `backend/app/modules/documents/service.py`
- `backend/tests/test_addgap_oa_out_keeps_task_open.py`
- `backend/tests/test_b2_reply_chain.py`
- `backend/tests/test_spec_alignment_e2e.py`
- `tasks/additional_gaps/FPMS-ADDGAP-OA-OUT-KEEPS-TASK-OPEN-20260710-01.md`
- `artifacts/FPMS-ADDGAP-OA-OUT-KEEPS-TASK-OPEN-20260710-01/**`

Runtime contracts:

- Permission: 沿用 Doc.Create。
- Status codes/errors: 成功创建状态保持 201；语义冲突 409；不得产生提前 close。
- Response envelope: 沿用 DocumentOut。
- SQLite: 单事务内保持短写入。
- Simplified Chinese UI: N/A。

Required verification:

- RED/GREEN behavior: `cd backend && .venv/bin/pytest -q tests/test_addgap_oa_out_keeps_task_open.py`
- Legacy regression behavior: `cd backend && .venv/bin/pytest -q tests/test_b2_reply_chain.py tests/test_spec_alignment_e2e.py`
- Scoped Ruff: `cd backend && .venv/bin/ruff check --fix app/modules/documents/service.py tests/test_addgap_oa_out_keeps_task_open.py tests/test_b2_reply_chain.py tests/test_spec_alignment_e2e.py && .venv/bin/ruff format app/modules/documents/service.py tests/test_addgap_oa_out_keeps_task_open.py tests/test_b2_reply_chain.py tests/test_spec_alignment_e2e.py && .venv/bin/ruff check app/modules/documents/service.py tests/test_addgap_oa_out_keeps_task_open.py tests/test_b2_reply_chain.py tests/test_spec_alignment_e2e.py`
- Scope: `git diff --check -- backend/app/modules/documents/service.py backend/tests/test_addgap_oa_out_keeps_task_open.py backend/tests/test_b2_reply_chain.py backend/tests/test_spec_alignment_e2e.py`
- Evidence: initialize/finalize with `./scripts/evidence_run.sh FPMS-ADDGAP-OA-OUT-KEEPS-TASK-OPEN-20260710-01 <step> <command...>`, then run `./scripts/task_validate.sh FPMS-ADDGAP-OA-OUT-KEEPS-TASK-OPEN-20260710-01`.

Done definition: RED evidence exists where applicable; minimum implementation is GREEN; scoped lint/type/build/test and scope diff pass; required dirty-baseline and completion artifacts exist under `artifacts/FPMS-ADDGAP-OA-OUT-KEEPS-TASK-OPEN-20260710-01/`; `./scripts/task_validate.sh FPMS-ADDGAP-OA-OUT-KEEPS-TASK-OPEN-20260710-01` returns 0; exact closure is complete; explicit non-closure is respected. Otherwise status is FAIL or BLOCKED, never PASS.

### 14 — `FPMS-ADDGAP-RECEIPT-SAME-CASE-GATE-20260710-01`

- Task file: `tasks/additional_gaps/FPMS-ADDGAP-RECEIPT-SAME-CASE-GATE-20260710-01.md`
- Wave: 3
- Owner role: Backend Developer / worker
- Exact closure: 任何收据附件写入前，附件文档 case_id 必须等于 package case_id。
- Explicit non-closure: 不判断 OA 来源归属，不扫描历史数据，不 archive package。
- Dependencies: 05
- Remaining follow-up task IDs: 15, 16, 17
- Shared ownership decision: only the source paths in the exact allowlist below; serialize any repeated path per approved plan.

Exact allowlist:

- `backend/app/modules/official_workflows/service.py`
- `backend/tests/test_addgap_receipt_same_case_gate.py`
- `tasks/additional_gaps/FPMS-ADDGAP-RECEIPT-SAME-CASE-GATE-20260710-01.md`
- `artifacts/FPMS-ADDGAP-RECEIPT-SAME-CASE-GATE-20260710-01/**`

Runtime contracts:

- Permission: 沿用 OfficialWorkflow.Update。
- Status codes/errors: 404 package/attachment；400 OFFICIAL_WORK_PACKAGE_RECEIPT_CASE_MISMATCH；有效写入 201。
- Response envelope: 沿用当前 receipt 输出模型。
- SQLite: 校验先于任何写；事务短。
- Simplified Chinese UI: N/A。

Required verification:

- RED/GREEN behavior: `cd backend && .venv/bin/pytest -q tests/test_addgap_receipt_same_case_gate.py`
- Scoped Ruff: `cd backend && .venv/bin/ruff check --fix app/modules/official_workflows/service.py tests/test_addgap_receipt_same_case_gate.py && .venv/bin/ruff format app/modules/official_workflows/service.py tests/test_addgap_receipt_same_case_gate.py && .venv/bin/ruff check app/modules/official_workflows/service.py tests/test_addgap_receipt_same_case_gate.py`
- Scope: `git diff --check -- backend/app/modules/official_workflows/service.py backend/tests/test_addgap_receipt_same_case_gate.py`
- Evidence: initialize/finalize with `./scripts/evidence_run.sh FPMS-ADDGAP-RECEIPT-SAME-CASE-GATE-20260710-01 <step> <command...>`, then run `./scripts/task_validate.sh FPMS-ADDGAP-RECEIPT-SAME-CASE-GATE-20260710-01`.

Done definition: RED evidence exists where applicable; minimum implementation is GREEN; scoped lint/type/build/test and scope diff pass; required dirty-baseline and completion artifacts exist under `artifacts/FPMS-ADDGAP-RECEIPT-SAME-CASE-GATE-20260710-01/`; `./scripts/task_validate.sh FPMS-ADDGAP-RECEIPT-SAME-CASE-GATE-20260710-01` returns 0; exact closure is complete; explicit non-closure is respected. Otherwise status is FAIL or BLOCKED, never PASS.

### 15 — `FPMS-ADDGAP-OA-RECEIPT-SOURCE-GATE-20260710-01`

- Task file: `tasks/additional_gaps/FPMS-ADDGAP-OA-RECEIPT-SOURCE-GATE-20260710-01.md`
- Wave: 3
- Owner role: Backend Developer / worker
- Exact closure: 同案 OA 收据必须附着于 linked reply document 或显式 package manifest。
- Explicit non-closure: 不验证收据号内容，不扫描历史数据，不 archive/close。
- Dependencies: 14
- Remaining follow-up task IDs: 16, 17
- Shared ownership decision: only the source paths in the exact allowlist below; serialize any repeated path per approved plan.

Exact allowlist:

- `backend/app/modules/official_workflows/service.py`
- `backend/tests/test_addgap_oa_receipt_source_gate.py`
- `tasks/additional_gaps/FPMS-ADDGAP-OA-RECEIPT-SOURCE-GATE-20260710-01.md`
- `artifacts/FPMS-ADDGAP-OA-RECEIPT-SOURCE-GATE-20260710-01/**`

Runtime contracts:

- Permission: 沿用 OfficialWorkflow.Update。
- Status codes/errors: 无效来源 400 OA_RECEIPT_ATTACHMENT_SOURCE_INVALID；有效写入 201。
- Response envelope: 沿用当前 receipt 输出模型。
- SQLite: 先校验后写入。
- Simplified Chinese UI: N/A。

Required verification:

- RED/GREEN behavior: `cd backend && .venv/bin/pytest -q tests/test_addgap_oa_receipt_source_gate.py`
- Scoped Ruff: `cd backend && .venv/bin/ruff check --fix app/modules/official_workflows/service.py tests/test_addgap_oa_receipt_source_gate.py && .venv/bin/ruff format app/modules/official_workflows/service.py tests/test_addgap_oa_receipt_source_gate.py && .venv/bin/ruff check app/modules/official_workflows/service.py tests/test_addgap_oa_receipt_source_gate.py`
- Scope: `git diff --check -- backend/app/modules/official_workflows/service.py backend/tests/test_addgap_oa_receipt_source_gate.py`
- Evidence: initialize/finalize with `./scripts/evidence_run.sh FPMS-ADDGAP-OA-RECEIPT-SOURCE-GATE-20260710-01 <step> <command...>`, then run `./scripts/task_validate.sh FPMS-ADDGAP-OA-RECEIPT-SOURCE-GATE-20260710-01`.

Done definition: RED evidence exists where applicable; minimum implementation is GREEN; scoped lint/type/build/test and scope diff pass; required dirty-baseline and completion artifacts exist under `artifacts/FPMS-ADDGAP-OA-RECEIPT-SOURCE-GATE-20260710-01/`; `./scripts/task_validate.sh FPMS-ADDGAP-OA-RECEIPT-SOURCE-GATE-20260710-01` returns 0; exact closure is complete; explicit non-closure is respected. Otherwise status is FAIL or BLOCKED, never PASS.

### 16 — `FPMS-ADDGAP-RECEIPT-HISTORY-SCAN-20260710-01`

- Task file: `tasks/additional_gaps/FPMS-ADDGAP-RECEIPT-HISTORY-SCAN-20260710-01.md`
- Wave: 3
- Owner role: Backend Developer / worker
- Exact closure: 新增只读扫描，报告历史 cross-case 与 OA-source-invalid receipt links。
- Explicit non-closure: 不自动修复/删除历史数据，不修改产品 API，不 close task。
- Dependencies: 14, 15
- Remaining follow-up task IDs: 17
- Shared ownership decision: only the source paths in the exact allowlist below; serialize any repeated path per approved plan.

Exact allowlist:

- `backend/scripts/audit_receipt_ownership.py`
- `backend/tests/test_addgap_receipt_history_scan.py`
- `tasks/additional_gaps/FPMS-ADDGAP-RECEIPT-HISTORY-SCAN-20260710-01.md`
- `artifacts/FPMS-ADDGAP-RECEIPT-HISTORY-SCAN-20260710-01/**`

Runtime contracts:

- Permission: N/A（离线只读审计）。
- Status codes/errors: 进程 0 表示扫描完成；发现问题通过结构化输出报告而非改写。
- Response envelope: N/A。
- SQLite: 只读、SQLite-safe 查询。
- Simplified Chinese UI: N/A。

Required verification:

- RED/GREEN behavior: `cd backend && .venv/bin/pytest -q tests/test_addgap_receipt_history_scan.py`
- Scoped Ruff: `cd backend && .venv/bin/ruff check --fix scripts/audit_receipt_ownership.py tests/test_addgap_receipt_history_scan.py && .venv/bin/ruff format scripts/audit_receipt_ownership.py tests/test_addgap_receipt_history_scan.py && .venv/bin/ruff check scripts/audit_receipt_ownership.py tests/test_addgap_receipt_history_scan.py`
- Scope: `git diff --check -- backend/scripts/audit_receipt_ownership.py backend/tests/test_addgap_receipt_history_scan.py`
- Evidence: initialize/finalize with `./scripts/evidence_run.sh FPMS-ADDGAP-RECEIPT-HISTORY-SCAN-20260710-01 <step> <command...>`, then run `./scripts/task_validate.sh FPMS-ADDGAP-RECEIPT-HISTORY-SCAN-20260710-01`.

Done definition: RED evidence exists where applicable; minimum implementation is GREEN; scoped lint/type/build/test and scope diff pass; required dirty-baseline and completion artifacts exist under `artifacts/FPMS-ADDGAP-RECEIPT-HISTORY-SCAN-20260710-01/`; `./scripts/task_validate.sh FPMS-ADDGAP-RECEIPT-HISTORY-SCAN-20260710-01` returns 0; exact closure is complete; explicit non-closure is respected. Otherwise status is FAIL or BLOCKED, never PASS.

### 17 — `FPMS-ADDGAP-OA-RECEIPT-ARCHIVE-EVENT-20260710-01`

- Task file: `tasks/additional_gaps/FPMS-ADDGAP-OA-RECEIPT-ARCHIVE-EVENT-20260710-01.md`
- Wave: 4
- Owner role: Backend Developer / worker
- Exact closure: 在一个 OFFICIAL_RECEIPT_ARCHIVED 事务中重验收据、精确关闭一个 OA task、archive package、将 OA1/OA2 恢复 SUB_EXAM 并写证据。
- Explicit non-closure: override 不发事件、不关 task、不改 case；不实现收据号内容匹配或通用状态矩阵。
- Dependencies: 13–16
- Remaining follow-up task IDs: 46, 47
- Shared ownership decision: only the source paths in the exact allowlist below; serialize any repeated path per approved plan.

Exact allowlist:

- `backend/app/modules/official_workflows/service.py`
- `backend/tests/test_addgap_oa_receipt_archive_event.py`
- `tasks/additional_gaps/FPMS-ADDGAP-OA-RECEIPT-ARCHIVE-EVENT-20260710-01.md`
- `artifacts/FPMS-ADDGAP-OA-RECEIPT-ARCHIVE-EVENT-20260710-01/**`

Runtime contracts:

- Permission: 沿用 OfficialWorkflow.Update。
- Status codes/errors: 缺/无效收据、零/多任务、错误 case state 均 409 且零写入；override 200/OVERRIDE；重复 archive 幂等。
- Response envelope: 沿用现有 `OfficialWorkPackageArchiveResultOut`（`package + evaluation`），不新增响应字段。
- SQLite: 单短事务，关闭选择必须确定且 SQLite-safe。
- Simplified Chinese UI: N/A。

Required verification:

- RED/GREEN behavior: `cd backend && .venv/bin/pytest -q tests/test_addgap_oa_receipt_archive_event.py`
- Scoped Ruff: `cd backend && .venv/bin/ruff check --fix app/modules/official_workflows/service.py tests/test_addgap_oa_receipt_archive_event.py && .venv/bin/ruff format app/modules/official_workflows/service.py tests/test_addgap_oa_receipt_archive_event.py && .venv/bin/ruff check app/modules/official_workflows/service.py tests/test_addgap_oa_receipt_archive_event.py`
- Scope: `git diff --check -- backend/app/modules/official_workflows/service.py backend/tests/test_addgap_oa_receipt_archive_event.py`
- Evidence: initialize/finalize with `./scripts/evidence_run.sh FPMS-ADDGAP-OA-RECEIPT-ARCHIVE-EVENT-20260710-01 <step> <command...>`, then run `./scripts/task_validate.sh FPMS-ADDGAP-OA-RECEIPT-ARCHIVE-EVENT-20260710-01`.

Done definition: RED evidence exists where applicable; minimum implementation is GREEN; scoped lint/type/build/test and scope diff pass; required dirty-baseline and completion artifacts exist under `artifacts/FPMS-ADDGAP-OA-RECEIPT-ARCHIVE-EVENT-20260710-01/`; `./scripts/task_validate.sh FPMS-ADDGAP-OA-RECEIPT-ARCHIVE-EVENT-20260710-01` returns 0; exact closure is complete; explicit non-closure is respected. Otherwise status is FAIL or BLOCKED, never PASS.

### 18 — `FPMS-ADDGAP-OA-SUBSEQUENT-TASK-IDENTITY-20260710-01`

- Task file: `tasks/additional_gaps/FPMS-ADDGAP-OA-SUBSEQUENT-TASK-IDENTITY-20260710-01.md`
- Wave: 5
- Owner role: Backend Developer / worker
- Exact closure: seed OA_REPLY_SUBSEQUENT 作为二次及以后 OA 的 task identity，且不提供可计算期限 fallback。
- Explicit non-closure: 不激活中文目录、不改变首 OA 任务、不从模板天数生成期限。
- Dependencies: 03
- Remaining follow-up task IDs: 26, 27, 33
- Shared ownership decision: only the source paths in the exact allowlist below; serialize any repeated path per approved plan.

Exact allowlist:

- `backend/scripts/seed_dev.py`
- `backend/tests/test_addgap_oa_subsequent_task_identity.py`
- `tasks/additional_gaps/FPMS-ADDGAP-OA-SUBSEQUENT-TASK-IDENTITY-20260710-01.md`
- `artifacts/FPMS-ADDGAP-OA-SUBSEQUENT-TASK-IDENTITY-20260710-01/**`

Runtime contracts:

- Permission: N/A（幂等 seed）。
- Status codes/errors: N/A；缺显式截止日时后续消费者必须 409。
- Response envelope: N/A。
- SQLite: seed 幂等、bootstrap-safe。
- Simplified Chinese UI: N/A。

Required verification:

- RED/GREEN behavior: `cd backend && .venv/bin/pytest -q tests/test_addgap_oa_subsequent_task_identity.py`
- Scoped Ruff: `cd backend && .venv/bin/ruff check --fix scripts/seed_dev.py tests/test_addgap_oa_subsequent_task_identity.py && .venv/bin/ruff format scripts/seed_dev.py tests/test_addgap_oa_subsequent_task_identity.py && .venv/bin/ruff check scripts/seed_dev.py tests/test_addgap_oa_subsequent_task_identity.py`
- Scope: `git diff --check -- backend/scripts/seed_dev.py backend/tests/test_addgap_oa_subsequent_task_identity.py`
- Evidence: initialize/finalize with `./scripts/evidence_run.sh FPMS-ADDGAP-OA-SUBSEQUENT-TASK-IDENTITY-20260710-01 <step> <command...>`, then run `./scripts/task_validate.sh FPMS-ADDGAP-OA-SUBSEQUENT-TASK-IDENTITY-20260710-01`.

Done definition: RED evidence exists where applicable; minimum implementation is GREEN; scoped lint/type/build/test and scope diff pass; required dirty-baseline and completion artifacts exist under `artifacts/FPMS-ADDGAP-OA-SUBSEQUENT-TASK-IDENTITY-20260710-01/`; `./scripts/task_validate.sh FPMS-ADDGAP-OA-SUBSEQUENT-TASK-IDENTITY-20260710-01` returns 0; exact closure is complete; explicit non-closure is respected. Otherwise status is FAIL or BLOCKED, never PASS.

### 19 — `FPMS-ADDGAP-NOTICE-CATALOG-CLASSIFICATION-20260710-01`

- Task file: `tasks/additional_gaps/FPMS-ADDGAP-NOTICE-CATALOG-CLASSIFICATION-20260710-01.md`
- Wave: 5
- Owner role: Backend Developer / worker
- Exact closure: 将全部 60 条 official-notice catalog 行标记为 reference-only/non-selectable，保留源代码且无执行副作用。
- Explicit non-closure: 不激活任何 OA、授权、复审、年费或其他语义，不删除目录项。
- Dependencies: 03
- Remaining follow-up task IDs: 20, 21, 33, 38
- Shared ownership decision: only the source paths in the exact allowlist below; serialize any repeated path per approved plan.

Exact allowlist:

- `backend/app/modules/documents/official_notice_catalog.py`
- `backend/tests/test_addgap_notice_catalog_classification.py`
- `tasks/additional_gaps/FPMS-ADDGAP-NOTICE-CATALOG-CLASSIFICATION-20260710-01.md`
- `artifacts/FPMS-ADDGAP-NOTICE-CATALOG-CLASSIFICATION-20260710-01/**`

Runtime contracts:

- Permission: N/A（目录数据定义）。
- Status codes/errors: N/A；所有未确认项 fail-closed。
- Response envelope: 目录输出字段沿用现有 schema。
- SQLite: N/A。
- Simplified Chinese UI: N/A；UI clarity 由 Task 20。

Required verification:

- RED/GREEN behavior: `cd backend && .venv/bin/pytest -q tests/test_addgap_notice_catalog_classification.py`
- Scoped Ruff: `cd backend && .venv/bin/ruff check --fix app/modules/documents/official_notice_catalog.py tests/test_addgap_notice_catalog_classification.py && .venv/bin/ruff format app/modules/documents/official_notice_catalog.py tests/test_addgap_notice_catalog_classification.py && .venv/bin/ruff check app/modules/documents/official_notice_catalog.py tests/test_addgap_notice_catalog_classification.py`
- Scope: `git diff --check -- backend/app/modules/documents/official_notice_catalog.py backend/tests/test_addgap_notice_catalog_classification.py`
- Evidence: initialize/finalize with `./scripts/evidence_run.sh FPMS-ADDGAP-NOTICE-CATALOG-CLASSIFICATION-20260710-01 <step> <command...>`, then run `./scripts/task_validate.sh FPMS-ADDGAP-NOTICE-CATALOG-CLASSIFICATION-20260710-01`.

Done definition: RED evidence exists where applicable; minimum implementation is GREEN; scoped lint/type/build/test and scope diff pass; required dirty-baseline and completion artifacts exist under `artifacts/FPMS-ADDGAP-NOTICE-CATALOG-CLASSIFICATION-20260710-01/`; `./scripts/task_validate.sh FPMS-ADDGAP-NOTICE-CATALOG-CLASSIFICATION-20260710-01` returns 0; exact closure is complete; explicit non-closure is respected. Otherwise status is FAIL or BLOCKED, never PASS.

### 20 — `FPMS-ADDGAP-NOTICE-CATALOG-UI-CLARITY-20260710-01`

- Task file: `tasks/additional_gaps/FPMS-ADDGAP-NOTICE-CATALOG-UI-CLARITY-20260710-01.md`
- Wave: 5
- Owner role: Frontend Developer / worker
- Exact closure: DocumentCreate 显示全部目录行，使用简体中文可执行/仅供参考标签，并禁选 reference-only。
- Explicit non-closure: 不隐藏 reference-only 项，不激活语义，不修改 backend gate。
- Dependencies: 19
- Remaining follow-up task IDs: 46
- Shared ownership decision: only the source paths in the exact allowlist below; serialize any repeated path per approved plan.

Exact allowlist:

- `frontend/src/modules/documents/pages/DocumentCreate.vue`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/addgap-notice-catalog-ui-clarity.spec.ts`
- `tasks/additional_gaps/FPMS-ADDGAP-NOTICE-CATALOG-UI-CLARITY-20260710-01.md`
- `artifacts/FPMS-ADDGAP-NOTICE-CATALOG-UI-CLARITY-20260710-01/**`

Runtime contracts:

- Permission: 沿用 DocTemplate.Read/Doc.Create。
- Status codes/errors: 读取成功 200；reference-only 在客户端不可提交。
- Response envelope: 消费既有模板列表响应。
- SQLite: N/A。
- Simplified Chinese UI: 所有标签、说明、禁用原因必须为简体中文。

Required verification:

- RED/GREEN behavior: `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npx playwright test src/tests/addgap-notice-catalog-ui-clarity.spec.ts --workers=1`
- Frontend checks: `cd frontend && npm run lint && npm run typecheck`
- Scope: `git diff --check -- frontend/src/modules/documents/pages/DocumentCreate.vue FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/addgap-notice-catalog-ui-clarity.spec.ts`
- Evidence: initialize/finalize with `./scripts/evidence_run.sh FPMS-ADDGAP-NOTICE-CATALOG-UI-CLARITY-20260710-01 <step> <command...>`, then run `./scripts/task_validate.sh FPMS-ADDGAP-NOTICE-CATALOG-UI-CLARITY-20260710-01`.

Done definition: RED evidence exists where applicable; minimum implementation is GREEN; scoped lint/type/build/test and scope diff pass; required dirty-baseline and completion artifacts exist under `artifacts/FPMS-ADDGAP-NOTICE-CATALOG-UI-CLARITY-20260710-01/`; `./scripts/task_validate.sh FPMS-ADDGAP-NOTICE-CATALOG-UI-CLARITY-20260710-01` returns 0; exact closure is complete; explicit non-closure is respected. Otherwise status is FAIL or BLOCKED, never PASS.

### 21 — `FPMS-ADDGAP-NOTICE-CATALOG-REFERENCE-GATE-20260710-01`

- Task file: `tasks/additional_gaps/FPMS-ADDGAP-NOTICE-CATALOG-REFERENCE-GATE-20260710-01.md`
- Wave: 5
- Owner role: Backend Developer / worker
- Exact closure: 文档普通创建和 wizard 均拒绝 reference-only official catalog template。
- Explicit non-closure: 不拒绝普通非目录模板，不激活目录语义，不更改 UI。
- Dependencies: 03, 19
- Remaining follow-up task IDs: 33, 38, 46
- Shared ownership decision: only the source paths in the exact allowlist below; serialize any repeated path per approved plan.

Exact allowlist:

- `backend/app/modules/documents/service.py`
- `backend/tests/test_addgap_notice_catalog_reference_gate.py`
- `tasks/additional_gaps/FPMS-ADDGAP-NOTICE-CATALOG-REFERENCE-GATE-20260710-01.md`
- `artifacts/FPMS-ADDGAP-NOTICE-CATALOG-REFERENCE-GATE-20260710-01/**`

Runtime contracts:

- Permission: 沿用 Doc.Create。
- Status codes/errors: reference-only 使用返回 409；可执行/普通模板保持既有成功状态。
- Response envelope: 错误沿用既有 detail 语义；成功沿用 DocumentOut/wizard 包络。
- SQLite: 校验先于持久化。
- Simplified Chinese UI: N/A。

Required verification:

- RED/GREEN behavior: `cd backend && .venv/bin/pytest -q tests/test_addgap_notice_catalog_reference_gate.py`
- Scoped Ruff: `cd backend && .venv/bin/ruff check --fix app/modules/documents/service.py tests/test_addgap_notice_catalog_reference_gate.py && .venv/bin/ruff format app/modules/documents/service.py tests/test_addgap_notice_catalog_reference_gate.py && .venv/bin/ruff check app/modules/documents/service.py tests/test_addgap_notice_catalog_reference_gate.py`
- Scope: `git diff --check -- backend/app/modules/documents/service.py backend/tests/test_addgap_notice_catalog_reference_gate.py`
- Evidence: initialize/finalize with `./scripts/evidence_run.sh FPMS-ADDGAP-NOTICE-CATALOG-REFERENCE-GATE-20260710-01 <step> <command...>`, then run `./scripts/task_validate.sh FPMS-ADDGAP-NOTICE-CATALOG-REFERENCE-GATE-20260710-01`.

Done definition: RED evidence exists where applicable; minimum implementation is GREEN; scoped lint/type/build/test and scope diff pass; required dirty-baseline and completion artifacts exist under `artifacts/FPMS-ADDGAP-NOTICE-CATALOG-REFERENCE-GATE-20260710-01/`; `./scripts/task_validate.sh FPMS-ADDGAP-NOTICE-CATALOG-REFERENCE-GATE-20260710-01` returns 0; exact closure is complete; explicit non-closure is respected. Otherwise status is FAIL or BLOCKED, never PASS.

### 22 — `FPMS-ADDGAP-DOCUMENT-DEADLINE-CARRIER-20260710-01`

- Task file: `tasks/additional_gaps/FPMS-ADDGAP-DOCUMENT-DEADLINE-CARRIER-20260710-01.md`
- Wave: 6
- Owner role: Backend Developer / worker
- Exact closure: 提供 canonical extra_data parser/merger，保留未知 JSON 和 legacy text，并只读投影 LEGACY_UNVERIFIED。
- Explicit non-closure: 不修改 API/schema/UI，不生成任务，不覆盖未知键。
- Dependencies: 03
- Remaining follow-up task IDs: 23–32, 35–40
- Shared ownership decision: only the source paths in the exact allowlist below; serialize any repeated path per approved plan.

Exact allowlist:

- `backend/app/modules/documents/extra_data.py`
- `backend/tests/test_addgap_document_deadline_carrier.py`
- `tasks/additional_gaps/FPMS-ADDGAP-DOCUMENT-DEADLINE-CARRIER-20260710-01.md`
- `artifacts/FPMS-ADDGAP-DOCUMENT-DEADLINE-CARRIER-20260710-01/**`

Runtime contracts:

- Permission: N/A（纯内部组件）。
- Status codes/errors: 畸形 shape 由调用方映射 422，cross-field 业务错误映射 400。
- Response envelope: N/A。
- SQLite: 数据仍以现有 TEXT/JSON 兼容格式保存；不引入 JSONB。
- Simplified Chinese UI: N/A。

Required verification:

- RED/GREEN behavior: `cd backend && .venv/bin/pytest -q tests/test_addgap_document_deadline_carrier.py`
- Scoped Ruff: `cd backend && .venv/bin/ruff check --fix app/modules/documents/extra_data.py tests/test_addgap_document_deadline_carrier.py && .venv/bin/ruff format app/modules/documents/extra_data.py tests/test_addgap_document_deadline_carrier.py && .venv/bin/ruff check app/modules/documents/extra_data.py tests/test_addgap_document_deadline_carrier.py`
- Scope: `git diff --check -- backend/app/modules/documents/extra_data.py backend/tests/test_addgap_document_deadline_carrier.py`
- Evidence: initialize/finalize with `./scripts/evidence_run.sh FPMS-ADDGAP-DOCUMENT-DEADLINE-CARRIER-20260710-01 <step> <command...>`, then run `./scripts/task_validate.sh FPMS-ADDGAP-DOCUMENT-DEADLINE-CARRIER-20260710-01`.

Done definition: RED evidence exists where applicable; minimum implementation is GREEN; scoped lint/type/build/test and scope diff pass; required dirty-baseline and completion artifacts exist under `artifacts/FPMS-ADDGAP-DOCUMENT-DEADLINE-CARRIER-20260710-01/`; `./scripts/task_validate.sh FPMS-ADDGAP-DOCUMENT-DEADLINE-CARRIER-20260710-01` returns 0; exact closure is complete; explicit non-closure is respected. Otherwise status is FAIL or BLOCKED, never PASS.

### 23 — `FPMS-ADDGAP-DOCUMENT-DEADLINE-READ-PROJECTION-20260710-01`

- Task file: `tasks/additional_gaps/FPMS-ADDGAP-DOCUMENT-DEADLINE-READ-PROJECTION-20260710-01.md`
- Wave: 6
- Owner role: Backend Developer / worker
- Exact closure: 所有既有 DocumentOut 响应投影 structured due/source/read-status/description，同时保留 extra_data。
- Explicit non-closure: 不接受写入、不同步任务、不修改数据库 schema。
- Dependencies: 22
- Remaining follow-up task IDs: 24, 25, 28
- Shared ownership decision: only the source paths in the exact allowlist below; serialize any repeated path per approved plan.

Exact allowlist:

- `backend/app/modules/documents/schemas.py`
- `backend/app/modules/documents/api.py`
- `backend/tests/test_addgap_document_deadline_read_projection.py`
- `tasks/additional_gaps/FPMS-ADDGAP-DOCUMENT-DEADLINE-READ-PROJECTION-20260710-01.md`
- `artifacts/FPMS-ADDGAP-DOCUMENT-DEADLINE-READ-PROJECTION-20260710-01/**`

Runtime contracts:

- Permission: 沿用各 Document.Read/Create/Edit 路由权限。
- Status codes/errors: GET/既有响应状态不变；读取 legacy 不报错并投影 LEGACY_UNVERIFIED。
- Response envelope: 扩展既有 DocumentOut，不新增 envelope。
- SQLite: 纯投影，SQLite-safe。
- Simplified Chinese UI: N/A。

Required verification:

- RED/GREEN behavior: `cd backend && .venv/bin/pytest -q tests/test_addgap_document_deadline_read_projection.py`
- Scoped Ruff: `cd backend && .venv/bin/ruff check --fix app/modules/documents/schemas.py app/modules/documents/api.py tests/test_addgap_document_deadline_read_projection.py && .venv/bin/ruff format app/modules/documents/schemas.py app/modules/documents/api.py tests/test_addgap_document_deadline_read_projection.py && .venv/bin/ruff check app/modules/documents/schemas.py app/modules/documents/api.py tests/test_addgap_document_deadline_read_projection.py`
- Scope: `git diff --check -- backend/app/modules/documents/schemas.py backend/app/modules/documents/api.py backend/tests/test_addgap_document_deadline_read_projection.py`
- Evidence: initialize/finalize with `./scripts/evidence_run.sh FPMS-ADDGAP-DOCUMENT-DEADLINE-READ-PROJECTION-20260710-01 <step> <command...>`, then run `./scripts/task_validate.sh FPMS-ADDGAP-DOCUMENT-DEADLINE-READ-PROJECTION-20260710-01`.

Done definition: RED evidence exists where applicable; minimum implementation is GREEN; scoped lint/type/build/test and scope diff pass; required dirty-baseline and completion artifacts exist under `artifacts/FPMS-ADDGAP-DOCUMENT-DEADLINE-READ-PROJECTION-20260710-01/`; `./scripts/task_validate.sh FPMS-ADDGAP-DOCUMENT-DEADLINE-READ-PROJECTION-20260710-01` returns 0; exact closure is complete; explicit non-closure is respected. Otherwise status is FAIL or BLOCKED, never PASS.

### 24 — `FPMS-ADDGAP-DOCUMENT-DEADLINE-CREATE-API-20260710-01`

- Task file: `tasks/additional_gaps/FPMS-ADDGAP-DOCUMENT-DEADLINE-CREATE-API-20260710-01.md`
- Wave: 6
- Owner role: Backend Developer / worker
- Exact closure: POST document 接受 write-status、due、source 字段并持久化 canonical structured deadline。
- Explicit non-closure: 不实现普通更新/影响预览/wizard/UI，不允许写入 LEGACY_UNVERIFIED。
- Dependencies: 02, 22, 23
- Remaining follow-up task IDs: 25, 29, 30, 39
- Shared ownership decision: only the source paths in the exact allowlist below; serialize any repeated path per approved plan.

Exact allowlist:

- `backend/app/modules/documents/schemas.py`
- `backend/app/modules/documents/service.py`
- `backend/app/modules/documents/api.py`
- `backend/tests/test_addgap_document_deadline_create_api.py`
- `tasks/additional_gaps/FPMS-ADDGAP-DOCUMENT-DEADLINE-CREATE-API-20260710-01.md`
- `artifacts/FPMS-ADDGAP-DOCUMENT-DEADLINE-CREATE-API-20260710-01/**`

Runtime contracts:

- Permission: Doc.Create，函数参数 Depends 注入。
- Status codes/errors: POST 201；shape 422；cross-field 400；缺确认/配置或冲突 409。
- Response envelope: 既有 DocumentOut，含新增 read projection。
- SQLite: 与 Task 02 同一事务；不依赖 RETURNING。
- Simplified Chinese UI: N/A。

Required verification:

- RED/GREEN behavior: `cd backend && .venv/bin/pytest -q tests/test_addgap_document_deadline_create_api.py`
- Scoped Ruff: `cd backend && .venv/bin/ruff check --fix app/modules/documents/schemas.py app/modules/documents/service.py app/modules/documents/api.py tests/test_addgap_document_deadline_create_api.py && .venv/bin/ruff format app/modules/documents/schemas.py app/modules/documents/service.py app/modules/documents/api.py tests/test_addgap_document_deadline_create_api.py && .venv/bin/ruff check app/modules/documents/schemas.py app/modules/documents/service.py app/modules/documents/api.py tests/test_addgap_document_deadline_create_api.py`
- Scope: `git diff --check -- backend/app/modules/documents/schemas.py backend/app/modules/documents/service.py backend/app/modules/documents/api.py backend/tests/test_addgap_document_deadline_create_api.py`
- Evidence: initialize/finalize with `./scripts/evidence_run.sh FPMS-ADDGAP-DOCUMENT-DEADLINE-CREATE-API-20260710-01 <step> <command...>`, then run `./scripts/task_validate.sh FPMS-ADDGAP-DOCUMENT-DEADLINE-CREATE-API-20260710-01`.

Done definition: RED evidence exists where applicable; minimum implementation is GREEN; scoped lint/type/build/test and scope diff pass; required dirty-baseline and completion artifacts exist under `artifacts/FPMS-ADDGAP-DOCUMENT-DEADLINE-CREATE-API-20260710-01/`; `./scripts/task_validate.sh FPMS-ADDGAP-DOCUMENT-DEADLINE-CREATE-API-20260710-01` returns 0; exact closure is complete; explicit non-closure is respected. Otherwise status is FAIL or BLOCKED, never PASS.

### 25 — `FPMS-ADDGAP-DOCUMENT-DEADLINE-UPDATE-API-20260710-01`

- Task file: `tasks/additional_gaps/FPMS-ADDGAP-DOCUMENT-DEADLINE-UPDATE-API-20260710-01.md`
- Wave: 6
- Owner role: Backend Developer / worker
- Exact closure: PUT document 可确认 missing/legacy 的同一日期，但普通编辑拒绝改变或清除已确认 due。
- Explicit non-closure: 不提供正式 deadline override workflow，不实现 UI，不同步其他任务类型。
- Dependencies: 22–24
- Remaining follow-up task IDs: 26, 32, 40
- Shared ownership decision: only the source paths in the exact allowlist below; serialize any repeated path per approved plan.

Exact allowlist:

- `backend/app/modules/documents/schemas.py`
- `backend/app/modules/documents/service.py`
- `backend/app/modules/documents/api.py`
- `backend/tests/test_addgap_document_deadline_update_api.py`
- `tasks/additional_gaps/FPMS-ADDGAP-DOCUMENT-DEADLINE-UPDATE-API-20260710-01.md`
- `artifacts/FPMS-ADDGAP-DOCUMENT-DEADLINE-UPDATE-API-20260710-01/**`

Runtime contracts:

- Permission: Doc.Edit，函数参数 Depends 注入。
- Status codes/errors: 成功 200；shape 422；cross-field 400；已确认 due 变更/清除 409。
- Response envelope: 既有 DocumentOut。
- SQLite: 单短事务，保留未知 extra_data。
- Simplified Chinese UI: N/A。

Required verification:

- RED/GREEN behavior: `cd backend && .venv/bin/pytest -q tests/test_addgap_document_deadline_update_api.py`
- Scoped Ruff: `cd backend && .venv/bin/ruff check --fix app/modules/documents/schemas.py app/modules/documents/service.py app/modules/documents/api.py tests/test_addgap_document_deadline_update_api.py && .venv/bin/ruff format app/modules/documents/schemas.py app/modules/documents/service.py app/modules/documents/api.py tests/test_addgap_document_deadline_update_api.py && .venv/bin/ruff check app/modules/documents/schemas.py app/modules/documents/service.py app/modules/documents/api.py tests/test_addgap_document_deadline_update_api.py`
- Scope: `git diff --check -- backend/app/modules/documents/schemas.py backend/app/modules/documents/service.py backend/app/modules/documents/api.py backend/tests/test_addgap_document_deadline_update_api.py`
- Evidence: initialize/finalize with `./scripts/evidence_run.sh FPMS-ADDGAP-DOCUMENT-DEADLINE-UPDATE-API-20260710-01 <step> <command...>`, then run `./scripts/task_validate.sh FPMS-ADDGAP-DOCUMENT-DEADLINE-UPDATE-API-20260710-01`.

Done definition: RED evidence exists where applicable; minimum implementation is GREEN; scoped lint/type/build/test and scope diff pass; required dirty-baseline and completion artifacts exist under `artifacts/FPMS-ADDGAP-DOCUMENT-DEADLINE-UPDATE-API-20260710-01/`; `./scripts/task_validate.sh FPMS-ADDGAP-DOCUMENT-DEADLINE-UPDATE-API-20260710-01` returns 0; exact closure is complete; explicit non-closure is respected. Otherwise status is FAIL or BLOCKED, never PASS.

### 26 — `FPMS-ADDGAP-LEGACY-DEADLINE-TASK-SYNC-20260710-01`

- Task file: `tasks/additional_gaps/FPMS-ADDGAP-LEGACY-DEADLINE-TASK-SYNC-20260710-01.md`
- Wave: 6
- Owner role: Backend Developer / worker
- Exact closure: 确认同一 legacy/missing 日期时，重算恰好一个 matching OA task 的 due/internal/reminders 并记录证据。
- Explicit non-closure: 不支持改变已确认日期，不触碰 grant task，不在零/多任务时猜测。
- Dependencies: 18, 25
- Remaining follow-up task IDs: 32, 46
- Shared ownership decision: only the source paths in the exact allowlist below; serialize any repeated path per approved plan.

Exact allowlist:

- `backend/app/modules/documents/service.py`
- `backend/app/modules/tasks/task_generation_service.py`
- `backend/tests/test_addgap_legacy_deadline_task_sync.py`
- `tasks/additional_gaps/FPMS-ADDGAP-LEGACY-DEADLINE-TASK-SYNC-20260710-01.md`
- `artifacts/FPMS-ADDGAP-LEGACY-DEADLINE-TASK-SYNC-20260710-01/**`

Runtime contracts:

- Permission: 沿用 Doc.Edit。
- Status codes/errors: 零/多 matching OA task 或冲突返回 409 且零写入；成功 200。
- Response envelope: 沿用 DocumentOut。
- SQLite: 精确选择并在单事务同步；SQLite-safe date math。
- Simplified Chinese UI: N/A。

Required verification:

- RED/GREEN behavior: `cd backend && .venv/bin/pytest -q tests/test_addgap_legacy_deadline_task_sync.py`
- Scoped Ruff: `cd backend && .venv/bin/ruff check --fix app/modules/documents/service.py app/modules/tasks/task_generation_service.py tests/test_addgap_legacy_deadline_task_sync.py && .venv/bin/ruff format app/modules/documents/service.py app/modules/tasks/task_generation_service.py tests/test_addgap_legacy_deadline_task_sync.py && .venv/bin/ruff check app/modules/documents/service.py app/modules/tasks/task_generation_service.py tests/test_addgap_legacy_deadline_task_sync.py`
- Scope: `git diff --check -- backend/app/modules/documents/service.py backend/app/modules/tasks/task_generation_service.py backend/tests/test_addgap_legacy_deadline_task_sync.py`
- Evidence: initialize/finalize with `./scripts/evidence_run.sh FPMS-ADDGAP-LEGACY-DEADLINE-TASK-SYNC-20260710-01 <step> <command...>`, then run `./scripts/task_validate.sh FPMS-ADDGAP-LEGACY-DEADLINE-TASK-SYNC-20260710-01`.

Done definition: RED evidence exists where applicable; minimum implementation is GREEN; scoped lint/type/build/test and scope diff pass; required dirty-baseline and completion artifacts exist under `artifacts/FPMS-ADDGAP-LEGACY-DEADLINE-TASK-SYNC-20260710-01/`; `./scripts/task_validate.sh FPMS-ADDGAP-LEGACY-DEADLINE-TASK-SYNC-20260710-01` returns 0; exact closure is complete; explicit non-closure is respected. Otherwise status is FAIL or BLOCKED, never PASS.

### 27 — `FPMS-ADDGAP-OA-DEADLINE-FAIL-CLOSED-20260710-01`

- Task file: `tasks/additional_gaps/FPMS-ADDGAP-OA-DEADLINE-FAIL-CLOSED-20260710-01.md`
- Wave: 6
- Owner role: Backend Developer / worker
- Exact closure: 可执行 OA task generation 必须使用 confirmed explicit due，绝不使用 task-template 天数 fallback。
- Explicit non-closure: 不实现日期录入/UI，不计算第二次 OA 法定期限，不修改其他任务类型。
- Dependencies: 02–04, 18, 22
- Remaining follow-up task IDs: 28, 29, 33, 46
- Shared ownership decision: only the source paths in the exact allowlist below; serialize any repeated path per approved plan.

Exact allowlist:

- `backend/app/modules/tasks/task_generation_service.py`
- `backend/tests/test_addgap_oa_deadline_fail_closed.py`
- `tasks/additional_gaps/FPMS-ADDGAP-OA-DEADLINE-FAIL-CLOSED-20260710-01.md`
- `artifacts/FPMS-ADDGAP-OA-DEADLINE-FAIL-CLOSED-20260710-01/**`

Runtime contracts:

- Permission: 沿用文档创建调用方权限。
- Status codes/errors: 缺失/未确认/冲突 due 返回 409 且文档事务回滚；成功沿用 201。
- Response envelope: 沿用调用端包络。
- SQLite: app-side date handling；无 PG-only SQL。
- Simplified Chinese UI: N/A。

Required verification:

- RED/GREEN behavior: `cd backend && .venv/bin/pytest -q tests/test_addgap_oa_deadline_fail_closed.py`
- Scoped Ruff: `cd backend && .venv/bin/ruff check --fix app/modules/tasks/task_generation_service.py tests/test_addgap_oa_deadline_fail_closed.py && .venv/bin/ruff format app/modules/tasks/task_generation_service.py tests/test_addgap_oa_deadline_fail_closed.py && .venv/bin/ruff check app/modules/tasks/task_generation_service.py tests/test_addgap_oa_deadline_fail_closed.py`
- Scope: `git diff --check -- backend/app/modules/tasks/task_generation_service.py backend/tests/test_addgap_oa_deadline_fail_closed.py`
- Evidence: initialize/finalize with `./scripts/evidence_run.sh FPMS-ADDGAP-OA-DEADLINE-FAIL-CLOSED-20260710-01 <step> <command...>`, then run `./scripts/task_validate.sh FPMS-ADDGAP-OA-DEADLINE-FAIL-CLOSED-20260710-01`.

Done definition: RED evidence exists where applicable; minimum implementation is GREEN; scoped lint/type/build/test and scope diff pass; required dirty-baseline and completion artifacts exist under `artifacts/FPMS-ADDGAP-OA-DEADLINE-FAIL-CLOSED-20260710-01/`; `./scripts/task_validate.sh FPMS-ADDGAP-OA-DEADLINE-FAIL-CLOSED-20260710-01` returns 0; exact closure is complete; explicit non-closure is respected. Otherwise status is FAIL or BLOCKED, never PASS.

### 28 — `FPMS-ADDGAP-DOCUMENT-DEADLINE-IMPACT-PREVIEW-20260710-01`

- Task file: `tasks/additional_gaps/FPMS-ADDGAP-DOCUMENT-DEADLINE-IMPACT-PREVIEW-20260710-01.md`
- Wave: 6
- Owner role: Backend Developer / worker
- Exact closure: impact preview 显示 structured due lineage，缺确认时返回明确 409 blocker。
- Explicit non-closure: 不写文档/任务，不改变 create/update，不提供推测日期。
- Dependencies: 22, 27
- Remaining follow-up task IDs: 30
- Shared ownership decision: only the source paths in the exact allowlist below; serialize any repeated path per approved plan.

Exact allowlist:

- `backend/app/modules/documents/service.py`
- `backend/app/modules/documents/schemas.py`
- `backend/app/modules/documents/api.py`
- `backend/tests/test_addgap_document_deadline_impact_preview.py`
- `tasks/additional_gaps/FPMS-ADDGAP-DOCUMENT-DEADLINE-IMPACT-PREVIEW-20260710-01.md`
- `artifacts/FPMS-ADDGAP-DOCUMENT-DEADLINE-IMPACT-PREVIEW-20260710-01/**`

Runtime contracts:

- Permission: Doc.Create，函数参数 Depends 注入。
- Status codes/errors: POST 200 preview；缺确认/配置 409；shape 422；业务字段 400。
- Response envelope: 扩展既有 impact preview 模型，不发明外层 envelope。
- SQLite: 只读/纯计算。
- Simplified Chinese UI: N/A。

Required verification:

- RED/GREEN behavior: `cd backend && .venv/bin/pytest -q tests/test_addgap_document_deadline_impact_preview.py`
- Scoped Ruff: `cd backend && .venv/bin/ruff check --fix app/modules/documents/service.py app/modules/documents/schemas.py app/modules/documents/api.py tests/test_addgap_document_deadline_impact_preview.py && .venv/bin/ruff format app/modules/documents/service.py app/modules/documents/schemas.py app/modules/documents/api.py tests/test_addgap_document_deadline_impact_preview.py && .venv/bin/ruff check app/modules/documents/service.py app/modules/documents/schemas.py app/modules/documents/api.py tests/test_addgap_document_deadline_impact_preview.py`
- Scope: `git diff --check -- backend/app/modules/documents/service.py backend/app/modules/documents/schemas.py backend/app/modules/documents/api.py backend/tests/test_addgap_document_deadline_impact_preview.py`
- Evidence: initialize/finalize with `./scripts/evidence_run.sh FPMS-ADDGAP-DOCUMENT-DEADLINE-IMPACT-PREVIEW-20260710-01 <step> <command...>`, then run `./scripts/task_validate.sh FPMS-ADDGAP-DOCUMENT-DEADLINE-IMPACT-PREVIEW-20260710-01`.

Done definition: RED evidence exists where applicable; minimum implementation is GREEN; scoped lint/type/build/test and scope diff pass; required dirty-baseline and completion artifacts exist under `artifacts/FPMS-ADDGAP-DOCUMENT-DEADLINE-IMPACT-PREVIEW-20260710-01/`; `./scripts/task_validate.sh FPMS-ADDGAP-DOCUMENT-DEADLINE-IMPACT-PREVIEW-20260710-01` returns 0; exact closure is complete; explicit non-closure is respected. Otherwise status is FAIL or BLOCKED, never PASS.

### 29 — `FPMS-ADDGAP-DOCUMENT-WIZARD-DEADLINE-BACKEND-20260710-01`

- Task file: `tasks/additional_gaps/FPMS-ADDGAP-DOCUMENT-WIZARD-DEADLINE-BACKEND-20260710-01.md`
- Wave: 6
- Owner role: Backend Developer / worker
- Exact closure: wizard schemas/service 接受并逐行保存 structured due/source/write-status。
- Explicit non-closure: 不实现前端字段，不改变模板列表分页，不允许 LEGACY_UNVERIFIED 写入。
- Dependencies: 22, 24, 27
- Remaining follow-up task IDs: 31
- Shared ownership decision: only the source paths in the exact allowlist below; serialize any repeated path per approved plan.

Exact allowlist:

- `backend/app/modules/documents/schemas.py`
- `backend/app/modules/documents/service.py`
- `backend/tests/test_addgap_document_wizard_deadline_backend.py`
- `tasks/additional_gaps/FPMS-ADDGAP-DOCUMENT-WIZARD-DEADLINE-BACKEND-20260710-01.md`
- `artifacts/FPMS-ADDGAP-DOCUMENT-WIZARD-DEADLINE-BACKEND-20260710-01/**`

Runtime contracts:

- Permission: 沿用 Doc.Create。
- Status codes/errors: 成功沿用 wizard 201/既有合同；shape 422；业务 400；缺确认/配置 409 且原子回滚。
- Response envelope: 沿用 wizard 结果包络。
- SQLite: 逐行保存仍在受控事务内，不依赖 RETURNING。
- Simplified Chinese UI: N/A。

Required verification:

- RED/GREEN behavior: `cd backend && .venv/bin/pytest -q tests/test_addgap_document_wizard_deadline_backend.py`
- Scoped Ruff: `cd backend && .venv/bin/ruff check --fix app/modules/documents/schemas.py app/modules/documents/service.py tests/test_addgap_document_wizard_deadline_backend.py && .venv/bin/ruff format app/modules/documents/schemas.py app/modules/documents/service.py tests/test_addgap_document_wizard_deadline_backend.py && .venv/bin/ruff check app/modules/documents/schemas.py app/modules/documents/service.py tests/test_addgap_document_wizard_deadline_backend.py`
- Scope: `git diff --check -- backend/app/modules/documents/schemas.py backend/app/modules/documents/service.py backend/tests/test_addgap_document_wizard_deadline_backend.py`
- Evidence: initialize/finalize with `./scripts/evidence_run.sh FPMS-ADDGAP-DOCUMENT-WIZARD-DEADLINE-BACKEND-20260710-01 <step> <command...>`, then run `./scripts/task_validate.sh FPMS-ADDGAP-DOCUMENT-WIZARD-DEADLINE-BACKEND-20260710-01`.

Done definition: RED evidence exists where applicable; minimum implementation is GREEN; scoped lint/type/build/test and scope diff pass; required dirty-baseline and completion artifacts exist under `artifacts/FPMS-ADDGAP-DOCUMENT-WIZARD-DEADLINE-BACKEND-20260710-01/`; `./scripts/task_validate.sh FPMS-ADDGAP-DOCUMENT-WIZARD-DEADLINE-BACKEND-20260710-01` returns 0; exact closure is complete; explicit non-closure is respected. Otherwise status is FAIL or BLOCKED, never PASS.

### 30 — `FPMS-ADDGAP-DOCUMENT-DEADLINE-CREATE-UI-20260710-01`

- Task file: `tasks/additional_gaps/FPMS-ADDGAP-DOCUMENT-DEADLINE-CREATE-UI-20260710-01.md`
- Wave: 6
- Owner role: Frontend Developer / worker
- Exact closure: DocumentCreate 提供简体中文截止日、来源、确认状态字段及影响提示。
- Explicit non-closure: 不实现 wizard/edit UI，不允许客户端绕过 backend fail-closed。
- Dependencies: 24, 28
- Remaining follow-up task IDs: 31, 32
- Shared ownership decision: only the source paths in the exact allowlist below; serialize any repeated path per approved plan.

Exact allowlist:

- `frontend/src/api/documents.ts`
- `frontend/src/api/documents.types.ts`
- `frontend/src/modules/documents/pages/DocumentCreate.vue`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/addgap-document-deadline-create-ui.spec.ts`
- `tasks/additional_gaps/FPMS-ADDGAP-DOCUMENT-DEADLINE-CREATE-UI-20260710-01.md`
- `artifacts/FPMS-ADDGAP-DOCUMENT-DEADLINE-CREATE-UI-20260710-01/**`

Runtime contracts:

- Permission: 消费 Doc.Create。
- Status codes/errors: 消费 preview 200/409 与 create 201/400/409/422。
- Response envelope: 消费 DocumentOut 和既有 preview 模型。
- SQLite: N/A。
- Simplified Chinese UI: 所有字段、提示、错误必须为简体中文。

Required verification:

- RED/GREEN behavior: `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npx playwright test src/tests/addgap-document-deadline-create-ui.spec.ts --workers=1`
- Frontend checks: `cd frontend && npm run lint && npm run typecheck`
- Scope: `git diff --check -- frontend/src/api/documents.ts frontend/src/api/documents.types.ts frontend/src/modules/documents/pages/DocumentCreate.vue FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/addgap-document-deadline-create-ui.spec.ts`
- Evidence: initialize/finalize with `./scripts/evidence_run.sh FPMS-ADDGAP-DOCUMENT-DEADLINE-CREATE-UI-20260710-01 <step> <command...>`, then run `./scripts/task_validate.sh FPMS-ADDGAP-DOCUMENT-DEADLINE-CREATE-UI-20260710-01`.

Done definition: RED evidence exists where applicable; minimum implementation is GREEN; scoped lint/type/build/test and scope diff pass; required dirty-baseline and completion artifacts exist under `artifacts/FPMS-ADDGAP-DOCUMENT-DEADLINE-CREATE-UI-20260710-01/`; `./scripts/task_validate.sh FPMS-ADDGAP-DOCUMENT-DEADLINE-CREATE-UI-20260710-01` returns 0; exact closure is complete; explicit non-closure is respected. Otherwise status is FAIL or BLOCKED, never PASS.

### 31 — `FPMS-ADDGAP-DOCUMENT-DEADLINE-WIZARD-UI-20260710-01`

- Task file: `tasks/additional_gaps/FPMS-ADDGAP-DOCUMENT-DEADLINE-WIZARD-UI-20260710-01.md`
- Wave: 6
- Owner role: Frontend Developer / worker
- Exact closure: DocumentWizard 每一行展示并持久化 structured due/source/write-status。
- Explicit non-closure: 不修改 backend contract，不重做 wizard 交互，不实现 edit UI。
- Dependencies: 29, 30
- Remaining follow-up task IDs: 32
- Shared ownership decision: only the source paths in the exact allowlist below; serialize any repeated path per approved plan.

Exact allowlist:

- `frontend/src/api/documents.ts`
- `frontend/src/api/documents.types.ts`
- `frontend/src/modules/documents/pages/DocumentWizard.vue`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/addgap-document-deadline-wizard-ui.spec.ts`
- `tasks/additional_gaps/FPMS-ADDGAP-DOCUMENT-DEADLINE-WIZARD-UI-20260710-01.md`
- `artifacts/FPMS-ADDGAP-DOCUMENT-DEADLINE-WIZARD-UI-20260710-01/**`

Runtime contracts:

- Permission: 消费 Doc.Create。
- Status codes/errors: 消费 wizard 成功合同及 400/409/422。
- Response envelope: 消费既有 wizard 结果。
- SQLite: N/A。
- Simplified Chinese UI: 所有逐行字段、阻断和错误必须为简体中文。

Required verification:

- RED/GREEN behavior: `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npx playwright test src/tests/addgap-document-deadline-wizard-ui.spec.ts --workers=1`
- Frontend checks: `cd frontend && npm run lint && npm run typecheck`
- Scope: `git diff --check -- frontend/src/api/documents.ts frontend/src/api/documents.types.ts frontend/src/modules/documents/pages/DocumentWizard.vue FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/addgap-document-deadline-wizard-ui.spec.ts`
- Evidence: initialize/finalize with `./scripts/evidence_run.sh FPMS-ADDGAP-DOCUMENT-DEADLINE-WIZARD-UI-20260710-01 <step> <command...>`, then run `./scripts/task_validate.sh FPMS-ADDGAP-DOCUMENT-DEADLINE-WIZARD-UI-20260710-01`.

Done definition: RED evidence exists where applicable; minimum implementation is GREEN; scoped lint/type/build/test and scope diff pass; required dirty-baseline and completion artifacts exist under `artifacts/FPMS-ADDGAP-DOCUMENT-DEADLINE-WIZARD-UI-20260710-01/`; `./scripts/task_validate.sh FPMS-ADDGAP-DOCUMENT-DEADLINE-WIZARD-UI-20260710-01` returns 0; exact closure is complete; explicit non-closure is respected. Otherwise status is FAIL or BLOCKED, never PASS.

### 32 — `FPMS-ADDGAP-DOCUMENT-DEADLINE-EDIT-UI-20260710-01`

- Task file: `tasks/additional_gaps/FPMS-ADDGAP-DOCUMENT-DEADLINE-EDIT-UI-20260710-01.md`
- Wave: 6
- Owner role: Frontend Developer / worker
- Exact closure: DocumentEdit 显示期限 lineage，可确认 missing/legacy 的同一日期，并将 confirmed date 保持只读。
- Explicit non-closure: 不提供已确认日期 override，不同步非 OA task，不改 create/wizard。
- Dependencies: 25, 26, 31
- Remaining follow-up task IDs: 46
- Shared ownership decision: only the source paths in the exact allowlist below; serialize any repeated path per approved plan.

Exact allowlist:

- `frontend/src/api/documents.ts`
- `frontend/src/api/documents.types.ts`
- `frontend/src/modules/documents/pages/DocumentEdit.vue`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/addgap-document-deadline-edit-ui.spec.ts`
- `tasks/additional_gaps/FPMS-ADDGAP-DOCUMENT-DEADLINE-EDIT-UI-20260710-01.md`
- `artifacts/FPMS-ADDGAP-DOCUMENT-DEADLINE-EDIT-UI-20260710-01/**`

Runtime contracts:

- Permission: 消费 Doc.Edit。
- Status codes/errors: 消费 update 200/400/409/422。
- Response envelope: 消费 DocumentOut。
- SQLite: N/A。
- Simplified Chinese UI: lineage、确认动作、只读原因及错误必须为简体中文。

Required verification:

- RED/GREEN behavior: `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npx playwright test src/tests/addgap-document-deadline-edit-ui.spec.ts --workers=1`
- Frontend checks: `cd frontend && npm run lint && npm run typecheck`
- Scope: `git diff --check -- frontend/src/api/documents.ts frontend/src/api/documents.types.ts frontend/src/modules/documents/pages/DocumentEdit.vue FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/addgap-document-deadline-edit-ui.spec.ts`
- Evidence: initialize/finalize with `./scripts/evidence_run.sh FPMS-ADDGAP-DOCUMENT-DEADLINE-EDIT-UI-20260710-01 <step> <command...>`, then run `./scripts/task_validate.sh FPMS-ADDGAP-DOCUMENT-DEADLINE-EDIT-UI-20260710-01`.

Done definition: RED evidence exists where applicable; minimum implementation is GREEN; scoped lint/type/build/test and scope diff pass; required dirty-baseline and completion artifacts exist under `artifacts/FPMS-ADDGAP-DOCUMENT-DEADLINE-EDIT-UI-20260710-01/`; `./scripts/task_validate.sh FPMS-ADDGAP-DOCUMENT-DEADLINE-EDIT-UI-20260710-01` returns 0; exact closure is complete; explicit non-closure is respected. Otherwise status is FAIL or BLOCKED, never PASS.

### 33 — `FPMS-ADDGAP-NOTICE-OA-ACCEPTANCE-ACTIVATION-20260710-01`

- Task file: `tasks/additional_gaps/FPMS-ADDGAP-NOTICE-OA-ACCEPTANCE-ACTIVATION-20260710-01.md`
- Wave: 6B
- Owner role: Backend Developer / worker
- Exact closure: 只激活受理通知、精确首 OA、二/三/四/五次 OA 目录行，并绑定冻结语义。
- Explicit non-closure: UM/design OA、补正、复审、驳回、年费、PCT、授权及其他目录仍 reference-only。
- Dependencies: 18–29
- Remaining follow-up task IDs: 34, 46
- Shared ownership decision: only the source paths in the exact allowlist below; serialize any repeated path per approved plan.

Exact allowlist:

- `backend/app/modules/documents/official_notice_catalog.py`
- `backend/scripts/seed_dev.py`
- `backend/tests/test_addgap_notice_oa_acceptance_activation.py`
- `tasks/additional_gaps/FPMS-ADDGAP-NOTICE-OA-ACCEPTANCE-ACTIVATION-20260710-01.md`
- `artifacts/FPMS-ADDGAP-NOTICE-OA-ACCEPTANCE-ACTIVATION-20260710-01/**`

Runtime contracts:

- Permission: N/A（幂等 seed/catalog）。
- Status codes/errors: 无 confirmed due 的可执行 OA 创建由既有 gate 返回 409。
- Response envelope: 目录输出沿用现有 schema。
- SQLite: seed 幂等、bootstrap-safe。
- Simplified Chinese UI: N/A。

Required verification:

- RED/GREEN behavior: `cd backend && .venv/bin/pytest -q tests/test_addgap_notice_oa_acceptance_activation.py`
- Scoped Ruff: `cd backend && .venv/bin/ruff check --fix app/modules/documents/official_notice_catalog.py scripts/seed_dev.py tests/test_addgap_notice_oa_acceptance_activation.py && .venv/bin/ruff format app/modules/documents/official_notice_catalog.py scripts/seed_dev.py tests/test_addgap_notice_oa_acceptance_activation.py && .venv/bin/ruff check app/modules/documents/official_notice_catalog.py scripts/seed_dev.py tests/test_addgap_notice_oa_acceptance_activation.py`
- Scope: `git diff --check -- backend/app/modules/documents/official_notice_catalog.py backend/scripts/seed_dev.py backend/tests/test_addgap_notice_oa_acceptance_activation.py`
- Evidence: initialize/finalize with `./scripts/evidence_run.sh FPMS-ADDGAP-NOTICE-OA-ACCEPTANCE-ACTIVATION-20260710-01 <step> <command...>`, then run `./scripts/task_validate.sh FPMS-ADDGAP-NOTICE-OA-ACCEPTANCE-ACTIVATION-20260710-01`.

Done definition: RED evidence exists where applicable; minimum implementation is GREEN; scoped lint/type/build/test and scope diff pass; required dirty-baseline and completion artifacts exist under `artifacts/FPMS-ADDGAP-NOTICE-OA-ACCEPTANCE-ACTIVATION-20260710-01/`; `./scripts/task_validate.sh FPMS-ADDGAP-NOTICE-OA-ACCEPTANCE-ACTIVATION-20260710-01` returns 0; exact closure is complete; explicit non-closure is respected. Otherwise status is FAIL or BLOCKED, never PASS.

### 34 — `FPMS-ADDGAP-OA-ALIAS-REPLY-VALIDATION-20260710-01`

- Task file: `tasks/additional_gaps/FPMS-ADDGAP-OA-ALIAS-REPLY-VALIDATION-20260710-01.md`
- Wave: 6B
- Owner role: Backend Developer / worker
- Exact closure: OA_OUT reply validation 接受 resolver 标识的可执行 OA semantic aliases，而非仅 literal OA_IN。
- Explicit non-closure: 不接受 reference-only alias，不改变 OA_OUT 不关 task 的规则。
- Dependencies: 33
- Remaining follow-up task IDs: 46
- Shared ownership decision: only the source paths in the exact allowlist below; serialize any repeated path per approved plan.

Exact allowlist:

- `backend/app/modules/documents/service.py`
- `backend/tests/test_addgap_oa_alias_reply_validation.py`
- `tasks/additional_gaps/FPMS-ADDGAP-OA-ALIAS-REPLY-VALIDATION-20260710-01.md`
- `artifacts/FPMS-ADDGAP-OA-ALIAS-REPLY-VALIDATION-20260710-01/**`

Runtime contracts:

- Permission: 沿用 Doc.Create。
- Status codes/errors: 有效 alias 成功 201；reference-only/方向/语义冲突 400/409。
- Response envelope: 沿用 DocumentOut。
- SQLite: SQLite-safe 查询。
- Simplified Chinese UI: N/A。

Required verification:

- RED/GREEN behavior: `cd backend && .venv/bin/pytest -q tests/test_addgap_oa_alias_reply_validation.py`
- Scoped Ruff: `cd backend && .venv/bin/ruff check --fix app/modules/documents/service.py tests/test_addgap_oa_alias_reply_validation.py && .venv/bin/ruff format app/modules/documents/service.py tests/test_addgap_oa_alias_reply_validation.py && .venv/bin/ruff check app/modules/documents/service.py tests/test_addgap_oa_alias_reply_validation.py`
- Scope: `git diff --check -- backend/app/modules/documents/service.py backend/tests/test_addgap_oa_alias_reply_validation.py`
- Evidence: initialize/finalize with `./scripts/evidence_run.sh FPMS-ADDGAP-OA-ALIAS-REPLY-VALIDATION-20260710-01 <step> <command...>`, then run `./scripts/task_validate.sh FPMS-ADDGAP-OA-ALIAS-REPLY-VALIDATION-20260710-01`.

Done definition: RED evidence exists where applicable; minimum implementation is GREEN; scoped lint/type/build/test and scope diff pass; required dirty-baseline and completion artifacts exist under `artifacts/FPMS-ADDGAP-OA-ALIAS-REPLY-VALIDATION-20260710-01/`; `./scripts/task_validate.sh FPMS-ADDGAP-OA-ALIAS-REPLY-VALIDATION-20260710-01` returns 0; exact closure is complete; explicit non-closure is respected. Otherwise status is FAIL or BLOCKED, never PASS.

### 35 — `FPMS-ADDGAP-GRANT-LINEAGE-SCHEMA-20260710-01`

- Task file: `tasks/additional_gaps/FPMS-ADDGAP-GRANT-LINEAGE-SCHEMA-20260710-01.md`
- Wave: 7
- Owner role: Backend Developer / worker
- Exact closure: Phase 0-EXT 为 grant task 增加 source/deadline/supersede/request-key carriers，并在重复扫描通过后创建唯一索引。
- Explicit non-closure: 不创建 grant task，不激活授权目录，不修改用户现有 migration，不更改 workflow status。
- Dependencies: 22；执行前重新确认当前 Alembic head
- Remaining follow-up task IDs: 36, 38–42
- Shared ownership decision: only the source paths in the exact allowlist below; serialize any repeated path per approved plan.

Exact allowlist:

- `backend/alembic/versions/addgap_grant_lineage.py`
- `backend/app/modules/fees/models.py`
- `backend/tests/test_addgap_grant_lineage_schema.py`
- `tasks/additional_gaps/FPMS-ADDGAP-GRANT-LINEAGE-SCHEMA-20260710-01.md`
- `artifacts/FPMS-ADDGAP-GRANT-LINEAGE-SCHEMA-20260710-01/**`

Runtime contracts:

- Permission: N/A（schema）。
- Status codes/errors: N/A；重复/不可回填数据 fail-closed。
- Response envelope: N/A。
- SQLite: SQLite-safe 类型、CURRENT_TIMESTAMP、唯一索引；clean upgrade head。
- Simplified Chinese UI: N/A。

Required verification:

- RED/GREEN behavior: `cd backend && .venv/bin/pytest -q tests/test_addgap_grant_lineage_schema.py`
- Scoped Ruff: `cd backend && .venv/bin/ruff check --fix alembic/versions/addgap_grant_lineage.py app/modules/fees/models.py tests/test_addgap_grant_lineage_schema.py && .venv/bin/ruff format alembic/versions/addgap_grant_lineage.py app/modules/fees/models.py tests/test_addgap_grant_lineage_schema.py && .venv/bin/ruff check alembic/versions/addgap_grant_lineage.py app/modules/fees/models.py tests/test_addgap_grant_lineage_schema.py`
- Migration gate: `cd backend && PYTHONPATH=. .venv/bin/alembic heads && PYTHONPATH=. .venv/bin/alembic upgrade head` on a clean temporary SQLite database.
- Scope: `git diff --check -- backend/alembic/versions/addgap_grant_lineage.py backend/app/modules/fees/models.py backend/tests/test_addgap_grant_lineage_schema.py`
- Evidence: initialize/finalize with `./scripts/evidence_run.sh FPMS-ADDGAP-GRANT-LINEAGE-SCHEMA-20260710-01 <step> <command...>`, then run `./scripts/task_validate.sh FPMS-ADDGAP-GRANT-LINEAGE-SCHEMA-20260710-01`.

Done definition: RED evidence exists where applicable; minimum implementation is GREEN; scoped lint/type/build/test and scope diff pass; required dirty-baseline and completion artifacts exist under `artifacts/FPMS-ADDGAP-GRANT-LINEAGE-SCHEMA-20260710-01/`; `./scripts/task_validate.sh FPMS-ADDGAP-GRANT-LINEAGE-SCHEMA-20260710-01` returns 0; exact closure is complete; explicit non-closure is respected. Otherwise status is FAIL or BLOCKED, never PASS.

### 36 — `FPMS-ADDGAP-GRANT-SOURCE-DEADLINE-20260710-01`

- Task file: `tasks/additional_gaps/FPMS-ADDGAP-GRANT-SOURCE-DEADLINE-20260710-01.md`
- Wave: 7
- Owner role: Backend Developer / worker
- Exact closure: 首个可执行授权通知按 source key 创建/复用一个 grant task，必须使用 confirmed explicit due，并移除 +60 推算。
- Explicit non-closure: 不激活授权目录、不生成 FeeDraft、不处理 replacement、不修改 UI。
- Dependencies: 03, 22, 35
- Remaining follow-up task IDs: 37, 38, 39
- Shared ownership decision: only the source paths in the exact allowlist below; serialize any repeated path per approved plan.

Exact allowlist:

- `backend/app/modules/grant_fees/service.py`
- `backend/tests/test_addgap_grant_source_deadline.py`
- `tasks/additional_gaps/FPMS-ADDGAP-GRANT-SOURCE-DEADLINE-20260710-01.md`
- `artifacts/FPMS-ADDGAP-GRANT-SOURCE-DEADLINE-20260710-01/**`

Runtime contracts:

- Permission: 沿用调用方权限。
- Status codes/errors: 缺失/未确认 due 或不同 active source 409；同 source 幂等复用。
- Response envelope: 沿用 grant task 输出模型。
- SQLite: source unique 约束；不依赖 RETURNING。
- Simplified Chinese UI: N/A。

Required verification:

- RED/GREEN behavior: `cd backend && .venv/bin/pytest -q tests/test_addgap_grant_source_deadline.py`
- Scoped Ruff: `cd backend && .venv/bin/ruff check --fix app/modules/grant_fees/service.py tests/test_addgap_grant_source_deadline.py && .venv/bin/ruff format app/modules/grant_fees/service.py tests/test_addgap_grant_source_deadline.py && .venv/bin/ruff check app/modules/grant_fees/service.py tests/test_addgap_grant_source_deadline.py`
- Scope: `git diff --check -- backend/app/modules/grant_fees/service.py backend/tests/test_addgap_grant_source_deadline.py`
- Evidence: initialize/finalize with `./scripts/evidence_run.sh FPMS-ADDGAP-GRANT-SOURCE-DEADLINE-20260710-01 <step> <command...>`, then run `./scripts/task_validate.sh FPMS-ADDGAP-GRANT-SOURCE-DEADLINE-20260710-01`.

Done definition: RED evidence exists where applicable; minimum implementation is GREEN; scoped lint/type/build/test and scope diff pass; required dirty-baseline and completion artifacts exist under `artifacts/FPMS-ADDGAP-GRANT-SOURCE-DEADLINE-20260710-01/`; `./scripts/task_validate.sh FPMS-ADDGAP-GRANT-SOURCE-DEADLINE-20260710-01` returns 0; exact closure is complete; explicit non-closure is respected. Otherwise status is FAIL or BLOCKED, never PASS.

### 37 — `FPMS-ADDGAP-GRANT-AUTO-DRAFT-GATE-20260710-01`

- Task file: `tasks/additional_gaps/FPMS-ADDGAP-GRANT-AUTO-DRAFT-GATE-20260710-01.md`
- Wave: 7
- Owner role: Backend Developer / worker
- Exact closure: 授权通知登记在客户指示前不再自动生成 generic zero-value FeeDraft。
- Explicit non-closure: 不改变其他文档类型 B3 fee linking，不实现客户指示 workflow，不删除既有 fee draft。
- Dependencies: 03, 36
- Remaining follow-up task IDs: 38, 46
- Shared ownership decision: only the source paths in the exact allowlist below; serialize any repeated path per approved plan.

Exact allowlist:

- `backend/app/modules/documents/fee_linking_service.py`
- `backend/tests/test_addgap_grant_auto_draft_gate.py`
- `tasks/additional_gaps/FPMS-ADDGAP-GRANT-AUTO-DRAFT-GATE-20260710-01.md`
- `artifacts/FPMS-ADDGAP-GRANT-AUTO-DRAFT-GATE-20260710-01/**`

Runtime contracts:

- Permission: 沿用 Doc.Create。
- Status codes/errors: 授权文档创建成功但无零金额草稿；其他类型状态不变。
- Response envelope: 沿用调用端响应。
- SQLite: 校验/分支在现有事务内。
- Simplified Chinese UI: N/A。

Required verification:

- RED/GREEN behavior: `cd backend && .venv/bin/pytest -q tests/test_addgap_grant_auto_draft_gate.py`
- Scoped Ruff: `cd backend && .venv/bin/ruff check --fix app/modules/documents/fee_linking_service.py tests/test_addgap_grant_auto_draft_gate.py && .venv/bin/ruff format app/modules/documents/fee_linking_service.py tests/test_addgap_grant_auto_draft_gate.py && .venv/bin/ruff check app/modules/documents/fee_linking_service.py tests/test_addgap_grant_auto_draft_gate.py`
- Scope: `git diff --check -- backend/app/modules/documents/fee_linking_service.py backend/tests/test_addgap_grant_auto_draft_gate.py`
- Evidence: initialize/finalize with `./scripts/evidence_run.sh FPMS-ADDGAP-GRANT-AUTO-DRAFT-GATE-20260710-01 <step> <command...>`, then run `./scripts/task_validate.sh FPMS-ADDGAP-GRANT-AUTO-DRAFT-GATE-20260710-01`.

Done definition: RED evidence exists where applicable; minimum implementation is GREEN; scoped lint/type/build/test and scope diff pass; required dirty-baseline and completion artifacts exist under `artifacts/FPMS-ADDGAP-GRANT-AUTO-DRAFT-GATE-20260710-01/`; `./scripts/task_validate.sh FPMS-ADDGAP-GRANT-AUTO-DRAFT-GATE-20260710-01` returns 0; exact closure is complete; explicit non-closure is respected. Otherwise status is FAIL or BLOCKED, never PASS.

### 38 — `FPMS-ADDGAP-NOTICE-GRANT-ACTIVATION-20260710-01`

- Task file: `tasks/additional_gaps/FPMS-ADDGAP-NOTICE-GRANT-ACTIVATION-20260710-01.md`
- Wave: 7
- Owner role: Backend Developer / worker
- Exact closure: 仅在 lineage/due/draft gates 完成后激活“授权通知书-电子”并绑定冻结 grant 语义。
- Explicit non-closure: 不激活其他授权别名、办登/年费/PCT/复审目录，不改变 deadline 规则。
- Dependencies: 35–37
- Remaining follow-up task IDs: 39, 46
- Shared ownership decision: only the source paths in the exact allowlist below; serialize any repeated path per approved plan.

Exact allowlist:

- `backend/app/modules/documents/official_notice_catalog.py`
- `backend/scripts/seed_dev.py`
- `backend/tests/test_addgap_notice_grant_activation.py`
- `tasks/additional_gaps/FPMS-ADDGAP-NOTICE-GRANT-ACTIVATION-20260710-01.md`
- `artifacts/FPMS-ADDGAP-NOTICE-GRANT-ACTIVATION-20260710-01/**`

Runtime contracts:

- Permission: N/A（幂等 seed/catalog）。
- Status codes/errors: 缺 confirmed due 的创建由 gate 409；合法创建沿用 201。
- Response envelope: 目录输出沿用既有 schema。
- SQLite: seed 幂等、bootstrap-safe。
- Simplified Chinese UI: N/A。

Required verification:

- RED/GREEN behavior: `cd backend && .venv/bin/pytest -q tests/test_addgap_notice_grant_activation.py`
- Scoped Ruff: `cd backend && .venv/bin/ruff check --fix app/modules/documents/official_notice_catalog.py scripts/seed_dev.py tests/test_addgap_notice_grant_activation.py && .venv/bin/ruff format app/modules/documents/official_notice_catalog.py scripts/seed_dev.py tests/test_addgap_notice_grant_activation.py && .venv/bin/ruff check app/modules/documents/official_notice_catalog.py scripts/seed_dev.py tests/test_addgap_notice_grant_activation.py`
- Scope: `git diff --check -- backend/app/modules/documents/official_notice_catalog.py backend/scripts/seed_dev.py backend/tests/test_addgap_notice_grant_activation.py`
- Evidence: initialize/finalize with `./scripts/evidence_run.sh FPMS-ADDGAP-NOTICE-GRANT-ACTIVATION-20260710-01 <step> <command...>`, then run `./scripts/task_validate.sh FPMS-ADDGAP-NOTICE-GRANT-ACTIVATION-20260710-01`.

Done definition: RED evidence exists where applicable; minimum implementation is GREEN; scoped lint/type/build/test and scope diff pass; required dirty-baseline and completion artifacts exist under `artifacts/FPMS-ADDGAP-NOTICE-GRANT-ACTIVATION-20260710-01/`; `./scripts/task_validate.sh FPMS-ADDGAP-NOTICE-GRANT-ACTIVATION-20260710-01` returns 0; exact closure is complete; explicit non-closure is respected. Otherwise status is FAIL or BLOCKED, never PASS.

### 39 — `FPMS-ADDGAP-GRANT-REPLACEMENT-SERVICE-20260710-01`

- Task file: `tasks/additional_gaps/FPMS-ADDGAP-GRANT-REPLACEMENT-SERVICE-20260710-01.md`
- Wave: 7
- Owner role: Backend Developer / worker
- Exact closure: 原子服务按 request key/reason 创建或复用 replacement notice/task，并 supersede 旧 task。
- Explicit non-closure: 不新增 API/UI，不允许普通文档创建隐式替换，不改变 workflow status 与 lineage_status 的分离。
- Dependencies: 02, 22, 35–38
- Remaining follow-up task IDs: 40–44
- Shared ownership decision: only the source paths in the exact allowlist below; serialize any repeated path per approved plan.

Exact allowlist:

- `backend/app/modules/grant_fees/service.py`
- `backend/app/modules/documents/service.py`
- `backend/tests/test_addgap_grant_replacement_service.py`
- `tasks/additional_gaps/FPMS-ADDGAP-GRANT-REPLACEMENT-SERVICE-20260710-01.md`
- `artifacts/FPMS-ADDGAP-GRANT-REPLACEMENT-SERVICE-20260710-01/**`

Runtime contracts:

- Permission: N/A（API 后续同时要求 GrantFeeTask.Write 与 Doc.Create）。
- Status codes/errors: 旧 task 不存在 404；业务 shape 400；语义/lineage/idempotency 冲突 409；成功幂等。
- Response envelope: 返回 composite replacement 所需实体。
- SQLite: 单事务、request key 唯一、flush 取 PK。
- Simplified Chinese UI: N/A。

Required verification:

- RED/GREEN behavior: `cd backend && .venv/bin/pytest -q tests/test_addgap_grant_replacement_service.py`
- Scoped Ruff: `cd backend && .venv/bin/ruff check --fix app/modules/grant_fees/service.py app/modules/documents/service.py tests/test_addgap_grant_replacement_service.py && .venv/bin/ruff format app/modules/grant_fees/service.py app/modules/documents/service.py tests/test_addgap_grant_replacement_service.py && .venv/bin/ruff check app/modules/grant_fees/service.py app/modules/documents/service.py tests/test_addgap_grant_replacement_service.py`
- Scope: `git diff --check -- backend/app/modules/grant_fees/service.py backend/app/modules/documents/service.py backend/tests/test_addgap_grant_replacement_service.py`
- Evidence: initialize/finalize with `./scripts/evidence_run.sh FPMS-ADDGAP-GRANT-REPLACEMENT-SERVICE-20260710-01 <step> <command...>`, then run `./scripts/task_validate.sh FPMS-ADDGAP-GRANT-REPLACEMENT-SERVICE-20260710-01`.

Done definition: RED evidence exists where applicable; minimum implementation is GREEN; scoped lint/type/build/test and scope diff pass; required dirty-baseline and completion artifacts exist under `artifacts/FPMS-ADDGAP-GRANT-REPLACEMENT-SERVICE-20260710-01/`; `./scripts/task_validate.sh FPMS-ADDGAP-GRANT-REPLACEMENT-SERVICE-20260710-01` returns 0; exact closure is complete; explicit non-closure is respected. Otherwise status is FAIL or BLOCKED, never PASS.

### 40 — `FPMS-ADDGAP-GRANT-REPLACEMENT-API-20260710-01`

- Task file: `tasks/additional_gaps/FPMS-ADDGAP-GRANT-REPLACEMENT-API-20260710-01.md`
- Wave: 7
- Owner role: Backend Developer / worker
- Exact closure: 新增 POST /grant-fee-tasks/{task_id}/replacement-notice，接受 nested document/reason/idempotency key 并返回 composite existing/new 结果。
- Explicit non-closure: 不修改 replacement service 规则，不新增第二端点，不重接已接 router。
- Dependencies: 39
- Remaining follow-up task IDs: 41, 44
- Shared ownership decision: only the source paths in the exact allowlist below; serialize any repeated path per approved plan.

Exact allowlist:

- `backend/app/modules/grant_fees/schemas.py`
- `backend/app/modules/grant_fees/api.py`
- `backend/app/modules/documents/schemas.py`
- `backend/app/modules/documents/api.py`
- `backend/tests/test_addgap_grant_replacement_api.py`
- `tasks/additional_gaps/FPMS-ADDGAP-GRANT-REPLACEMENT-API-20260710-01.md`
- `artifacts/FPMS-ADDGAP-GRANT-REPLACEMENT-API-20260710-01/**`

Runtime contracts:

- Permission: GrantFeeTask.Write 与 Doc.Create，均以函数参数 Depends 注入。
- Status codes/errors: POST 200；404 old task；400 business shape；409 semantics/lineage/idempotency；422 payload。
- Response envelope: GrantFeeTaskReplacementNoticeOut，明确 existing/new，不发明外层 envelope。
- SQLite: 调用原子 SQLite-safe service。
- Simplified Chinese UI: N/A。

Required verification:

- RED/GREEN behavior: `cd backend && .venv/bin/pytest -q tests/test_addgap_grant_replacement_api.py`
- Scoped Ruff: `cd backend && .venv/bin/ruff check --fix app/modules/grant_fees/schemas.py app/modules/grant_fees/api.py app/modules/documents/schemas.py app/modules/documents/api.py tests/test_addgap_grant_replacement_api.py && .venv/bin/ruff format app/modules/grant_fees/schemas.py app/modules/grant_fees/api.py app/modules/documents/schemas.py app/modules/documents/api.py tests/test_addgap_grant_replacement_api.py && .venv/bin/ruff check app/modules/grant_fees/schemas.py app/modules/grant_fees/api.py app/modules/documents/schemas.py app/modules/documents/api.py tests/test_addgap_grant_replacement_api.py`
- Scope: `git diff --check -- backend/app/modules/grant_fees/schemas.py backend/app/modules/grant_fees/api.py backend/app/modules/documents/schemas.py backend/app/modules/documents/api.py backend/tests/test_addgap_grant_replacement_api.py`
- Evidence: initialize/finalize with `./scripts/evidence_run.sh FPMS-ADDGAP-GRANT-REPLACEMENT-API-20260710-01 <step> <command...>`, then run `./scripts/task_validate.sh FPMS-ADDGAP-GRANT-REPLACEMENT-API-20260710-01`.

Done definition: RED evidence exists where applicable; minimum implementation is GREEN; scoped lint/type/build/test and scope diff pass; required dirty-baseline and completion artifacts exist under `artifacts/FPMS-ADDGAP-GRANT-REPLACEMENT-API-20260710-01/`; `./scripts/task_validate.sh FPMS-ADDGAP-GRANT-REPLACEMENT-API-20260710-01` returns 0; exact closure is complete; explicit non-closure is respected. Otherwise status is FAIL or BLOCKED, never PASS.

### 41 — `FPMS-ADDGAP-GRANT-LIST-LINEAGE-PROJECTION-20260710-01`

- Task file: `tasks/additional_gaps/FPMS-ADDGAP-GRANT-LIST-LINEAGE-PROJECTION-20260710-01.md`
- Wave: 7
- Owner role: Backend Developer / worker
- Exact closure: grant list response 增加独立 lineage fields，不改变 workflow state/status。
- Explicit non-closure: 不改变 state action 可用性、不实现 UI、不合并 lineage_status 与 workflow status。
- Dependencies: 35–40
- Remaining follow-up task IDs: 42, 43
- Shared ownership decision: only the source paths in the exact allowlist below; serialize any repeated path per approved plan.

Exact allowlist:

- `backend/app/modules/grant_fees/service.py`
- `backend/app/modules/grant_fees/schemas.py`
- `backend/tests/test_addgap_grant_list_lineage_projection.py`
- `tasks/additional_gaps/FPMS-ADDGAP-GRANT-LIST-LINEAGE-PROJECTION-20260710-01.md`
- `artifacts/FPMS-ADDGAP-GRANT-LIST-LINEAGE-PROJECTION-20260710-01/**`

Runtime contracts:

- Permission: 沿用 GrantFeeTask.Read。
- Status codes/errors: GET 200；GET 无 body。
- Response envelope: 扩展既有 grant list item/model。
- SQLite: 只读 SQLite-safe projection。
- Simplified Chinese UI: N/A。

Required verification:

- RED/GREEN behavior: `cd backend && .venv/bin/pytest -q tests/test_addgap_grant_list_lineage_projection.py`
- Scoped Ruff: `cd backend && .venv/bin/ruff check --fix app/modules/grant_fees/service.py app/modules/grant_fees/schemas.py tests/test_addgap_grant_list_lineage_projection.py && .venv/bin/ruff format app/modules/grant_fees/service.py app/modules/grant_fees/schemas.py tests/test_addgap_grant_list_lineage_projection.py && .venv/bin/ruff check app/modules/grant_fees/service.py app/modules/grant_fees/schemas.py tests/test_addgap_grant_list_lineage_projection.py`
- Scope: `git diff --check -- backend/app/modules/grant_fees/service.py backend/app/modules/grant_fees/schemas.py backend/tests/test_addgap_grant_list_lineage_projection.py`
- Evidence: initialize/finalize with `./scripts/evidence_run.sh FPMS-ADDGAP-GRANT-LIST-LINEAGE-PROJECTION-20260710-01 <step> <command...>`, then run `./scripts/task_validate.sh FPMS-ADDGAP-GRANT-LIST-LINEAGE-PROJECTION-20260710-01`.

Done definition: RED evidence exists where applicable; minimum implementation is GREEN; scoped lint/type/build/test and scope diff pass; required dirty-baseline and completion artifacts exist under `artifacts/FPMS-ADDGAP-GRANT-LIST-LINEAGE-PROJECTION-20260710-01/`; `./scripts/task_validate.sh FPMS-ADDGAP-GRANT-LIST-LINEAGE-PROJECTION-20260710-01` returns 0; exact closure is complete; explicit non-closure is respected. Otherwise status is FAIL or BLOCKED, never PASS.

### 42 — `FPMS-ADDGAP-GRANT-STATE-LINEAGE-GATE-20260710-01`

- Task file: `tasks/additional_gaps/FPMS-ADDGAP-GRANT-STATE-LINEAGE-GATE-20260710-01.md`
- Wave: 7
- Owner role: Backend Developer / worker
- Exact closure: grant state response 暴露 lineage，并对 legacy/superseded task 移除状态变更 actions。
- Explicit non-closure: 不更改 workflow state 值、不实现 UI、不自动迁移 legacy task。
- Dependencies: 41
- Remaining follow-up task IDs: 43, 44
- Shared ownership decision: only the source paths in the exact allowlist below; serialize any repeated path per approved plan.

Exact allowlist:

- `backend/app/modules/grant_fees/service.py`
- `backend/app/modules/grant_fees/schemas.py`
- `backend/tests/test_addgap_grant_state_lineage_gate.py`
- `tasks/additional_gaps/FPMS-ADDGAP-GRANT-STATE-LINEAGE-GATE-20260710-01.md`
- `artifacts/FPMS-ADDGAP-GRANT-STATE-LINEAGE-GATE-20260710-01/**`

Runtime contracts:

- Permission: 沿用 GrantFeeTask.Read/Write。
- Status codes/errors: GET 200；被 gate 的写动作保持明确 409。
- Response envelope: 扩展既有 state response。
- SQLite: 只读 lineage 判断，SQLite-safe。
- Simplified Chinese UI: N/A。

Required verification:

- RED/GREEN behavior: `cd backend && .venv/bin/pytest -q tests/test_addgap_grant_state_lineage_gate.py`
- Scoped Ruff: `cd backend && .venv/bin/ruff check --fix app/modules/grant_fees/service.py app/modules/grant_fees/schemas.py tests/test_addgap_grant_state_lineage_gate.py && .venv/bin/ruff format app/modules/grant_fees/service.py app/modules/grant_fees/schemas.py tests/test_addgap_grant_state_lineage_gate.py && .venv/bin/ruff check app/modules/grant_fees/service.py app/modules/grant_fees/schemas.py tests/test_addgap_grant_state_lineage_gate.py`
- Scope: `git diff --check -- backend/app/modules/grant_fees/service.py backend/app/modules/grant_fees/schemas.py backend/tests/test_addgap_grant_state_lineage_gate.py`
- Evidence: initialize/finalize with `./scripts/evidence_run.sh FPMS-ADDGAP-GRANT-STATE-LINEAGE-GATE-20260710-01 <step> <command...>`, then run `./scripts/task_validate.sh FPMS-ADDGAP-GRANT-STATE-LINEAGE-GATE-20260710-01`.

Done definition: RED evidence exists where applicable; minimum implementation is GREEN; scoped lint/type/build/test and scope diff pass; required dirty-baseline and completion artifacts exist under `artifacts/FPMS-ADDGAP-GRANT-STATE-LINEAGE-GATE-20260710-01/`; `./scripts/task_validate.sh FPMS-ADDGAP-GRANT-STATE-LINEAGE-GATE-20260710-01` returns 0; exact closure is complete; explicit non-closure is respected. Otherwise status is FAIL or BLOCKED, never PASS.

### 43 — `FPMS-ADDGAP-GRANT-LINEAGE-UI-20260710-01`

- Task file: `tasks/additional_gaps/FPMS-ADDGAP-GRANT-LINEAGE-UI-20260710-01.md`
- Wave: 7
- Owner role: Frontend Developer / worker
- Exact closure: GrantFeeTaskList 以简体中文展示 source/deadline/legacy/superseded lineage。
- Explicit non-closure: 不提供 replacement action，不改变 workflow status 显示语义，不修改 backend。
- Dependencies: 41, 42
- Remaining follow-up task IDs: 44
- Shared ownership decision: only the source paths in the exact allowlist below; serialize any repeated path per approved plan.

Exact allowlist:

- `frontend/src/api/grantFees.ts`
- `frontend/src/api/grantFees.types.ts`
- `frontend/src/modules/grantFees/pages/GrantFeeTaskList.vue`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/addgap-grant-lineage-ui.spec.ts`
- `tasks/additional_gaps/FPMS-ADDGAP-GRANT-LINEAGE-UI-20260710-01.md`
- `artifacts/FPMS-ADDGAP-GRANT-LINEAGE-UI-20260710-01/**`

Runtime contracts:

- Permission: 消费 GrantFeeTask.Read。
- Status codes/errors: 消费 GET 200；错误提示简体中文。
- Response envelope: 消费扩展后的 list/state 模型。
- SQLite: N/A。
- Simplified Chinese UI: 所有 lineage 标签、空态和提示必须为简体中文。

Required verification:

- RED/GREEN behavior: `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npx playwright test src/tests/addgap-grant-lineage-ui.spec.ts --workers=1`
- Frontend checks: `cd frontend && npm run lint && npm run typecheck`
- Scope: `git diff --check -- frontend/src/api/grantFees.ts frontend/src/api/grantFees.types.ts frontend/src/modules/grantFees/pages/GrantFeeTaskList.vue FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/addgap-grant-lineage-ui.spec.ts`
- Evidence: initialize/finalize with `./scripts/evidence_run.sh FPMS-ADDGAP-GRANT-LINEAGE-UI-20260710-01 <step> <command...>`, then run `./scripts/task_validate.sh FPMS-ADDGAP-GRANT-LINEAGE-UI-20260710-01`.

Done definition: RED evidence exists where applicable; minimum implementation is GREEN; scoped lint/type/build/test and scope diff pass; required dirty-baseline and completion artifacts exist under `artifacts/FPMS-ADDGAP-GRANT-LINEAGE-UI-20260710-01/`; `./scripts/task_validate.sh FPMS-ADDGAP-GRANT-LINEAGE-UI-20260710-01` returns 0; exact closure is complete; explicit non-closure is respected. Otherwise status is FAIL or BLOCKED, never PASS.

### 44 — `FPMS-ADDGAP-GRANT-REPLACEMENT-UI-20260710-01`

- Task file: `tasks/additional_gaps/FPMS-ADDGAP-GRANT-REPLACEMENT-UI-20260710-01.md`
- Wave: 7
- Owner role: Frontend Developer / worker
- Exact closure: GrantFeeTaskList 提供显式 replacement-notice 动作，录入 reason、request key、confirmed due。
- Explicit non-closure: 不允许 legacy/superseded task 发起替换，不改变普通状态动作，不修改 backend contract。
- Dependencies: 40, 43
- Remaining follow-up task IDs: 46
- Shared ownership decision: only the source paths in the exact allowlist below; serialize any repeated path per approved plan.

Exact allowlist:

- `frontend/src/api/grantFees.ts`
- `frontend/src/api/grantFees.types.ts`
- `frontend/src/modules/grantFees/pages/GrantFeeTaskList.vue`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/addgap-grant-replacement-ui.spec.ts`
- `tasks/additional_gaps/FPMS-ADDGAP-GRANT-REPLACEMENT-UI-20260710-01.md`
- `artifacts/FPMS-ADDGAP-GRANT-REPLACEMENT-UI-20260710-01/**`

Runtime contracts:

- Permission: 消费 GrantFeeTask.Write 与 Doc.Create。
- Status codes/errors: 消费 POST 200/400/404/409/422。
- Response envelope: 消费 GrantFeeTaskReplacementNoticeOut。
- SQLite: N/A。
- Simplified Chinese UI: 对话框、字段、确认、错误和成功反馈必须为简体中文。

Required verification:

- RED/GREEN behavior: `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npx playwright test src/tests/addgap-grant-replacement-ui.spec.ts --workers=1`
- Frontend checks: `cd frontend && npm run lint && npm run typecheck`
- Scope: `git diff --check -- frontend/src/api/grantFees.ts frontend/src/api/grantFees.types.ts frontend/src/modules/grantFees/pages/GrantFeeTaskList.vue FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/addgap-grant-replacement-ui.spec.ts`
- Evidence: initialize/finalize with `./scripts/evidence_run.sh FPMS-ADDGAP-GRANT-REPLACEMENT-UI-20260710-01 <step> <command...>`, then run `./scripts/task_validate.sh FPMS-ADDGAP-GRANT-REPLACEMENT-UI-20260710-01`.

Done definition: RED evidence exists where applicable; minimum implementation is GREEN; scoped lint/type/build/test and scope diff pass; required dirty-baseline and completion artifacts exist under `artifacts/FPMS-ADDGAP-GRANT-REPLACEMENT-UI-20260710-01/`; `./scripts/task_validate.sh FPMS-ADDGAP-GRANT-REPLACEMENT-UI-20260710-01` returns 0; exact closure is complete; explicit non-closure is respected. Otherwise status is FAIL or BLOCKED, never PASS.

### 45 — `FPMS-ADDGAP-MANIFEST-RELEASE-GATE-20260710-01`

- Task file: `tasks/additional_gaps/FPMS-ADDGAP-MANIFEST-RELEASE-GATE-20260710-01.md`
- Wave: 8
- Owner role: Tester / monitor
- Exact closure: release_gate.sh 支持 --manifest <file> 和可选 --exclude-task ID 验证列出的 task IDs，同时保留 no-arg 兼容行为。
- Explicit non-closure: 不运行/修复产品测试，不改变 task_validate.sh，不伪造任一 task 证据。
- Dependencies: Wave 0；必须在 Task 47 前执行
- Remaining follow-up task IDs: 47
- Shared ownership decision: only the source paths in the exact allowlist below; serialize any repeated path per approved plan.

Exact allowlist:

- `scripts/release_gate.sh`
- `backend/tests/test_addgap_manifest_release_gate.py`
- `tasks/additional_gaps/FPMS-ADDGAP-MANIFEST-RELEASE-GATE-20260710-01.md`
- `artifacts/FPMS-ADDGAP-MANIFEST-RELEASE-GATE-20260710-01/**`

Runtime contracts:

- Permission: N/A（本地 gate）。
- Status codes/errors: 进程 0 表示所选任务全部有效；任一缺失/FAIL/非法 manifest 非零。
- Response envelope: N/A。
- SQLite: 测试使用隔离临时 artifact fixtures，不访问共享 SQLite。
- Simplified Chinese UI: N/A。

Required verification:

- RED/GREEN behavior: `cd backend && .venv/bin/pytest -q tests/test_addgap_manifest_release_gate.py`
- Scoped Ruff: `cd backend && .venv/bin/ruff check --fix tests/test_addgap_manifest_release_gate.py && .venv/bin/ruff format tests/test_addgap_manifest_release_gate.py && .venv/bin/ruff check tests/test_addgap_manifest_release_gate.py`
- Scope: `git diff --check -- scripts/release_gate.sh backend/tests/test_addgap_manifest_release_gate.py`
- Evidence: initialize/finalize with `./scripts/evidence_run.sh FPMS-ADDGAP-MANIFEST-RELEASE-GATE-20260710-01 <step> <command...>`, then run `./scripts/task_validate.sh FPMS-ADDGAP-MANIFEST-RELEASE-GATE-20260710-01`.

Done definition: RED evidence exists where applicable; minimum implementation is GREEN; scoped lint/type/build/test and scope diff pass; required dirty-baseline and completion artifacts exist under `artifacts/FPMS-ADDGAP-MANIFEST-RELEASE-GATE-20260710-01/`; `./scripts/task_validate.sh FPMS-ADDGAP-MANIFEST-RELEASE-GATE-20260710-01` returns 0; exact closure is complete; explicit non-closure is respected. Otherwise status is FAIL or BLOCKED, never PASS.

### 46 — `FPMS-ADDGAP-FINAL-REAL-PATH-E2E-20260710-01`

- Task file: `tasks/additional_gaps/FPMS-ADDGAP-FINAL-REAL-PATH-E2E-20260710-01.md`
- Wave: 8
- Owner role: Frontend Developer / worker
- Exact closure: 新增并通过一个不依赖 enrichment 的真实用户路径 E2E，覆盖七个 GAP 的可观察结果。
- Explicit non-closure: 不修改任何产品源码，不替代各原子 task 测试，不通过直接数据库注入跳过 UI/API。
- Dependencies: 01–44 PASS
- Remaining follow-up task IDs: 47
- Shared ownership decision: only the source paths in the exact allowlist below; serialize any repeated path per approved plan.

Exact allowlist:

- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/addgap-final-real-path.spec.ts`
- `tasks/additional_gaps/FPMS-ADDGAP-FINAL-REAL-PATH-E2E-20260710-01.md`
- `artifacts/FPMS-ADDGAP-FINAL-REAL-PATH-E2E-20260710-01/**`

Runtime contracts:

- Permission: 通过真实登录/权限路径覆盖各既有权限。
- Status codes/errors: 按真实 API 合同断言 200/201 与 fail-closed 400/409/422；不得接受提前 close。
- Response envelope: 只消费已冻结的既有/扩展模型。
- SQLite: --workers=1；与其他 SQLite-writing tests 串行。
- Simplified Chinese UI: 所有被测用户可见文本必须为简体中文。

Required verification:

- RED/GREEN behavior: `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npx playwright test src/tests/addgap-final-real-path.spec.ts --workers=1`
- Scope: `git diff --check -- FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/addgap-final-real-path.spec.ts`
- Evidence: initialize/finalize with `./scripts/evidence_run.sh FPMS-ADDGAP-FINAL-REAL-PATH-E2E-20260710-01 <step> <command...>`, then run `./scripts/task_validate.sh FPMS-ADDGAP-FINAL-REAL-PATH-E2E-20260710-01`.

Done definition: RED evidence exists where applicable; minimum implementation is GREEN; scoped lint/type/build/test and scope diff pass; required dirty-baseline and completion artifacts exist under `artifacts/FPMS-ADDGAP-FINAL-REAL-PATH-E2E-20260710-01/`; `./scripts/task_validate.sh FPMS-ADDGAP-FINAL-REAL-PATH-E2E-20260710-01` returns 0; exact closure is complete; explicit non-closure is respected. Otherwise status is FAIL or BLOCKED, never PASS.

### 47 — `FPMS-ADDGAP-FINAL-CLOSE-AUDIT-20260710-01`

- Task file: `tasks/additional_gaps/FPMS-ADDGAP-FINAL-CLOSE-AUDIT-20260710-01.md`
- Wave: 8
- Owner role: Independent Reviewer / explorer
- Exact closure: 运行所有 task gates、全量检查和 manifest gate（先 exclude self），并产出七项 item-to-slice 最终 close audit。
- Explicit non-closure: 不修复产品代码、不扩大七个 GAP、不把代表性测试当作全部覆盖、不在任何 residual gap 非 None 时宣告完成。
- Dependencies: 01–46 PASS
- Remaining follow-up task IDs: None
- Shared ownership decision: only the source paths in the exact allowlist below; serialize any repeated path per approved plan.

Exact allowlist:

- `docs/reviews/fpms_additional_gap_mitigation_close_audit_20260710.md`
- `backend/tests/test_addgap_final_close_ledger_contract.py`
- `tasks/additional_gaps/FPMS-ADDGAP-FINAL-CLOSE-AUDIT-20260710-01.md`
- `artifacts/FPMS-ADDGAP-FINAL-CLOSE-AUDIT-20260710-01/**`

Runtime contracts:

- Permission: 审计所有函数参数权限注入；不变更权限注册表。
- Status codes/errors: 审计必须覆盖 200/201/204 body 语义及 400/401/403/404/409/422 合同。
- Response envelope: 审计既有响应包络一致性。
- SQLite: 串行运行全量 SQLite 测试；检查 migration/seed 兼容。
- Simplified Chinese UI: 审计触及页面全部为简体中文。

Required verification:

- Contract test: `cd backend && .venv/bin/pytest -q tests/test_addgap_final_close_ledger_contract.py`
- Full backend: `cd backend && .venv/bin/ruff check . && .venv/bin/pytest -q`
- Full frontend: `cd frontend && npm run lint && npm run typecheck && npm run build`
- Real path: `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npx playwright test src/tests/addgap-final-real-path.spec.ts --workers=1`
- Program gate before self-finalize: `./scripts/release_gate.sh --manifest tasks/batches/FPMS-ADDITIONAL-GAP-MITIGATION-20260710-01.md --exclude-task FPMS-ADDGAP-FINAL-CLOSE-AUDIT-20260710-01`
- After this task passes its own task gate, lead runs the same manifest gate without exclusion and stores output under the program artifact.
- Scope: `git diff --check -- docs/reviews/fpms_additional_gap_mitigation_close_audit_20260710.md backend/tests/test_addgap_final_close_ledger_contract.py`
- Evidence: initialize/finalize with `./scripts/evidence_run.sh FPMS-ADDGAP-FINAL-CLOSE-AUDIT-20260710-01 <step> <command...>`, then run `./scripts/task_validate.sh FPMS-ADDGAP-FINAL-CLOSE-AUDIT-20260710-01`.

Done definition: RED evidence exists where applicable; minimum implementation is GREEN; scoped lint/type/build/test and scope diff pass; required dirty-baseline and completion artifacts exist under `artifacts/FPMS-ADDGAP-FINAL-CLOSE-AUDIT-20260710-01/`; `./scripts/task_validate.sh FPMS-ADDGAP-FINAL-CLOSE-AUDIT-20260710-01` returns 0; exact closure is complete; explicit non-closure is respected. Otherwise status is FAIL or BLOCKED, never PASS.

## Batch close rule

Tasks 45–47 are program-level acceptance tasks for all seven GAPs. Task 47 first runs the manifest gate with itself excluded, finalizes its own evidence and task gate, and then the lead runs the manifest gate without exclusion over all 47 tasks. The Goal remains active unless all 47 tasks are PASS, the final real-path E2E and full checks pass, every GAP row in the final item-to-slice ledger is `covered`, and every residual gap is exactly `None`.
