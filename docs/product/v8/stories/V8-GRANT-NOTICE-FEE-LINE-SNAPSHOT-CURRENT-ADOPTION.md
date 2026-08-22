# Story V8-GRANT-NOTICE-FEE-LINE-SNAPSHOT-CURRENT-ADOPTION

- Status: `READY_FOR_REVIEW`.
- Risk: `PROTECTED`.
- External prerequisite task:
  `FPMS-V8-GRANT-NOTICE-FEE-LINE-SNAPSHOT-20260713-01`.
- Current product/test anchor: `83d014fb825c76e90c53821c7db9ed7f3cd49436`.
- Current integration inspection commit: `89fa7e1`.
- Authority: the exact frozen task contract, V8 domain contract, and the independently
  accepted document-evidence review-service dependency.

## Observable outcome and exact paths

The pure read-only parser accepts only the frozen `GrantFeeLines` grammar, binds the exact
source document and reviewed evidence identity/hash, preserves line order, emits the exact
canonical V1 JSON plus bare SHA-256, and fails closed without SQL, mutation, file access,
rate lookup, eligibility decision or downstream write.

Current-tree scope is exactly:

- `backend/app/modules/documents/grant_fee_lines.py`
- `backend/tests/test_v8_grant_notice_fee_line_snapshot.py`

Both Git blobs are byte-identical between the historical product anchor and current HEAD.
No product or test byte is adopted from an uncommitted worktree.

## Current verification

- exact focused current-tree test: `46 passed`, one dependency warning;
- scoped Ruff on the two paths: PASS;
- exact diff check: PASS;
- `git diff 83d014f HEAD` on the two paths: empty;
- source blob: `e27a994f26aa48cae01cffd216220cc690d8e291` at both commits;
- test blob: `aabda6a78306a3ad81cb771e29cdf494bd26e8e3` at both commits.

Independent High review must inspect the exact contract and current bytes, independently
rerun the focused test and scoped checks, and approve P0/P1/P2 `0/0/0` before this external
prerequisite becomes `CURRENT_VERIFIED` in the lean ledger.

## Non-goals and rollback

No parser change, second callable, adapter, lifecycle event, fee amount, eligibility rule,
schema/migration, OCR/PDF, database access or downstream task implementation. Rollback
removes only this current-adoption story, its independent receipt and later ledger story
entry; it does not revert the already-present parser/test bytes.
