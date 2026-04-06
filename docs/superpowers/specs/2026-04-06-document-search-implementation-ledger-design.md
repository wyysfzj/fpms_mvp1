# P2 #19 中间文件专项查询 Strict Query Implementation Ledger Design

## Story Shape Classification

- `shared_file_density`: `medium`
- `prereq_dependency_density`: `medium`
- `be_fe_coupling`: `query ledger before implementation`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-prereq-heavy-story`

## Problem Statement

`P2 #19 中间文件专项查询` 不能再沿用 old review 的 `single missing feature` framing。当前仓库已经存在真实的 documents list/query 页面与 backend query contract，第一轮 `template_code / doc_name / case_no / need_reply / replied / direction / date / client` 专项查询闭环已经落地。但相对 `FPMS SPEC 2.0` §9.3.2，`DocType` 是否具备独立查询语义仍未被真实关闭。如果不先建立一份严格的 doc-search implementation ledger，后续很容易再次把 `DocType` 借道 `direction`、`template_code` 或 `ref_no` 的近似实现误判成 full spec parity。

## Assumptions

- 权威对象固定为：
  - `#19 strict doc-search implementation ledger`
- 关闭标准固定为：
  - 只有真实页面/API/用户路径存在，query slice 才能计入 `Implemented`
- doc/spec/plan/contract 不得单独支撑：
  - `Implemented`
  - `Closed`
- `DocType` 不能被偷换为：
  - `direction`
  - `template_code`
  - `ref_no`
- 第一轮结果形态固定为：
  - `strict query ledger`
  - `query decomposition / reclassification`
- 第一轮不自动包含：
  - dispatch
  - reply workflow
  - reporting / export / print
  - OCR / full-text
  - wizard / 录入链路

## Scope

- 对 `#19` 做 strict query inventory
- 标记各 query slice 为：
  - `Implemented`
  - `Partially Implemented`
  - `Contract/Plan Only`
  - `Missing`
- 冻结 `#19` 的 query 边界与 non-closure
- 给出后续 implementation slice priority 建议

## Explicit Non-scope

- 任何产品实现补丁
- 任何 review close update
- `DocType` carrier/filter 的直接实现
- dispatch / reply workflow
- reporting / export / print
- OCR / full-text
- wizard / 录入 / 打印链路

## Exact Current Query Inventory

### `DOCSEARCH-LIST`

- Current product evidence:
  - `frontend/src/modules/documents/pages/DocumentList.vue`
  - `backend/app/modules/documents/api.py`
  - `backend/app/modules/documents/service.py`
- Observed capability:
  - real document-specific list page exists
  - real `GET /documents` query endpoint exists
  - pagination and detail-route entry exist
- Current classification:
  - `Implemented`

### `DOCSEARCH-FILTERS`

- Current product evidence:
  - `backend/app/modules/documents/api.py`
  - `backend/app/modules/documents/service.py`
  - `frontend/src/modules/documents/pages/DocumentList.vue`
  - `backend/tests/test_document_specific_search_api.py`
- Observed capability:
  - `doc_name`
  - `case_no`
  - `template_code`
  - `client_id`
  - `need_reply`
  - `replied`
  - `direction`
  - `date_from / date_to`
- Current classification:
  - `Implemented`

### `DOCSEARCH-TEMPLATE-CODE`

- Current product evidence:
  - `frontend/src/api/documents.ts`
  - `frontend/src/api/documents.types.ts`
  - `frontend/src/modules/documents/pages/DocumentList.vue`
  - `backend/app/modules/documents/service.py`
- Observed capability:
  - independent `template_code` filter exists in both BE and FE
- Current classification:
  - `Implemented`

### `DOCSEARCH-REPLY`

- Current product evidence:
  - `backend/app/modules/documents/api.py`
  - `backend/app/modules/documents/service.py`
  - `frontend/src/modules/documents/pages/DocumentList.vue`
  - `backend/tests/test_document_specific_search_api.py`
- Observed capability:
  - `need_reply`
  - `replied`
  - visible replied state on the list page
- Current classification:
  - `Implemented`

### `DOCSEARCH-DOCTYPE`

- Current product evidence:
  - `docs/superpowers/specs/2026-04-01-document-specific-search-design.md`
  - `tasks/postenhancement/backend/DOCSEARCH-PRE-01.md`
  - `frontend/src/api/documents.ts`
  - `frontend/src/api/documents.types.ts`
  - `frontend/src/modules/documents/pages/DocumentCreate.vue`
  - `frontend/src/modules/documents/pages/DocumentEdit.vue`
  - `backend/app/modules/tasks/task_generation_service.py`
- Observed capability:
  - current FE `doc_type` is mapped to `ref_no`
  - no independent backend `DocType` query param exists
  - current design docs explicitly defer `DocType` independent closure
- Residual concern:
  - spec expects `DocType=OFFICIAL_IN / OFFICIAL_OUT / CLIENT_IN / CLIENT_OUT`
  - repo currently has no proven independent carrier/filter closure for that semantics
- Current classification:
  - `Partially Implemented`

### `DOCSEARCH-EXPORT`

- Current product evidence:
  - no dedicated search export path
- Current classification:
  - `Missing`

### `DOCSEARCH-FULLTEXT`

- Current product evidence:
  - no OCR/full-text search path
- Current classification:
  - `Missing`

## Query Boundary Freeze

### Included in `#19`

- document-specific search page
- search filters and result columns
- minimal carrier/filter semantics required to support query correctness
- the `DocType` residual semantics question

### Explicit non-closure / deferred from `#19` first-round ledger

- dispatch workflow
- reply workflow itself
- reporting / export / print
- OCR / full-text
- wizard / document entry / mailing / envelope
- generic documents CRUD and attachment management outside query semantics

## Product-closure Standard

### `Implemented`

- a real FE page and/or user path exists
- the supporting backend/API contract exists
- the slice expresses the semantics required by spec

### `Partially Implemented`

- a real product slice exists
- but the slice is still representative / partial relative to spec semantics

### `Contract/Plan Only`

- only doc/spec/plan/task evidence exists
- no real product behavior exists yet

### `Missing`

- neither product behavior nor contract closure exists

## Residual Query Ledger

- primary residual:
  - `DOCSEARCH-DOCTYPE`
- deferred residuals outside first-round query closure:
  - `DOCSEARCH-EXPORT`
  - `DOCSEARCH-FULLTEXT`

## Shared-file / Ownership Analysis

- backend shared ownership:
  - `backend/app/modules/documents/api.py`
  - `backend/app/modules/documents/service.py`
  - `backend/app/modules/documents/schemas.py`
- frontend shared ownership:
  - `frontend/src/api/documents.ts`
  - `frontend/src/api/documents.types.ts`
  - `frontend/src/modules/documents/pages/DocumentList.vue`
- adjacent semantic hot spots:
  - `frontend/src/modules/documents/pages/DocumentCreate.vue`
  - `frontend/src/modules/documents/pages/DocumentEdit.vue`
  - `backend/app/modules/tasks/task_generation_service.py`

Conclusion:
- `#19` is `shared`
- follow-up implementation must serialize shared ownership
- the next story should not absorb create/edit/task-generation rewrite unless strictly required

## Risks / Blockers

- treating `DocType` as equivalent to `direction`
- treating `DocType` as equivalent to `template_code`
- treating FE `doc_type -> ref_no` mapping as proof of `DocType` carrier
- pulling dispatch/reply/reporting/full-text into this item

## Recommended First Follow-up

- `DOCSEARCH-DOCTYPE-SPEC-01`

Why:
- the main unresolved issue is semantic authority, not missing page scaffolding
- the spec/refresh/ledger all already point to `DocType` as the residual
- this follow-up can decide whether implementation is direct or prerequisite-driven

## Exact Closure Slice

- `DOCSEARCH-LEDGER-01`
  - freeze strict doc-search implementation ledger for `#19`

## Design Conclusion

- `受 shared-ownership / query decomposition 约束，当前应先做 ledger/reclassification`
