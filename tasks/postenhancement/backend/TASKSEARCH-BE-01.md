# TASKSEARCH-BE-01

- exact closure slice: implement `APPLY_FEE_LIMIT` + `EXAM_REQUEST_LIMIT` special search backend contract with the frozen task projection, minimal filters, simple overdue semantics, pagination, and `due_date_range` realized as `due_date_from` / `due_date_to`; `remark` remains a nullable placeholder because current Task carrier does not persist it
- explicit non-closure: no frontend, no reminder linkage, no summary/export/reporting, no schema changes
- remaining follow-up task ids: `TASKSEARCH-FE-01`, `TASKSEARCH-QA-01`
