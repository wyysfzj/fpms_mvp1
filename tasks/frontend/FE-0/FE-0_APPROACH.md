# Phase FE‑0：Bootstrapping & Standards — Approach (FPMS MVP1 Frontend)

## 目标
FE‑0 的目标是把前端仓库从“可运行雏形”提升到 **可持续迭代的工程基线**，并为后续 FE‑1/FE‑2 的业务页面开发提供统一标准：

1) **可构建**：`dev/build` 可稳定运行（Vite 入口齐全）。  
2) **可验证**：每个原子任务都能跑 `lint/typecheck/build` 并产出 Evidence Log。  
3) **可对接后端**：统一 HTTP client（JWT 注入、错误 envelope 归一化、request_id 捕获）。  
4) **可控会话**：token 持久化、启动恢复、路由守卫（未登录不可进入受保护页面）。  
5) **可复用规范**：后续页面必须复用同一套 API client / 错误结构 / 分页类型。

---

## 核心原则（AI‑EOS）
- **Atomic**：一个任务 = 一个 PR 级别改动，完成即可合并；不跨任务扩 scope。  
- **Evidence-first**：必须运行并记录 `lint/typecheck/build`（以及必要的手工 smoke）。  
- **Gated execution**：如果质量门禁失败，先修门禁再谈功能。  
- **No speculation**：不做“看起来可能需要”的后续建议；只交付当前任务定义的范围。  
- **Stop on mismatch**：遇到 endpoint mismatch / CORS / auth 返回结构不同 → 停止并提出“最小修复任务”。

---

## FE‑0 的任务拆分
FE‑0 分为两个原子任务（按顺序执行）：

### FE‑0‑00（前置阻塞清理 + 门禁）
**为什么先做它**：如果项目无法 build 或没有 lint/typecheck 门禁，就无法满足后续每个任务“可证据化”的要求。

交付：
- 补齐 Vite 入口（`index.html`）
- 补齐 TS/Vite 类型声明（`vite-env.d.ts` + tsconfig types）
- 增加 `lint` 与 `typecheck` scripts
- 最小 ESLint 配置（不引入重型格式化链路；只做质量门禁）
- Evidence Log

### FE‑0‑01（Auth + API client + Guard 闭环）
交付：
- Axios client：baseURL 配置、Bearer token 注入、错误 envelope 归一化、request_id 捕获
- Pinia auth store：login/logout、token 持久化与启动恢复
- Router guard：未登录跳转 login；登录后访问 login 自动跳 dashboard
- 一个受保护页面（Dashboard）调用受保护接口做 smoke（如 GET /clients?page=1&page_size=1）
- Evidence Log + curl 对照验证步骤

---

## 一致性规范（FE‑0 形成后必须全局遵守）
- env：`VITE_API_BASE_URL` 必须是完整 API 前缀（包含 `/api/v1`）
- token key：统一使用 `fpms_token`（localStorage）
- error：统一归一化为 `ApiError { status, code, message, details, requestId }`
- pagination：统一 `{ items, page, page_size, total }`
- 401：清 token + 触发全局回登录（避免循环跳转）

---

## 输出物要求（每个任务都必须交付）
- 代码变更（严格遵守 file allowlist）
- 可复现的命令清单
- Evidence Log（建议写入 `./task/frontend/FE-0/`，文件名含 task id）
