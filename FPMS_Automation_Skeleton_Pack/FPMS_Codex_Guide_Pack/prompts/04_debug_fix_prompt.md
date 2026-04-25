下面是我刚刚运行自动化后的失败结果。请基于**最小修改原则**修复，不要重构无关模块。

## 失败输出
<PASTE_FAILURE_LOG_HERE>

## 本次只允许修改

- `FPMS_Automation_Skeleton_Pack/pytest_python/**`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/**`
- 与失败直接相关的少量测试适配层文件

除非失败明确证明业务源码本身有 bug，否则不要改业务源码。

## 你的任务

1. 先分析失败根因，分成：
   - 测试数据问题
   - selector 问题
   - API endpoint 封装问题
   - DB 断言问题
   - 环境差异问题
   - 真实产品 bug
2. 只修当前失败链路
3. 保持 testcase id / manifest / yaml 资产不变
4. 不要顺手大改别的 wave
5. 修复后运行最小必要命令重试

## 输出格式

1. 根因判断
2. 修改文件列表
3. 具体修复点
4. 重跑命令
5. 仍然存在的 blocker
