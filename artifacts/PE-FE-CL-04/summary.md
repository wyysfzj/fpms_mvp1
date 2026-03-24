# PE-FE-CL-04 证据摘要（复核修订）

- 任务文件: `tasks/postenhancement/frontend/PE-FE-CL-04.md`
- 实施范围: `frontend/src/modules/billing/pages/BillDetail.vue`
- 本次修订目标: 修复坏账标记/恢复动作的确定性错误提示映射（status+code -> 中文文案）。

## 本次代码变更

1. 新增坏账错误处理助手：
   - `isApiError(error)`
   - `normalizeBadDebtApiError(error)`
   - `mapBadDebtErrorMessage(apiError)`
2. 按冻结契约实现确定性映射：
   - `400 + BAD_DEBT_NOT_ALLOWED` -> `当前账单不满足坏账操作条件`
   - `401` -> `登录已失效，请重新登录`
   - `403` -> `无权限执行坏账操作`
   - `404 + BILL_NOT_FOUND` -> `未找到目标账单`
   - `409 + BAD_DEBT_ALREADY_MARKED / BAD_DEBT_RESTORE_INVALID` -> `账单状态冲突，请刷新后重试`
   - `422` -> `参数校验失败，请检查后重试`
   - unknown/network -> `坏账操作失败，请稍后重试`
3. 在 `handleMarkBadDebt` 与 `handleRestoreBadDebt` 的 `catch` 中：
   - 保留 `error.value`（错误横幅状态）
   - 新增 `ElMessage.error(...)` 确定性中文提示

## Gate 结果

- `cd frontend && npm run lint` -> 通过（rc=0）
- `cd frontend && npm run typecheck` -> 通过（rc=0）
- `./scripts/task_validate.sh PE-FE-CL-04` -> 通过（rc=0）
