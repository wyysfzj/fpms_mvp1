# REPO-TASK-GATE-JSONL-STRUCTURAL-VALIDATION-20260714-01

Status: PASS / INDEPENDENT REVIEW APPROVED 2026-07-14
Program: `FPMS-POSTDEMO-V8-ULTRA-CONTRACT-DELTA-3-20260714-01`
Execution lane: `H3-0` / single lane
Risk tier: `HIGH` — repository governance and task-acceptance semantics
Executor role: Repository governance worker

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-14-fpms-v8-ultra-contract-freeze-delta-3.md`, only `Governance G1 — structural JSONL repository task gate` and `High execution handoff`
- `tasks/batches/FPMS-POSTDEMO-V8-ULTRA-CONTRACT-DELTA-3-20260714-01.md`, row `07`
- Existing behavior in `scripts/task_validate.sh`

This task is contract-frozen by the delta-3 Ultra materialization. High must execute the
contract directly and must not reopen the broader design unless implementation proves a
specific contradiction.

## Story Shape Classification

- `shared_file_density`: high; `scripts/task_validate.sh` is a repository-wide acceptance gate and has one serialized owner in this lane.
- `prereq_dependency_density`: low; G1 is the first delta-3 High execution lane and has no product prerequisite.
- `be_fe_coupling`: none.
- `evidence_cost`: high; the changed gate must validate its own task evidence without weakening fail-closed acceptance.
- `chosen_runbook`: `P0-single-lane-story`

## Task Contract Profile

Task Contract Profile: `TC-REPOSITORY-GOVERNANCE`

- RED expectation: the new stdlib regression test fails against the current whitespace-sensitive `grep` implementation on at least one frozen structural case.
- GREEN expectation: the exact test module passes after the smallest structural-validation change, while the existing missing-artifact checks and success output remain intact.

## Exact Closure Slice

Replace only the whitespace-sensitive lint/test success `grep` checks in
`scripts/task_validate.sh` with Python-standard-library structural validation of
`artifacts/<TASK-ID>/results.jsonl`.

The validator must read the file line by line, ignore whitespace-only lines, require every
nonempty line to decode as a JSON object, and accept the task only when the decoded records
contain at least one exact successful `lint` record and at least one exact successful
`test` record. Add one repository-level stdlib regression test module that proves this
contract through the public shell script.

## Frozen Observable Contract

### JSONL structure and fail-closed behavior

- Parse each nonempty physical line independently with Python's standard-library `json`
  module. A JSON value split over multiple physical lines is not one JSONL record.
- Every nonempty line must decode successfully and the decoded value must be a JSON object.
  Malformed JSON and valid JSON arrays, strings, numbers, booleans, or `null` fail the
  whole invocation with a nonzero exit code.
- A malformed or non-object line must produce a concise diagnostic that includes its
  one-based physical line number. No exact prose beyond the visible line number is frozen.
- Whitespace-only lines are ignored. JSON whitespace, object key order, and additional
  fields do not affect validity.
- A valid object is a successful lint record only when `record.get("step") == "lint"`,
  `type(record.get("rc")) is int`, and `record.get("rc") == 0`.
- A valid object is a successful test record only when `record.get("step") == "test"`,
  `type(record.get("rc")) is int`, and `record.get("rc") == 0`.
- JSON `false`, string `"0"`, and floating-point `0.0` are not successful return codes,
  even though Python equality could otherwise equate some of them with integer zero.
- Step names are exact and case-sensitive. A fake escaped substring such as
  `\"step\":\"lint\"` or `\"rc\":0` inside an unrelated string field does not satisfy
  either required record.
- The file may contain earlier valid lint/test records with nonzero return codes. Later
  exact successful records for both required steps make the invocation pass; the validator
  must not treat an earlier RED/failure record as a permanent failure.
- Any malformed or non-object nonempty line remains fatal even if later exact successful
  records exist.
- If the structurally valid file lacks either required exact successful record, exit
  nonzero. This task adds no required evidence step beyond `lint` and `test`.

### Existing task-gate behavior to preserve

- Invocation still accepts exactly one `<TASK-ID>` argument; the existing usage and exit
  status behavior for a wrong argument count remains unchanged.
- Keep the existing relative artifact root `artifacts/<TASK-ID>` and exact prerequisite
  checks for the artifact directory, `summary.md`, `results.jsonl`, and `git/diff.patch`.
- Preserve the existing missing-input messages: `Missing artifacts`, `Missing summary`,
  `Missing results`, and `Missing git diff`.
- Print `Task Gate PASS` and exit zero only after all prerequisite and structural checks
  succeed.
- Use only shell plus Python standard-library facilities. Do not add `jq`, a Python
  package, or another runtime dependency.

## Exact Regression Test Contract

Create `scripts/tests/test_task_validate_jsonl.py` using only Python standard-library
`unittest`, `tempfile`, `pathlib`, `json`, and `subprocess` facilities as needed. Tests
must invoke the repository's `scripts/task_validate.sh` as a subprocess while using an
isolated temporary directory as the subprocess working directory. The temporary directory
owns all synthetic `artifacts/<TASK-ID>/**`; tests must not create repository evidence,
import backend `conftest.py`, open a product database, or write SQLite.

The test module must independently prove:

1. the four existing missing-input gates fail in order and retain their exact messages;
2. whitespace-only lines plus reordered keys, ordinary JSON whitespace, and extra fields
   pass when exact successful lint and test records exist;
3. a fake `"step":"lint"`/`"rc":0` substring inside an unrelated JSON string does not
   satisfy the lint requirement;
4. malformed JSON fails and reports its one-based physical line number;
5. each valid non-object JSON kind—array, string, number, boolean, and `null`—fails and
   reports its one-based physical line number;
6. for each required step, `rc` values `false`, `"0"`, and `0.0` do not count as success;
7. omitting either an exact successful lint record or an exact successful test record
   fails;
8. earlier valid nonzero lint/test records followed by later exact integer-zero successes
   pass; and
9. success returns zero and includes `Task Gate PASS` in output.

Tests may use helpers local to this one test module to create the temporary artifact tree;
do not add a reusable test framework or another test-support file.

## Explicit Non-Closure

Do not change the evidence schema, add a required evidence step, change evidence
generation, or reinterpret any step other than the existing `lint` and `test` gate
requirements. Do not modify `scripts/evidence_run.sh`, `scripts/release_gate.sh`, the
external `atomic-evidence-gates` skill/helper, historical evidence, existing artifact
contents, product code, backend/frontend tests, schema, migration, seed, or SQLite data.

Do not implement concurrent-wave ownership, peer validation, common-manifest anchoring,
or the G2 wrapper. Do not run release, product, backend, frontend, Playwright, repo-wide
Ruff, or SQLite-writing tests. Do not absorb another repository-governance closure.

## Dependencies and Serialized Ownership

### Prerequisites

- Ultra delta-3 materialization and its required independent reviews must be accepted, and
  the user must manually return execution to High.
- No product task or G2 implementation is a prerequisite for G1.

### High execution order

- Execute this task alone in `H3-0`.
- The assigned repository governance worker exclusively owns
  `scripts/task_validate.sh` and `scripts/tests/test_task_validate_jsonl.py` for the whole
  RED/GREEN/evidence/review cycle.
- Do not run another task-gate writer or shared-file verification concurrently.
- G2 starts in `H3-1` only after this task is independently accepted as PASS.

## Remaining Follow-Up Task IDs

- `REPO-CONCURRENT-WAVE-ATOMIC-EVIDENCE-VALIDATION-20260714-01` (`G2`)
- None beyond G2.

## Allowed Files

- `tasks/repo/REPO-TASK-GATE-JSONL-STRUCTURAL-VALIDATION-20260714-01.md`
- `scripts/task_validate.sh`
- `scripts/tests/test_task_validate_jsonl.py`
- `artifacts/REPO-TASK-GATE-JSONL-STRUCTURAL-VALIDATION-20260714-01/**`

No other source, test, task, manifest, design, plan, skill, history, or shared-ownership
file is authorized. Preserve and subtract the dirty baseline when applicable.

## High TDD Runbook

1. Capture the dirty baseline for every allowlisted path before implementation.
2. Add only the frozen stdlib subprocess tests, then run the exact unittest command and
   preserve a RED caused by the current text-grep behavior.
3. Replace only the two text-grep decisions with the minimum stdlib structural validator.
4. Run the exact GREEN unittest and scoped syntax/compile/diff checks.
5. Generate task-local evidence, obtain independent review, run the repository task gate,
   and directly run the external atomic evidence helper. This H3-0 lane has no peers and
   must not call the not-yet-implemented G2 wrapper.

If a second shared file, new evidence requirement, external-helper change, or peer-aware
contract becomes necessary, stop this lane and escalate; do not stretch this task.

## Verification Commands

### RED

- After creating the test module but before changing the shell validator:
  `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v scripts.tests.test_task_validate_jsonl`
- Expected status: nonzero, with at least one failure proving the old whitespace-sensitive
  text matching does not satisfy the frozen structural behavior. A missing test module or
  test syntax/import error is not an acceptable RED.

### GREEN and task-scoped checks

- Shell syntax: `bash -n scripts/task_validate.sh`
- Python compile without repository bytecode output:
  `PYTHONPYCACHEPREFIX="${TMPDIR:-/tmp}/fpms-g1-pycache" python3 -m py_compile scripts/tests/test_task_validate_jsonl.py`
- Exact stdlib regression test:
  `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v scripts.tests.test_task_validate_jsonl`
- Scoped whitespace/error check:
  `git diff --check -- scripts/task_validate.sh scripts/tests/test_task_validate_jsonl.py tasks/repo/REPO-TASK-GATE-JSONL-STRUCTURAL-VALIDATION-20260714-01.md`
- Scope validation: record a `scope` evidence step proving the baseline-subtracted patch
  contains only the four allowlist entries above; generated task evidence must remain
  under this task's artifact directory.
- Independent review: record one `independent_review` evidence step approving the exact
  structural contract, preserved legacy checks, allowlist, and non-closure boundary.
- Repository task gate, after complete evidence exists:
  `./scripts/task_validate.sh REPO-TASK-GATE-JSONL-STRUCTURAL-VALIDATION-20260714-01`
- Direct external atomic helper, single lane with no peer/wrapper arguments:
  `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate REPO-TASK-GATE-JSONL-STRUCTURAL-VALIDATION-20260714-01 --required-step lint --required-step test --required-step independent_review --required-step scope`

Do not run `scripts/release_gate.sh` or any product/full-repository verification command.

## Expected Verification Status

- The intentional pre-implementation unittest is nonzero for the named behavioral reason.
- `bash -n`, Python compile, the post-implementation unittest, `git diff --check`, scoped
  evidence, independent review, the repository task gate, and the direct external atomic
  helper all return `0`.
- The successful task-gate invocation emits `Task Gate PASS`.

## Evidence Path

- `artifacts/REPO-TASK-GATE-JSONL-STRUCTURAL-VALIDATION-20260714-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, plus
  `baseline_allowlist.diff` and `baseline_external_files.txt` when the task starts from a
  dirty worktree.

## Done Definition

The exact RED demonstrates the old text matcher's defect; the minimum allowlisted change
implements structural JSONL validation; every frozen positive, negative, type-strictness,
line-number, and early-failure/later-success regression passes; existing missing-input
behavior and `Task Gate PASS` remain; task-scoped syntax/compile/diff/scope checks pass;
an independent reviewer accepts the exact closure and non-closure; complete task evidence
exists; the changed repository task gate and direct external atomic helper both pass.
Only then may this task be marked `PASS`.
