# Post-demo 专利收费场景 GAP Review

任务：`PD-FEE-SCENARIO-GAP-REVIEW-20260705-01`

## 1. 评审结论

当前设计方向是正确的：费用只按“官费”处理，`FeeRate` 作为官费参数目录，`FeeDraft / FeeItem / PayList / GovPayment` 继续承接草单、明细、官费清单和缴费登记；新增收费要求不应变成一个独立“新增费用”类型。

但当前实现只完成了第一条竖切：

- 官费参数目录已有雏形；
- 国内新申请 / 受理节点可预览部分官费；
- 授权费、年费开始从官费参数取数；
- 案件费用页出现“官费节点线”。

和 `专利收费场景-20260626.docx`、天悦网页、官方 2024 收费政策相比，仍存在明显 GAP：费用种类覆盖不完整，触发场景没有规则层，期限规则没有结构化，费减语义在不同模块仍不一致，复杂政策类费用只入了参数目录但未形成可执行规则。

## 2. 证据来源

### 2.1 客户 DOCX

- 文件：`docs/postdemo/专利收费场景-20260626.docx`
- 本轮提取：`artifacts/PD-FEE-SCENARIO-GAP-REVIEW-20260705-01/extracted/专利收费场景-20260626.txt`
- 结构：254 段、4 张表、无图片。
- 覆盖内容：国内费用、PCT 国际阶段、PCT 进入中国国家阶段、费用减缴规则。

### 2.2 公司网页

- URL：`http://www.tianyueip.com/product/612`
- 本轮直连抓取超时；使用上一轮已抓取证据：`artifacts/PD-FEE-SCENARIO-DESIGN-20260704-01/extracted/tianyueip_product_612.txt`
- 当前 web search 仍能检索到该页面，标题为“最新国内专利收费标准”。
- 网页相较客户 DOCX 额外体现：期限补偿请求费、补偿期年费、外观设计国际注册指定中国单独指定费、开放许可年费减免、PCT 进入中国国家阶段免缴规则、费用减缴依据。

### 2.3 官方交叉来源

- 国家知识产权局第 594 号公告，2024-08-06：期限补偿请求费 200 元、补偿期年费 8000 元/年、开放许可年费减免 15%、外观设计国际申请指定费可按规定减缴、PCT 进入中国国家阶段免缴规则。
- 国家知识产权局《专利和集成电路布图设计缴费服务指南》：申请费、实审费、复审费、恢复、延期、年费、滞纳金、费减申请期限等细则。

### 2.4 现有设计与实现

- 设计：`docs/postdemo/postdemo_fee_scenario_integration_design_20260704.md`
- 费率模型/API：`backend/app/modules/fees/models.py`、`schemas.py`、`api.py`
- 申请费/预览服务：`backend/app/modules/fees/service.py`
- 参数目录 seed：`backend/scripts/seed_dev.py`
- 授权费：`backend/app/modules/grant_fees/service.py`
- 年费：`backend/app/modules/annuity/service.py`
- 案件费用 UI：`frontend/src/modules/cases/components/CaseFeesTab.vue`
- E2E seed/test：`FPMS_Automation_Skeleton_Pack/playwright_ts/src/support/pdP1LiveSeed.py`、`src/tests/pd-p1.live-backend.spec.ts`

## 3. Brainstorming / Grill 结论

### 3.1 推荐产品假设

1. `FeeRate` 不是“收费场景”，而是官费参数目录。
2. 触发场景应由独立规则层表达，例如 `FILING_ACCEPTED`、`EXAM_REQUESTED`、`REJECTION_RECEIVED`、`ANNUITY_DUE`。
3. P1.5 可以优先启用国内主线，但参数目录应能容纳全部客户/网页/官方可识别官费条目。
4. 任何自动生成都应先走“预览 -> 人工确认 -> 草单/清单”，避免文件入库时静默生成不可解释费用。
5. 费减应明确区分“客户减免比例”和“官方应缴比例”，不能在不同模块混用。

### 3.2 被拷问后的结论

当前实现最大问题不是表不够，而是缺少“官费触发规则层”。只有参数表，系统知道“多少钱”；但没有规则层，系统不能可靠知道“什么时候、因哪个文件、按哪个期限、用哪些案件字段生成这笔钱”。

## 4. GAP 总览

| GAP ID | 主题 | 严重度 | 当前状态 | 影响 |
| --- | --- | --- | --- | --- |
| GAP-FEE-001 | 费减语义不一致 | P0 | 费用服务仍把 `case.fee_reduction` 当应缴比例 | 金额可能系统性错误 |
| GAP-FEE-002 | 申请费金额/演示 seed 不一致 | P0 | live demo seed 使用 1000 元发明申请费，官方/客户为 900 元 | Demo 与官方标准冲突 |
| GAP-FEE-003 | 缺少触发规则模型/服务 | P0 | 仅预览 `FILING_ACCEPTED` | 多数收费场景无法自动候选 |
| GAP-FEE-004 | 期限规则未结构化 | P0 | `FeeDraft/FeeItem/Preview` 无 due date rule | 无法形成收费节点线和期限提醒 |
| GAP-FEE-005 | 参数目录有条目但多数未启用 | P1 | seed 中大量 `enabled=False` | 覆盖目录不等于可用功能 |
| GAP-FEE-006 | 复杂计算模式未通用实现 | P1 | `PER_PAGE/TIER/COMPOSITE` 只局部支持 | 页数、优先权、滞纳金、PCT 无法算 |
| GAP-FEE-007 | 前端参数表类型缺来源字段 | P1 | backend 有 source 字段，frontend `FeeRate` 类型未暴露 | 用户无法审计费率来源 |
| GAP-FEE-008 | 官费节点 UI 仅展示新申请 | P1 | UI 固定 `FILING_ACCEPTED` | 无法展示全生命周期费用节点 |
| GAP-FEE-009 | 官方缴费 Excel 仍未验证 | P1 | 内部 pay-list 导出不等于官网模板 | 不能承诺批量上传官网缴费 |
| GAP-FEE-010 | 官方政策来源版本化不足 | P1 | 有 source 字段但无强约束/枚举/冲突处理 | 后续费率更新审计风险 |

## 5. 费用种类覆盖 GAP

### 5.1 已入参数目录且已启用

来自 `backend/scripts/seed_dev.py`：

- 国内申请费：发明、实用新型、外观。
- 权利要求附加费。
- 公布印刷费。
- 发明实质审查费。
- 年费：发明、实用新型、外观设计年度阶梯。

GAP：这些“启用”不代表全部可触发。实际自动预览只覆盖 `FILING_ACCEPTED`，且申请费服务未覆盖说明书附加费、优先权费、独立实审请求场景。

### 5.2 已入参数目录但未启用

来自 `backend/scripts/seed_dev.py`：

- 说明书附加费 31-300 页、301 页起。
- 优先权要求费。
- 复审费。
- 年费滞纳金。
- 恢复权利请求费。
- 第一次/再次延长期限请求费。
- 著录事项变更费。
- 专利权评价报告请求费。
- 无效宣告请求费。
- 专利文件副本证明费。
- PCT 国际阶段费用。
- PCT 进入中国国家阶段费用。
- 专利权期限补偿请求费、补偿期年费。
- 外观设计国际注册指定中国单独指定费。

GAP：这些条目只是参数目录或待确认目录，尚未形成“触发 -> 期限 -> 草单候选 -> 人工确认”的产品能力。

### 5.3 当前参数目录疑似缺失

以下在官方缴费指南或网页中出现，但当前 seed 目录未形成明确可用条目，至少需要确认是否纳入 FPMS 官费范围：

1. `GAP-CATALOG-001`：印花税 5 元。官方缴费指南列为授予阶段代收；当前 `FeeRate` seed 未见 `CN_STAMP_TAX`。
2. `GAP-CATALOG-002`：专利登记相关费用 / 授权登记组合边界。当前 `GrantFeeTask` 使用“授权官费”或年费 fallback，但没有明确拆分登记、印花税、授权当年年费。
3. `GAP-CATALOG-003`：PCT 国际申请中由 WIPO/国际局收取且随汇率变化的费用。当前只登记国知局收取的部分和部分 PCT 项目，缺汇率/国际局标准来源。
4. `GAP-CATALOG-004`：开放许可年费减免 15%。当前有 `CN_ANNUITY_FEE_*` 和 `allow_reduction_years_from_grant`，但没有开放许可状态字段、期间、减免优先级规则。
5. `GAP-CATALOG-005`：批量著录项目变更“同日同类不涉转移按一件缴费”。当前只有 `CN_BIBLIO_CHANGE_FEE` 固定费率，没有批量规则。
6. `GAP-CATALOG-006`：费用种类转换。官方指南提到费用种类填错后的转换请求；当前没有转换流程或审计对象。

## 6. 触发场景 GAP

### 6.1 当前实现

- `backend/app/modules/fees/service.py::preview_official_fee_candidates` 只支持 `FILING_ACCEPTED`。
- `generate_apply_fee_draft` 是手动 API 调用，不是统一场景引擎。
- `CaseFeesTab.vue` 固定调用 `trigger_event: 'FILING_ACCEPTED'`。

### 6.2 缺失触发场景

| GAP ID | 缺失触发 | 证据 | 当前影响 |
| --- | --- | --- | --- |
| GAP-TRIGGER-001 | `EXAM_REQUESTED` 独立实审请求 | DOCX：发明实审费可主动提交实审请求或届满前通知触发 | 目前只有新申请阶段 `has_exam_request` 为真时一起算 |
| GAP-TRIGGER-002 | `REJECTION_RECEIVED` + 客户选择复审 | DOCX：驳回决定起 3 个月 | 复审费参数未启用，也无官文触发 |
| GAP-TRIGGER-003 | `EXTENSION_REQUESTED` | DOCX：OA/补正期限届满前申请延期 | 无第一次/再次延期月份和历史次数判断 |
| GAP-TRIGGER-004 | `RIGHT_LOSS_NOTICE_RECEIVED` / `RESTORE_RIGHT_REQUESTED` | DOCX：视撤/终止通知后 2 个月 | 参数未启用，恢复工作包缺失 |
| GAP-TRIGGER-005 | `BIBLIO_CHANGE_SUBMITTED` | DOCX：著录事项变更 1 个月 | 无变更流程与费用联动 |
| GAP-TRIGGER-006 | `EVALUATION_REPORT_REQUESTED` | DOCX：实用新型/外观评价报告 | 参数未启用，无请求流程 |
| GAP-TRIGGER-007 | `INVALIDATION_REQUESTED` | DOCX：无效宣告请求 1 个月内 | 无无效案件/费用触发联动 |
| GAP-TRIGGER-008 | `COPY_CERT_REQUESTED` | DOCX：专利文件副本证明费每份 | 无份数、请求人、清单字段 |
| GAP-TRIGGER-009 | `GRANT_NOTICE_RECEIVED` | DOCX/官方指南：授权当年费用 | 仅有 `GrantFeeTask`，金额拆分不清 |
| GAP-TRIGGER-010 | `ANNUITY_DUE` / `ANNUITY_LATE` | DOCX/官方指南：年费、滞纳金 | 年费可生成，滞纳金未实现 |
| GAP-TRIGGER-011 | PCT 国际阶段各节点 | DOCX：检索、初审、单一性、后提交等 | 全部未启用 |
| GAP-TRIGGER-012 | PCT 进中国国家阶段 | DOCX/第 594 号公告：宽限、译文、免缴 | 全部未启用 |
| GAP-TRIGGER-013 | 外观设计国际注册指定中国 | 天悦网页/第 594 号公告 | 参数金额为空，未启用 |
| GAP-TRIGGER-014 | 期限补偿请求 / 补偿期年费 | 天悦网页/第 594 号公告 | 参数金额为空，未启用 |
| GAP-TRIGGER-015 | 开放许可期间年费减免 | 第 594 号公告 | 无开放许可状态和减免选择规则 |

## 7. 期限规则 GAP

### 7.1 当前模型短板

- `FeeDraft` 和 `FeeItem` 没有 `due_date`、`due_date_rule_code`、`source_event_date`、`deadline_basis`。
- `OfficialFeePreviewOut` 只返回候选金额，不返回缴费期限或期限依据。
- `PayList` 有计划缴费日期，但它不是费用触发规则中的法定期限。

### 7.2 具体期限差异

| GAP ID | 期限规则 | 当前问题 |
| --- | --- | --- |
| GAP-DEADLINE-001 | 申请费：申请日起 2 个月，或收到受理通知书起 15 日内 | DOCX 简化为申请日/受理通知起 2 个月；实现没有二选一规则 |
| GAP-DEADLINE-002 | 实审费：申请日或最早优先权日起 3 年内 | 实现只看 `has_exam_request`，没有独立期限 |
| GAP-DEADLINE-003 | 复审费：驳回决定收到日起 3 个月 | 无官文日期/客户指示触发 |
| GAP-DEADLINE-004 | 恢复权利：收到权利丧失通知日起 2 个月 | 无恢复工作包和期限 |
| GAP-DEADLINE-005 | 延长期限：应在指定期限届满前提交并缴费 | 无 OA/补正 deadline 关联 |
| GAP-DEADLINE-006 | 著录变更/评价报告/无效：请求日起 1 个月 | 无请求对象和期限字段 |
| GAP-DEADLINE-007 | 年费：授权当年与后续年度期限不同 | 当前年费任务按申请日年度推算，未区分授权当年登记手续通知 |
| GAP-DEADLINE-008 | 年费滞纳金：未满 1 个月不收，1-2 月 5%，最高 25% | seed 只记录 `monthly_percent=5,max=25`，缺“未满一月 0”与区间规则 |
| GAP-DEADLINE-009 | PCT 优先权文件费：优先权日起 16 个月 | 无 PCT 期限规则 |
| GAP-DEADLINE-010 | PCT 进入中国：30-32 月宽限 | 只有 `pct_national_entry_date`，无宽限判断 |

## 8. 计算规则 GAP

| GAP ID | 计算规则 | 当前实现差距 |
| --- | --- | --- |
| GAP-CALC-001 | 客户 `0.85` 表示减免 85%，官方应缴 15% | `fees.service` 使用 `case.fee_reduction` 直接作为付款比例；`discount_rate` 参数未参与 `generate_apply_fee_draft` |
| GAP-CALC-002 | 申请费标准应为发明 900 | live E2E seed `pdP1LiveSeed.py` 中发明申请费仍为 1000，和客户/官方来源不一致 |
| GAP-CALC-003 | 说明书附加费按说明书含附图页数，分 31-300 与 301+ 两档 | 参数已登记但未启用，申请费计算未读取 `spec_pages/draw_pages` |
| GAP-CALC-004 | 优先权要求费按优先权项数 | 有 `T_Priority`，但申请费计算未读取优先权行数 |
| GAP-CALC-005 | 实审费可新申请同时缴，也可独立缴 | 当前只作为 `FILING_ACCEPTED` 的附带项 |
| GAP-CALC-006 | 复审费允许减缴 | 参数未启用，无客户是否复审的指示对象 |
| GAP-CALC-007 | 年费只在授权当年起 10 年内可费减 | `calc_params` 有说明，但年费计算没有真正按费减年限和应缴比例计算 |
| GAP-CALC-008 | 开放许可年费减免 15%，且不得重复享受 | 没有开放许可字段、期间、优先适用规则 |
| GAP-CALC-009 | 年费滞纳金按全额年费比例，不按减缴后年费 | 当前未实现滞纳金计算 |
| GAP-CALC-010 | 批量著录事项变更按数量/权利转移条件区分 | 当前只有固定费率 |
| GAP-CALC-011 | PCT 国际局代收费用涉及外汇/国际局标准 | 无汇率、月份版本和 WIPO 标准来源 |
| GAP-CALC-012 | PCT 进入中国免缴申请费/附加费/实审费的条件 | 参数目录未表达免缴规则 |
| GAP-CALC-013 | 外观国际单独指定费第一期/第二期可减缴 | seed 只有一个金额为空的合并条目 |
| GAP-CALC-014 | 专利权期限补偿请求费和补偿期年费 | seed 金额为空，未按官方 200/8000 入可执行版本 |

## 9. 数据模型 / 参数表 GAP

1. `GAP-MODEL-001`：没有 `OfficialFeeScenarioRule` 或等价配置表。设计中已提出，但实现未落地。
2. `GAP-MODEL-002`：`FeeRate.source_status` 是自由字符串，缺少枚举、状态迁移、启用门禁。
3. `GAP-MODEL-003`：`FeeRate` 缺少唯一约束或版本选择规则；同一 `fee_code/currency/rate_group/effective_from` 多条启用时，服务可能取值不稳定。
4. `GAP-MODEL-004`：`FeeRate.calc_mode` 枚举不含 `PER_ITEM`、`PERCENT_BY_MONTH`，设计用词与实现枚举不完全一致。
5. `GAP-MODEL-005`：`FeeRate.calc_params` 是自由 JSON 文本，缺少按 calc_mode 的 schema 校验。
6. `GAP-MODEL-006`：`FeeItem` 缺少计算快照字段，例如减缴前金额、减免比例、应缴比例、公式、参数版本、source rule id。
7. `GAP-MODEL-007`：`FeeDraft` 缺少来源事件、来源文件、触发场景、人工确认状态、期限依据。
8. `GAP-MODEL-008`：案件字段缺开放许可状态、期限补偿信息、PCT 单一性主题数、PCT 国际局费用版本、外观国际指定阶段。
9. `GAP-MODEL-009`：案件已有优先权表，但费用服务未把优先权表作为计费输入。
10. `GAP-MODEL-010`：说明书页数口径未冻结，`spec_pages/draw_pages/claim_pages` 是否等同官方“说明书包括附图页数”仍需确认。

## 10. API / 服务 GAP

1. `GAP-API-001`：`/fees/official-fee-preview` 只接受 `case_id/trigger_event/currency/source_document_id`，无法传入触发日期、请求数量、延期月数、PCT 主题数、文件份数。
2. `GAP-API-002`：预览 API 返回金额候选，但不返回期限、阻塞字段、规则版本、人工确认动作。
3. `GAP-API-003`：没有“预览结果确认并生成草单”的专用 API；当前生成和预览分离，idempotency 没有持久化。
4. `GAP-API-004`：`generate_apply_fee_draft` 接收 `discount_rate`，但服务计算实际读取 `case.fee_reduction`。
5. `GAP-API-005`：缺少按官文/文书触发费用候选的 API，例如驳回决定、授权通知、年费通知、视撤通知。
6. `GAP-API-006`：缺少官方缴费模板兼容 API；现有 xlsx 是内部官费清单。

## 11. UI / Demo GAP

1. `GAP-UI-001`：案件“官费节点线”只显示申请/受理候选，不是完整生命周期费用节点线。
2. `GAP-UI-002`：节点状态只有候选/已有草稿/缺费率，缺少“缺页数、缺优先权、缺期限、待确认官方模板、来源待确认”等细分阻塞。
3. `GAP-UI-003`：`formatSourceStatus` 只识别 `PENDING`，但 seed 使用 `PENDING_CONFIRMATION`，UI 会显示“来源状态：未标记”。
4. `GAP-UI-004`：前端 `FeeRate` 类型没有 source_doc/source_url/source_policy/source_version/source_status，费率参数表 UI 无法展示来源审计。
5. `GAP-UI-005`：没有费用触发规则维护/查看 UI。
6. `GAP-UI-006`：没有按文件详情展示“由本文件触发的费用”。
7. `GAP-UI-007`：演示 seed 中发明申请费 1000、费减 0.85 应缴 85% 的演示口径会误导客户。

## 12. 测试覆盖 GAP

1. `GAP-TEST-001`：申请费测试覆盖发明 + 权利要求附加 + 公布印刷 + 实审，但不覆盖实用新型/外观申请费生成。
2. `GAP-TEST-002`：没有测试 `0.85` 客户减免比例必须转换为 `0.15` 应缴比例。
3. `GAP-TEST-003`：没有说明书附加费页数分档测试。
4. `GAP-TEST-004`：没有优先权要求费按优先权行数计算测试。
5. `GAP-TEST-005`：没有独立实审请求触发测试。
6. `GAP-TEST-006`：没有复审、延期、恢复、著录变更、评价报告、无效、证明副本费用测试。
7. `GAP-TEST-007`：没有年费费减、授权当年年费、滞纳金区间测试。
8. `GAP-TEST-008`：没有 PCT/PCT_CN/Hague/期限补偿/开放许可测试。
9. `GAP-TEST-009`：没有官方缴费 Excel 字段兼容测试。
10. `GAP-TEST-010`：E2E 只覆盖 demo 主线，不覆盖异常和待确认状态。

## 13. 合规 / 审计 GAP

1. `GAP-AUDIT-001`：费率来源有文本字段，但没有“官方来源优先、客户确认次之、网页线索最低”的启用策略。
2. `GAP-AUDIT-002`：缺少费率版本生效/失效冲突检测。
3. `GAP-AUDIT-003`：生成草单后如果案件页数、权利要求项数、费减、优先权变更，缺少重算/差异提醒。
4. `GAP-AUDIT-004`：缺少人工确认人、确认时间、确认理由的审计记录。
5. `GAP-AUDIT-005`：缺少官方缴费回执与 `PayList/GovPayment` 的结构化核对规则。
6. `GAP-AUDIT-006`：公司网页是客户提供线索，不应作为唯一执行依据；当前 source_policy 有提示，但实现没有强制阻止 `PENDING_CONFIRMATION` 条目启用。

## 14. 建议优先级

### P0：先修正会导致金额错误的问题

1. 修正 fee reduction 语义：所有官费计算统一使用“官方应缴比例”，客户输入 `0.85` 必须转换为 `0.15`。
2. 修正 live demo seed 中发明申请费 1000 -> 900，并同步 E2E 期望金额。
3. 给 `FeeRate.source_status` 和 `enabled` 增加启用门禁：待确认条目不得自动生成草单。

### P1：建立规则层，覆盖国内主线

1. 增加 `OfficialFeeScenarioRule` 或服务层等价规则。
2. 让预览返回期限、计算依据、缺失字段和规则版本。
3. 补齐国内申请费组合：说明书附加费、优先权费、实用新型/外观、独立实审。
4. 补齐年费费减、授权当年边界和滞纳金区间。
5. UI 从“一个申请/受理节点”升级为案件生命周期费用节点线。

### P2：文件驱动中间费用

1. 驳回 -> 复审费。
2. OA/补正延期 -> 延长期限请求费。
3. 视撤/终止 -> 恢复权利请求费。
4. 著录变更、评价报告、无效、证明副本。
5. 文件详情显示由该文件触发/阻塞的费用。

### P3：政策复杂场景

1. PCT 国际阶段。
2. PCT 进入中国国家阶段免缴/宽限/译文/单一性。
3. 外观设计国际注册指定中国。
4. 期限补偿请求和补偿期年费。
5. 开放许可年费减免。

## 15. 待客户/官方确认

1. 以哪个版本作为上线执行费率：CNIPA 官方、客户盖章确认版、还是天悦网页线索？
2. 客户是否接受先全量入参数目录，但只启用国内主线触发？
3. 说明书附加费页数口径：说明书正文、附图、摘要附图是否计入？
4. 优先权要求费是否按系统优先权行数直接计项？
5. 申请费期限是否按官方“申请日起 2 个月 / 受理通知起 15 日内”双规则执行？
6. 年费期限和滞纳金是否由系统自动判定，还是财务人工确认？
7. 授权阶段是否纳入印花税、登记相关费用、授权当年年费三类拆分？
8. PCT 国际局代收费用是否需要系统维护汇率和月份标准？
9. 官方补充缴费信息模板是否提供空表、成功样例、字段说明和 500 行限制确认？
10. 开放许可、期限补偿、外观国际指定中国是否进入近期演示范围？

## 16. 下一步拆任务建议

1. `PD-FEE-SCENARIO-FEE-REDUCTION-SEMANITCS-FIX`：统一费减语义和 demo seed 金额。
2. `PD-FEE-SCENARIO-RULE-LAYER-SPEC`：冻结触发规则模型/服务契约。
3. `PD-FEE-SCENARIO-APPLY-FEE-COMPLETE`：补齐说明书附加费、优先权费、UM/DES、独立实审。
4. `PD-FEE-SCENARIO-DEADLINE-RULES`：结构化费用期限规则。
5. `PD-FEE-SCENARIO-ANNUITY-LATE-FEE`：年费费减和滞纳金。
6. `PD-FEE-SCENARIO-FEE-NODE-LIFECYCLE-UI`：费用节点线扩展到案件生命周期。
