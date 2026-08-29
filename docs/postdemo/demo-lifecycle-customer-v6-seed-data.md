# FPMS 客户演示 V6：种子数据与 Runtime 输入详细说明

版本日期：2026-08-26
适用演示：`demo-lifecycle-customer-v6` / 同案双轨费用闭环
数据分级：`SYNTHETIC_TEST_ONLY`（真实业务形态的合成测试数据）
适用环境：本地 `TECHNICAL_REHEARSAL`，不适用于生产或正式客户数据导入

## 1. 文档目的

本文回答三个问题：演示从零开始时预先准备了哪些数据；每类数据的固定值是什么；哪些值并非种子，而是在每次运行时输入或由系统生成。

本演示的唯一字段合同是 `FPMS_Automation_Skeleton_Pack/data/testcases/demo_v6_ui_parity_v1.json`（`fpms.demo-v6-ui-parity/v1`）。它逐项冻结 103 个输入/来源字段与 30 个可见输出字段的 `EXPLICIT_INPUT`、`SOURCE_BOUND`、`APP_GENERATED` 分类、控件、来源选择器和 normalization。完整字段键索引见 Runbook“冻结的 UI-only 执行合同”；本文的值表不得覆盖或重新解释该 JSON。

为避免把一次演示结果误当作基础数据，本文使用以下四类术语：

| 类型 | 含义 | 每次演示前是否保留 | 例子 |
| --- | --- | --- | --- |
| 系统种子 | 产品运行所需、与某个演示案件无关的基础目录 | 保留 | 60 类官方来文目录、管理员账号 |
| Runtime bundle 种子 | 经固定 manifest 和 authority 绑定的本地合成输入 | 保留并校验摘要 | 模板、12 份合成证据、官费费率簿、服务费价目 |
| 场景 Runtime 输入 | 演示脚本在 fresh run 中录入的业务值 | 不预写入数据库；每轮重新录入 | 客户名称、案名、账单日期、两笔回款 |
| 每轮生成数据 | 系统在执行流程时创建的业务对象和技术标识 | 每轮清空 | 客户 ID、案件 UUID、草单 ID、活动、账单、核销 |

> 事实边界：本文记录的是本地技术排练的合成输入，不代表客户授权、生产数据、官方提交、正式报价、正式官费来源激活或官方缴费成功。

## 2. Runtime bundle 身份与授权边界

### 2.1 Bundle manifest

| 字段 | 值或校验规则 |
| --- | --- |
| `schema_version` | `fpms.demo-input-bundle/integrated-a-v2` |
| `bundle_id` | `fpms-integrated-a` |
| `bundle_version` | `2026.08.21` |
| `classification` | `DEMO_ONLY` |
| `purpose` | `LOCAL_INTEGRATED_A_E2E` |
| `valid_from` | `2026-08-21` |
| `valid_until` | `2026-09-30` |
| `decision_version` | `DEC-INTEGRATED-DEMO-A-20260821` |
| `decision_ref` | `docs/product/v8/customer-decisions/2026-08-21-integrated-demo-a-written-spec-acceptance.txt` |
| 来源标签 | `本地合成技术排练输入` |
| `source_ref` | `synthetic-integrated-a-input` |
| `source_version` | `2026.08.21` |
| `source_sha256` | `cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc` |
| manifest SHA-256 | 由每次 materialize 后的 `manifest.json` 计算并传给 runner；不是跨运行固定种子 |
| 设计契约 SHA-256 | `bfcf7497f91613d4e20bec6b42ce0be60c6c1267059d28c90825106a27481ae6` |

声明能力：`FICTIONAL_LIFECYCLE_EVIDENCE`、`INTERNAL_TEMPLATE_PREVIEW`、`SERVICE_PRICE_TO_OBLIGATION`。

### 2.2 Bundle authority

| 字段 | 值或校验规则 |
| --- | --- |
| `schema_version` | `fpms.demo-bundle-authority/v1` |
| `status` | `APPROVED` |
| `authority_classification` | `SYNTHETIC_TEST_ONLY` |
| `approved_by` | `synthetic-test-fixture-generator` |
| `approved_at` | `2026-08-16T12:00:00+08:00` |
| `decision_sha256` | `731566d51b56eed1c6b9bf2c1b1b32505f14e64347dca500dd851d66dddbe3d5` |
| authority SHA-256 | 由当前 `authority.json` 计算，并与当前 manifest 交叉绑定；不是跨运行固定种子 |

`APPROVED` 只表示该合成 bundle 可用于本地技术排练。authority 文件没有授予客户激活资格，且分级明确为 `SYNTHETIC_TEST_ONLY`；因此不得将它解释为客户已授权的正式输入。

## 3. 统一客户与案件场景

以下字段由演示 runner 在 fresh run 中录入，属于“场景 Runtime 输入”，不是预存在业务表中的案件种子。

| 对象 | 字段 | 值或规则 |
| --- | --- | --- |
| 客户 | 客户名称 | `澄岳智造技术（苏州）有限公司` |
| 客户 | 客户编码 | `CYZN-<run suffix>`；后缀每轮唯一 |
| 客户 | 客户邮箱 | `service@chengyue-ip.example` |
| 联系人 | 姓名 | `周岚` |
| 联系人 | 职务 | `知识产权经理` |
| 联系人 | 邮箱 | `zhou.lan@chengyue-ip.example` |
| 联系人 | 手机 | 不设固定种子值，不虚构 |
| 案件 | 案号 | `CYIP-CN-INV-<run suffix>`；后缀每轮唯一 |
| 案件 | 案名 | `一种柔性制造产线中视觉检测工位的自适应标定方法` |
| 案件 | 案件类型 | 普通案件（系统默认） |
| 案件 | 专利类别 | 发明 |
| 案件 | 流向 | 中国国内 |
| 案件 | 第一申请人 | `澄岳智造技术（苏州）有限公司` |
| 案件 | 费减 | 不减免（`0`） |
| 案件 | 证件号、地址、邮编 | 不提供；演示不得自行补造 |

账号边界：本地系统保留管理员用户名 `admin`，并在运行时创建证据复核用户 `demo_evidence_reviewer`；密码每轮生成且不得写入本文、Runbook、截图或演示输出。

## 4. 文书模板种子

| 字段 | 固定值 |
| --- | --- |
| 消费者 | `DOCUMENT_RENDER` |
| 模板代码 | `DEMO_INTEGRATED_LETTER_1` |
| 模板组 | `INTERNAL_DEMO` |
| 语言 | `zh-CN` |
| 文件 | `templates/integrated-demo-letter.docx` |
| 媒体类型 | `application/vnd.openxmlformats-officedocument.wordprocessingml.document` |
| 大小 | `36,707` bytes |
| SHA-256 | 运行时读取当前生成的 DOCX 并写入 manifest；生成器可能改变容器元数据，因此不得写死历史摘要 |
| 变量 | `case_no`、`client_name` |

模板只用于内部文书预览；生成的预览文件和其摘要属于每轮输出，不是新的种子。

## 5. 生命周期证据种子（12 份）

所有文件均为 `application/pdf`，分级均为 `FICTIONAL_DEMO_EVIDENCE`。日期用于演示流程排序和期限验证，不是对真实官方事件的陈述。

| # | 证据键 | 中文名称 | 时间或期限 | 大小（bytes） | SHA-256 |
| ---: | --- | --- | --- | ---: | --- |
| 1 | `FILING_FINAL_SUBMISSION` | 发明专利请求书及申请文件 | 生效 `2026-08-01 09:00:00` | 1,095 | `8b46d75006d32b5c6dadd48e1b3255133370d3055bf49d08f25bbfc7a794eed2` |
| 2 | `FILING_RECEIPT` | 发明专利申请递交回执 | 收件 `2026-08-02 10:00:00` | 1,083 | `1f56a981b7557520be4ac0a8b07cde5eadd72cd17be3eecbad7742ba06475948` |
| 3 | `ACCEPTANCE_NOTICE` | 发明专利申请受理通知书 | 生效 `2026-08-03 09:00:00` | 1,086 | `30e230dc3f9f224a08814337ee478806c3385d01103b469adaa22433a8251da8` |
| 4 | `PRELIMINARY_EXAMINATION_SOURCE` | 发明专利申请初步审查合格通知书 | 生效 `2026-08-04 09:00:00` | 1,102 | `08974fae3ab69d452117854448b2ca1e730dc0da742c2b0802076a20a462647c` |
| 5 | `PUBLICATION_NOTICE` | 发明专利申请公布通知书 | 生效 `2026-08-05 09:00:00` | 1,087 | `abebc9aaaa5d1d970fb50ecc8d870e047fcbca8cf538ef003f004aa1312f7a6b` |
| 6 | `SUBSTANTIVE_EXAMINATION_SOURCE` | 发明专利申请进入实质审查阶段通知书 | 生效 `2026-08-06 09:00:00` | 1,102 | `0638cd698fdd0cfa994a61335938a8bf7f691aa61536324f52a4b4316d06a6c3` |
| 7 | `OA_NOTICE_1` | 第一次审查意见通知书 | 生效 `2026-08-07 09:00:00`；期限 `2026-09-22` | 1,083 | `871b94b524bc7e68445321785871a5cb74dffb8036a7e9c928c3c0bb14fe009d` |
| 8 | `OA_RECEIPT_1` | 第一次审查意见答复递交回执 | 收件 `2026-08-08 10:00:00` | 1,084 | `4a2a18080c2167429a09aee36238c2ab09e60a72b9afc7bb780af6e8ed055b69` |
| 9 | `OA_NOTICE_2` | 第二次审查意见通知书 | 生效 `2026-08-09 09:00:00`；期限 `2026-10-23` | 1,083 | `3aa5cf4824c2ba177ce35e34bfb12b18d59839f52809ca5f53270d6badb39dd3` |
| 10 | `OA_RECEIPT_2` | 第二次审查意见答复递交回执 | 收件 `2026-08-10 10:00:00` | 1,084 | `ff5bc7dafe1471764c0635105796a05e897cb5e8d4cddf8679aa41e50a997af4` |
| 11 | `GRANT_NOTICE_ORIGINAL` | 办理登记手续通知书 | 生效 `2026-08-11 09:00:00`；期限 `2026-11-23` | 1,093 | `3c8f584872c144589936bce6db4589b276df5a83591adaeb15f80b5822fb2579` |
| 12 | `GRANT_NOTICE_REPLACEMENT` | 办理登记手续更正通知书 | 生效 `2026-08-12 09:00:00`；期限 `2026-11-24` | 1,096 | `d61d3bf33ca2403e6c77c4a98ccf1dcedb555481acb5f85b3dcdd33b352fe730` |

补充属性：

- 两份 OA 通知的期限来源均为 `MANUAL_OFFICIAL_NOTICE`，状态 `CONFIRMED`，序号分别为 `1`、`2`，来源模板分别为 `DEMO_OA_NOTICE_1`、`DEMO_OA_NOTICE_2`。
- 两份 OA 回执与申请递交回执的类型均为 `RECEIPT_PDF`。
- 原授权通知和更正通知的期限来源均为 `IMPORTED_OFFICIAL_NOTICE`，状态 `CONFIRMED`，来源模板分别为 `DEMO_GRANT_NOTICE_1`、`DEMO_GRANT_NOTICE_2`；更正通知显式 `supersedes=GRANT_NOTICE_ORIGINAL`。
- OA 答复陈述书（Word/PDF）和修改后的权利要求书由每轮运行生成，分级为 `SYNTHETIC_TEST_OUTPUT`，不属于这 12 份输入证据。

### 5.1 Actor upload manifest 的使用

`--ui-session` 启动后，runner 在本轮 actor artifact 中生成 `upload-manifest.json` 和 `upload-files/`。操作者只能从该清单逐行取文件：先按 `evidence_key` 和 `title_zh_cn` 找到 Runbook 所需证据，再使用同一行的绝对 `path` 上传，并核对 `classification`、`media_type`、`size_bytes` 与 `sha256`。不得使用仓库 bundle 原路径、另一 actor 或上一轮 artifact。

每行 `metadata` 固定包含 `effective_at`、`received_at`、`receipt_kind`、`official_due_date`、`official_due_date_source`、`official_due_date_status`、`oa_sequence`、`source_template_code`、`supersedes_role`；不适用字段为 `null`。12 行非空 metadata 如下，金额、日期和来源不因 upload manifest 改变：

| # | `evidence_key` | 本行非空 `metadata` |
| ---: | --- | --- |
| 1 | `FILING_FINAL_SUBMISSION` | `effective_at=2026-08-01T09:00:00` |
| 2 | `FILING_RECEIPT` | `received_at=2026-08-02T10:00:00`; `receipt_kind=RECEIPT_PDF` |
| 3 | `ACCEPTANCE_NOTICE` | `effective_at=2026-08-03T09:00:00` |
| 4 | `PRELIMINARY_EXAMINATION_SOURCE` | `effective_at=2026-08-04T09:00:00` |
| 5 | `PUBLICATION_NOTICE` | `effective_at=2026-08-05T09:00:00` |
| 6 | `SUBSTANTIVE_EXAMINATION_SOURCE` | `effective_at=2026-08-06T09:00:00` |
| 7 | `OA_NOTICE_1` | `effective_at=2026-08-07T09:00:00`; `official_due_date=2026-09-22`; `official_due_date_source=MANUAL_OFFICIAL_NOTICE`; `official_due_date_status=CONFIRMED`; `oa_sequence=1`; `source_template_code=DEMO_OA_NOTICE_1` |
| 8 | `OA_RECEIPT_1` | `received_at=2026-08-08T10:00:00`; `receipt_kind=RECEIPT_PDF` |
| 9 | `OA_NOTICE_2` | `effective_at=2026-08-09T09:00:00`; `official_due_date=2026-10-23`; `official_due_date_source=MANUAL_OFFICIAL_NOTICE`; `official_due_date_status=CONFIRMED`; `oa_sequence=2`; `source_template_code=DEMO_OA_NOTICE_2` |
| 10 | `OA_RECEIPT_2` | `received_at=2026-08-10T10:00:00`; `receipt_kind=RECEIPT_PDF` |
| 11 | `GRANT_NOTICE_ORIGINAL` | `effective_at=2026-08-11T09:00:00`; `official_due_date=2026-11-23`; `official_due_date_source=IMPORTED_OFFICIAL_NOTICE`; `official_due_date_status=CONFIRMED`; `source_template_code=DEMO_GRANT_NOTICE_1` |
| 12 | `GRANT_NOTICE_REPLACEMENT` | `effective_at=2026-08-12T09:00:00`; `official_due_date=2026-11-24`; `official_due_date_source=IMPORTED_OFFICIAL_NOTICE`; `official_due_date_status=CONFIRMED`; `source_template_code=DEMO_GRANT_NOTICE_2`; `supersedes_role=GRANT_NOTICE_ORIGINAL` |

会前必须再次核对 bundle `valid_until=2026-09-30`。当前日期晚于该值、清单不是恰好 12 行、任一清单摘要或文件摘要不匹配时，立即停止，不得继续 actor 会话。

## 6. 官费来源与费率种子

### 6.1 费率簿身份

| 字段 | 固定值 |
| --- | --- |
| 来源机构 | `CNIPA` |
| 费率簿代码 | `CNIPA-GRANT-DEMO-V6` |
| 版本 | `2026.03.30` |
| 发布日 / 生效日 | `2026-03-30` |
| 失效日 | `null` |
| 来源参考 | `https://www.cnipa.gov.cn/art/2026/3/30/art_1518_205552.html` |
| 费率簿 SHA-256 | `ddeafdef210787c6e5a9a1b4394fa727ce591eccfe07fe9404485fbaebdeab3d` |

### 6.2 官费行

| 费用代码 | 名称 | 类型 | 币种 | 金额 | 计价 | 可费减 | 行 SHA-256 |
| --- | --- | --- | --- | ---: | --- | --- | --- |
| `CNIPA-GRANT-REGISTRATION` | 授权登记费 | `GOV` | CNY | 900.00 | `FIXED` | `false` | `7291641854197baebb55f1fc9d87d6dab8439dfe626c270cb034f1fac335b449` |
| `CNIPA-GRANT-ANNOUNCEMENT` | 授权公告印刷费 | `GOV` | CNY | 50.00 | `FIXED` | `false` | `43c65522c3bcd30d030ccabf5a795acabe5b7249c436d06d964e98d77ec1902f` |
|  | **合计** |  | **CNY** | **950.00** |  |  |  |

两行状态均为 `ACTIVE`、`enabled=true`。演示先进行 digest-bound 预览，确认后才创建 GOV obligation 和只读 GOV 草单。

> 官费事实边界：bundle 中的标题为 `Synthetic CNIPA official fee source fixture`。该快照虽然绑定 CNIPA 来源参考和摘要，仍只是演示用 runtime fixture；它不证明生产环境已激活正式官费源。演示中的 PAY 只表示办理指示，GOV 缴费登记状态为 `REGISTERED_PENDING_OFFICIAL_EVIDENCE`，官方回执、凭证和发票字段均为 `null`。

## 7. 服务费价目种子与调整输入

| 代码 | 名称 | 币种 | 单价 | 初始数量 | 最终数量 | 可调整 | 来源 SHA-256 |
| --- | --- | --- | ---: | ---: | ---: | --- | --- |
| `FWSQDJ001` | 授权登记阶段代理服务费 | CNY | 1,200.00 | 1 | 1 | `false` | `dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd` |
| `FWSQDJ002` | 授权登记附加文件处理服务费 | CNY | 300.00 | 1 | 2 | `true` | `ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff` |

共同来源：`synthetic-integrated-a-rate`，版本 `2026.08.21`。共同免责声明：`仅用于本地合成技术排练，不是正式报价或官方费用。`

服务费计算：

- 初始：`1,200.00 × 1 + 300.00 × 1 = 1,500.00 CNY`。
- 唯一允许的演示调整：将 `FWSQDJ002` 数量从 `1` 改为 `2`。
- 调整原因：`客户确认增加一份附加文件处理`。
- 锁定后：`1,200.00 × 1 + 300.00 × 2 = 1,800.00 CNY`。

官费和服务费是同案的两条独立轨道：官费草单只读；服务费调整必须留下独立审计活动，不能用通用编辑绕过。

## 8. 账单、回款与核销 Runtime 输入

以下数值在每轮运行中重新录入；业务编号含唯一后缀，因此不是固定种子 ID。

| 对象 | 字段 | 值或规则 |
| --- | --- | --- |
| AR 账单 | 账单号 | `AR-CYZN-<run suffix>` |
| AR 账单 | 金额 | 读取锁定 SERVICE 草单：`1,800.00 CNY` |
| AR 账单 | 账单日 | `2026-08-25` |
| AR 账单 | 到期日 | `2026-09-24` |
| 第一笔回款 | 回款号 | `RCPT-CYZN-<run suffix>-01` |
| 第一笔回款 | 银行流水号 | `BTR-CYZN-<run suffix>-01` |
| 第一笔回款 | 金额 / 日期 / 方式 | `1,200.00 CNY` / `2026-08-25` / `BANK_TRANSFER` |
| 第一笔回款 | 备注 | `澄岳智造技术（苏州）有限公司第一笔客户回款` |
| 第一笔核销 | 金额 | `1,200.00 CNY`；核销后账单为 `PARTIALLY_SETTLED`，余额 `600.00 CNY` |
| 第二笔回款 | 回款号 | `RCPT-CYZN-<run suffix>-02` |
| 第二笔回款 | 银行流水号 | `BTR-CYZN-<run suffix>-02` |
| 第二笔回款 | 金额 / 日期 / 方式 | 必须读取权威账单余额 `600.00 CNY` / `2026-08-26` / `BANK_TRANSFER` |
| 第二笔回款 | 备注 | `澄岳智造技术（苏州）有限公司第二笔客户回款` |
| 第二笔核销 | 金额 | `600.00 CNY`；核销后账单为 `SETTLED`，余额 `0.00 CNY` |

验证等式：`1,200.00 + 600.00 = 1,800.00 CNY`。登记 Payment 不会自动减少账单余额；只有创建有效 Offset 才会改变结清状态。

兼容字段说明：bundle 顶层仍有历史字段 `first_receipt_amount=1000.00`。该字段不属于 V6 生效场景，V6 的权威第一笔回款是 `1,200.00 CNY`，不得在本演示中使用 1,000.00。

## 9. 系统官方来文目录种子（60 类）

来源标签：`相关流程操作-20260526.docx [P0101] TABLE 001`。目录行均为来文方向 `IN` 且数据库目录状态 `enabled=true`；这只表示目录可被识别，不代表 UI 向导允许执行全部类型。

当前 V6 可执行类型为：`001`、`003`、`005`、`009`、`021`、`024`、`029`、`031`、`034`。其余类型只作参考识别，UI 中不可作为本轮流程动作执行。

| 代码 | 名称 | 外部代码 |
| --- | --- | --- |
| `001` | 受理通知-电子 | `200101` |
| `002` | 补正通知 | `220704,200029,210302,220302,230301` |
| `003` | 第一次审查意见通知书 | `210401,210402` |
| `004` | 第一次审查意见通知书（新型） | `220301` |
| `005` | 第二次审查意见通知书 | `210403` |
| `006` | 初步审查合格 | `210304` |
| `007` | 公布通知书 | `210305` |
| `008` | 公布及进入实审通知 | `210308` |
| `009` | 授权通知书-电子 | `200602` |
| `010` | 专利证书 | `400001,400002,400003` |
| `011` | 驳回决定 | `210407,200305,210408` |
| `012` | 视为撤回 | `200022` |
| `013` | 视为放弃 | `200601` |
| `014` | 专利权终止通知 | `200702` |
| `015` | 恢复权利通知书 | `200026` |
| `016` | 年费缴费通知书 | `200701` |
| `017` | 复审请求受理通知书 | `200905` |
| `018` | 复审通知书 | `200908A,200924` |
| `019` | 复审决定书 | `200912` |
| `020` | 复审补正通知书 | `200907` |
| `021` | 第三次审查意见通知书 | `210403` |
| `022` | 变更手续合格通知 | — |
| `023` | 手续合格通知书 | `200028` |
| `024` | 第四次审查意见通知书 | `210403` |
| `025` | 延长期限审批通知书 | `200024` |
| `026` | 实审期限届满前通知 | `210306` |
| `027` | 向外国申请专利保密审查通知 | `210326` |
| `028` | 国际申请进入中国通知 | `250302` |
| `029` | 第五次审查意见通知书 | `210403` |
| `030` | 第一次审查意见通知书（外观） | `220301` |
| `031` | 费用减缓审批通知书 | `200021` |
| `032` | 视为未要求优先权通知 | `200302` |
| `033` | 进入实审通知 | `210307` |
| `034` | 缴纳申请费通知书 | `200103` |
| `035` | PPH审查决定 | `210419` |
| `036` | 无效口审通知 | — |
| `037` | 改正译文错误通知书 | `210409` |
| `038` | 分案通知 | — |
| `039` | 予以优先审查通知书 | — |
| `040` | 复审案件结案通知书 | `200913` |
| `041` | 向外国申请专利保密审查决定书 | `21032701` |
| `042` | 办理恢复权利手续补正通知书 | `200032` |
| `043` | 审查业务专业便函 | `200020;200025;210417` |
| `044` | 视为未提出通知书 | `200023` |
| `045` | 专利登记簿副本 | — |
| `046` | 国际申请初审合格 | `250304` |
| `047` | 避免重复授予专利权的通知书 | `210415` |
| `048` | PCT检索报告 | — |
| `049` | 修改文件缺陷通知 | — |
| `050` | 国际检索单位书面意见 | — |
| `051` | 传送检索报告和书面意见的通知 | — |
| `052` | 国际申请号和申请日通知 | — |
| `053` | 关于缴纳规定费用通知 | — |
| `054` | 收到记录本通知 | — |
| `055` | 收到检索本的通知 | — |
| `056` | PCT电子提交收据 | — |
| `057` | 国际公布通知 | — |
| `058` | 传送优先权文件通知 | — |
| `059` | 指定局不适用30个月进入期限的通知 | — |
| `060` | 无其他可适用表格时的通知书 | — |

## 10. 明确不属于种子的数据

下列数据每轮都必须由运行生成，不能复制上一轮值，也不能写死进本文：

- run ID、数据库文件、证据目录、客户/联系人/案件主键、所有 UUID 和自增 ID。
- 客户编码、案号、账单号、回款号、银行流水号中的 `<run suffix>`。
- 文书预览摘要、OA 答复输出摘要、附件版本 ID、活动 ID、任务 ID 和期限记录 ID。
- GOV obligation、GOV 草单、PayList、GovPayment、SERVICE 草单、Bill、Payment、Offset 的对象 ID。
- 登录密码、token、cookie、幂等键和其他凭据。
- 每轮网络与 console 采集结果。

2026-08-25 的冻结技术排练 `integrated-r1-f4a9ef065058` 可作为验证样例：11 个阶段通过，绑定 12 份输入证据，官费为 950.00 CNY，服务费从 1,500.00 调整到 1,800.00 CNY，两笔回款/核销为 1,200.00 和 600.00 CNY，最终账单 `SETTLED`、余额 0.00，`network_errors=[]`、`console_errors=[]`。这些结果及其 manifest/authority/template 摘要只证明该次运行，不会转化为下一轮种子或下一轮期待摘要。

## 11. 每次演示前的新建规则与演示后清理边界

### 保留并重新校验

- 系统账号骨架和 60 类官方来文目录。
- runtime bundle 的输入契约、authority、模板、12 份证据、官费费率簿和服务费价目。
- 本文列出的稳定版本、有效期、分类与来源摘要；manifest、authority 和模板文件摘要必须从当前 materialized bundle 读取并交叉校验，任一不符即停止。

### 新建与独立清理

- 旧 run 不作为新演示的 reset 输入，也不在 preflight 中删除；失败 artifact 必须保留。
- 创建新的 run root、数据库、WAL/SHM 路径、业务号、证据目录和动态凭据；不得在旧数据库中按表删行后复用。
- 演示结束后，只能通过已验证的 exact run root 执行独立 cleanup/归档；不得全表 truncate、按业务前缀匹配或宽泛删除目录。

### Fresh-run 停止条件

出现以下任一情况，不进入客户共享页面：

- 数据库不是零业务行，或发现上一轮业务号、UUID、附件或财务对象。
- manifest、authority、模板、证据、费率簿或价目摘要不匹配。
- bundle 已过有效期、分类不是 `SYNTHETIC_TEST_ONLY`，或被误标为客户可激活。
- 页面首次加载出现 Network Error、console error 或预检失败。
- 官费被展示为已获官方凭证，或服务费结清被解释为官费已支付。

## 12. 演示人员快速核对表

| 核对项 | 期待值 |
| --- | --- |
| 业务数据库 | 0 条演示业务数据 |
| Bundle | `fpms-integrated-a` / `2026.08.21`；当前 manifest/authority 精确摘要交叉匹配，不使用历史前缀 |
| 证据 | 12 份，全部 `FICTIONAL_DEMO_EVIDENCE` |
| 官费 | 2 行；900.00 + 50.00 = 950.00 CNY |
| 服务费 | 2 行；初始 1,500.00，调整后 1,800.00 CNY |
| 客户回款 | 1,200.00 + 权威余额 600.00 = 1,800.00 CNY |
| 最终服务费账单 | `SETTLED`；余额 0.00 CNY |
| 最终官费状态 | `REGISTERED_PENDING_OFFICIAL_EVIDENCE`；官方凭证字段为 `null` |
| 客户屏幕 | 只显示正常业务页面，不显示隐藏演示控制路由或主持人控制页面 |
| 技术健康 | Network Error 与 console error 均为 0 |

本文只说明输入数据和边界；实际演示步骤、话术、UI 操作、期待结果与逐阶段停止条件以 `docs/postdemo/demo-lifecycle-customer-v6-runbook.md` 为准。
