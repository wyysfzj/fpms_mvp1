# DOCSEARCH-BE-01

- exact closure slice: implement the first-round spec 9.3.2 document-specific search backend contract only after `DOCSEARCH-PRE-01` freezes the stable mapping for `DocType` -> no direct carrier, `TemplateCode` -> `DocTemplate.code`, `DocName` -> `Document.title`, `NeedReply` -> `Document.need_reply`, `已Reply` -> `Document.reply_date is not null`, and `Reply` -> display/query synonym for `已Reply`, not a new carrier
- explicit non-closure: blocked for now; no backend code changes until prerequisite closes; no frontend, no dispatch/reply linkage, no summary/export/reporting, no OCR/full-text, no schema changes
- remaining follow-up task ids: `DOCSEARCH-FE-01`, `DOCSEARCH-QA-01`
