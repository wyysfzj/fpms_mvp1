# PD-P1-FE-OA-PDF-CATEGORY-FALLBACK-20260611-01 — OA PDF category fallback

## Exact Closure Slice

Update the OA reply manifest UI fallback so the PDF fidelity attachment is labeled as official `附加文件：其他证明文件` when no explicit upload position is present.

## Explicit Non-Closure

No backend changes. No route changes. No attachment role model changes. No CPC/OA direct submit, RPA, auto-signature, auto-payment, or email sending.

## Remaining Follow-Up Task IDs

- `PD-P1-QA-FULLSCOPE-ANSWER-DELTA-20260611-01`

## Allowed Files

- `frontend/src/modules/documents/components/OAReplyManifest.vue`
- `tasks/postdemo/PD-P1-FE-OA-PDF-CATEGORY-FALLBACK-20260611-01.md`
- `artifacts/PD-P1-FE-OA-PDF-CATEGORY-FALLBACK-20260611-01/**`

## Verification Commands

- Static red/green scan for `附加文件类别待确认`
- `cd frontend && npm run typecheck`
- `cd frontend && npm run lint`
- `./scripts/task_validate.sh PD-P1-FE-OA-PDF-CATEGORY-FALLBACK-20260611-01`

## Acceptance

- `OAReplyManifest.vue` no longer shows `附加文件类别待确认` for the PDF fidelity attachment.
- The fallback text is Simplified Chinese and says `附加文件：其他证明文件`.
- No product behavior outside this component changes.
