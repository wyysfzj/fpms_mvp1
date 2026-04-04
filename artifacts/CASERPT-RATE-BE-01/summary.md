# CASERPT-RATE-BE-01 Summary

- 状态: PASS
- 闭环: 为 `GET /cases` summary 新增授权率相关指标：
  - `granted_count`
  - `grant_rate`
  - `terminated_count`
  - `invalidated_count`
  - `in_prosecution_count`
- 关键语义:
  - `granted_count` 采用 granted-lineage：`GRANTED / TERMINATED / INVALIDATED / EXPIRED`
  - `grant_rate` 分母采用 closed prosecution outcomes：granted-lineage + `REJECTED / WITHDRAWN / ABANDONED`
  - `in_prosecution_count` 统计当前未进入分母的在途状态
- 非闭环:
  - 不做 trend reporting
  - 不做前端展示
  - 不做 schema change
