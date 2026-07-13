# FPMS Additional Functional GAP Mitigation Design

Status: APPROVED — independent spec review completed 2026-07-10
Goal: `019f4a1a-6f55-77a2-b558-b6555201415c`
Program ID: `FPMS-ADDITIONAL-GAP-MITIGATION-20260710-01`

## 1. Objective

Mitigate the seven gaps from `FPMS-POST-ENHANCEMENT-ADDITIONAL-FUNCTIONAL-GAP-AUDIT-20260710-02` through fail-closed, backward-compatible, atomic implementation slices. The result must let a user start from a UI-created case and a normally registered official document, reach the filing/OA work package without enrichment, retain the OA task until receipt archive, reject cross-case receipt evidence, distinguish executable official notices from reference-only catalog rows, maintain an explicit official due date, and create grant-fee tasks only from traceable deadline evidence.

This document freezes contracts. It does not authorize product-code edits by itself; execution requires the batch manifest and one exact task file per slice.

## 2. Source hierarchy and verified facts

The design applies this evidence order: customer originals and rendered screenshots, extracted customer text, P1 Functional Spec/design, audits, then current code.

Key verified facts:

- The customer OA path does not end at internal reply-document creation. It continues through save, preview, signature, submit, receipt confirmation, and download of the electronic filing receipt. The rendered receipt identifies the receiving case, submitter/time, and received files.
- P1 AC-07 requires the OA task to remain open until receipt archive. The lifecycle design requires OA1/OA2 to return to `SUB_EXAM` only after receipt-based archive.
- V6 explicitly says work packages are production system outputs but uses enrichment because product create/resolve paths are absent.
- Customer text confirms first OA is normally four months and second/N OA two months, but the Goal's fail-closed rule makes the actual notice-carried due date authoritative. Template durations identify workflow/task type; they are not a substitute for a missing official due date.
- Grant deadline design says to use the notice-carried deadline or existing task due date and explicitly forbids service-side recomputation. Current `+60` behavior contradicts that design.
- The 60-row customer catalog is a source list, not authority to infer all state, task, fee, or reply semantics. Only explicitly sourced mappings may become executable.
- The worktree is dirty before this Goal. In particular, future ownership files `documents/api.py`, `official_notice_catalog.py`, `grant_fees/service.py`, `official_workflows/service.py`, `seed_dev.py`, and `frontend/src/api/documents.ts` already contain user changes. Every implementation task must capture dirty-baseline artifacts and preserve those changes.
- The current Alembic graph has one head, `frfe04_block_struct_cols_01`, supplied by an untracked user migration. The grant-lineage schema task must re-check the head at execution and may not rewrite that migration.

## 3. Story Shape Classification

- `shared_file_density`: high. The seven gaps converge on `official_workflows/service.py`, `documents/service.py`, `documents/api.py`, shared schemas, `seed_dev.py`, and frontend API clients.
- `prereq_dependency_density`: high. Transaction atomicity and semantic/deadline contracts precede reliable work-package, OA, catalog, and grant behavior; grant lineage also requires an explicit Phase 0-EXT schema slice.
- `be_fe_coupling`: high. Four gaps are not closed until backend contracts are reachable and legible through Simplified Chinese product UI.
- `evidence_cost`: high. Closure needs RED/GREEN service and API tests, dirty-baseline evidence, scoped lint, real-path UI validation without enrichment, a final release gate, and an item-to-slice ledger.
- `chosen_runbook`: `P0-prereq-heavy-story`.

Reason: a multi-lane run would create shared-file conflicts and could make deadline/state changes reachable before their prerequisites. The selected runbook keeps a serial control lane, with only the isolated wizard page fix eligible for an early non-conflicting slice.

## 4. Assumptions and fail-closed decisions

### 4.1 Frozen assumptions

1. `FILING_PREP` is unique per case for the MVP1 initial filing lifecycle. Resolve returns an existing package before checking the current case state, including an archived package. Creation is allowed only while the case is `NOT_FILED`; refiling/divisional behavior is non-closure. A database-unique `resolve_key` provides the concurrency guarantee.
2. `OA_REPLY` is unique per source official document. Resolve returns an existing package before checking the current case state. A different source document receives a different package, created only when the case state equals the resolved source semantics (`OA1` or `OA2`). A database-unique `resolve_key` provides the concurrency guarantee.
3. A source can start an OA package only when it is an incoming document with explicit executable OA semantics. Display-name similarity is not enough.
4. Creating an OA outgoing reply records the internal reply chain but does not close the official deadline task.
5. A normal OA archive requires archived receipt evidence. On archive, exactly one open task belonging to the source document and matching the resolved OA task-template code is closed, and OA1/OA2 returns to `SUB_EXAM` in the same transaction. Zero or multiple matching tasks is a 409 conflict.
6. Receipt evidence must belong to the package case. For OA, it must additionally belong to the linked reply document or already be an explicit manifest attachment for that package.
7. `Document.extra_data` remains the SQLite-compatible persistence carrier for the current phase, but the public API and UI receive structured fields. Existing valid JSON and legacy plain-text descriptions remain readable. A legacy `OfficialDueDate` without source/status is projected as unverified, never silently confirmed.
8. A confirmed official due date is immutable through ordinary edit. Setting a previously missing date is allowed; changing an existing confirmed date returns 409 until the customer approves an override permission/audit policy.
9. A grant-fee task is actionable only when it has a source document and an explicit confirmed due date. Legacy tasks stay visible as `LEGACY_UNVERIFIED` and cannot silently be treated as sourced.
10. Reissued/corrected grant notices are never inferred by title or creation order. Supersede is an explicit atomic action carrying the replacement notice payload, reason, and idempotency key; it creates the replacement document and task together, so the path is reachable without a pre-existing replacement document ID.

### 4.2 Customer-confirmation items and current mitigation

| Unconfirmed item | Current mitigation |
| --- | --- |
| Complete semantics for all 60 official-notice rows | Only the source-confirmed acceptance, first OA, second/N OA, and grant rows are executable. Every other row is disabled for workflow selection and marked reference-only/pending confirmation. |
| OA/rectification/reexamination archive target matrix | Automatic restore is limited to `OA1`/`OA2` → `SUB_EXAM`. Other current states return 409 and remain unchanged. |
| Official-due-date override roles | Ordinary edit cannot replace an existing confirmed date. No new override permission is guessed. |
| Automated `receiving_case_no` comparison | Same-case attachment ownership is mandatory now. Number-content matching remains a separately documented confirmation item. |
| Grant notice extraction source | Users must explicitly enter and confirm the notice-carried date. No OCR or `doc_date + N` fallback is introduced. |

## 5. Approaches considered

### Approach A — patch only the visible defects

Change `200` to `100`, add two work-package endpoints, skip OA task closure, and remove `+60`.

Advantages: smallest diff and fastest initial green tests.
Rejected because it leaves real Chinese catalog choices semantically disconnected, gives no canonical deadline/provenance contract, and would allow 409 side-effect failures after a document has already committed.

### Approach B — replace documents/tasks/work packages with a configurable workflow engine

Introduce normalized event, rule, state-machine, deadline, and evidence tables for every official notice.

Advantages: strongest long-term configurability.
Rejected for this Goal because source semantics are incomplete, the migration surface is large, and it violates the minimum/surgical constraint.

### Approach C — semantic adapter plus explicit provenance carriers (selected)

Keep existing tables and services. Add a small semantic resolver over `DocTemplate.input_fields`, structured API fields over the existing document JSON carrier, two idempotent work-package resolve paths, receipt-driven OA completion, and only the grant-lineage columns that cannot be represented safely without schema.

Advantages: fail-closed, testable, backward-compatible, and limited to the seven gaps. It also provides a stable seam for later customer-confirmed catalog mappings without inventing a full workflow engine.

## 6. Frozen contracts

### 6.1 Document semantic metadata

`DocTemplate.input_fields` may contain the following system-owned keys while preserving existing customer/source keys. All consumers call one resolver; they do not independently interpret raw JSON.

```json
{
  "catalog_kind": "OFFICIAL_NOTICE",
  "catalog_status": "EXECUTABLE|REFERENCE_ONLY",
  "execution_behavior": "ACCEPTANCE_NOTICE|OA_REPLY|GRANT_NOTICE|null",
  "completion_event": "OFFICIAL_RECEIPT_ARCHIVED|null",
  "archive_status_restore": "SUB_EXAM|null",
  "deadline_source_policy": "EXPLICIT_OFFICIAL_DUE_REQUIRED|null",
  "canonical_template_code": "OA_IN|GRANT_NOTICE|ACCEPTANCE_NOTICE|null"
}
```

The resolver returns one immutable `ResolvedDocumentSemantics` value with:

- `catalog_status`
- `execution_behavior`
- `case_status_effect`
- `task_template_code`
- `requires_reply`
- `completion_event`
- `archive_status_restore`
- `deadline_source_policy`
- `fee_trigger`

It treats malformed or unknown metadata as non-executable. It may use narrow backward-compatible fallbacks for the existing technical `OA_IN`, `GRANT_NOTICE`, and `ACCEPTANCE_NOTICE` codes, but no display-name matching. Document state effects, task generation, work-package resolution, OA close, impact preview, and grant-fee creation consume this resolved value. A direct field and metadata conflict is a 409 configuration error rather than a precedence guess.

Source-confirmed executable catalog subset:

| Customer catalog row | Behavior | Existing fields/target |
| --- | --- | --- |
| 受理通知-电子 | `ACCEPTANCE_NOTICE` | `status_effect=ACCEPTED` |
| 第一次审查意见通知书 | `OA_REPLY` | `status_effect=OA1`, task kind `OA_REPLY`, explicit official due required |
| 第二/三/四/五次审查意见通知书 | `OA_REPLY` | `status_effect=OA2`, new task identity `OA_REPLY_SUBSEQUENT` with no calculable fallback, explicit official due required; UI may say “通常两个月，具体以官文载明期限为准” |
| 授权通知书-电子 | `GRANT_NOTICE` | `status_effect=GRANT_PENDING`, grant task uses explicit official due |

The new-type/design first-action rows, rectification, reexamination, rejection, annuity, PCT, and all other rows remain `REFERENCE_ONLY` until their semantics are confirmed.

### 6.2 Structured document deadline carrier

Public document create/update/preview and wizard write contracts expose:

- `official_due_date: date | null`
- `official_due_date_source: "MANUAL_OFFICIAL_NOTICE" | "IMPORTED_OFFICIAL_NOTICE" | null`
- `official_due_date_status: "CONFIRMED" | "NEEDS_CONFIRMATION" | null`
- `description: string | null`

Document output uses a distinct read type whose `official_due_date_status` additionally permits service-derived `LEGACY_UNVERIFIED`. Clients cannot write `LEGACY_UNVERIFIED`.

Canonical persistence keys are `OfficialDueDate`, `OfficialDueDateSource`, `OfficialDueDateStatus`, and `description`. Unknown JSON keys are preserved. A legacy plain string is read as `description`; once structured data is saved it becomes canonical JSON. An existing JSON `OfficialDueDate` with no source/status projects as `official_due_date_status=LEGACY_UNVERIFIED` and is not executable until a user confirms that same date.

For an executable OA or grant notice:

- missing date or status other than `CONFIRMED` → 409 with no document/task/fee side effect committed;
- Pydantic date/enum shape errors → 422; valid fields in an invalid business combination → 400;
- valid confirmed date → task `due_date` equals the explicit date;
- confirming an unverified existing date to the same date atomically recalculates the one matching OA task's due date, internal date, and reminders and records audit evidence;
- zero or multiple matching OA tasks during confirmation → 409;
- an existing confirmed date changed, cleared, or deleted by ordinary update → 409;
- GET remains bodyless and exposes the structured projection plus legacy `extra_data`.

Create and impact preview retain `Doc.Create`; update retains `Doc.Edit`. Permissions remain function-parameter dependencies. Reference-only or missing executable semantics is a 409 missing-configuration/business conflict, not a schema error.

### 6.3 Document creation transaction

The document record, template state effect, task generation, work-package/grant side effects, and permitted fee side effects form one transaction. A 400/409 in any required side effect rolls the transaction back. Optional legacy fee generation may not swallow an error that is part of these seven fail-closed contracts.

### 6.4 Work-package identity and resolve contracts

Before resolve services are enabled, an explicitly authorized Phase 0-EXT schema task adds nullable `OfficialWorkPackage.resolve_key` and a unique index. It scans current data first, fails without mutation when duplicate identities exist, then backfills:

- `FILING_PREP:{case_id}`
- `OA_REPLY:{source_document_id}`

The column is nullable only for compatibility with unrelated historical package kinds; all new filing/OA packages require it. The unique index turns concurrent resolve races into a database conflict that the service handles by re-reading and returning the winner.

| Route | Permission | Success | Idempotency | Failure |
| --- | --- | --- | --- | --- |
| `POST /cases/{case_id}/official-work-packages/filing-preparation/resolve` | `OfficialWorkflow.Update` | 200, existing `FilingPreparationPackageOut` envelope | one `FILING_PREP` per case | case 404; duplicate-corrupt state 409 |
| `POST /official-documents/{document_id}/official-work-packages/oa-reply/resolve` | `OfficialWorkflow.Update` | 200, existing `OaReplyPackageOut` envelope | one `OA_REPLY` per source document | document 404; wrong direction 400; missing/reference-only semantics or duplicate-corrupt state 409 |

POST is used because resolve may create and initialize a package. Returning 200 for both created and reused results makes retry semantics stable; it does not claim 201 creation semantics. No router rewiring is required because the module router already exists.

Creation-only state gates run after the existing-package lookup: filing requires `NOT_FILED`; OA requires the case state specified by the resolved semantics (`OA1` for first OA, `OA2` for subsequent OA). A mismatch returns 409 and creates nothing. This ordering keeps archived-package resolve idempotent after the case has advanced.

### 6.5 OA completion event matrix

| Event | Source reply date | OA task | Package | Case |
| --- | --- | --- | --- | --- |
| `OA_OUT_CREATED` | set to internal reply-document date | remains `OPEN` | may link reply document; not archived | unchanged |
| receipt metadata recorded | unchanged | remains `OPEN` | receipt evidence recorded | unchanged |
| archive requested without valid receipt | unchanged | remains `OPEN` | 409, unchanged | unchanged |
| `OFFICIAL_RECEIPT_ARCHIVED` | unchanged | the unique open task whose document and template match resolved OA semantics → `DONE`, TaskLog `CLOSE` | `ARCHIVED` | `OA1`/`OA2` → `SUB_EXAM` |
| archive from an unconfirmed case state | unchanged | unchanged | 409, unchanged | unchanged |
| complete no-receipt override | unchanged | unchanged | `OVERRIDE` only | unchanged |
| repeated archive of already archived package | unchanged | no duplicate logs | unchanged | no state replay |

`OVERRIDE` never emits `OFFICIAL_RECEIPT_ARCHIVED`, never closes an OA task, and never restores the case. Only an archived receipt plus final package state `ARCHIVED` emits the event. The archive transaction records checklist evidence containing actor, source document, the one closed task ID, and case transition. A generic OUT document without executable OA source semantics keeps the existing non-OA reply behavior and cannot close an OA task accidentally.

### 6.6 Receipt ownership

- Missing package/attachment: 404.
- Attachment document case differs from package case: 400 `OFFICIAL_WORK_PACKAGE_RECEIPT_CASE_MISMATCH`.
- OA package attachment is same-case but neither on `reply_document_id` nor present in its manifest: 400 `OA_RECEIPT_ATTACHMENT_SOURCE_INVALID`.
- Validation happens before evidence flags or receipt rows are written.
- A final read-only scan joins package → receipt → attachment → document and records historical mismatches without mutating them.

### 6.7 Grant lineage schema and service

An explicitly authorized Phase 0-EXT migration adds SQLite-safe nullable compatibility columns to `t_grant_fee_task`:

- `source_document_id` (`String(36)` FK to `t_document.id`, indexed)
- `deadline_source` (`String(32)`)
- `deadline_confirmed_at` (`DateTime`, nullable)
- `superseded_by_task_id` (`String(36)` self-FK, indexed)
- `supersede_reason` (`Text`, nullable)
- `superseded_at` (`DateTime`, nullable)
- `superseded_by` (`String(36)`, nullable)
- `supersede_request_key` (`String(64)`, nullable, unique)

It also creates a standard unique index on non-null `source_document_id`; SQLite permits multiple nulls, preserving legacy rows. Existing-source duplicates are scanned before migration and block the migration rather than being arbitrarily merged. No existing task is backfilled with an invented source. Existing rows remain valid and expose a separate `lineage_status=LEGACY_UNVERIFIED`; this does not replace the existing workflow `status`.

First notice behavior:

- executable grant semantic + confirmed official date → create one task keyed by `source_document_id`;
- same source repeated → reuse the task;
- no confirmed date → 409; no `+60`, no task, no generic zero-value automatic grant draft;
- different source with an existing active task → explicit supersede-with-notice is required; title/date similarity never supersedes automatically.

Supersede behavior:

- `POST /grant-fee-tasks/{task_id}/replacement-notice` requires `GrantFeeTask.Write` and `Doc.Create` as function-parameter dependencies;
- payload contains `idempotency_key`, non-empty `reason`, and a nested incoming replacement-notice payload with template, document date/title/reference, and confirmed structured official due-date fields; case is derived from the old task and cannot be supplied as a different value;
- success is 200 with `GrantFeeTaskReplacementNoticeOut`, containing the created/reused `DocumentOut`, replacement `GrantFeeTaskListItemResponse`, and superseded task ID. The stable 200 covers both first execution and retry;
- validates old task 404, template/document business shape 400, Pydantic shape 422, reference-only/missing semantics or lineage conflict 409;
- atomically creates/reuses the replacement document/task, marks the old task superseded, preserves old financial records, and writes actor/reason/time;
- `idempotency_key` plus unique `source_document_id` provide database-level retry/concurrency safety; the same key returns the same result and a conflicting payload/key returns 409;
- superseded and legacy-unverified tasks remain visible with `lineage_status=SUPERSEDED|LEGACY_UNVERIFIED` and no state-changing actions until reconciled.

Existing grant state responses keep their current workflow `state/status` fields. Source confidence is exposed separately as `lineage_status=CONFIRMED|LEGACY_UNVERIFIED|SUPERSEDED`, plus `source_document_id`, `deadline_source`, and `deadline_confirmed_at`.

### 6.8 Frontend contracts

- `DocumentWizard` requests at most 100 templates and shows a Simplified Chinese load failure only for a real failure.
- Filing page accepts `case_id`; OA page accepts `document_id`; each calls its resolve POST when `package_id` is absent and then replaces the route with `package_id`.
- Case detail provides “进入新申请递交准备”. Existing document detail OA action becomes functional through page-level resolve.
- Document create/wizard/edit expose “官方期限”, “期限来源”, “确认状态”, and an impact warning. An existing confirmed date is read-only under the unconfirmed override policy.
- Template choices display executable/reference status in Chinese. Reference-only rows are not selectable for workflow automation.
- Grant-fee list shows source document, deadline source/status, legacy/superseded status, and provides the explicit supersede action.

## 7. Compatibility and boundaries

- No CPC/official-system direct submit, RPA, signing, payment, receipt download, OCR, or email automation.
- No complete legal-state transition matrix.
- No guessing semantics for rectification, reexamination, UM/design OA, rejection, annuity, or PCT notices.
- No automatic content comparison between `receiving_case_no` and application number in this Goal.
- No replacement of the existing document table or `extra_data` column.
- No reset/cleanup of the dirty worktree and no rewrite of the user-owned FRFE04 migration.
- Existing product UI text touched by these tasks remains Simplified Chinese.

## 8. Verification strategy

Each code slice follows RED → minimal GREEN → scoped lint/format → targeted test → scope diff → task gate. Tests that write SQLite run serially.

Final verification must cover:

1. UI-created case → filing resolve → package, twice, with one row and no enrichment.
2. Real Chinese first/second OA catalog selection with explicit due → task and OA resolve.
3. OA_OUT creation leaves task open; no-receipt archive returns 409; a complete override returns 200/`OVERRIDE` but changes neither task nor case; cross-case receipt returns 400; valid receipt archive closes the one matching task and restores `SUB_EXAM`; zero/multiple matching OA tasks returns 409.
4. Reference-only catalog rows cannot silently start state/task/fee effects.
5. Wizard template request succeeds within the backend limit.
6. Legacy JSON deadline reads correctly; structured create/wizard/edit and impact preview work; missing executable deadline fails closed without a persisted document.
7. Grant first source, missing date, duplicate source, legacy task, and explicit reissue/supersede paths preserve provenance and never use `+60`.
8. Concurrent filing/OA resolve attempts converge on one database row and one response identity.
9. Repo-wide checks and `./scripts/release_gate.sh` at final close, with unrelated dirty-baseline failures clearly separated.

## 9. Completion criteria

The design is implemented only when every task in the approved batch manifest independently passes with required evidence, the real-path verification uses no enrichment, and the final close ledger records residual gap `None` for all seven IDs. Customer-confirmation items remain fail-closed and are not counted as residual gaps when the approved mitigation explicitly prevents unsafe execution.
