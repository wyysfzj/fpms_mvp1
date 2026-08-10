# Story — Grant-evidence Source API Verification-path Compatibility

- Risk: `PROTECTED` because it controls verification of an authority-management API.
- Status: `REVIEW_REQUIRED`.
- Amended task:
  `tasks/postdemo/v8/FPMS-V8-GRANT-EVIDENCE-SOURCE-CARRIER-API-20260810-01.md`.
- Amended task SHA-256:
  `252b73f40e21deebeeb1e44f61c94f7a4dee4c9106fc4d82e1a518529c8a3d52`.

## Concrete changed input

The frozen scoped-regression command names two test paths that do not exist anywhere in the
current integrated tree or reachable Git history:

- `backend/tests/test_v8_decision_gate_record_api.py`;
- `backend/tests/test_system_config_readiness_api.py`.

The same pre-existing route closures are currently and observably owned by:

- `backend/tests/test_v8_decision_gate_confirm_api.py`, which verifies decision-gate record and
  revoke HTTP behavior; and
- `backend/tests/test_system_params.py`, whose
  `test_config_readiness_reports_missing_seed_config` verifies
  `GET /api/v1/system/config-readiness`.

## Exact compatibility closure

For this API task only, replace its frozen scoped-regression command with:

```bash
cd backend && .venv/bin/pytest -q \
  tests/test_v8_decision_gate_confirm_api.py \
  tests/test_system_params.py
```

All other task bytes, RED/GREEN commands, acceptance-matrix items, allowed product paths,
dependency hashes, response/envelope/permission/transaction semantics and independent review
requirements remain exact and unchanged. The two replacement tests are read-only regression
inputs and are not added to the task's editable allowlist.

## Explicit non-closure

- No product, test, task, manifest, catalog, batch or accepted activation bytes change.
- No missing test is recreated, copied or renamed.
- No regression assertion is deleted or weakened.
- No generic path discovery or fallback is authorized.
- No old taskctl/evidence protocol is reactivated.

## Acceptance

One independent High reviewer must confirm that both obsolete paths are absent, both exact live
paths cover the intended existing routes, and this overlay changes only the scoped-regression
path selection. Approval requires `P0/P1/P2 = 0/0/0` before API RED begins.
