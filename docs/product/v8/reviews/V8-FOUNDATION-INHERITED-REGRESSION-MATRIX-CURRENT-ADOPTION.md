# 独立复审：V8 Foundation 历史回归矩阵

- Review class: `PROTECTED`
- Candidate commits: `527f5179a5145d0749d659f005bc13f95097afa2`,
  `a0deb51b6556c881749dc2e7a6b0b206dafd6e5d`,
  `7439bcd18f13fb61887b784d39436147afc23a4b`
- Verdict: `APPROVED`
- P0/P1/P2: `0/0/0`

独立 High reviewer 审核了最终候选的合同、差异和当前测试。70 个 inherited task
各自只解析一次：66 个仍然有效的任务直接绑定其精确 tracked task contract 及该合同
声明的测试/spec 路径；4 个真正被替代的任务绑定明确的当前 successor。Tasks 01、
05–12 另有 literal path guard；Task46 明确绑定
`V8-LIFECYCLE-OVERLAY-REAL-UI-E2E-CURRENT-ADOPTION`、当前 live E2E 以及七领域
successor bundle；退役 taskctl gates 和历史 evidence sanitation 只绑定 C3 治理。

首轮 review 发现两个 P1：group-level 映射不能证明逐任务覆盖，document detail 测试
没有验证挂载后的应用路由。第二轮确认应用路由问题已修复，但仍指出 Tasks05–12 和
Task46 的映射不够精确。最终修正关闭了两项：每个仍有效任务从自己的合同解析精确
验证路径，只有确实 superseded 的任务使用 successor；应用层 OpenAPI 和本地 handler
同时证明 GET detail 无 request body。

Reviewer 独立重跑最终 focused contract，结果 `5 passed`；scoped Ruff 和
`git diff --check` 均通过。候选只修改测试，不改变产品行为，也没有削弱法律状态、
官费、期限、文书谱系、权限、schema 或 migration 断言。完整当前 V8 backend matrix
为 `4643 passed, 24 skipped, 114 subtests passed`；24 skips 仅来自被 C3 明确替代的
4 个旧 control-plane module。继承 UI 为 `22 passed`，当前 isolated real-stack
overlay E2E 为 `1 passed`。

最终十五个 story path 的 tree fingerprint 为
`5b056e16e92fe5ed7e6a33cc4b719cf404a9dde57a7e2e0863887dc2d34cbefc`。
