# 案件列表生命周期投影与状态口径设计

日期：2026-08-28

状态：书面规格独立复核通过，待用户确认

后续实施任务：`FPMS-POST-V6-CASE-STATUS-PROJECTION-IMPLEMENTATION-20260828-01`

## 1. 目标

让案件列表、工作台流程表和案件详情使用含义明确但不互相冒充的状态字段：

- 旧 `Case.status` 继续承担流程分组和兼容职责；
- 生命周期三元组继续承担业务阶段、官方程序阶段和法律状态的权威投影；
- 列表 API 显式提供两类状态，供后续筛选和报表逐步迁移；
- 当前 UI 不再把“待授权”标成“法律状态”，也不把进入第五阶段说成已经授权。

本设计是受控过渡，不重构状态机，也不删除旧字段。

## 2. 已确认的当前事实

当前代码存在两套用途不同的状态：

| 数据 | 当前来源 | 正确用途 |
| --- | --- | --- |
| `status` | `t_case.status` | 旧流程分组、筛选、兼容状态，例如 `GRANT_PENDING` |
| `business_stage` | 生命周期权威投影 | 业务处理阶段，例如“授权登记中” |
| `official_procedure_stage` | 生命周期权威投影 | 官方程序阶段，例如“授权登记” |
| `legal_status` | 生命周期权威投影 | 法律状态，例如“申请审理中” |

`CaseList.vue` 和 `WorkflowCaseTable.vue` 当前只读取 `status`，却把对应列命名为
“法律状态”。案件详情三轨则读取生命周期三元组。因此同一案件会同时出现列表“待授权”和
详情“法律状态：申请审理中”，但没有解释两者来自不同字段。

列表响应还遗漏 `updated_at`，所以前端即使已有更新时间列也只能显示 `-`。当前演示案件的
`filing_date` 确实为空；递交时间或回执时间不能自动等同为法律意义上的申请日。

## 3. 设计原则

1. **字段名称表达真实语义。** 流程状态、业务阶段、官方程序阶段和法律状态不得混称。
2. **权威事实不回退。** 生命周期三元组为空时显示待确认，不使用旧 `status` 补造法律结论。
3. **兼容优先。** 保留 `status`、现有查询参数和流程分组键，不引入迁移。
4. **只增加必要投影。** 不增加新表、新请求、新 store 或通用状态框架。
5. **申请日失败关闭。** 没有明确 `filing_date` 时显示“待录入”，不从其他时间推断。

## 4. API 契约

`GET /api/v1/cases` 的每个 `CaseListItem` 增加：

| 字段 | 类型 | 来源 | 说明 |
| --- | --- | --- | --- |
| `workflow_status` | `string` | `Case.status` | 语义明确的兼容别名 |
| `business_stage` | `string \| null` | `Case.business_stage` | 当前业务阶段 |
| `official_procedure_stage` | `string \| null` | `Case.official_procedure_stage` | 当前官方程序阶段 |
| `legal_status` | `string \| null` | `Case.legal_status` | 当前法律状态 |
| `updated_at` | `string \| null` | `Case.updated_at` | 案件记录更新时间 |

现有 `status` 必须原样保留，且 `workflow_status === status`。本轮不改变：

- `status` 查询参数、排序和统计；
- `filing_date` 的来源和可空性；
- 案件详情接口与 lifecycle-overlay 接口；
- HTTP 状态码、权限和响应外层结构。

所有新增生命周期字段直接读取 `t_case` 已有权威投影列，不新增查询或事件扫描。

## 5. 前端数据契约

`BackendCase` 与公共 `Case` 类型增加上述五个字段。映射规则固定为：

- `workflow_status` 优先读取新增字段；服务端旧版本缺失时仅为兼容读取 `status`；
- `status` 继续保留，避免破坏现有消费者；
- 三个生命周期轴保持可空，不做交叉 fallback；
- 后端 `updated_at` 契约保持 `string | null`；前端公共 `Case.updated_at` 为兼容现有消费者，
  继续把空值归一化为 `''`，由现有日期格式化函数展示为 `-`。

流程分组、步骤卡、筛选和标签颜色使用 `workflow_status || status`。法律状态展示只能读取
`legal_status`。

## 6. UI 文字与可见结果

### 6.1 工作台流程卡

- 第五张卡标题在工作台投影为“授权阶段”；基础 `WORKFLOW_STEPS` 的“授权”不改，避免连带
  改变案件详情五步条；
- 计数仍按 `workflow_status` 对应的 `GRANTED` 分组统计；
- 进入第五阶段不表示已经取得专利权。

### 6.2 工作台案件表与完整案件列表

- “当前步骤”改为“当前阶段”；
- 两张列表在本地把现有 `stepIndex` 格式化为“第 N 阶段/5”，并使用现有
  `flow.rule.stepText` 作为阶段文字；`GRANT_PENDING` 的阶段文字显示“授权登记”；
- `getCaseWorkflow()` 的 `stepLabel`、`stepNoText` 返回值保持不变，案件详情继续显示原有
  “授权 / 第5步/5”；
- 原“法律状态”列改为“流程状态”，继续显示“待授权”；
- 状态筛选标签改为“流程状态”，查询参数仍为 `status`；
- 申请日为空时显示“待录入”，不显示推断日期；
- 更新时间使用新增的 `updated_at` 投影，不再无故显示 `-`。

列表首轮不新增三元组列、悬浮卡或展开面板，避免表格拥挤。新增 API 字段是后续筛选、报表或
客户视图的稳定准备面，不要求本轮把所有字段同时铺到表格上。

### 6.3 案件详情

案件详情三轨继续展示：

- 业务阶段：授权登记中；
- 官方程序阶段：授权登记；
- 法律状态：申请审理中；
- 核验状态：已确认。

本轮不改变详情组件、三元组映射或当前优先摘要。

## 7. 缺失值和异常边界

- `workflow_status` 缺失但旧 `status` 存在：兼容使用旧值；
- 两者均缺失：显示“未知流程状态”，不得映射到受理阶段；
- 生命周期任一轴为空：对应字段保持待确认；
- `filing_date` 为空：显示“待录入”；
- `updated_at` 为空：显示 `-`，但正常数据库记录应有该值；
- 未识别枚举：使用现有受控未知状态文案，不直接向客户显示英文代码。

## 8. 最小修改边界

实施预计只涉及：

- `backend/app/modules/cases/schemas.py`：扩展 `CaseListItem`；
- `backend/app/modules/cases/service.py`：在 `list_cases_report_service` 实际组装
  `CaseListItem` 时投影已有列；
- `backend/app/modules/cases/api.py`：保持现有委托与响应外层不变，不在路由层重复组装字段；
- `frontend/src/api/cases.ts`、`frontend/src/api/cases.types.ts`：接收和映射新增字段；
- `frontend/src/constants/workflow.ts`、`frontend/src/constants/labels.zh.ts`：只把
  `GRANT_PENDING.stepText` 明确为“授权登记”并调整列表文案；不改 `WORKFLOW_STEPS` 和
  `getCaseWorkflow()` 的公共返回契约；
- `frontend/src/modules/cases/pages/CaseList.vue`：使用 workflow status 并展示更新时间；
- `frontend/src/modules/dashboard/dashboard.api.ts`：按 workflow status 计数和筛选，并只在工作台
  把第五阶段卡投影为“授权阶段”；
- `frontend/src/modules/dashboard/components/WorkflowCaseTable.vue`：使用 workflow status；
- 与上述契约直接相关的后端和前端测试。

不新建状态服务、聚合接口、数据库字段或通用组件。

## 9. 验收标准

1. 案件列表 API 同时返回 `status`、`workflow_status` 和三个生命周期轴。
2. `workflow_status` 与 `status` 完全一致，旧消费者继续工作。
3. `GRANT_PENDING` 案件在工作台归入“授权阶段”，表格显示“第5阶段/5 · 授权登记”；
   案件详情五步条仍显示“5. 授权”。
4. 列表列名和筛选名为“流程状态”，值为“待授权”。
5. 案件详情仍显示权威三元组，不被旧 `status` 覆盖。
6. 列表更新时间来自 `updated_at`；申请日为空时显示“待录入”。
7. 不发生数据库迁移、生命周期写入、历史回填或额外网络请求。
8. 针对案件列表 API、工作流映射和客户可见中文文案的定向测试通过。

## 10. 测试策略

- 后端 API 测试构造一个 `GRANT_PENDING` 案件并写入三个生命周期轴，断言列表响应字段和值。
- 后端测试断言 `updated_at` 非空且 `filing_date` 仍可为空。
- 前端 contract 测试断言两张表使用 `workflow_status || status`，并禁止把流程列命名为法律状态。
- 工作流映射测试断言工作台第五阶段卡为“授权阶段”、当前阶段为“授权登记”、序号使用
  “阶段”，并断言公共 `getCaseWorkflow()` 与案件详情五步条仍为“授权 / 第5步/5”。
- 工作台统计测试断言计数和阶段筛选读取 `workflow_status || status`。
- 运行现有案件详情三轨 contract，证明权威三元组没有回归。

不为本任务引入新的测试框架或全站视觉重构。

## 11. 明确不做

- 不删除、重命名或迁移数据库中的 `status`；
- 不改变任何生命周期进入/退出条件；
- 不自动填写申请日、申请号、授权日或专利号；
- 不根据授权通知、递交时间或回执时间推导法律事实；
- 不增加三元组筛选、报表聚合或列表详情展开；
- 不修改 V6 种子、runbook、费用链或已暂停 Demo 数据；
- 不清理相邻页面的旧状态代码和文案。

## 12. 停止条件

如果实施发现新增字段不能直接来自 `t_case` 现有投影列，或需要修改生命周期写入、数据库
schema、申请日来源或历史记录，必须停止受影响部分并重新确认，不得在本任务中吸收。
