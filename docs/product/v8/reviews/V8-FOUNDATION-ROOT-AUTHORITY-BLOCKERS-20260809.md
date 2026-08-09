# V8 Foundation 根权限阻塞核验（2026-08-09）

## 当前结论

Row277 PayList 真实 UI 边界已经完成产品提交、真实浏览器验证、独立 High 复审和
coverage-ledger 绑定。C3 checker 的共享文件 successor 证明缺陷、同 commit 长短
SHA 别名缺陷、七个旧 fingerprint 抄录值和 source-registry 当前 owner 也已完成
最小修正与独立验收。

Row253 已依据不反推合同完成实现、回归和独立 High 复审。当前 Foundation 为
`175/197`，剩余 `22` 行；Row253 下游从权限阻塞转为正常依赖链，可继续执行。

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

## 已解除：Row253 不需要反向映射权限

- Catalog ID：`FPMS-V8-LEGACY-LIFECYCLE-IMPORT-20260712-01`。
- 已冻结的最小合法解释不建立反向矩阵：保留每个已知旧 `Case.status`，业务阶段
  和官方阶段均为空，法律状态仅为 `UNKNOWN`，核验状态为
  `LEGACY_UNVERIFIED`。
- `GRANTED` 与所有其他旧字符串一样，不形成已确认法律事实；部分投影、历史冲突、
  evidence 漂移或非法载体均不写入并明确报告。
- 产品范围 `61cd23c..c8396aa` 经独立 High 复审 P0/P1/P2 `0/0/0`，101 项 focused
  与受影响回归通过。

因此 Row253 不再是权限根；Row257 及 overlay/UI 后续链可以按现有依赖继续。

## 恢复条件

当前只剩一项最小权威输入：

1. 授权通知年费行从 `REVIEW_REQUIRED` 到 `MATCHED` 的受控来源/动作合同。

该输入只阻塞 Row120、279 和 280。Row257 起的其余依赖链继续由 High 执行；不
需要重新分析已完成的 175 行，也不需要切换 Ultra。
