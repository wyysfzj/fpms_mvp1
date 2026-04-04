# 2026-04-05 Annuity Report Success Semantics Plan

## Story Shape Classification

- `shared_file_density`: `low`
- `prereq_dependency_density`: `medium`
- `be_fe_coupling`: `semantics freeze before implementation`
- `evidence_cost`: `medium`

## chosen_runbook

- `P0-single-lane-story`

## Task

### `ANNRPT-SUCCESS-SPEC-01`

- exact closure slice: freeze `RPT-ANN` success-rate denominator, numerator, on-time rule, and year-lineage authority before implementation
- explicit non-closure: no product-code changes, no grouped-amount rework, no chart/export, no close update
- remaining follow-up task ids:
  - `ANNRPT-SUCCESS-01`
  - `ANNRPT-QA-SUCCESS-SPEC-01`

### `ANNRPT-QA-SUCCESS-SPEC-01`

- exact closure slice: audit evidence and exact closure for the success-rate semantics freeze
- explicit non-closure: no product-code changes
- remaining follow-up task ids: `None`
