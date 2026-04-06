# EXPSTAT-GROSSPROFIT-BE-01

- exact closure slice: add case-level `gross_profit_amounts` summary rows to `GET /expenses?include_stats=true` using `CaseReceipt.received_amt - Expense.amount`, grouped by `(case_id, currency)`
- explicit non-closure: no frontend changes, no client/department/worker gross-profit, no FX conversion, no `SPEC 5.11`
- remaining follow-up task ids: `EXPSTAT-GROSSPROFIT-FE-01`, `EXPSTAT-GROSSPROFIT-QA-01`
