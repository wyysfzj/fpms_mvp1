# FPMS-DEMO-ABC-EVIDENCE-REBUILD-20260817-01

Status: READY
Risk-Tier: HIGH
Risk-Class: PROTECTED
Closure-Tags: ["demo", "evidence", "acceptance"]
Task-Path: tasks/postdemo/FPMS-DEMO-ABC-EVIDENCE-REBUILD-20260817-01.md

## Exact Closure Slice

Reconstruct every local ABC implementation task's baseline-subtracted committed patch from its
frozen task commit to its immediately following implementation commit. Persist full commit/tree
identities, task-card digest, exact changed-file allowlist, binary-safe patch digest, reconstruction
timestamp and current candidate identity. Explicitly label evidence-only rehearsal tasks as having
no product diff rather than presenting an unexplained empty patch.

## Explicit Non-Closure

Do not change product code, rerun historical tests, manufacture independent review, change prior
result status, or call the product/release gate. Historical logs remain historical; current-candidate
verification belongs to the final rehearsal task.

## Remaining Follow-Up Task IDs

- `FPMS-DEMO-ABC-FINAL-REHEARSAL-20260817-01`

## Allowed Files

- `scripts/rebuild_demo_abc_evidence.py`
- `artifacts/FPMS-DEMO-ABC-*/git/**`
- `artifacts/FPMS-DEMO-ABC-EVIDENCE-REBUILD-20260817-01/**`

## Verification Commands

1. Script validates every implementation commit is the direct child of its frozen task commit.
2. Every implementation patch is non-empty and changed files equal its persisted allowlist.
3. Every stored patch SHA-256 recomputes exactly; evidence-only tasks carry an explicit marker.
4. Current candidate identity and clean tracked/untracked status are persisted.

## Evidence Path

- `artifacts/FPMS-DEMO-ABC-EVIDENCE-REBUILD-20260817-01/`

## Rollback

Revert the script commit and delete only the exact reconstructed generated evidence files.

## Done definition

No ABC implementation bundle retains an unexplained empty patch. Independent acceptance and current
rehearsal remain separate gates.
