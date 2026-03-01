# POST-ENHANCEMENT Atomic Tasks — Backend Batches

## 0. 执行协议（给 Agent Team）
- 单任务单责任：每次执行只拿 1 个 Task ID。
- 并行限制：仅允许文件 allowlist 不重叠任务并行。
- 强制遵循：`AGENTS.md` + SQLite PoC 兼容约束 + 统一权限注入规则。
- 每个任务交付必须包含：
  - 修改文件清单
  - 验证命令输出
  - 关键 API 状态码验证
  - `artifacts/<TASK-ID>/...` 证据

## 1. 批次总览（建议执行顺序）
1. BE-B0（契约与权限基线）
2. BE-B1（Schema/Foundation）
3. BE-B2（Annual Fee）
4. BE-B3（Dunning/Bad Debt）
5. BE-B4（Commission）
6. BE-B5（Consulting/Search + Expense）
7. BE-B6（回归与一致性硬化）

---

## BE-B0 — 契约与权限基线

### PE-BE-00-01 (service)
- 目标：扩展 CaseType/状态枚举，加入 `CONSULTING` / `SEARCH` 并补齐校验映射。
- Allowlist:
  - `backend/app/modules/cases/enums.py`
  - `backend/app/modules/cases/schemas.py`
- 依赖：无
- 验收：现有 case 创建/更新不回归；新 case type 可通过校验。
- 验证：`cd backend && ruff check . && pytest -q`

### PE-BE-00-02 (service)
- 目标：统一新增模块权限常量并写入 RBAC seed 字典。
- Allowlist:
  - `backend/app/modules/rbac/service.py`
  - `docs/permissions_matrix.md`
- 依赖：PE-BE-00-01
- 验收：Admin 角色自动拥有新增域权限；seed 幂等。
- 验证：`cd backend && pytest -q tests/test_system_params.py`

### PE-BE-00-03 (doc)
- 目标：定义新增 API 错误语义与响应 envelope 统一约束（面向后续任务）。
- Allowlist:
  - `docs/error_codes.md`
  - `docs/api_usage_guide.md`
- 依赖：无
- 验收：新增域错误码、状态码、envelope 示例完整。
- 验证：文档自检 + 链接可读。

---

## BE-B1 — Schema/Foundation（每任务一张表/一组紧耦合表）

### PE-BE-DB-01 (schema)
- 目标：新增 `T_Expense`（通用第三方支出）。
- Allowlist:
  - `backend/alembic/versions/<new>_create_t_expense.py`
  - `backend/app/modules/expenses/models.py`
- 依赖：PE-BE-00-01
- 验收：SQLite migrate 成功，模型可导入。
- 验证：`cd backend && alembic upgrade head && python3 -m py_compile app/modules/expenses/models.py`

### PE-BE-DB-02 (schema)
- 目标：新增 `T_PayList`（官费清单头）。
- Allowlist:
  - `backend/alembic/versions/<new>_create_t_pay_list.py`
  - `backend/app/modules/annuity/models.py`
- 依赖：PE-BE-DB-01
- 验收：表结构含状态/币种/日期/创建审计字段。
- 验证：`cd backend && alembic upgrade head`

### PE-BE-DB-03 (schema)
- 目标：新增 `T_GovPayment`（官费缴费明细）。
- Allowlist:
  - `backend/alembic/versions/<new>_create_t_gov_payment.py`
  - `backend/app/modules/annuity/models.py`
- 依赖：PE-BE-DB-02
- 验收：与 `T_PayList`/Case/FeeItem 外键正确。
- 验证：`cd backend && alembic upgrade head`

### PE-BE-DB-04 (schema)
- 目标：新增 `T_AnnuityTask`（年费任务）。
- Allowlist:
  - `backend/alembic/versions/<new>_create_t_annuity_task.py`
  - `backend/app/modules/annuity/models.py`
- 依赖：PE-BE-00-01
- 验收：支持年度、截止日、客户指示、通知状态字段。
- 验证：`cd backend && alembic upgrade head`

### PE-BE-DB-05 (schema)
- 目标：新增 `T_Dunning` + `T_DunningLine`。
- Allowlist:
  - `backend/alembic/versions/<new>_create_t_dunning.py`
  - `backend/app/modules/collections/models.py`
- 依赖：PE-BE-00-01
- 验收：支持多轮催款与账单快照。
- 验证：`cd backend && alembic upgrade head`

### PE-BE-DB-06 (schema)
- 目标：新增 `T_CommissionRule`。
- Allowlist:
  - `backend/alembic/versions/<new>_create_t_commission_rule.py`
  - `backend/app/modules/commission/models.py`
- 依赖：PE-BE-00-02
- 验收：规则支持 CaseType/FeeType/S1/S2/WaitPay/ForceSettle。
- 验证：`cd backend && alembic upgrade head`

### PE-BE-DB-07 (schema)
- 目标：新增 `T_Commission`。
- Allowlist:
  - `backend/alembic/versions/<new>_create_t_commission.py`
  - `backend/app/modules/commission/models.py`
- 依赖：PE-BE-DB-06
- 验收：支持 base fee、阶段金额、状态与可结算标志。
- 验证：`cd backend && alembic upgrade head`

### PE-BE-DB-08 (schema)
- 目标：新增 `T_CommissionSettlement` + `T_CommissionSettleLine`。
- Allowlist:
  - `backend/alembic/versions/<new>_create_t_commission_settlement.py`
  - `backend/app/modules/commission/models.py`
- 依赖：PE-BE-DB-07
- 验收：可支撑结算批次与明细关联。
- 验证：`cd backend && alembic upgrade head`

---

## BE-B2 — Annual Fee 生命周期

### PE-BE-AN-01 (service)
- 目标：实现年费任务提取服务（按到期区间/状态筛选）。
- Allowlist:
  - `backend/app/modules/annuity/service.py`
- 依赖：PE-BE-DB-04
- 验收：返回可分页任务列表，支持待处理筛选。
- 验证：`cd backend && pytest -q tests/test_b6_search_filters.py`

### PE-BE-AN-02 (endpoint)
- 目标：`GET /annuity/tasks`。
- Allowlist:
  - `backend/app/modules/annuity/api.py`
- 依赖：PE-BE-AN-01, PE-BE-00-02
- 验收：分页、过滤、权限与 envelope 符合规范。
- 验证：`cd backend && ruff check . && pytest -q`

### PE-BE-AN-03 (endpoint)
- 目标：`PUT /annuity/tasks/{task_id}/instruction`（客户指示录入）。
- Allowlist:
  - `backend/app/modules/annuity/api.py`
  - `backend/app/modules/annuity/service.py`
- 依赖：PE-BE-AN-02
- 验收：状态流转合法，400/404/409 语义正确。
- 验证：`cd backend && pytest -q`

### PE-BE-AN-04 (service)
- 目标：实现“年费任务→费用草单”生成服务。
- Allowlist:
  - `backend/app/modules/annuity/service.py`
- 依赖：PE-BE-AN-03
- 验收：支持 PayNextYear/草单幂等控制。
- 验证：`cd backend && pytest -q`

### PE-BE-AN-05 (endpoint)
- 目标：`POST /annuity/tasks/generate-drafts`。
- Allowlist:
  - `backend/app/modules/annuity/api.py`
- 依赖：PE-BE-AN-04
- 验收：批量生成结果返回成功/失败明细。
- 验证：`cd backend && pytest -q`

### PE-BE-AN-06 (endpoint)
- 目标：`POST /pay-lists/from-fee-items`（官费清单生成）。
- Allowlist:
  - `backend/app/modules/annuity/api.py`
  - `backend/app/modules/annuity/service.py`
- 依赖：PE-BE-DB-02, PE-BE-DB-03
- 验收：同一 client/currency 约束正确。
- 验证：`cd backend && pytest -q`

### PE-BE-AN-07 (endpoint)
- 目标：`POST /gov-payments`（官方缴费登记）。
- Allowlist:
  - `backend/app/modules/annuity/api.py`
  - `backend/app/modules/annuity/service.py`
- 依赖：PE-BE-AN-06
- 验收：可回写清单状态，支持重复保护。
- 验证：`cd backend && pytest -q`

---

## BE-B3 — Dunning / Bad Debt

### PE-BE-CL-01 (service)
- 目标：实现逾期账单筛选与催款批次生成服务。
- Allowlist:
  - `backend/app/modules/collections/service.py`
- 依赖：PE-BE-DB-05
- 验收：按客户+截止日聚合，生成头/行快照。
- 验证：`cd backend && pytest -q`

### PE-BE-CL-02 (endpoint)
- 目标：`POST /dunning`。
- Allowlist:
  - `backend/app/modules/collections/api.py`
- 依赖：PE-BE-CL-01
- 验收：创建催款批次并返回摘要。
- 验证：`cd backend && pytest -q`

### PE-BE-CL-03 (endpoint)
- 目标：`GET /dunning`（查询与分页）。
- Allowlist:
  - `backend/app/modules/collections/api.py`
- 依赖：PE-BE-CL-02
- 验收：支持轮次/状态/客户过滤。
- 验证：`cd backend && pytest -q`

### PE-BE-CL-04 (endpoint)
- 目标：`POST /bills/{bill_id}/bad-debt`。
- Allowlist:
  - `backend/app/modules/collections/api.py`
  - `backend/app/modules/collections/service.py`
- 依赖：PE-BE-CL-01
- 验收：仅允许未核销余额账单进入坏账。
- 验证：`cd backend && pytest -q`

### PE-BE-CL-05 (endpoint)
- 目标：`POST /bills/{bill_id}/bad-debt/restore`。
- Allowlist:
  - `backend/app/modules/collections/api.py`
  - `backend/app/modules/collections/service.py`
- 依赖：PE-BE-CL-04
- 验收：坏账恢复后状态一致。
- 验证：`cd backend && pytest -q`

---

## BE-B4 — Commission

### PE-BE-COM-01 (endpoint)
- 目标：`POST /commission/rules`。
- Allowlist:
  - `backend/app/modules/commission/api.py`
  - `backend/app/modules/commission/service.py`
- 依赖：PE-BE-DB-06
- 验收：规则唯一性与参数合法性校验完成。
- 验证：`cd backend && pytest -q`

### PE-BE-COM-02 (endpoint)
- 目标：`GET /commission/rules`。
- Allowlist:
  - `backend/app/modules/commission/api.py`
- 依赖：PE-BE-COM-01
- 验收：分页过滤与权限校验通过。
- 验证：`cd backend && pytest -q`

### PE-BE-COM-03 (endpoint)
- 目标：`PUT /commission/rules/{rule_id}`。
- Allowlist:
  - `backend/app/modules/commission/api.py`
  - `backend/app/modules/commission/service.py`
- 依赖：PE-BE-COM-02
- 验收：启停/比例/适用范围更新安全。
- 验证：`cd backend && pytest -q`

### PE-BE-COM-04 (service)
- 目标：实现账单生成触发提成记录服务。
- Allowlist:
  - `backend/app/modules/commission/service.py`
- 依赖：PE-BE-DB-07, PE-BE-COM-01
- 验收：根据规则生成/更新 `T_Commission`。
- 验证：`cd backend && pytest -q`

### PE-BE-COM-05 (service)
- 目标：在 billing 链路中接入提成服务 hook（不改变旧返回契约）。
- Allowlist:
  - `backend/app/modules/billing/service.py`
  - `backend/app/modules/commission/service.py`
- 依赖：PE-BE-COM-04
- 验收：账单生成后可写提成；失败不影响账单主事务需有明确策略。
- 验证：`cd backend && pytest -q tests/test_spec_alignment_e2e.py`

### PE-BE-COM-06 (service)
- 目标：实现 WaitPay/ForceSettle 可结算判定更新（offset/reverse 后重算）。
- Allowlist:
  - `backend/app/modules/commission/service.py`
  - `backend/app/modules/billing/service.py`
- 依赖：PE-BE-COM-05
- 验收：回款比例变化后提成状态可更新。
- 验证：`cd backend && pytest -q`

### PE-BE-COM-07 (endpoint)
- 目标：`GET /commission`（提成记录查询）。
- Allowlist:
  - `backend/app/modules/commission/api.py`
- 依赖：PE-BE-COM-06
- 验收：支持 agent/case/status/date 过滤。
- 验证：`cd backend && pytest -q`

### PE-BE-COM-08 (endpoint)
- 目标：`POST /commission/settlements`（创建结算批次）。
- Allowlist:
  - `backend/app/modules/commission/api.py`
  - `backend/app/modules/commission/service.py`
- 依赖：PE-BE-DB-08
- 验收：批次状态流转与唯一性通过。
- 验证：`cd backend && pytest -q`

### PE-BE-COM-09 (endpoint)
- 目标：`POST /commission/settlements/{id}/generate-lines`。
- Allowlist:
  - `backend/app/modules/commission/api.py`
  - `backend/app/modules/commission/service.py`
- 依赖：PE-BE-COM-08
- 验收：自动筛选可结算提成并落明细。
- 验证：`cd backend && pytest -q`

### PE-BE-COM-10 (endpoint)
- 目标：`GET /commission/reports/settlement`。
- Allowlist:
  - `backend/app/modules/commission/api.py`
  - `backend/app/modules/commission/service.py`
- 依赖：PE-BE-COM-09
- 验收：按代理人/案件/时间聚合统计。
- 验证：`cd backend && pytest -q`

---

## BE-B5 — Consulting/Search + Expense

### PE-BE-CS-01 (endpoint)
- 目标：`POST /consulting/cases`（或扩展 `/cases` 的 consulting/search 验证分支）。
- Allowlist:
  - `backend/app/modules/consulting/api.py`
  - `backend/app/modules/consulting/service.py`
  - `backend/app/modules/cases/service.py`
- 依赖：PE-BE-00-01
- 验收：可创建 CONSULTING/SEARCH 案件并校验专属字段。
- 验证：`cd backend && pytest -q`

### PE-BE-CS-02 (endpoint)
- 目标：`POST /expenses`（支出录入）。
- Allowlist:
  - `backend/app/modules/expenses/api.py`
  - `backend/app/modules/expenses/service.py`
- 依赖：PE-BE-DB-01
- 验收：支持 case/category/date/amount 校验。
- 验证：`cd backend && pytest -q`

### PE-BE-CS-03 (endpoint)
- 目标：`GET /expenses`（支出查询统计）。
- Allowlist:
  - `backend/app/modules/expenses/api.py`
  - `backend/app/modules/expenses/service.py`
- 依赖：PE-BE-CS-02
- 验收：支持按案件/类别/时间查询。
- 验证：`cd backend && pytest -q`

### PE-BE-CS-04 (service)
- 目标：实现顾问/检索服务费草单生成策略（固定/工时/混合）。
- Allowlist:
  - `backend/app/modules/consulting/service.py`
  - `backend/app/modules/fees/service.py`
- 依赖：PE-BE-CS-01
- 验收：草单明细金额可追溯计算。
- 验证：`cd backend && pytest -q`

### PE-BE-CS-05 (endpoint)
- 目标：`POST /consulting/fee-drafts`。
- Allowlist:
  - `backend/app/modules/consulting/api.py`
  - `backend/app/modules/consulting/service.py`
- 依赖：PE-BE-CS-04
- 验收：可生成 CONSULT_FEE/SEARCH_FEE 草单。
- 验证：`cd backend && pytest -q`

### PE-BE-CS-06 (service)
- 目标：顾问/检索账单生成时接入提成规则匹配。
- Allowlist:
  - `backend/app/modules/consulting/service.py`
  - `backend/app/modules/commission/service.py`
  - `backend/app/modules/billing/service.py`
- 依赖：PE-BE-COM-05, PE-BE-CS-05
- 验收：顾问/检索项目可写提成记录并进入结算候选。
- 验证：`cd backend && pytest -q`

---

## BE-B6 — 一致性硬化与测试补齐

### PE-BE-QA-01 (service)
- 目标：统一关键模块错误 envelope（避免裸 `HTTPException detail` 分叉）。
- Allowlist:
  - `backend/app/modules/cases/api.py`
  - `backend/app/modules/fees/api.py`
  - `backend/app/modules/billing/api.py`
- 依赖：全部功能批次完成后执行
- 验收：错误返回一致，前端解析统一。
- 验证：`cd backend && pytest -q`

### PE-BE-QA-02 (service)
- 目标：统一分页上限策略（`page_size le=100`）。
- Allowlist:
  - `backend/app/modules/*/api.py`（仅 list endpoint 参数）
- 依赖：PE-BE-QA-01
- 验收：所有列表端点具备 page_size 上限。
- 验证：`cd backend && pytest -q`

### PE-BE-TEST-01 (doc+test)
- 目标：新增 annuity/collections/commission/consulting 关键 E2E 测试。
- Allowlist:
  - `backend/tests/test_annuity_e2e.py`
  - `backend/tests/test_collections_e2e.py`
  - `backend/tests/test_commission_e2e.py`
  - `backend/tests/test_consulting_e2e.py`
- 依赖：B2-B5 完成
- 验收：关键路径全绿。
- 验证：`cd backend && pytest -q`

---

## 2. Router Wiring 原子任务（串行，避免冲突）

### PE-BE-WIRE-01 (endpoint)
- 目标：将新增模块 router 接入 `backend/app/api/router.py`（一次性）。
- Allowlist:
  - `backend/app/api/router.py`
- 依赖：至少一个新增模块 API 文件落地
- 验收：路由可被 `app/main.py` 正常加载。
- 验证：`cd backend && python3 -m py_compile app/api/router.py && pytest -q`

---

## 3. 每个任务统一验证脚本模板
```bash
./scripts/evidence_run.sh <TASK-ID> lint bash -lc "cd backend && ruff check ."
./scripts/evidence_run.sh <TASK-ID> fmt  bash -lc "cd backend && ruff format ."
./scripts/evidence_run.sh <TASK-ID> test bash -lc "cd backend && pytest -q"
./scripts/evidence_finalize.sh <TASK-ID>
./scripts/task_validate.sh <TASK-ID>
```

## 4. 多 Agent 分配建议
- 可并行：
  - DB 任务按“不同 migration 文件 + 不同模型文件”并行
  - API 任务按“不同模块 api.py”并行
- 必须串行：
  - `router.py` wiring
  - 同一 `api.py` 内多个 endpoint
  - Commission 与 Billing hook 任务（PE-BE-COM-05/06）
