你现在要把 `FPMS_Automation_Skeleton_Pack` 的一批 skeleton 用例落地为**可运行的 pytest 自动化**。

## 本次范围

只实现以下 wave 和 testcase：

- Wave: `<WAVE>`
- Testcase IDs:
  - `<CASE_ID_1>`
  - `<CASE_ID_2>`
  - `<CASE_ID_3>`
  - `<CASE_ID_4>`

请不要扩到其他 wave。

## 必须阅读的文件

### 测试资产
- `FPMS_Automation_Skeleton_Pack/docs/source/FPMS_SPEC_2_0.md`
- `FPMS_Automation_Skeleton_Pack/docs/source/FPMS_SPEC2_0_Test_Cases_E2E.md`
- `FPMS_Automation_Skeleton_Pack/data/manifests/wave_manifest.yaml`
- `FPMS_Automation_Skeleton_Pack/data/manifests/reference_resolution.yaml`
- `FPMS_Automation_Skeleton_Pack/data/testcases/by_wave/<wave-lower>.yaml`
- `FPMS_Automation_Skeleton_Pack/data/seeds/*.yaml`
- `FPMS_Automation_Skeleton_Pack/pytest_python/framework/*.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/handlers/wave_<wave-lower>.py`
- `FPMS_Automation_Skeleton_Pack/pytest_python/tests/test_wave_<wave-lower>.py`

### 真实项目代码
请定位并阅读与这些用例直接相关的：
- endpoint / controller / service
- ORM / repository / SQL
- 鉴权与登录
- 数据模型 / 枚举 / 状态机

## 你的任务

1. 只在必要范围内补全：
   - `framework/api_client.py`
   - `framework/db_assert.py`
   - `framework/helpers.py`（只有确有必要时）
   - 对应 `handlers/wave_<wave-lower>.py`
2. 只去掉**本次已真正实现** handler 的 `@skeleton_case`
3. 保持所有 testcase id、handler 名称、router 映射不变
4. 对每条用例补足：
   - Arrange
   - Act
   - Assert
   - API 断言
   - DB 断言（若 `db_dsn` 可用）
5. 所有动态唯一值统一使用 `runtime.run_id`
6. 对环境差异（warning vs blocking）不要硬写死成单一路径；请做成：
   - 可配置判断
   - 或代码中显式注释该环境差异

## 验收要求

完成后请运行并确保以下命令尽可能通过：

```bash
cd FPMS_Automation_Skeleton_Pack
python3 scripts/validate_assets.py

cd pytest_python
pytest tests/test_asset_integrity.py -q
pytest tests/test_wave_<wave-lower>.py -q
```

## 输出格式

完成后请输出：

1. 已修改文件列表
2. 已实现 testcase id 列表
3. 每条 testcase 对应的主要断言点
4. 仍未解决的 blocker
5. 你运行过的命令及结果摘要

## 严格禁止

- 不要改 testcase id
- 不要批量去掉未实现 handler 的 skeleton 标记
- 不要把断言替换成 `assert True`
- 不要为了通过而修改 YAML/JSON 资产
