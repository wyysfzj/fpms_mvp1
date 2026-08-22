# REPO-DELTA3-PATH-ONLY-TABLE-MANIFEST-COMPATIBILITY-20260714-01

Status: PASS / INDEPENDENT REVIEW APPROVED 2026-07-14
Program: `FPMS-POSTDEMO-V8-ULTRA-CONTRACT-DELTA-3-20260714-01`
Risk tier: `HIGH` (authoritative evidence-validation governance)
Chosen runbook: `P0-single-lane-story`

## Discovery and Authority

The independently accepted G2 wrapper requires one common manifest for declared peers.
Its accepted table parser currently recognizes a row only when the exact task ID is a
separate cell beside the exact task-file path. The authoritative Delta-3 manifest instead
records each exact task-file path once, with no duplicate task-ID cell. Consequently the
frozen H3-2 peer command fails before isolated validation even though both exact task paths
are present once.

The observed reproduction is:

```text
atomic evidence validation rejected: manifest must contain exactly one row for
FPMS-V8-DE-RAW-ATTACHMENT-REGISTRATION-GUARD-20260714-01
```

This task resolves only that structural compatibility gap. The approved Delta-3 manifest,
its controller hashes, G2 history, and all product contracts remain unchanged.

## Story Shape Classification

- `shared_file_density=high` — the repository wrapper and its one regression module are
  shared governance owners and must be edited serially.
- `prereq_dependency_density=low` — G2 and the Delta-3 controller are already PASS.
- `be_fe_coupling=none` — repository CLI only.
- `evidence_cost=high` — fail-closed manifest ownership proof gates concurrent HIGH work.
- `chosen_runbook=P0-single-lane-story`.

## Exact Closure Slice

Extend only the G2 wrapper's Markdown-table manifest parsing. Determine the accepted table
shape from the table header, never from whether a data cell merely looks like an ID:

- An explicit-ID table has exactly one `Task ID` header and exactly one `Task file`
  header. Read both cells from every data row. The supplied ID is authoritative and must
  equal `Path(task_file).stem`; a mismatch fails closed and must never fall back to path
  derivation.
- A path-only table has no `Task ID` header and exactly one task-path header named either
  `Exact task-file path` or `Task file`. Each qualifying data row must contain one
  normalized repository-relative `.md` path in that column; derive its exact task ID only
  from `Path(task_file).stem`.
- Missing, repeated or mixed task headers do not select either shape and therefore cannot
  yield accepted task rows.

Existing downstream validation must continue to require each declared current/peer ID and
path exactly once, reject duplicate IDs or paths, and match `task.json.task_file` exactly.

The authoritative regression is the unchanged manifest:
`tasks/batches/FPMS-POSTDEMO-V8-ULTRA-CONTRACT-DELTA-3-20260714-01.md`. Its rows for
`FPMS-V8-DE-RAW-ATTACHMENT-REGISTRATION-GUARD-20260714-01` and
`FPMS-V8-DE-EXTERNAL-SUBMISSION-ROLE-ALLOWLIST-20260714-01` must parse as exact ID/path
pairs without editing that manifest.

## Exact TDD Contract

1. RED first in `scripts/tests/test_atomic_evidence_validate.py`: prove the public wrapper
   rejects an otherwise valid temporary peer manifest whose table rows contain one exact
   task-file path but no separate task-ID cell.
2. Add a repository regression that structurally parses the unchanged authoritative
   Delta-3 manifest and finds each H3-2 ID/path pair exactly once.
3. Add an explicit-ID mismatch regression proving that a wrong `Task ID` beside a valid
   path is rejected and never reinterpreted as a path-only row.
4. GREEN with the smallest header-aware table-parser change implementing the two exact
   shapes above. For path-only rows, the derived ID is the exact file stem.
5. Preserve all existing explicit-ID, heading, absence, duplication, mismatch, symlink,
   allowlist, dirty-worktree, isolated-clone, return-code, and cleanup regressions.
6. Use only Python standard-library test facilities already authorized by G2. Do not open
   a product database or run SQLite tests.

## Explicit Non-Closure

No edit to the Delta-3 manifest, its controller task/evidence, either H3-2 task contract,
the external atomic-evidence skill/helper, G1, evidence schema, release gate, product
source, backend/frontend test, migration, database, or customer/legal/fee behavior. Do not
accept multiple task paths in one row, infer an ID from prose, relax exact ID/path
cardinality, or merge peers across manifests.

## Dependencies and Serialization

- `REPO-CONCURRENT-WAVE-ATOMIC-EVIDENCE-VALIDATION-20260714-01` — PASS.
- `FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-3-20260714-01` — PASS.
- This task is the sole owner of the wrapper and regression module until PASS. No G2 or
  other repository-tool task may edit either path concurrently.
- This task performs no SQLite write and does not consume `GLOBAL_SQLITE_SERIAL_QUEUE`.

## Remaining Follow-Up Task IDs

- `FPMS-V8-DE-RAW-ATTACHMENT-REGISTRATION-GUARD-20260714-01` — retry only its incomplete
  peer-mode atomic validation after this task PASS.
- `FPMS-V8-DE-EXTERNAL-SUBMISSION-ROLE-ALLOWLIST-20260714-01` — use the corrected parser
  for its final peer-mode atomic validation after its own review/evidence gates PASS.

## Allowed Files

- `tasks/repo/REPO-DELTA3-PATH-ONLY-TABLE-MANIFEST-COMPATIBILITY-20260714-01.md`
- `scripts/atomic_evidence_validate.py`
- `scripts/tests/test_atomic_evidence_validate.py`
- `artifacts/REPO-DELTA3-PATH-ONLY-TABLE-MANIFEST-COMPATIBILITY-20260714-01/**`

No other path is authorized. Preserve and subtract the existing dirty baseline for both
shared implementation paths.

## Verification Commands

- Dependency gates:
  - `./scripts/task_validate.sh REPO-CONCURRENT-WAVE-ATOMIC-EVIDENCE-VALIDATION-20260714-01`
  - `./scripts/task_validate.sh FPMS-V8-ULTRA-CONTRACT-TASK-MATERIALIZATION-BATCH-3-20260714-01`
- RED/GREEN exact suite:
  - `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v scripts.tests.test_atomic_evidence_validate`
- Compile:
  - `PYTHONPYCACHEPREFIX="${TMPDIR:-/tmp}/fpms-delta3-manifest-compat-pycache" python3 -m py_compile scripts/atomic_evidence_validate.py scripts/tests/test_atomic_evidence_validate.py`
- Task-scoped Ruff/format:
  - `ruff check --fix scripts/atomic_evidence_validate.py scripts/tests/test_atomic_evidence_validate.py`
  - `ruff format scripts/atomic_evidence_validate.py scripts/tests/test_atomic_evidence_validate.py`
  - `ruff check scripts/atomic_evidence_validate.py scripts/tests/test_atomic_evidence_validate.py`
- Scoped diff:
  - `git diff --check -- scripts/atomic_evidence_validate.py scripts/tests/test_atomic_evidence_validate.py tasks/repo/REPO-DELTA3-PATH-ONLY-TABLE-MANIFEST-COMPATIBILITY-20260714-01.md`
- Scope validation must prove the baseline-subtracted patch contains only the three
  non-evidence allowlist destinations.
- Repository task gate:
  - `./scripts/task_validate.sh REPO-DELTA3-PATH-ONLY-TABLE-MANIFEST-COMPATIBILITY-20260714-01`
- Final no-peer atomic validation:
  - `python3 scripts/atomic_evidence_validate.py REPO-DELTA3-PATH-ONLY-TABLE-MANIFEST-COMPATIBILITY-20260714-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

Do not run product tests, SQLite, repository-wide Ruff/pytest, broad Playwright, the
release gate, or any command that edits the authoritative manifest.

## Evidence Path

- `artifacts/REPO-DELTA3-PATH-ONLY-TABLE-MANIFEST-COMPATIBILITY-20260714-01/**`

PASS requires the original structural RED, complete GREEN suite, compile and scoped-diff
checks, dirty-baseline subtraction, scope validation, independent governance/code review,
repository task gate, and final no-peer atomic evidence validation.

## Done Definition

The unchanged Delta-3 path-only table resolves both H3-2 peers to their exact task IDs and
paths; all prior fail-closed G2 behaviors remain GREEN; only the three non-evidence
allowlist paths appear in the scoped patch; independent review approves; task and atomic
evidence gates PASS; and no manifest, external helper, product path, or release gate moved.
