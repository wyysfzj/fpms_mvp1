# POST-ENHANCEMENT Plan — FPMS SPEC 2.0 Critical Gap Closure

## 1. 背景与目标
本计划用于关闭当前关键缺口：
- Commission（提成规则/提成记录/结算批次）
- Consulting & Search（顾问/检索项目全链路）
- Annual Fee Lifecycle（年登印费/年费全生命周期）
- Dunning & Bad Debt（催款/坏账）

核心目标：
1. 对齐 `docs/FPMS SPEC 2.0.md`（文档生成功能按当前约束可排除）
2. 不破坏已实现 MVP1 主链路
3. 前后端实现保持架构一致性、模块边界清晰、API 契约稳定
4. 全程符合现有 iron rules / quality gate

## 2. 适用规则（Iron Rules / Quality Gate）
执行时必须遵循：
- 仓库 `AGENTS.md`（一任务一责任、权限注入规范、状态码语义、响应风格）
- SQLite PoC 兼容要求（CURRENT_TIMESTAMP、外键开启、禁用 PG 方言特性、不依赖 RETURNING）
- 非破坏性变更原则（additive change only）
- 代码质量门禁：
  - `ruff check --fix .`
  - `ruff format .`
  - `ruff check .`
  - `cd frontend && npm run lint && npm run typecheck`
- 回归门禁：现有后端测试必须持续通过

## 3. 兼容性与不回归策略
1. API 兼容
- 不改现有 endpoint path / 方法 / 关键字段语义
- 新能力优先通过新增 endpoint 提供
- 旧 endpoint 只允许增加“可选联动”，默认行为不变

2. 数据兼容
- 新表/新索引/新字段都采用向前兼容迁移
- 不依赖 `alembic downgrade base`
- 迁移后 seed 脚本保持可重复执行（idempotent）

3. 前端兼容
- 既有页面路由不变
- 新页面独立挂载
- 统一沿用现有错误处理、请求拦截、分页模式

## 4. 目标架构（增量扩展）
后端新增业务域模块（vertical slice）：
- `app/modules/annuity/`：年登印费、年费任务、客户指示、通知状态
- `app/modules/collections/`：催款单、催款轮次、坏账标记/恢复
- `app/modules/commission/`：规则、记录、结算批次/明细
- `app/modules/consulting/`：顾问/检索项目专用流程
- `app/modules/expenses/`：第三方支出（供 FE/CS 共用）

前端新增模块：
- `frontend/src/modules/annuity/`
- `frontend/src/modules/collections/`
- `frontend/src/modules/commission/`
- `frontend/src/modules/consulting/`
- `frontend/src/modules/expenses/`

联动原则：
- API 仅编排，业务逻辑放 service
- 模块间通过 service 调用联动，避免 API 层强耦合

## 5. 分波次实施
### Wave 0 — 契约冻结与执行基线
- 冻结现有接口契约（防回归）
- 建立 Feature Flag（SystemParam）用于增量开关
- 输出 FR/US 追踪清单与执行顺序

### Wave 1 — Domain Foundation（Schema + Model + 基础读写）
- 建立缺失核心表：
  - `T_Expense`
  - `T_PayList`, `T_GovPayment`
  - `T_AnnuityTask`
  - `T_Dunning`, `T_DunningLine`
  - `T_CommissionRule`, `T_Commission`, `T_CommissionSettlement`, `T_CommissionSettleLine`
- 扩展 CaseType 支持 `CONSULTING/SEARCH` 及必要状态域

### Wave 2 — Annual Fee Lifecycle
- 年登印费/年费任务提取与状态流转
- 客户指示与通知状态
- 关联草单生成
- 关联官费清单与缴费登记

### Wave 3 — Dunning & Bad Debt
- 逾期筛选
- 催款单生成（多轮）
- 催款状态跟踪
- 坏账标记与恢复

### Wave 4 — Commission Engine
- 规则维护
- 账单/收款触发提成记录更新
- WaitPay / ForceSettle
- 结算批次与报表查询

### Wave 5 — Consulting/Search Full Chain
- 立案
- 内部任务
- 支出
- 服务费草单
- 账单、收款、提成纳入结算

### Wave 6 — Frontend Integration + E2E + Release Gate
- 页面与菜单接入
- 权限码前后端统一
- 完整回归与证据产出

## 6. API 契约统一规范
- 权限注入必须采用函数参数：
  - `_perm: None = Depends(require_perm("Title.Action"))`
- 错误语义统一：400/401/403/404/409/422
- 204 不返回 body，不声明 response_model
- 分页统一：`{items, page, page_size, total}`
- 错误 envelope 统一：`{"error": {"code", "message", "details"}}`

## 7. 多 Agent 执行编排建议
1. 并行原则
- 只并行“文件不重叠”任务
- 涉及同一 `api.py` 或同一 migration 序列的任务必须串行

2. 执行顺序
- 先 backend schema/model/service/api
- 再 frontend api client/page
- 最后 integration/e2e/release gate

3. 每个原子任务必须输出
- 任务 ID
- 修改文件列表
- 验证命令与预期状态码
- artifacts 证据

## 8. 完成定义（DoD）
- 对应 FR/US 状态提升为 Fully Implemented（或按约束标注 N/A）
- 无既有功能回归
- lint/typecheck/tests 全通过
- task gate & release gate 通过
