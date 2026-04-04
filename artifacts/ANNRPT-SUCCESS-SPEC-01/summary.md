# ANNRPT-SUCCESS-SPEC-01

- status: PASS
- closure slice: 冻结 `RPT-ANN` success-rate 的 denominator、numerator、按时规则与 year-lineage authority
- non-closure: 不做产品实现、不重做 grouped amount、不做 chart/export
- verification:
  - `./scripts/evidence_run.sh ANNRPT-SUCCESS-SPEC-01 lint test -f docs/superpowers/specs/2026-04-05-annuity-report-success-semantics-design.md`
  - `./scripts/evidence_run.sh ANNRPT-SUCCESS-SPEC-01 test /bin/zsh -lc "test -f ... && rg -n 'client_instruction = \"PAY\"|fee_item_id|FeeItem.year_no|paid_date <= due_date|manual' ..."`
- notes:
  - denominator 固定为 `client_instruction = "PAY"`
  - 无 `fee_item -> year_no` lineage 的 manual `GovPayment` 第一轮不计入 numerator

