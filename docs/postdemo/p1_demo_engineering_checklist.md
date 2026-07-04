# P1 Demo 工程检查清单

本文档用于工程侧准备、验证和复盘 P1 demo。它沉淀自 2026-07-04 的修复闭环：先可见复跑，发现问题后拆 atomic task 修复，再复跑，再修复 seed cleanup。

## 1. 必跑命令

从仓库根目录开始：

```bash
cd FPMS_Automation_Skeleton_Pack/playwright_ts
npm run demo:p1:seed
NO_PROXY=127.0.0.1,localhost no_proxy=127.0.0.1,localhost \
FPMS_API_URL=http://127.0.0.1:8000/api/v1 \
FPMS_BASE_URL=http://127.0.0.1:5173 \
npm run test:pd-p1
```

配套检查：

```bash
cd frontend && npm run typecheck
cd frontend && npm run lint
cd FPMS_Automation_Skeleton_Pack/playwright_ts && npx tsc --noEmit
cd backend && .venv/bin/python -m pytest tests/test_grant_fee_notice_task_creation.py -q
```

本地代理会影响 localhost API 时，必须显式设置 `NO_PROXY=127.0.0.1,localhost`。

## 2. Seed / Cleanup 合同

`demo:p1:seed` 必须满足：

- 可重复运行。
- 只清理明确属于 P1 demo fixture 的数据。
- 不做通配符删除。
- 能清理完整 demo 动态生成的数据，包括年费任务、年费草单、GovPayment 和 pay-list。
- 清理顺序遵守外键依赖：OfficialFeeChecklist -> GovPayment -> PayList -> FeeItem -> FeeDraft -> AnnuityTask -> Case。

验证失败特征：

- `sqlite3.IntegrityError: FOREIGN KEY constraint failed`
- 删除 `CASE-PD-P1-LIVE` 时失败
- 前一轮 demo 生成的动态 pay-list 或 GovPayment 残留

对应 evidence：`artifacts/PD-P1-DEMO-SEED-ANNUITY-CLEANUP-20260704-01/summary.md`。

## 3. 可见 UI E2E 标准

工程验证不能只跑自动化测试。客户 demo 前至少走一遍可见路径：

1. 打开案件编辑页，确认字段和中文状态。
2. 搜索申请人主数据，确认总委托书备案编号。
3. 新申请递交准备，确认 checklist 和导入记录为中文。
4. OA 答复，确认文件角色和人工动作。
5. 回执归档，确认缺回执不能关闭，补齐后归档检查通过。
6. 费用草单和官费清单，确认费减和模板边界。
7. 信函交接，确认抬头和状态为中文。
8. 授权通知，确认文件驱动案件进入已授权。
9. 授权费任务，确认授权后收费节点出现。
10. 年费任务，确认 typed case no 可解析真实案卷。
11. 年费草单和年费官费清单，确认年费节点闭环。

每一步都记录“期待结果”和“实际结果”。截图至少保留最终关键页，例如年费官费清单。

## 4. 中文 UI 和状态检查

用户可见 UI 不允许出现内部英文状态。至少检查：

- `READY`
- `DRAFT`
- `OPEN`
- `PENDING`
- `MANUAL_ONLY`
- `UNCONFIRMED`
- `CNIPA_IMPORT_STARTED`
- `occurred_at=`
- `note=`

业务状态应显示为：

- 已准备
- 草稿
- 待处理
- 待通知
- 人工官方缴费
- 待确认
- 接收类表格导入
- 操作时间 / 说明

如果某个页面必须保留英文技术值，应明确说明它是文件名、ID、协议名或 API 字段，不是客户业务状态。

## 5. Atomic 修复闭环

demo 中发现问题后，不允许直接塞进 rerun 任务。标准流程：

1. 建立新的 atomic task。
2. 写清 closure / non-closure / allowlist / verification。
3. 先复现失败或记录可观察失败。
4. 做最小修复。
5. 跑 targeted verification。
6. 生成 evidence：`results.jsonl`、`summary.md`、`git/diff.patch`、dirty baseline。
7. 跑 `./scripts/task_validate.sh <TASK-ID>`。
8. 回到完整 demo rerun。

本轮已验证的 atomic 修复：

| Task | 修复点 | Evidence |
| --- | --- | --- |
| `PD-P1-ANNUITY-DEMO-UI-CLOSE-20260704-01` | 年费弹窗 typed case no 解析真实案卷 id；首年年费字段改成第几年 | `artifacts/PD-P1-ANNUITY-DEMO-UI-CLOSE-20260704-01/summary.md` |
| `PD-P1-DEMO-SEED-ANNUITY-CLEANUP-20260704-01` | demo seed 清理动态年费 pay-list/GovPayment | `artifacts/PD-P1-DEMO-SEED-ANNUITY-CLEANUP-20260704-01/summary.md` |
| `PD-P1-LIFECYCLE-DEMO-RERUN-20260704-01` | 完整可见 UI demo 复跑和截图证据 | `artifacts/PD-P1-LIFECYCLE-DEMO-RERUN-20260704-01/summary.md` |

## 6. Demo 通过标准

只有同时满足以下条件，才能说 P1 demo PASS：

- `demo:p1:seed` 可重复运行。
- 可见 UI 路径走完，不靠第一页排序或口头绕过。
- 自动化 P1 live E2E 通过。
- 前端 typecheck/lint 通过。
- 后端相关 targeted test 通过。
- Playwright harness typecheck 通过。
- 所有新修复 task gate 通过。
- evidence 路径完整。
- 残余风险已关闭或明确标记为非 P1 / 工具限制。

## 7. 常见失败模式

| 失败表现 | 优先检查 |
| --- | --- |
| demo 数据和脚本不一致 | 是否重新执行 `demo:p1:seed` |
| 申请人主数据找不到 | 是否用搜索条件定位目标申请人 |
| OA 工作包提前关闭 | 是否绕过回执归档硬门禁 |
| 页面出现英文状态 | 是否缺少 UI 映射或保留了后端 enum |
| 年费弹窗有案号但生成失败 | typed case no 是否解析为真实 case id |
| seed 失败外键错误 | 是否有动态 pay-list / GovPayment 残留 |
| 文件上传无法通过浏览器工具完成 | 是否为工具限制；是否用真实 API 准备并回到 UI 验证 |

## 8. 不得扩大范围

P1 demo 验证不得把以下内容当成已实现：

- CPC/OA direct submit。
- 网页 RPA 自动操作。
- 自动扫码签名。
- 自动下载官方回执。
- 自动缴费。
- 龙虾邮件发送替代。

这些只能作为后续 P2/P3 或待确认项说明。
