# DOCSEARCH-FE-01

- exact closure slice: implement the frozen document-specific filters and projection wiring in `DocumentList.vue` plus shared documents FE api/types only after `DOCSEARCH-PRE-01` and the rewritten backend contract close with the stable mapping for `DocType` -> no direct carrier, `TemplateCode` -> `DocTemplate.code`, `DocName` -> `Document.title`, `NeedReply` -> `Document.need_reply`, `已Reply` -> `Document.reply_date is not null`, and `Reply` -> display/query synonym for `已Reply`, not a new carrier
- explicit non-closure: deferred for now; no new page/system, no dispatch/reply view, no summary/export/print, no reporting/dashboard, no OCR/full-text UI
- remaining follow-up task ids: `DOCSEARCH-QA-01`
