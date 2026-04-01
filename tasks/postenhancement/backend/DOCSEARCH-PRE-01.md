# DOCSEARCH-PRE-01

- exact closure slice: freeze the stable mapping between spec 9.3.2 query terms and current repo carriers as:
  - `DocType` -> no direct carrier, never equate to `direction`
  - `TemplateCode` -> `DocTemplate.code`
  - `DocName` -> `Document.title`
  - `NeedReply` -> `Document.need_reply`
  - `已Reply` -> `Document.reply_date is not null`
  - `Reply` -> display/query synonym for `已Reply`, not a new carrier
  update the spec, implementation plan, and follow-up task wording so downstream implementation has an executable contract
- explicit non-closure: no product code changes, no backend endpoint changes, no frontend changes, no dispatch/reply/export/reporting, no schema changes unless a new follow-up prerequisite is explicitly created
- remaining follow-up task ids: `DOCSEARCH-BE-01`, `DOCSEARCH-FE-01`, `DOCSEARCH-QA-01`
