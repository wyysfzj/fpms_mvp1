# ANNRPT-SUCCESS-BE-01

- status: PASS
- closure slice: `/annuity/tasks` summary 增加 `monitored_task_count`、`on_time_paid_count`、`late_paid_count`、`success_rate`
- non-closure: 未实现按客户/国别/年度拆分成功率、图表、导出
- verification:
  - `python3 -m ruff check backend/app/modules/annuity/api.py backend/app/modules/annuity/service.py backend/app/modules/annuity/schemas.py backend/tests/test_annuity_report.py`
  - `cd backend && pytest -q tests/test_annuity_report.py`
- notes:
  - denominator 固定为 `client_instruction == "PAY"`
  - success numerator 仅接受 `fee_item -> year_no` 可回投的 `GovPayment`

