# P2 #14 Masterdata Applicant + Country Close Ledger

## Item

- review item: `P2 #14`
- title: `申请人 / 国家主数据`
- interpretation: `shared prerequisite + dual object CRUD stories`

## Approved Decomposition

1. `MD-PRE`
2. `MD-CTR`
3. `MD-APP`

## Item-to-slice Ledger

### MD-PRE

- status: `PASS`
- commit: `c40c07c`
- closure:
  - 新增 `Applicant / Country` 结构化主数据承载与 SQLite-safe migration
  - 新增 list-only backend skeleton
  - 冻结独立权限命名空间
  - 新增最小 settings/masterdata 路由骨架
- evidence:
  - `artifacts/MDPRE-DB-01/**`
  - `artifacts/MDPRE-BE-01/**`
  - `artifacts/MDPRE-FE-01/**`
  - `artifacts/MDPRE-QA-01/**`
- residual gap:
  - 未实现 Applicant/Country 对象级 CRUD
  - 未做 selector / case form / import-export 联动
- close decision: `covered`

### MD-CTR

- status: `PASS`
- commit: `671aed6`
- closure:
  - `Country` 第一轮 `list + create + update + enable/disable`
  - backend CRUD contract
  - `CountryList.vue` 对象级管理页
  - QA close audit
- evidence:
  - `artifacts/MDCTR-BE-01/**`
  - `artifacts/MDCTR-FE-01/**`
  - `artifacts/MDCTR-QA-01/**`
- residual gap:
  - 未做 case form 国家下拉切换
  - 未做 selector 启用项过滤
  - 未做 import/export / delete / 历史治理
- close decision: `covered`

### MD-APP

- status: `PASS`
- commit: `7a4749e`
- closure:
  - `Applicant` 第一轮 `list + create + update + enable/disable`
  - backend CRUD contract
  - `ApplicantList.vue` 对象级管理页
  - QA close audit
- evidence:
  - `artifacts/MDAPP-BE-01/**`
  - `artifacts/MDAPP-FE-01/**`
  - `artifacts/MDAPP-QA-01/**`
- residual gap:
  - 未做 case form 申请人切换
  - 未做 selector 启用项过滤
  - 未做 import/export / delete / 历史治理
- close decision: `covered`

## Program-level Judgment

- `P2 #14` 按批准的 decomposition 解释，状态为 `PASS`
- prerequisite 与两个对象级 CRUD stories 均已关闭
- 当前 residual gap 全部位于明确批准的 `non-closure`

## Remaining Deferred Follow-ups

- `Applicant` / `Country` 与 case form 的 selector 联动
- selector 仅展示启用项的下游消费面切换
- search/filter 扩展
- import/export
- 删除、别名、去重、合并、历史治理
