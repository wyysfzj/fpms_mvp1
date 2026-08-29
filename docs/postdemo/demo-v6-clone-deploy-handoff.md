# FPMS 客户演示 V6：Clone、部署与同事交接

交付版本：未来不可变 tag `demo-v6-customer-20260829-r1`
数据边界：`SYNTHETIC_TEST_ONLY`

## 1. 验收状态与能力边界

| 验收项 | 当前状态 | 能证明什么 |
| --- | --- | --- |
| 已归档严格 UI 技术路径 | PASS | 当前严格技术路径曾完整通过，不等于未来 tag 或 actor 已验收 |
| 指定 tag 的会前严格 UI | 待 fresh run | 必须在 actor 会话前绑定指定 tag 重跑 |
| HUMAN：待完成 | PENDING | 不得预写或代签 receipt |
| CODEX：待完成 | PENDING | 不得预写或代签 receipt |
| Comparator：待完成 | PENDING | 两份独立 actor receipt 存在后才可运行 |

## 2. 指定 tag 与安装

只有 tag 发布后才执行：

```bash
git clone --branch demo-v6-customer-20260829-r1 --single-branch \
  https://github.com/wyysfzj/fpms_mvp1.git fpms-demo-v6
cd fpms-demo-v6
test "$(git describe --tags --exact-match HEAD)" = "demo-v6-customer-20260829-r1"
test -z "$(git status --porcelain=v1 -uall)"

python3.11 -m venv backend/.venv
backend/.venv/bin/python -m pip install --upgrade pip
FPMS_V6_PYTHON_SOURCE="$(mktemp -d)"
git archive HEAD backend | tar -x -C "$FPMS_V6_PYTHON_SOURCE"
backend/.venv/bin/python -m pip install "$FPMS_V6_PYTHON_SOURCE/backend[dev]"
npm ci --prefix frontend
npm ci --prefix FPMS_Automation_Skeleton_Pack/playwright_ts
(
  cd FPMS_Automation_Skeleton_Pack/playwright_ts
  if [ "$(uname -s)" = "Linux" ]; then
    npx playwright install --with-deps chromium
  else
    npx playwright install chromium
  fi
)
```

不要用旧 candidate 分支、remote 默认分支或自引用 SHA 替代该 tag。本文不联网验证 remote；交接人负责先确认 tag 已发布且不可移动。

## 3. Canonical 定向检查

```bash
backend/.venv/bin/python scripts/check_customer_demo_lifecycle_v6.py
node FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/demo-v6-ui-parity-contract.mjs
(
  cd backend
  .venv/bin/python -m pytest -q tests/test_demo_integrated_a_runner.py
)
backend/.venv/bin/ruff check --no-fix \
  scripts/check_customer_demo_lifecycle_v6.py \
  backend/tests/test_demo_integrated_a_runner.py
git diff --check
test -z "$(git status --porcelain=v1 -uall)"
```

## 4. Actor 会话前的 fresh 严格 UI 检查

下面三项参数 `--strict-ui --runs 1 --headless` 缺一不可：

```bash
FPMS_V6_STRICT_PARENT="$(mktemp -d)"
export FPMS_V6_STRICT_ARTIFACT="$FPMS_V6_STRICT_PARENT/strict-ui"
backend/.venv/bin/python scripts/run_demo_integrated_a_rehearsal.py \
  --profile TECHNICAL_REHEARSAL \
  --strict-ui \
  --runs 1 \
  --headless \
  --artifact "$FPMS_V6_STRICT_ARTIFACT"
test -f "$FPMS_V6_STRICT_ARTIFACT/run1/strict-pass-receipt.json"
```

它证明该 clean tag 的严格 UI 技术路径本轮通过；它不证明 HUMAN/CODEX 独立操作，也不替代 actor receipt。

## 5. HUMAN 与 CODEX 独立会话

```bash
FPMS_V6_HUMAN_PARENT="$(mktemp -d)"
export HUMAN_RECEIPT_ROOT="$FPMS_V6_HUMAN_PARENT/human-receipt"
backend/.venv/bin/python scripts/run_demo_integrated_a_rehearsal.py \
  --ui-session --actor HUMAN --artifact "$HUMAN_RECEIPT_ROOT"

FPMS_V6_CODEX_PARENT="$(mktemp -d)"
export CODEX_RECEIPT_ROOT="$FPMS_V6_CODEX_PARENT/codex-receipt"
backend/.venv/bin/python scripts/run_demo_integrated_a_rehearsal.py \
  --ui-session --actor CODEX --artifact "$CODEX_RECEIPT_ROOT"
```

CODEX 必须在另一个 clean clone、另一个账号中执行。每个会话启动后先读取 actor artifact 下的 `upload-manifest.json`：清单恰有 12 行，每行 `path` 指向同一 actor artifact 的 `upload-files/`。按 `evidence_key`、`title_zh_cn` 和 `metadata` 选取文件；禁止使用另一 actor、旧运行或 bundle 原路径。

两位 actor 均按 `docs/postdemo/demo-lifecycle-customer-v6-runbook.md` 的 01–11 顺序，只操作普通业务 UI。`/demo/inputs` 只用于非共享预检、截图登记和最终导出；禁止 curl、直接 API/SQL、隐藏写入路由和内部 ID 抄写。

## 6. Receipt comparator

两份 `pass-receipt.json` 都实际存在后，生成 clean candidate JSON 并运行：

```bash
export HUMAN_RECEIPT_ROOT="/absolute/path/to/human-receipt"
export CODEX_RECEIPT_ROOT="/absolute/path/to/codex-receipt"
FPMS_V6_ACCEPTANCE_PARENT="$(mktemp -d)"
export ACCEPTANCE_ROOT="$FPMS_V6_ACCEPTANCE_PARENT/actor-acceptance"
mkdir "$ACCEPTANCE_ROOT"
export CANDIDATE_JSON="$ACCEPTANCE_ROOT/candidate.json"

python3 - <<'PY'
import json
import os
import subprocess
from pathlib import Path

def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], text=True).strip()

if git("status", "--porcelain"):
    raise SystemExit("candidate clone is not clean")
Path(os.environ["CANDIDATE_JSON"]).write_text(
    json.dumps({"commit": git("rev-parse", "HEAD"), "tree": git("rev-parse", "HEAD^{tree}"), "status": "CLEAN"}, indent=2) + "\n",
    encoding="utf-8",
)
PY

backend/.venv/bin/python scripts/compare_demo_v6_ui_receipts.py \
  --candidate "$CANDIDATE_JSON" \
  --human "$HUMAN_RECEIPT_ROOT/pass-receipt.json" \
  --codex "$CODEX_RECEIPT_ROOT/pass-receipt.json" \
  --output "$ACCEPTANCE_ROOT/comparison.json"
```

Comparator 只校验 receipt 的 schema、candidate/tree、actor 隔离、103/30 ledger、mutation ledger、11 阶段截图登记字段及网络/console 空数组是否满足冻结合同并相互一致。它不重看浏览器、不能判断截图视觉内容，也不能证明客户授权、正式递交、正式官费来源激活或官方缴费成功。

## 7. 客户可见检查点

- 客户详情面包屑显示客户名称。
- 案件列表显示“第5阶段/5 · 授权登记”和“流程状态”。
- 文书页面显示结构化文书字段。
- 首次申请规则在授权登记阶段显示为历史核验，不冒充当前阻断。
- “预览官费”“确认官费”按钮可见、可点；确认前不形成缴费义务。
- 三轨摘要当前优先；完整历史默认收起；技术标识、摘要和原始英文状态只在展开审计信息后可见。

## 8. 停止条件

tag 不匹配、工作区非 clean、upload manifest 不是 12 行、bundle 已过 `2026-09-30`、严格 UI 未通过、业务库非空、页面事实漂移、Network/console 错误、任一 receipt 缺失或 comparator 失败时立即停止。保留失败 artifact，不在客户面前改代码或复用旧运行。
