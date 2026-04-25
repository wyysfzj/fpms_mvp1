你现在在一个真实业务仓库根目录工作，目录中包含 `FPMS_Automation_Skeleton_Pack/`，它是一套已经结构化好的 FPMS 自动化测试资产包。

你的目标不是重新设计测试，而是**把 skeleton pack 落地到真实系统**，逐步变成可运行的 pytest + Playwright 自动化。

## 一、先阅读这些文件

### 业务规格与测试源
- `FPMS_Automation_Skeleton_Pack/docs/source/FPMS_SPEC_2_0.md`
- `FPMS_Automation_Skeleton_Pack/docs/source/FPMS_SPEC2_0_Test_Cases_E2E.md`

### 编排与数据
- `FPMS_Automation_Skeleton_Pack/README.md`
- `FPMS_Automation_Skeleton_Pack/data/manifests/smoke_p0.yaml`
- `FPMS_Automation_Skeleton_Pack/data/manifests/wave_manifest.yaml`
- `FPMS_Automation_Skeleton_Pack/data/manifests/reference_resolution.yaml`
- `FPMS_Automation_Skeleton_Pack/data/testcases/by_wave/*.yaml`
- `FPMS_Automation_Skeleton_Pack/data/boundary/boundary_matrix.yaml`
- `FPMS_Automation_Skeleton_Pack/data/seeds/*.yaml`

### pytest 骨架
- `FPMS_Automation_Skeleton_Pack/pytest_python/framework/*.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/handlers/*.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/*.py`

### Playwright 骨架
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/support/*.ts`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/pages/*.ts`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/handlers/*.ts`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/*.spec.ts`

### 真实项目代码
请自行定位并阅读：
- 登录 / 鉴权
- 案卷维护
- 中间文件
- 时限
- 费用
- 账单 / 收款 / 催款 / 坏账
- 报表 / 查询
- 数据库访问层
- 前端页面 / 路由 / 组件

## 二、实施原则

1. structured YAML / JSON / schema 是 source of truth，不要随意改
2. testcase id / boundary id / wave manifest 不得重命名
3. 只去掉已实现 handler 的 skeleton 标记
4. 所有动态唯一值统一使用 `FPMS_RUN_ID`
5. pytest 负责 API / service / DB / 规则校验 / 批处理
6. Playwright 负责 UI 流程 / 权限 / 上传下载 / 导出打印
7. selector 收敛到 page object，不要散落在 handler
8. 对 warning vs blocking 差异要显式处理，不要写成脆弱断言
9. 优先最小修改、可验证、可审查的实现

## 三、工作顺序

请严格按以下顺序工作：

### Phase 0：分析，不改代码
输出：
- 真实模块映射表
- 真实 API / DB / 页面 / 路由映射
- 风险清单
- 首批建议实现范围

### Phase 1：先做最小可运行闭环
只实现：
- `W0` 的 P0
- `A` 的 P0 主链路

优先 pytest，再补 Playwright。

### Phase 2：跑验证命令
至少运行：
```bash
cd FPMS_Automation_Skeleton_Pack
python3 scripts/validate_assets.py
```

```bash
cd FPMS_Automation_Skeleton_Pack/pytest_python
pytest tests/test_asset_integrity.py -q
```

```bash
cd FPMS_Automation_Skeleton_Pack/playwright_ts
npx playwright test src/tests/asset-integrity.spec.ts
```

### Phase 3：再告诉我是否继续扩到 B / G0 / D

## 四、这次先做的具体目标

本轮只做：

- `TC-W0-001`
- `TC-W0-007`
- `TC-W0-010`
- `TC-W0-014`
- `TC-A-001`
- `TC-A-003`
- `TC-A-005`
- `TC-A-006`
- `TC-A-008`

你可以在分析后判断是否再追加 `TC-A-010`、`TC-A-011`、`TC-A-012`，但不要超出 A wave。

## 五、输出要求

请按以下格式输出：

1. 你确认阅读过的关键文件
2. 真实代码映射关系
3. 计划修改文件清单
4. 风险与 blocker
5. 已实施内容
6. 已运行命令与结果
7. 尚未完成但建议下一步继续做的 testcase ids

## 六、严格禁止

- 不要一次性扩到全部 155 条
- 不要改 structured data 让测试“看起来通过”
- 不要批量移除 skeleton 标记
- 不要把断言改成空断言或恒真断言
- 不要大面积重构业务代码
