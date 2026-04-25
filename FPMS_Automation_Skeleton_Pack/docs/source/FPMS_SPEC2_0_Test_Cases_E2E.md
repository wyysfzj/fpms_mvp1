# FPMS SPEC 2.0 测试用例总集（E2E 编排版）

> 生成日期：2026-04-12
> 适用对象：产品 QA、手工测试、自动化测试（Codex / API / UI / DB 校验）
> 来源：基于你提供的 **FPMS SPEC 2.0** 逐模块、逐场景拆解而成。
> 组织方式：优先按 **Wave 0 → A → B → C → G0 → D → E → F → G → H → X** 推进，确保既可沿业务主线执行，也可按模块拆分回归。

---

## 1. 文档目标

本测试集的目标有三层：

1. **功能覆盖**：覆盖 FPMS SPEC 2.0 中模块 1–8 的核心功能、字段规则、联动逻辑、报表和权限。
2. **流程覆盖**：覆盖 E2E 场景 **A–H + 授权场景 G0**，确保从立案、递交、OA、授权、年费、无效/诉讼、预收款、催款/坏账到顾问项目都能闭环。
3. **可执行覆盖**：每条用例都同时考虑：
   - 人工执行可读性
   - 自动化执行可落地性
   - 数据库/服务层断言点
   - 批处理/报表/文档输出的可验证性

---

## 2. 使用说明

### 2.1 用例粒度

- **详细用例数**：155
- **边界条件矩阵**：20 组
- **覆盖类型**：Happy Path / Unhappy Path / Boundary / 权限 / 审计 / 报表 / 状态机 / 批处理

### 2.2 自动化约定

建议自动化采用以下分层：

- **API/Service 层**：字段校验、状态机、金额计算、任务生成、提成结算、报表查询。
- **UI 层**：表单输入、批处理、向导、权限可见性、导出/模板下载、附件上传下载。
- **DB 断言层**：`T_Case`、`T_Document`、`T_Task`、`T_FeeDraft`、`T_Bill`、`T_Payment`、`T_Offset`、`T_CaseReceipt`、`T_Commission` 等核心表。
- **文件/报表层**：Word/Excel/PDF 导出、模板渲染、电子附件落库、催款函/交接单/信封输出。

### 2.3 动态编号规则

为避免重复数据污染，自动化执行时请将以下字段统一加 `${RUN_ID}`：

- `CaseNo`
- `BillNo`
- `PayNo`
- `DunningNo`
- 需要唯一性的 `TemplateCode/Code`（若在临时环境下创建）

### 2.4 推荐执行顺序

1. **Wave 0**：主数据、参数、模板、权限、信头准备
2. **Wave A**：新案主干
3. **Wave B**：OA
4. **Wave C**：PCT 国际 → 国家阶段
5. **Wave G0**：授权
6. **Wave D**：年费
7. **Wave E**：无效 / 诉讼
8. **Wave F**：预收款
9. **Wave G**：催款 & 坏账
10. **Wave H**：顾问 / 检索
11. **Wave X**：查询 / 报表 / 审计 / 手工账单 / 状态机回归

---

## 3. 测试环境与前置假设

- 系统支持按角色登录：Admin / Formalities / Agent / Limited Editor / Finance / Supervisor。
- 模板生成、报表导出、附件存储在测试环境可用；若无法真实发邮件，可采用**文件生成 + 状态标记**替代。
- 定时/批处理任务（如年费滚动生成、PCT 进入初始化）应支持：
  - 手工触发
  - 或通过服务接口同步触发
- 如 UI 无法直接看到后台字段，自动化应补充 DB 或接口断言。
- 若部分规则在实现中为“警告或强校验可配置”，测试需同时覆盖：
  - **阻断模式**
  - **确认后强制保存模式**

---

## 4. 共享测试数据集

### 4.1 用户与角色
| 数据ID | 角色 | 账号示例 | 说明 |
| --- | --- | --- | --- |
| DS-U-ADM | Admin | admin.fpms | 全权限；配置/高危操作 |
| DS-U-FM-01 | Formalities | formalities1 | 案卷/文档/批处理/时限维护 |
| DS-U-AG-01 | Agent | agent.primary | 主办代理人 |
| DS-U-AG-02 | Agent | agent.secondary | 协办代理人 |
| DS-U-LMT-01 | Limited Agent | agent.limited | 仅 CaseEditLimited |
| DS-U-FI-01 | Finance | finance1 | 费用/账单/收款/官费清单 |
| DS-U-SP-01 | Supervisor | supervisor1 | 监督任务和审批 |

### 4.2 国家/地区
| 数据ID | Code | 名称 | 默认币种 | 国内 | PCT成员 |
| --- | --- | --- | --- | --- | --- |
| DS-CTY-CN | CN | 中国 | CNY | 是 | 是 |
| DS-CTY-US | US | 美国 | USD | 否 | 是 |
| DS-CTY-JP | JP | 日本 | JPY | 否 | 是 |
| DS-CTY-HK | HK | 中国香港 | HKD | 否 | 否/按实现 |
| DS-CTY-EP | EP | 欧洲专利局 | EUR | 否 | 是 |

### 4.3 客户
| 数据ID | 名称 | 类型 | 国家 | 默认币种 | 说明 |
| --- | --- | --- | --- | --- | --- |
| DS-CL-001 | 北京创新科技有限公司 | 直接客户 | CN | CNY | 有有效默认文件地址和账单地址 |
| DS-CL-002 | Wilson & Partners LLP | 代理所 | US | USD | 用于 ForeignAgent |
| DS-CL-003 | Global Pharma Inc. | 直接客户 | US | USD | 用于涉外/PCT |
| DS-CL-004 | Dormant Client | 直接客户 | CN | CNY | 含一条停用地址用于负例 |

### 4.4 申请人
| 数据ID | 名称 | 申请人类型 | 国家 | HasGeneralPower | IsJobInvention |
| --- | --- | --- | --- | --- | --- |
| DS-AP-001 | 北京创新科技有限公司 | 法人 | CN | 是 | 是 |
| DS-AP-002 | 张三 | 自然人 | CN | 否 | 否 |
| DS-AP-003 | ACME Biotech Inc. | 法人 | US | 否 | 否 |
| DS-AP-004 | Osaka Machines KK | 法人 | JP | 否 | 否 |

### 4.5 文档模板种子
| 数据ID | TemplateCode | DocType | 关键配置 | 备注 |
| --- | --- | --- | --- | --- |
| DS-TPL-DOC-001 | OA_NOTICE | OFFICIAL_IN | StatusEffect=OA1/OA2 | DeadlineTemplate=OA_REPLY_LIMIT |
| DS-TPL-DOC-002 | OA_REPLY | OFFICIAL_OUT | StatusRestore=SUB_EXAM | ReplyTo=OA_NOTICE |
| DS-TPL-DOC-003 | GRANT_NOTICE | OFFICIAL_IN | StatusEffect=GRANTED | InputField=IssueDate/GrantDate/GrantNo/FirstAnnuityYear/ValidUntil |
| DS-TPL-DOC-004 | GRANT_FEE_NOTICE | CLIENT_OUT | 授权费通知函 | 附件模板可生成 |
| DS-TPL-DOC-005 | ANNUITY_NOTICE | CLIENT_OUT | 年费通知函 | 附件模板可生成 |
| DS-TPL-DOC-006 | INVALID_REQUEST | OFFICIAL_OUT | StatusEffect=INVALID_FILED | FeeDraftType=INVALID_FEE |
| DS-TPL-DOC-007 | INVALID_DECISION | OFFICIAL_IN | DecisionResult/AffectedClaims | 更新无效案和原案状态 |
| DS-TPL-DOC-008 | DUNNING_LETTER | CLIENT_OUT | 催款函 | 来源 T_Dunning |

### 4.6 时限模板种子
| 数据ID | Code | Base | 用途 |
| --- | --- | --- | --- |
| DS-TPL-TASK-001 | APPLY_FEE_LIMIT | CASE_EVENT/FILING_DATE | 新案申请费时限 |
| DS-TPL-TASK-002 | EXAM_REQUEST_LIMIT | FILING_DATE | 实审请求时限 |
| DS-TPL-TASK-003 | OA_REPLY_LIMIT | DISPATCH_DATE/OfficialDueDate | OA 答复时限 |
| DS-TPL-TASK-004 | GRANT_CERT_FEE_LIMIT | GRANT_DATE/IssueDate | 授权费时限 |
| DS-TPL-TASK-005 | PCT_NATIONAL_ENTRY_LIMIT | CUSTOM/CASE_EVENT | 国家阶段进入时限 |
| DS-TPL-TASK-006 | INVALID_DEFENSE_LIMIT | DISPATCH_DATE | 无效答辩/举证期限 |

### 4.7 标准费率种子
| 数据ID | Code | Group | FeeType | CalcMode | 说明 |
| --- | --- | --- | --- | --- | --- |
| DS-RATE-001 | CN_APPL_BASE | APPLY | GOV | FIXED | 国内基础申请官费 |
| DS-RATE-002 | CN_APPL_SERVICE_BASE | APPLY | SERVICE | FIXED | 新案申请服务费 |
| DS-RATE-003 | CN_APPL_EXTRA_CLAIM | APPLY | GOV | BY_CLAIMS | 超 10 项加收 |
| DS-RATE-004 | CN_GRANT_REG | GRANT | GOV | FIXED | 授权登记费 |
| DS-RATE-005 | CN_GRANT_CERT | GRANT | GOV | FIXED | 证书费 |
| DS-RATE-006 | CN_STAMP_DUTY | GRANT | GOV | FIXED | 印花税 |
| DS-RATE-007 | CN_ANNUITY_YEAR | ANNUITY | GOV/SERVICE | BY_YEAR | 年费分档 |
| DS-RATE-008 | OA_SERVICE_STANDARD | INTERMEDIATE | SERVICE | FIXED | OA 答复服务费 |
| DS-RATE-009 | INVALID_REQUEST_FEE | INVALID | GOV/SERVICE | FIXED | 无效请求费 |
| DS-RATE-010 | CONSULT_FIXED | CONSULT | SERVICE | FIXED | 顾问固定报价 |
| DS-RATE-011 | CONSULT_SENIOR_HOUR | CONSULT | SERVICE | FIXED | 高级顾问小时费 |

### 4.8 提成规则种子
| 数据ID | 适用范围 | BaseMode | 比例 | 备注 |
| --- | --- | --- | --- | --- |
| DS-COM-001 | NORMAL/IN_IN/INVENTION | BY_SERVICE_FEE | S1=30%, S2=20% | WaitPay=true |
| DS-COM-002 | OA | BY_SERVICE_FEE | S1=20%, S2=0~10% | 按阶段追加 |
| DS-COM-003 | GRANT | BY_SERVICE_FEE | S1=0, S2=20% | 授权节点可结算 |
| DS-COM-004 | CONSULTING/SEARCH | FIXED or BY_SERVICE_FEE | S1=40%, S2=0 或 30/10 | 顾问规则 |

### 4.9 场景案卷种子
| 数据ID | CaseType | 初始状态 | 用途 |
| --- | --- | --- | --- |
| DS-CASE-A-001 | NORMAL/IN_IN/INVENTION | NOT_FILED | 新案申请主线 |
| DS-CASE-B-001 | NORMAL/IN_IN/INVENTION | SUB_EXAM | OA 场景 |
| DS-CASE-C-INTL | PCT_INTL | PCT_INTL_EXAM | PCT 国际案 |
| DS-CASE-C-NAT | PCT_NATIONAL | NOT_FILED | 国家阶段子案 |
| DS-CASE-G0-001 | NORMAL | SUB_EXAM/OA2 | 待授权案 |
| DS-CASE-D-001 | NORMAL | GRANTED | 需年费监视 |
| DS-CASE-E-ORIG | NORMAL | GRANTED | 无效/诉讼原案 |
| DS-CASE-H-001 | CONSULTING/SEARCH | NOT_STARTED/IN_PROGRESS | 顾问/检索项目 |

### 4.10 日期种子
| 数据ID | 含义 | 日期值 | 用途 |
| --- | --- | --- | --- |
| DS-DATE-001 | 收案日 | 2026-04-01 | 新案 |
| DS-DATE-002 | 申请日 | 2026-04-05 | 新案 |
| DS-DATE-003 | 最早优先权日 | 2026-03-15 | 优先权边界 |
| DS-DATE-004 | OA 官方发文日 | 2026-08-15 | OA |
| DS-DATE-005 | OA 官方绝限 | 2026-10-15 | 官方绝限覆盖 |
| DS-DATE-006 | 授权发文日 | 2027-06-20 | GRANT_NOTICE |
| DS-DATE-007 | 授权公告日 | 2027-07-01 | GRANT_NOTICE |
| DS-DATE-008 | 有效期截止 | 2046-04-05 | 20 年示例 |
| DS-DATE-009 | 国家阶段进入日 | 2028-07-15 | PCT_NATIONAL |
| DS-DATE-010 | 年费到期日示例 | 2028-04-05 | Annuity Y1 |

---

## 5. Wave 总览

| Wave/Suite | 说明 | 详细用例数 | 含 Happy | 含 Unhappy | 含 Boundary |
| --- | --- | --- | --- | --- | --- |
| W0 基础配置 | 执行前置：主数据、参数、模板、权限 | 14 | 11 | 4 | 1 |
| A 新案申请 | E2E 场景 A：新案立案 → 递交 → 申请费 → 账单 → 收款 → 提成 | 24 | 12 | 12 | 8 |
| B OA/补正 | E2E 场景 B：OA 来文 → 答复时限 → OA 回复 → 账单/收款 → 提成 | 13 | 11 | 3 | 1 |
| C PCT→国家阶段 | E2E 场景 C：PCT 国际 → 国家阶段计划 → 子案建立 → 接主流水线 | 12 | 9 | 3 | 1 |
| G0 授权阶段 | 授权节点：GRANT_NOTICE → 授权费时限/草单/账单 → 年费初始化 → 提成 | 10 | 8 | 2 | 0 |
| D 年费周期 | E2E 场景 D：多年度滚动年费通知/草单/清单/账单/收款 | 13 | 11 | 4 | 2 |
| E 无效/诉讼 | E2E 场景 E：立案 → 请求/受理/答辩/裁决 → 费用 → 提成 | 14 | 11 | 3 | 0 |
| F 预收款 | E2E 场景 F：预收款池 → 后续冲销 → CaseReceipt → 提成影响 | 10 | 8 | 2 | 1 |
| G 催款与坏账 | E2E 场景 G：逾期 → 催款单/函 → 回款 → 坏账/回收 | 10 | 9 | 2 | 0 |
| H 顾问/检索 | E2E 场景 H：项目立案 → 内部任务/支出 → 草单/账单/收款 → 提成 | 8 | 8 | 1 | 1 |
| X 查询/报表/审计 | 跨模块查询、报表、手工账单、日志、权限、状态机回归 | 27 | 26 | 3 | 1 |

---

## 6. 详细测试用例
### W0 基础配置

执行前置：主数据、参数、模板、权限

| TC ID | P级 | 类别 | 阶段/主题 | 覆盖 | 前置与数据 | 操作摘要 | 预期结果 | 自动化建议 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TC-W0-001 | P0 | Happy | 主数据-客户 | FR-CM-03<br>FR-WD-09<br>FR-WD-10 | 使用 DS-U-ADM 登录；准备 DS-CL-001 基本信息、两条地址、一条联系人。 | 进入“设置→客户维护”，创建客户、默认文件地址、默认账单地址和联系人；保存后再打开编辑页校验。 | 客户、地址、联系人均保存成功；默认地址标记唯一；搜索可按名称命中；后续案卷和账单下拉中可选。 | API+UI；断言 T_Client/T_ClientAddress/T_ClientContact 被创建，默认地址唯一。 |
| TC-W0-002 | P1 | Unhappy/Boundary | 主数据-客户地址 | FR-WD-10<br>V-C-06 | DS-U-ADM；客户 DS-CL-004 含一条停用地址和一条有效地址。 | 将停用地址设为默认账单地址并尝试在案卷中选择；再切换为有效地址重试。 | 停用地址不能被设为有效默认收件地址或在案卷中被使用；切换为有效地址后可正常引用。 | UI+DB；验证停用标志在地址选择器中过滤或阻断。 |
| TC-W0-003 | P1 | Happy | 主数据-申请人 | FR-CM-03 | DS-U-ADM；准备法人申请人 DS-AP-001 和自然人 DS-AP-002。 | 创建申请人主数据并填写名称、国籍、地址、IsLegalEntity、HasGeneralPower、IsJobInvention 等字段；保存并搜索。 | 申请人保存成功；能按名称模糊搜索；HasGeneralPower/IsLegalEntity 在案卷引用时可被带出。 | API+UI；后续案卷测试复用。 |
| TC-W0-004 | P2 | Happy | 主数据-申请人合并 | FR-CM-03 | DS-U-ADM；创建两条近似重复的申请人记录。 | 在“申请人维护”执行合并；保留主记录，确认关联地址/标记字段。 | 重复记录被合并；主记录保留，关联引用不丢失，旧记录不可再被新案选用。 | 建议人工+后台脚本校验引用完整性。 |
| TC-W0-005 | P1 | Happy | 主数据-国家地区 | FR-CM-01<br>FR-FE-01<br>FR-CS-01 | DS-U-ADM；准备 CN/US/JP/HK/EP 数据。 | 维护国家代码、默认币种、IsDomestic、DefaultLanguage、PCT 成员标志；保存后在案卷/费率/报表处引用。 | 国家配置可被案卷、费率、年费和报表使用；Domestic/PCT member 标志在规则分支中可识别。 | API+UI；验证 T_Country 可被下拉引用。 |
| TC-W0-006 | P2 | Happy | 主数据-菌种保藏单位 | FR-CM-05 | DS-U-ADM；准备 DS-BIO-UNIT-001。 | 维护菌种保藏单位编码、中英文名、地址、联系人；保存后在案卷扩展页引用。 | 菌种保藏单位保存成功；在案卷“菌种保藏”标签页可搜索选择。 | UI+API。 |
| TC-W0-007 | P0 | Happy | 业务参数-费率固定金额 | FR-FE-01<br>FR-FE-03 | DS-U-FI-01；准备 CN_APPL_BASE、CN_APPL_SERVICE_BASE。 | 在费率维护中创建 Group=APPLY 的 FIXED 费率，设置 FeeType、DefaultCurrency、DefaultAmount、AllowReduction/AllowDiscount。 | 费率创建成功，可按 Group/Country/CaseType 查询到；后续草单生成时可被命中。 | API+UI；断言 T_FeeRate 基本字段。 |
| TC-W0-008 | P1 | Happy | 业务参数-费率分档 | FR-FE-01<br>FR-FE-03 | DS-U-FI-01；准备 BY_YEAR、BY_CLAIMS、BY_PAGES、COMPOSITE 四类 CalcParams。 | 创建年费分档、超项费、超页费和复合计算费率；保存后执行计算预览或在草单生成中调用。 | 系统能保存 CalcMode/CalcParams；不同模式能被后续草单正确调用。 | 优先 API/服务层自动化；对 CalcParams 做 schema 断言。 |
| TC-W0-009 | P1 | Unhappy | 业务参数-时限模板合法配置 | FR-DL-01<br>V-TM-01<br>V-TM-02<br>V-TM-03<br>V-TM-04 | DS-U-ADM；准备模板代码 APPLY_FEE_LIMIT、OA_REPLY_LIMIT。 | 创建有效模板；再分别尝试 Code 重复、AddYears/AddMonths/AddDays 全为 0、DailyRemind=true 但无 InnerOffset/Remind、DeadlineBase=CUSTOM 但调用端不传 BaseDate。 | 有效模板可保存；重复 Code 被拒；无增量模板被拒；DailyRemind 配置不足被拒；调用端缺 BaseDate 时任务生成失败并给出明确错误。 | API+UI；模板校验优先服务层自动化。 |
| TC-W0-010 | P0 | Happy | 业务参数-文档模板配置 | FR-WD-01<br>FR-WD-03<br>V-TPL-01<br>V-TPL-02<br>V-TPL-03<br>V-TPL-04<br>V-TPL-05 | DS-U-ADM；准备 OA_NOTICE、OA_REPLY、GRANT_NOTICE、ANNUITY_NOTICE 模板与对应 TaskTemplate/FeeRate。 | 创建 DocTemplate，设置 DocType、StatusEffect、StatusRestore、DeadlineTemplateCode、FeeDraftType、FeeItemList、InputFieldList、PlainTemplateID_CN/EN。 | 模板保存成功；字段映射有效；后续向导中默认值、状态联动、任务和草单生成均可被带出。 | UI+API；校验模板定义对象存在。 |
| TC-W0-011 | P1 | Unhappy | 业务参数-文档模板非法配置 | FR-WD-03<br>V-TPL-01<br>V-TPL-02<br>V-TPL-03<br>V-TPL-04<br>V-TPL-05 | DS-U-ADM；准备不存在的 DeadlineTemplateCode、FeeCode、InputField 字段名。 | 分别尝试保存：重复 TemplateCode；不存在的 DeadlineTemplateCode；只配置 StatusRestore 未说明回复逻辑；FeeItemList 引用不存在费率；InputFieldList 引用不存在字段。 | 系统逐项阻止保存并提示具体错误点。 | 服务层自动化最佳；UI 断言错误提示。 |
| TC-W0-012 | P1 | Happy | 文档模板与信头 | FR-WD-09<br>FR-WD-10<br>FR-BL-04 | DS-U-ADM；准备中文/英文 Word 模板与 CN/EN 信头。 | 上传 T_Template，配置 Group/Language/FilePath/Enabled；创建两套 T_LetterHead 并关联到模板。 | 模板和信头均可保存；不同语言模板输出时能正确带出对应抬头。 | 可用文件存在性检查+模板渲染 smoke。 |
| TC-W0-013 | P1 | Happy | 系统参数 | FR-BL-09<br>FR-COM-04<br>FR-COM-05 | DS-U-ADM；准备催款间隔、默认 WaitPay 阈值、退款策略等参数。 | 维护 T_SystemParam（若实现）；分别设置催款间隔、预收款负账单策略、WaitPay 阈值、ForceSettle 默认策略。 | 参数保存成功；相关流程读取到新值，且更新后对新交易生效。 | API/配置读取自动化。 |
| TC-W0-014 | P0 | Happy/Unhappy | 权限矩阵 | FR-CM-06<br>FR-DL-06<br>FR-BL-06 | 准备 DS-U-ADM / DS-U-FM-01 / DS-U-AG-01 / DS-U-LMT-01 / DS-U-FI-01。 | 分别以各角色登录，验证菜单、按钮和高危操作权限：案卷完整编辑、受限编辑、时限取消、反冲销、已缴费修改、坏账标记。 | Admin 拥有全权限；Formalities 具备流程维护权限；Limited Editor 仅见补充信息入口；Finance 无法修改非法业务字段；高危操作仅授权用户可执行。 | UI+权限接口自动化。 |

### A 新案申请

E2E 场景 A：新案立案 → 递交 → 申请费 → 账单 → 收款 → 提成

| TC ID | P级 | 类别 | 阶段/主题 | 覆盖 | 前置与数据 | 操作摘要 | 预期结果 | 自动化建议 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TC-A-001 | P0 | Happy | A1 新案立案-最小必填 | FR-CM-01<br>FR-CM-02<br>V-A-01<br>V-C-01<br>V-C-02 | DS-U-FM-01；客户 DS-CL-001；申请人 DS-AP-001；国家 DS-CN；动态案号 CASE-A-${RUN_ID}-001。 | 进入新案页面，填写 CaseNo、CaseType=NORMAL、PatentCategory=INVENTION、FlowDir=IN_IN、FromCountry=CN、Title_CN、RecvDate、ClientID、1 个申请人并设为主申请人，保存。 | 案卷保存成功；Status 默认 NOT_FILED；T_Case/T_CaseApplicant 创建成功；CreatedBy/CreatedAt 写入；案卷可在高级查询中被检索到。 | UI+API+DB；此案作为场景 A 后续用例的基准案。 |
| TC-A-002 | P1 | Happy | A1 新案立案-完整字段 | FR-CM-02<br>FR-CM-03<br>FR-CM-05<br>V-C-04<br>V-P-01<br>V-P-02<br>V-P-03 | DS-U-FM-01；使用 DS-CL-001、DS-AP-001、DS-AP-003、DS-BIO-UNIT-001；案号 CASE-A-${RUN_ID}-002。 | 创建一件国内发明案，录入中英文名称、客户/申请人/发明人、文件地址/账单地址、2 条优先权、1 条菌种保藏、规格字段、FeeReduction、DiscountRate、NoPower/NoPrioText/RequireHK 等控制标记后保存。 | 保存成功；PrioDate 自动取最早优先权日；GeneralPowerUsed 对有通用委托书的申请人自动勾选或建议勾选；菌种和规格信息持久化；审计字段更新。 | UI+DB；建议检查子表 T_Priority/T_BioDeposit/T_CaseInventor。 |
| TC-A-003 | P0 | Unhappy | A1 案卷号唯一 | FR-CM-01<br>FR-CM-02<br>V-A-01 | 系统中已存在 CASE-A-${RUN_ID}-001。 | 再次创建新案并使用同一 CaseNo 保存。 | 保存被拒绝；提示 CaseNo 已存在；数据库不新增重复 T_Case 记录。 | API+UI；唯一索引/服务校验双断言。 |
| TC-A-004 | P1 | Unhappy | A1 案件类型组合非法 | FR-CM-01<br>V-A-02 | DS-U-FM-01；配置中存在禁止的 CaseType+PatentCategory 组合。 | 创建新案时选择被配置禁止的组合并保存。 | 系统阻止保存并说明非法组合。 | 规则引擎/配置驱动自动化。 |
| TC-A-005 | P0 | Unhappy | A1 涉外必填项 | FR-CM-02<br>FR-CM-03<br>V-A-03<br>V-B-01<br>V-B-02 | DS-U-FM-01；客户 DS-CL-003；外方代理 DS-CL-002；案号 CASE-A-${RUN_ID}-003。 | 创建 FlowDir=IN_OUT 或 OUT_IN 的案件，先不填 ToCountry/ForeignAgentID 保存；再填入一个非“代理所”类型客户作为 ForeignAgent 保存；最后改为合法代理所重试。 | 缺 ToCountry 或 ForeignAgent 时保存被拒；选择非代理所时系统给出警告或阻断；改为合法代理所后保存成功。 | UI+服务层自动化。 |
| TC-A-006 | P0 | Unhappy/Boundary | A1 申请人列表规则 | FR-CM-02<br>V-C-01<br>V-C-02<br>V-C-03 | DS-U-FM-01；准备法人申请人 DS-AP-001、自然人 DS-AP-002。 | 分别测试：无申请人保存；两个申请人都标为主申请人；主申请人为自然人但 ApplicantKind=LEGAL_PERSON；再将 ApplicantKind 调整为 NATURAL_PERSON。 | 无申请人被拒；多个主申请人被拒；ApplicantKind 与第一申请人类型不一致时触发阻断或强确认；一致后保存成功。 | UI+规则自动化；若系统支持强制确认，需覆盖确认/取消两条分支。 |
| TC-A-007 | P1 | Happy/Unhappy | A1 发明人与地址 | FR-CM-03<br>V-C-05<br>V-C-06<br>V-C-07 | DS-U-FM-01；客户 DS-CL-001 含有效默认地址，DS-CL-004 含停用地址。 | 创建案卷时先不填发明人、地址保存；再在需要发明人的国家配置下测试无发明人提示；切换到停用地址保存；最后改回有效地址。 | 在无强校验国家下发明人可为空；强校验国家下提示或阻断；停用地址不能提交；如文档/账单地址均为空则系统给出警告或阻断。 | UI 自动化为主。 |
| TC-A-008 | P0 | Unhappy/Boundary | A1 日期与编号一致性 | FR-CM-02<br>V-D-01<br>V-D-02<br>V-D-03<br>V-D-04<br>V-A-04 | DS-U-FM-01；CASE-A-${RUN_ID}-004；优先权日=2026-03-15。 | 分别测试：Status=PUBLISHED 但无 PubDate/PubNo；Status=GRANTED 但缺 GrantDate/GrantNo/FirstAnnuityYear/ValidUntil；FilingDate 早于优先权日；FilingDate=优先权日；AppNo 使用非法格式。 | 缺公开/授权必要字段时被拒；FilingDate<PrioDate 被拒；FilingDate=PrioDate 可通过；非法 AppNo 格式被拒或报错。 | 服务层规则自动化建议覆盖。 |
| TC-A-009 | P1 | Boundary | A1 规格/费减/折扣边界 | FR-CM-02<br>V-E-01<br>V-E-02 | DS-U-FM-01；CASE-A-${RUN_ID}-005。 | 录入 SpecPages/DrawPages/ClaimCount/ClaimPages/ManuscriptWords=0 保存；再测试大数值、FeeReduction=0/1、DiscountRate=0/1、FeeReduction<0、FeeReduction>1、DiscountRate<0、DiscountRate>1。 | 非负整数和 0 边界可保存；超大值不溢出；费减/折扣在 0..1 范围内可保存；越界时被阻止；ApplicantKind 与费减政策不合理时给警告或阻断。 | 服务层+UI；边界可批量参数化。 |
| TC-A-010 | P0 | Happy/Unhappy | A1 限制修改视图 | FR-CM-06 | DS-U-LMT-01 仅有 CaseEditLimited；已有 CASE-A-${RUN_ID}-001。 | 以受限代理人打开案卷详情，确认仅看到“补充信息”入口；修改 Title_CN、规格字段、发明人列表、备注并保存；尝试修改 CaseNo/Status/FilingDate/AppNo/ClientID。 | 白名单字段可保存并更新 UpdatedBy/UpdatedAt；黑名单字段只读或无法提交；保存不触发状态变更、时限生成、费用草单生成。 | UI+DB；重点断言无副作用。 |
| TC-A-011 | P0 | Happy | A2 批量递交成功 | FR-CM-07<br>FR-CM-04<br>V-BF-01<br>V-BF-02 | 准备 3 件 Status=NOT_FILED 的国内新案；其中 1 件为发明案，1 件为实用新型；GenerateList=true。 | 进入案件递交批处理，按 CaseType/FlowDir/RecvDate 筛选并勾选 3 案，设置 SubmittedDate=2026-04-05，ApplyExamNow=true，执行批处理。 | 所选案件 Status 由 NOT_FILED 变为 WAITING_RECEIPT；发明案 HasExamRequest=true（如业务限定仅发明有效）；生成递交清单文档并登记 T_Document/T_DocAttachment；后续申请费任务可被触发。 | UI+批处理服务+DB。 |
| TC-A-012 | P0 | Unhappy/Boundary | A2 批量递交校验 | FR-CM-07<br>V-BF-01<br>V-BF-02 | 存在未递交案件，但本次不勾选任何行；另准备 SubmittedDate<RecvDate 和 SubmittedDate=RecvDate 场景。 | 执行批处理时先不勾选记录；再对勾选记录输入早于 RecvDate 的 SubmittedDate；最后改为等于 RecvDate。 | 未勾选时不能执行；SubmittedDate<RecvDate 时阻断或强警告；SubmittedDate=RecvDate 可通过。 | 服务层参数化。 |
| TC-A-013 | P0 | Happy | A3 申请费时限自动生成 | FR-DL-02<br>FR-DL-03<br>FR-DL-10 | CASE-A-${RUN_ID}-001 已完成递交；系统存在 APPLY_FEE_LIMIT 模板。 | 触发新案递交后的任务生成；查看 T_Task 和首页/我的任务视图。 | 生成 APPLY_FEE_LIMIT 任务，带有 BaseDate、Deadline、InnerDeadline、Remind1/2/3、WorkerID、SupervisorID、Status=OPEN；写入 TaskLog(CREATE)。 | API+DB+UI；验证任务在正确用户视图中出现。 |
| TC-A-014 | P1 | Happy/Boundary | A3 时限基准与提醒 | FR-DL-01<br>FR-DL-02<br>V-TM-03<br>V-TM-04 | 配置 APPLY_FEE_LIMIT 使用 CASE_EVENT 或 FILING_DATE 两种模板版本。 | 分别以 FilingDate 和 SubmittedDate 为基准生成任务；验证 DailyRemind 开启时 DailyRemindFrom 的取值；检查提醒日是否基于 INNER/DEADLINE 正确回推。 | 不同 BaseDateSource 下 Deadline/InnerDeadline 计算正确；DailyRemindFrom 落在 InnerDeadline 或 Deadline；提醒日不晚于 Deadline。 | 服务层自动化，适合参数化。 |
| TC-A-015 | P0 | Happy | A4 申请费草单生成 | FR-FE-02<br>FR-FE-03<br>V-FD-01<br>V-FD-02<br>V-FI-01<br>V-FI-03<br>V-FI-05 | CASE-A-${RUN_ID}-001 为国内发明案，ClaimCount=12，FeeReduction=0.15；费率已配置 APPLY 基础官费、超项费、服务费。 | 从申请费任务或费用界面生成 APPLY_FEE 草单，检查系统按 FIXED + BY_CLAIMS 生成 FeeItem；必要时调整服务费折扣。 | 生成 1 张 APPLY_FEE 草单；至少 1 条 FeeItem；官费项目按费减计算，超项费按超出 10 项部分计算；服务费可按折扣计算；TotalGov/TotalService/TotalAmt 正确。 | 服务层/DB 自动化优先。 |
| TC-A-016 | P1 | Unhappy/Boundary | A4 草单/明细非法数据 | FR-FE-02<br>FR-FE-03<br>V-FD-01<br>V-FD-02<br>V-FI-01<br>V-FI-02<br>V-FI-03 | 存在一张 OPEN 草单。 | 删除全部明细后保存；清空币种保存；创建一条 FeeCode/FeeName 同时为空的明细；录入负数 Quantity/Amount；设置与 FeeRate 不一致的 FeeType。 | 系统逐项阻止保存并提示错误；Amount=0 的异常行得到提醒；币种变更时要求重算 LocalAmount。 | 服务层自动化为主。 |
| TC-A-017 | P0 | Happy | A5 官费清单与缴费 | FR-FE-04<br>V-PL-01<br>V-PL-02<br>V-PL-03<br>V-GP-01<br>V-GP-02 | 存在 APPLY_FEE 草单，含 GOV 项；Finance 用户登录。 | 从草单生成 PayList(Type=APPLY)，设置 PlannedPayDate；导出清单；登记 GovPayment 的 PaidAmt/PaidDate/InvoiceNo，更新 PayList 为 PAID。 | PayList 和 GovPayment 创建成功；Status 从 DRAFT/EXPORTED 变为 PAID；PaidAmt 缺省取 PlannedAmt；PaidDate 与 ActualPayDate 合理一致；已缴记录可用于费用查询。 | API+UI+DB。 |
| TC-A-018 | P1 | Unhappy | A5 官费清单校验 | FR-FE-04<br>V-PL-01<br>V-PL-02<br>V-PL-03<br>V-GP-03 | 存在未支付 PayList。 | 将 PlannedPayDate 设为明显异常旧日期；在 Status≠PAID 时填写 ActualPayDate/InvoiceNo；在已存在 PaidAmt/PaidDate 的 GovPayment 上尝试用普通财务账号直接修改。 | 异常计划日期触发警告；Status≠PAID 不允许填写实际缴费字段；已缴记录的修改需高权限并记录日志。 | UI+权限自动化。 |
| TC-A-019 | P0 | Happy | A6 申请费账单生成 | FR-BL-01<br>FR-BL-02<br>V-BL-01<br>V-BL-02<br>V-BL-03<br>V-BL-04 | 存在同一客户下 1~2 张 APPLY_FEE 草单；Finance 登录。 | 选择草单生成 AR 账单，设置 BillDate、DueDate、Currency、DiscountRate，保存后查看 Bill 和 BillItem。 | 生成 1 张 AR 账单；BillItem 与 FeeDraft/FeeItem 绑定；TotalGov/TotalService/TotalMisc/Amount/Balance 正确；Status=UNSETTLED。 | API+DB+UI。 |
| TC-A-020 | P1 | Unhappy | A6 账单生成非法组合 | FR-BL-02<br>FR-BL-03<br>V-BL-01<br>V-BL-02<br>V-BL-03<br>V-BL-04 | 准备不同 ClientID 的草单、不同币种草单和空草单。 | 尝试生成单一账单覆盖不同客户草单；尝试对混合币种草单不提供汇率直接生成；尝试生成无明细账单；尝试创建负数 AR 账单。 | 系统拒绝跨客户单账单；缺汇率时拒绝生成；无明细被拒；负数 AR 提示应改用调整账单。 | 服务层自动化。 |
| TC-A-021 | P0 | Happy | A7 客户付款与冲销 | FR-BL-05<br>FR-FE-07<br>V-PM-01<br>V-PM-02<br>V-PM-03<br>V-OF-01<br>V-OF-02<br>V-CR-01<br>V-CR-03 | 存在未结申请费账单；Finance 登录。 | 登记 Payment 和默认 PaymentLine；在收款与冲销界面将付款全额或部分分配到该账单；保存后查看 Bill、PaymentLine、Offset、CaseReceipt。 | Payment/PaymentLine/Offset 创建成功；账单 Balance 正确减少，状态变为 PARTIALLY_SETTLED 或 SETTLED；CaseReceipt 记录 ReceivableAmt/ReceivedAmt/IsArrears；相关查询可见。 | API+DB+UI。 |
| TC-A-022 | P1 | Unhappy/Boundary | A7 收款和冲销校验 | FR-BL-05<br>V-PM-01<br>V-PM-02<br>V-PM-03<br>V-OF-01<br>V-OF-02<br>V-CR-02 | 存在未结账单；同一客户已有 PayNo=PAY-${RUN_ID}-001。 | 分别测试：Amount<0；PayDate 明显晚于当前日期；同一 Client+PayNo 重复；单笔 OffsetAmt 超过 PaymentLine.BalanceAmt；对同一 Bill 的分配总额超过 Bill.Balance；ReceivedAmt>ReceivableAmt。 | 非法金额、日期、重复 PayNo 被拒；超额冲销被拒；ReceivedAmt>ReceivableAmt 被识别为预收并提示确认。 | 服务层自动化建议。 |
| TC-A-023 | P0 | Happy | A8 提成生成与可结算入口 | FR-COM-01<br>FR-COM-02<br>FR-COM-03<br>FR-COM-04 | 申请费账单已生成且含 SERVICE 项；存在 NORMAL 规则和主/协办代理。 | 在账单生成或收款后触发提成逻辑，检查 T_Commission 是否按规则创建或更新，并按 70/30 分摊给主协办代理。 | 为每位代理生成/更新 Commission；BaseFee 来源于服务费；S1/S2 金额按规则和分摊比例计算；WaitPay/ForceSettle 初值正确。 | 服务层+DB。 |
| TC-A-024 | P1 | Boundary | A8 WaitPay 阈值 | FR-COM-04<br>FR-COM-05 | 存在 WaitPay=true 的提成规则；同一案已产生部分收款。 | 将已收比例分别控制在 0%、50%、90%、100%，检查 S1/S2 可结算性；再将 ForceSettle=true 重试。 | 未达阈值前提成不可结算；达到阈值后进入可结算列表；ForceSettle 可绕过收款比例限制。 | 服务层自动化。 |

### B OA/补正

E2E 场景 B：OA 来文 → 答复时限 → OA 回复 → 账单/收款 → 提成

| TC ID | P级 | 类别 | 阶段/主题 | 覆盖 | 前置与数据 | 操作摘要 | 预期结果 | 自动化建议 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TC-B-001 | P0 | Happy | B1 OA来文登记 | FR-WD-01<br>FR-WD-02<br>FR-WD-03<br>FR-WD-04 | 现有一件 Status=SUB_EXAM 的案件 CASE-B-${RUN_ID}-001；配置 OA_NOTICE 模板。 | 在中间文件向导 Step1 选案并选择 OFFICIAL_IN + OA_NOTICE；Step2 填写 DocName、DispatchDate、ReceiveDate、IncomingRegNo、Summary、NeedReply=true 并保存到草稿。 | 文档草稿创建成功；默认带出 DocName/NotifyAgent/NeedReply；StatusEffect 准备将案卷置为 OA1；必要字段可编辑。 | UI 自动化。 |
| TC-B-002 | P1 | Happy/Boundary | B1 官方绝限覆盖 | FR-WD-04<br>FR-DL-02 | CASE-B-${RUN_ID}-001；OA_NOTICE 模板配置 DeadlineTemplateCode=OA_REPLY_LIMIT；ExtraData 包含 OfficialDueDate。 | 录入 OA 来文时填写 OfficialDueDate；进入 Step3 查看任务计算结果。 | 若官方绝限存在，任务 Deadline 以 OfficialDueDate 为准；BaseDate 仍保留 DispatchDate 供内部限和提醒计算；InnerDeadline/Remind* 正确。 | 服务层+UI。 |
| TC-B-003 | P0 | Unhappy | B1 文档行校验 | FR-WD-02<br>V-DOC-01<br>V-DOC-02<br>V-DOC-03<br>V-DOC-04<br>V-DOC-05 | CASE-B-${RUN_ID}-001；OA_NOTICE 模板存在。 | 分别测试：DocName 为空；DispatchDate 缺失或明显异常；NeedReply=true 且 Deadline 无法自动算出但为空；挂号号超长；必填 InputField 缺失。 | 系统逐项阻止继续完成向导，并提示具体字段错误。 | 服务层校验自动化。 |
| TC-B-004 | P0 | Happy | B2 OA答复任务生成 | FR-DL-02<br>FR-DL-03<br>FR-DL-10 | 完成 TC-B-001；存在 OA_REPLY_LIMIT 模板。 | 完成向导 Step3 并提交；查看 T_Task、TaskLog、我的任务/监督任务视图。 | 系统为该 OA 来文创建 OA_REPLY_LIMIT 任务；WorkerID 和 SupervisorID 按规则带出；TaskLog 记录 CREATE。 | API+DB+UI。 |
| TC-B-005 | P2 | Happy | B3 内部准备任务 | FR-CS-02<br>FR-DL-06 | CASE-B-${RUN_ID}-001；Agent/Formalities 可手工建任务。 | 在案卷或时限模块手工增加“内部答复准备”任务，设 BaseDate/Deadline/Worker/Supervisor；保存后修改备注和责任人。 | 内部任务保存成功；责任人变更写 CHANGE_WORKER/CHANGE_SUPERVISOR 日志；不影响官方答复任务本身。 | API+UI。 |
| TC-B-006 | P0 | Happy | B4 OA答复去文 | FR-WD-02<br>FR-WD-03<br>FR-WD-06 | 已有未完成 OA_NOTICE 文档和 OA_REPLY_LIMIT 任务；OA_REPLY 模板已配置 StatusRestore=SUB_EXAM。 | 通过向导或主界面录入 OFFICIAL_OUT + OA_REPLY，填写 ReplyToID 指向对应 OA_NOTICE，上传答复附件或模板生成 docx。 | 答复文档保存成功；ReplyToID 关联正确；附件被存档；如模板配置，案件状态准备恢复到 SUB_EXAM。 | UI+附件存储断言。 |
| TC-B-007 | P0 | Unhappy | B4 ReplyTo 约束 | FR-WD-03<br>FR-WD-04 | 存在本案 OA_NOTICE、他案 OA_NOTICE 和非可回复文档。 | 录入 OA_REPLY 时分别将 ReplyToID 指向他案文档、非 OA_NOTICE 文档或已完成无须回复文档。 | 系统应只允许选择同案且符合 ReplyToTemplateCode 的文档；非法 ReplyToID 被过滤或阻断。 | 服务层自动化。 |
| TC-B-008 | P0 | Happy | B5 自动核销任务与状态恢复 | FR-DL-04<br>FR-DL-10<br>FR-CM-04 | TC-B-006 成功；对应 OA_REPLY_LIMIT 任务仍为 OPEN。 | 提交 OA_REPLY 后检查任务、TaskLog 和案卷状态。 | 系统根据 ReplyToID 找到 OA_REPLY_LIMIT 任务并标记 DONE，DoneDate=ReplyDate；写入 MARK_DONE 日志；Case.Status 从 OA1/OA2 恢复为 SUB_EXAM。 | API+DB+UI。 |
| TC-B-009 | P1 | Happy | B6 OA费用草单 | FR-WD-05<br>FR-FE-02<br>FR-FE-03 | OA_REPLY 模板配置 FeeDraftType=OA_FEE，存在 OA 服务费和可选官方费费率。 | 完成向导 Step4 或从费用界面生成 OA_FEE 草单，检查 FeeItem。 | 生成 OA_FEE 草单；SERVICE 项来自 OA 服务费；如配置 GOV 项也同步生成；Total* 汇总正确。 | API+DB。 |
| TC-B-010 | P2 | Happy | B7 OA官方费清单 | FR-FE-04 | 存在 OA_FEE 草单且含 GOV 项。 | 生成 PayList(Type=INTERMEDIATE/OA) 并登记 GovPayment。 | 仅 GOV 项进入官费清单；PaidDate/PaidAmt 可查询；不影响 SERVICE 项账单逻辑。 | API+UI。 |
| TC-B-011 | P0 | Happy | B8 OA账单与收款 | FR-BL-02<br>FR-BL-05<br>FR-FE-07 | 存在 OA_FEE 草单；Finance 登录。 | 从草单生成 OA 应收账单；登记客户付款并冲销；检查 CaseReceipt。 | 账单生成成功；付款后 Balance 正确减少；CaseReceipt 记录本次 OA 服务费/官费收款；费用情况查询能看到。 | API+UI+DB。 |
| TC-B-012 | P1 | Happy | B9 OA服务费计入提成 | FR-COM-02<br>FR-COM-03<br>FR-COM-04 | 同案已经存在 A 场景申请费提成；本次 OA 账单含 SERVICE 项。 | 触发提成计算，查看 Commission 是累加 BaseFee 还是新增阶段记录（按规则实现）。 | OA 服务费进入 Commission 管道；BaseFee/S1/S2 被新增或累加且可追溯阶段来源 Remark=OA 阶段；多代理人分摊正确。 | 服务层+DB。 |
| TC-B-013 | P1 | Happy/Unhappy | 主界面修改 NeedReply/Deadline | FR-WD-04<br>FR-DL-06 | 已存在一条 NeedReply=true 且已有 T_Task 的 OA 来文。 | 在文档主界面将 NeedReply 改为 false 或修改 Deadline；保存时选择“更新任务”或“取消任务”（如实现该交互）。 | 若改为 false，系统同步取消或关闭对应任务并记录日志；若只修改 Deadline，任务日期同步更新且保留审计痕迹。 | UI+服务层自动化。 |

### C PCT→国家阶段

E2E 场景 C：PCT 国际 → 国家阶段计划 → 子案建立 → 接主流水线

| TC ID | P级 | 类别 | 阶段/主题 | 覆盖 | 前置与数据 | 操作摘要 | 预期结果 | 自动化建议 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TC-C-001 | P0 | Happy | C0 PCT国际案立案 | FR-CM-01<br>FR-CM-05<br>V-PCT-01 | DS-U-FM-01；客户 DS-CL-003；申请人 DS-AP-003；案号 CASE-C-${RUN_ID}-INTL。 | 创建 CaseType=PCT_INTL 案，填写 IntlAppNo、IntlAppDate、RO、ISA、IntlPubNo/Date、IntlPubLang、NeedIPER 等。 | 案卷保存成功；PCT 国际字段持久化；状态为 PCT_INTL_EXAM 或配置默认状态；后续可登记国际阶段来文。 | UI+DB。 |
| TC-C-002 | P0 | Unhappy | C0 PCT国际必填缺失 | FR-CM-05<br>V-PCT-01 | DS-U-FM-01；PCT_INTL 新案。 | 不填写 IntlAppNo 或 IntlAppDate 直接保存。 | 保存被拒并提示缺少国际申请号/日。 | 服务层自动化。 |
| TC-C-003 | P1 | Happy/Boundary | C1 NeedIPER 提醒 | FR-CM-05<br>V-PCT-03<br>FR-DL-02 | 已有 PCT_INTL 案，NeedIPER=true。 | 保存时暂不填 IPERDate；触发相关提醒/查询逻辑；之后补录 IPERDate。 | 系统允许保存或强提示，但会在时限/提醒中标识需补录 IPERDate；补录后提醒消失，UpdatedAt 更新。 | 人工+服务层校验。 |
| TC-C-004 | P1 | Happy | C1 国际阶段来文登记 | FR-WD-01<br>FR-WD-02<br>FR-WD-06 | 已有 PCT_INTL 案；配置受理通知/检索报告/书面意见/IPER 模板。 | 分别录入 OFFICIAL_IN 文档：RO 受理通知、国际检索报告、书面意见、IPER；上传附件。 | 每类来文均能登记并归档；必要字段进入 ExtraData；附件可预览下载。 | UI+附件存储。 |
| TC-C-005 | P0 | Happy | C2 国家阶段计划初始化 | FR-DL-02<br>FR-CM-05 | 已有 PCT_INTL 案；目标国家=CN/US/JP。 | 执行国家阶段计划初始化，生成每国一条计划数据和进入期限基础信息。 | 系统生成 3 条国家阶段计划记录，状态为 PLANNED/OPEN（按实现）；每条记录含国家、预计进入期限、是否已建子案标记。 | API+DB。 |
| TC-C-006 | P0 | Happy | C3 进入时限任务生成 | FR-DL-02<br>FR-DL-03 | 已有国家阶段计划；配置 PCT_NATIONAL_ENTRY_LIMIT。 | 生成各国进入时限任务并检查 Worker/Supervisor/提醒日。 | 每个目标国家生成 1 条进入任务；任务与计划和母案正确关联；我的任务/监督任务可见。 | 服务层+DB。 |
| TC-C-007 | P0 | Happy | C4 客户 ENTER/ABANDON 指示 | FR-CM-05<br>FR-DL-07 | 存在 CN/US/JP 进入计划。 | 在国家阶段计划中将 CN、US 标记为 ENTER，JP 标记为 ABANDON；保存并查看计划状态。 | 计划状态正确变更；ABANDON 国家不再要求创建国家案；ENTER 国家保留待建子案动作。 | UI+DB。 |
| TC-C-008 | P0 | Happy | C5 创建国家阶段案卷 | FR-CM-01<br>FR-CM-05 | CN 计划状态=ENTER；母案含申请人/发明人/优先权/PCT 信息。 | 基于 ENTER 计划创建 CaseType=PCT_NATIONAL 子案。 | 系统为 CN 创建新案卷；复制申请人、发明人、优先权、PCT 信息；Status=NOT_FILED；国家计划状态变为 CASE_CREATED 且记录 NationalCaseID。 | API+DB+UI。 |
| TC-C-009 | P0 | Unhappy | C5 国家阶段必填缺失 | FR-CM-05<br>V-PCT-02 | 创建或编辑 PCT_NATIONAL 子案。 | 不填写 PCT_NationalEntryDate 保存。 | 保存被拒并提示国家阶段进入日必填。 | 服务层自动化。 |
| TC-C-010 | P1 | Unhappy | C5 重复创建国家案 | FR-CM-05 | 同一母案、同一国家计划已创建 NationalCaseID。 | 再次对同一国家执行“创建国家案”。 | 系统阻止重复创建，或提示已有 NationalCaseID 并跳转现有子案。 | API+UI。 |
| TC-C-011 | P1 | Happy | C5 进入任务核销 | FR-DL-04<br>FR-DL-10 | CN 国家子案已创建；对应进入任务仍 OPEN。 | 完成进入操作后核销 PCT_NATIONAL_ENTRY_LIMIT 任务。 | 任务状态变为 DONE，DoneDate 记录；TaskLog 写 MARK_DONE；计划状态保持 CASE_CREATED/ENTERED。 | UI+DB。 |
| TC-C-012 | P2 | Happy | C6 国家案对接主流水线 | FR-CM-07<br>FR-WD-04<br>FR-FE-04<br>FR-BL-05<br>FR-COM-02 | 已有 PCT_NATIONAL 子案。 | 对该子案执行递交、申请费、OA、授权或年费等任一后续流程 smoke。 | 国家阶段子案完全复用 A/B/G0/D/E/F/G/H 流水线；下游模块不依赖母案特殊分支。 | 建议接口级烟测。 |

### G0 授权阶段

授权节点：GRANT_NOTICE → 授权费时限/草单/账单 → 年费初始化 → 提成

| TC ID | P级 | 类别 | 阶段/主题 | 覆盖 | 前置与数据 | 操作摘要 | 预期结果 | 自动化建议 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TC-G0-001 | P0 | Happy | L5 授权通知录入 | FR-WD-03<br>FR-CM-04<br>V-D-01 | 一件 NORMAL/PCT_NATIONAL 案状态在 SUB_EXAM 或 OA2；配置 GRANT_NOTICE 模板。 | 录入 OFFICIAL_IN + GRANT_NOTICE，填写 IssueDate、GrantDate、GrantNo、FirstAnnuityYear、ValidUntil、Summary。 | 文档保存成功；T_Case.Status 更新为 GRANTED；Grant 相关字段回写；文档可在中间文件列表中查询。 | UI+DB。 |
| TC-G0-002 | P0 | Unhappy | GRANT_NOTICE 必填字段缺失 | FR-WD-03<br>V-D-01<br>V-DOC-05 | 存在待授权案件。 | 录入 GRANT_NOTICE 时缺少 GrantDate、GrantNo、FirstAnnuityYear 或 ValidUntil 任一字段保存。 | 系统阻止保存并指出缺失字段；案卷状态不应进入 GRANTED。 | 服务层自动化。 |
| TC-G0-003 | P0 | Happy | 授权费时限任务生成 | FR-DL-02<br>FR-DL-03 | TC-G0-001 成功；存在 GRANT_CERT_FEE_LIMIT 模板。 | 录入授权通知后检查是否生成授权费时限任务。 | 系统创建 GRANT_CERT_FEE_LIMIT 任务，含 Deadline/InnerDeadline/Remind*、WorkerID、SupervisorID；任务在首页/我的任务出现。 | API+DB+UI。 |
| TC-G0-004 | P1 | Happy | GrantFeeTask 提取 | FR-FE-05 | 已授权案件，存在 T_GrantFeeTask 机制。 | 打开授权费管理列表，按授权日期/客户过滤，查看 GovFeeAmt、ServiceFeeAmt、ClientInstruction、NotifyCount。 | 新授权案件出现在授权费列表；字段完整；默认 ClientInstruction=NONE、DraftGenerated=false、NoticeSent=false。 | UI+DB。 |
| TC-G0-005 | P1 | Happy | 授权费通知函 | FR-FE-05<br>FR-WD-06 | GrantFeeTask.ClientInstruction=NONE。 | 执行“生成授权费通知函”。 | 生成 T_Document(TemplateCode=GRANT_FEE_NOTICE) 和附件；GrantFeeTask.NoticeSent=true，NotifyCount+1。 | UI+DB+附件。 |
| TC-G0-006 | P0 | Happy | 授权费草单生成 | FR-FE-02<br>FR-FE-05<br>V-GF-02 | GrantFeeTask.ClientInstruction=PAY；费率已配置登记费/证书费/印花税。 | 执行“生成授权费草单”。 | 生成 T_FeeDraft(Type=GRANT_FEE) 和多条 FeeItem；DraftGenerated=true；TotalGov/TotalService/TotalAmt 正确。 | API+DB。 |
| TC-G0-007 | P0 | Unhappy | 授权费费率缺失/重复 | FR-FE-05<br>V-GF-01<br>V-GF-02 | GrantFeeTask.ClientInstruction=PAY；去掉一项 GRANT 费率或预先造一张 GRANT_FEE 草单。 | 尝试生成授权费草单。 | 缺关键费率时系统阻断；同案同类型草单已存在时系统提示避免重复或阻断。 | 服务层自动化。 |
| TC-G0-008 | P0 | Happy | 授权费清单/账单/收款闭环 | FR-FE-04<br>FR-BL-02<br>FR-BL-05<br>FR-FE-07 | 存在 GRANT_FEE 草单。 | 将 GOV 项生成 PayList(Type=GRANT) 并登记缴费；从草单生成账单；客户付款并冲销。 | 授权费官费清单、账单、收款和 CaseReceipt 全链路成功；费用查询能看见官方缴费与客户收款两部分。 | API+DB+UI。 |
| TC-G0-009 | P1 | Happy | 年费初始化触发 | FR-FE-06 | TC-G0-001 成功；IsFeeMonitor=true。 | 授权完成后检查是否创建 AnnuityTask 初始记录。 | 按 FirstAnnuityYear 和 ValidUntil 生成年费任务或具备后续滚动生成条件；未监视案件不应初始化年费任务。 | API+DB。 |
| TC-G0-010 | P1 | Happy | 授权服务费提成 | FR-COM-02<br>FR-COM-04<br>FR-COM-06 | 授权费账单含 SERVICE 项；存在授权阶段提成规则。 | 触发提成计算并查看是否进入 S2 可结算判断。 | 授权阶段服务费进入 Commission；可作为 S2 结算关键节点；满足状态+回款阈值后进入可结算列表。 | 服务层+DB。 |

### D 年费周期

E2E 场景 D：多年度滚动年费通知/草单/清单/账单/收款

| TC ID | P级 | 类别 | 阶段/主题 | 覆盖 | 前置与数据 | 操作摘要 | 预期结果 | 自动化建议 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TC-D-001 | P0 | Happy | D0/D1 年费任务初始化 | FR-FE-06 | 已授权案件，IsFeeMonitor=true，FirstAnnuityYear=1，ValidUntil=2046-04-05。 | 执行授权后的年费初始化或定时任务。 | 系统生成 T_AnnuityTask 多年度记录或首批滚动记录；YearNo、DueDate、Currency、ClientInstruction、DraftGenerated、NoticeSent、IsOverdue 初始化正确。 | API+DB。 |
| TC-D-002 | P1 | Happy/Unhappy | D1 滚动生成去重 | FR-FE-06 | 已有部分年份 AnnuityTask。 | 再次执行滚动生成作业。 | 仅创建缺失年度；已有年度不重复创建。 | 批任务自动化。 |
| TC-D-003 | P0 | Happy | D2 即将到期检索 | FR-FE-06<br>FR-DL-07 | 存在多个国家、多个客户的年费任务。 | 按未来 3 个月/6 个月/1 年、Country、Client、Instruction、NoticeSent 等筛选。 | 列表返回正确任务集合，排序合理，可导出。 | UI+查询自动化。 |
| TC-D-004 | P0 | Happy | D3 年费通知函 | FR-FE-06<br>FR-WD-06 | ClientInstruction=NONE 的年费任务。 | 执行“生成年费通知函”。 | 生成 T_Document(ANNUITY_NOTICE) 和附件；NoticeSent=true；NotifyCount+1。 | UI+DB。 |
| TC-D-005 | P0 | Happy | D4 PAY 生成年费草单 | FR-FE-02<br>FR-FE-03<br>FR-FE-06<br>V-FI-04 | 年费任务 YearNo=1，ClientInstruction=PAY。 | 执行“生成年费草单”。 | 生成 T_FeeDraft(Type=ANNUITY_FEE) 和 YearNo=1 的 FeeItem；YearNo 不小于 FirstAnnuityYear；DraftGenerated=true。 | API+DB。 |
| TC-D-006 | P1 | Happy/Boundary | D4 同时缴下一年度 | FR-FE-06 | YearNo=N 的年费任务，勾选 PayNextYear。 | 执行草单生成。 | 同一草单可同时包含 YearNo=N 和 N+1 两个年度明细；金额分别正确。 | 服务层自动化。 |
| TC-D-007 | P1 | Happy/Unhappy | D3/D4 ABANDON 处理 | FR-FE-06<br>FR-CM-04 | 年费任务 ClientInstruction 可设为 ABANDON。 | 将当前年度设为 ABANDON，并检查是否批量影响后续年度；再尝试为 ABANDON 年度生成草单。 | ABANDON 年度不应生成草单；按策略可联动未来年度也置为 ABANDON；专利后续可能终止或停止监视。 | UI+DB。 |
| TC-D-008 | P0 | Unhappy | D4 年度边界非法 | FR-FE-03<br>V-FI-04 | 存在 FirstAnnuityYear=3 的案件。 | 尝试为 YearNo=2 创建 ANNUITY_FEE 明细或手工改 YearNo<FirstAnnuityYear。 | 系统阻止保存并提示年度非法。 | 服务层自动化。 |
| TC-D-009 | P0 | Happy | D5 年费官费清单与缴费 | FR-FE-04<br>FR-FE-06 | 存在含 GOV 项的 ANNUITY_FEE 草单。 | 生成 PayList(Type=ANNUITY)，登记 GovPayment 实缴信息。 | 年费官费清单生成成功；PaidDate/PaidAmt/InvoiceNo 可查询到；不同 YearNo 明细不混淆。 | API+DB。 |
| TC-D-010 | P0 | Happy | D6 年费账单与收款 | FR-BL-02<br>FR-BL-05<br>FR-FE-07 | 存在 ANNUITY_FEE 草单。 | 生成账单、登记客户付款、冲销到账单并查看 CaseReceipt。 | 账单、收款、CaseReceipt 成功闭环；YearNo 在 BillItem/CaseReceipt 中可追踪。 | API+DB+UI。 |
| TC-D-011 | P1 | Happy/Unhappy | D7 逾期/终止/恢复 | FR-FE-06<br>FR-CM-04 | 存在逾期未缴的年费任务。 | 触发逾期识别；标记专利终止或停止监视；后续补缴/恢复时重新启用相关任务或状态。 | IsOverdue 正确置位；终止后不再继续常规通知；恢复后可重新纳入后续年份管理（如业务允许）。 | 需要人工验证业务策略。 |
| TC-D-012 | P2 | Happy | D8 年费服务费提成 | FR-COM-02<br>FR-COM-04 | 年费草单/账单包含 SERVICE 项，且规则允许计入提成。 | 触发提成计算。 | 年费服务费按规则进入 BaseFee；如系统配置不计入，则明确不生成提成。 | 服务层自动化。 |
| TC-D-013 | P1 | Boundary | IsFeeMonitor=false | FR-CM-02<br>V-E-03<br>FR-FE-06 | 已授权案件但 IsFeeMonitor=false。 | 执行年费初始化与定期提取。 | 默认不生成或不展示该案年费任务；除非后续手工启用监视。 | API+UI。 |

### E 无效/诉讼

E2E 场景 E：立案 → 请求/受理/答辩/裁决 → 费用 → 提成

| TC ID | P级 | 类别 | 阶段/主题 | 覆盖 | 前置与数据 | 操作摘要 | 预期结果 | 自动化建议 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TC-E-001 | P0 | Happy | E1 无效案立案 | FR-CM-01<br>FR-CM-05<br>V-INV-01<br>V-INV-02<br>V-INV-03 | DS-U-FM-01；原案 CASE-E-${RUN_ID}-ORIG 已授权。 | 创建 CaseType=INVALIDATION 案卷，填写 OriginalCaseID、InvalidClientID、InvalidRole、InvalidPatentee、InvalidRequester。 | 无效案保存成功；Status=INVALID_INIT；OriginalCaseID 指向原案；报表可识别我方角色。 | UI+DB。 |
| TC-E-002 | P0 | Unhappy | E1 无效案必填缺失 | FR-CM-05<br>V-INV-01<br>V-INV-02 | 准备新建 INVALIDATION 案卷。 | 缺少 InvalidClientID、InvalidRole 或 Patentee/Requester 之一保存。 | 系统阻止保存并给出缺失项提示。 | 服务层自动化。 |
| TC-E-003 | P1 | Happy | E1 诉讼案立案 | FR-CM-01 | DS-U-FM-01；原案或争议对象存在。 | 创建 CaseType=LITIGATION 案卷，填写 LitigationType、CourtName、Plaintiff、Defendant、LitigationRole。 | 诉讼案保存成功；Status=LIT_INIT 或配置默认状态；后续可登记立案/开庭/判决文书。 | UI+DB。 |
| TC-E-004 | P0 | Happy | E2 请求书/起诉状 + 初始草单 | FR-WD-02<br>FR-WD-05<br>FR-CM-04 | INVALIDATION/LITIGATION 案已创建；配置 INVALID_REQUEST 或 LITIGATION_COMPLAINT 模板和费用类型。 | 录入 OFFICIAL_OUT 请求书/起诉状，必要时在 Step4 生成 INVALID_FEE/LITIGATION_FEE 草单。 | 文档保存成功；案件状态变为 INVALID_FILED 或 LIT_FILED；初始费用草单按模板生成。 | UI+DB。 |
| TC-E-005 | P0 | Happy | E3 受理/答辩/开庭通知 → 任务 | FR-WD-04<br>FR-DL-02 | 已 filed 的无效/诉讼案件。 | 录入 OFFICIAL_IN 受理通知、答辩通知、举证通知或开庭通知。 | 相应 T_Document 创建成功；NeedReply=true 的文档生成答辩/举证/开庭准备任务；案件状态更新为 INVALID_ACCEPTED/INVALID_IN_HEARING 或 LIT_ACCEPTED/LIT_HEARING。 | UI+DB。 |
| TC-E-006 | P0 | Happy | E4 答辩/证据/意见去文 → 核销 | FR-WD-04<br>FR-DL-04<br>FR-DL-10 | 存在 OPEN 的 INVALID_DEFENSE_LIMIT 或相关诉讼任务。 | 录入 OFFICIAL_OUT 答辩状、证据提交、书面意见文书，ReplyToID 指向对应通知。 | 去文保存成功；对应任务被 DONE；TaskLog 写 MARK_DONE；必要时补充 INVALID_FEE/LITIGATION_FEE 草单。 | API+DB+UI。 |
| TC-E-007 | P0 | Unhappy | E4 ReplyTo 非法 | FR-WD-04 | 存在他案通知或不匹配模板。 | 将答辩文书的 ReplyToID 指向错误案件或错误模板类型。 | 系统阻断或过滤非法 ReplyToID；不应误核销他案任务。 | 服务层自动化。 |
| TC-E-008 | P0 | Happy | E5 无效决定-全部无效 | FR-CM-04<br>FR-WD-03 | 无效案已进入审理中；原案为 GRANTED。 | 录入 INVALID_DECISION，DecisionResult=全部无效，且根据我方角色设置结果。 | 无效案状态更新为 INVALID_WON/INVALID_LOST（依角色）；原案状态更新为 INVALIDATED 或 TERMINATED（按规则）；DecisionResult 等保存在 ExtraData。 | API+DB。 |
| TC-E-009 | P1 | Happy | E5 无效决定-部分无效 | FR-CM-04 | 无效案已审理中；原案为 GRANTED。 | 录入 INVALID_DECISION，DecisionResult=部分无效，填写 AffectedClaims。 | 无效案状态为 INVALID_PARTIAL；原案状态为 INVALIDATED_PARTIAL；受影响权利要求可追踪。 | API+DB。 |
| TC-E-010 | P1 | Happy | E5 诉讼判决 | FR-CM-04 | 诉讼案已开庭。 | 录入 LITIGATION_JUDGMENT，分别测试胜诉/败诉/和解。 | 诉讼案状态更新为 LIT_WON/LIT_LOST/LIT_SETTLED；如判决不影响原专利状态，则原案保持不变。 | API+DB。 |
| TC-E-011 | P0 | Happy | E6 费用闭环 | FR-FE-02<br>FR-FE-04<br>FR-BL-02<br>FR-BL-05<br>FR-FE-07 | 存在 INVALID_FEE/LITIGATION_FEE 草单，含 GOV/SERVICE/MISC 项。 | 从草单生成官费清单（如有 GOV）、账单、收款和冲销。 | 无效/诉讼费用全链路闭环；BillItem、GovPayment、CaseReceipt 都能按 CaseID/阶段追踪。 | API+DB+UI。 |
| TC-E-012 | P1 | Happy | E7 提成 | FR-COM-01<br>FR-COM-02<br>FR-COM-04<br>FR-COM-06 | 无效/诉讼账单含 SERVICE 项且规则已配置。 | 触发提成计算并查看是否进入结算候选。 | BaseFee 来源于无效/诉讼服务费；阶段说明写入 Remark；满足 WaitPay/状态条件时进入可结算列表。 | 服务层+DB。 |
| TC-E-013 | P1 | Unhappy | 原案引用异常 | FR-CM-05 | 尝试创建无效案时 OriginalCaseID 不存在或原案并非适格状态。 | 保存无效/诉讼案。 | 系统阻断或给出强警告；避免对不存在或不适格原案建立派生案。 | 服务层自动化。 |
| TC-E-014 | P2 | Happy | 多阶段费用与提成累积 | FR-COM-02<br>FR-COM-03 | 同一无效/诉讼案已存在初始服务费提成记录。 | 再次录入答辩/开庭/上诉阶段文书并生成追加服务费账单。 | Commission 可按累加或多记录模式继续增加 BaseFee；各阶段可追溯，不与前阶段记录混淆。 | 服务层+DB。 |

### F 预收款

E2E 场景 F：预收款池 → 后续冲销 → CaseReceipt → 提成影响

| TC ID | P级 | 类别 | 阶段/主题 | 覆盖 | 前置与数据 | 操作摘要 | 预期结果 | 自动化建议 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TC-F-001 | P0 | Happy | F1 录入通用预收款 | FR-BL-09<br>V-PM-01<br>V-PM-02<br>V-PM-03 | Finance 登录；客户 DS-CL-001。 | 登记 Payment，Remark=预收款，创建默认 PaymentLine(CaseID=NULL)。 | Payment 保存成功；PaymentLine.RawAmount=Amount、AllocatedAmt=0、BalanceAmt=Amount；在预收款报表可见。 | API+DB+UI。 |
| TC-F-002 | P0 | Unhappy | F1 预收款输入非法 | FR-BL-09<br>V-PM-01<br>V-PM-02<br>V-PM-03 | 同一客户已存在 PayNo=PRE-${RUN_ID}-001。 | 分别测试 Amount<0、PayDate 明显超当前、重复 PayNo。 | 系统逐项阻止保存。 | 服务层自动化。 |
| TC-F-003 | P1 | Happy | F2 预收款池查询 | FR-BL-09 | 存在多条未分配 PaymentLine。 | 进入预收款池或报表查看客户预收余额。 | 按客户展示 PayNo/PayDate/原金额/BalanceAmt/Remark；客户总预收余额汇总正确。 | 查询自动化。 |
| TC-F-004 | P1 | Happy | F3 案卷级预挂 | FR-BL-09 | 存在未分配 PaymentLine 和目标案 CASE-A-${RUN_ID}-001。 | 将 PaymentLine 预挂到某案或创建 CaseID 已知的 PaymentLine。 | 后续冲销时默认优先显示该案相关账单；但仍可在权限允许下调整分配目标。 | UI+DB。 |
| TC-F-005 | P0 | Happy | F4 用预收抵扣后续账单-全额 | FR-BL-05<br>FR-BL-09<br>V-OF-01<br>V-OF-02 | 存在预收款 PaymentLine 和后续新案/年费/顾问账单。 | 在冲销界面使用预收款全额抵扣单张账单。 | Bill.Balance 降为 0、Status=SETTLED；PaymentLine.AllocatedAmt 增加、BalanceAmt 减少；生成 Offset。 | API+DB+UI。 |
| TC-F-006 | P0 | Happy | F6 预收跨多案多账单分摊 | FR-BL-05<br>FR-BL-09 | 单条预收款金额足以覆盖多张账单。 | 将同一 PaymentLine 分配到不同案、不同类型的多张账单。 | 系统允许多次/多目标消耗；每张账单余额正确变化；PaymentLine 剩余金额正确。 | 服务层自动化。 |
| TC-F-007 | P0 | Unhappy | F4/F6 超额分配 | FR-BL-05<br>V-OF-01<br>V-OF-02 | 存在 BalanceAmt=1000 的 PaymentLine 和 Balance=600 的账单。 | 尝试一次分配 1200 或对某账单分配 700。 | 系统分别因超过 PaymentLine.BalanceAmt 或 Bill.Balance 而拒绝。 | 服务层自动化。 |
| TC-F-008 | P1 | Happy | F5 转化为案卷实收 | FR-FE-07<br>FR-BL-09<br>V-CR-02 | 预收款已冲销到具体账单。 | 检查 T_CaseReceipt 的 ReceivableAmt/ReceivedAmt/IsPrepayment/IsArrears 变化。 | 预收在未分配前不提高 PaidRatio；一旦通过 Offset 绑定到具体案/费用项，CaseReceipt 更新为已收，并可用于提成 PaidRatio。 | API+DB。 |
| TC-F-009 | P1 | Happy/Boundary | F7 剩余预收处理 | FR-BL-09 | 客户预收余额 > 当前所有账单总额。 | 测试余额留存、退款或通过负账单/调整账单处理。 | 余额可继续留存并在预收报表中显示；退款/调整遵循系统参数策略；不会把未分配余额当作已收服务费。 | 需要人工确认财务策略。 |
| TC-F-010 | P1 | Happy | F8 与提成关系 | FR-COM-04<br>FR-COM-05 | 存在 WaitPay=true 的提成记录，客户有大额未分配预收。 | 先仅录入预收不分配；再将其分配到服务费账单。 | 未分配预收不改变 Commission 可结算性；完成 Offset 且 CaseReceipt 更新后，PaidRatio 提升，可结算性随之变化。 | 服务层自动化。 |

### G 催款与坏账

E2E 场景 G：逾期 → 催款单/函 → 回款 → 坏账/回收

| TC ID | P级 | 类别 | 阶段/主题 | 覆盖 | 前置与数据 | 操作摘要 | 预期结果 | 自动化建议 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TC-G-001 | P0 | Happy | G1 逾期识别 | FR-BL-07<br>FR-BL-08 | 存在多张 AR 账单，其中包括未到期、已结清、坏账和逾期未结账单。 | 按 ToDate 执行逾期识别或打开逾期报表。 | 仅 Direction=AR、Status=UNSETTLED/PARTIALLY_SETTLED、IsBadDebt=false、DueDate<=ToDate、Balance>0 的账单被识别为逾期。 | 查询/服务层自动化。 |
| TC-G-002 | P0 | Happy | G2 生成催款单快照 | FR-BL-08 | 客户存在多张逾期账单。 | 以客户+截止日生成 T_Dunning/T_DunningLine。 | 催款单头和明细创建成功；OutstandingAmt 记录生成时快照，不受后续收款回写影响；TotalAmt 为各行合计。 | API+DB+UI。 |
| TC-G-003 | P0 | Unhappy | G2 催款范围过滤 | FR-BL-08 | 客户同时存在已结清、未到期、坏账和 AP 账单。 | 生成催款单。 | 已结清、未到期、坏账、AP 账单不应进入催款明细。 | 查询自动化。 |
| TC-G-004 | P1 | Happy | G3 生成催款函 | FR-BL-08<br>FR-WD-06 | 催款单已创建；存在 DUNNING_LETTER 模板。 | 从催款单生成催款函 Word/PDF 或 Email 并发送。 | 催款函生成成功；可作为 T_Document 存档；T_Dunning.Status/SentDate 更新。 | UI+文件输出。 |
| TC-G-005 | P0 | Happy | G4 催款后部分付款 | FR-BL-05<br>FR-BL-08<br>FR-FE-07 | 逾期账单已被催款。 | 登记客户部分付款并冲销到账单。 | 账单余额减少、状态更新为 PARTIALLY_SETTLED；CaseReceipt 更新已收金额；历史 DunningLine 快照不变。 | API+DB。 |
| TC-G-006 | P1 | Happy | G5 多轮催款 | FR-BL-08 | 账单仍有未结余额，已存在第一轮催款单。 | 再次生成第二轮/第三轮催款单。 | 新一轮 Dunning/DunningLine 创建成功；OutstandingAmt 反映当轮余额；旧催款数据不被覆盖。 | API+DB。 |
| TC-G-007 | P0 | Happy | G6 标记坏账 | FR-BL-07 | 存在长期逾期且无回收希望的应收账单。 | 对账单执行“标记坏账”，填写 BadDebtDate、BadDebtReason。 | Bill.IsBadDebt=true，Status=BAD_DEBT；在普通应收统计与坏账统计中区分显示。 | UI+DB。 |
| TC-G-008 | P1 | Happy | G7 坏账后收回 | FR-BL-05<br>FR-BL-07<br>FR-FE-07 | 账单已是 BAD_DEBT。 | 登记客户付款并冲销到坏账账单。 | 系统仍允许登记收款和 Offset；Bill.Balance 下降；CaseReceipt 记录坏账后回收金额；账单可按策略继续保持 BAD_DEBT 或转状态。 | API+DB。 |
| TC-G-009 | P2 | Happy/Unhappy | G7 坏账恢复策略 | FR-BL-07 | 存在 BAD_DEBT 账单。 | 执行“从坏账恢复”或在完全收回后检查系统状态。 | 如系统支持恢复，IsBadDebt 恢复为 false，状态改为 UNSETTLED/PARTIALLY_SETTLED/SETTLED；若不支持则明确只保留 BAD_DEBT 但余额更新。 | 需按实现策略人工确认。 |
| TC-G-010 | P1 | Happy | G8 对提成的间接影响 | FR-COM-04<br>FR-COM-05 | 存在 WaitPay=true 的提成记录，对应账单长期逾期后部分回收或坏账后回收。 | 观察回款前后 Commission 可结算状态。 | 只有通过 Offset/CaseReceipt 确认归属的回款才提升 PaidRatio；催款和坏账标签本身不直接改变 BaseFee，但会影响可结算性。 | 服务层自动化。 |

### H 顾问/检索

E2E 场景 H：项目立案 → 内部任务/支出 → 草单/账单/收款 → 提成

| TC ID | P级 | 类别 | 阶段/主题 | 覆盖 | 前置与数据 | 操作摘要 | 预期结果 | 自动化建议 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TC-H-001 | P0 | Happy | H1 项目立案 | FR-CS-01 | DS-U-FM-01；客户 DS-CL-001；案号 CASE-H-${RUN_ID}-001。 | 创建 CaseType=CONSULTING 或 SEARCH 案卷，填写项目范围、负责人、预计工时、状态 NOT_STARTED 或 IN_PROGRESS。 | 项目案卷保存成功；顾问专属字段持久化；可在高级案件查询中被检出。 | UI+DB。 |
| TC-H-002 | P1 | Happy | H2 内部任务 | FR-CS-02<br>FR-DL-06 | 顾问案已创建。 | 创建项目内部任务，例如 CONSULT_SCOPING、SEARCH_EXECUTION、ANALYSIS_REPORT；调整责任人并核销。 | 任务可正常创建、编辑、DONE；不依赖官方来文；日志完整。 | API+UI。 |
| TC-H-003 | P1 | Happy/Boundary | H3 项目支出 | FR-CS-03<br>FR-FE-08<br>V-EX-01<br>V-EX-02 | 顾问案已创建。 | 录入 SEARCH_DB、TRANSLATION、TRANSPORT 等支出；测试 Quantity*UnitPrice 与 Total 不一致的手工总额。 | 非负校验生效；Total 不一致时系统提示确认是否采用手工总额；支出可按案件/时间/类别查询。 | UI+DB。 |
| TC-H-004 | P0 | Happy | H4 固定报价草单 | FR-CS-04<br>FR-FE-02<br>FR-FE-03 | 顾问案配置固定报价。 | 生成 CONSULT_FEE 或 SEARCH_FEE 草单，添加固定报价服务费明细。 | 草单生成成功；TotalService 正确；TotalGov 一般为 0；状态为 OPEN。 | API+DB。 |
| TC-H-005 | P1 | Happy | H4 工时/混合报价草单 | FR-CS-04<br>FR-FE-02<br>FR-FE-03 | 顾问案配置按工时或混合模式。 | 创建多条服务费明细：高级顾问工时、检索分析人工时、可转嫁杂费。 | 数量、单价、金额和杂费汇总正确；可同时包含 SERVICE 与 MISC。 | API+DB。 |
| TC-H-006 | P0 | Happy | H5 账单/收款/CaseReceipt | FR-CS-05<br>FR-BL-02<br>FR-BL-05<br>FR-FE-07 | 存在 CONSULT_FEE/SEARCH_FEE 草单。 | 从草单生成账单；客户付款并冲销；查看 CaseReceipt。 | 项目账单和收款闭环成功；CaseReceipt 记录项目实收；费用报表可见。 | API+DB+UI。 |
| TC-H-007 | P1 | Happy | H6 顾问提成 | FR-CS-06<br>FR-COM-01<br>FR-COM-02<br>FR-COM-06 | 顾问案账单含 SERVICE 项；存在 CONSULTING/SEARCH 提成规则。 | 触发提成计算并查看结算候选。 | 根据顾问/检索规则创建 Commission；可为一次性提成或 S1/S2 两阶段；满足条件可进入结算批次。 | 服务层+DB。 |
| TC-H-008 | P1 | Happy/Unhappy | 状态关闭 | FR-CS-01<br>FR-CS-05<br>FR-CS-06 | 顾问案存在未完成任务、未结账单或未结算提成。 | 先尝试将项目状态设为 CLOSED；再在任务完成、账单结清、提成结算后重试。 | 业务未完成时不应关闭或需强警告；全部闭环后状态可变为 CLOSED。 | 人工+服务层自动化。 |

### X 查询/报表/审计

跨模块查询、报表、手工账单、日志、权限、状态机回归

| TC ID | P级 | 类别 | 阶段/主题 | 覆盖 | 前置与数据 | 操作摘要 | 预期结果 | 自动化建议 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TC-X-001 | P0 | Happy | 高级案件查询-基本维度 | FR-CM-01 | 系统中存在 NORMAL/PCT/INVALIDATION/CONSULTING 等多类案件。 | 按 CaseNo、AppNo、CaseType、PatentCategory、FlowDir、Status、RecvDate/FilingDate/GrantDate 等组合查询。 | 结果集准确，字段列完整，可跳转案卷详情。 | 查询自动化。 |
| TC-X-002 | P1 | Happy | 高级案件查询-控制标记与费用维度 | FR-DL-07<br>FR-FE-09 | 系统中存在有/无费减、有/无年费监视、有/无未结账单的案件。 | 按 IsFeeMonitor、ApplicantKind、HasExamRequest、NoPower、NoPrioText、FeeReduction、未结账单、年费欠款等维度查询。 | 联查条件生效，结果准确。 | 查询自动化。 |
| TC-X-003 | P1 | Happy | 中间文件查询与清单导出 | FR-WD-07 | 存在多种 DocType 和模板的文档。 | 按 DocType、TemplateCode、CaseNo、Client、DispatchDate、NeedReply/ReplyDate 查询并导出清单/证书清单。 | 查询结果正确；导出文件内容与过滤条件一致。 | UI+文件对比。 |
| TC-X-004 | P1 | Happy | 费用情况查询双表 | FR-FE-09 | 存在 GovPayment 和 CaseReceipt 数据。 | 进入费用情况查询，按 CaseNo/AppNo/Client/日期范围检索。 | 上半表显示官费缴费一览，下半表显示个案收款一览；字段与金额对应正确。 | 查询自动化。 |
| TC-X-005 | P1 | Happy | 申请费时限检索 | FR-DL-07 | 存在 OPEN 的 APPLY_FEE_LIMIT 任务，部分已有草单或清单。 | 按 Deadline 区间、CaseType、Client、Agent 查询申请费时限。 | 仅未完成申请费时限返回；可看到是否已有草单/官费清单等辅助字段。 | 查询自动化。 |
| TC-X-006 | P1 | Happy | 实审请求时限检索 | FR-DL-07 | 存在 EXAM_REQUEST_LIMIT 任务，部分案件 HasExamRequest=true。 | 按 Deadline 区间和 HasExamRequest=false 条件查询。 | 仅尚未提实审且任务未完成的案件被返回。 | 查询自动化。 |
| TC-X-007 | P1 | Happy | 案件统计报表 | FR-CM-04 | 系统中有多客户、多国别、多代理人、多状态案件。 | 生成按客户/国别/代理人/年度的案件统计报表。 | 新案数、授权数、终止/无效数、在审数量等指标正确。 | 报表校验脚本。 |
| TC-X-008 | P1 | Happy | 费用与收入报表 | FR-FE-09<br>FR-BL-01 | 存在多类型账单和回款。 | 生成按客户、案件类型、国别、时间段的费用与收入报表。 | 服务费、官费、未收金额汇总正确；可选仅已收/部分收口径也正确。 | 报表校验脚本。 |
| TC-X-009 | P1 | Happy | 年费统计报表 | FR-FE-06 | 存在多年度 T_AnnuityTask、GovPayment、CaseReceipt。 | 生成按国别/客户/年份的年费统计报表。 | 应缴/实缴/客户实收/放弃终止等指标正确。 | 报表校验。 |
| TC-X-010 | P1 | Happy | 应收/逾期/坏账报表 | FR-BL-07<br>FR-BL-08 | 存在 UNSETTLED/PARTIALLY_SETTLED/BAD_DEBT 账单和催款批次。 | 生成应收账款、逾期账款、坏账和催款效果报表。 | 账龄区间、坏账金额、催款后 30/60/90 天回款量正确。 | 报表校验。 |
| TC-X-011 | P1 | Happy | 提成报表 | FR-COM-07 | 存在多代理人、多案件、多结算批次提成数据。 | 生成按代理人/案件/时间区间的提成报表。 | BaseFee、S1_Amt、S2_Amt、SettleNo、SettleDate 等字段准确可导出。 | 报表校验。 |
| TC-X-012 | P0 | Happy | 任务操作日志 | FR-DL-10 | 准备一条手工任务或官方任务。 | 依次执行 CREATE、UPDATE、CHANGE_WORKER、CHANGE_SUPERVISOR、MARK_DONE、UNMARK_DONE、CANCEL、RESTORE。 | T_TaskLog 记录 8 类动作，OldValue/NewValue/ActionBy/ActionAt 完整。 | API+DB。 |
| TC-X-013 | P1 | Happy/Unhappy | 反冲销 | FR-BL-06 | 存在 1 条可反冲销 Offset 和 1 条超过允许窗口的 Offset。 | 对两条 Offset 分别执行反冲销。 | 可反冲销记录被标记 IsReversed=true，并回滚 Bill/PaymentLine 余额；超窗口记录被阻止。 | 服务层+DB。 |
| TC-X-014 | P1 | Happy | 手工 AP 账单 | FR-BL-03<br>V-BL-05<br>V-BL-07 | Finance 登录；准备外所/供应商客户。 | 手工创建 Direction=AP 的账单并录入 1~2 条明细。 | AP 账单保存成功，Amount=明细 LocalAmount 合计；在客户应收统计中不计入 AR。 | UI+DB。 |
| TC-X-015 | P1 | Happy | 非案件账单 | FR-BL-03<br>V-BL-06<br>V-BL-07 | Finance 登录。 | 创建手工账单时让 BillItem.CaseID 为空并保存。 | 账单保存成功；明细被标记为非案件账单；不进入案件维度统计或需单独分类。 | UI+DB。 |
| TC-X-016 | P1 | Happy | 账单打印/导出 | FR-BL-04 | 存在已保存账单和中英模板。 | 分别导出中文、英文和 Excel 账单。 | 模板带出 BillNo、ClientName、费用明细和汇总金额；导出文件可下载；必要时可归档到电子文档。 | 文件渲染 smoke。 |
| TC-X-017 | P1 | Happy | 我的任务与监督任务视图 | FR-DL-04<br>FR-DL-05<br>FR-DL-08<br>FR-DL-09 | 存在当前用户的 Worker 任务和 Supervisor 任务。 | 进入我的任务、监督任务和首页提醒，按内限/绝限、状态、逾期、类型过滤并导出。 | 两类视图只显示与当前用户相关任务；排序、筛选、导出和首页提醒正确。 | UI 自动化。 |
| TC-X-018 | P1 | Happy | 邮寄信息登记 | FR-WD-08 | 存在多条 OFFICIAL_OUT/CLIENT_OUT 文档。 | 查询待寄出文档，在第一条填写挂号号并执行“复制到全部”，再保存。 | OutgoingRegNo 和可选 ForwardDate 批量更新成功；复制逻辑正确。 | UI+DB。 |
| TC-X-019 | P1 | Happy | 文件交接单 | FR-WD-09 | 同一客户同一日期存在多份去文。 | 选择客户+日期生成 Dispatch 单，确认明细后保存并导出 Word。 | T_DocDispatch/T_DocDispatchLine 创建成功；导出的交接单列出所有文档与挂号号。 | UI+DB+文件。 |
| TC-X-020 | P1 | Happy/Boundary | 信封打印地址优先级 | FR-WD-10 | 分别准备 Case.DocAddressID、客户默认地址、申请人地址、无地址四类案件。 | 输入 CaseNo/AppNo 打印信封。 | 系统按 Case.DocAddressID→客户默认文件地址→第一申请人地址→手工指定 的优先级选地址；缺失时要求人工指定。 | UI 自动化。 |
| TC-X-021 | P1 | Happy | 附件查看/删除权限 | FR-WD-06 | 存在带多附件的文档；准备 Formalities、Agent、无删除权限用户。 | 查看附件列表并尝试下载/删除。 | 有权用户可查看和删除；无权用户只能查看不能删除；删除后附件记录和物理文件状态一致。 | UI+存储断言。 |
| TC-X-022 | P0 | Happy | NORMAL/PCT_NATIONAL 状态机 | FR-CM-04 | 准备普通案子案。 | 依次触发 NOT_FILED→WAITING_RECEIPT→SUB_EXAM/OA1→GRANTED→TERMINATED/INVALIDATED 等关键状态事件。 | 状态迁移符合状态总表；关键字段同步更新；非法缺字段时不允许进入下一状态。 | 服务层状态机自动化。 |
| TC-X-023 | P1 | Happy | PCT_INTL / INVALIDATION / LITIGATION / CONSULTING 状态机 | FR-CM-04<br>FR-CS-01 | 准备 PCT_INTL、INVALIDATION、LITIGATION、CONSULTING/SEARCH 四类案件。 | 依状态总表分别触发关键事件：PCT 受理/国际公开/国家进入；无效 filed/accepted/hearing/decision；诉讼 filed/accepted/hearing/judgment；顾问 not_started/in_progress/completed/closed。 | 每类案卷均按各自状态机迁移，且互不混淆。 | 服务层自动化。 |
| TC-X-024 | P0 | Unhappy | 非法直接跳状态 | FR-CM-04 | 准备处于早期状态的各类案件。 | 尝试手工或接口将 NOT_FILED 直接改为 GRANTED、将 PCT_INTL 直接改为 GRANTED、将顾问案未完成直接 CLOSED。 | 系统阻断非法跳转或要求满足前置条件；审计日志记录拒绝/异常。 | 服务层自动化。 |
| TC-X-025 | P1 | Happy | 个案收款手工登记 | FR-FE-07<br>V-CR-01<br>V-CR-02<br>V-CR-03 | 存在一个无账单或历史迁移案件。 | 从个案收款菜单逐案登记 ReceivableAmt/ReceivedAmt/FeeCode/FeeType/ReceiptDate/InvoiceNo。 | CaseReceipt 保存成功；Received<Receivable 时标记欠款；Received>Receivable 时识别预收并确认。 | UI+DB。 |
| TC-X-026 | P1 | Happy | 费率导入导出 | FR-FE-01 | 准备费率 Excel 或 CSV。 | 批量导入标准费率，再导出比对。 | 导入成功且字段映射正确；导出结果与数据库一致。 | 适合脚本化。 |
| TC-X-027 | P1 | Happy/Unhappy | 手工任务日期与状态校验 | FR-DL-06<br>V-TASK-01<br>V-TASK-02<br>V-TASK-03<br>V-TASK-04<br>V-TASK-05 | 任意案件；有任务维护权限的用户。 | 手工创建/编辑任务，分别测试 Deadline<BaseDate、InnerDeadline>Deadline、Remind>Deadline、Status=DONE 但 DoneDate 为空、Status=OPEN 但 DoneDate 非空；再输入合法组合保存。 | 非法组合均被拒绝；合法组合可保存；状态与完成日的一致性得到保证。 | 服务层自动化。 |

## 7. FR 覆盖矩阵

> 说明：每条 FR 至少映射 1 条以上详细用例；关键 FR 映射了 Happy + Unhappy/Boundary 多条用例。

| FR ID | 描述 | 覆盖用例 |
| --- | --- | --- |
| FR-BL-01 | 系统必须支持维护账单头 `T_Bill` 与账单明细 `T_BillItem`，包括收付方向（应收/应付）、账单状态（尚未冲销/部分冲销/已经冲销/坏账）、折扣率、坏账信息等。 | TC-A-019, TC-X-008 |
| FR-BL-02 | 系统必须支持从费用草单 `T_FeeDraft/T_FeeItem` 自动生成账单（应收为主），并绑定账单明细与原草单/费用明细。 | TC-A-019, TC-A-020, TC-B-011, TC-G0-008, TC-D-010, TC-E-011, TC-H-006 |
| FR-BL-03 | 系统必须支持纯手工创建账单，允许直接录入明细行（不依赖草单），同时支持 AR（应收）与 AP（应付）方向。 | TC-A-020, TC-X-014, TC-X-015 |
| FR-BL-04 | 系统必须支持基于模板系统打印/导出账单文档（中/英、不同版式）。 | TC-W0-012, TC-X-016 |
| FR-BL-05 | 系统必须支持记录收款 `T_Payment`，并通过 `T_Offset` 将收款分配到一个或多个账单上，自动更新账单余额与状态。 | TC-A-021, TC-A-022, TC-B-011, TC-C-012, TC-G0-008, TC-D-010, TC-E-011, TC-F-005, TC-F-006, TC-F-007, TC-G-005, TC-G-008, TC-H-006 |
| FR-BL-06 | 系统必须支持对冲销记录进行反冲销（在时间/权限控制下），恢复账单余额与收款余额。 | TC-W0-014, TC-X-013 |
| FR-BL-07 | 系统必须支持将账单标记为坏账/从坏账恢复，并在催款与普通统计中区别显示。 | TC-G-001, TC-G-007, TC-G-008, TC-G-009, TC-X-010 |
| FR-BL-08 | 系统必须支持生成催款单 `T_Dunning/T_DunningLine`，按客户+截止日期列出未结账单，并可基于模板生成催款函。 | TC-G-001, TC-G-002, TC-G-003, TC-G-004, TC-G-005, TC-G-006, TC-X-010 |
| FR-BL-09 | 系统必须支持预收款管理：允许登记预收收款行，在未分配到账单时保持“预收状态”，并在后续冲销账单时从预收款中扣减。 | TC-W0-013, TC-F-001, TC-F-002, TC-F-003, TC-F-004, TC-F-005, TC-F-006, TC-F-008, TC-F-009 |
| FR-CM-01 | 系统必须支持根据案件类型、专利类别、申请方向创建新案，案卷号在全系统唯一。 | TC-W0-005, TC-A-001, TC-A-003, TC-A-004, TC-C-001, TC-C-008, TC-E-001, TC-E-003, TC-X-001 |
| FR-CM-02 | 保存时必须校验必填字段及组合规则（案卷号唯一、法律状态与申请号/申请日对应、优先权完整性等）。 | TC-A-001, TC-A-002, TC-A-003, TC-A-005, TC-A-006, TC-A-008, TC-A-009, TC-D-013 |
| FR-CM-03 | 系统必须支持从主数据中选择客户、申请人、外方代理，并允许从案卷界面跳转创建新记录后回填。 | TC-W0-001, TC-W0-003, TC-W0-004, TC-A-002, TC-A-005, TC-A-007 |
| FR-CM-04 | 系统必须维护完整的法律状态枚举，并支持由中间文件/流程自动更新。 | TC-A-011, TC-B-008, TC-G0-001, TC-D-007, TC-D-011, TC-E-004, TC-E-008, TC-E-009, TC-E-010, TC-X-007, TC-X-022, TC-X-023, TC-X-024 |
| FR-CM-05 | 系统必须支持 A）0..n 条优先权记录，B）0..n 条菌种保藏记录，C）PCT 国际/国家阶段字段，D）无效案专属字段。 | TC-W0-006, TC-A-002, TC-C-001, TC-C-002, TC-C-003, TC-C-005, TC-C-007, TC-C-008, TC-C-009, TC-C-010, TC-E-001, TC-E-002, TC-E-013 |
| FR-CM-06 | 系统必须提供“限制修改视图”，只允许编辑白名单字段，权限独立控制。 | TC-W0-014, TC-A-010 |
| FR-CM-07 | 系统必须提供“案件递交批处理”，依据筛选条件列出案件，并批量设置递交日期、提实审与法律状态。 | TC-A-011, TC-A-012, TC-C-012 |
| FR-COM-01 | 系统必须支持维护提成规则 `T_CommissionRule`，包括一次/二次提成比例、基数计算方式和适用范围。 | TC-A-023, TC-E-012, TC-H-007 |
| FR-COM-02 | 系统必须支持在服务费账单生成时，根据提成规则自动为相关案件和代理人生成或更新提成记录 `T_Commission`。 | TC-A-023, TC-B-012, TC-C-012, TC-G0-010, TC-D-012, TC-E-012, TC-E-014, TC-H-007 |
| FR-COM-03 | 系统必须支持多代理人（主办/协办/团队成员）按比例分摊提成基数，并分别记录各自提成金额。 | TC-A-023, TC-B-012, TC-E-014 |
| FR-COM-04 | 系统必须支持 `WaitPay`（款到后才能结算）逻辑，即在相关账单收款比例未达条件时，将提成记录标记为“不可结算”。 | TC-W0-013, TC-A-023, TC-A-024, TC-B-012, TC-G0-010, TC-D-012, TC-E-012, TC-F-010, TC-G-010 |
| FR-COM-05 | 系统必须支持 `ForceSettle`（案件可结算酬金）逻辑，以允许对特殊案件提前结算提成。 | TC-W0-013, TC-A-024, TC-F-010, TC-G-010 |
| FR-COM-06 | 系统必须支持提成结算批次 `T_CommissionSettlement` 的创建，与结算明细 `T_CommissionSettleLine` 的生成，并标记对应的提成记录（S1\_Done/S2\_Done）。 | TC-G0-010, TC-E-012, TC-H-007 |
| FR-COM-07 | 系统必须提供提成结算报表，按代理人/案件/时间区间统计提成金额，并支持导出。 | TC-X-011 |
| FR-CS-01 | 系统必须支持以 CaseType=CONSULTING/SEARCH 的方式为顾问/检索项目建立案卷记录，并记录项目专属属性（范围、负责人、预计工时等）。 | TC-W0-005, TC-H-001, TC-H-008, TC-X-023 |
| FR-CS-02 | 系统必须允许在顾问/检索案卷上创建内部任务 `T_Task`（非官方时限任务），用于项目执行管理。 | TC-B-005, TC-H-002 |
| FR-CS-03 | 系统必须支持记录顾问/检索项目的支出费用 `T_Expense`，按案件/类别/时间进行查询和统计。 | TC-H-003 |
| FR-CS-04 | 系统必须支持为顾问/检索项目生成服务费草单 `T_FeeDraft/T_FeeItem`，支持固定报价、按工时计费或混合模式。 | TC-H-004, TC-H-005 |
| FR-CS-05 | 系统必须支持从顾问/检索草单生成账单 `T_Bill/T_BillItem`，并使用收款/冲销机制处理相关款项。 | TC-H-006, TC-H-008 |
| FR-CS-06 | 系统必须支持按照 `T_CommissionRule` 的 CONSULTING/SEARCH 规则为顾问/检索项目生成提成记录 `T_Commission`，并纳入结算批次。 | TC-H-007, TC-H-008 |
| FR-DL-01 | 系统必须支持维护时限模板（起算基准、年/月/日增量、提醒规则、默认监督人/责任人）。 | TC-W0-009, TC-A-014 |
| FR-DL-02 | 系统必须能根据时限模板，从案件事件/中间文件/年费任务中自动创建时限任务。 | TC-A-013, TC-A-014, TC-B-002, TC-B-004, TC-C-003, TC-C-005, TC-C-006, TC-G0-003, TC-E-005 |
| FR-DL-03 | 每个时限任务必须区分“作业人”和“监督人”，并在不同视图中以不同角色展示。 | TC-A-013, TC-B-004, TC-C-006, TC-G0-003 |
| FR-DL-04 | 系统必须为作业人提供“我的时限任务”视图，按内部时限/官方绝限排序，支持核销/取消核销。 | TC-B-008, TC-C-011, TC-E-006, TC-X-017 |
| FR-DL-05 | 系统必须为监督人提供“监督时限”视图，按作业人/类型/状态/逾期情况过滤任务。 | TC-X-017 |
| FR-DL-06 | 系统必须支持手工新增/编辑/删除时限任务（受角色/权限控制）。 | TC-W0-014, TC-B-005, TC-B-013, TC-H-002, TC-X-027 |
| FR-DL-07 | 系统必须提供“申请费时限检索”和“实审时限检索”，用于批量查找尚未缴费/尚未提实审案件。 | TC-C-007, TC-D-003, TC-X-002, TC-X-005, TC-X-006 |
| FR-DL-08 | 登录或进入首页时，系统必须自动查询并展示当前用户相关的“今日提醒清单”。 | TC-X-017 |
| FR-DL-09 | 系统必须允许将任意时限列表导出/打印为期限清单。 | TC-X-017 |
| FR-DL-10 | 系统必须记录时限任务的关键操作日志（创建、修改、责任人变更、核销、取消核销、取消任务）以便审计。 | TC-A-013, TC-B-004, TC-B-008, TC-C-011, TC-E-006, TC-X-012 |
| FR-FE-01 | 系统必须支持维护标准费率表 `T_FeeRate`，按费用类型/国别/专利类别/案件类型区分官费、服务费、杂费及默认金额与币种。 | TC-W0-005, TC-W0-007, TC-W0-008, TC-X-026 |
| FR-FE-02 | 系统必须支持按“案件+草单类型”创建费用草单 `T_FeeDraft`，并包含 1..N 条费用明细 `T_FeeItem`。 | TC-A-015, TC-A-016, TC-B-009, TC-G0-006, TC-D-005, TC-E-011, TC-H-004, TC-H-005 |
| FR-FE-03 | 系统必须根据标准费率表 + 案件参数 + 费减比例/折扣率，自动计算费用明细金额，可被用户手工覆盖。 | TC-W0-007, TC-W0-008, TC-A-015, TC-A-016, TC-B-009, TC-D-005, TC-D-008, TC-H-004, TC-H-005 |
| FR-FE-04 | 系统必须支持基于费用草单构造“官费清单 `T_PayList` + 官费缴费明细 `T_GovPayment`”，并支持导出、缴费登记以及状态追踪。 | TC-A-017, TC-A-018, TC-B-010, TC-C-012, TC-G0-008, TC-D-009, TC-E-011 |
| FR-FE-05 | 系统必须支持年登印费管理：从授权案件中提取登记费任务，记录客户指示与通知状态，并自动生成相关草单与通知函。 | TC-G0-004, TC-G0-005, TC-G0-006, TC-G0-007 |
| FR-FE-06 | 系统必须支持年费管理：按到期区间提取年费任务，记录客户指示/通知状态，并自动生成年费草单与通知函。 | TC-G0-009, TC-D-001, TC-D-002, TC-D-003, TC-D-004, TC-D-005, TC-D-006, TC-D-007, TC-D-009, TC-D-011, TC-D-013, TC-X-009 |
| FR-FE-07 | 系统必须支持个案收款登记 `T_CaseReceipt`，记录应收/实收、欠款标记、可提成标记和发票信息。 | TC-A-021, TC-B-011, TC-G0-008, TC-D-010, TC-E-011, TC-F-008, TC-G-005, TC-G-008, TC-H-006, TC-X-025 |
| FR-FE-08 | 系统必须支持第三方支出记录 `T_Expense`，并可按案件、项目、时间查询与统计。 | TC-H-003 |
| FR-FE-09 | 系统必须提供“费用情况查询”，将官方缴费记录与个案收款记录以两张一览表方式展示。 | TC-X-002, TC-X-004, TC-X-008 |
| FR-WD-01 | 系统必须支持四大类中间文件（官方来文、致函官方、客户来文、致函客户），以及可配置子类型（常用文件定义）。 | TC-W0-010, TC-B-001, TC-C-004 |
| FR-WD-02 | 系统必须提供“中间文件录入向导”，支持对 1..N 个案件批量登记中间文件。 | TC-B-001, TC-B-003, TC-B-006, TC-C-004, TC-E-004 |
| FR-WD-03 | 系统必须根据常用文件定义自动填充缺省字段（是否需通知代理人、是否需回复、时限模板、费用草单类型、案件状态变更等）。 | TC-W0-010, TC-W0-011, TC-B-001, TC-B-006, TC-B-007, TC-G0-001, TC-G0-002, TC-E-008 |
| FR-WD-04 | 对“需要回复”的中间文件，系统必须自动计算回复绝限、内部限和提醒日期，并建立对应的时限任务记录。 | TC-B-001, TC-B-002, TC-B-007, TC-B-013, TC-C-012, TC-E-005, TC-E-006, TC-E-007 |
| FR-WD-05 | 对定义了费用草单类型/费用项目的中间文件，系统必须自动生成关联费用草单，并可手工补充。 | TC-B-009, TC-E-004 |
| FR-WD-06 | 系统必须支持为每个中间文件存档 0..N 个电子附件，并支持查看/导出。 | TC-B-006, TC-C-004, TC-G0-005, TC-D-004, TC-G-004, TC-X-021 |
| FR-WD-07 | 系统必须支持按多种条件查询中间文件，并输出不同格式的中间文件清单/证书清单。 | TC-X-003 |
| FR-WD-08 | 系统必须支持“邮寄信息登记”，对一批中间文件统一输入挂号号，支持“一号复制给全部”或逐条录入。 | TC-X-018 |
| FR-WD-09 | 系统必须支持为指定客户+邮寄日期生成“文件交接单”，并支持打印或基于模板生成 Word 版本。 | TC-W0-001, TC-W0-012, TC-X-019 |
| FR-WD-10 | 系统必须支持信封打印，按“客户地址/申请人联系人/申请人地址”的优先级自动选择收件人信息，并打印信封版式。 | TC-W0-001, TC-W0-002, TC-W0-012, TC-X-020 |

## 8. 校验规则（V-*）覆盖矩阵

> 说明：以下矩阵覆盖规格中显式列出的字段/流程校验规则。
> 若同一规则在多个场景复用，则会映射到多条用例。

| 规则ID | 覆盖用例 |
| --- | --- |
| V-A-01 | TC-A-001, TC-A-003 |
| V-A-02 | TC-A-004 |
| V-A-03 | TC-A-005 |
| V-A-04 | TC-A-008 |
| V-B-01 | TC-A-005 |
| V-B-02 | TC-A-005 |
| V-BF-01 | TC-A-011, TC-A-012 |
| V-BF-02 | TC-A-011, TC-A-012 |
| V-BL-01 | TC-A-019, TC-A-020 |
| V-BL-02 | TC-A-019, TC-A-020 |
| V-BL-03 | TC-A-019, TC-A-020 |
| V-BL-04 | TC-A-019, TC-A-020 |
| V-BL-05 | TC-X-014 |
| V-BL-06 | TC-X-015 |
| V-BL-07 | TC-X-014, TC-X-015 |
| V-C-01 | TC-A-001, TC-A-006 |
| V-C-02 | TC-A-001, TC-A-006 |
| V-C-03 | TC-A-006 |
| V-C-04 | TC-A-002 |
| V-C-05 | TC-A-007 |
| V-C-06 | TC-W0-002, TC-A-007 |
| V-C-07 | TC-A-007 |
| V-CR-01 | TC-A-021, TC-X-025 |
| V-CR-02 | TC-A-022, TC-F-008, TC-X-025 |
| V-CR-03 | TC-A-021, TC-X-025 |
| V-D-01 | TC-A-008, TC-G0-001, TC-G0-002 |
| V-D-02 | TC-A-008 |
| V-D-03 | TC-A-008 |
| V-D-04 | TC-A-008 |
| V-DOC-01 | TC-B-003 |
| V-DOC-02 | TC-B-003 |
| V-DOC-03 | TC-B-003 |
| V-DOC-04 | TC-B-003 |
| V-DOC-05 | TC-B-003, TC-G0-002 |
| V-E-01 | TC-A-009 |
| V-E-02 | TC-A-009 |
| V-E-03 | TC-D-013 |
| V-EX-01 | TC-H-003 |
| V-EX-02 | TC-H-003 |
| V-FD-01 | TC-A-015, TC-A-016 |
| V-FD-02 | TC-A-015, TC-A-016 |
| V-FI-01 | TC-A-015, TC-A-016 |
| V-FI-02 | TC-A-016 |
| V-FI-03 | TC-A-015, TC-A-016 |
| V-FI-04 | TC-D-005, TC-D-008 |
| V-FI-05 | TC-A-015 |
| V-GF-01 | TC-G0-007 |
| V-GF-02 | TC-G0-006, TC-G0-007 |
| V-GP-01 | TC-A-017 |
| V-GP-02 | TC-A-017 |
| V-GP-03 | TC-A-018 |
| V-INV-01 | TC-E-001, TC-E-002 |
| V-INV-02 | TC-E-001, TC-E-002 |
| V-INV-03 | TC-E-001 |
| V-OF-01 | TC-A-021, TC-A-022, TC-F-005, TC-F-007 |
| V-OF-02 | TC-A-021, TC-A-022, TC-F-005, TC-F-007 |
| V-P-01 | TC-A-002 |
| V-P-02 | TC-A-002 |
| V-P-03 | TC-A-002 |
| V-PCT-01 | TC-C-001, TC-C-002 |
| V-PCT-02 | TC-C-009 |
| V-PCT-03 | TC-C-003 |
| V-PL-01 | TC-A-017, TC-A-018 |
| V-PL-02 | TC-A-017, TC-A-018 |
| V-PL-03 | TC-A-017, TC-A-018 |
| V-PM-01 | TC-A-021, TC-A-022, TC-F-001, TC-F-002 |
| V-PM-02 | TC-A-021, TC-A-022, TC-F-001, TC-F-002 |
| V-PM-03 | TC-A-021, TC-A-022, TC-F-001, TC-F-002 |
| V-TASK-01 | TC-X-027 |
| V-TASK-02 | TC-X-027 |
| V-TASK-03 | TC-X-027 |
| V-TASK-04 | TC-X-027 |
| V-TASK-05 | TC-X-027 |
| V-TM-01 | TC-W0-009 |
| V-TM-02 | TC-W0-009 |
| V-TM-03 | TC-W0-009, TC-A-014 |
| V-TM-04 | TC-W0-009, TC-A-014 |
| V-TPL-01 | TC-W0-010, TC-W0-011 |
| V-TPL-02 | TC-W0-010, TC-W0-011 |
| V-TPL-03 | TC-W0-010, TC-W0-011 |
| V-TPL-04 | TC-W0-010, TC-W0-011 |
| V-TPL-05 | TC-W0-010, TC-W0-011 |


## 9. 边界条件专项矩阵

> 本矩阵用于补充“详细用例表”之外的参数化边界测试。
> 自动化时建议将这些边界点做成 **data-driven** 测试集。

| 边界ID | 对象 | 边界点 | 测试值 | 预期 |
| --- | --- | --- | --- | --- |
| BND-001 | CaseNo | 最小非空/唯一 | 动态值 CASE-${RUN_ID}-001 / 重复现有 CaseNo | 非空且唯一时可保存；重复时报错 |
| BND-002 | Title_CN | 仅空白字符 | '   ' | 应视为无效并阻止保存 |
| BND-003 | FilingDate vs PrioDate | 等于/小于 | 2026-03-15 = 2026-03-15；2026-03-14 < 2026-03-15 | 等于允许；小于拒绝 |
| BND-004 | SubmittedDate vs RecvDate | 等于/小于 | 2026-04-01 = 2026-04-01；2026-03-31 < 2026-04-01 | 等于允许；小于拒绝/警告 |
| BND-005 | FeeReduction | 0/1/越界 | 0；1；-0.01；1.01 | 0 和 1 合法；越界拒绝 |
| BND-006 | DiscountRate | 0/1/越界 | 0；1；-0.01；1.01 | 0 和 1 合法；越界拒绝 |
| BND-007 | SpecPages/DrawPages/ClaimCount/ClaimPages/ManuscriptWords | 0/超大正整数 | 0；99999 | 非负允许；系统不应溢出 |
| BND-008 | ClaimCount 超项阈值 | 阈值点 | 10；11 | 10 不加收或仅基础费；11 触发 1 项超项费 |
| BND-009 | Page 超页阈值 | 阈值点 | 30；31 | 31 触发超页费 |
| BND-010 | Task Deadline vs BaseDate | 等于/早于 | Deadline=BaseDate；Deadline<BaseDate | 等于可保存；早于拒绝 |
| BND-011 | InnerDeadline vs Deadline | 等于/晚于 | Inner=Deadline；Inner>Deadline | 等于允许；晚于拒绝 |
| BND-012 | RemindX | 等于 Deadline / 晚于 Deadline | Remind=Deadline；Remind>Deadline | 等于允许；晚于拒绝 |
| BND-013 | Payment Amount | 0/负数 | 0；-1 | 按实现决定 0 是否允许；负数拒绝 |
| BND-014 | OffsetAmt vs PaymentLine.BalanceAmt | 等于/大于 | 1000；1001 | 等于可全额冲销；大于拒绝 |
| BND-015 | OffsetAmt vs Bill.Balance | 等于/大于 | 600；601 | 等于可全额结清；大于拒绝 |
| BND-016 | CaseReceipt ReceivedAmt vs ReceivableAmt | 等于/小于/大于 | 1000；800；1200 | 等于结清；小于欠款；大于识别预收 |
| BND-017 | Annuity YearNo | 等于/小于 FirstAnnuityYear | 3；2 | 等于允许；小于拒绝 |
| BND-018 | GovPayment PaidAmt | 空/0/正数 | NULL；0；PlannedAmt | 空值默认 PlannedAmt；0 或正数按业务规则处理 |
| BND-019 | OutgoingRegNo/IncomingRegNo | 长度上限 | 最大长度；超长 | 达到上限允许；超长拒绝 |
| BND-020 | NotifyCount | 0→1→N | 0,1,2... | 每次发送通知仅递增 1，不允许回退为负 |

---

## 10. 执行建议（给 Codex / 人工测试）

### 10.1 给 Codex 的拆分建议

建议按以下目录拆分自动化仓库：

- `tests/w0_setup/`
- `tests/e2e_a_case_creation/`
- `tests/e2e_b_oa/`
- `tests/e2e_c_pct_national/`
- `tests/e2e_g0_grant/`
- `tests/e2e_d_annuity/`
- `tests/e2e_e_invalid_litigation/`
- `tests/e2e_f_prepayment/`
- `tests/e2e_g_dunning_bad_debt/`
- `tests/e2e_h_consulting_search/`
- `tests/x_search_report_audit/`

### 10.2 自动化优先级建议

- **P0 先自动化**：案卷创建、批量递交、OA 来/去文、关键时限、草单/账单/收款/冲销、授权、年费、预收、坏账、提成主干。
- **P1 第二批**：模板校验、报表、交接单、信封、附件权限、复杂状态机。
- **P2 末批**：极端参数、较少发生的人工维护路径、恢复/强制保存策略差异。

### 10.3 人工执行建议

- 每个 Wave 至少先跑 1 次 **端到端 happy path**。
- 对“警告 vs 阻断”的功能，必须在测试记录里明确当前环境参数。
- 所有涉及文档输出的用例，除字段值外，还要人工检查：
  - 模板语言
  - 抬头/信头
  - 明细表格列
  - 附件归档路径

### 10.4 回归策略建议

- **日常回归**：W0-关键配置 + A + B + G0 + D + X 中的 P0
- **发版回归**：全量执行 155 条详细用例 + 20 组边界矩阵
- **财务/提成专项回归**：A4/A5/A6/A7/A8、G0、D、F、G、H、X-报表

---

## 11. 备注

1. 本文档默认把 FPMS SPEC 2.0 中的**显式功能、显式校验、显式状态迁移、显式 E2E 场景**全部转成了可执行测试项。
2. 若后续要进一步落地为自动化脚本，建议在此 Markdown 基础上再补一层：
   - Page Object / API Client
   - Seed Data Builder
   - DB Assertion Library
   - Report/File Snapshot Comparator
3. 若你后续要我继续做下一步，最自然的是把这份文档再拆成：
   - `testdata.json/yaml`
   - `pytest/playwright` 目录结构
   - `priority smoke suite`
   - `full regression suite`
