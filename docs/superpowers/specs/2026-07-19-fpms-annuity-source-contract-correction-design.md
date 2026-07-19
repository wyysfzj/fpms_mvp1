# FPMS 年费费率候选来源合同最小纠偏设计

**状态：待独立复审**

**适用任务：**
`FPMS-V8-CNIPA-ANNUITY-RATE-CANDIDATE-20260715-01`

**用户决定：** 2026-07-19 批准对同一 canary 做最小来源纠偏；不更换 canary，
不新增兼容任务，不削弱来源、费用或激活的 fail-closed 规则。

## 1. 已确认的问题

原 Delta-4 和任务合同把
`https://www.cnipa.gov.cn/attach/0/b2d5a31081404b83a36c0df1ebe591e7.pdf`
称为 2026-03-30 版缴费服务指南，但该直链当前返回 31 页文件；CNIPA
2026-03-30 官方文章
`https://www.cnipa.gov.cn/art/2026/3/30/art_1518_205552.html`
所链接的官方下载文件为 32 页，并包含旧直链没有的专利权期限补偿收费等内容。
两个文件虽然给出的三类专利年费档位相同，但不是同一来源字节，不能共享
发布日期、版本身份或 `content_sha256`。

原任务还要求精确 PDF 字节 SHA-256 和真实 UTC `retrieved_at`，却没有冻结这两个
值，同时禁止实现时猜测或联网取值。因此任务不能按原合同继续。

## 2. 采用的最小修正

保留原 task ID、rate-book code、三个 fee code、费率档位、inactive candidate
边界、TDD、独立复审和 current-v2 close 流程。只修正来源身份：

1. 元数据权威页固定为
   `https://www.cnipa.gov.cn/art/2026/3/30/art_1518_205552.html`；
2. PDF 来源固定为该文章实际链接的
   `https://www.cnipa.gov.cn/module/download/down.jsp?i_ID=205552&colID=1518`；
3. `source_reference`、唯一 snapshot source 的 `url` 和数据文件中的 PDF URL
   都使用上述 exact PDF URL；
4. `source_published_on`、`version_code`、`source_version` 和 `effective_from`
   继续为 `2026-03-30`，其含义仅是采用该日官方页面所发布的 reviewed
   snapshot，不推断更早历史效力；
5. 从 exact PDF URL 取得的原始响应 bytes 在本地计算 lowercase SHA-256；
   `retrieved_at` 记录该次成功取得的真实 UTC 秒级时间并以 `Z` 结尾；
6. 两个值逐字节写入 canonical data、source snapshot、测试和任务合同，不允许
   占位符、镜像文件、文本抽取 hash、旧 31 页文件 hash 或实现时网络访问；
7. task-local 来源复审记录官方文章、exact PDF URL、字节数、页数、SHA-256、
   `retrieved_at` 和三个年费表。产品 materializer/test 均保持离线确定性。

若 exact 官方 PDF 无法取得，任务保持 `BLOCKED`；不得用第三方镜像、商业网页、
客户文件或相同费率值替代来源字节。

## 3. 合同传播边界

取得并冻结 provenance 后，只对以下现有合同做同一事实的最小传播：

- 当前设计增量；
- 原 Delta-4 中该 annuity candidate 的来源 URL 说明；
- annuity candidate task 的 Frozen Authority、Exact Data Contract 和测试要求；
- `docs/agents/source-authority.md` 中该指南的索引 URL；
- canary canonical JSON、实现和定向测试。

不改变 fast-close 设计、治理 task ID、canary task ID 或执行顺序。治理 task
仍须在 canary current-v2 terminal PASS 后才能进行 shadow/activation。已启动的
canary 与治理任务都保留原 baseline；任何合同传播必须作为各自允许且可归属的
变更，不能重捕获或吸收 baseline。

如果现有 allowlist/基线协议不能安全表示上述来源传播，只暂停 canary 和
fast-close activation，返回 Ultra 重新决定；不得创建 compatibility task 或
直接修改 evidence state。

## 4. 拒绝的方案

- **继续使用 31 页直链：** 会把旧字节误标为 2026-03-30 当前版，拒绝。
- **只因年费金额相同而忽略来源差异：** 破坏来源谱系和后续激活审计，拒绝。
- **改用第三方镜像或客户资料：** 不能成为 `source_authority=CNIPA`，拒绝。
- **更换 canary：** 会改变已批准 fast-close 身份、计划和治理任务基线，拒绝。
- **新增兼容任务：** 不修复来源事实且违反 fast-close 简化目标，拒绝。

## 5. 验收

修正完成前必须同时满足：

- exact 32 页官方 PDF 已从固定 URL 取得，真实 byte hash/time 已冻结；
- task、数据、snapshot、测试和来源索引没有 31/32 页或 URL/hash/date 冲突；
- 三个年费档位与官方附件表一致，其他费用事实未被本任务吸收；
- targeted RED/GREEN、离线 provenance/strict parser/replay/transaction tests 通过；
- independent source/domain review 为 `APPROVED`, `P0: 0`, `P1: 0`, `P2: 0`；
- current-v2 scope、task gate、atomic evidence 和 close 全部通过；
- fast-close shadow/activation 仍在 canary terminal PASS 之后。
