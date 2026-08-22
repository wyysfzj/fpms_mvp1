# FPMS P1 V7 UI E2E 成功演示 Runbook

任务：`PD-P1-V7-DEMO-RUNBOOK-DOC-20260711-01`  
执行角色：QA / Demo Operator  
适用版本：V7（2026-07-11）

本文是可独立执行的操作手册。操作员必须按顺序完成 Preflight、权限核对、受控 cleanup、
14 个检查点、Evidence 固化和演示后清理。任何核心检查点不得靠口头说明替代系统可见结果。

## 1. 执行原则与边界

### 1.1 核心真实路径铁律

- `WIZARD`、`WORKPKG`、`OA`、`RECEIPT`、`CATALOG`、`DEADLINE`、`GRANT` 必须走真实路径。
- 核心 GAP 路径不得使用 enrichment。
- 禁止 route mock、请求拦截或伪造响应。
- 禁止数据库注入、直接 SQL、ORM 控制台写入或手工改状态。
- 禁止用 enrichment 创建或覆盖客户、案件、文件向导、工作包、OA、回执、期限、授权来源、
  授权任务、替代关系或授权草单。
- 核心对象 ID 必须由真实公共 UI/API 行为生成，并在运行记录中动态捕获；不得预设固定 ID。
- 打开或解析递交准备工作包只证明业务准备和工作包状态变化，不代表已经向官方提交，也不
  推进法律状态。

### 1.2 允许的最小 enrichment

`enrichment` 只能在 `V7-13` 执行，且仅能补充当前 UI 无法在可控演示时长内完整创建的：

1. 申请费草单及申请费官费清单；
2. 格式函、交接记录及其展示附件；
3. 年费任务、年费草单及年费官费清单。

每次 enrichment 必须记录脚本/命令、准确新增记录、执行前后数量、rc 和操作者，并证明没有
覆盖 UI 创建的客户/案件事实或任何核心 GAP 对象。未在上述明确 allowlist 中的对象一律禁止。

### 1.3 不承诺的能力

本轮不演示或承诺自动官方提交、RPA、自动签名、自动下载回执、自动缴费或自动发送邮件。
FPMS 展示的是内部准备、核验、归档、费用和责任动作的可审计闭环。

## 2. 固定 V7 演示数据与动态运行记录

### 2.1 固定业务名称

| 对象 | 固定值 |
| --- | --- |
| 客户名称 | `P1七版演示客户有限公司` |
| 客户代码 | `PD-P1-V7-LIVE` |
| 主联系人 | `钱七老师` |
| 案号 | `P1E2E-V7-LIVE` |
| 案件标题 | `P1七版真实GAP闭环演示方法及系统` |
| 申请号 | `CN202610000007.0` |
| 授权号/专利号 | `ZL202610000007.0` |

### 2.2 动态 ID 运行记录

执行前创建 `artifacts/PD-P1-V7-DEMO-RUN-<时间戳>/run-record.md`，按真实响应依次填写：

| 对象 | 动态 ID | 生成检查点 | 清理确认 |
| --- | --- | --- | --- |
| 客户 / 联系人 | 待记录 | `V7-01` | 待确认 |
| 案件 | 待记录 | `V7-02` | 待确认 |
| 递交工作包 | 待记录 | `V7-04` | 待确认 |
| 第一份 OA 来源文书 / 工作包 / 任务 | 待记录 | `V7-05` | 待确认 |
| OA_OUT 文书 | 待记录 | `V7-06` | 待确认 |
| 错案/错来源/有效回执 | 待记录 | `V7-07`、`V7-08` | 待确认 |
| 后续 OA 来源文书 / 工作包 / 任务 | 待记录 | `V7-09` | 待确认 |
| 原授权来源 / 授权任务 | 待记录 | `V7-10` | 待确认 |
| 新授权来源 / 替代任务 | 待记录 | `V7-11` | 待确认 |
| 新任务草单 / PAY 流程记录 | 待记录 | `V7-12` | 待确认 |
| allowlist enrichment 记录 | 待记录 | `V7-13` | 待确认 |

禁止将历史 V6、其他测试或生产数据 ID 填入 V7 运行记录。

## 3. 四维状态记录

每个检查点都必须在运行记录中填写以下四列，只使用下列业务词汇：

| 维度 | V7 允许的状态流 |
| --- | --- |
| 案件业务状态 | 客户资料建立 → 新案立案 → 递交准备 → OA答复处理中 → 授权处理 → 年费监控 |
| 法律状态 | 未递交 → 等待受理 → 实审中 → 一通或二通阶段 → 实审中 → 已授权 → 维持有效 |
| 工作包/文件状态 | 未创建 → 已解析/待准备 → 待提交 → 待回执 → 已归档/已关闭；授权任务另分来源已确认/已被替代 |
| 费用节点状态 | 无费用 → 待预览 → 待客户指示 → 已生成草单 → 已生成官费清单 → 待缴费登记 → 已登记 |

上表是允许的完整业务词汇，不表示本轮每个节点都已发生。当前 V7-13 因缺少安全入口而
BLOCKED，实际运行的费用证据在 V7-12 结束于“已生成草单”；后续节点不得出现在最终状态中。

若 UI 可见状态与上述业务含义不一致，立即停止；不得由讲解人“手工推进”状态。

## 4. 七项 GAP 操作矩阵

| canonical ID | V7 必验处理 | 通过证据 |
| --- | --- | --- |
| `WIZARD` | 使用真实、受上限约束的模板列表，不出现确定性的 page-size 422。 | 向导页面截图、请求/响应状态和模板选择记录。 |
| `WORKPKG` | 递交与 OA 使用 existing-first resolve；真实页面无需 enrichment 可达。 | 两次 resolve 的同一对象 ID、页面 URL 和可见状态。 |
| `OA` | 创建 OA_OUT 后任务和案件仍保持开放/OA 状态；后续 OA 身份独立。 | 前后任务状态、案件状态和两组 source/package/task ID。 |
| `RECEIPT` | 错案、同案错来源均失败且无变化；有效归属回执只关闭一个任务。 | 失败前后快照、有效归档结果和任务计数。 |
| `CATALOG` | 60 行全部可见；批准行显示“可执行”，参考行显示“仅供参考”且不可操作。 | 行数、两类样例及禁用动作截图。 |
| `DEADLINE` | 完整日期/source/`CONFIRMED`；验证创建、读取、更新、向导、预览及缺失/畸形 fail-closed。 | 字段前后值、预览和失败无写入证据。 |
| `GRANT` | 来源关联且期限已确认；不自动草拟；替代后旧任务已被替代且所有变更入口受阻，新任务走客户指示/PAY 草单路径。 | 旧/新 lineage、禁用 UI、409 无变更和新任务草单。 |

## 5. Preflight

### 5.1 环境与服务

1. 使用独立、可删除的 SQLite 数据库文件和独立存储目录；不得连接生产或共享演示库。
2. 从当前迁移头创建数据库，执行标准 seed；记录 migration head、seed rc 和服务启动时间。
3. 后端、前端均绑定本机明确端口；前端 API base 必须指向本轮后端。
4. 健康检查、登录页、客户列表、案件列表、文档向导、官方工作包和授权任务页均应可打开。
5. 浏览器使用干净上下文；禁用 HTTP 代理变量，避免代理污染本机流量。
6. 确认系统时间、时区、截图时间戳和证据目录一致。
7. 记录当前版本标识；不执行 commit、push、reset、clean 或 stash。

#### 5.1.1 从仓库根目录创建隔离环境

以下命令使用仓库已有的 Alembic、`backend/scripts/seed_dev.py`、uvicorn 和 Vite 入口。先由
操作员通过安全渠道设置每轮 `JWT_SECRET`。标准 seed 的管理员密码当前由
`backend/scripts/seed_dev.py` 固定写入；下述 AST 读取只把该值放入当前 shell 变量，不输出，
命令和 Evidence 均不得记录密码或 token。

```bash
cd /Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic
export FPMS_V7_RUN_ID="$(date +%Y%m%d%H%M%S)"
export FPMS_V7_DB="/tmp/fpms_p1_v7_${FPMS_V7_RUN_ID}.db"
export FPMS_V7_STORAGE="/tmp/fpms_p1_v7_storage_${FPMS_V7_RUN_ID}"
export FPMS_V7_BACKEND_PORT=8077
export FPMS_V7_FRONTEND_PORT=5177
export DATABASE_URL="sqlite:////tmp/fpms_p1_v7_${FPMS_V7_RUN_ID}.db"
export STORAGE_DIR="${FPMS_V7_STORAGE}"
export FPMS_ENV=demo
export CORS_ORIGINS='["http://127.0.0.1:5177"]'
export VITE_API_BASE_URL="http://127.0.0.1:8077/api/v1"
export FPMS_ADMIN_PASSWORD="$(python3 -c 'import ast; from pathlib import Path; tree=ast.parse(Path("backend/scripts/seed_dev.py").read_text()); values={n.args[0].value for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=="get_password_hash" and n.args and isinstance(n.args[0],ast.Constant) and isinstance(n.args[0].value,str)}; assert len(values)==1; print(values.pop())')"
test -n "${FPMS_ADMIN_PASSWORD:?could not derive the standard-seed admin password at runtime}"
test -n "${JWT_SECRET:?set a per-run JWT_SECRET through the secure operator channel}"
test ! -e "${FPMS_V7_DB}"
mkdir -p "${FPMS_V7_STORAGE}"
```

预期：所有命令 rc=0；数据库在 migration 前不存在；存储目录为空。若数据库已存在，不得覆盖，
应更换 `FPMS_V7_RUN_ID`。

#### 5.1.2 迁移与标准 seed

```bash
cd /Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic
(
  cd backend
  FPMS_ENV="${FPMS_ENV}" DATABASE_URL="${DATABASE_URL}" STORAGE_DIR="${STORAGE_DIR}" \
    JWT_SECRET="${JWT_SECRET}" FPMS_ADMIN_PASSWORD="${FPMS_ADMIN_PASSWORD}" \
    .venv/bin/alembic upgrade head
)
(
  cd backend
  FPMS_ENV="${FPMS_ENV}" DATABASE_URL="${DATABASE_URL}" STORAGE_DIR="${STORAGE_DIR}" \
    JWT_SECRET="${JWT_SECRET}" FPMS_ADMIN_PASSWORD="${FPMS_ADMIN_PASSWORD}" \
    PYTHONPATH=. .venv/bin/python scripts/seed_dev.py
)
```

真实入口分别为 `backend/.venv/bin/alembic` 和 `backend/scripts/seed_dev.py`。预期两段 rc=0；
seed 只建立标准主数据，不建立 V7 客户、案件或核心 GAP 对象。

#### 5.1.3 启动后端与前端

分别在两个受控终端执行，并把 PID 写入运行记录：

```bash
cd /Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic
(
  cd backend
  FPMS_ENV="${FPMS_ENV}" DATABASE_URL="${DATABASE_URL}" STORAGE_DIR="${STORAGE_DIR}" \
    JWT_SECRET="${JWT_SECRET}" FPMS_ADMIN_PASSWORD="${FPMS_ADMIN_PASSWORD}" \
    .venv/bin/uvicorn app.main:app --host 127.0.0.1 --port "${FPMS_V7_BACKEND_PORT}"
)
```

```bash
cd /Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic
(
  cd frontend
  VITE_API_BASE_URL="${VITE_API_BASE_URL}" npm run dev -- \
    --host 127.0.0.1 --port "${FPMS_V7_FRONTEND_PORT}"
)
```

健康检查：

```bash
curl -fsS "http://127.0.0.1:${FPMS_V7_BACKEND_PORT}/healthz"
curl -fsS "http://127.0.0.1:${FPMS_V7_FRONTEND_PORT}/" >/dev/null
```

预期：两个 `curl` rc=0；后端响应 `{"status":"ok"}`。服务日志路径/PID由启动终端记录，
不得把密码、JWT 或 Authorization header 写入 Evidence。

#### 5.1.4 公共 API 零数据预览

以下命令只使用现有 `/api/v1/auth/login`、`GET /api/v1/clients` 和 `GET /api/v1/cases`
公共入口。token 只存在当前终端环境，不得输出或写入 Evidence。

```bash
cd /Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic
export FPMS_V7_TOKEN="$(
  curl -fsS -X POST "http://127.0.0.1:${FPMS_V7_BACKEND_PORT}/api/v1/auth/login" \
    -H 'Content-Type: application/json' \
    -d "{\"username\":\"admin\",\"password\":\"${FPMS_ADMIN_PASSWORD}\"}" \
  | python3 -c 'import json,sys; print(json.load(sys.stdin)["access_token"])'
)"
test -n "${FPMS_V7_TOKEN}"
curl -fsS -G "http://127.0.0.1:${FPMS_V7_BACKEND_PORT}/api/v1/clients" \
  -H "Authorization: Bearer ${FPMS_V7_TOKEN}" \
  --data-urlencode 'q=PD-P1-V7-LIVE' --data-urlencode 'page_size=20' \
  | python3 -c 'import json,sys; d=json.load(sys.stdin); print("v7_client_pre_count=" + str(d["total"])); assert d["total"] == 0'
curl -fsS -G "http://127.0.0.1:${FPMS_V7_BACKEND_PORT}/api/v1/cases" \
  -H "Authorization: Bearer ${FPMS_V7_TOKEN}" \
  --data-urlencode 'case_no=P1E2E-V7-LIVE' --data-urlencode 'page_size=20' \
  | python3 -c 'import json,sys; d=json.load(sys.stdin); print("v7_case_pre_count=" + str(d["total"])); assert d["total"] == 0'
unset FPMS_V7_TOKEN
```

预期：登录及两次查询均 rc=0，输出仅为 `v7_client_pre_count=0`、`v7_case_pre_count=0`。
任何非零结果都说明数据库不是本轮全新隔离库，Preflight 必须停止。

任一服务指向错误数据库、页面出现未解释的 401/403/5xx、migration/seed 非零，均不得进入
`V7-01`。

### 5.2 权限核对

使用演示管理员或专用演示账号登录，逐项验证实际 UI 可见和操作权限：

- 客户及联系人：读取、创建、维护；
- 案件：读取、创建、维护；
- 文书与模板：`Doc.Read`、`Doc.Create`、`Doc.Edit`、`Doc.Attach`、`DocTemplate.Read`；
- 官方工作流：`OfficialWorkflow.Read`、`OfficialWorkflow.Update`；
- OA 任务读取与关闭结果核对：`Task.Read`；
- 授权任务：`GrantFeeTask.Read`、`GrantFeeTask.Write`；
- 费用草单、官费清单、格式函和年费支线所需读取/创建权限。

权限验证只允许正常登录和产品权限路径。不得临时修改权限注册表或数据库。出现 403 时先确认
账号和既有角色配置；无法按既有授权恢复则停止演示。

### 5.3 演示前 cleanup 与明确 allowlist

演示前 cleanup 只能删除下列 V7 专属事实及运行记录中动态捕获的从属对象：

- 客户代码精确等于 `PD-P1-V7-LIVE`；
- 案号精确等于 `P1E2E-V7-LIVE`；
- 与上述客户/案件由本轮生成并记录 ID 的联系人、文书、工作包、任务、回执、授权替代对象；
- `V7-13` 记录的申请费、格式函和年费 enrichment 对象。

禁止通配符删除，禁止 `LIKE '%P1%'`，禁止按“最近创建”批量删除，禁止删除 V6、其他测试或
真实客户数据。执行顺序应从从属对象到客户主记录，并保存预览清单、删除计数和 rc。若待删除
对象不在明确 allowlist 或无法证明归属，本次 cleanup 必须停止。

本仓库当前没有 V7 记录级 cleanup API 或脚本；现有 `demo:p1:v6:cleanup` 只识别 V6 固定值，
不得用于 V7。因为本 runbook 强制使用全新隔离 SQLite，演示前 cleanup 的真实机制就是上述
“数据库不存在 + 公共 API 精确查询总数为 0”，不能对共享数据库执行删除。演示后使用第 9 节
的精确隔离环境销毁命令。

### 5.4 Preflight 通过记录

在运行记录中勾选：

- [ ] 独立 SQLite / 存储目录已确认；
- [ ] migration、seed、健康检查通过；
- [ ] 前后端端口和 API base 已记录；
- [ ] 演示账号及权限通过；
- [ ] 演示前 cleanup 仅命中明确 allowlist；
- [ ] V6 保护文件状态无变化；
- [ ] Evidence 目录可写；
- [ ] 核心路径禁止项已向所有操作员说明。

## 6. V7-01 至 V7-14 执行检查点

### `V7-01` UI 创建客户与主联系人

- 操作：通过客户新建页创建 `P1七版演示客户有限公司`，客户代码
  `PD-P1-V7-LIVE`；进入详情添加主联系人 `钱七老师`。
- 验证：客户列表、详情和联系人列表均显示固定值；动态 ID 写入运行记录。
- 四维状态：案件业务状态为“客户资料建立”；案件尚未创建，法律状态为 N/A；工作包/文件
  状态为“未创建”；费用节点状态为“无费用”。
- Evidence：创建成功页、客户详情、联系人行截图及必要的成功响应摘要。
- 停止条件：重复代码指向非本轮客户、联系人未归属该客户或页面依赖 enrichment。
- 恢复：确认是 V7 allowlist 对象后清理该客户重做；不得改数据库绕过唯一约束。

### `V7-02` UI 创建案件并确认四个初始状态

- 操作：通过案件新建页创建案号 `P1E2E-V7-LIVE`，标题
  `P1七版真实GAP闭环演示方法及系统`，关联 V7 客户，填写申请号
  `CN202610000007.0` 和授权/专利号 `ZL202610000007.0` 所需基础事实。
- 验证：案件详情可重新打开，客户关联和固定字段一致。
- 四维状态：案件业务状态“新案立案”；法律状态“未递交”；工作包/文件状态“未创建”；
  费用节点状态“无费用”。
- Evidence：新建结果、案件详情和四维状态基线截图。
- 停止条件：案件来源不是 UI、关键字段被脚本覆盖或初始状态异常。
- 恢复：只清理本轮 V7 案件及从属记录后从 `V7-02` 重做。

### `V7-03` 向导边界与 60 行目录分类

- 操作：打开文档向导，加载真实模板并选择可执行官方模板；打开官方文书目录。
- 验证：模板列表请求受 API 上限约束且页面无确定性 422；目录显示全部 60 行；分别定位
  “可执行”和“仅供参考”样例，参考行操作禁用。
- 四维状态：四维不推进；这是能力与门禁检查。
- GAP：`WIZARD`、`CATALOG`。
- Evidence：模板列表成功、60 行计数、两类中文状态和禁用动作截图。
- 停止条件：模板请求 422、目录少于 60 行、参考行可执行。
- 恢复：刷新一次并核对标准 seed；仍异常则停止，不得 route mock 或补数据库数据。

### `V7-04` 递交工作包 existing-first resolve

- 操作：从案件真实入口 resolve 递交准备工作包；再次执行同一 resolve 并打开准备页。
- 验证：两次返回同一动态 package ID，页面可达且显示准备状态，无 enrichment。
- 四维状态：案件业务状态“递交准备”；工作包/文件状态“已解析/待准备”；法律状态仍
  “未递交”，不得因打开页面自行推进；费用仅“待预览”。
- GAP：`WORKPKG`。
- Evidence：两次 resolve ID、页面 URL、字段/文件 readiness 截图。
- 停止条件：生成重复包、页面必须依赖固定 fixture、法律状态被准备动作错误推进。
- 恢复：保留首个真实包，重新从案件入口解析；重复对象需作为缺陷停止。

### `V7-05` 创建带明确期限的 OA 并 resolve OA 工作包

- 操作：用真实文书创建路径登记 OA 来文，输入明确官方期限日期、来源和 `CONFIRMED`；从
  案件/OA 入口 resolve 工作包并再次 resolve。
- 验证：文书创建、读取、编辑、影响预览及向导回显同一完整期限三元组；两次 resolve 返回
  同一 OA package/task identity；缺失或不完整三元组应 fail-closed 且无写入。
- 四维状态：案件业务状态“OA答复处理中”；法律状态“一通或二通阶段”；工作包/文件状态
  “已解析/待准备”至“待提交”；费用节点状态不因 OA 自动变化。
- GAP：`DEADLINE`、`WORKPKG`、`OA`。
- Evidence：期限三字段、预览、成功对象 ID、失败前后计数和 OA 页面截图。
- 停止条件：期限由模板偏移推导、状态不是 `CONFIRMED`、重复工作包或失败后有写入。
- 恢复：删除仅本轮未完成 OA 对象后通过真实创建路径重做；不得直接修数据库字段。

### `V7-06` 创建 OA_OUT 并证明任务保持开放

- 操作：通过真实文书路径创建与第一份 OA 来源关联的 OA_OUT。
- 验证：OA_OUT 创建成功，但 OA 任务仍为开放，案件仍处于 OA 答复处理中；不恢复案件状态。
- 四维状态：工作包/文件状态进入“待回执”；案件业务状态和法律状态保持 OA 阶段；费用不变。
- GAP：`OA`。
- Evidence：OA_OUT 关联、创建前后任务状态和案件状态截图。
- 停止条件：创建 OA_OUT 后任务被自动关闭或案件被恢复。
- 恢复：保留证据并停止；不得手工重开任务掩盖错误。

### `V7-07` 错案与错来源回执 fail-closed

- 操作：仅使用真实公共 UI/API 创建两组失败 fixture，不使用 enrichment 或历史预置记录：
  1. `POST /api/v1/cases` 创建案号 `P1E2E-V7-RECEIPT-GATE-<运行后缀>` 的隔离案件，payload
     固定包含 `case_type=NORMAL`、`patent_category=INV`、`flow_dir=CN_DOMESTIC`、
     `status=NOT_FILED` 和标题“V7回执门禁隔离案件”；捕获 `wrong_case_id`。
  2. `POST /api/v1/documents` 在隔离案件创建 `direction=OUT`、本轮 `doc_date`、标题
     “V7跨案回执载体”的无模板普通发文；捕获 `wrong_case_document_id`。
  3. `POST /api/v1/documents/{wrong_case_document_id}/attachments` 以 multipart 上传本轮 PDF，
     `official_file_role=ELECTRONIC_RECEIPT`、`source_role_alias=ELECTRONIC_RECEIPT`；捕获
     `wrong_case_attachment_id`。
  4. `POST /api/v1/documents` 在 V7 主案件创建相同字段但标题为“V7同案非OA来源文书”的普通
     发文；上传同角色 PDF 并捕获 `wrong_source_document_id`、`wrong_source_attachment_id`。
  5. 分别向首次 OA 的
     `POST /api/v1/official-work-packages/{first_oa_package_id}/receipts` 提交两份附件。payload
     均完整包含 `receipt_kind=ELECTRONIC_APPLICATION_RECEIPT`、对应 attachment ID、本轮
     `receiving_case_no`、`submitter`、`received_at`、`received_file_list`、
     `archive_status=ARCHIVED` 和 note。
- 验证：两个请求都被业务门禁拒绝；原 OA task/package/case 状态及归档计数完全不变。
- 四维状态：四维均不变化。
- GAP：`RECEIPT`。
- Evidence：`run-record.md#V7-07` 记录上述五个动态 ID、公共入口和两次失败前后
  task/package/case 快照；操作员附件记录两个 400 合同及路径，客户主叙事只展示中文失败
  含义；`wrong_case_created_count=1`、`wrong_source_created_count=1`、归档新增计数均为 0。
- 停止条件：任一错误回执产生归档、关闭任务或改变案件。
- 恢复：无需改数据；若有变更则停止并保留数据库副本作为缺陷证据。

### `V7-08` 归档有效归属回执并只关闭一个 OA 任务

- 操作：在 V7-06 已关联首次 OA package 的真实 `OA_OUT` 文书上，通过
  `POST /api/v1/documents/{first_oa_out_document_id}/attachments` 上传本轮 PDF，multipart
  角色均为 `ELECTRONIC_RECEIPT`，捕获 `valid_receipt_attachment_id`。随后：
  1. 调用 `POST /api/v1/official-work-packages/{first_oa_package_id}/oa-reply/refresh`，JSON body
     必须为 `{}`，符合 `OaReplyRefreshIn`；
  2. 逐项使用 `PATCH /api/v1/official-work-packages/{first_oa_package_id}/oa-reply/checklist/{item_code}`
     写入 `{"status":"DONE","evidence_note":"V7 现场人工核对"}`；`DONE` 是现有 OA package
     API/test 已验证的完成值，不使用自造枚举；
  3. 调用 `POST /api/v1/official-work-packages/{first_oa_package_id}/receipts`，使用与 V7-07
     相同的完整元数据结构和 `valid_receipt_attachment_id`，捕获 `valid_receipt_id`；
  4. 调用 `POST /api/v1/official-work-packages/{first_oa_package_id}/archive`，body 为 `{}`，
     捕获归档结果。
- 验证：归档事务成功；恰好一个对应 OA 任务关闭；工作包归档/关闭；通过案件公共读取入口
  捕获归档后实际 case status，并只按已验证的产品映射记录业务/法律含义。
- 四维状态：案件业务和法律状态记录归档后页面/API 的实际观察值，不预填未观察到的自动
  法律过渡；工作包/文件状态“已归档/已关闭”；费用不变。
- GAP：`RECEIPT`、`OA`。
- Evidence：记录 `first_oa_out_document_id`、`valid_receipt_attachment_id`、
  `valid_receipt_id`、关闭的唯一 task ID、archive response、归档前后任务计数，以及
  `GET /api/v1/tasks/{first_oa_task_id}`、
  `GET /api/v1/official-work-packages/{first_oa_package_id}/oa-reply` 和
  `GET /api/v1/cases/{main_case_id}` 的观察值；不得用口头状态替代响应/页面证据。
- 停止条件：零个或多个任务关闭、归档失败却发生部分变更、错误任务被关闭。
- 恢复：保持失败现场并停止；不得重复归档或手工关任务。

### `V7-09` 创建身份独立的后续 OA

- 操作：通过同一真实创建流程新增后续 OA，使用新的来源文书和完整 `CONFIRMED` 期限三元组，
  resolve 新 OA 工作包；捕获 `later_oa_source_id`、`later_oa_package_id`、`later_oa_task_id`，
  并证明三者均不同于首次 OA。随后创建只回复该来源的 `later_oa_out_document_id`，上传所需
  OA 答复附件及 `later_valid_receipt_attachment_id`，再按 V7-08 的 refresh、checklist、
  receipts、archive 四个公共入口完成该后续 OA 自己的有效回执闭环；refresh 同样发送 `{}`，
  每项 checklist 同样发送 `{"status":"DONE","evidence_note":"V7 现场人工核对"}`。
- 验证：第一组历史保持已归档；后续 OA 最初任务开放；使用自己的同案正确来源回执归档后，
  仅 `later_oa_task_id` 关闭，`later_oa_package_id` 已归档。进入 V7-10 前调用
  `GET /api/v1/cases/{main_case_id}` 并记录实际恢复后的 case status；若未恢复到产品观察到的
  OA 后稳定状态则停止，不得手工改状态或继续授权步骤。
- 四维状态：案件业务和法律状态只记录页面/API 实际观察值；新包按“已解析/待准备 → 待提交 →
  待回执 → 已归档/已关闭”推进，费用不变。不得把未观察到的提交、受理或法律过渡补进叙事。
- GAP：`OA`、`DEADLINE`。
- Evidence：两组 source/package/task identity 对照；后续 `OA_OUT`、答复附件、有效 receipt
  attachment/receipt、关闭的唯一 task、archive response 和归档后 case status；所有动态 ID
  写入 `run-record.md#V7-09`。
- 停止条件：后续 OA 复用旧任务/旧包或覆盖旧来源。
- 恢复：保留 identity 对照并停止，不得重写主键或 source key。

### `V7-10` 创建授权通知并证明无自动草单

- 操作：通过真实文书创建路径登记授权通知，填写明确日期、来源和 `CONFIRMED`；打开授权任务列表。
- 验证：生成来源关联、期限已确认的授权任务；创建后费用草单数量不增加。
- 四维状态：案件业务状态按授权任务页面的实际观察记录为“授权处理”；法律状态沿用 V7-09
  归档后观察值。只有另一个真实公共案件动作及其证据明确建立“已授权”时才可记录该法律状态，
  不得因创建授权通知或任务自动宣称法律状态推进；授权任务“来源已确认”，费用节点“待客户
  指示”，不得直接变成“已生成草单”。
- GAP：`GRANT`、`DEADLINE`。
- Evidence：授权来源/任务 lineage、期限三元组和草单前后计数。
- 停止条件：无来源、期限不完整或自动生成草单。
- 恢复：若任务未创建，核对真实授权事实和文书类型后重走创建；自动草单则停止。

### `V7-11` 替代授权来源与任务

- 操作：通过公开替代操作创建新的授权来源/任务，记录旧/新 lineage。
- 验证：新任务来源已确认；旧任务明确显示“已被替代”；案件只保留一个可操作的新任务。
- 四维状态：案件和法律状态不变；工作包/文件状态在授权任务维度由“来源已确认”分叉为
  旧任务“已被替代”和新任务“来源已确认”；费用仍“待客户指示”。
- GAP：`GRANT`。
- Evidence：旧/新 source/task 对照、替代原因、列表和详情截图。
- 停止条件：旧任务仍可操作、两个任务均可行动或新任务 lineage 不完整。
- 恢复：不得手工改旧状态；保留替代结果并停止。

### `V7-12` 旧任务 fail-closed 与新任务正常 PAY 草单路径

- 操作：对旧任务分别尝试直接草单、批量客户指示、通知生成和状态变更；再对新任务完成
  客户指示并走 PAY 草单路径。
- 验证：旧任务所有变更入口均被阻止且无副作用，UI 动作禁用/隐藏；新任务先从“待客户指示”
  进入 PAY，再生成一份正常草单。
- 四维状态：旧任务保持“已被替代”；新任务费用节点“待客户指示 → 已生成草单”，其他
  案件/法律状态不被旧任务操作影响。
- GAP：`GRANT`。
- Evidence：各旧任务门禁前后快照、禁用 UI、新任务指示/PAY/草单 ID。
- 停止条件：旧任务任一入口产生写入，或新任务绕过客户指示直接生成草单。
- 恢复：错误写入即停止并保留隔离数据库；不得删除副作用后继续演示。

### `V7-13` 仅执行 allowlist 最小 enrichment 支线

- 仓库机制审计：`FPMS_Automation_Skeleton_Pack/playwright_ts/package.json` 当前只有
  `demo:p1:v6:cleanup` 与 `demo:p1:v6:enrich`；其真实入口
  `FPMS_Automation_Skeleton_Pack/playwright_ts/src/support/pdP1LiveSeed.py` 只接受 V4/V5/V6
  variant。V6 enrichment 会创建递交包、OA、回执和授权任务等核心对象，违反 V7 allowlist，
  因而禁止运行，也不得改参数冒充 V7。
- 缺失前置：仓库尚无经过独立审查的 V7 enrichment 脚本/API，无法仅创建申请费、格式函和
  年费 fixture，也没有 dry-run 预览与准确创建/清理计数。Task 3 是文档任务，无权新增该机制。
- 操作：当前必须将 `V7-13` 标记为 BLOCKED，不执行任何 enrichment 命令；在单独原子任务
  提供并验证安全 V7 入口前，`V7-14` 和最终 READY 均为 BLOCKED。
- 验证：当前缺少入口，预期新增记录数为 0、执行 enrichment 命令数为 0；客户/案件固定事实、
  四维状态以及所有核心工作包/OA/回执/期限/授权 lineage 快照与 V7-12 结束时完全相同。
- 四维状态：案件业务状态、法律状态、工作包/文件状态和费用节点状态均保持 V7-12 的实际
  观察值，不展示任何假设存在的申请费、格式函或年费 fixture。
- Evidence：保存 `mechanism_audit` 输出（`v7_safe_entries=0`、`readiness=BLOCKED`）、
  `enrichment_command_executed=false`、`created_record_count=0`、四维状态前后对照和核心对象
  动态 ID/字段快照；不得提供或截图并不存在的新增记录。
- 停止条件：脚本触及 allowlist 外对象、覆盖客户/案件、创建核心 GAP 对象或使用通配符 cleanup。
- 恢复：立即停止脚本，保存日志和隔离数据库；不得继续客户演示。

### `V7-14` 汇总、非目标、Evidence 与 cleanup 交接

- 操作：按七项矩阵复核证据，展示四维生命周期摘要，明确非目标，交接演示后清理。
- 验证：14 个检查点均有结果；失败演示均有无变更证据；动态 ID 完整；核心路径无 mock、
  数据库注入或 enrichment。
- 四维状态：按真实公共行为已经建立的证据总结实际状态；若没有独立真实公共行为证明，案件
  业务状态和法律状态均保持 V7-12 的最后实际观察值，不得因 `V7-13` 或授权通知创建本身宣称
  “已授权”“年费监控”或“维持有效”。只有另有明确真实公共行为证据并写入运行记录时，才可
  展示相应推进。
  核心工作包历史应为“已归档/已关闭”且旧授权任务“已被替代”；本轮费用节点只展示 V7-12
  实际生成的授权草单，即“已生成草单”。由于 V7-13 为 BLOCKED 且创建记录数为 0，不得展示
  “已生成官费清单”“待缴费登记”或“已登记”。只有另设真实公共检查点并留下直接证据，才可
  在未来运行中记录后续费用节点；不得把列表、fixture 或口头说明当作缴费证据。
- Evidence：最终矩阵、运行记录、截图索引、命令结果、清理清单。
- 停止条件：任一核心证据缺失、残余不一致或清理范围不明确。
- 恢复：只允许回到最近一个有完整快照的检查点；不可凭口头补证。

## 7. 通用停止条件与恢复规则

### 7.1 必须立即停止

- 连接到生产、共享或未知数据库；
- 核心路径需要 route mock、数据库注入或 enrichment 才能继续；
- 401/403/5xx 无法通过正常账号、既有权限或服务恢复解决；
- 错案/错来源回执发生任何写入；
- OA_OUT 自动关闭任务，或有效回执未严格关闭一个任务；
- 期限三元组缺失、不一致、非 `CONFIRMED` 却仍生成可执行任务；
- 授权任务自动出草单，或“已被替代”任务仍可变更；
- enrichment 触及明确 allowlist 外记录；
- Evidence 中出现秘密、个人敏感数据或无法归属的对象。

### 7.2 恢复层级

1. 页面级：仅刷新一次或重新登录，记录恢复前后时间与结果。
2. 服务级：在确认独立数据库不变后重启本轮服务，重新健康检查。
3. 检查点级：仅从最近一个已完成快照重做当前检查点；不得跳过失败门禁。
4. 数据级：只允许对 V7 明确 allowlist 对象执行 cleanup 后从 `V7-01` 重来。
5. 缺陷级：若出现错误副作用、身份污染或核心 fail-closed 失效，封存数据库和日志并终止。

所有恢复必须写入 `recovery-log.md`：触发条件、操作者、动作、结果、是否影响先前证据。

## 8. Evidence 规范

### 8.1 目录结构

```text
artifacts/PD-P1-V7-DEMO-RUN-<时间戳>/
  run-record.md
  four-state-ledger.md
  checkpoint-matrix.md
  recovery-log.md
  cleanup-preview.txt
  cleanup-result.txt
  commands.jsonl
  outputs/
  screenshots/
  network/
  final-summary.md
```

### 8.2 每个检查点最小证据

- 检查点 ID、开始/结束时间、操作者、页面 URL；
- 输入摘要、动态对象 ID、可见结果和四维状态；
- 关键前后快照；失败门禁需记录“无变更”的计数/状态对比；
- 截图名称使用 `V7-xx-序号-中文说明.png`；
- 命令只记录可复现参数，不记录密码、token、Authorization header 或个人敏感信息；
- API 技术码只进入操作员附件，不作为客户讲解主文案；
- 每项结论必须指向具体文件，不得只写“已验证”。

### 8.3 成功判定

`checkpoint-matrix.md` 必须包含 `V7-01` 至 `V7-14`，每行状态只能是 PASS、FAIL 或 BLOCKED。
只有 14 行全部 PASS、七项 GAP 均有直接证据、四维状态自洽、核心路径禁止项为零，才允许进入
演示后清理和 READY 判定。

## 9. 演示后清理

1. 冻结并复制 Evidence 索引；证据日志先做秘密扫描，任何原始凭据命中均阻止关闭。
2. 从运行记录生成待清理预览，只包含 `PD-P1-V7-LIVE`、`P1E2E-V7-LIVE`、动态捕获从属 ID
   和 `V7-13` 的明确 allowlist 记录。
3. 人工复核预览；出现 V6、非 V7 客户/案件、通配符或未记录 ID 时拒绝执行。
4. 按依赖反序清理：费用/交接/年费支线 → 授权草单与替代任务 → 回执/OA_OUT/OA 包与任务 →
   递交包 → 文书 → 案件 → 联系人 → 客户。
5. 记录每类删除计数；再次查询固定客户代码、案号和动态 ID，预期均为零。
6. 保留隔离数据库文件直到证据审阅完成；通过后才删除本轮数据库和存储目录。
7. 不清理 V6 历史 Evidence，不修改 V6 文档。

### 9.1 当前可执行的隔离环境 cleanup

本仓库没有 V7 记录级删除脚本/API，因此不得在共享库尝试本节。仅在确认
`DATABASE_URL=sqlite:////tmp/fpms_p1_v7_<本轮ID>.db` 且 Evidence 已完成审阅后，停止两个
启动终端中的 uvicorn/Vite（`Ctrl-C`，预期各 rc=130），再从仓库根目录执行：

```bash
cd /Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic
set -euo pipefail
: "${FPMS_V7_RUN_ID:?FPMS_V7_RUN_ID must be non-empty before cleanup}"
: "${FPMS_V7_DB:?FPMS_V7_DB must be set before cleanup}"
: "${FPMS_V7_STORAGE:?FPMS_V7_STORAGE must be set before cleanup}"
printf '%s\n' "${FPMS_V7_DB}" "${FPMS_V7_DB}-wal" "${FPMS_V7_DB}-shm" "${FPMS_V7_STORAGE}"
test "${FPMS_V7_DB}" = "/tmp/fpms_p1_v7_${FPMS_V7_RUN_ID}.db"
test "${FPMS_V7_STORAGE}" = "/tmp/fpms_p1_v7_storage_${FPMS_V7_RUN_ID}"
python3 -c 'from pathlib import Path; import os; p=Path(os.environ["FPMS_V7_STORAGE"]); print("storage_file_count=" + str(sum(1 for x in p.rglob("*") if x.is_file())))'
python3 -c 'from pathlib import Path; import os,shutil; db=Path(os.environ["FPMS_V7_DB"]); [Path(str(db)+s).unlink(missing_ok=True) for s in ("","-wal","-shm")]; shutil.rmtree(Path(os.environ["FPMS_V7_STORAGE"]), ignore_errors=True)'
test ! -e "${FPMS_V7_DB}"
test ! -e "${FPMS_V7_DB}-wal"
test ! -e "${FPMS_V7_DB}-shm"
test ! -e "${FPMS_V7_STORAGE}"
```

预览命令必须先打印四个精确路径和 `storage_file_count`；不得出现通配符或其他路径。销毁及
四个末态断言预期 rc=0、剩余路径计数为 0。若路径断言失败，禁止执行 Python 删除命令。

## 10. READY 门禁与签字

只有以下各项全部满足，最终摘要才可写 `READY`：

- [ ] Preflight、权限和演示前 cleanup 全部通过；
- [ ] 固定 V7 数据名称完全一致，动态 ID 全部记录；
- [ ] `V7-01` 至 `V7-14` 全部 PASS；
- [ ] 七项 GAP 矩阵均有真实路径直接证据；
- [ ] 核心路径使用 route mock = 0、数据库注入 = 0、enrichment = 0；
- [ ] enrichment 仅命中申请费、格式函、年费明确 allowlist；
- [ ] 四维状态记录完整且没有用工作包准备冒充官方提交/法律状态推进；
- [ ] OA_OUT 保持任务开放；有效回执只关闭一个任务；后续 OA identity 独立；
- [ ] 所有期限为完整日期/source/`CONFIRMED` 且错误输入 fail-closed；
- [ ] 授权旧任务显示“已被替代”且不可变更，新任务走客户指示/PAY 草单路径；
- [ ] 当前费用终态为 V7-12 观察到的“已生成草单”；没有独立真实公共检查点时，不包含
      “已生成官费清单”“待缴费登记”或“已登记”；
- [ ] Evidence 无秘密且每项结论可追溯；
- [ ] 演示后清理仅命中 V7 allowlist，V6 与其他数据无变化。

当前仓库状态下，安全 V7 enrichment 入口缺失，`V7-13` 必须为 BLOCKED，因此本 runbook 的
READY 结论也是 BLOCKED。只有另一个明确授权的原子任务提供“仅申请费/格式函/年费”的 V7
入口、dry-run 精确预览、创建/清理计数、非核心对象保护和独立 evidence/task gate 后，才可
重新执行 `V7-13` 并解除 READY 阻塞。

签字：

| 角色 | 姓名 | 结论 | 时间 |
| --- | --- | --- | --- |
| Demo Operator | 待填写 | READY / NOT READY | 待填写 |
| QA Reviewer | 待填写 | READY / NOT READY | 待填写 |
| Business Owner | 待填写 | READY / NOT READY | 待填写 |

## 11. V6 冻结声明

V6 是历史执行证据，本任务不得修改以下文件：

- `docs/postdemo/postdemo_p1_lifecycle_demo_design_20260704.md`
- `docs/postdemo/postdemo_p1_lifecycle_demo_script_20260704.md`
- `docs/postdemo/postdemo_p1_v6_ui_e2e_success_runbook_20260705.md`

V7 不追写 V6 的现场结果、修复项或 residual risks。若 V7 执行发现新问题，只记录在本轮
Evidence 和 V7 后续原子任务中。
