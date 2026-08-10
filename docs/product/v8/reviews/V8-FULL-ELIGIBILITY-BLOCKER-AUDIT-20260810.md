# V8 Full eligibility 与外部阻塞审计（2026-08-10）

## 结论

Foundation 已由 `V8-FOUNDATION-CLOSE-CURRENT-ADOPTION` terminally 关闭，197/197 行满足
C3.1 Foundation。进入 Full 后，frozen catalog 的 86 个 deferred row 中没有一个当前
dependency-ready 的合法产品 lane：83 行直接要求尚未确认的客户/source-backed decision
gate；余下 3 行是这些 gated rows 全部完成后的累计 regression、Final ledger 和 Final
close。不得把 `PENDING` 推断为同意、safe default、历史分类或自动激活。

## 冻结输入

- Catalog：`docs/product/v8/catalog.frozen.json`，283 个唯一 row，SHA-256
  `72c849825c9cbd39cb25f743d448b67a2a31bfccf7cfb68a3d2557c7bda178bf`。
- 当前 decision authority：`docs/product/v8/source-decision-registry.md`。
- Foundation close：commit `2b89dd30f2ba0266ced0e6943cd828362789cdfe`；lean Foundation
  checker terminal PASS。
- C3.1 规则：只有 source、scope/version/effective time 和 customer decision 都明确的
  lane 才可进入 Full；缺少决定时只阻塞对应 lane。

## 逐类覆盖

86 行的 `deferred_kind` 分布为：29 `gate_activation`、31 `gated_product`、22
`legacy_form`、4 `full_only`。

- 29 个 gate activation row（ordinals 170–198）各自带 exact `gate_requirements`：7 个
  GLOBAL business gate 与 `form-001`–`form-022` 的 22 个 legacy-form gate。
- 31 个 gated product row（ordinals 200–229）分别要求 grant evidence source/manual
  review、application/grant-year/future-annuity draft、payment workbook 或 service-rate gate。
- 22 个 form product row（ordinals 230–251）各自要求对应
  `DG-LEGACY-FORM-CLASS:form-NNN`。
- Full activation row 199 同时要求全部 7 个 GLOBAL gate、legacy `ALL-22` 和完整 applicable
  coverage。
- Official workbook real UI E2E row 278 要求 payment-workbook gate，因此也在上述 83 个
  direct customer-blocked rows 内。
- 只有 rows 281–283 没有直接 `gate_requirements`；它们依次是累计 inherited regression、
  Final item-to-slice ledger 和 Final close，依赖 Full activation 及全部 gated product/form
  rows，故为传递 dependency-blocked，而非可执行工作。

Catalog 审计得到：83 行至少一个 gate requirement，3 行没有 gate requirement但依赖
deferred predecessors；不存在第四种情况。

## 未决权威

source/decision registry 当前明确记录以下状态均为 `PENDING`：

- `DG-GRANT-EVIDENCE-SOURCE:GLOBAL`
- `DG-GRANT-MANUAL-REVIEW:GLOBAL`
- `DG-FEE-APPLICATION-DRAFT:GLOBAL`
- `DG-FEE-GRANT-YEAR-DRAFT:GLOBAL`
- `DG-FEE-FUTURE-ANNUITY:GLOBAL`
- `DG-PAYMENT-WORKBOOK:GLOBAL`
- `DG-SERVICE-RATE-VERSION:GLOBAL`
- `DG-LEGACY-FORM-CLASS:form-001`–`form-022`（以及 Full activation 所需的完整覆盖）

已批准的 grant-year official-fee manual review 只允许受权操作者确认通知书官费金额；registry
明确声明它不激活 `DG-FEE-GRANT-YEAR-DRAFT`。因此不能把该决定扩张为 Full gate 批准。

## Ledger disposition

本审计批准后，coverage ledger 应作一次机械分类：

- 所有带 `gate_requirements` 的 83 行：`CUSTOMER_BLOCKED`，blocker code
  `CUSTOMER_DECISION_REQUIRED`，引用本报告；gate identity 继续以 frozen catalog 为唯一
  精确映射。
- Rows 281–283：`PENDING`，blocker code `DEPENDENCY_BLOCKED`，根依赖为
  `FPMS-V8-FULL-MANIFEST-ACTIVATION-20260712-01`，引用本报告。
- 不创建 story、不运行产品 RED/GREEN、不修改 product/source/contract、不把 blocker
  计作 PASS。

该分类使当前状态可恢复、可审计，但 Full、Final 和 Release 均不得宣称完成。客户以后确认
某一 exact gate 时，只重开该 gate 的 activation/product closure；其他 blocker 不受影响。

## 非闭包与恢复条件

本审计不替客户选择、不激活 source/rate/form/workbook、不创建自动草单、不推进法律状态、
不运行 Final/release gate。恢复任一 lane 至少需要：exact gate code/scope、decision value、
source/version、actor、effective time 与 rollback impact 进入 registry，并经独立 PROTECTED
review；随后该 lane 才从 `CUSTOMER_BLOCKED` 转为可执行。
