# FRMS SPEC 2.0 2nd Review Post Ledger

## Purpose

本文件用于登记 `docs/FPMS_SPEC2_2nd_Review.md` 中已推进条目的 post-review 收口状态，以及已批准但暂不在本轮 Phase 3 范围内的 blocked follow-up。

---

## P0 #1 — 官费清单与缴费 (FR-FE-04)

- Source review item: `docs/FPMS_SPEC2_2nd_Review.md`
- Source spec: `docs/FPMS SPEC 2.0.md`
- Final QA ledger: `artifacts/FRFE04-QA-01/summary.md`
- Story status: `已完成（Phase 3 兼容闭环）`
- SPEC full-close status: `BLOCKED by approved follow-up ledger`

### 已完成闭环

- 从 `GOV` 草单生成官费清单
- 历史清单头创建
- 官费清单查询、详情、状态追踪
- Excel 导出与 `DRAFT -> EXPORTED -> PAID`
- 生成行官方缴费登记
- 历史手工补录明细，且允许 `fee_item_id` 为空
- Fee Management 语义入口与简体中文 UI

### 已登记 Blocked Follow-up

| Follow-up ID | Blocked Item | Reason |
|---|---|---|
| `FRFE04-BLOCK-01` | `T_PayList` 缺 `Type/FlowDir/InvoiceNoFrom/To` | 现有模型未提供结构字段；本轮受 Phase 3 无 schema 变更约束 |
| `FRFE04-BLOCK-02` | `T_GovPayment` 缺 `FeeCode/YearNo/PlannedAmt/PlannedCurrency/PaidCurrency/VoucherNo/InvoiceNo` | 现有模型未提供结构字段；本轮受 Phase 3 无 schema 变更约束 |
| `FRFE04-BLOCK-03` | 依赖上述缺失结构字段的增强查询 | 查询口径依赖未落库字段，不能在本轮伪完成 |
| `FRFE04-BLOCK-04` | `XML / 文本` 多格式官方导出 | 本轮仅交付统一 Excel 导出 |
| `FRFE04-BLOCK-05` | 已缴记录高权限修改与审计日志 | 需要独立权限/审计设计，不纳入本轮闭环 |

### Close Decision

- `FR-FE-04`：可在 post-review 台账中标记为 `已完成（Phase 3 兼容闭环）`
- 不应标记为 `SPEC 全量完成`
- 上述 5 项 blocked follow-up 必须保留在后续计划中

---

## Evidence

- `artifacts/FRFE04-QA-01/results.jsonl`
- `artifacts/FRFE04-QA-01/summary.md`
- `artifacts/FRFE04-QA-01/git/diff.patch`
