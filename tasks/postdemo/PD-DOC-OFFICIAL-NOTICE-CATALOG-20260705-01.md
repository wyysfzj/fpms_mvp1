# PD-DOC-OFFICIAL-NOTICE-CATALOG-20260705-01 — 官方来文/官文代码目录补齐

## Story Shape Classification

- shared_file_density: Medium. Touches documents service/search and seed path only.
- prereq_dependency_density: Low. Existing `DocTemplate.input_fields` can carry official codes.
- be_fe_coupling: Low. Existing frontend template dropdown consumes `/doc-templates`.
- evidence_cost: Medium. Requires seed/search tests and task gate.
- chosen_runbook: `P0-prereq-heavy-story`

## Closure

补齐 `相关流程操作-20260526.docx` extracted `[P0101] TABLE 001` 的官方来文/官文代码清单，使系统 seeded `DocTemplate`/官方文书目录可覆盖客户清单，并且 `/api/v1/doc-templates` 可按名称或官文代码搜索到对应项。

## Non-Closure

不实现官方系统自动识别/自动下载，不改变 OA/CPC 提交流程，不把附件角色枚举当作官文目录，不新增数据库表或 migration。

## Allowlist

- `tasks/postdemo/PD-DOC-OFFICIAL-NOTICE-CATALOG-20260705-01.md`
- `backend/app/modules/documents/official_notice_catalog.py`
- `backend/app/modules/documents/service.py`
- `backend/scripts/seed_dev.py`
- `backend/tests/test_official_notice_catalog_seed.py`
- `artifacts/PD-DOC-OFFICIAL-NOTICE-CATALOG-20260705-01/**`

## Verification

- `cd backend && ruff check --fix app/modules/documents/official_notice_catalog.py app/modules/documents/service.py scripts/seed_dev.py tests/test_official_notice_catalog_seed.py`
- `cd backend && ruff format app/modules/documents/official_notice_catalog.py app/modules/documents/service.py scripts/seed_dev.py tests/test_official_notice_catalog_seed.py`
- `cd backend && ruff check app/modules/documents/official_notice_catalog.py app/modules/documents/service.py scripts/seed_dev.py tests/test_official_notice_catalog_seed.py`
- `cd backend && pytest tests/test_official_notice_catalog_seed.py -q`
- `./scripts/task_validate.sh PD-DOC-OFFICIAL-NOTICE-CATALOG-20260705-01`

## Done Definition

- Official catalog seed covers all 60 TABLE 001 rows.
- Key examples are present: `受理通知-电子/200101`, `补正通知/220704,200029,210302,220302,230301`, `第一次审查意见通知书/210401,210402`, `授权通知书-电子/200602`, `驳回决定/210407,200305,210408`, `年费缴费通知书/200701`, `复审通知书/200908A,200924`, `PCT电子提交收据`.
- `/doc-templates?q=<名称或官文代码>` can find seeded official notice entries.
- Existing `OA_IN`, `OA_OUT`, `ACCEPTANCE_NOTICE`, `GRANT_NOTICE`, `CLIENT_IN` behavior remains available.

## Follow-Up Task IDs

None.

