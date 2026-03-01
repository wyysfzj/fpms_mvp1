# FPMS MVP1 — Backlog (Tech Debt)

## From Batch FB2

### R1 — 后端缺少 GET /clients/{id} 端点
- **严重度**: HIGH
- **来源**: FB2 Review
- **描述**: 后端 `api.py` 没有 `GET /clients/{client_id}` 单客户查询端点。Service 层 `get_client()` 已存在（`service.py:56`），但未接入 API 路由。前端 `getClient()` 调用会 404。
- **影响**: `ClientDetail.vue` 和 `ClientForm.vue`（编辑模式）均无法加载客户数据。
- **修复**: 在 `backend/app/modules/masterdata/clients/api.py` 添加 `@router.get("/clients/{client_id}")` 端点，调用已有的 `get_client` service。

### R2 — ClientList.vue handleView 路由指向 edit 而非 detail
- **严重度**: MED
- **来源**: FB2 Review
- **描述**: `ClientList.vue` 中 `handleView(row)` 路由到 `/clients/${row.id}/edit`，FB2 已新增 `/clients/:id` 详情页，"查看"操作应指向详情页。
- **影响**: 用户点击"查看"进入编辑页面而非只读详情页。
- **修复**: 将 `handleView` 中的路由改为 `/clients/${row.id}`。
