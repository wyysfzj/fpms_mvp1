# FPMS 自动化测试资产包（YAML/JSON + pytest + Playwright 骨架）

本包基于以下两份源文档生成：

- `docs/source/FPMS_SPEC_2_0.md`
- `docs/source/FPMS_SPEC2_0_Test_Cases_E2E.md`

## 1. 资产包内容

### 1.1 数据层
- `data/seeds/`：共享种子数据（用户、客户、申请人、模板、费率、提成规则、场景案卷、日期）
- `data/testcases/`：155 条详细用例，既提供 `all_testcases.*`，也按 wave 拆分
- `data/boundary/`：20 组参数化边界矩阵
- `data/coverage/`：FR 覆盖矩阵、规则覆盖矩阵
- `data/manifests/`：wave 清单、优先级索引、P0 smoke、full regression、引用归一化建议

### 1.2 自动化骨架
- `pytest_python/`：偏 API / Service / DB / 批处理 的 pytest 骨架
- `playwright_ts/`：偏 UI / 页面交互 / 文件导出 的 Playwright(TypeScript) 骨架

### 1.3 追溯与生成
- `scripts/validate_assets.py`：校验结构化资产是否与源 Markdown 一致
- `schemas/*.schema.json`：测试用例与边界数据的 JSON Schema

## 2. 当前覆盖统计

- 详细用例总数： **170**
- 边界矩阵总数： **20**
- Wave 数： **11**
- P0 数量： **79**
- P1 数量： **83**
- P2 数量： **8**

## 3. 推荐落地方式

### 3.1 给 Codex
1. 先读 `data/manifests/smoke_p0.yaml`
2. 再按 `wave_manifest.yaml` 顺序实现：
   `W0 -> A -> B -> C -> G0 -> D -> E -> F -> G -> H -> X`
3. 对每个 wave：
   - 先实现 `pytest_python/handlers/wave_*.py` 的服务层/数据库校验
   - 再实现 `playwright_ts/src/handlers/wave*.ts` 的 UI 路径
4. 所有动态唯一值统一走 `RUN_ID`

### 3.2 给人工测试
- 直接查看 `data/testcases/by_wave/*.yaml`
- 逐条执行 `preconditions -> steps_summary -> expected`
- 遇到“警告 vs 阻断”差异时，记录当前环境参数

### 3.3 给自动化同事
- pytest 适合：规则校验、任务/费用/账单/提成计算、数据库断言
- Playwright 适合：表单、向导、权限、导出、附件、打印流

## 4. 已知数据引用差异
见 `data/manifests/reference_resolution.yaml`：
- `DS-CN`：建议统一归一化为 `DS-CTY-CN`
- `DS-BIO-UNIT-001`：需要在目标环境补一个菌种保藏单位种子

## 5. 运行示例

### pytest
```bash
cd pytest_python
pip install -r requirements.txt
pytest -m p0
pytest tests/test_wave_a.py -m "p0 and happy"
pytest tests/test_boundary_matrix.py
```

### Playwright
```bash
cd playwright_ts
npm install
npx playwright test
npx playwright test --grep "@P0"
npx playwright test src/tests/wave-a.case-creation.spec.ts
```
