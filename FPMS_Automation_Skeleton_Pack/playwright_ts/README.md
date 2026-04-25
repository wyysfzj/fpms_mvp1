# Playwright(TypeScript) 骨架说明

该目录适合放置：
- UI 页面流测试
- 向导、批处理、模板导出、附件上传下载
- 权限可见性、按钮可操作性、报表导出 smoke
- 文件输出与打印前端链路

## 目录
- `src/fixtures/`：统一 fixture
- `src/pages/`：Page Object 占位
- `src/handlers/`：每条用例的 UI 实现入口
- `src/tests/`：按 wave 的 spec 入口
- `src/support/`：数据加载、annotations、router

## 落地建议
1. 先实现 `waveW0.ts` 中的权限/配置 smoke
2. 再实现 `waveA.ts`、`waveB.ts`、`waveG0.ts`、`waveD.ts`
3. 选择器补在 page object 中，不要散落在 handler
4. 所有导出文件都应带 snapshot 或内容断言
