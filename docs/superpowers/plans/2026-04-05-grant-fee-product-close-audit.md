# P2 #15 授权费管理 Product Close Audit Plan

## Story Shape Classification

- `shared_file_density`: `low`
- `prereq_dependency_density`: `low`
- `be_fe_coupling`: `close-audit after committed product slices`
- `evidence_cost`: `low`

## chosen_runbook

- `P0-single-lane-story`

## Batch Manifest

| Wave | Task ID | Owner | Allowlist | Verification |
|---|---|---|---|---|
| 1 | `GF-CLOSE-02` | main thread | `docs/FPMS_SPEC2_2nd_Review_REFRESH.md`, `docs/priority-ranked-mitigation-ledger.md`, `docs/superpowers/specs/2026-04-05-grant-fee-product-close-audit-design.md`, `docs/superpowers/plans/2026-04-05-grant-fee-product-close-audit.md`, `tasks/postenhancement/backend/GF-CLOSE-02.md`, `tasks/postenhancement/backend/GF-QA-CLOSE-02.md` | `./scripts/task_validate.sh GF-CLOSE-02` |
| 2 | `GF-QA-CLOSE-02` | main thread | `artifacts/GF-CLOSE-02/**`, `artifacts/GF-QA-CLOSE-02/**`, `tasks/postenhancement/backend/GF-QA-CLOSE-02.md` | `./scripts/task_validate.sh GF-QA-CLOSE-02` |

## Exact Closure Slice

- `GF-CLOSE-02`
  - update `#15` from `Partially Closed` to `Closed` if committed product evidence satisfies strict spec parity for §5.7.2–5.7.3

## Explicit Non-closure

- no product-code changes
- no re-audit of `#19`
- no new residual implementation stories
