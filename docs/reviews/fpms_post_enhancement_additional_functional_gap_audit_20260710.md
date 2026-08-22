# FPMS 两轮 Review 与 Enhancement 后 Additional Functional GAP 审计

任务：`FPMS-POST-ENHANCEMENT-ADDITIONAL-FUNCTIONAL-GAP-AUDIT-20260710-02`  
审计日期：2026-07-10  
审计视角：中国专利代理机构业务架构、流程控制、期限与证据链完整性  
审计范围：只读核对当前工作区，不修改产品代码

## 一、增量审计结论

**有 additional GAP。** 在排除两轮 review、2026-07-05 功能审计及 2026-07-10 meta-audit 已明确记录的问题后，本轮确认 **7 个新增或具有独立业务后果的功能实现 GAP**：

- 5 个 `P0`：官方工作包无法从产品流程创建/发现、OA 任务和案件状态闭环时点错误、官方通知目录与可执行模板脱节、回执附件缺少同案件归属校验、授权费法定期限由代码无依据推算；
- 1 个 `P0` 直接页面阻断：文书向导模板请求固定返回 422；
- 1 个 `P1`：OA 官方期限虽有后端隐藏字段，但普通 UI 无结构化维护入口。

因此，当前系统不能按“页面存在、接口 200、demo 路径可打开”判断国内专利主线已经功能闭环。更准确的判断是：

| 闭环层级 | 当前判断 | 说明 |
| --- | --- | --- |
| Demo 可见 | 部分达到 | 预置 `package_id`、测试 fixture 或 enrichment 后可展示工作包和费用页面。 |
| 人工可操作 | 部分达到 | 已存在文书、任务、附件、清单和归档动作，但若从新案件/新官文起步，多个入口不可达或语义会走错。 |
| 生产控制 | 未达到 | 工作包创建、OA 完成时点、跨案证据、通知模板语义和法定期限来源仍不能 fail-closed。 |

## 二、去重边界

本报告不重复以下既有结论：格式函占位/渲染、费率来源 fail-open、22 项致函官方目录待客户确认、每页计费口径、PayList/GovPayment 结构性不足、今日提醒打印集合、文档导出截断、授权/年费 preview 字段收窄、官方缴费 Excel、回执元数据内容门禁、override 独立权限、附件类型校验、文档版本链及产品审计导出。

增量接纳规则：

1. 前述报告没有明确记录该具体缺口；或
2. 虽与既有大类有关，但该缺口会独立导致错误期限、错误案件状态、跨案件证据污染或产品入口不可达；
3. 必须同时具备业务场景、规范/设计依据和当前代码证据。

## 三、Additional GAP 总表与业务优先级

| ID | Additional GAP | 直接业务后果 | 严重度 | 业务优先级 | 确认状态 | 关闭判断 |
| --- | --- | --- | --- | --- | --- | --- |
| `ADD-GAP-WORKPKG-01` | 官方工作包只有按 ID 读/改，没有产品创建、列表或按案件/官文解析入口 | 新案件或新 OA 官文无法在产品内启动递交/OA 工作包；demo 依赖 fixture | Critical | P0 | 已确认 | Open |
| `ADD-GAP-OA-01` | OA_OUT 创建即关闭任务；回执归档不恢复案件状态 | 未收到官方回执时任务已完成，收到回执后案件仍可能停在 OA1/OA2 | Critical | P0 | 已确认 | Open |
| `ADD-GAP-CATALOG-01` | 60 项官方通知目录与 `OA_IN`/`GRANT_NOTICE` 可执行模板并行且无语义映射 | 用户选中真实中文官文名称后不建任务、不变状态、不触发授权费 | Critical | P0 | 已确认；目录权威性待客户确认 | Open |
| `ADD-GAP-RECEIPT-01` | 回执附件未校验与工作包属于同一案件 | A 案回执可作为 B 案归档证据，形成跨案错误闭卷 | Critical | P0 | 已确认 | Open |
| `ADD-GAP-GRANT-01` | 授权费期限按官文日 `+60` 天硬算，任务又未绑定源官文 | 法定期限可能错误；更正/重发官文也不会刷新任务 | Critical | P0 | 已确认；结构化期限来源待确认 | Open |
| `ADD-GAP-WIZARD-01` | 文书向导请求 200 条模板，后端上限为 100 | 页面固定收到 422，模板下拉为空，批量文书向导无法起步 | High | P0 | 已确认 | Open |
| `ADD-GAP-DEADLINE-01` | `OfficialDueDate` 仅藏在 JSON，普通 UI 只有“描述/补充说明”文本框 | 流程人员无法可靠维护 OA 官方期限，任务会退回模板推算 | High | P1 | 已确认；字段来源/override 规则待确认 | Open |

## 四、场景回放与代码审计

### 4.1 `ADD-GAP-WORKPKG-01`：工作包页面存在，但真实业务入口不可达

**业务场景**

流程人员在 UI 新建国内发明案件，或登记一份 OA 官文，然后希望进入“新申请递交准备”或“OA 答复工作包”。系统应按案件/官文幂等创建或找到工作包，不应要求人员事先知道数据库中的 `package_id`。

**规范与设计依据**

- P1 Functional Spec 要求从案件进入递交准备视图、从 OA 来文进入答复工作包：`docs/postdemo/postdemo_p1_functional_spec_20260531.md:417-420`。
- V6 生产数据来源说明写明“案件进入递交准备时，由系统按规则自动生成”新申请工作包，并由 OA 来文创建答复工作包：`docs/postdemo/postdemo_p1_v6_ui_e2e_success_runbook_20260705.md:190-204`。

**当前实现证据**

- `backend/app/modules/official_workflows/api.py:53-327` 只有按现有 `package_id` 获取、刷新、关联、清单、费用、回执和归档端点；唯一名为 create 的端点创建的是 receipt，不是 `OfficialWorkPackage`。未发现工作包 create/list/resolve 服务。
- OA 页面只读取 `package_id/packageId`，无值就不请求：`frontend/src/modules/documents/pages/OAReplyPackage.vue:244-272`。
- 文书详情的“进入 OA 工作包”链接传递的却是 `document_id`：`frontend/src/modules/documents/pages/DocumentDetail.vue:240-258`。因此该入口到达 OA 页面后仍显示“请选择具体 OA 答复工作包”。
- V6 runbook 明确说明需运行 enrichment，因为 UI 不能从零生成全部官方工作包 fixture：`docs/postdemo/postdemo_p1_v6_ui_e2e_success_runbook_20260705.md:61-70`。
- enrichment 直接克隆并插入 `OfficialWorkPackage`、manifest 和 checklist：`FPMS_Automation_Skeleton_Pack/playwright_ts/src/support/pdP1LiveSeed.py:1203-1263`。

**影响与判断**

这是“资源页面实现了、业务用例没实现”。带固定 ID 的 E2E 可以通过，但不能证明新案件、新官文的真实主线可用。该 GAP 阻断 AC-03、AC-05，也使费用联动和回执归档只能在预置工作包上演示。

**建议处置**

拆分原子任务实现：

1. 按 `case_id` 幂等 ensure/resolve `FILING_PREP` 工作包；
2. 按 `source_document_id` 幂等 ensure/resolve `OA_REPLY` 工作包，并验证官文同案、方向和需答复语义；
3. 增加案件/官文入口与最小可查询列表；
4. 把 demo enrichment 降级为测试数据工具，不再作为生产主线前置条件。

### 4.2 `ADD-GAP-OA-01`：OA 完成事件与状态变化时点错误

**业务场景**

代理人完成 OA 答复文书，但尚未在专利业务办理系统提交、尚未取得电子申请回执。此时内部答复材料可以标记“已准备”，但 OA 法定期限任务不能视为已经完成。只有归档官方回执并完成核对后，任务才能关闭，案件才能由 OA1/OA2 回到实审中。

**规范与设计依据**

- P1 AC-07 明确：内部任务不能仅因创建 OA_OUT 文书就完成，默认必须等待回执归档：`docs/postdemo/postdemo_p1_functional_spec_20260531.md:419-422`。
- 生命周期设计明确“答复归档：一通或二通阶段 → 实审中；工作包归档、内部任务关闭”：`docs/postdemo/postdemo_p1_lifecycle_demo_design_20260704.md:98-105`。

**当前实现证据**

- 创建任何指向来源文书的 OUT 回复时，`_apply_reply_chain` 立即把来源文书全部 OPEN 任务改为 DONE，并写 `AUTO_WRITEOFF`：`backend/app/modules/documents/service.py:305-340`。
- 默认 `OA_OUT.status_restore=None`：`backend/scripts/seed_dev.py:1193-1204`，所以创建答复文书不会恢复案件状态。
- `archive_official_work_package` 在门禁通过时只写 `package.status="ARCHIVED"`，没有关闭 OA 任务或更新 `Case.status`：`backend/app/modules/official_workflows/service.py:2049-2065`。

**影响与判断**

形成两个相反错误：回执前任务提前完成，回执后案件状态不随证据恢复。期限看板会过早消失待办，案件法律状态又会滞留在 OA 阶段。这不是单纯的“状态矩阵以后再做”，而是当前 P1 国内 OA 主线的错误关闭时点。

**建议处置**

冻结事件语义后拆分原子任务：`OA_OUT_CREATED` 只表示内部材料已准备；`OFFICIAL_RECEIPT_ARCHIVED` 才关闭来源 OA 任务并恢复 `SUB_EXAM`。历史 OA1/OA2、补正、复审等不同来文是否采用同一恢复状态，应在任务合同中逐项列明，不能用通用 OUT 文书自动销账。

### 4.3 `ADD-GAP-CATALOG-01`：真实官文目录与流程驱动模板脱节

**业务场景**

流程人员在“登记往来文件”中选择“第一次审查意见通知书”或“授权通知书-电子”。从业务名称看，这应分别产生 OA 答复任务或授权费/授权状态节点。

**当前实现证据**

- 60 项 `OFFICIAL_NOTICE_*` 全部 `enabled=True`，但 `status_effect=None`、`deadline_template_code=None`、`fee_draft_type=None`、`need_reply=False`：`backend/app/modules/documents/official_notice_catalog.py:95-121`。
- 真正可执行的语义放在另一组技术模板中：`OA_IN` 才有 `need_reply=True/deadline_template_code=OA_REPLY/status_effect=OA1`，`GRANT_NOTICE` 才有 `status_effect=GRANT_PENDING/fee_draft_type=GRANT_FEE`：`backend/scripts/seed_dev.py:1177-1229`。
- 文书创建的状态变化依赖模板 `status_effect`，任务依赖 `deadline_template_code`：`backend/app/modules/documents/service.py:258-276`、`backend/app/modules/tasks/task_generation_service.py:95-112`。
- 授权费触发还额外硬编码只接受模板代码 `GRANT_NOTICE`：`backend/app/modules/grant_fees/service.py:392-403`。
- 前端把所有 enabled 且方向相同的模板放入同一选择框：`frontend/src/modules/documents/pages/DocumentCreate.vue:63-80,312-314`。

**影响与判断**

“目录覆盖 60 项”只是名义覆盖。用户选择客户熟悉的真实官文名称时，系统可能静默不建期限任务、不标记需答复、不进入 OA、不触发授权费；而测试和 demo 使用的是平行的 `OA_IN/GRANT_NOTICE`。这会制造非常危险的“登记成功但流程未启动”。

**建议处置**

在客户确认 60 项目录权威性前，先把这些项标记为“目录/历史别名、非流程模板”或禁用流程选择；随后建立明确 alias/resolver，把已确认的官文名称和代码映射到可执行行为。禁止仅靠显示名称相似让用户自行判断。

### 4.4 `ADD-GAP-RECEIPT-01`：回执证据允许跨案件关联

**业务场景**

流程人员同时处理 A、B 两案，误把 A 案电子申请回执的附件 ID 提交给 B 案工作包。系统必须拒绝，而不能把它标成 B 案归档证据。

**当前实现证据**

- `record_official_work_package_receipt` 只确认 package 存在，然后按附件 ID 取任意附件并直接设置 `is_archive_evidence/is_receipt_evidence`；未把 package 保留下来，也没有比较附件所属 `Document.case_id` 与 `package.case_id`：`backend/app/modules/official_workflows/service.py:1965-2009`。
- `DocAttachment` 通过 `document_id` 才能追溯案件：`backend/app/modules/documents/models.py:16-38`。
- 归档硬门禁只检查 receipt 有 attachment ID 且 archive status 属于已归档集合：`backend/app/modules/official_workflows/service.py:527-532,1901-1938`。

**影响与判断**

这与既有 `IC-02`“回执元数据内容不完整”不同：即使元数据未来全部必填，错误案件的真实 PDF 仍可让另一案件通过门禁。结果是跨案证据污染、错误关闭工作包和审计链失真。

**建议处置**

新增 fail-closed 归属校验：附件文书案件必须等于工作包案件；OA 回执原则上还应属于 reply document 或明确允许的 package evidence document。对历史数据先做只读异常扫描。`receiving_case_no` 是否还需与申请号/官方接收号自动比对，可列为客户确认项，但同案件校验不应等待客户决策。

### 4.5 `ADD-GAP-GRANT-01`：授权费期限来源不真实且无法追溯官文

**业务场景**

收到办理登记手续通知书/授权通知书，通知书载明具体期限；后续又收到更正或重发通知。系统应使用该官文载明期限，并能追溯当前任务来自哪份官文。

**规范与设计依据**

- 收费后续触发设计要求 `deadline_rule=以办理登记手续通知书/授权通知书载明期限为准`；若源官文没有结构化期限，只展示已有 `GrantFeeTask.due_date`，不得在服务里重新推算：`docs/postdemo/postdemo_fee_followup_trigger_design_20260705.md:189-195`。

**当前实现证据**

- 服务常量硬编码 `GRANT_FEE_NOTICE_DUE_DAYS=60`，新任务期限等于 `document.doc_date + 60 days`：`backend/app/modules/grant_fees/service.py:41-48,417-423`。
- 查询只按 `case_id` 找第一条既有任务；存在时直接返回，不会根据后来的更正/重发官文更新：`backend/app/modules/grant_fees/service.py:405-415`。
- `T_GrantFeeTask` 没有 `source_document_id` 或期限来源字段：`backend/app/modules/fees/models.py:126-161`。
- 当前测试把 2026-04-10 官文对应 2026-06-09 到期写成固定期望，实际上固化了 `+60` 推算：`backend/tests/test_grant_fee_notice_task_creation.py:213-270`。

**影响与判断**

UI 虽显示“以通知书载明期限为准”，底层日期却可能是系统制造的 60 天日期，形成解释与事实冲突。对专利期限管理，这是 Critical 风险；不能用“当前只做 demo”降低优先级。

**建议处置**

在结构化官文期限字段来源确认前 fail-closed：要求人工明确录入通知书载明期限及来源文书，或将任务标为 `NEEDS_CONFIRMATION`，不得静默生成看似精确的期限。后续增加 `source_document_id/deadline_source/deadline_confirmed_at` 或等价审计字段，并定义更正官文的 supersede 规则。

### 4.6 `ADD-GAP-WIZARD-01`：文书向导模板加载固定 422

**业务场景**

用户打开文书向导批量登记文书，第一步需要选择已启用模板。

**当前实现证据**

- 页面固定调用 `getDocTemplates(page_size=200)`：`frontend/src/modules/documents/pages/DocumentWizard.vue:1134-1147`。
- 后端 `GET /doc-templates` 明确约束 `page_size <= 100`，超出返回 FastAPI 422：`backend/app/modules/documents/api.py:165-182`。
- 仓库已有同类缺陷的真实 RED 证据：另一个页面请求同一 URL 的 `page_size=200` 时返回 422，改为 100 后通过：`artifacts/SKELE2E-FE-STATIC-PAGEERROR-01/summary.md:16-22`。

**影响与判断**

该请求没有环境依赖，按当前前后端合同必然失败；页面 catch 后清空模板并显示“模板列表加载失败”。文书向导后续任务、费用和附件候选预览均无法从正常 UI 起步。

**建议处置**

单独原子修复为后端允许值，并新增页面级测试断言模板请求 200、下拉非空。若模板超过 100，使用服务端搜索/分页，而不是再次提高硬编码上限。

### 4.7 `ADD-GAP-DEADLINE-01`：OA 官方期限只有隐藏 JSON 合同，没有业务 UI

**业务场景**

流程人员登记 OA 官文时，应看到并维护“官方答复期限”，随后系统据此计算内部期限和提醒；不应要求其知道 JSON 键名。

**规范与设计依据**

- P1 字段矩阵要求官方期限由 `Document.extra_data.OfficialDueDate`/任务期限自动带出：`docs/postdemo/postdemo_p1_functional_spec_20260531.md:190-201`。
- AC-05 要求从 OA 来文进入工作包时带出官文期限：`docs/postdemo/postdemo_p1_functional_spec_20260531.md:417-420`。

**当前实现证据**

- 任务生成器只在 `extra_data` 是合法 JSON 且精确包含大小写敏感键 `OfficialDueDate` 时采用该日期，否则退回模板日期计算：`backend/app/modules/tasks/task_generation_service.py:186-240`。
- 普通文书登记 UI 只提供“描述”文本框，并把该文本原样写入 `extra_data`：`frontend/src/modules/documents/pages/DocumentCreate.vue:177-183,570-584`、`frontend/src/api/documents.ts:117-126`。
- 文书向导同样只提供“补充说明”，提示可写摘要/备注，然后原样传 `extra_data`：`frontend/src/modules/documents/pages/DocumentWizard.vue:319-328,1230-1245`。

**影响与判断**

后端能力对普通流程用户不可发现、不可校验，也无法区分备注与结构化期限。真实使用中大概率输入普通说明，任务便退回模板推算；OA 页面随后显示的“官方期限”可能为空或与官文不一致。

**建议处置**

增加独立日期字段 UI、来源提示、必填/待确认状态和影响预览；后端接受单一规范字段并保留兼容读取旧 JSON。官方期限字段来源及谁有权 override 仍为 `待确认`，但不能因此继续让用户编辑原始 JSON。

## 五、与既有 GAP 的关系

| 本轮发现 | 与既有项关系 | 为什么仍属于 additional GAP |
| --- | --- | --- |
| `ADD-GAP-WORKPKG-01` | 既有审计评估了工作包字段和页面 | 未审计产品从案件/官文创建和发现工作包的可达性；demo 文档反而明确依赖 enrichment。 |
| `ADD-GAP-OA-01` | 与 IC-09 法律状态矩阵相关 | IC-09 是通用校验过宽；本项是 OA 任务提前 DONE、回执后案件不恢复的具体错误闭环。 |
| `ADD-GAP-CATALOG-01` | 与 BIZ-03 的 22 项 OUT 目录不同 | 本项针对 60 项 IN 官文与 `OA_IN/GRANT_NOTICE` 的执行语义断裂。 |
| `ADD-GAP-RECEIPT-01` | 与 IC-02/FG-04 回执内容门禁相关 | 内容完整也不能防止 A 案 PDF 被挂到 B 案；归属完整性是独立控制。 |
| `ADD-GAP-GRANT-01` | 与 TRACE-01、年费期限 GAP 不同 | 本项是授权费任务真实 due date 被 `+60` 制造且无来源官文，不是 preview 字段展示或年费算法。 |
| `ADD-GAP-WIZARD-01` | 无同项 | 这是当前前后端参数合同的确定性运行错误。 |
| `ADD-GAP-DEADLINE-01` | 与 AC-05/期限设计相关 | 后端测试覆盖 JSON 不等于流程人员可从 UI 维护官方期限。 |

## 六、建议关闭顺序

按专利事务所“期限和证据优先、页面便利性其次”的原则：

1. `ADD-GAP-WORKPKG-01`：先让真实案件/官文能够创建并进入工作包；
2. `ADD-GAP-OA-01`：冻结 OA_OUT、官方提交、回执归档、任务关闭、状态恢复的事件矩阵；
3. `ADD-GAP-RECEIPT-01`：阻止跨案证据归档；
4. `ADD-GAP-CATALOG-01`：把客户官文目录与可执行流程行为统一，未确认项 fail-closed；
5. `ADD-GAP-GRANT-01`：停止 `+60` 推算，建立期限来源和更正官文规则；
6. `ADD-GAP-WIZARD-01`：修复确定性 422，恢复文书向导入口；
7. `ADD-GAP-DEADLINE-01`：提供结构化官方期限维护和 override 审计。

每项必须拆为独立原子任务；不得把“工作包创建 + OA 状态机 + 回执校验 + 期限模型”合并成一个 mega task。

## 七、待确认问题

以下问题需要客户/业务负责人确认，但不影响本报告对 GAP 存在性的判断：

1. 60 项官方通知目录是否作为权威初始化字典；若是，哪些名称/代码映射 OA、补正、驳回、授权、年费等可执行行为；
2. 授权通知/办理登记手续通知是否已有可稳定读取的结构化期限；没有时是否强制人工录入并双人复核；
3. OA1、OA2、补正、复审等答复回执归档后的目标法律状态是否都回 `SUB_EXAM`，还是按官文类别分别恢复；
4. 官方期限允许哪些角色 override，是否必须保存原期限、修改原因和复核人；
5. 回执 `receiving_case_no` 与申请号/官方接收号是否要求系统自动比对，哪些场景允许人工例外。

## 八、最终关闭判断

本轮审计任务的关闭切片是“识别并证据化 additional functional GAP”，不是修复产品。7 项均有当前代码证据，且已与既有 review 去重。因此：

- **审计任务：PASS**；
- **产品 additional GAP：7 项 Open**；
- **当前 FPMS 国内专利 P1 主线：可做受控 demo，但不能声明从真实案件起步的端到端生产功能已闭环。**

