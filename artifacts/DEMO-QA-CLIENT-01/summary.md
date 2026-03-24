# DEMO-QA-CLIENT-01 证据摘要

## 任务范围

本任务仅做 QA 验证与证据归档，不修改产品代码。验证对象是客户列表“查看 / 编辑”链路，以及客户详情接口的状态码语义。

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

- `/clients/:id` 路由注册后的前端编译正常
- 客户列表“查看 / 编辑”分流没有引入类型或构建回归
- 客户主档表单/详情页契约收口后的页面仍可通过构建

### 2. 后端 smoke

通过 `test` 证据步骤使用 `TestClient` 验证：

- 登录 `admin / admin123`
- 列出客户
- 对现有客户执行 `GET /api/v1/clients/{id}`
- 对不存在客户执行 `GET /api/v1/clients/{id}`

结果：

- `POST /api/v1/auth/login` -> `200`
- `GET /api/v1/clients?page=1&page_size=1` -> `200`
- `GET /api/v1/clients/e58e49d9-422e-42f7-b449-a9884e50ad93` -> `200`
- `GET /api/v1/clients/<missing-uuid>` -> `404`

结论：

- 客户详情读取路径已不再返回 `405 Method Not Allowed`
- 缺失客户时返回受控 `404`

## 关键结论

- 这条 demo 缺陷已从“点击查看/编辑即 405”收口为正常链路
- 当前预期语义为：
  - 存在客户详情：`200`
  - 不存在客户详情：`404`
- 客户列表前端已具备：
  - “查看”进入详情页
  - “编辑”进入编辑页

## 证据文件

- `artifacts/DEMO-QA-CLIENT-01/results.jsonl`
- `artifacts/DEMO-QA-CLIENT-01/commands.jsonl`
- `artifacts/DEMO-QA-CLIENT-01/git/diff.patch`
- `artifacts/DEMO-QA-CLIENT-01/outputs/*`
