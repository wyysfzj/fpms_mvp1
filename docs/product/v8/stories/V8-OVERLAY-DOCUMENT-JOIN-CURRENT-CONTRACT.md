# Story V8-OVERLAY-DOCUMENT-JOIN-CURRENT-CONTRACT

- Risk: `PROTECTED`
- Outcome: close catalog row `261` by enriching the already-frozen overlay page with exact
  document-evidence, official-work-package and task facts linked to its activity IDs.
- Catalog ID: `FPMS-V8-OVERLAY-DOCUMENT-JOIN-20260712-01`.
- Dependency owner: `V8-OVERLAY-CENTER-QUERY-CURRENT-ADOPTION`.

## Exact association graph

The activity evidence table is the only root. For the milestones already selected by the
center query:

1. An evidence row whose `object_type` is `DocumentEvidenceVersion` selects that exact version.
2. An evidence row whose `object_type` is `OfficialWorkPackage` selects that exact package.
3. An evidence row whose `object_type` is `OfficialWorkPackageReceipt` selects that exact
   receipt and its owning package.
4. A manifest whose `evidence_version_id` is one of the directly selected versions selects its
   owning package.
5. Tasks attach only through exact `Task.document_id` equality to a selected version's
   `document_id` or a selected package's source/reply document ID, with the same case ID.

No title, date, filename, template, status, case-wide sweep or fuzzy fallback may create an
association. Each selected object must exist, belong to the same case, and satisfy its accepted
enum/identity invariants; otherwise fail 409 `LIFECYCLE_OVERLAY_DOCUMENT_CONFLICT` rather than
silently omit it. Unrecognized evidence object types remain in `evidence_summary` and do not
become document facts.

## Projection and ordering

Each directly selected evidence version becomes one `OverlayDocumentEvidence`. Project all
accepted `EvidenceVersionResult` fields exactly; `is_current` means its identity key equals
`f"{case_id}|{lineage_key}"`, and `is_final` comes only from `FINAL`. Attach every same-case
derivation where the selected version is parent or child, ordered by
`(derived_at, evidence_derivation_id)` and projected exactly.

Each selected package becomes one `OverlayWorkPackage`, ordered by package ID. Manifest evidence
version IDs are non-null IDs ordered by manifest `(sort_order NULLS LAST, id)`; receipts are
ordered by `(received_at NULLS LAST, receipt_id)` and projected exactly. Reuse
`evaluate_official_work_package()` as the sole package-gate semantic owner and expose its blocker
types, in returned order, as `missing_gate_codes`; do not copy its blocker rules.

Tasks are ordered by `(due_date NULLS LAST, task_id)` and projected exactly. Every fact is attached
to each root milestone whose evidence graph selects it; no fact migrates to a different activity
merely because it is newer. Query joins may be bulked across the page, while package evaluation
is once per distinct package. Preserve the center result, generated timestamp, cursor fields,
warnings, decision gates and legacy conflicts unchanged.

## Verification, non-goals and rollback

The focused test proves exact version/derivation/package/manifest/receipt/task projection,
deterministic ordering, shared package reuse, unrelated-object exclusion, missing/cross-case and
enum corruption fail-closed behavior, and read-only execution. Run it with the accepted center
test plus scoped Ruff/format/diff. An independent High reviewer reviews the exact commit/range.

No fee join, decision-gate resolution, pagination, endpoint/UI, package mutation, schema,
new association column, fuzzy inference or adjacent cleanup. Rollback reverts only the row-261
service/test change and its adoption; the row-260 center remains intact.
