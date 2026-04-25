# FPMS Skeleton Pack 在 Codex 中的落地指南

## 0. 目标

本指南面向你当前这套资产：

- `FPMS_Automation_Skeleton_Pack/`
- `FPMS SPEC 2.0`
- `FPMS_SPEC2_0_Test_Cases_E2E.md`

目标不是“让 Codex 自己猜业务”，而是让 Codex把这套结构化测试资产逐步落地成**可运行的自动化测试**：

- `pytest_python/`：偏 API / Service / DB / 批处理
- `playwright_ts/`：偏 UI / 页面流 / 上传下载 / 导出打印

---

## 1. 我建议的目录摆放

### 推荐方案：先保留 pack 为独立目录

把 zip 直接解压到你的项目根目录，先不要拆平。这样 pack 内的相对路径最稳定，也最适合第一轮让 Codex 落地。

```text
<repo-root>/
  FPMS_Automation_Skeleton_Pack/
    docs/source/
      FPMS_SPEC_2_0.md
      FPMS_SPEC2_0_Test_Cases_E2E.md
    data/
    pytest_python/
    playwright_ts/
    schemas/
    scripts/
  <your actual backend/frontend code...>
```

### 为什么先不要拆平

当前骨架代码默认假设以下目录是同级关系：

- `FPMS_Automation_Skeleton_Pack/data/`
- `FPMS_Automation_Skeleton_Pack/pytest_python/`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/`

先保留这个结构，Codex 更容易直接工作。

---

## 2. 先做一次“静态自检”

先不要急着让 Codex 改代码，先确认 pack 本身无损。

### 2.1 结构化资产校验

```bash
cd <repo-root>/FPMS_Automation_Skeleton_Pack
python3 scripts/validate_assets.py
```

预期：
- 输出 `Asset validation passed.`
- 统计为 `Cases: 155 | Boundary: 20 | Waves: 11`

### 2.2 pytest 骨架校验

```bash
cd <repo-root>/FPMS_Automation_Skeleton_Pack/pytest_python
cp .env.example .env
pip install -r requirements.txt
pytest tests/test_asset_integrity.py -q
```

预期：
- 资产完整性测试通过
- 绝大多数 wave 用例还会 `skip`，这是正常现象，因为当前 handler 仍是 skeleton

### 2.3 Playwright 骨架校验

```bash
cd <repo-root>/FPMS_Automation_Skeleton_Pack/playwright_ts
cp .env.example .env
npm install
npx playwright install
npx playwright test src/tests/asset-integrity.spec.ts
```

预期：
- asset-integrity 通过
- 业务 spec 大多仍会跳过或不具备真实实现，这也是正常现象

---

## 3. 在 Codex 中应该怎么开工

## 3.1 优先使用什么模式

对于这类多文档、多目录、跨前后端和数据库的任务，不建议一上来就让 Codex“全量实现 155 条”。

更稳的做法：

1. 先让 Codex做**理解与规划**
2. 再让它按 **wave / stage / priority** 分批实现
3. 每次只落一个可验证的小闭环

### 我建议的第一批

按 pack 自带顺序，首批先做：

- `W0`
- `A`
- `B`
- `G0`
- `D`

但真正第一次交给 Codex 时，再缩成：

- `W0 P0`
- `A P0` 中最主干的几条

---

## 4. skeleton pack 中，哪些文件是 Codex 的核心上下文

第一次给 Codex 时，至少要把这些文件加入上下文：

### 4.1 业务规格与测试来源

- `FPMS_Automation_Skeleton_Pack/docs/source/FPMS_SPEC_2_0.md`
- `FPMS_Automation_Skeleton_Pack/docs/source/FPMS_SPEC2_0_Test_Cases_E2E.md`

### 4.2 测试编排入口

- `FPMS_Automation_Skeleton_Pack/README.md`
- `FPMS_Automation_Skeleton_Pack/data/manifests/smoke_p0.yaml`
- `FPMS_Automation_Skeleton_Pack/data/manifests/wave_manifest.yaml`
- `FPMS_Automation_Skeleton_Pack/data/manifests/reference_resolution.yaml`

### 4.3 结构化测试数据

- `FPMS_Automation_Skeleton_Pack/data/testcases/by_wave/*.yaml`
- `FPMS_Automation_Skeleton_Pack/data/boundary/boundary_matrix.yaml`
- `FPMS_Automation_Skeleton_Pack/data/seeds/*.yaml`

### 4.4 pytest 骨架

- `FPMS_Automation_Skeleton_Pack/pytest_python/framework/router.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/framework/data_loader.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/framework/api_client.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/framework/db_assert.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_*.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_wave_*.py`

### 4.5 Playwright 骨架

- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/support/router.ts`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/support/dataLoader.ts`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/fixtures/fpms.fixtures.ts`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/pages/*.ts`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/handlers/wave*.ts`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/*.spec.ts`



## 4.7 wave 与文件名的对应关系

| Wave | pytest 测试入口 | pytest handler | Playwright spec | Playwright handler |
|---|---|---|---|---|
| W0 | `pytest_python/tests/test_wave_w0.py` | `pytest_python/handlers/wave_w0.py` | `playwright_ts/src/tests/wave-w0.setup.spec.ts` | `playwright_ts/src/handlers/waveW0.ts` |
| A | `pytest_python/tests/test_wave_a.py` | `pytest_python/handlers/wave_a.py` | `playwright_ts/src/tests/wave-a.case-creation.spec.ts` | `playwright_ts/src/handlers/waveA.ts` |
| B | `pytest_python/tests/test_wave_b.py` | `pytest_python/handlers/wave_b.py` | `playwright_ts/src/tests/wave-b.oa.spec.ts` | `playwright_ts/src/handlers/waveB.ts` |
| C | `pytest_python/tests/test_wave_c.py` | `pytest_python/handlers/wave_c.py` | `playwright_ts/src/tests/wave-c.pct-national.spec.ts` | `playwright_ts/src/handlers/waveC.ts` |
| G0 | `pytest_python/tests/test_wave_g0.py` | `pytest_python/handlers/wave_g0.py` | `playwright_ts/src/tests/wave-g0.grant.spec.ts` | `playwright_ts/src/handlers/waveG0.ts` |
| D | `pytest_python/tests/test_wave_d.py` | `pytest_python/handlers/wave_d.py` | `playwright_ts/src/tests/wave-d.annuity.spec.ts` | `playwright_ts/src/handlers/waveD.ts` |
| E | `pytest_python/tests/test_wave_e.py` | `pytest_python/handlers/wave_e.py` | `playwright_ts/src/tests/wave-e.invalid-litigation.spec.ts` | `playwright_ts/src/handlers/waveE.ts` |
| F | `pytest_python/tests/test_wave_f.py` | `pytest_python/handlers/wave_f.py` | `playwright_ts/src/tests/wave-f.prepayment.spec.ts` | `playwright_ts/src/handlers/waveF.ts` |
| G | `pytest_python/tests/test_wave_g.py` | `pytest_python/handlers/wave_g.py` | `playwright_ts/src/tests/wave-g.dunning-bad-debt.spec.ts` | `playwright_ts/src/handlers/waveG.ts` |
| H | `pytest_python/tests/test_wave_h.py` | `pytest_python/handlers/wave_h.py` | `playwright_ts/src/tests/wave-h.consulting-search.spec.ts` | `playwright_ts/src/handlers/waveH.ts` |
| X | `pytest_python/tests/test_wave_x.py` | `pytest_python/handlers/wave_x.py` | `playwright_ts/src/tests/wave-x.search-report-audit.spec.ts` | `playwright_ts/src/handlers/waveX.ts` |
| Boundary | `pytest_python/tests/test_boundary_matrix.py` | `pytest_python/handlers/boundary.py` | `playwright_ts/src/tests/boundary.matrix.spec.ts` | `playwright_ts/src/handlers/boundary.ts` |


### 4.6 真实项目代码

然后再补进你真实项目中的这些模块：

- 登录与鉴权
- 案卷维护
- 中间文件
- 时限
- 费用
- 账单 / 收款 / 预收 / 坏账
- 报表 / 查询
- 数据访问层 / ORM / SQL
- 路由与页面组件

---

## 5. 让 Codex 实施时，必须固定的约束

以下约束非常重要，建议直接写进 prompt 或 `AGENTS.md`：

1. **不要改测试用例 ID**
   - 例如 `TC-A-001`、`BND-003` 绝不能被重命名

2. **不要改 manifest 编排**
   - `smoke_p0.yaml`
   - `wave_manifest.yaml`
   - `priority_index.yaml`

3. **不要删 structured data**
   - YAML / JSON / schema 保持为 source of truth

4. **只去掉已实现 handler 的 skeleton 标记**
   - pytest：`@skeleton_case`
   - Playwright：`markSkeleton(...)`

5. **动态唯一值统一走 `RUN_ID`**
   - Python: `runtime.run_id`
   - TS: `process.env.FPMS_RUN_ID`

6. **Page selector 只能放在 page object 或统一 helper**
   - 不要把 selector 散落在 handler 里

7. **warning / blocking 的环境差异要可配置**
   - 不要写死成只接受一种 UI 文案或一种后端行为

8. **优先最小修改**
   - 先让测试能跑起来，再考虑抽象

9. **业务源码尽量少改**
   - 首轮重点是补自动化适配层，不是大规模重构业务系统

---

## 6. 第一轮最推荐的落地顺序

## Phase 1：建立“可执行骨架”

### pytest 先做
优先补这些点：

- `framework/api_client.py`
  - 封装真实 endpoint
- `framework/db_assert.py`
  - 接真实数据库 client
- 登录 / token / session 准备
- 新案、文档、任务、费用、账单常用断言 helper

### Playwright 再做
优先补这些点：

- `LoginPage.ts`
- `CasePage.ts`
- `DocumentPage.ts`
- `TaskPage.ts`
- `FeePage.ts`
- 通用 toast / dialog / table / upload helper

---

## Phase 2：按业务主干实现 smoke

优先顺序：

1. `W0`
2. `A`
3. `B`
4. `G0`
5. `D`

再扩到：

6. `C`
7. `E`
8. `F`
9. `G`
10. `H`
11. `X`
12. `Boundary`

---

## 7. 一个很重要的策略：不要把 155 条一次性交给 Codex

对 Codex 最稳的粒度是：

- 一次 1 个 wave
- 或一次 1 个 stage
- 或一次 5～15 条紧密相关用例

### 好粒度示例

- `A1 新案立案` 一组
- `A2 批量递交 + 申请费任务` 一组
- `B OA 来文 + 答复任务 + 回复核销` 一组

### 不好的粒度示例

- “请把整个 FPMS pack 全部实现并跑通”
- “请一次性完成 pytest + playwright 全量 155 条”

---

## 8. 建议你在仓库里补一个 AGENTS.md

建议放两个层级：

### 8.1 repo 根目录 `AGENTS.md`
放全仓共识：

- 不改生产逻辑的边界
- 依赖安装原则
- 运行测试和 lint 的统一命令
- 安全限制

### 8.2 `FPMS_Automation_Skeleton_Pack/AGENTS.md`
放自动化专项规则：

- 用 structured YAML 作为 source of truth
- 保持 handler / data / manifest 映射
- 实现顺序
- RUN_ID 规则
- DB 断言策略
- warning vs blocking 处理方式

本 guide 包里已经附了一个 `AGENTS.md.example`。

---

## 9. 我建议你对 Codex 下达任务时使用的工作流

## Step 1：先让 Codex做“理解，不改代码”

目标：
- 找到业务路由
- 找到 API
- 找到数据库表
- 找到 selector
- 判断 pack 与现网代码差距

使用：
- `prompts/01_bootstrap_analysis_prompt.md`

## Step 2：先实现 pytest 的一个小闭环

目标：
- 先落服务层 / API / DB 断言
- 优先把“主流程”跑通

使用：
- `prompts/02_pytest_wave_prompt_template.md`

## Step 3：再实现 Playwright UI 主路径

目标：
- 表单填写
- 按钮权限
- 导出 / 上传 / 打印链路
- 页面 smoke

使用：
- `prompts/03_playwright_wave_prompt_template.md`

## Step 4：失败后不要让它“重写一切”

目标：
- 让 Codex基于失败日志做最小修复
- 只修当前失败点

使用：
- `prompts/04_debug_fix_prompt.md`

---

## 10. 第一轮最推荐的具体任务

这是我建议你真正交给 Codex 的第一批：

### 10.1 先做 W0
目的：
- 登录
- 权限
- 模板 / 参数 / 基础配置 smoke
- 证明自动化环境已可用

### 10.2 再做 A 波中的 A1 + A2 主干
重点：
- 新案最小必填
- CaseNo 唯一
- 涉外必填
- 申请人规则
- 日期一致性
- 限制修改视图
- 批量递交
- 申请费任务 / 草单 / 账单 / 收款 主链路

### 10.3 然后做 B
重点：
- OA 通知
- 答复时限
- ReplyTo 核销
- OA 中间费 / 账单 / 收款

---

## 11. 你可以直接复制给 Codex 的使用习惯

每次给 Codex 的 prompt，最好都包含这 5 块：

1. **任务范围**
   - 只做哪个 wave / 哪些 case id

2. **必须阅读的文件**
   - spec + e2e + manifests + handlers + 真实代码路径

3. **改动约束**
   - 不改 ids / 不删 data / 只去掉已实现 skeleton

4. **验收命令**
   - pytest / playwright / asset validation

5. **输出格式**
   - 改了哪些文件
   - 覆盖了哪些 case
   - 还有哪些 blocker

---

## 12. 首轮验收标准

当你让 Codex 完成一批实现后，至少检查：

### 12.1 结构未被破坏
```bash
cd <repo-root>/FPMS_Automation_Skeleton_Pack
python3 scripts/validate_assets.py
```

### 12.2 pytest 可跑
```bash
cd <repo-root>/FPMS_Automation_Skeleton_Pack/pytest_python
pytest tests/test_asset_integrity.py -q
pytest tests/test_wave_w0.py -q
pytest tests/test_wave_a.py -m p0 -q
```

### 12.3 Playwright 可跑
```bash
cd <repo-root>/FPMS_Automation_Skeleton_Pack/playwright_ts
npx playwright test src/tests/wave-w0.setup.spec.ts
npx playwright test src/tests/wave-a.case-creation.spec.ts --grep @P0
```

### 12.4 只实现了应实现的 handler
检查：
- 目标 handler 的 skeleton 标记被移除
- 非目标 handler 仍保持 skeleton
- 没出现“为了通过测试，把整个 router 改成无条件 pass”的投机写法

---

## 13. 常见坑

### 坑 1：让 Codex 直接实现全部 wave
结果通常是：
- prompt 太散
- 它会误改结构
- selector / endpoint / db 适配不稳定

### 坑 2：没有把 spec 和 by_wave yaml 一起给它
结果通常是：
- 它只看 handler 注释，忽略更完整上下文

### 坑 3：没要求它先输出映射关系
结果通常是：
- 它直接开始写代码，但根本没找对真实模块

### 坑 4：没有限制“只去掉已实现的 skeleton”
结果通常是：
- 它可能批量去掉 skeleton 标记，但实际没写断言

### 坑 5：没有统一 RUN_ID
结果通常是：
- 重跑时数据冲突
- CaseNo / BillNo / PaymentNo 重复

---

## 14. 我的最终建议

真正执行时，按下面这个节奏最稳：

1. 先把 pack 解压到 repo 根目录
2. 补 `AGENTS.md`
3. 用 Codex 先做 repo 分析，不改代码
4. 让它先落 `W0`
5. 再落 `A` 的 P0 主链路
6. 先把 pytest 跑通，再补 Playwright
7. 每一小批都单独验证
8. 失败时只做最小修复，不推倒重来
