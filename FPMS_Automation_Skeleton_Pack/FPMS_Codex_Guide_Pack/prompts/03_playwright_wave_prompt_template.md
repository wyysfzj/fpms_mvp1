你现在要把 `FPMS_Automation_Skeleton_Pack` 的一批 skeleton 用例落地为**可运行的 Playwright UI 自动化**。

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
- `FPMS_Automation_Skeleton_Pack/data/testcases/by_wave/<wave-lower>.yaml`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/support/*.ts`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/pages/*.ts`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/handlers/wave<Wave>.ts`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/*.spec.ts`

### 真实项目代码
请定位并阅读：
- 登录页面
- 对应业务页面
- 路由
- 表单组件
- 表格 / 弹窗 / toast / 上传 / 导出组件

## 你的任务

1. 只在必要范围内补全：
   - `src/pages/*.ts`
   - `src/fixtures/fpms.fixtures.ts`
   - 对应 `src/handlers/wave<Wave>.ts`
2. selector 统一收敛到 page object 或 helper
3. 只去掉**本次已实现** handler 的 `markSkeleton(...)`
4. 所有动态唯一值统一使用 `process.env.FPMS_RUN_ID`
5. 优先实现：
   - UI 主路径
   - 表单校验
   - toast / dialog 断言
   - 列表可检索性
   - 导出 / 上传 / 打印前端链路
6. 需要时调用 API / DB fixture 做辅助校验，但不要把 UI 用例完全退化成纯 API 测试

## 验收要求

完成后请运行并确保以下命令尽可能通过：

```bash
cd FPMS_Automation_Skeleton_Pack/playwright_ts
npx playwright test src/tests/asset-integrity.spec.ts
npx playwright test src/tests/wave-<wave-lower>.spec.ts
```

> 注意：请根据实际文件名替换命令中的 spec 路径。

## 输出格式

完成后请输出：

1. 已修改文件列表
2. 已实现 testcase id 列表
3. 每条 testcase 的关键 UI 断言点
4. 尚未解决的 UI blocker（例如 selector 不稳定、上传控件特殊、导出文件名不稳定）
5. 你运行过的命令及结果摘要

## 严格禁止

- 不要改 testcase id
- 不要把 selector 散落在 handler 中
- 不要批量去掉未实现 handler 的 skeleton 标记
- 不要为通过测试而弱化成无意义断言
