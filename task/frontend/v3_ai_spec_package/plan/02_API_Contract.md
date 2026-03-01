# V3 Case Workflow Stepper — API Contract

> **版本**: 1.0
> **日期**: 2026-02-22
> **作者**: Backend Agent + Frontend Agent
> **状态**: 已实现

---

## 1. GET /api/v1/cases/{case_id} — 案件详情

### 请求

```
GET /api/v1/cases/{case_id}
Authorization: Bearer <token>
```

**权限**: `Case.Read`

### 响应 200

```json
{
  "id": "uuid-string",
  "case_no": "P2310-001",
  "case_type": "NORMAL",
  "patent_category": "INV",
  "flow_dir": "CN_DOMESTIC",
  "client_id": "uuid-string | null",
  "client_name": "蔚来汽车 | null",
  "title_cn": "智能充电桩控制方法 | null",
  "title_en": "Smart Charging Pile Control Method | null",
  "app_no": "202410012345.6 | null",
  "status": "WAITING_RECEIPT",
  "filing_date": "2024-01-18 | null",
  "recv_date": "2024-01-15 | null",
  "applicants": [
    {
      "seq": 1,
      "is_first": true,
      "name_cn": "蔚来汽车科技有限公司",
      "name_en": null,
      "address_cn": "上海市...",
      "address_en": null
    }
  ],
  "inventors": [
    {
      "seq": 1,
      "name_cn": "张三",
      "name_en": null
    }
  ],
  "priorities": [
    {
      "seq": 1,
      "country_code": "CN",
      "prio_no": "202310012345.6",
      "prio_date": "2023-10-15"
    }
  ],
  "created_at": "2024-01-15T10:00:00",
  "updated_at": "2024-01-15T10:00:00"
}
```

### 字段说明

| 字段 | 类型 | 是否新增 | 说明 |
|---|---|---|---|
| `id` | `string` | 否 | 案件 UUID |
| `case_no` | `string` | 否 | 案号 |
| `case_type` | `string` | 否 | 案件类型: NORMAL / PCT_INTL / PCT_NATL / PRIORITY |
| `patent_category` | `string` | 否 | 专利类别: INV / UM / DES |
| `flow_dir` | `string` | 否 | 流程方向: CN_DOMESTIC / CN_OUTBOUND / FOREIGN_INBOUND |
| `client_id` | `string \| null` | 否 | 客户 UUID |
| `client_name` | `string \| null` | **是** | 客户中文名称（通过 client_id 关联查询） |
| `title_cn` | `string \| null` | **是** | 案件中文标题 |
| `title_en` | `string \| null` | **是** | 案件英文标题 |
| `app_no` | `string \| null` | **是** | 申请号 |
| `status` | `string` | **是** | 法律状态（见 §3 CaseStatus 枚举） |
| `filing_date` | `string (YYYY-MM-DD) \| null` | **是** | 申请日 |
| `recv_date` | `string (YYYY-MM-DD) \| null` | **是** | 收案日 |
| `applicants` | `array` | **是** | 申请人列表（可能为空 `[]`） |
| `inventors` | `array` | **是** | 发明人列表（可能为空 `[]`） |
| `priorities` | `array` | **是** | 优先权列表（可能为空 `[]`） |
| `created_at` | `string (ISO datetime) \| null` | **是** | 创建时间 |
| `updated_at` | `string (ISO datetime) \| null` | **是** | 更新时间 |

### 错误响应

- `401`: AUTH_REQUIRED
- `403`: FORBIDDEN
- `404`: Case not found

---

## 2. GET /api/v1/cases — 案件列表

### 请求

```
GET /api/v1/cases?page=1&page_size=20&status=WAITING_RECEIPT&q=充电桩
Authorization: Bearer <token>
```

**权限**: `Case.Read`

**查询参数**:

| 参数 | 类型 | 说明 |
|---|---|---|
| `q` | `string` | 模糊搜索（案号、标题、申请号） |
| `case_no` | `string` | 精确匹配案号 |
| `app_no` | `string` | 精确匹配申请号 |
| `client_id` | `string` | 筛选客户 |
| `status` | `string` | 筛选法律状态 |
| `date_from` | `date` | 收案日起始 |
| `date_to` | `date` | 收案日截止 |
| `sort_by` | `string` | 排序字段: case_no / recv_date / filing_date / created_at |
| `sort_dir` | `string` | 排序方向: asc / desc |
| `page` | `int` | 页码（默认 1） |
| `page_size` | `int` | 每页数量（默认 20） |

### 响应 200

```json
{
  "items": [
    {
      "id": "uuid-string",
      "case_no": "P2310-001",
      "case_type": "NORMAL",
      "patent_category": "INV",
      "client_id": "uuid-string | null",
      "client_name": "蔚来汽车 | null",
      "title_cn": "智能充电桩控制方法 | null",
      "title_en": "Smart Charging Pile Control Method | null",
      "status": "WAITING_RECEIPT",
      "filing_date": "2024-01-18 | null",
      "recv_date": "2024-01-15 | null"
    }
  ],
  "page": 1,
  "page_size": 20,
  "total": 12
}
```

### 列表字段说明

| 字段 | 类型 | 是否新增 | 说明 |
|---|---|---|---|
| `id` | `string` | 否 | 案件 UUID |
| `case_no` | `string` | 否 | 案号 |
| `case_type` | `string` | 否 | 案件类型 |
| `patent_category` | `string` | 否 | 专利类别 |
| `client_id` | `string \| null` | 否 | 客户 UUID |
| `client_name` | `string \| null` | 否 | 客户中文名称 |
| `title_cn` | `string \| null` | 否 | 案件中文标题 |
| `title_en` | `string \| null` | **是** | 案件英文标题 |
| `status` | `string` | 否 | 法律状态 |
| `filing_date` | `string (YYYY-MM-DD) \| null` | **是** | 申请日 |
| `recv_date` | `string (YYYY-MM-DD) \| null` | **是** | 收案日 |

---

## 3. CaseStatus 枚举

### 现有值（保留，向后兼容）

| 值 | 说明 |
|---|---|
| `NOT_FILED` | 未递交 |
| `PENDING` | 审查中 |
| `GRANTED` | 已授权 |
| `REJECTED` | 已驳回 |
| `WITHDRAWN` | 已撤回 |
| `ABANDONED` | 已放弃 |
| `EXPIRED` | 已过期 |

### V3 新增值

| 值 | 说明 | Workflow Step |
|---|---|---|
| `WAITING_RECEIPT` | 等待受理 | 受理 (ACCEPTED) |
| `PRELIM_EXAM` | 初步审查 | 初审 (PRELIM) |
| `PRELIM_PASS` | 初审通过 | 初审 (PRELIM) |
| `AMENDMENT` | 补正 | 初审 (PRELIM) |
| `PUBLISHED` | 公布 | 公布 (PUBLISHED) |
| `SUB_EXAM` | 实质审查 | 实审 (SUB_EXAM) |
| `OA1` | 第一次审查意见 | 实审 (SUB_EXAM) |
| `OA2` | 第二次审查意见 | 实审 (SUB_EXAM) |
| `REEXAM` | 复审 | 实审 (SUB_EXAM) |
| `TERMINATED` | 终止 | 授权 (GRANTED) — 分支 |
| `INVALIDATED` | 无效 | 授权 (GRANTED) — 分支 |

> 注: `GRANTED` 和 `REJECTED` 已存在于旧枚举中，无需重复添加。

---

## 4. 兼容性声明

- **所有变更均为增量**：现有字段含义不变，仅新增字段
- **默认值兼容**：新建案件默认 status = `NOT_FILED`
- **null 安全**：新增的 nullable 字段在未设置时返回 `null`
- **分页结构不变**：`{ items, page, page_size, total }` 格式保持一致

---

## 5. 前端对接建议

### 5.1 类型定义更新

前端 `cases.types.ts` 需新增以下字段：

```typescript
// 详情
interface CaseDetail {
  // ...existing fields...
  client_name: string | null
  title_cn: string | null
  title_en: string | null
  app_no: string | null
  status: string
  filing_date: string | null
  recv_date: string | null
  applicants: CaseApplicant[]
  inventors: CaseInventor[]
  priorities: CasePriority[]
  created_at: string | null
  updated_at: string | null
}

// 列表项
interface CaseListItem {
  // ...existing fields...
  title_en: string | null   // 新增
  filing_date: string | null // 新增
  recv_date: string | null   // 新增
}
```

### 5.2 Workflow Step 映射

前端应在 `constants/workflow.ts` 中实现 `status → workflow step` 的映射，用于：
- Dashboard WorkflowOverview 卡片统计
- CaseList "当前步骤" 列
- CaseDetail Stepper 可视化

---

## 6. 种子数据

`seed_dev.py` 已更新，包含覆盖所有 13 种 V3 法律状态的测试案件 (V3-001 ~ V3-013)，每种状态至少 1 条数据。

| 案号 | 状态 | 标题 | 客户 |
|---|---|---|---|
| V3-001 | WAITING_RECEIPT | 智能充电桩控制方法及系统 | 蔚来汽车 |
| V3-002 | PRELIM_EXAM | 电池热管理温控装置 | 蔚来汽车 |
| V3-003 | PRELIM_PASS | 自动驾驶路径规划算法 | 比亚迪 |
| V3-004 | AMENDMENT | 车载激光雷达信号处理方法 | 比亚迪 |
| V3-005 | PUBLISHED | 5G基站天线阵列优化设计 | 华为 |
| V3-006 | SUB_EXAM | 分布式数据库一致性协议 | 华为 |
| V3-007 | OA1 | 手机摄像模组光学防抖方法 | 小米 |
| V3-008 | OA2 | 智能家居语音控制交互系统 | 小米 |
| V3-009 | REEXAM | 芯片制造工艺缺陷检测方法 | 华为 |
| V3-010 | GRANTED | 新能源汽车能量回收控制策略 | 比亚迪 |
| V3-011 | REJECTED | 无线充电效率提升装置 | 小米 |
| V3-012 | TERMINATED | 固态电池电解质制备方法 | 蔚来汽车 |
| V3-013 | INVALIDATED | 物联网设备安全认证协议 | 华为 |
