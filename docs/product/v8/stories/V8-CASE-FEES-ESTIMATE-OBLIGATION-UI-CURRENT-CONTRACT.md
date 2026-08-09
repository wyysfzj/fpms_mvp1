# Story V8-CASE-FEES-ESTIMATE-OBLIGATION-UI-CURRENT-CONTRACT

- Risk: `PROTECTED`
- Outcome: close catalog row `267` by separating explicit fee estimation, persisted overlay
  obligations and persisted drafts in `CaseFeesTab`.
- Authority: the row-267 Ultra freeze; this story binds its exact contract to C3 delivery.

## Reviewed-source selector

The accepted overlay is the page's case-scoped reviewed-source read seam. Build selectable source
document IDs only from milestone `documentEvidence[].version` entries whose exact server
`reviewState` is `APPROVED` and whose `documentId` is non-null. Preserve milestone/version order
and retain the first occurrence of each exact document ID. Display the stored ID; do not infer from
role, current/final flags, document kind, case state or dates. The explicit “不选择来源文档” choice
sends `source_document_id: null`. If there is no reviewed document, null is the only choice.

All other controls, strict request, raw decimals/provenance, `ESTIMATE` presentation, real
obligation rendering, draft separation and no-mutation/error behavior remain exactly as frozen.
The focused Playwright test and serialized typecheck/scoped ESLint verify those observables.

No adapter/backend/parent edit, inferred source, automatic preview, numeric conversion,
instruction/draft mutation or adjacent cleanup. Rollback reverts only the page/test change and its
adoption.
