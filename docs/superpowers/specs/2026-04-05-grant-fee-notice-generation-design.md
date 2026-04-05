# Grant Fee Notice Generation Design

## Story Shape Classification

- `shared_file_density`: `high`
- `prereq_dependency_density`: `medium`
- `be_fe_coupling`: `cross-module FE/BE document-generation prerequisite freeze`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-prereq-heavy-story`

## Problem Statement

`FPMS SPEC 2.0` §5.7.2 明确要求在“授权费管理”界面对 `ClientInstruction=NONE` 的记录执行“生成授权费通知函”，调用模板系统生成 `T_Document(TemplateCode=GRANT_FEE_NOTICE)`、存档 Word 文档，并更新对应任务的 `NoticeSent=true`、`NotifyCount++`。当前 repo 只有 grant-fee 内部 `notice_sent / notify_count` carrier visibility，没有真实 grant-fee notice document generation path。由于这条链会同时碰 `grant_fees`、`documents`、`templates`，不能直接在没有 authority freeze 的情况下开写。

## Assumptions

- grant-fee task carrier 已存在：
  - `T_GrantFeeTask.notice_sent`
  - `T_GrantFeeTask.notify_count`
- documents side 已存在：
  - `create_document(...)`
  - `resolve_document_template_render_source(...)`
  - `build_document_template_render_context(...)`
  - `persist_generated_attachment(...)`
- templates side 已存在：
  - `TemplateRenderer.render_template_docx_bytes(...)`
- 第一轮目标只做：
  - real `GRANT_FEE_NOTICE` document generation authority freeze
- 当前不自动包含：
  - reminder task generation
  - dispatch / outgoing register
  - bill linkage
  - detail/edit page

## Scope

- 冻结 grant-fee notice generation 的 source-of-truth
- 冻结最小实现路径：
  - grant-fee selected tasks
  - real `Document`
  - rendered docx attachment
  - task carrier write-back
- 冻结 template source rule
- 冻结 FE/BE exact closure slice candidates

## Explicit Non-scope

- 不做任何产品实现补丁
- 不做 reminder task generation
- 不做 dispatch / envelope
- 不做 bill / settlement semantics
- 不更新 `#15` close decision

## Current Capability Assessment

### Available now

- grant-fee page already supports:
  - filters
  - selection
  - batch PAY / ABANDON
- documents module already supports:
  - `Document` creation
  - `DocTemplate` CRUD
  - template source resolution through `Template`
  - docx rendering
  - generated attachment persistence

### Missing as grant-fee-specific contract

- 哪个 `DocTemplate.code` 被视为 grant-fee notice authority
- grant-fee row -> generated `Document` lineage
- notice generation success 后如何更新：
  - `notice_sent`
  - `notify_count`
- 批量 notice generation 的 partial-failure 语义

## Authority Freeze

### Template authority

- 第一轮唯一权威模板代码固定为：
  - `GRANT_FEE_NOTICE`
- `DocTemplate.code == "GRANT_FEE_NOTICE"` 必须存在且可解析到可渲染的 `.docx` template source

### User-path authority

- notice generation must originate from the existing grant-fee worklist page
- selected rows must satisfy:
  - `client_instruction == NONE`
  - current derived state in:
    - `OPEN`
    - or `WAITING_CLIENT`
- rows with:
  - `client_instruction == PAY`
  - `client_instruction == ABANDON`
  - or `draft_generated == true`
  must not be silently absorbed

### Generated object authority

- each selected task produces:
  - one real `Document`
  - `direction = OUT`
  - `doc_template_id = GRANT_FEE_NOTICE template id`
  - one persisted docx attachment
- first-round linkage authority is:
  - `Document.extra_data` stores `grant_fee_task_id`
  - no schema change

### Write-back authority

- successful notice generation updates the corresponding task:
  - `notice_sent = true`
  - `notify_count = notify_count + 1`
- write-back is justified only after document + attachment persistence succeeds

## Recommended First Product Slice

- `GF-NOTICE-DOC-01`

### Exact closure candidate

- backend:
  - batch notice-generation endpoint for selected grant-fee rows
  - create real `Document`
  - render and persist notice attachment
  - write back `notice_sent / notify_count`
- frontend:
  - replace remaining notice placeholder path with real batch “生成通知函”
  - report success / invalid-row errors on existing worklist

## Shared-file / Ownership Analysis

- Backend:
  - `backend/app/modules/grant_fees/api.py`
  - `backend/app/modules/grant_fees/service.py`
  - `backend/app/modules/grant_fees/schemas.py`
  - `backend/app/modules/documents/service.py`
  - `backend/app/modules/documents/models.py`
  - `backend/tests/test_grant_fee_*`
  - possible documents tests
- Frontend:
  - `frontend/src/api/grantFees.ts`
  - `frontend/src/api/grantFees.types.ts`
  - `frontend/src/modules/grantFees/pages/GrantFeeTaskList.vue`

## SQLite / Phase Compatibility Assessment

- This freeze story is doc-only and compatible
- The proposed first implementation slice appears achievable without schema / migration by storing `grant_fee_task_id` in `Document.extra_data`
- If implementation later proves `extra_data` lineage insufficient, execution must stop and split a schema prerequisite rather than stretch the story

## Risks / Blockers

- largest risk:
  - hidden need for durable explicit linkage beyond `extra_data`
- second risk:
  - template code exists but no matching renderable source file
- third risk:
  - batch partial failure semantics becoming larger than one closure slice

## Exact Closure Slice Candidates

### Preferred

- `GF-NOTICE-DOC-SPEC-01`
  - freeze grant-fee real notice generation authority and implementation-ready minimal path

### Explicit non-closure

- no product implementation
- no reminder task generation
- no close update for `#15`

## Design Conclusion

- `可在当前约束下拆成可执行原子任务`
