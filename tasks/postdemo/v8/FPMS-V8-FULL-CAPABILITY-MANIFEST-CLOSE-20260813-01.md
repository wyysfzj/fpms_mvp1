# FPMS V8 Full Capability Manifest Close

Status: `IMPLEMENTATION`
Risk: `PROTECTED`
Runbook: `P0-prereq-heavy-story`

## Observable outcome

Close catalog Row199 against the current Git-native 283-row coverage ledger after the exact
Full CONFIG_REQUIRED successor is independently approved. Row199 becomes `CURRENT_VERIFIED`
through `V8-FULL-CAPABILITY-MANIFEST-CURRENT-ADOPTION`; the only unresolved rows afterward are
the ordered terminal rows 281, 282 and 283.

The Full result is `CAPABILITY_VERIFIED`, not production activation. Payment workbook and
service price remain `CONFIG_REQUIRED`, their source-decision gates remain `PENDING`, production
actions remain `409 / NO WRITE`, and TEST_ONLY remains isolated.

## Preconditions

- Input capability adoption commit `03138fbd5b1089634b84d353bf2abffd70777e41` is current.
- Full CONFIG_REQUIRED successor candidate
  `99316d6c83fe9c1c0e93b9703a5ea28509ea1ac6` and independent review receipt
  `dcb78fe978d3c655ef5fae7280ffba9e34b9bbeb` are reachable.
- Before this adoption the exact unresolved set is Row199 plus Rows281–283; every other catalog
  row resolves to a current or superseding story.

## Exact closure

1. Prove the frozen catalog remains exactly 283 ordered unique rows and Row199 retains its exact
   catalog identity and 29 gate requirements.
2. Prove every row except Row199 and terminal Rows281–283 is current before adoption.
3. Bind the reviewed Full successor and the exact current stories for rows170–198.
4. Adopt only Row199, leaving exactly Rows281–283 pending in their frozen order.
5. Record explicit Full capability/configuration status and no production activation claim.
6. Bind the exact candidate paths with the lean checker tree fingerprint and independent High
   review receipt.

## Non-closure

- Do not change the frozen catalog, source-decision registry, product code or runtime data.
- Do not configure or activate any real workbook, upload proof or service price version.
- Do not change Rows281–283 or execute inherited regression, Final, release or broad checks.
- Do not use the historical taskctl/evidence machinery or old manifest gate as current authority.
- Do not include `docs/product/v8/coverage-ledger.json` or final review receipt in the candidate
  fingerprint.

## Exact allowlist

- `tasks/postdemo/v8/FPMS-V8-FULL-CAPABILITY-MANIFEST-CLOSE-20260813-01.md`
- `docs/product/v8/stories/V8-FULL-CAPABILITY-MANIFEST-CLOSE.md`
- `scripts/tests/test_v8_full_capability_manifest_close.py`
- `scripts/tests/test_v8_full_config_required_successor.py`
- `docs/product/v8/reviews/V8-FULL-CAPABILITY-MANIFEST-CURRENT-ADOPTION.md`
- `docs/product/v8/coverage-ledger.json`

The story fingerprint may bind these existing immutable/current authority paths without editing
them:

- `tasks/postdemo/v8/FPMS-V8-FULL-MANIFEST-ACTIVATION-20260712-01.md`
- `tasks/postdemo/v8/FPMS-V8-FULL-CONFIG-REQUIRED-SUCCESSOR-20260813-01.md`
- `docs/product/v8/stories/V8-FULL-CONFIG-REQUIRED-SUCCESSOR.md`

`backend/uv.lock` remains unrelated and untouched.

## Verification and acceptance

```text
python3 -m pytest -q scripts/tests/test_v8_full_config_required_successor.py scripts/tests/test_v8_full_capability_manifest_close.py
python3 -m ruff check scripts/tests/test_v8_full_config_required_successor.py scripts/tests/test_v8_full_capability_manifest_close.py
python3 scripts/v8_lean_coverage_check.py --milestone inventory --integration-sha <candidate-sha>
git diff --check -- <exact allowlist>
```

The candidate requires independent High review with P0/P1/P2 `0/0/0`; the reviewer owns the
review receipt. Rollback reverts only the Row199 ledger adoption and this story metadata. It never
changes production configuration or business data.
