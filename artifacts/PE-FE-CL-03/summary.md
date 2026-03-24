# PE-FE-CL-03 证据摘要

- 任务文件：`tasks/postenhancement/frontend/PE-FE-CL-03.md`
- 执行范围：仅实现催款列表页与详情页（allowlist 内）

## 变更文件
- `frontend/src/modules/collections/pages/DunningList.vue`（new）
- `frontend/src/modules/collections/pages/DunningDetail.vue`（new）

## 验收对应
- 已支持轮次筛选（`round_no`）
- 已支持状态筛选（`status`）
- 已支持行明细查看（列表行进入详情页，详情页展示批次字段明细）

## 验证结果
- `cd frontend && npm run lint` -> 通过
- `cd frontend && npm run typecheck` -> 通过
