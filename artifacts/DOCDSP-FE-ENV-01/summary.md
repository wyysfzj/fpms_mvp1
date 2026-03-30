# Summary

## Commands
- `cd frontend && npm run lint -- src/api/documents.ts src/api/documents.types.ts src/modules/documents/pages/DocumentEnvelopePrint.vue src/router/index.ts`
- `cd frontend && npm run typecheck`
- `./scripts/task_validate.sh DOCDSP-FE-ENV-01`

## Results
- 新增单文档信封打印预览页与路由。
- 页面可展示收件人、地址、地址来源，并支持浏览器打印。
- lint、typecheck、task gate 全部通过。

## Notes
- 本任务只关闭信封打印预览与地址来源展示。
- 不记录打印日志，不回写 dispatch 数据。
