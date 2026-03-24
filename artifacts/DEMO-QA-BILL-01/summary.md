# DEMO-QA-BILL-01 证据摘要

## 任务范围

本任务仅做 QA 验证与证据归档，不修改产品代码。验证对象是 bill-from-draft demo 链路中的三类问题：

- 账单创建页不应再要求演示员手工输入 UUID
- 费用草稿列表不应再以 UUID 作为主展示
- 账单详情关系链应显示可读的费用草稿关联

## 已执行检查

### 1. 门禁检查

通过 `lint` 证据步骤执行：

```bash
cd backend && ruff check app/modules/billing/api.py app/modules/billing/schemas.py
cd frontend && npm run lint && npm run typecheck && npm run build
```

结果：

- backend `ruff check` 通过
- `npm run lint` 通过
- `npm run typecheck` 通过
- `npm run build` 通过

说明：

- billing detail enriched contract 的前后端对接没有引入静态检查回归
- bill create / fee draft list / bill detail 三个页面在当前集成状态下可正常构建

### 2. bill-from-draft smoke

通过 `test` 证据步骤使用 `TestClient` 验证：

- 登录 `admin / admin123`
- 新建客户：`苏州星桥知识产权代理有限公司`
- 新建案件：`ZY-BILL-D4E1324F`
- 新建费率：`授权登记费`
- 新建费用草稿并添加一条费用明细
- 锁定费用草稿
- 从该草稿生成账单
- 拉取账单详情并校验 enriched 字段
- 对不存在账单执行 `GET /api/v1/bills/{id}`
- 对前端源码做页面级断言

结果：

- `POST /api/v1/auth/login` -> `200`
- `POST /api/v1/clients` -> `201`
- `POST /api/v1/cases` -> `201`
- `POST /api/v1/fees/rates` -> `201`
- `POST /api/v1/fees/drafts` -> `201`
- `POST /api/v1/fees/drafts/{draft_id}/items` -> `201`
- `POST /api/v1/fees/drafts/{draft_id}/lock` -> `200`
- `POST /api/v1/bills/from-drafts` -> `201`
- `GET /api/v1/bills/{bill_id}` -> `200`
- `GET /api/v1/bills/{missing_id}` -> `404`

关键返回值验证：

- `client_name = 苏州星桥知识产权代理有限公司`
- `case_no = ZY-BILL-D4E1324F`
- `primary_draft_id = <draft_id>`
- `primary_draft_label = GRANT_FEE-9874B2B6`
- `source_draft_ids = [<draft_id>]`
- `items[0].draft_id = <draft_id>`
- `items[0].description = 授权登记费`

### 3. 页面源码断言

已验证以下页面包含本轮 demo 关键改动：

- [BillCreate.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/billing/pages/BillCreate.vue)
  - 包含“请选择已锁定且可开票的费用草稿”
  - 使用 `availableDraftOptions`
- [FeeDraftList.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/fees/pages/FeeDraftList.vue)
  - 使用 `getDraftDisplayId`
- [BillDetail.vue](/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend/src/modules/billing/pages/BillDetail.vue)
  - 向 `RelationChainCard` 传递 `fee-draft`
  - 消费 `primary_draft_label`

## 关键结论

- 有效的“锁定草稿 + 明细存在”链路下，`POST /api/v1/bills/from-drafts` 可正常返回 `201`
- 账单详情接口已经具备可读的客户、案件、费用草稿展示字段
- 费用草稿列表和账单详情页都已从“UUID 主展示”收口为“业务标识主展示”
- 这条 demo 路径已不再要求演示员手工输入 UUID 才能继续

## 残余观察

- 本次 smoke 使用的是“已有费用明细”的锁定草稿成功路径
- “无明细草稿”的业务错误语义仍在后端保留；当前 demo 路径已通过前端筛选减少触发概率

## 证据文件

- `artifacts/DEMO-QA-BILL-01/results.jsonl`
- `artifacts/DEMO-QA-BILL-01/commands.jsonl`
- `artifacts/DEMO-QA-BILL-01/git/diff.patch`
- `artifacts/DEMO-QA-BILL-01/outputs/*`
