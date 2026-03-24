# Wave 16 Findings

- 2026-02-28 (resolved, non-blocking): `PE-BE-AN-06` task gate initially failed due `results.jsonl` schema mismatch (missing `step=lint/test`). Remediated via `scripts/evidence_run.sh`; gate now PASS.
- 2026-02-28 (final review): no unresolved Wave 16 issue for `PE-BE-AN-06`; allowlist, same-client/currency constraints, batch result contract, permission injection pattern, and task gate/test evidence all PASS.
