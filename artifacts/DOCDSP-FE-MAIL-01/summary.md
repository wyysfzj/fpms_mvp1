# DOCDSP-FE-MAIL-01

## Task
- 邮寄信息登记页面能力

## Exact closure slice
- dispatch 流程页筛选与列表
- 文档勾选
- `OutgoingRegNo / ForwardDate` 批量登记

## Explicit non-closure
- 不做交接单详情
- 不做信封打印预览
- 不改 `DocumentList.vue`

## Verification
- `cd frontend && npm run lint -- src/api/documents.ts src/api/documents.types.ts src/modules/documents/pages/DocumentDispatch.vue src/router/index.ts`
- `cd frontend && npm run typecheck`

## Notes
- 新增了独立路由 `DocumentDispatch.vue`，入口为 `/documents/dispatch`。
- 邮寄批量动作已通过 `batchRegisterDocumentMailing` 直接对接后端 `/documents/dispatch/mailing/batch-register`。
- 本任务未触碰 `DocumentList.vue`、后端文件或后续交接单/信封页面。
