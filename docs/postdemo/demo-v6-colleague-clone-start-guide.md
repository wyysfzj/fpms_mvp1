# FPMS V6 客户演示：同事 Clone 与启动 Quickstart

交付版本：未来不可变 tag `demo-v6-customer-20260829-r2`

数据边界：`SYNTHETIC_TEST_ONLY`

本文只帮助同事拿到指定版本、安装依赖并找到入口。完整会前验收、严格 UI 检查、HUMAN/CODEX 会话、receipt 比较和停止条件，统一以 `docs/postdemo/demo-v6-clone-deploy-handoff.md` 为 canonical 验收路径；不要把本 Quickstart 当作第二套较弱验收。

## 1. 获取指定 tag

只有交接人确认 tag 已发布后才执行：

```bash
git clone --branch demo-v6-customer-20260829-r2 --single-branch \
  https://github.com/wyysfzj/fpms_mvp1.git fpms-demo-v6
cd fpms-demo-v6
test "$(git describe --tags --exact-match HEAD)" = "demo-v6-customer-20260829-r2"
test -z "$(git status --porcelain=v1 -uall)"
```

不得改用旧 candidate 分支、普通 remote 默认分支或交接文档中的自引用 commit。tag 尚未发布、不能精确匹配或工作区不干净时立即停止。

## 2. 安装依赖

```bash
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

首次安装通常需要网络；Linux 的系统依赖可能需要设备管理员权限，必须在会前完成。

## 3. 最小入口检查

```bash
backend/.venv/bin/python scripts/check_customer_demo_lifecycle_v6.py
node FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/demo-v6-ui-parity-contract.mjs
```

随后立即转到 canonical handoff，执行其中完整的会前严格 UI 检查。不能因这两个命令成功而跳过 handoff。

## 4. Actor 启动入口

HUMAN 与 CODEX 必须使用不同 clean clone、账号、数据库、run root 和 evidence root。共同场景有 11 个阶段、103 个输入/来源字段、30 个可见输出字段。

Runner 启动 actor 会话后，会在 actor artifact 下生成：

- `upload-manifest.json`：12 份冻结合成证据的操作清单；
- `upload-files/`：与清单逐行绑定的本地上传文件；
- `pass-receipt.json`：只有完整结束会话后才可能生成的 actor receipt。

操作者必须按 `upload-manifest.json` 的 `evidence_key` 和 `title_zh_cn` 选择对应 `path`，并使用 Runbook“十二份上传文件的附件角色”表选择中文附件角色。固定顺序是先选择文件、再选择附件角色、最后确认上传；`evidence_key` 不能直接填入附件角色。不得改用仓库原始 bundle 路径或上轮 artifact。具体命令、逐阶段动作和验收状态见 canonical handoff 与 Runbook。

## 5. 必读资料

- `docs/postdemo/demo-v6-clone-deploy-handoff.md`
- `docs/postdemo/demo-lifecycle-customer-v6-runbook.md`
- `docs/postdemo/demo-lifecycle-customer-v6-seed-data.md`
- `docs/postdemo/demo-lifecycle-customer-v6.html`
- `FPMS_Automation_Skeleton_Pack/data/testcases/demo_v6_ui_parity_v1.json`

任一检查失败时保留失败 artifact、停止共享屏幕，不在客户面前改代码、改库、关闭校验或复用旧运行。
