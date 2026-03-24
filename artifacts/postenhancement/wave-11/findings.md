# Wave 11 Findings

- 2026-02-28 (resolved, non-blocking): `PE-BE-AN-01` task gate initially failed due `results.jsonl` schema mismatch (missing `step=lint/test`). Remediated via `scripts/evidence_run.sh`; gate now PASS.
- 2026-02-28 (resolved): `backend/app/modules/annuity/service.py` previously had invalid syntax at line 36 (`) from exc`). Initial direct import check failed:
  - `cd backend && python3 -c 'import app.modules.annuity.service'`
  - `SyntaxError: invalid syntax`
- 2026-02-28 (re-validation): import now passes:
  - `cd backend && python3 -c 'import app.modules.annuity.service'` (exit `0`)
- 2026-02-28 (final review): no unresolved Wave 11 issue for `PE-BE-AN-01`; allowlist, task gate/test evidence, and syntax/import revalidation all PASS.
