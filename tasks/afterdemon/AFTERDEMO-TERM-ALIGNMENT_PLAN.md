# AFTERDEMO_TERM_ALIGNMENT_PLAN — 后 Demo 术语与页面语义整改方案

**Type**: Doc change  
**Priority**: P0  
**Date**: 2026-03-08

## Goal

基于当前项目实现、原始系统用户手册 `docs/TXX.pdf`、以及现有产品/测试文档，冻结一套更符合中国专利代理/知识产权事务所使用习惯，同时兼顾业务含义与演示友好性的术语标准，并拆分为后续可逐个批准执行的原子任务。

本文件是 planning-only runbook。  
本次执行不改产品代码，不直接改 UI 文案。  
后续每次执行必须严格按 `AGENTS.md` 只实现本文件中的 **一个** 原子任务。

## Investigation Scope

本次调查覆盖以下证据来源：

- 原始手册：
  - `docs/TXX.pdf`
- 当前业务/测试文档：
  - `docs/demo2.md`
  - `docs/FPMS_Frontend_Manual_Test_User_Guide.md`
  - `docs/FPMS SPEC 2.0.md`
- 当前前端实现：
  - `frontend/src/constants/labels.zh.ts`
  - `frontend/src/constants/menu.ts`
  - `frontend/src/modules/cases/pages/CaseDetail.vue`
  - `frontend/src/modules/cases/components/CaseClaimsTab.vue`
  - `frontend/src/modules/cases/components/CaseDocumentsTab.vue`
  - `frontend/src/modules/cases/components/CaseReceiptsSummary.vue`
  - `frontend/src/modules/documents/pages/DocumentList.vue`
  - `frontend/src/modules/documents/pages/DocumentCreate.vue`

## Confirmed Findings

### Problem A — 关键页签存在“名称与实际内容对象不一致”

- 当前案件详情页 tabs 定义为：
  - `概览`
  - `权利要求`
  - `官方文件`
  - `费用`
  - `账单`
  - `任务`
- 代码位置：
  - `frontend/src/constants/labels.zh.ts`
  - `frontend/src/modules/cases/pages/CaseDetail.vue`

其中最严重的错位是：

- `权利要求` 页签实际展示的是“申请人 + 发明人”，不是权利要求文本或权项结构
- 代码位置：
  - `frontend/src/modules/cases/components/CaseClaimsTab.vue`

这不是简单“叫法不同”，而是业务对象命名错误，会直接削弱专业用户对系统可信度的判断。

### Problem B — “官方文件 / 公文记录 / 中间文件” 三套口径并存

- 案件详情页签标签是 `官方文件`
- 页内面板标题是 `公文记录`
- 顶层模块实际又是独立 `文档管理`
- 原始手册 `docs/TXX.pdf` 的正式模块名称是 `中间文件管理`
- 原始手册在流程图里同时使用 `官方文件`

这说明当前项目把：

- 老事务所习惯口径：`中间文件`
- 对客户更直白的业务口径：`官方文件`
- 通用软件口径：`公文/文档`

混在了一起，但没有建立层级关系。

### Problem C — “账单 / 账务 / 收款摘要” 语义边界未冻结

- 案件详情页签名称是 `账单`
- 页内组件展示的是：
  - 累计开票
  - 累计回款
  - 未结清
  - 账单列表
- 但空态文案写成 `暂无账务信息`
- 代码位置：
  - `frontend/src/modules/cases/components/CaseReceiptsSummary.vue`

按当前实现，它还不是完整“账务台账”，更接近：

- 案件维度账单摘要
- 收款概览
- 账单列表

所以继续混用 `账务` 容易让业务方误解为已经具备完整个案财务台账能力。

### Problem D — 文档口径已经相互打架

- `docs/FPMS_Frontend_Manual_Test_User_Guide.md` 记录当前 UI 为：
  - `概览/权利要求/官方文件/费用/账单/任务`
- `docs/demo2.md` 又写成：
  - `概览/公文记录/费用/账务/任务`
- 这导致当前存在三层不一致：
  - UI 页面
  - 演示脚本
  - 原始系统业务口径

### Problem E — 顶层模块命名也缺少统一策略

- 菜单当前使用：
  - `案件管理`
  - `文档管理`
  - `费用草稿`
  - `账单管理`
  - `回款与核销`
  - `任务与期限`
- 代码位置：
  - `frontend/src/constants/menu.ts`

而原始手册长期沉淀的行业口径更接近：

- `案卷维护`
- `中间文件管理`
- `时限管理`
- `费用管理`
- `账单管理`

当前菜单并非错误，但缺少“哪些地方偏演示友好、哪些地方偏行业专业”的统一产品策略。

## Domain Judgment

结合中国专利代理事务所常见操作口径、老牌代理系统惯例、以及管理层/演示场景理解成本，本项目建议采用“两层术语策略”：

### Layer 1 — UI 短标签

用于页面页签、菜单、按钮，要求短、清楚、业务上不误导：

- `概览`
- `申请人/发明人`
- `往来文件`
- `费用`
- `账单与收款`
- `任务`

### Layer 2 — 文档/说明型标签

用于演示脚本、帮助文档、实施方案，允许兼顾业务含义：

- `中间文件与往来管理`
- `往来文件（原公文记录）`
- `账单与收款（含收款摘要）`
- `申请人/发明人（当前页签内容）`

### Long-term Professional Direction

若未来产品明确面向资深流程人员、追求更强行业专业性，可逐步强化以下领域术语：

- `案件`
- `中间文件`
- `时限`
- `费用草单`
- `账单`
- `收款/冲销`

其中：

- `案件` 继续作为主业务对象名，不回退为顶层主显示词 `案卷`
- `中间文件` 作为领域规范词保留在规格、任务、实施说明中
- 前端展示层可保留更易懂的 `往来文件`

`案卷` 仅保留为旧系统兼容术语，不再作为新版主显示词。

## Naming Freeze Recommendation

建议先冻结以下标准，作为后续整改统一依据：

### Case Detail Tabs

- `概览`
- `申请人/发明人`
- `往来文件`
- `费用`
- `账单与收款`
- `任务`

### Explanatory Copy

- `往来文件（原公文记录）`
- `账单与收款（含收款摘要）`
- `中间文件与往来管理` 作为领域/规格级表述

### Keep As-Is for Now

- 顶层菜单 `案件管理`
- 顶层菜单 `账单管理`
- 顶层菜单 `回款与核销`
- 顶层菜单 `任务与期限`

### Do Not Use in New UI Copy

- `权利要求` 作为申请人/发明人页签名
- `账务` 作为当前案件详情账单摘要页签名
- `公文记录` 作为案件详情主页签名
- `案卷` 作为新版主 UI 的案件对象名

## Six-Agent Team Execution

- Lead / Main thread:
  - 冻结命名标准
  - 分配唯一任务文件路径
  - 审核是否越界
- Architect (`explorer`):
  - 校验业务术语是否符合专利代理所习惯
  - 维护术语词典与边界定义
- Frontend Developer (`worker`):
  - 只实现一个前端术语整改原子任务
- Tester (`worker`):
  - 跑前端质量门
  - 做术语与显示审计
- Reviewer (`explorer`):
  - 复核“名称是否与实际对象一致”
  - 复核“文档/UI/测试口径是否统一”

## Atomic Task List

### 1) `tasks/afterdemon/AD-FE-TERM-01.md`
**Title**: 修正案件详情页签与实际业务对象错配

**Owner**: Frontend Developer  
**Scope**: case detail terminology only

**Allowed files**
- `frontend/src/constants/labels.zh.ts`
- `frontend/src/modules/cases/pages/CaseDetail.vue`
- `frontend/src/modules/cases/components/CaseClaimsTab.vue`

**Requirements**
- 将当前错误的 `权利要求` 页签调整为更符合实际内容的名称
- 页签与页内标题必须保持一致
- 不在本任务中扩展真正的权利要求文本功能
- 不修改案件数据结构和接口

**Acceptance**
- 页签名称与实际展示内容一致
- 不再把申请人/发明人页错误标成权利要求
- 无关页面不改

### 2) `tasks/afterdemon/AD-FE-TERM-02.md`
**Title**: 统一案件详情中的往来文件口径

**Owner**: Frontend Developer  
**Scope**: case documents tab terminology only

**Allowed files**
- `frontend/src/constants/labels.zh.ts`
- `frontend/src/modules/cases/components/CaseDocumentsTab.vue`
- `frontend/src/modules/documents/pages/DocumentCreate.vue`
- `frontend/src/modules/documents/pages/DocumentList.vue`

**Requirements**
- 冻结 `中间文件 / 往来文件 / 公文记录 / 官方文件` 的分层使用规则
- 案件详情页签采用 `往来文件`
- 页内标题与联动按钮文案同步一致
- documents 模块仍可保留通用 `文档` 技术实现，不改后端接口和数据模型

**Acceptance**
- 同一条用户链路中不再混用 `往来文件` / `公文记录` / `官方文件`
- 案件详情到文档创建的流程口径统一
- 无关菜单与模块不改

### 3) `tasks/afterdemon/AD-FE-TERM-03.md`
**Title**: 统一案件详情中的账单与收款口径

**Owner**: Frontend Developer  
**Scope**: case billing summary terminology only

**Allowed files**
- `frontend/src/constants/labels.zh.ts`
- `frontend/src/modules/cases/components/CaseReceiptsSummary.vue`

**Requirements**
- 页签采用 `账单与收款`
- 清理 `账单` 与 `账务` 混用
- 区块标题、空态、说明文案反映“账单对象 + 收款结果”的实际能力
- 不把当前能力夸大为完整账务台账

**Acceptance**
- 页签、摘要、空态语义一致
- 不再出现“页签叫账单，空态叫账务”的冲突
- 当前页面能力边界更清晰

### 4) `tasks/afterdemon/AD-DOC-TERM-01.md`
**Title**: 统一 demo 与测试文档中的案件详情术语

**Owner**: Reviewer / Doc Owner  
**Scope**: doc terminology only

**Allowed files**
- `docs/demo2.md`
- `docs/FPMS_Frontend_Manual_Test_User_Guide.md`
- optional scoped note under `docs/`

**Requirements**
- 文档按冻结标准统一页签名称
- 允许文档使用解释型写法，如 `官方文件（公文记录）`
- 明确哪些名称是 UI 短标签，哪些是业务解释
- 不借机重写整份演示稿逻辑

**Acceptance**
- 演示文档与测试文档不再互相冲突
- 文档对当前 UI 和业务语义的描述一致

### 5) `tasks/afterdemon/AD-FE-TERM-04.md`
**Title**: 建立前端术语词典与命名守卫

**Owner**: Frontend Developer  
**Scope**: naming governance only

**Allowed files**
- `frontend/src/constants/labels.zh.ts`
- optional new terminology helper under `frontend/src/constants/`
- optional lint/test note under `docs/`

**Requirements**
- 将核心业务术语集中固化
- 明确“领域规范词 / UI 短标签 / 禁用词”
- 至少覆盖：
  - `案件 / 案卷`
  - `中间文件 / 往来文件 / 公文记录 / 官方文件`
  - `账单 / 收款 / 账务`
  - `申请人/发明人 / 权利要求`
- 为后续 UI 开发提供单一来源
- 不在本任务中批量改所有页面

**Acceptance**
- 后续页面不必再次临时拍脑袋选词
- 至少覆盖案件、公文/官方文件、账单/收款摘要三组高频术语

### 6) `tasks/afterdemon/AD-QA-TERM-01.md`
**Title**: 后 Demo 术语整改审计与证据

**Owner**: Tester  
**Scope**: verification only

**Allowed files**
- `artifacts/AD-QA-TERM-01/**`

**Requirements**
- 验证已执行的术语整改任务在 UI 上一致
- 运行前端质量门
- 输出审计结论与证据

**Acceptance**
- `artifacts/AD-QA-TERM-01/` 下有完整证据
- 已执行整改范围内无明显术语冲突

## Recommended Execution Order

1. `tasks/afterdemon/AD-FE-TERM-01.md`
2. `tasks/afterdemon/AD-FE-TERM-02.md`
3. `tasks/afterdemon/AD-FE-TERM-03.md`
4. `tasks/afterdemon/AD-DOC-TERM-01.md`
5. `tasks/afterdemon/AD-FE-TERM-04.md`
6. `tasks/afterdemon/AD-QA-TERM-01.md`

## Recommended First Implementation Task

Start with:

`tasks/afterdemon/AD-FE-TERM-01.md`

原因：

- 它修正的是最严重的对象命名错误
- 改动面最小
- 对业务可信度提升最大
- 不依赖后端变化

## Shared Acceptance Checklist

- 页签名称必须对应当前实际内容对象
- 同一条用户链路不再出现互相冲突的近义术语
- 演示文档、测试文档、前端显示口径一致
- 不夸大当前已实现能力
- 不在单次执行中跨多个原子任务

## Verification Commands

Planning / doc task:

```bash
sed -n '1,260p' tasks/afterdemon/AFTERDEMO-TERM-ALIGNMENT_PLAN.md
```

Later frontend implementation tasks:

```bash
cd frontend && npm run lint
cd frontend && npm run typecheck
cd frontend && npm run build
```
