# DOCSEARCH-BE-01

- exact closure slice: implement the first-round document-specific search backend contract with the frozen executable mapping for `TemplateCode` -> `DocTemplate.code`, `DocName` -> `Document.title`, `NeedReply` -> `Document.need_reply`, `已Reply/Reply` -> `Document.reply_date is not null`, plus `case_no`, `date`, and `direction`
- explicit non-closure: no frontend, no `DocType` independent carrier/filter, no dispatch/reply linkage, no summary/export/reporting, no OCR/full-text, no schema changes
- remaining follow-up task ids: `DOCSEARCH-FE-01`, `DOCSEARCH-QA-01`
