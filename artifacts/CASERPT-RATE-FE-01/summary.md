# CASERPT-RATE-FE-01 Summary

- 状态: PASS
- 闭环: 在现有 `CaseList.vue` 上展示授权率相关指标，并接通 `cases` API client/types 新 summary 字段。
- 新增展示:
  - 授权数量
  - 授权率
  - 终止数量
  - 无效数量
  - 审中数量
- 关键语义:
  - `grant_rate = null` 时显示 `暂无`
  - 所有新增文案均为简体中文
- 非闭环:
  - 不新建页面
  - 不做图表 / 导出
  - 不做 trend UI
