# PRODUCT-B-OA-WIZARD-CONTRACT-01

Task ID: `PRODUCT-B-OA-WIZARD-CONTRACT-01`

Story Shape Classification:
- shared_file_density: low
- prereq_dependency_density: high
- be_fe_coupling: medium
- evidence_cost: medium

chosen_runbook: `P0-prereq-heavy-story`

## Exact Closure Slice

Freeze the B-wave MVP product/backend assertion surface for OA document wizard, OA reply chain, OA fee draft lineage, and downstream automation readiness.

This task closes only:
- Template-code alias decisions for skeleton B-wave semantics.
- MVP assertion surface for `TC-B-001/002/003/004/006/007/008/009/010/011/012`.
- Deferred product branches for `TC-B-013` and non-MVP warning UI behavior.
- Stable backend error code expectations for automation.

## Explicit Non-Closure

Do not:
- modify backend code
- modify pytest automation handlers
- modify frontend UI
- modify skeleton data
- implement deadline, reply-chain, fee, bill, payment, or commission rules

## Remaining Follow-Up Task IDs

- `BE-B-OA-WIZARD-READINESS-01`
- `BE-B-OA-REPLY-READINESS-01`
- `BE-B-OA-FINANCE-READINESS-01`
- `PRODUCT-B-NEED-REPLY-DEADLINE-EDIT-CONTRACT-01`

## Allowed Files

- `tasks/product/PRODUCT-B-OA-WIZARD-CONTRACT-01.md`
- `docs/product/PRODUCT-B-OA-WIZARD-CONTRACT-01.md`
- `artifacts/PRODUCT-B-OA-WIZARD-CONTRACT-01/**`

## Verification Commands

```bash
test -f tasks/product/PRODUCT-B-OA-WIZARD-CONTRACT-01.md
test -f docs/product/PRODUCT-B-OA-WIZARD-CONTRACT-01.md
rg -n "OA_NOTICE|OA_IN|OA_REPLY_LIMIT|OA_REPLY|OfficialDueDate|ReplyTo|OA_FEE|deferred" docs/product/PRODUCT-B-OA-WIZARD-CONTRACT-01.md
./scripts/task_validate.sh PRODUCT-B-OA-WIZARD-CONTRACT-01
```

## Evidence Path

- `artifacts/PRODUCT-B-OA-WIZARD-CONTRACT-01/results.jsonl`
- `artifacts/PRODUCT-B-OA-WIZARD-CONTRACT-01/summary.md`
- `artifacts/PRODUCT-B-OA-WIZARD-CONTRACT-01/git/diff.patch`
