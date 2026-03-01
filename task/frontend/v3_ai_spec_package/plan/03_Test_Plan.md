# FPMS V3 Case Workflow Stepper — 测试计划

> **版本**: 1.1
> **日期**: 2026-02-22
> **作者**: Test Agent
> **状态**: 后端测试已通过（29/29），前端测试待实现

---

## 1. 测试范围

本测试计划覆盖 V3 Case Workflow Stepper 功能的全部新增与修改，包括：
- 后端 CaseStatus 枚举扩展验证
- 后端 GET /cases/{id} 返回完整字段验证
- 后端 GET /cases 列表返回新增字段验证
- 前端 workflow.ts 状态映射逻辑单元测试
- 前端组件渲染与交互测试
- 端到端交互流验证

---

## 2. 后端 API 测试用例

### 2.1 CaseStatus 枚举扩展验证

| 用例 ID | 描述 | 前置条件 | 测试步骤 | 预期结果 | 实现状态 |
|---|---|---|---|---|---|
| BE-01 | V3 新增状态值均可用于创建案件 | 已登录 admin 用户 | 通过 ORM 创建各 V3 状态案件，验证列表和详情 API | 全部 13 种状态可查询 | ✅ 已通过 |
| BE-02 | 所有 13 种 V3 法律状态均在 CaseStatus 枚举中 | 无 | 导入 CaseStatus 枚举，检查 13 个值是否存在 | 全部存在 | ✅ 已通过 |
| BE-03 | 现有状态值（NOT_FILED 等）保持向后兼容 | 无 | 检查旧枚举值仍存在于 CaseStatus | 全部存在 | ✅ 已通过 |

### 2.2 GET /cases/{id} 返回完整字段

| 用例 ID | 描述 | 前置条件 | 测试步骤 | 预期结果 | 实现状态 |
|---|---|---|---|---|---|
| BE-04 | 详情返回 title_cn 字段 | 创建含 title_cn 的案件 | GET /cases/{id} | 响应包含 title_cn | ✅ 已通过 |
| BE-05 | 详情返回 status 字段 | 创建案件 | GET /cases/{id} | 响应包含 status，默认 "NOT_FILED" | ✅ 已通过 |
| BE-06 | 详情返回 filing_date 字段 | 创建案件 | GET /cases/{id} | 响应包含 filing_date（可为 null） | ✅ 已通过 |
| BE-07 | 详情返回 recv_date 字段 | 创建案件 | GET /cases/{id} | 响应包含 recv_date（可为 null） | ✅ 已通过 |
| BE-08 | 详情返回 client_name 字段 | 创建客户+案件关联 | GET /cases/{id} | 响应包含 client_name = 客户中文名 | ✅ 已通过 |
| BE-09 | 详情返回 applicants 列表 | 创建含申请人的案件 | GET /cases/{id} | 响应包含 applicants 数组 | ✅ 已通过 |
| BE-10 | 详情返回 inventors 列表 | 创建含发明人的案件 | GET /cases/{id} | 响应包含 inventors 数组 | ✅ 已通过 |
| BE-11 | 详情返回 priorities 列表 | 创建含优先权的案件 | GET /cases/{id} | 响应包含 priorities 数组 | ✅ 已通过 |
| BE-12 | 详情返回 created_at / updated_at | 创建案件 | GET /cases/{id} | 响应包含时间戳字段 | ✅ 已通过 |
| BE-13 | client_id 为 null 时 client_name 为 null | 创建无客户案件 | GET /cases/{id} | client_name 为 null | ✅ 已通过 |

### 2.3 GET /cases 列表返回新增字段

| 用例 ID | 描述 | 前置条件 | 测试步骤 | 预期结果 | 实现状态 |
|---|---|---|---|---|---|
| BE-14 | 列表 items 包含 client_name | 创建客户+案件 | GET /cases | items 中每条包含 client_name | ✅ 已通过 |
| BE-15 | 列表 items 包含 title_cn | 创建含标题案件 | GET /cases | items 中每条包含 title_cn | ✅ 已通过 |
| BE-16 | 列表 items 包含 status | 创建案件 | GET /cases | items 中每条包含 status | ✅ 已通过 |
| BE-17 | 列表支持 status 筛选 | 创建不同状态案件 | GET /cases?status=WAITING_RECEIPT | 仅返回匹配状态的案件 | ✅ 已通过 |
| BE-18 | 列表 items 包含 filing_date | 创建案件 | GET /cases | items 中包含 filing_date | ✅ 已通过 |
| BE-19 | 列表 items 包含 recv_date | 创建案件 | GET /cases | items 中包含 recv_date | ✅ 已通过 |

### 2.4 种子数据正确性验证

| 用例 ID | 描述 | 前置条件 | 测试步骤 | 预期结果 | 实现状态 |
|---|---|---|---|---|---|
| BE-20 | 种子数据覆盖 13 种 V3 法律状态 | 运行 seed_dev.py | 查询各状态案件数量 | 每种状态至少 1 条 | 🟡 需更新 seed_dev.py |

---

## 3. 前端单元测试用例

### 3.1 workflow.ts 状态映射

| 用例 ID | 描述 | 测试步骤 | 预期结果 | 实现状态 |
|---|---|---|---|---|
| FE-01 | WAITING_RECEIPT → 受理（第1步） | `getStatusRule('WAITING_RECEIPT')` | stepKey='ACCEPTED', stepText='受理' | 🟡 需实现 workflow.ts |
| FE-02 | PRELIM_EXAM → 初审（第2步） | `getStatusRule('PRELIM_EXAM')` | stepKey='PRELIM', stepText='初审' | 🟡 需实现 workflow.ts |
| FE-03 | PRELIM_PASS → 初审（第2步） | `getStatusRule('PRELIM_PASS')` | stepKey='PRELIM', stepText='初审' | 🟡 需实现 workflow.ts |
| FE-04 | AMENDMENT → 初审（第2步） | `getStatusRule('AMENDMENT')` | stepKey='PRELIM', stepText='初审' | 🟡 需实现 workflow.ts |
| FE-05 | PUBLISHED → 公布（第3步） | `getStatusRule('PUBLISHED')` | stepKey='PUBLISHED', stepText='公布' | 🟡 需实现 workflow.ts |
| FE-06 | SUB_EXAM → 实审（第4步） | `getStatusRule('SUB_EXAM')` | stepKey='SUB_EXAM', stepText='实审' | 🟡 需实现 workflow.ts |
| FE-07 | OA1 → 实审（第4步） | `getStatusRule('OA1')` | stepKey='SUB_EXAM', stepText='实审' | 🟡 需实现 workflow.ts |
| FE-08 | OA2 → 实审（第4步） | `getStatusRule('OA2')` | stepKey='SUB_EXAM', stepText='实审' | 🟡 需实现 workflow.ts |
| FE-09 | REEXAM → 实审（第4步） | `getStatusRule('REEXAM')` | stepKey='SUB_EXAM', stepText='实审' | 🟡 需实现 workflow.ts |
| FE-10 | GRANTED → 授权（第5步） | `getStatusRule('GRANTED')` | stepKey='GRANTED', stepText='授权' | 🟡 需实现 workflow.ts |
| FE-11 | REJECTED → 实审分支（第4步） | `getStatusRule('REJECTED')` | stepKey='SUB_EXAM', branchNote 非空 | 🟡 需实现 workflow.ts |
| FE-12 | TERMINATED → 授权分支（第5步） | `getStatusRule('TERMINATED')` | stepKey='GRANTED', branchNote 非空 | 🟡 需实现 workflow.ts |
| FE-13 | INVALIDATED → 授权分支（第5步） | `getStatusRule('INVALIDATED')` | stepKey='GRANTED', branchNote 非空 | 🟡 需实现 workflow.ts |
| FE-14 | 未知状态默认返回受理 | `getStatusRule('FOOBAR')` | stepKey='ACCEPTED', stepText='受理' | 🟡 需实现 workflow.ts |
| FE-15 | undefined/null 状态默认返回受理 | `getStatusRule(undefined)` | stepKey='ACCEPTED', stepText='受理' | 🟡 需实现 workflow.ts |

### 3.2 WorkflowOverview 组件

| 用例 ID | 描述 | 测试步骤 | 预期结果 | 实现状态 |
|---|---|---|---|---|
| FE-16 | 渲染 5 张阶段卡片 | mount 组件并传入统计数据 | DOM 中有 5 个 `.wf-card` 元素 | 🟡 需实现组件 |
| FE-17 | 卡片显示正确数量和占比 | 传入 `{ACCEPTED: 2, PRELIM: 3, ...}` | 每卡显示对应数量和百分比 | 🟡 需实现组件 |
| FE-18 | 点击卡片触发 emit 事件 | 点击"实审"卡 | emit('select', 'SUB_EXAM') | 🟡 需实现组件 |
| FE-19 | selected 卡片高亮样式 | 设置 selectedStep='SUB_EXAM' | 对应卡片有 `.active` class | 🟡 需实现组件 |
| FE-20 | "查看全部案件"按钮 | 点击按钮 | emit('viewAll') 或 router.push('/cases') | 🟡 需实现组件 |

### 3.3 CaseStepper 组件

| 用例 ID | 描述 | 测试步骤 | 预期结果 | 实现状态 |
|---|---|---|---|---|
| FE-21 | PUBLISHED 状态：步骤 1-2 done，步骤 3 active，步骤 4-5 默认 | 传入 status='PUBLISHED' | class 分布: done, done, active, '', '' | 🟡 需实现组件 |
| FE-22 | GRANTED 状态：全部 done | 传入 status='GRANTED' | 全部 5 步均为 done | 🟡 需实现组件 |
| FE-23 | WAITING_RECEIPT 状态：步骤 1 active，其余默认 | 传入 status='WAITING_RECEIPT' | class 分布: active, '', '', '', '' | 🟡 需实现组件 |
| FE-24 | REJECTED 分支：显示黄色警告 | 传入 status='REJECTED' | DOM 中有 `.alert-note` 元素，含分支提示文字 | 🟡 需实现组件 |
| FE-25 | TERMINATED 分支：显示黄色警告 | 传入 status='TERMINATED' | DOM 中有 `.alert-note` 元素 | 🟡 需实现组件 |
| FE-26 | KPI 卡片显示当前步骤信息 | 传入 status='SUB_EXAM' | 显示"实审"、"第4步/5"、法律状态、下一动作 | 🟡 需实现组件 |

### 3.4 CaseList 查询参数筛选

| 用例 ID | 描述 | 测试步骤 | 预期结果 | 实现状态 |
|---|---|---|---|---|
| FE-27 | 接收 route query step 参数并筛选 | 路由 `?step=SUB_EXAM` | 列表仅显示实审阶段案件 | 🟡 需实现 CaseList 增强 |
| FE-28 | 筛选说明标题显示 | 路由 `?step=SUB_EXAM` | 标题显示"案件列表 · 实审" | 🟡 需实现 CaseList 增强 |
| FE-29 | 清除阶段筛选恢复全部 | 点击"清除阶段筛选"按钮 | 路由 query 清空，列表显示全部 | 🟡 需实现 CaseList 增强 |
| FE-30 | 无 step 参数时显示全部案件 | 路由无 query | 正常分页显示全部案件 | 🟡 需实现 CaseList 增强 |

---

## 4. E2E 测试场景

### 4.1 主流程导航

| 场景 ID | 描述 | 步骤 | 预期结果 | 实现状态 |
|---|---|---|---|---|
| E2E-01 | Dashboard → 点击阶段卡 → CaseList 筛选 → CaseDetail Stepper | 1. 打开 Dashboard<br>2. 点击"实审"卡片<br>3. 验证 CaseList 页面 URL 含 `?step=SUB_EXAM`<br>4. 验证列表仅显示实审案件<br>5. 点击某案件行<br>6. 验证 CaseDetail 显示 Stepper，第4步高亮 | 全流程可通 | 🟡 需全部实现完成 |

### 4.2 清除筛选

| 场景 ID | 描述 | 步骤 | 预期结果 | 实现状态 |
|---|---|---|---|---|
| E2E-02 | CaseList 清除筛选恢复全部 | 1. 从 Dashboard 点击"受理"卡进入列表<br>2. 验证筛选生效<br>3. 点击"清除阶段筛选"<br>4. 验证列表恢复全部案件 | 筛选正确清除 | 🟡 需全部实现完成 |

### 4.3 返回链路

| 场景 ID | 描述 | 步骤 | 预期结果 | 实现状态 |
|---|---|---|---|---|
| E2E-03 | CaseDetail → 返回案件列表 → 返回仪表盘 | 1. 从 CaseDetail 点击"返回"<br>2. 回到 CaseList<br>3. 从 CaseList 点击"返回"<br>4. 回到 Dashboard | 每步导航可用 | 🟡 需全部实现完成 |

### 4.4 分支状态警告

| 场景 ID | 描述 | 步骤 | 预期结果 | 实现状态 |
|---|---|---|---|---|
| E2E-04 | 打开 REJECTED 案件验证分支警告 | 1. 在 CaseList 找到 REJECTED 案件<br>2. 进入详情页<br>3. 检查 Stepper 和警告提示 | 黄色 alert-note 显示分支信息 | 🟡 需全部实现完成 |

### 4.5 响应式断点

| 场景 ID | 描述 | 步骤 | 预期结果 | 实现状态 |
|---|---|---|---|---|
| E2E-05 | 窗口 ≤1260px 多栏降级 | 1. 缩小窗口到 1260px<br>2. 检查 workflow-grid 为 3 列<br>3. 检查 split-grid 为 1 列 | 布局正常降级，无错位 | 🟡 需全部实现完成 |
| E2E-06 | 窗口 ≤780px 窄屏布局 | 1. 缩小窗口到 780px<br>2. 检查 workflow-grid 为 2 列<br>3. 检查 stepper 为纵向 | 窄屏布局正常 | 🟡 需全部实现完成 |

---

## 5. 测试数据设计

### 5.1 13 种法律状态测试案件（全部简体中文）

| 序号 | case_no | title_cn | status | client_name | filing_date | app_no | 说明 |
|---|---|---|---|---|---|---|---|
| 1 | P2024-0001 | 智能充电桩控制方法及装置 | WAITING_RECEIPT | 蔚来汽车科技有限公司 | 2024-01-18 | 202410012345.6 | 受理阶段 |
| 2 | P2024-0002 | 基于深度学习的自动驾驶路径规划系统 | PRELIM_EXAM | 百度在线网络技术有限公司 | 2024-02-20 | 202410023456.7 | 初审审查中 |
| 3 | P2024-0003 | 新型锂电池正极材料制备方法 | PRELIM_PASS | 宁德时代新能源科技股份有限公司 | 2024-03-15 | 202410034567.8 | 初审通过 |
| 4 | P2024-0004 | 柔性显示屏弯折结构改进 | AMENDMENT | 京东方科技集团股份有限公司 | 2024-04-10 | 202410045678.9 | 补正中 |
| 5 | P2024-0005 | 量子通信密钥分发协议优化方法 | PUBLISHED | 中国科学技术大学 | 2024-05-22 | 202410056789.0 | 已公布 |
| 6 | P2024-0006 | 高性能芯片散热结构及制造工艺 | SUB_EXAM | 华为技术有限公司 | 2024-06-08 | 202410067890.1 | 实审中 |
| 7 | P2024-0007 | 基于大语言模型的智能客服对话系统 | OA1 | 阿里巴巴（中国）有限公司 | 2024-07-12 | 202410078901.2 | 一通答复中 |
| 8 | P2024-0008 | 光伏组件封装工艺及设备 | OA2 | 隆基绿能科技股份有限公司 | 2024-08-05 | 202410089012.3 | 二通答复中 |
| 9 | P2024-0009 | 新型mRNA疫苗递送载体 | REEXAM | 复星医药集团股份有限公司 | 2024-09-18 | 202410090123.4 | 复审中 |
| 10 | P2024-0010 | 无人机集群编队飞行控制方法 | GRANTED | 大疆创新科技有限公司 | 2024-10-25 | 202410101234.5 | 已授权 |
| 11 | P2024-0011 | 基于区块链的供应链溯源系统 | REJECTED | 蚂蚁科技集团股份有限公司 | 2024-11-03 | 202410112345.6 | 已驳回 |
| 12 | P2024-0012 | 石墨烯基超级电容器制备方法 | TERMINATED | 比亚迪股份有限公司 | 2024-12-15 | 202410123456.7 | 已终止 |
| 13 | P2024-0013 | 基于5G的远程医疗手术导航系统 | INVALIDATED | 中兴通讯股份有限公司 | 2025-01-08 | 202510134567.8 | 已无效 |

### 5.2 边界情况测试数据

| 序号 | case_no | title_cn | status | client_name | 说明 |
|---|---|---|---|---|---|
| 14 | P2024-0014 | （无标题） | NOT_FILED | (无客户) | 旧状态 + 空字段 |
| 15 | P2024-0015 | 测试边界案件 | PENDING | 测试客户有限公司 | 旧状态兼容 |
| 16 | P2024-0016 | 已撤回的申请 | WITHDRAWN | 小米科技有限公司 | 旧状态兼容 |

### 5.3 发明人与申请人测试数据

案件 P2024-0006（华为技术有限公司）包含完整子表数据：

**申请人**:
| seq | is_first | name_cn | name_en |
|---|---|---|---|
| 1 | true | 华为技术有限公司 | Huawei Technologies Co., Ltd. |
| 2 | false | 海思半导体有限公司 | HiSilicon Technologies Co., Ltd. |

**发明人**:
| seq | name_cn | name_en |
|---|---|---|
| 1 | 张伟 | Zhang Wei |
| 2 | 李娜 | Li Na |
| 3 | 王强 | Wang Qiang |

**优先权**:
| seq | country_code | prio_no | prio_date |
|---|---|---|---|
| 1 | CN | 202310067890.1 | 2023-06-08 |

---

## 6. 测试文件清单

| 文件 | 类型 | 说明 |
|---|---|---|
| `backend/tests/test_v3_workflow.py` | 后端 pytest | CaseStatus 枚举验证 + API 字段验证 + 状态筛选测试 |
| `frontend/src/constants/__tests__/workflow.spec.ts` | 前端单元 | workflow.ts 映射逻辑测试（待 workflow.ts 实现后） |
| `frontend/src/modules/cases/components/__tests__/CaseStepper.spec.ts` | 前端组件 | Stepper 渲染与状态测试（待组件实现后） |
| `frontend/src/modules/dashboard/components/__tests__/WorkflowOverview.spec.ts` | 前端组件 | 阶段卡渲染与交互测试（待组件实现后） |

---

## 7. 测试执行策略

### 7.1 执行顺序

```
阶段 1（立即可执行）:
  ✅ BE-02, BE-03 — CaseStatus 枚举验证
  ✅ BE-04 ~ BE-13 — GET /cases/{id} 字段验证
  ✅ BE-14 ~ BE-17 — GET /cases 列表字段验证（已有字段）

阶段 2（需后端实现 V3-02, V3-03 后）:
  🟡 BE-01 — V3 状态创建案件
  🟡 BE-18, BE-19 — 列表 filing_date, recv_date 字段

阶段 3（需后端实现 V3-04 后）:
  🟡 BE-20 — 种子数据验证

阶段 4（需前端实现 V3-00 后）:
  🟡 FE-01 ~ FE-15 — workflow.ts 单元测试

阶段 5（需前端组件实现后）:
  🟡 FE-16 ~ FE-30 — 组件测试

阶段 6（需全部实现完成后）:
  🟡 E2E-01 ~ E2E-06 — 端到端测试
```

### 7.2 质量门禁

```bash
# 后端测试
cd backend && pytest tests/test_v3_workflow.py -v

# 前端测试（待实现）
cd frontend && npx vitest run src/constants/__tests__/workflow.spec.ts

# 后端 lint
cd backend && ruff check --fix . && ruff format .

# 前端 lint + typecheck + build
cd frontend && npm run lint && npm run typecheck && npm run build
```

---

## 8. 风险与说明

| 风险 | 影响 | 缓解 |
|---|---|---|
| 后端 GET /cases 列表尚未返回 filing_date, recv_date | BE-18, BE-19 会失败 | 标记为 xfail，待 V3-03 实现后移除 |
| 前端 workflow.ts 尚未实现 | 所有 FE 测试不可执行 | 在测试计划中先定义用例，代码实现后补充测试文件 |
| 测试使用 session-scoped fixtures | 不同测试间可能有数据残留 | 使用唯一 case_no 前缀 `V3-` 避免冲突 |
| PUT /cases/{id} 目前不支持更新 status | BE-01 无法直接测试状态更新 | 通过直接 ORM 操作设置 status 进行验证 |

---

*本文档由 Test Agent 自动生成。*
