# Wave 12 Findings

- 2026-02-28 (resolved, non-blocking): `PE-BE-AN-02` task gate initially failed due `results.jsonl` schema mismatch (missing `step=lint/test`). Remediated via `scripts/evidence_run.sh`; gate now PASS.
- 2026-02-28 (non-blocking): `ruff` emitted pyproject deprecation warnings for top-level linter settings migration to `[tool.ruff.lint]`; checks still PASS.
- 2026-02-28 (final review): no unresolved Wave 12 issue for `PE-BE-AN-02`; allowlist, permission injection pattern, envelope semantics, and task gate/test evidence all PASS.
