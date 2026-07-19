# FPMS 年费费率候选来源与 canary 收口最小纠偏设计

**状态：R3 已批准（独立设计与计划复审均为 APPROVE，P0/P1/P2 = 0）**

**适用任务：**
`FPMS-V8-DE-PREPARE-OA-REPLY-SEAM-20260712-01`、
`REPO-GOVERNANCE-FAST-CLOSE-CUTOVER-20260719-01`、
`REPO-CNIPA-ANNUITY-SOURCE-AUTHORITY-ACTIVATION-20260719-01` 和
`FPMS-V8-CNIPA-ANNUITY-RATE-CANDIDATE-20260715-01`

**用户决定：** 2026-07-19 提供 `/Users/cfcc/Downloads/CNIIPA.pdf`；在 R2
证明原顺序不可执行后，明确批准把 fast-close current-v2 canary 更换为
`FPMS-V8-DE-PREPARE-OA-REPLY-SEAM-20260712-01`。不新增兼容任务，不削弱来源、
费用、基线、独立复审或激活的 fail-closed 规则。

## 0. R2 控制结论

R2 复审确认本文件当前第 3 节所写“ordinary HIGH task 直接修改 live
`docs/agents/source-authority.md`，再由在途任务 governance-adopt”的路径在
current-v2 中不可执行，后文该路径不得启动：

1. live governance bytes 已由当前 activation terminal receipt 绑定；
2. 直接修改 `source-authority.md` 会先报
   `active governance differs from reviewed activation PASS`；
3. 因此不会生成 `governance_change.json`，也不满足 `governance-adopt` 前置条件；
4. 把 live index 延后到 fast-close 之后又违反 `GOV-SOURCE-001`，并与
   “fast-close 等当前 annuity canary PASS”形成闭环。

不改 evidence state、不重捕 baseline、也不创建 compatibility task 的最小可执行
重排是：

1. 以已经在 current-v2 下实施到最后回归修正阶段的
   `FPMS-V8-DE-PREPARE-OA-REPLY-SEAM-20260712-01` 替换 fast-close shadow canary；
2. OA task terminal PASS 后，完成并激活现有 fast-close 动态治理能力；
3. 在新治理下执行一个独立 HIGH source-authority activation task，原子安装本设计
   审过的 live index 和 manifest/digest；
4. 所有 non-PASS selected consumers 按各自 change report adoption；然后恢复原
   annuity candidate task，保留其 task ID、baseline 和历史无效 RED。

用户已明确批准该重排。R3 独立复审通过并提交前，不得 materialize 新的
source-authority activation task；OA canary 只可按自己已经冻结的合同继续。

OA 只读诊断随后确认一个只影响该 canary 的冻结合同冲突：当前
`DocumentEvidenceDerivation` 与新建 child `DocumentEvidenceVersion` 之间没有 ORM
relationship，且 Session 使用 `autoflush=False`；把两个 pending object 同批交给
一次 `flush` 时，UOW 没有对象级依赖边，实际先写 derivation，child FK 必然失败。
`actor_id` 不是 FK，case 和 parent 已存在，所以不能把该错误归因于 fixture 或
actor。R3 因此还必须对 Delta-7 fresh-write 的“一次 flush”机械步骤作最窄
latest-wins 纠偏；不改变任何 OA 业务、谱系、replay 或 caller-owned transaction
语义。

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
5. 用户提供文件的原始 bytes 已冻结为：
   - byte size：`2478214`；
   - pages：`32`；
   - lowercase SHA-256：
     `3792384f32e782c96e5630a6ac42892d8b8cd272a219a7d674ceebf16ec7cdce`；
   - 本地取得时间（UTC 秒级）：
     `2026-07-19T03:55:57Z`；
   - PDF creation/modification：
     `2026-03-30 16:00:48 CST`；
6. 上述 hash/time 逐字节写入 canonical data、source snapshot、测试和任务合同，不允许
   占位符、镜像文件、文本抽取 hash、旧 31 页文件 hash 或实现时网络访问；
7. task-local 来源复审记录官方文章、exact PDF URL、字节数、页数、SHA-256、
   `retrieved_at` 和三个年费表。产品 materializer/test 均保持离线确定性。

精确 canonical snapshot bytes 为：

```text
{"schema_version":"CNIPA_RATE_SOURCE_V1","sources":[{"content_sha256":"3792384f32e782c96e5630a6ac42892d8b8cd272a219a7d674ceebf16ec7cdce","document_no":null,"published_on":"2026-03-30","retrieved_at":"2026-07-19T03:55:57Z","title":"专利和集成电路布图设计缴费服务指南","url":"https://www.cnipa.gov.cn/module/download/down.jsp?i_ID=205552&colID=1518"}]}
```

其 lowercase SHA-256 为
`e8599a13429e3f536312eaeed0ec1a09b5f91533caacf2d8514dbeef1533d544`。

若 exact 官方 PDF 无法取得，任务保持 `BLOCKED`；不得用第三方镜像、商业网页、
客户文件或相同费率值替代来源字节。

## 3. 合同传播边界

本设计是只覆盖 Delta-4 `D4-10` annuity candidate 来源身份的 latest-wins
增量。原 Delta-4 文件保持不可变历史，其 SHA-256 必须继续为
`7c2a8c5947136be8434ba963616473c39158f25cbd2abb4a8fae23f0f6a4fff8`；不能为了
修正一个来源 URL 而破坏其他已经按该 hash 冻结的任务。

取得并冻结 provenance 后，严格按以下串行、无环顺序传播：

1. **OA current-v2 canary。**
   `FPMS-V8-DE-PREPARE-OA-REPLY-SEAM-20260712-01` 保留原 task ID、三路径
   allowlist、legacy-adopt baseline、有效 RED、已有实现和失败回归证据；只修复其
   Delta-7 exact closure 内的剩余问题并在 unchanged current-v2 下独立收口。
   它不读取或修改年费来源。该 task-file 必须追加 latest-wins 技术纠偏，只
   supersede Delta-7 fresh creation 第 4 步及 task-file 中相同的 “before one
   flush” 字样：
   - 完成所有验证并确认 fresh/source derivation set 为空后，先
     `transaction.add(version)`，再执行一次仅针对该 child 的
     `transaction.flush([version])`；
   - child 已取得同一事务内的数据库 FK identity 后，才设置 package reply link、
     构造并 add derivation，再执行一次最终 `transaction.flush()`；
   - 两次 flush 必须在同一个 caller-owned transaction 内，seam 仍不得 commit、
     rollback、写 activity 或捕获并伪装失败；caller rollback 必须同时移除 version、
     package link 和 derivation；
   - replay 路径仍是零写入，其他 Delta-7 validation/cardinality/snapshot/replay
     字节全部不变。
   测试必须先把单次 flush 断言改为精确两次有序 flush，并以当前 FK failure
   记录一个新的 review-finding RED，再做上述最小 service 修改。不得用 Core
   直写绕开 ORM、动态修改 mapper、扩张 models allowlist 或拆成两个 transaction。
2. **fast-close activation。**
   `REPO-GOVERNANCE-FAST-CLOSE-CUTOVER-20260719-01` 在自己的 task-file allowlist
   内追加本 R3 latest-wins overlay：shadow canary 改为上述 OA task；候选 manifest
   的 expanded-acceptance task IDs 必须包含
   `REPO-CNIPA-ANNUITY-SOURCE-AUTHORITY-ACTIVATION-20260719-01`。OA terminal PASS
   后才可继续 fast-close RED/GREEN、独立复审、shadow 和原子激活。
3. **独立 source-authority activation。**
   fast-close terminal activation 后，materialize 一个新的 HIGH governance
   activation task：
   `REPO-CNIPA-ANNUITY-SOURCE-AUTHORITY-ACTIVATION-20260719-01`。它不是
   compatibility task，只拥有其 task file、`docs/agents/source-authority.md`、
   `docs/agents/manifest.json`、一份 focused source-contract unittest 和自己的
   artifact tree。它使用已激活的 dynamic activation authority，在 candidate
   中绑定本设计的 exact 来源事实、manifest/digest 和独立复审，最后原子安装 live
   index；不能先直接修改 live governance。
4. **in-flight adoption。**
   source activation terminal PASS 后，所有仍为 non-PASS 且选择了
   `source-authority.md` 的 consumer 分别生成自己的 `governance_change.json`，
   取得独立 approval，再由各自 controller adoption。预计 OA 和 fast-close 此时已
   terminal；现有 annuity task 必须保持原 task ID、四路径 allowlist、完整 baseline
   和历史 evidence prefix。任何其他实际 non-PASS selected consumer 也按同一规则
   处理，不能按设计时名单遗漏。
5. **恢复 annuity candidate。**
   原 annuity task 只在自己的现有 allowlist 内更新 Frozen Authority、Exact Data
   Contract、canonical JSON、实现和定向测试，并明确本设计只对 Delta-4 `D4-10`
   来源身份 latest-wins。原无效 missing-test RED 保留历史，不重跑或改写；首个真实
   行为 RED 使用已存在的 test path。

共享文件和 SQLite-writing 验证全部串行。任何步骤要求改动另一个任务的 source、
test、task、baseline 或 evidence state 时，只暂停受影响步骤并返回 Ultra；不得
创建 compatibility task、直接编辑 state 或重捕 baseline。

## 4. 拒绝的方案

- **继续使用 31 页直链：** 会把旧字节误标为 2026-03-30 当前版，拒绝。
- **只因年费金额相同而忽略来源差异：** 破坏来源谱系和后续激活审计，拒绝。
- **改用第三方镜像或客户资料：** 不能成为 `source_authority=CNIPA`，拒绝。
- **继续把 annuity 当 fast-close canary：** 会形成 live source index 与
  fast-close activation 的依赖环；用户已批准改用 OA current-v2 canary。
- **新增兼容任务：** 不修复来源事实且违反 fast-close 简化目标，拒绝。
- **直接改写 Delta-4：** 会破坏大量任务锁定的
  `7c2a8c…` 权威 hash；改用本设计对 D4-10 来源身份作窄范围 latest-wins
  覆盖。
- **在 current-v2 直接改 live source index：** activation receipt 会在生成
  adoption report 前拒绝；必须使用 fast-close 激活后的 dynamic activation。
- **把 source index 延后到 annuity candidate 之后：** 违反 `GOV-SOURCE-001`，
  且不能以 task-local candidate bytes 代替 live index。
- **为保留“一次 flush”改用 Core INSERT 或运行时 mapper 注入：** 改变现有 ORM
  persistence seam 或引入全局 mapper 副作用，且没有优于同一事务两次有序 flush
  的法律、谱系或原子性收益，拒绝。
- **扩张到 `models.py` 增加 relationship：** 超出 OA task 的冻结 allowlist，
  也把一个局部写入顺序问题扩大为共享模型变更，拒绝。
- **用两个 transaction 消除 FK：** 破坏 caller rollback 对三项 carrier 的原子
  删除，拒绝。

## 5. 验收

修正完成前必须同时满足：

- exact 32 页官方 PDF 已从固定 URL 取得，真实 byte hash/time 已冻结；
- task、数据、snapshot、测试和来源索引没有 31/32 页或 URL/hash/date 冲突；
- Delta-4 原文件 hash 仍为
  `7c2a8c5947136be8434ba963616473c39158f25cbd2abb4a8fae23f0f6a4fff8`，
  本设计只 supersede D4-10 来源身份；
- 三个年费档位与官方附件表一致，其他费用事实未被本任务吸收；
- OA current-v2 canary 以原 task/allowlist/baseline terminal PASS，且 fast-close
  task 的 shadow/canary binding 已改为该 terminal bundle；
- OA fresh path 使用同一 caller-owned transaction 中精确两次有序 flush，先
  child version、后 package link + derivation；没有内部 commit/rollback/activity，
  caller rollback 仍同时删除三项 carrier；
- fast-close 动态治理 terminal activation 在 source-authority activation 之前；
- 独立 source-authority activation 原子安装 reviewed live index 和新 manifest/
  digest，且所有实际 non-PASS selected consumers 完成 task-local adoption；
- 原 annuity task 的 task ID、allowlist、baseline 和已有 evidence prefix 未重写；
- targeted RED/GREEN、离线 provenance/strict parser/replay/transaction tests 通过；
- independent source/domain review 为 `APPROVED`, `P0: 0`, `P1: 0`, `P2: 0`；
- current-v2 scope、task gate、atomic evidence 和 close 全部通过；
- fast-close shadow/activation 仍在 canary terminal PASS 之后。
