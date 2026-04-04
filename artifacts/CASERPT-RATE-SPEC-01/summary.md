# CASERPT-RATE-SPEC-01 Summary

- 状态: PASS
- 闭环: 冻结 `RPT-CASE` 的授权率口径，明确 `granted-lineage` 分子、closed prosecution outcome 分母，以及在途状态排除集合。
- 关键语义:
  - 分子计入 `GRANTED / TERMINATED / INVALIDATED / EXPIRED`
  - 分母计入授权成功与已关闭非授权结局：`GRANTED / TERMINATED / INVALIDATED / EXPIRED / REJECTED / WITHDRAWN / ABANDONED`
  - 在途状态不计入分母
- 结论:
  - `grant-rate` 在当前 `Case.status` carrier 下可直接进入实现
  - `trend reporting` 仍保持 prerequisite-blocked
- 非闭环:
  - 不做任何案件统计产品实现
  - 不做趋势统计
  - 不更新 `RPT-CASE` 或 `#13` close decision
