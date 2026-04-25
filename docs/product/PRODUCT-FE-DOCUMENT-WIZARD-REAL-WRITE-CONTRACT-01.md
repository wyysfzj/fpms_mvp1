# Document Wizard Real-Write UX Contract

## Decision

The document wizard MVP uses one real write action:

- `POST /documents/wizard/batch-create`
- User-facing label: `完成向导并提交`
- The write action creates document records and may persist reviewed task, fee, and attachment rows when supplied in the final payload.

Preview steps remain non-writing:

- task preview
- fee preview
- attachment preview

## Existing Backend Contract

The backend batch-create endpoint already accepts final payload sections:

- `task_rows`
- `fee_rows`
- `attachment_rows`

When rows are supplied, backend persistence is allowed to create:

- `Document`
- `Task`
- `FeeDraft` / `FeeItem`
- `DocAttachment`

The frontend must not treat preview responses as persisted data until the final submit succeeds.

## MVP Assertion Surface

For application completeness, FE should expose a single unambiguous final submit path:

1. Build and review candidate documents.
2. Preview generated tasks, fees, and attachments.
3. Submit once with the reviewed rows.
4. Show success with created document count and created identifiers if backend returns them.

## Step 2 Button Semantics

The existing early Step 2 submit behavior must not be presented as equivalent to full wizard completion.

Approved MVP options for follow-up FE work:

- Rename early Step 2 action to `仅登记文书`.
- Or disable early Step 2 submit until review steps are complete.
- Or keep early Step 2 action only if it clearly states downstream task/fee/attachment rows will not be written.

The preferred FE follow-up is to make `完成向导并提交` the primary real-write action and reduce early Step 2 submit ambiguity.

## Deferred Decisions

The following are not part of this MVP contract:

- New document rendering behavior.
- New approval workflow.
- New binary storage behavior.
- Automatic generation rules beyond the current backend preview and final-row persistence.
- New backend endpoint shape.

## Follow-Up Task

- `FE-DOCUMENT-WIZARD-REAL-WRITE-UX-01`
