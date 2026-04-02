# P2 #20 账单打印前端按钮设计说明

## Story Shape Classification

- `shared_file_density`: `low`
- `prereq_dependency_density`: `low`
- `be_fe_coupling`: `frontend-only on existing backend contract`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-single-lane-story`

## Problem Statement

当前 repo 已具备账单打印 backend contract 与账单详情页打印按钮，但 `P2 #20` 仍存在“账单打印前端按钮”缺口。结合 review 文本 `Billing Backend renderer exists, need frontend button` 与现有代码状态，这一条的第一轮职责不是重做 billing print 链路，而是在现有 bill print contract 基础上补齐缺失的 frontend print entry，使用户可从账单列表直接触发打印。

## Assumptions

- backend renderer / endpoint 已存在并可复用：
  - `GET /api/v1/bills/{bill_id}/print`
  - 权限：`Bill.Print`
- frontend 已存在 shared API：
  - `frontend/src/api/billing.ts::printBill`
- 当前 repo 已存在详情页打印按钮：
  - `frontend/src/modules/billing/pages/BillDetail.vue`
- 第一轮按钮落点固定为：
  - `BillList`
- 第一轮点击行为固定为：
  - 沿用现有详情页语义
  - 直接下载/打开 backend 返回的 DOCX
  - 不新建专门预览页
- 第一轮可见条件固定为：
  - 在账单列表行内显示打印按钮
  - 以现有页面可见账单为前提
  - 不额外引入复杂禁用态矩阵
- 第一轮失败反馈固定为：
  - 简体中文 toast / message
- 第一轮 deferred slices 固定为：
  - `批量打印`
  - `打印预览页`
  - `导出 PDF`
  - `邮件发送`
  - `打印历史`
  - `打印模板改造`

## Scope

- `BillList.vue` 增加打印入口
- 复用现有 `printBill` FE API
- 保持列表页打印交互与详情页语义一致
- QA / evidence / close audit

## Explicit Non-scope

- backend renderer 改造
- print template 改造
- 批量打印
- 打印预览页
- PDF 导出
- 邮件发送
- 打印历史
- 新权限命名空间

## Existing Backend Renderer / Endpoint Inventory

- `backend/app/modules/billing/api.py::print_bill`
  - 路由：`GET /api/v1/bills/{bill_id}/print`
  - 权限：`Bill.Print`
  - 返回：DOCX 二进制下载响应
  - 已处理：
    - `404` 账单/客户不存在
    - `409` 模板未配置
    - `500` 模板文件缺失
- `frontend/src/api/billing.ts::printBill`
  - 已能获取打印 `Blob`
- `frontend/src/modules/billing/pages/BillDetail.vue`
  - 已有打印按钮
  - 已有下载逻辑与错误提示

## Button Placement Definition

- 第一轮只在：
  - `frontend/src/modules/billing/pages/BillList.vue`
  中增加列表行内打印按钮
- 不修改：
  - `BillDetail` 的既有打印位置与主交互语义

## Click Behavior Definition

- 点击列表行内打印按钮后：
  - 调用现有 `printBill(bill.id)`
  - 下载/打开 backend 返回的 DOCX 文件
- 成功后显示简体中文成功提示
- 当前不做：
  - 新标签页预览页
  - 专门 print route
  - 浏览器内嵌预览

## Visibility / Permission Definition

- 第一轮默认在账单列表每行显示打印按钮
- 页面本身以当前可见账单为前提
- 具体权限仍由 backend `Bill.Print` 执行强校验
- 前端当前不新增独立 permission gate / disabled matrix

## Error-handling Definition

- 调用失败时显示简体中文 toast / message
- 优先复用详情页中已有的打印失败提示文案逻辑
- 对 `409` 模板未配置保留专门提示
- 当前不做页面内错误槽位或新窗口回传

## Deferred Slices Ledger

- `批量打印`
- `打印预览页`
- `导出 PDF`
- `邮件发送`
- `打印历史`
- `打印模板改造`

## Model-layer Impact

- 无 schema 变更
- 无 migration
- 无 ORM model 修改

## API / Service Impact

- backend 无改动
- shared FE API 高概率无改动，直接复用现有 `printBill`

## UI / Permission Impact

- `BillList.vue` 新增打印入口
- 所有新增用户可见文案必须为简体中文
- backend `Bill.Print` 作为最终权限边界

## Cross-module Impact

- 主要影响：
  - `billing`
- 不进入：
  - `documents`
  - print template system
  - mail / export systems

## SQLite / Phase Compatibility Assessment

- SQLite 无特殊新增要求
- 不涉及 schema / migration
- 可作为标准 frontend-first story 执行

## Risks / Blockers / Prerequisite Tasks

- 最大风险是误把现有详情页打印按钮忽略掉，重复实现第二套下载逻辑
- 第二个风险是把列表入口顺手扩成批量打印或预览页
- 第三个风险是前后端交互语义不一致；第一轮必须沿用详情页现有下载行为
- 当前无单独 prerequisite task 要求

## Exact Closure Slice Candidates

建议冻结为：

`在现有 Bill.Print backend contract、现有 printBill FE API 与现有 BillDetail 打印语义基础上，为 BillList 增加第一轮账单打印入口，使用户可直接从账单列表行内触发打印下载。`

## Final Design Judgment

- `可在当前约束下拆成可执行原子任务`
