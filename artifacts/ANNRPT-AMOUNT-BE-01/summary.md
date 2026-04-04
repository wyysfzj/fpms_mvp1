# ANNRPT-AMOUNT-BE-01

- status: PASS
- closure slice: `/annuity/tasks` summary 增加 `client_amounts`、`country_amounts`、`year_amounts`
- non-closure: 未实现 success-rate、图表、导出
- verification:
  - `python3 -m ruff check backend/app/modules/annuity/api.py backend/app/modules/annuity/service.py backend/app/modules/annuity/schemas.py backend/tests/test_annuity_report.py`
  - `cd backend && pytest -q tests/test_annuity_report.py`
- notes:
  - grouped amount semantics follow `ANNRPT-AMOUNT-SPEC-01`
  - `official_paid_amount` 按案件内 payable 比例分摊到年度分组

