# FPMS 客户演示 V6：Clone、部署与同事交接

适用分支：`codex/demo-v6-ui-parity-candidate-20260826`
适用系统：macOS 或 Linux 现场电脑
业务范围：同一案件的生命周期、证据链、双轨费用、客户账单、两次回款与核销
默认数据边界：`SYNTHETIC_TEST_ONLY`

## 1. 先看结论

本候选分支可以从全新 clone 安装依赖，运行既有 A 技术回归，并由 HUMAN 或另一 Codex 账号从空业务库通过同一套正常 UI 完成 11 阶段 V6 演示。它是客户在场的合成技术展示候选，不是生产或正式客户数据发布分支。

| 路径 | 输入要求 | 可以证明 | 是否可面对客户 |
| --- | --- | --- | --- |
| A 技术回归 | 仓库生成的 `SYNTHETIC_TEST_ONLY` bundle | 两轮自动回归与技术稳定性 | 只用于会前排练 |
| B-HUMAN | 主持人按 Runbook 在正常 UI 输入/选择 | 人工可完成同一 01–11 链 | 可作客户在场的合成技术展示 |
| B-CODEX | 另一 Codex 账号从 fresh clone 按同一 Runbook 操作浏览器 | 与 HUMAN 输入/输出等价 | 可作独立复核，不替代 HUMAN |

三条路径都读取 `fpms.demo-v6-ui-parity/v1`。B 路径仍是 `SYNTHETIC_TEST_ONLY`，现场必须明确表述为“客户在场的合成技术展示”，不得称为正式客户输入、生产数据、正式报价、官方递交或官方缴费成功。

## 2. 交付物索引

- 客户路线图：`docs/postdemo/demo-lifecycle-customer-v6.html`
- 完整演示 Runbook：`docs/postdemo/demo-lifecycle-customer-v6-runbook.md`
- 种子与 Runtime 输入：`docs/postdemo/demo-lifecycle-customer-v6-seed-data.md`
- Canonical runner：`scripts/run_demo_integrated_a_rehearsal.py`
- V6 文档检查：`scripts/check_customer_demo_lifecycle_v6.py`

`docker-compose.demo.yml` 是通用 SQLite 产品容器，不会自动准备 V6 的 11 阶段 runtime bundle 和业务链。不要把“通用容器成功启动”当作 V6 演示通过。

## 3. 现场电脑前置条件

首次安装和 Playwright 系统依赖通常需要网络。本文没有交付或验证 Python wheelhouse、npm 离线缓存，因此不承诺全新 clone 可离线安装；必须在到场前完成安装和验收。

```text
Git
Python 3.11+
Node.js 20+
npm
Chromium（由 Playwright 安装）
```

建议至少预留 8 GB 内存和 5 GB 磁盘。端口 `5173`、`8000` 必须空闲。不要连接生产数据库或共享演示数据库。

## 4. 全新 Clone 与依赖安装

```bash
git clone --branch codex/demo-v6-ui-parity-candidate-20260826 --single-branch \
  https://github.com/wyysfzj/fpms_mvp1.git fpms-demo-v6
cd fpms-demo-v6

git rev-parse HEAD
git status --short
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

test -z "$(git status --porcelain=v1 -uall)"
```

Linux 的 `--with-deps` 可能要求 sudo/root 权限，必须在会前由设备管理员完成。将 `git rev-parse HEAD` 的完整值与交接人提供的候选 SHA-256 字符串逐字比较。期待结果：`git status --short` 无输出；Python、前端和 Playwright 安装命令均返回 `0`。如果公司网络需要代理，应在会前完成安装，不要在客户面前临时修改项目依赖声明。

## 5. 会前技术演练

### 5.1 静态与构建检查

```bash
backend/.venv/bin/python scripts/check_customer_demo_lifecycle_v6.py
node FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/demo-integrated-v6-static-contract.mjs
(
  cd backend
  .venv/bin/python -m pytest -q \
    tests/test_demo_abc_local_runner.py \
    tests/test_demo_abc_runtime_bundle.py \
    tests/test_demo_integrated_a_runner.py \
    tests/test_demo_v6_grant_official_fee.py \
    tests/test_v8_official_rate_book_activation.py \
    tests/test_v8_official_rate_book_schema.py \
    tests/test_official_fee_rate_catalog_seed.py
)
backend/.venv/bin/ruff check --no-fix \
  scripts/check_customer_demo_lifecycle_v6.py \
  scripts/run_demo_integrated_a_rehearsal.py \
  backend/app/modules/fees/official_rate_book.py \
  backend/scripts/seed_dev.py \
  backend/tests/test_demo_abc_local_runner.py \
  backend/tests/test_demo_abc_runtime_bundle.py \
  backend/tests/test_demo_integrated_a_runner.py \
  backend/tests/test_demo_v6_grant_official_fee.py \
  backend/tests/test_v8_official_rate_book_activation.py
npm --prefix frontend run typecheck
npm --prefix frontend run build
test -z "$(git status --porcelain=v1 -uall)"
```

期待结果：V6 文档检查显示 `customer demo lifecycle V6: PASS`；pytest 无失败；typecheck 和 build 返回 `0`。

### 5.2 完整 11 阶段技术演练

```bash
FPMS_V6_RUN_ROOT="$(mktemp -d)"
export FPMS_V6_ARTIFACT="$FPMS_V6_RUN_ROOT/technical-rehearsal"

backend/.venv/bin/python scripts/run_demo_integrated_a_rehearsal.py \
  --profile TECHNICAL_REHEARSAL \
  --runs 2 \
  --headless \
  --artifact "$FPMS_V6_ARTIFACT"

backend/.venv/bin/python - <<'PY'
import json
import os
from pathlib import Path

root = Path(os.environ["FPMS_V6_ARTIFACT"])
summary = json.loads((root / "summary.json").read_text(encoding="utf-8"))
assert summary["status"] == "TECHNICAL_REHEARSAL_PASS"
assert summary["runs"] == 2
for ordinal in (1, 2):
    run = root / f"run{ordinal}"
    receipt = json.loads((run / "pass-receipt.json").read_text(encoding="utf-8"))
    stages = json.loads((run / "v6-stages.json").read_text(encoding="utf-8"))
    assert receipt["stage_count"] == 11
    assert stages["network_errors"] == []
    assert stages["console_errors"] == []
print("TECHNICAL_REHEARSAL_PASS: 2 runs × 11 stages, network=0, console=0")
PY
```

Runner 每次创建全新数据库、业务号、密码和证据目录，并通过 exact run root 进行有界的运行后处理。不要把上一轮当作 reset 输入或在 preflight 删除旧 run；失败 artifact 必须保留，通过轮次只保留只读 artifact 作为排练证据。

## 6. Setup-only HUMAN / CODEX 会话

两个 actor 必须使用不同 clean clone、不同外部 evidence root 和不同操作者账号。下面只展示共同命令形式；不能由一个 actor 冒充两次。`--ui-session` 不接受 `--profile`、`--runs` 或 `--headless`。

```bash
FPMS_V6_ACTOR_PARENT="$(mktemp -d)"
FPMS_V6_ACTOR_ROOT="$FPMS_V6_ACTOR_PARENT/human-receipt"  # CODEX 改为独立父目录/codex-receipt

backend/.venv/bin/python scripts/run_demo_integrated_a_rehearsal.py \
  --ui-session \
  --actor HUMAN \
  --artifact "$FPMS_V6_ACTOR_ROOT"
```

命令会启动 8000/5173 和一个长期保持的 headed 浏览器。stdout 只显示脱敏会话信息；当前 run 的一次性 `admin` 密码只显示在本地 terminal stderr，不写入 artifact/receipt。用它在正常登录页登录，然后：

1. 打开 `/demo/inputs`，点击“校验演示输入与空业务库”；确认 `SYNTHETIC_TEST_ONLY`、不允许客户激活、所有业务表为 0。
2. 严格按 `docs/postdemo/demo-lifecycle-customer-v6-runbook.md` 的 01–11 顺序操作，只使用页面填入、选择、上传、点击和正常链接导航。
3. 每阶段结束点击顶部“记录阶段 NN 截图”；截图必须互不相同。
4. 第 11 阶段只读核对后回 `/demo/inputs`，点击“完成并导出本轮证据”。等待 terminal 正常退出。
5. 检查 `$FPMS_V6_ACTOR_ROOT/pass-receipt.json`：actor、candidate、103/30 ledger、11 screenshots、Network/console 空数组均完整。

CODEX actor 将 `--actor HUMAN` 改为 `--actor CODEX`，除此以外不改变业务值。给另一 Codex 账号的指令是：

```text
读取 AGENTS.md、docs/postdemo/demo-v6-clone-deploy-handoff.md、
docs/postdemo/demo-lifecycle-customer-v6-runbook.md 和唯一 JSON contract。
从 clean clone 执行 --ui-session --actor CODEX；只控制浏览器正常 UI。
禁止 curl、直接 API/SQL、隐藏演示控制路由、内部 ID 抄写、旧 artifact 或数据库复用。
严格按 01–11 操作和截图；任一停止条件发生立即停止且保留 artifact，不改代码重试。
```

### 两份 receipt 比较

```bash
backend/.venv/bin/python scripts/compare_demo_v6_ui_receipts.py \
  --candidate "$CANDIDATE_JSON" \
  --human "$HUMAN_RECEIPT_ROOT/pass-receipt.json" \
  --codex "$CODEX_RECEIPT_ROOT/pass-receipt.json" \
  --output "$ACCEPTANCE_ROOT/comparison.json"
```

`$CANDIDATE_JSON` 是包含当前 `commit`、`tree`、`status=CLEAN` 的 JSON 文件，不是裸 SHA 字符串。比较 PASS 才证明两个 actor 在允许差异之外得到相同规范化输入、输出与可见 mutation 顺序。

## 8. 现场停止条件

出现任何一项立即停止，不在客户面前调试：

- 分支或 commit 与会前验收版本不一致，或 `git status --short` 非空。
- `/demo/inputs` 不是 `SYNTHETIC_TEST_ONLY`、业务表任一非 0，或 manifest/authority 摘要不匹配。
- 端口被占用、迁移/seed 失败、首次加载 Network Error、console error。
- 页面出现英文新增状态、重复对象、跨案对象或金额不满足 `1,200.00 + 600.00 = 1,800.00`。
- GOV 被展示为已有官方凭证，或 SERVICE 结清被解释为官费已官方支付。
- 需要临时改代码、改数据库、关闭校验或重复使用上一轮 run。

恢复方式：保留失败 artifact，停止共享屏幕，修复后用全新的 run root、数据库、业务号和 artifact 重新完成会前验收。

## 9. 最终交接 Checklist

- [ ] 从 GitHub 指定候选分支全新 clone；完整 commit SHA 与交接值一致，工作区干净。
- [ ] Python、frontend、Playwright 均按 lock/项目声明安装成功。
- [ ] 文档检查、pytest、typecheck、build 全部返回 `0`。
- [ ] `TECHNICAL_REHEARSAL_PASS`，11 阶段，Network Error 0，console error 0。
- [ ] HUMAN 与 CODEX 使用不同 clean clone、账号、run root、数据库和 evidence root。
- [ ] 两份 actor `pass-receipt.json` 与 comparator 均 PASS。
- [ ] 主持人已打开 Runbook、种子说明和客户生命周期 HTML。
- [ ] 已准备离线依赖、备用电脑、电源和本地失败 artifact 路径。
- [ ] 已确认所有停止条件，且不会在客户面前临时修改系统。
