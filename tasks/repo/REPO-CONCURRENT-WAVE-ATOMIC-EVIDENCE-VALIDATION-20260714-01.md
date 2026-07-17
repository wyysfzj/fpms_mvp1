# REPO-CONCURRENT-WAVE-ATOMIC-EVIDENCE-VALIDATION-20260714-01

Status: PASS / INDEPENDENT REVIEW APPROVED 2026-07-14
Program: `FPMS-POSTDEMO-V8-ULTRA-CONTRACT-DELTA-3-20260714-01`
Materialization row: `08`
Execution lane: `H3-1` / single lane
Risk tier: `HIGH` — repository governance, evidence ownership, and task-acceptance semantics
Executor role: Repository governance worker

## Design References

- `AGENTS.md`
- `docs/superpowers/specs/2026-07-14-fpms-v8-ultra-contract-freeze-delta-3.md`, only `Governance G2 — concurrent-wave atomic evidence validator`, `Mandatory execution rule after G2`, and `High execution handoff`
- `tasks/batches/FPMS-POSTDEMO-V8-ULTRA-CONTRACT-DELTA-3-20260714-01.md`, row `08` and `Common execution-manifest rule`
- `tasks/repo/REPO-TASK-GATE-JSONL-STRUCTURAL-VALIDATION-20260714-01.md` (`G1` prerequisite)
- `/Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py`, read-only external helper behavior

This task is contract-frozen by delta-3 Ultra materialization. High must execute this
contract directly and must not reopen broad design or source analysis unless
implementation proves one specific contradiction.

## Story Shape Classification

- `shared_file_density`: high; this wrapper becomes the repository-wide validation entry point whenever a declared wave has post-init peer dirt, while its two implementation files have one exclusive owner.
- `prereq_dependency_density`: high; G1 must be independently accepted first, and every later peer-aware wave depends on this governance gate.
- `be_fe_coupling`: none; this is repository tooling with no backend or frontend runtime surface.
- `evidence_cost`: high; acceptance must prove exact ownership, dirty-baseline subtraction, isolated delegation, and fail-closed cleanup without weakening the external helper.
- `chosen_runbook`: `P0-prereq-heavy-story`

## Task Contract Profile

Task Contract Profile: `TC-REPOSITORY-GOVERNANCE`

- RED expectation: the complete stdlib test module loads and runs, but at least one frozen public-CLI behavior fails because the repository wrapper does not yet exist. A missing test module, test syntax error, or broken test fixture is not an acceptable RED.
- GREEN expectation: the exact stdlib suite passes after adding the smallest wrapper that proves common-manifest ownership and delegates validation in isolation, while the external helper, evidence schema, main worktree, and all product files remain unchanged.

## Exact Closure Slice

Add one repository wrapper, `scripts/atomic_evidence_validate.py`, and its one stdlib
regression module, `scripts/tests/test_atomic_evidence_validate.py`.

With no declared peer, the wrapper must directly invoke the existing external atomic
evidence helper and preserve its behavior and return code. With one or more declared
peers, the wrapper must prove that the current task and every peer are uniquely anchored
to one common authoritative execution manifest, own non-overlapping exact allowlists,
and account for all post-init external worktree dirt. Only after that proof may it create
a temporary local clone containing the committed baseline plus the current task alone
and delegate the current task's evidence validation to the unchanged external helper.

This is one repository-governance closure. The test module is the regression proof for
the same wrapper behavior, not a second closure slice.

## Frozen CLI Contract

The peer-aware public CLI is exactly:

```bash
python3 scripts/atomic_evidence_validate.py <TASK-ID> \
  --required-step lint --required-step test \
  --required-step independent_review --required-step scope \
  --manifest <COMMON-EXECUTION-BATCH-MANIFEST> \
  --concurrent-task <PEER-TASK-ID>
```

- `--required-step` and `--concurrent-task` are repeatable.
- Each peer task ID must be unique and must differ from `<TASK-ID>`.
- When at least one peer is present, `--manifest` is required exactly once.
- When no peer is present, `--manifest` is forbidden. The wrapper must immediately invoke
  `/Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate`
  for the current task, forward every supplied `--required-step`, preserve stdout and
  stderr, and exit with the helper's exact return code.
- Invalid argument combinations fail nonzero before evidence validation. No exact error
  prose is frozen, but the diagnostic must identify the rejected argument relationship.

## Fail-Closed Ownership Proof

All peer-aware checks below must pass before the wrapper creates a clone or invokes the
external helper. CLI assertions alone are never ownership evidence.

### Task metadata and manifest identity

1. Locate the repository root from Git and load
   `artifacts/<ID>/task.json` for the current task and every peer.
2. Each metadata file must be a JSON object whose `task_id`, `task_file`, `allowlist`, and
   `repo_root` are present and match the active repository and declared task. Missing,
   malformed, wrong-type, or mismatched values fail closed.
3. Each `task_file` must be one normalized repository-relative task-file path. Its file
   stem must equal the exact task ID.
4. The one `--manifest` path must identify a repository-local regular file. Parse it
   structurally and support both accepted manifest forms:
   - a `## NNN. <TASK-ID>` entry paired with an exact
     `- Task file: \`path\`` line; and
   - a Markdown table row containing the exact task ID and exact task-file path.
5. The current task and every declared peer must each have exactly one unique ID-to-path
   row in that same manifest. Missing IDs, missing paths, repeated IDs, repeated paths,
   cross-row mismatches, or a task-file path that differs from `task.json` fail closed.
6. The explicit current-plus-peer set is the active validation wave. The wrapper does
   not infer peers, merge manifests, or schedule work.

### Exact allowlist contract

1. Structurally parse the `## Allowed Files` section of every active task file. Require
   one unambiguous list of path entries and reject missing, duplicate, or malformed
   entries.
2. Normalize every entry as a repository-relative POSIX path. Reject absolute paths,
   any `..` segment, empty paths, directory allowlists, symlink paths or escapes, and
   fuzzy glob syntax.
3. The only permitted glob is that task's own exact
   `artifacts/<TASK-ID>/**` evidence family. It may not name another task's artifacts.
   Every other entry must identify one exact file or one exact tracked deletion state.
4. After normalization, the task-file allowlist and `task.json.allowlist` must be exactly
   equal as sets. Neither source is allowed to broaden or omit the other.
5. Compare every active task's non-evidence exact paths pairwise. Exact collisions and
   path-prefix ownership collisions fail. One path or subtree cannot be claimed by two
   active tasks, and this wrapper never authorizes shared ownership.

### NUL-safe current-worktree accounting

1. Read current status only through:

   ```bash
   git status --porcelain=v1 -z --untracked-files=all
   ```

2. Parse the NUL-delimited porcelain record structure; do not split on whitespace and do
   not infer renames from a textual ` -> ` substring.
3. Any rename or copy status is rejected explicitly. Consume and report both paths from
   its NUL record so neither side can evade ownership validation.
4. Read the current task's init-time
   `artifacts/<TASK-ID>/baseline_external_files.txt` when present. Do not rewrite it or
   append an ignore.
5. Every dirty path outside the current task's allowlist must be either an exact captured
   baseline-external path or owned by exactly one declared peer allowlist. Unknown dirt
   and multiply owned dirt fail closed. Peer artifact dirt is recognized only by that
   peer's exact `artifacts/<PEER-TASK-ID>/**` entry.
6. A peer named only on the command line, without matching task metadata, task-file
   allowlist, and common-manifest identity, grants no scope exception.

## Isolated External-Helper Delegation

After the complete ownership proof succeeds, the peer-aware path must:

1. Create a temporary local clone from the current repository's committed baseline
   without network access.
2. Copy into that clone only the current task's existing exact allowlisted files, apply
   its exact allowlisted deletion states, and copy its complete
   `artifacts/<TASK-ID>/**` family.
3. Do not copy peer source, peer tests, peer task files, peer evidence, unknown dirt, or
   other baseline-external modifications into the clone.
4. From the clone, invoke the unchanged external helper as:

   ```bash
   python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate <TASK-ID> --required-step <STEP> ...
   ```

   Preserve the supplied required-step order, forward the helper's stdout and stderr
   without reinterpretation, and exit with its exact return code.
5. Remove the temporary directory in a `finally` path after success, helper failure, or
   wrapper exception.
6. Never commit, push, reset, clean, stash, or rewrite the main worktree. Never rewrite
   current or peer evidence to make validation pass.

## Exact Regression Test Contract

Create `scripts/tests/test_atomic_evidence_validate.py` using only Python standard-library
`unittest`, `unittest.mock`, `tempfile`, `pathlib`, `json`, `shutil`, and `subprocess`
facilities as needed. Tests must use temporary Git repositories and public subprocess
behavior for repository integration. They must not import backend `conftest.py`, open a
product database, or write SQLite.

The test module must independently prove:

1. no-peer invocation rejects a manifest, delegates directly to the exact external
   helper when no manifest is supplied, forwards all required steps and output, and
   propagates zero and nonzero helper return codes;
2. a valid current task plus two non-overlapping peers succeeds under one common
   manifest, with coverage for both accepted manifest entry forms;
3. peer mode rejects a missing manifest, repeated manifest argument, a peer equal to the
   current task, and duplicate peer IDs;
4. manifest task ID/path absence, duplication, and mismatch each fail closed;
5. missing or mismatched `task.json` identity, task path, repository root, or allowlist
   fails closed;
6. a task-file `## Allowed Files` set that differs from `task.json.allowlist` fails;
7. absolute paths, `..`, directory allowlists, non-evidence globs, foreign artifact
   globs, symlinks, and symlink escapes fail;
8. exact and path-prefix allowlist overlap fails before helper invocation;
9. current external dirt captured at init is accepted, one declared peer's exact dirt is
   accepted, unknown dirt fails, and dirt owned by multiple peers fails;
10. NUL-safe status parsing preserves filenames containing whitespace or the text
    ` -> `, while real rename and copy records reject both recorded paths;
11. the temporary clone contains current files, current deletion states, and the current
    artifact family, but excludes peer files and peer artifacts; and
12. helper stdout/stderr/return-code propagation and temporary-directory cleanup hold on
    success and nonzero helper exit.

Local helpers may remain inside this single test module. Do not add a reusable test
framework or another support file.

## Explicit Non-Closure

Do not modify the external `atomic-evidence-gates` skill or helper, G1 or
`scripts/task_validate.sh`, the evidence schema, evidence generation, baseline files,
`scripts/evidence_run.sh`, `scripts/release_gate.sh`, historical evidence, the delta-3
manifest, AGENTS governance, or release semantics. Do not implement product, backend,
frontend, API, UI, permission, lifecycle, fee, document, schema, migration, seed, or
business behavior.

Do not allow shared ownership, blanket-ignore concurrent dirt, infer undeclared peers,
merge tasks from different manifests, add a second wrapper, or absorb a product guard.
Do not run release, product, backend, frontend, Playwright, repo-wide Ruff, or
SQLite-writing verification.

## Dependencies and Serialized Ownership

### Prerequisites

- The delta-3 materialization controller and both independent reviews must be accepted,
  and the user must manually return execution to High.
- `REPO-TASK-GATE-JSONL-STRUCTURAL-VALIDATION-20260714-01` (`G1`) must be independently
  accepted as PASS before evidence initialization or any edit for this task.

### High execution order and ownership

- Execute this task alone in `H3-1`; it has no peers during its own implementation or
  validation.
- The assigned repository governance worker exclusively owns
  `scripts/atomic_evidence_validate.py` and
  `scripts/tests/test_atomic_evidence_validate.py` for the complete RED/GREEN/evidence
  and review cycle. No shared owner is permitted.
- G2 uses no SQLite queue and performs no backend import, but shared-file verification
  remains serialized.
- Before G2 is accepted, the two product guards may be inspected read-only but must not
  initialize evidence, edit, or seek acceptance.
- After G2 is accepted, every task with post-init peer dirt must name all active peers
  from one common authoritative execution manifest and validate through this wrapper.
  A single-lane task with no peer may continue to invoke the external helper directly or
  use this wrapper's no-peer direct-helper path.

## Remaining Follow-Up Task IDs

- `FPMS-V8-DE-RAW-ATTACHMENT-REGISTRATION-GUARD-20260714-01`
- `FPMS-V8-DE-EXTERNAL-SUBMISSION-ROLE-ALLOWLIST-20260714-01`
- Every later task ID whose approved High execution manifest declares peers and whose
  validation observes post-init peer dirt; each remains its own atomic task.
- No further G2 implementation task.

## Allowed Files

- `tasks/repo/REPO-CONCURRENT-WAVE-ATOMIC-EVIDENCE-VALIDATION-20260714-01.md`
- `scripts/atomic_evidence_validate.py`
- `scripts/tests/test_atomic_evidence_validate.py`
- `artifacts/REPO-CONCURRENT-WAVE-ATOMIC-EVIDENCE-VALIDATION-20260714-01/**`

No manifest, external skill, G1 file, product file, backend/frontend test, historical
evidence family, or shared-ownership file is authorized. Preserve and subtract the dirty
baseline when applicable.

## High TDD Runbook

1. Confirm the materialization handoff and independently accepted G1 gate, then verify
   this H3-1 lane has no peer or competing owner.
2. Initialize task evidence with exactly the four allowed entries above, preserving the
   current dirty baseline before source or test edits.
3. Add only the frozen stdlib test module and run the exact unittest command to RED. The
   failure must demonstrate absent wrapper behavior through the public CLI.
4. Add the minimum stdlib wrapper one behavior at a time: no-peer delegation, metadata
   and common-manifest identity, exact allowlist ownership, NUL-safe dirt accounting,
   then isolated helper delegation and cleanup.
5. Run the exact GREEN unittest, compile check, scoped diff check, scope evidence, and
   independent repository-governance review.
6. Finalize complete task-local evidence, run the repository task gate, then self-validate
   this single-lane task through the wrapper with no manifest and no peer. That final
   wrapper invocation must take the direct external-helper path.

If implementation requires a shared owner, external-helper edit, evidence-schema change,
second source/test file, or relaxed ownership rule, stop and escalate this lane. Do not
stretch the task.

## Verification Commands

### Dependency gate

- `./scripts/task_validate.sh REPO-TASK-GATE-JSONL-STRUCTURAL-VALIDATION-20260714-01`
- Expected status: `0` before evidence initialization or editing begins.

### RED

- After creating the test module but before creating the wrapper:
  `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v scripts.tests.test_atomic_evidence_validate`
- Expected status: nonzero because at least one public-CLI wrapper behavior is absent. A
  missing test module, syntax error, or fixture failure is not an acceptable RED.

### GREEN and task-scoped checks

- Python compile without repository bytecode output:
  `PYTHONPYCACHEPREFIX="${TMPDIR:-/tmp}/fpms-g2-pycache" python3 -m py_compile scripts/atomic_evidence_validate.py scripts/tests/test_atomic_evidence_validate.py`
- Exact stdlib regression test:
  `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v scripts.tests.test_atomic_evidence_validate`
- Scoped whitespace/error check:
  `git diff --check -- scripts/atomic_evidence_validate.py scripts/tests/test_atomic_evidence_validate.py tasks/repo/REPO-CONCURRENT-WAVE-ATOMIC-EVIDENCE-VALIDATION-20260714-01.md`
- Scope validation: record a successful `scope` evidence step proving the
  baseline-subtracted patch contains only the four allowed entries and that no peer,
  manifest, external helper, G1, or product file changed.
- Independent review: record a successful `independent_review` evidence step approving
  CLI parity, manifest/task/allowlist identity, pairwise ownership, NUL-safe status,
  isolated-copy scope, helper return-code propagation, cleanup, and explicit
  non-closure.
- Repository task gate after complete evidence exists:
  `./scripts/task_validate.sh REPO-CONCURRENT-WAVE-ATOMIC-EVIDENCE-VALIDATION-20260714-01`
- Atomic evidence validation for this G2 task, single lane and no peer:

  ```bash
  python3 scripts/atomic_evidence_validate.py \
    REPO-CONCURRENT-WAVE-ATOMIC-EVIDENCE-VALIDATION-20260714-01 \
    --required-step lint --required-step test \
    --required-step independent_review --required-step scope
  ```

  No `--manifest` or `--concurrent-task` is permitted here. The wrapper must directly
  invoke the external helper and propagate its `0` return code.

Expected HTTP status codes: `None` (repository CLI only; no endpoint).

Do not run `scripts/release_gate.sh`, product tests, broad repository tests, or any
SQLite-writing command.

## Expected Verification Status

- The G1 dependency gate returns `0` before execution.
- The intentional pre-implementation unittest is nonzero only for the named absent
  wrapper behavior.
- Python compile, the post-implementation unittest, `git diff --check`, scoped evidence,
  independent review, and the repository task gate all return `0`.
- Negative helper-return and invalid-ownership cases are asserted inside the unittest;
  the complete GREEN unittest process returns `0`.
- The final no-peer wrapper command returns the unchanged external helper's `0` and
  leaves no temporary directory or main-worktree mutation.

## Evidence Path

- `artifacts/REPO-CONCURRENT-WAVE-ATOMIC-EVIDENCE-VALIDATION-20260714-01/**`
- Required PASS artifacts: `results.jsonl`, `summary.md`, `git/diff.patch`, plus
  `baseline_allowlist.diff` and `baseline_external_files.txt` when the task starts from a
  dirty worktree.

## Done Definition

G1 is independently accepted; the exact RED proves the missing wrapper behavior; only
the wrapper and its one stdlib regression module are added; every frozen direct-helper,
common-manifest identity, exact allowlist, ownership, NUL-safe status, isolated-clone,
return-code, and cleanup case is GREEN; baseline-subtracted scope and independent review
approve the one closure and its non-closure; complete task evidence exists; the repository
task gate passes; and the wrapper self-validates this task through its no-peer direct
external-helper path. Only then may this task be marked `PASS`.
