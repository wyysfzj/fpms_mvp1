# pytest 骨架说明

该目录适合放置：
- API / Service 自动化
- DB 断言
- 规则校验与批处理逻辑
- 与 UI 无关或 UI 价值较低的复杂业务测试

## 目录
- `framework/`：运行时、数据加载、router、API/DB 占位层
- `handlers/`：每个用例的实现入口；目前全部带 `@skeleton_case`
- `tests/`：按 wave 的 pytest 参数化入口

## 实现约定
1. 在 `handlers/wave_*.py` 中逐个去掉 `@skeleton_case`
2. 使用 `runtime.run_id` 注入动态唯一值
3. 优先实现 `P0` + 主干 happy path
4. 对 DB 断言，补全 `framework/db_assert.py`

## 建议先实现的文件
- `handlers/wave_w0.py`
- `handlers/wave_a.py`
- `handlers/wave_b.py`
- `handlers/wave_g0.py`
- `handlers/wave_d.py`
