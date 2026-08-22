# FPMS Additional Functional GAP Mitigation Final Close Audit

Program: `FPMS-ADDITIONAL-GAP-MITIGATION-20260710-01`  
Audit task: `FPMS-ADDGAP-FINAL-CLOSE-AUDIT-20260710-01`  
Audit role: Independent Reviewer  
Frozen manifest: `tasks/batches/FPMS-ADDITIONAL-GAP-MITIGATION-20260710-01.md`  
Manifest cardinality: 47 original tasks; supplemental Tasks48–70 remain outside the manifest.

## Decision rule

`covered` means every required atomic slice is mapped to direct task evidence, every original
dependency and relevant supplemental task is independently accepted, and no functional residual
remains inside the approved interpretation. Task46's representative real path supports every row
but never substitutes for the atomic slice evidence. Task47 is accepted only after the accepting
lead finalizes its scoped evidence and runs its task gate; the lead then records the no-exclusion
47-task manifest gate under the program artifact.

## Final item-to-slice ledger

| GAP ID | Required closure slices | Original task IDs | Relevant supplemental IDs | Direct evidence | Residual gap | Close decision |
| --- | --- | --- | --- | --- | --- | --- |
| `ADD-GAP-WIZARD-01` | Bound template requests to API maximum and prove the real wizard path no longer deterministically returns 422. | 01, 45, 46, 47 | Task68 | artifacts/FPMS-ADDGAP-WIZARD-TEMPLATE-LIMIT-20260710-01/{summary.md,results.jsonl,git/diff.patch}; artifacts/FPMS-ADDGAP-FINAL-REAL-PATH-E2E-20260710-01/summary.md; supplemental appendix evidence | None | covered |
| `ADD-GAP-WORKPKG-01` | Deterministic semantics and resolve identity; filing/OA existing-first services and bodyless APIs; reachable case, filing, and OA UI paths. | 03–12, 45–47 | None | artifacts/FPMS-ADDGAP-WORKPKG-RESOLVE-KEY-SCHEMA-20260710-01/** through artifacts/FPMS-ADDGAP-OA-PAGE-RESOLVE-20260710-01/**; artifacts/FPMS-ADDGAP-FINAL-REAL-PATH-E2E-20260710-01/summary.md | None | covered |
| `ADD-GAP-OA-01` | Semantic state effects; source-keyed OA package; OA_OUT remains open; owned receipt archive closes exactly one task/restores case; subsequent identity and confirmed due. | 03–04, 10–18, 26–27, 33–34, 45–47 | Tasks48, 51, 53, 56, 65–67, 70 | artifacts/FPMS-ADDGAP-OA-ENSURE-SERVICE-20260710-01/** through artifacts/FPMS-ADDGAP-OA-ALIAS-REPLY-VALIDATION-20260710-01/**; supplemental appendix evidence | None | covered |
| `ADD-GAP-RECEIPT-01` | Same-case ownership, OA source ownership, historical scan, and transactionally revalidated receipt archive event. | 14–17, 45–47 | None | artifacts/FPMS-ADDGAP-RECEIPT-SAME-CASE-GATE-20260710-01/** through artifacts/FPMS-ADDGAP-OA-RECEIPT-ARCHIVE-EVENT-20260710-01/**; artifacts/FPMS-ADDGAP-FINAL-REAL-PATH-E2E-20260710-01/summary.md | None | covered |
| `ADD-GAP-CATALOG-01` | Classify all 60 notices fail-closed; expose Chinese execution status; reject reference-only automation; activate only approved acceptance/OA/grant aliases. | 03–04, 18–21, 27–28, 33–34, 36–38, 45–47 | Tasks48, 50, 51, 53, 55 | artifacts/FPMS-ADDGAP-NOTICE-CATALOG-CLASSIFICATION-20260710-01/** through artifacts/FPMS-ADDGAP-NOTICE-GRANT-ACTIVATION-20260710-01/**; supplemental appendix evidence | None | covered |
| `ADD-GAP-DEADLINE-01` | Atomic document write; structured carrier and read/create/update/wizard contracts; legacy sync; OA fail-closed generation; impact preview and Chinese UI. | 02–04, 22–34, 45–47 | Tasks48, 51, 53, 54, 56, 64–68, 70 | artifacts/FPMS-ADDGAP-DOCUMENT-DEADLINE-CARRIER-20260710-01/** through artifacts/FPMS-ADDGAP-OA-ALIAS-REPLY-VALIDATION-20260710-01/**; supplemental appendix evidence | None | covered |
| `ADD-GAP-GRANT-01` | Source-keyed confirmed due; no premature generic draft; narrow activation; atomic replacement; separate lineage projections/gates; all mutation entrypoints and Chinese UI fail closed. | 02–04, 22–25, 35–44, 45–47 | Tasks49, 50, 52, 53, 55, 57–62, 64, 69 | artifacts/FPMS-ADDGAP-GRANT-LINEAGE-SCHEMA-20260710-01/** through artifacts/FPMS-ADDGAP-GRANT-REPLACEMENT-UI-20260710-01/**; supplemental appendix evidence | None | covered |

## Program acceptance

| Task | Closure | Current evidence status | Acceptance decision |
| --- | --- | --- | --- |
| `Task45` | Manifest-aware release gate with self-exclusion and fail-closed manifest parsing. | PASS — artifacts/FPMS-ADDGAP-MANIFEST-RELEASE-GATE-20260710-01/** | accepted |
| `Task46` | One isolated, no-enrichment real public API/UI path with seven observable checkpoints. | PASS — artifacts/FPMS-ADDGAP-FINAL-REAL-PATH-E2E-20260710-01/** | accepted |
| `Task47` | Independent ledger, supplemental gates, full checks, scoped evidence, and pre-self manifest gate. | PASS — artifacts/FPMS-ADDGAP-FINAL-CLOSE-AUDIT-20260710-01/** | accepted; lead runs the post-task no-exclusion manifest gate |

## Permission and status-code audit

- Protected document, work-package, and grant endpoints keep permission enforcement as function
  parameters: `Doc.*`, `DocTemplate.*`, `OfficialWorkflow.Read/Update`, and
  `GrantFeeTask.Read/Write`; replacement independently requires `GrantFeeTask.Write` and
  `Doc.Create`. Permission registries were not changed by Task47.
- Successful contracts retain 200 for reads, previews, resolves, state actions, replacement, and
  idempotent reuse; 201 for document and wizard creation. Repository 204 routes return
  `Response(status_code=204)` without a response model/body and remain covered by the full backend
  regression suite.
- The mapped tasks preserve 400 business validation, 401 authentication, 403 permission, 404
  missing resource, 409 conflict/fail-closed configuration or lineage, and 422 request-shape
  semantics. Task46 directly observes representative 400/409/422 contracts; atomic API tests
  provide the non-representative status/error coverage.

## Response-envelope and SQLite audit

- Existing page/list, resource, composite replacement, preview, and error envelopes are extended
  rather than replaced. Workflow `state/status` stays distinct from `lineage_status`.
- The migration and service slices use SQLite-safe nullable lineage columns, `CURRENT_TIMESTAMP`,
  application-generated string IDs, database uniqueness, flush-based identity, and serialized
  writes. No PostgreSQL-only type/function or correctness dependency on `RETURNING` was introduced.
- Seed/catalog work is idempotent and leaves customer-unconfirmed rows reference-only. Task47 does
  not mutate schema, seed, product data, or prior evidence.

## Simplified Chinese UI audit

The touched wizard, document create/edit, catalog, filing/OA package, grant lineage, and replacement
surfaces use Simplified Chinese for headings, fields, actions, validation, empty states, and
fail-closed feedback. English remains limited to technical codes, IDs, enums, paths, and logs.
Task46 verifies the real visible checkpoints without route interception or database injection.

## Supplemental Tasks48–70 appendix

| Task | Canonical task ID | Parent GAP / slice | Closure | Evidence | Independent review / task gate | Residual | Decision |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `Task48` | `FPMS-ADDGAP-OA-DEADLINE-OBSOLETE-TEST-ALIGNMENT-20260711-01` | OA, Catalog, Deadline / obsolete explicit-due fixtures | Preserve coverage while aligning executable OA tests to confirmed due. | artifacts/FPMS-ADDGAP-OA-DEADLINE-OBSOLETE-TEST-ALIGNMENT-20260711-01/{summary.md,results.jsonl,git/diff.patch} | APPROVE / PASS | None | covered |
| `Task49` | `FPMS-ADDGAP-GRANT-AUTO-DRAFT-OBSOLETE-TEST-ALIGNMENT-20260711-01` | Grant / obsolete generic auto-draft expectations | Preserve fee-linking coverage under the no-premature-draft rule. | artifacts/FPMS-ADDGAP-GRANT-AUTO-DRAFT-OBSOLETE-TEST-ALIGNMENT-20260711-01/{summary.md,results.jsonl,git/diff.patch} | APPROVE / PASS | None | covered |
| `Task50` | `FPMS-ADDGAP-GRANT-NOTICE-OBSOLETE-TEST-ALIGNMENT-20260711-01` | Grant, Catalog / grant notice source and deadline fixtures | Preserve notice creation/reuse with exact confirmed lineage. | artifacts/FPMS-ADDGAP-GRANT-NOTICE-OBSOLETE-TEST-ALIGNMENT-20260711-01/{summary.md,results.jsonl,git/diff.patch} | APPROVE / PASS | None | covered |
| `Task51` | `FPMS-ADDGAP-DOCUMENT-IMPACT-OBSOLETE-TEST-ALIGNMENT-20260711-01` | OA, Catalog, Deadline / impact-preview fixtures | Preserve impact assertions under confirmed explicit due. | artifacts/FPMS-ADDGAP-DOCUMENT-IMPACT-OBSOLETE-TEST-ALIGNMENT-20260711-01/{summary.md,results.jsonl,git/diff.patch} | APPROVE / PASS | None | covered |
| `Task52` | `FPMS-ADDGAP-GRANT-PREVIEW-NO-AUTO-DRAFT-20260711-01` | Grant / impact preview | Suppress generic grant draft impact before instruction. | artifacts/FPMS-ADDGAP-GRANT-PREVIEW-NO-AUTO-DRAFT-20260711-01/{summary.md,results.jsonl,git/diff.patch} | APPROVE / PASS | None | covered |
| `Task53` | `FPMS-ADDGAP-SPEC-E2E-OBSOLETE-TEST-ALIGNMENT-20260711-01` | OA, Deadline, Grant / legacy spec E2E | Align explicit due and explicit grant draft while retaining finance chain. | artifacts/FPMS-ADDGAP-SPEC-E2E-OBSOLETE-TEST-ALIGNMENT-20260711-01/{summary.md,results.jsonl,git/diff.patch} | APPROVE / PASS | None | covered |
| `Task54` | `FPMS-ADDGAP-WIZARD-DEADLINE-OBSOLETE-TEST-ALIGNMENT-20260711-01` | Deadline / wizard validation | Align malformed raw carrier expectation to 422 without weakening coverage. | artifacts/FPMS-ADDGAP-WIZARD-DEADLINE-OBSOLETE-TEST-ALIGNMENT-20260711-01/{summary.md,results.jsonl,git/diff.patch} | APPROVE / PASS | None | covered |
| `Task55` | `FPMS-ADDGAP-GRANT-ACTIVATION-OBSOLETE-TEST-ALIGNMENT-20260711-01` | Catalog, Grant / seed expectation | Preserve original six activations and add exact grant row 009 semantics. | artifacts/FPMS-ADDGAP-GRANT-ACTIVATION-OBSOLETE-TEST-ALIGNMENT-20260711-01/{summary.md,results.jsonl,git/diff.patch} | APPROVE / PASS | None | covered |
| `Task56` | `FPMS-ADDGAP-OA-REPLY-CHAIN-OBSOLETE-TEST-ALIGNMENT-20260711-01` | OA, Deadline / reply-chain fixtures | Preserve reply/open/no-writeoff/status/filter/lifecycle assertions with due tuple. | artifacts/FPMS-ADDGAP-OA-REPLY-CHAIN-OBSOLETE-TEST-ALIGNMENT-20260711-01/{summary.md,results.jsonl,git/diff.patch} | APPROVE / PASS | None | covered |
| `Task57` | `FPMS-ADDGAP-GRANT-WORKLIST-LINEAGE-TEST-ALIGNMENT-20260711-01` | Grant / list exact-key contract | Add four lineage projection keys without weakening list assertions. | artifacts/FPMS-ADDGAP-GRANT-WORKLIST-LINEAGE-TEST-ALIGNMENT-20260711-01/{summary.md,results.jsonl,git/diff.patch} | APPROVE / PASS | None | covered |
| `Task58` | `FPMS-ADDGAP-GRANT-STATE-LINEAGE-TEST-ALIGNMENT-20260711-01` | Grant / state fixtures and exact-key contract | Give ordinary state fixtures confirmed lineage and retain state assertions. | artifacts/FPMS-ADDGAP-GRANT-STATE-LINEAGE-TEST-ALIGNMENT-20260711-01/{summary.md,results.jsonl,git/diff.patch} | APPROVE / PASS | None | covered |
| `Task59` | `FPMS-ADDGAP-GRANT-MUTATION-LINEAGE-GATE-20260711-01` | Grant / mutation entrypoints | Gate direct draft, batch instruction, and notice mutations before side effects. | artifacts/FPMS-ADDGAP-GRANT-MUTATION-LINEAGE-GATE-20260711-01/{summary.md,results.jsonl,git/diff.patch} | APPROVE / PASS | None | covered |
| `Task60` | `FPMS-ADDGAP-GRANT-MUTATION-LINEAGE-UI-GATE-20260711-01` | Grant / mutation UI actions | Hide or disable mutation actions for non-actionable lineage in Chinese UI. | artifacts/FPMS-ADDGAP-GRANT-MUTATION-LINEAGE-UI-GATE-20260711-01/{summary.md,results.jsonl,git/diff.patch} | APPROVE / PASS | None | covered |
| `Task61` | `FPMS-ADDGAP-GRANT-DRAFT-LINEAGE-TEST-ALIGNMENT-20260711-01` | Grant / draft regression fixtures | Use real same-case confirmed sources and retain draft/item/idempotency assertions. | artifacts/FPMS-ADDGAP-GRANT-DRAFT-LINEAGE-TEST-ALIGNMENT-20260711-01/{summary.md,results.jsonl,git/diff.patch} | APPROVE / PASS | None | covered |
| `Task62` | `FPMS-ADDGAP-GRANT-NOTICE-LINEAGE-TEST-ALIGNMENT-20260711-01` | Grant / notice regression fixtures | Use real same-case confirmed sources and retain render/attachment/error assertions. | artifacts/FPMS-ADDGAP-GRANT-NOTICE-LINEAGE-TEST-ALIGNMENT-20260711-01/{summary.md,results.jsonl,git/diff.patch} | APPROVE / PASS | None | covered |
| `Task63` | `FPMS-ADDGAP-EVIDENCE-SECRET-SANITATION-20260711-01` | Program evidence / secret hygiene | Redact only frozen raw credential substrings while preserving evidence meaning and structure. | artifacts/FPMS-ADDGAP-EVIDENCE-SECRET-SANITATION-20260711-01/{summary.md,results.jsonl,git/diff.patch} | APPROVE / PASS | None | covered |
| `Task64` | `FPMS-ADDGAP-DOCUMENT-ATOMICITY-DEADLINE-TEST-ALIGNMENT-20260711-02` | Deadline, Grant / atomicity fixture | Align the atomicity test to confirmed grant deadline lineage without weakening rollback assertions. | artifacts/FPMS-ADDGAP-DOCUMENT-ATOMICITY-DEADLINE-TEST-ALIGNMENT-20260711-02/{summary.md,results.jsonl,git/diff.patch} | APPROVE / PASS | None | covered |
| `Task65` | `FPMS-ADDGAP-NEED-REPLY-DEADLINE-TEST-ALIGNMENT-20260711-02` | OA, Deadline / need-reply fixture | Align the OA helper fixture to confirmed explicit due while retaining deadline-edit rules. | artifacts/FPMS-ADDGAP-NEED-REPLY-DEADLINE-TEST-ALIGNMENT-20260711-02/{summary.md,results.jsonl,git/diff.patch} | APPROVE / PASS | None | covered |
| `Task66` | `FPMS-ADDGAP-DOCUMENT-SEARCH-DEADLINE-TEST-ALIGNMENT-20260711-02` | OA, Deadline / search fixtures | Align OA search fixtures to confirmed explicit due while preserving search result assertions. | artifacts/FPMS-ADDGAP-DOCUMENT-SEARCH-DEADLINE-TEST-ALIGNMENT-20260711-02/{summary.md,results.jsonl,git/diff.patch} | APPROVE / PASS | None | covered |
| `Task67` | `FPMS-ADDGAP-DOCUMENT-UI-DEADLINE-TEST-ALIGNMENT-20260711-02` | OA, Deadline / UI-path fixture | Align the UI-path OA fixture to confirmed explicit due without changing its other assertions. | artifacts/FPMS-ADDGAP-DOCUMENT-UI-DEADLINE-TEST-ALIGNMENT-20260711-02/{summary.md,results.jsonl,git/diff.patch} | APPROVE / PASS | None | covered |
| `Task68` | `FPMS-ADDGAP-WIZARD-PREVIEW-DEADLINE-TEST-ALIGNMENT-20260711-02` | Wizard, Deadline / preview expectation | Use explicit confirmed due and assert preview returns that exact value; retain non-deadline behavior. | artifacts/FPMS-ADDGAP-WIZARD-PREVIEW-DEADLINE-TEST-ALIGNMENT-20260711-02/{summary.md,results.jsonl,git/diff.patch} | APPROVE / PASS | None | covered |
| `Task69` | `FPMS-ADDGAP-GRANT-SCHEMA-TEST-ALIGNMENT-20260711-02` | Grant / schema contract | Align the frozen schema assertion to the accepted grant lineage carriers. | artifacts/FPMS-ADDGAP-GRANT-SCHEMA-TEST-ALIGNMENT-20260711-02/{summary.md,results.jsonl,git/diff.patch} | APPROVE / PASS | None | covered |
| `Task70` | `FPMS-ADDGAP-DOCUMENT-UI-OA-OUT-STATE-TEST-ALIGNMENT-20260711-01` | OA, Deadline / OA_OUT state expectation | Align the obsolete auto-writeoff assertion to Task43's accepted keep-open contract. | artifacts/FPMS-ADDGAP-DOCUMENT-UI-OA-OUT-STATE-TEST-ALIGNMENT-20260711-01/{summary.md,results.jsonl,git/diff.patch} | APPROVE / PASS | None | covered |

## Verification evidence

- Original Tasks01–46 task status and gate-equivalent evidence: verified by the Task47 contract test;
  the Task45 manifest gate is rerun with Task47 excluded before handoff.
- Supplemental Tasks48–70: each task gate is rerun serially and recorded under Task47 evidence.
- Task47 contract test, repository Ruff, full backend pytest, frontend lint/typecheck/build, and the
  frozen Task46 real path are recorded under
  `artifacts/FPMS-ADDGAP-FINAL-CLOSE-AUDIT-20260710-01/outputs/`.
- A program-wide secret scan covers Tasks01–70. Any unredacted bearer/JWT result is a sanitation
  blocker and cannot be repaired inside Task47's allowlist.
- Final no-exclusion manifest acceptance is intentionally post-Task47 and remains owned by the lead.

## Final audit conclusion

All seven approved functional GAP interpretations have complete item-to-slice mappings and no
remaining functional residual (`None`). The batch must not be announced complete until Task47's
independent scoped evidence and task gate pass and the lead records the final 47-task manifest gate
without exclusion.
