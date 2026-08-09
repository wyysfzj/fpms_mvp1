# V8 Foundation 根权限阻塞核验（2026-08-09）

## 当前结论

Row277 PayList 真实 UI 边界已经完成产品提交、真实浏览器验证、独立 High 复审和
coverage-ledger 绑定。C3 checker 的共享文件 successor 证明缺陷、同 commit 长短
SHA 别名缺陷、七个旧 fingerprint 抄录值和 source-registry 当前 owner 也已完成
最小修正与独立验收。

当前 Foundation 为 `174/197`，剩余 `23` 行。依赖图中只有下面两个未完成根；其余
21 行全部是它们的下游。没有第三条可安全执行的独立产品 lane。

## 根一：Row120 授权费草单条件合同矛盾

- Catalog ID：`FPMS-V8-GRANT-DRAFT-OBLIGATION-ADAPTER-20260712-01`。
- 已批准 Row120 合同要求完整复核 Row130 授权当年年费投影，然后原样调用通用
  `prepare_draft`。
- 已验收 Row130 明确把通知书中的每条年费保存为：
  `official_full_amount=None`、`difference_review_state=REVIEW_REQUIRED`，且禁止从
  rate book 或减缴比例推导完整官费。
- 已验收通用草单 writer 明确只接受
  `difference_review_state=MATCHED`；否则以存储状态冲突 fail closed。

因此，当前合同同时要求“保持 Row130 的 REVIEW_REQUIRED 精确投影”和“成功进入只
接受 MATCHED 的 writer”，在任何合法持久状态下都无法同时成立。直接把
REVIEW_REQUIRED 当 MATCHED、反推完整官费、绕过通用 writer 或伪造人工复核都会
削弱官费 fail-closed，均不获授权。

需要冻结的唯一业务决定是：授权通知书金额经过哪一个受控动作、依据什么来源，
才能从 `REVIEW_REQUIRED` 变为 `MATCHED`。推荐保持通用 writer 不变，新增或指定
一个独立人工核对/更正事实（含操作者、来源、前后金额和谱系），Row120 只能在该
事实存在后起草。若客户认为经独立复核的官方通知金额本身即可直接起草，也必须
明确它如何形成 MATCHED，不能由实现猜测。

该根单独阻塞 Row120、Row279 和 Row280。

## 根二：Row253 旧状态导入缺少反向映射权限

- Catalog ID：`FPMS-V8-LEGACY-LIFECYCLE-IMPORT-20260712-01`。
- 设计只冻结了“已确认三轴 → 兼容 Case.status”的单向映射，并明确新业务不得从
  旧 `Case.status` 反推法律事实。
- 迁移章节允许一次性 `LEGACY_IMPORT/LEGACY_UNVERIFIED`，并明确旧 `GRANTED`
  绝不能自动成为 `PATENT_IN_FORCE`，但没有冻结每一个旧状态到业务阶段、官方
  阶段和法律状态的反向矩阵。
- 现有 preflight 只能分类已有三轴与旧状态是否一致；它不能提供缺失的反向业务
  权限。

因此实现不能自行决定 `PENDING/OA1/OA2/GRANT_PENDING/REJECTED/...` 应导入哪些
三轴，也不能把旧终局状态当作已确认法律事实。需要客户/业务负责人批准逐状态
矩阵：可导入的三轴、必须保持 `UNKNOWN` 的字段、冲突分类，以及明确不导入的
状态。推荐默认保持旧 `Case.status` 不变、法律状态为 `UNKNOWN`、核验状态为
`LEGACY_UNVERIFIED`；任何更具体的程序/法律轴只按批准矩阵写入。

该根阻塞 Row253、257、258、260–276、279 和 280，共 22 行；与根一在 279/280
重叠。两根合并恰好覆盖全部剩余 23 行。

## 恢复条件

只需提供并批准两项最小权威输入：

1. 授权通知年费行从 `REVIEW_REQUIRED` 到 `MATCHED` 的受控来源/动作合同；
2. 旧 `Case.status` 到三轴 `LEGACY_UNVERIFIED` 导入的逐状态矩阵。

收到后可继续 High：先分别实现 Row120、Row253，随后 Row253 下游 overlay/UI 可按
依赖链持续推进；不需要重新分析已完成的 174 行，也不需要切换 Ultra。
