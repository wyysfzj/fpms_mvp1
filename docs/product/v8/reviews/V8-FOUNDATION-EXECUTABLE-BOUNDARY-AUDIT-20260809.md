# V8 Foundation 可执行边界审计（2026-08-09）

## 结论

Row274 已完成产品实现、修正、独立 High 复审和当前账本绑定。Foundation 当前共有
`182 CURRENT_VERIFIED + 10 SUPERSEDED_BY_STORY = 192/197` 行获得当前验收；剩余五行
都不再具有可安全执行的独立 lane：两个根权限缺口和三个传递依赖项。

这不是测试失败、工具格式、scope 性能或普通代码缺陷。继续伪造数据、放宽断言或在
现有 allowlist 中吸收产品修复都会削弱官费或生命周期 fail-closed。

## 根阻塞一：授权年费从 REVIEW_REQUIRED 到 MATCHED 的权威动作缺失

- 直接受影响：`FPMS-V8-GRANT-DRAFT-OBLIGATION-ADAPTER-20260712-01`（Row120）。
- 已验收的授权当年年费投影保存 `official_full_amount=None`、
  `difference_review_state=REVIEW_REQUIRED`，并禁止从费率表或减缴比例反推金额。
- 已验收的通用草单 writer 只接受 `MATCHED`，否则 409/no-write。
- Row120 同时要求保持前述投影并调用通用 writer；两者在当前合法持久状态中无法同时
  成立。

需要的最小权威决定仍是：由哪个受控动作、基于哪个来源、记录哪些操作者/金额/谱系
事实，将该行从 `REVIEW_REQUIRED` 转为 `MATCHED`。不得由实现默认通知书金额已复核，
不得绕过通用 writer。

该根传递阻塞 Foundation regression matrix（Row279）以及 Foundation close（Row280）。
详细先前证据见
`docs/product/v8/reviews/V8-FOUNDATION-ROOT-AUTHORITY-BLOCKERS-20260809.md`。

## 根阻塞二：live fixture 所需 warning/conflict 没有产品投影合同

- 直接受影响：`FPMS-V8-LIVE-FIXTURE-20260712-01`（Row275）。
- 传递受影响：`FPMS-V8-LIFECYCLE-OVERLAY-REAL-UI-E2E-20260712-01`（Row276）和
  Foundation close（Row280）。

现有后端 `backend/app/modules/cases/lifecycle_overlay_service.py` 在组装
`LifecycleOverlay` 时把顶层 `warnings`、`legacy_conflicts` 固定为 `()`，并在每个
milestone 上把 `warnings` 固定为 `()`。因此 Row275 仅拥有 seed/test 文件的 allowlist，
无法让任务要求的 unverified、legacy conflict 和 reference-only warning 通过真实 overlay
被观察到。

更关键的是，`append_case_activity` 接受并返回 `conflict_codes`，但
`CaseActivityEvent` 没有冲突码字段，canonical `payload_json` 也不写入这些代码。当前没有
可供 overlay 稳定读取的 durable conflict lineage。把测试专用键塞进 payload、直接构造
DTO、mock overlay 或只断言原始数据库行，都不满足 Row275/276 的真实路径合同。

### 必须先冻结的最小后继产品合同

1. 决定冲突码的 durable carrier：明确使用现有权威事实还是新增 schema/migration；禁止
   从自由文本或测试 payload 猜测。
2. 精确定义 `confirmation_status`、持久冲突、unresolved decision gate 以及
   `HISTORICAL`/`INTERNAL_ONLY` 到 milestone/top-level warning 和 legacy-conflict DTO 的
   映射、代码、中文消息、来源对象与顺序/去重规则。
3. 由新的独立产品 task 拥有 service、必要 carrier/migration 和 focused tests；Row275
   保持 seed-only，不吸收产品行为。
4. 产品 task terminal adoption 后，Row275 才创建至少 401 个活动，以现有 `limit=200`
   形成真实三页；随后 Row276 运行 real login/API/Vite/SQLite 路径。

Row275/276 的 JSON stdout、凭据变量和 lock ownership 可以按本地标准由 High 做机械冻结：
seed 输出确定性 JSON；外层 scheduler 预留串行队列但不创建 lockdir；seed 是文件系统
lockdir 的唯一 owner，session 关闭后在 `finally` 释放。它们不是切换 Ultra 的理由。
真正需要高风险冻结的是上述 warning/conflict persistence 与投影语义。

## 当前停止边界

Foundation 的五个未验收行是 Row120、275、276、279、280。所有其余 Foundation 行均已
验收。Full/Final/Release 不能越过 Foundation close；客户 decision-gate lanes 也不得被
猜测激活。因此当前没有另一个合法、依赖就绪且文件无冲突的产品 lane。

恢复时只需处理两个根：先冻结并实现 warning/conflict 后继产品合同，再完成 Row275/276；
并取得授权年费 `REVIEW_REQUIRED -> MATCHED` 的客户/来源决定后完成 Row120。之后串行执行
Row279、Row280，再进入 eligible Full、Final 和最后 release close。不得重做已验收的
192 行或 Row274 的 RED/GREEN。

## 2026-08-10 durable update

第二个根已由 `V8-OVERLAY-WARNING-CONFLICT-LINEAGE-CURRENT-ADOPTION` 关闭。Delta-31 carrier、
迁移、持久化 replay 校验和真实 overlay warning/conflict 投影均已获得独立 PROTECTED 验收，
因此 Row275 已恢复为 dependency-ready `PENDING`。Row276 继续只依赖 Row275。第一个根
（Row120 的授权年费人工复核权威动作）没有被本后继故事推断或改变，仍保持
`AUTHORITY_BLOCKED`。
