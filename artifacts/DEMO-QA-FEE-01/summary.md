# DEMO-QA-FEE-01 证据摘要

## 任务范围

本任务仅做 QA 验证与证据归档，不修改产品代码。验证对象是费用草稿详情页中的两条 demo 缺陷：

- 费用明细列表请求 `GET /api/v1/fees/drafts/{draft_id}/items` 不应再返回 `405`
- 关系链与概览应优先显示可读业务标识，而不是 UUID

## 已执行检查

### 1. 前端门禁

通过 `lint` 证据步骤执行：

```bash
cd frontend && npm run lint && npm run typecheck && npm run build
```

结果：

- `npm run lint` 通过
- `npm run typecheck` 通过
- `npm run build` 通过

说明：

- fee draft 详情页的可读标签逻辑没有引入编译或类型回归
- fee API types 与 enriched contract 对齐后，前端构建仍然稳定

### 2. 后端 smoke + 前端源码断言

通过 `test` 证据步骤使用 `TestClient` 验证：

- 登录 `admin / admin123`
- 新建客户：`上海启衡知识产权服务有限公司`
- 新建案件：`ZY-FEE-2840B457`
- 新建费用草稿：`GRANT_FEE`
- 验证费用草稿列表、详情、明细、缺失草稿状态码
- 断言前端 fee 详情页已优先使用可读标签变量和 enriched fee types

结果：

- `POST /api/v1/auth/login` -> `200`
- `POST /api/v1/clients` -> `201`
- `POST /api/v1/cases` -> `201`
- `POST /api/v1/fees/drafts` -> `201`
- `GET /api/v1/fees/drafts?page=1&page_size=20&case_id=<case_id>` -> `200`
- `GET /api/v1/fees/drafts/<draft_id>` -> `200`
- `GET /api/v1/fees/drafts/<draft_id>/items` -> `200`
- `GET /api/v1/fees/drafts/<missing_id>/items` -> `404`

源码断言：

- [FeeDraftDetail.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/fees/pages/FeeDraftDetail.vue) 包含 `clientDisplayName`、`caseDisplayNo`、`displayDraftId`
- [fees.types.ts](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/api/fees.types.ts) 已声明 `client_name`、`case_no`

## 关键结论

- 费用明细读接口已收口为受控语义：
  - 现有草稿：`200`
  - 缺失草稿：`404`
  - 不再出现 `405 Method Not Allowed`
- 费用草稿详情链路已具备展示友好的业务标识：
  - 案件显示 `case_no`
  - 客户显示 `client_name`
  - 草稿页使用可读的展示编号逻辑

## 残余观察

- `POST /api/v1/fees/drafts` 的创建响应当前仍可能返回 `case_no=null`、`client_name=null`
- 这不影响本次已定义的读链路验收，因为列表与详情接口已经返回可读字段
- 如果后续希望“创建完成后第一屏也立即显示完整业务标签”，可以单独立项补齐创建响应 contract

## 证据文件

- `artifacts/DEMO-QA-FEE-01/results.jsonl`
- `artifacts/DEMO-QA-FEE-01/commands.jsonl`
- `artifacts/DEMO-QA-FEE-01/git/diff.patch`
- `artifacts/DEMO-QA-FEE-01/outputs/*`
