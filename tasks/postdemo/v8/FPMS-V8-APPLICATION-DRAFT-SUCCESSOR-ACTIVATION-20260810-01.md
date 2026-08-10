# FPMS-V8-APPLICATION-DRAFT-SUCCESSOR-ACTIVATION-20260810-01

Status: CONTRACT FROZEN / NOT STARTED
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Executor role: Team Lead / default
Repository risk: `HIGH`
Task Contract Profile: `TC-QA`

## Authority and Frozen Inputs

- `AGENTS.md`
- `docs/agents/README.md`
- `docs/agents/execution.md`
- `docs/agents/evidence.md`
- `docs/agents/domain-safety.md`
- `docs/agents/source-authority.md`
- Accepted lane manifest:
  `tasks/batches/FPMS-POSTDEMO-V8-APPLICATION-DRAFT-GATE-20260712-01.md`
- Accepted activation review:
  `docs/product/v8/reviews/V8-APPLICATION-DRAFT-GATE-MANIFEST-ACTIVATION-CURRENT-ADOPTION.md`
- Accepted manifest reviewed commit: `89447b9f9fae426ee31d678c16b91584d1c541f3`
- Accepted manifest adoption commit: `a1cbb50e1b22d1e0cea1cd569e8d05486b45546c`
- Accepted manifest preimage SHA-256:
  `bb73b877a50cce52155b9d137a92f95bb74ff8d82e406e2b072ee19fc22f9e5c`
- Successor product contract:
  `tasks/postdemo/v8/FPMS-V8-APPLICATION-INTERNAL-DRAFT-PAYMENT-SEPARATION-20260810-01.md`
- Frozen successor contract SHA-256:
  `2a04bd220a0d1c96b61b5d7bb027add302cb55fc1ba69575b8724503215a9937`

The rebind is authorized only while the accepted manifest preimage and successor task bytes match
the hashes above. Any drift pauses this task for a new independent contract review; it must not be
absorbed into this patch.

## Story Shape Classification

- `shared_file_density`: high
- `prereq_dependency_density`: low
- `be_fe_coupling`: low
- `evidence_cost`: high
- `chosen_runbook`: `P0-single-lane-story`

## Exact Closure Slice

Rebind the already accepted application-draft lane to the executable successor product contract.
The manifest remains a two-row lane with the existing activation controller first and exactly one
product row second.

The only semantic manifest change is:

```text
- tasks/postdemo/v8/FPMS-V8-APPLICATION-AUTO-DRAFT-POLICY-20260712-01.md
+ tasks/postdemo/v8/FPMS-V8-APPLICATION-INTERNAL-DRAFT-PAYMENT-SEPARATION-20260810-01.md
```

Update the corresponding execution-order prose only as required to name the internal-draft /
payment-separation successor and its task-owned serialized shared files. Do not change the lane's
policy, controller, count, ordering, activation state, dependencies or release boundary.

## Immutable Manifest Contract

After the rebind, the exact ordered task-file list is:

1. `tasks/postdemo/v8/FPMS-V8-APPLICATION-DRAFT-MANIFEST-ACTIVATION-20260712-01.md`
2. `tasks/postdemo/v8/FPMS-V8-APPLICATION-INTERNAL-DRAFT-PAYMENT-SEPARATION-20260810-01.md`

The superseded path
`tasks/postdemo/v8/FPMS-V8-APPLICATION-AUTO-DRAFT-POLICY-20260712-01.md` must occur zero times in
the manifest. The successor path must occur exactly once. The activation controller remains the
first row and the sole `SELF_PENDING` identity; this rebind task is not inserted as a third lane
row.

All of these accepted manifest values must remain byte-for-value unchanged:

- title, status, program and controller task
  `FPMS-V8-APPLICATION-DRAFT-MANIFEST-ACTIVATION-20260712-01`;
- `Manifest phase: lane` and `Task count: 2`;
- `DG-FEE-APPLICATION-DRAFT:GLOBAL` and `APPROVED_POLICY`;
- decision version `customer-decision:2026-08-10:v8-full-batch-scheme-a:v1`;
- decision source SHA-256
  `e6cfd648f1d366e27bde3f74310f00033a6db60ce55d850d2e668764745faace`;
- source commit `e5a41c8d07f11d1b0dec68891ef7bef53312f883` and adoption commit
  `72877386974cd57c720b7c622e6b00ca49c03d7d`;
- `reviewed-real-application-fee-notice`, `one-internal-pending-review-draft`, and
  `client-instruction-required`;
- `independent-high-zero-finding-required`, `after-activation-pass-only`, and
  `globally-serialized`;
- all three `CURRENT_VERIFIED` prerequisite rows, their order and exact successor identities;
- fail-closed gate language, no-payment language, and the explicit non-closure.

The focused test is updated, not weakened. It must keep every existing metadata and prerequisite
assertion and additionally prove the exact controller, two-row successor order, successor
uniqueness and complete absence of the superseded product row.

## Dependencies and Serialization

Required before edit:

- the accepted manifest/review commits and all manifest-named prerequisite successor histories
  remain reachable;
- the accepted manifest preimage matches its frozen hash;
- the successor product task exists, passes atomic task structure validation and matches its frozen
  hash;
- no other owner is editing the lane manifest or focused test.

The manifest and focused test are shared governance files. One owner edits them serially; the same
owner runs RED/GREEN, scope capture and evidence close before releasing ownership. The successor
product task remains blocked until this activation receives an independent HIGH terminal PASS.
This focused file-reading test performs no SQLite write, but the manifest's existing global SQLite
serialization declaration remains unchanged.

## Explicit Non-Closure

- No product-code, API, UI, schema, migration, model, seed, payment, obligation, draft or runtime
  decision-gate change.
- No customer source, source registry, adoption document, coverage ledger, catalog or other
  manifest change.
- No edit to the old activation task, old product task or successor product task.
- No third lane row, second customer gate, dependency refresh, status promotion, commit/hash
  substitution, release claim, test deletion or assertion weakening.
- No artifact or evidence from the accepted original activation is rewritten; this successor
  activation has its own evidence bundle.

## Remaining Follow-Up Task IDs

- `FPMS-V8-APPLICATION-INTERNAL-DRAFT-PAYMENT-SEPARATION-20260810-01`, which may start only after
  this task reaches independently accepted terminal PASS.

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-APPLICATION-DRAFT-SUCCESSOR-ACTIVATION-20260810-01.md`
- `tasks/batches/FPMS-POSTDEMO-V8-APPLICATION-DRAFT-GATE-20260712-01.md`
- `backend/tests/test_v8_application_draft_manifest_contract.py`
- `artifacts/FPMS-V8-APPLICATION-DRAFT-SUCCESSOR-ACTIVATION-20260810-01/**`

No other source, test, task, manifest, ledger, catalog, review or adoption path is authorized.
Preserve and subtract the complete initial tracked and untracked dirty baseline. Concurrent files
outside this allowlist remain other owners' work.

## Verification Commands

Test-first order is mandatory:

1. Update `backend/tests/test_v8_application_draft_manifest_contract.py` to define the exact
   successor and superseded task paths. Rename only the affected test for the successor meaning.
2. Preserve all current assertions and add assertions that:
   - the controller task is exactly the existing activation controller;
   - the task list is exactly `[existing activation task, successor product task]`;
   - task count is exactly `2`, paths are unique, the successor occurs once and the superseded path
     occurs zero times;
   - the activation remains the sole `SELF_PENDING` row;
   - all Scheme A values and three ordered prerequisite rows remain exact.
3. Run and preserve RED against the unchanged accepted manifest. Expected cause: the manifest's
   second row is still the superseded product path; no unrelated failure is accepted as RED.
4. Make the minimum manifest edit: replace the second task path and the directly corresponding
   execution-order prose. Then run one canonical GREEN.

Commands:

- RED:
  `cd backend && .venv/bin/pytest -q tests/test_v8_application_draft_manifest_contract.py`
- GREEN:
  `cd backend && .venv/bin/pytest -q tests/test_v8_application_draft_manifest_contract.py`
- Scoped format and check-only lint:
  `cd backend && .venv/bin/ruff check --fix tests/test_v8_application_draft_manifest_contract.py && .venv/bin/ruff format tests/test_v8_application_draft_manifest_contract.py && .venv/bin/ruff check tests/test_v8_application_draft_manifest_contract.py`
- Frozen-authority and scope checks:
  `shasum -a 256 docs/product/v8/customer-decisions/2026-08-10-v8-full-batch-scheme-a.txt tasks/postdemo/v8/FPMS-V8-APPLICATION-INTERNAL-DRAFT-PAYMENT-SEPARATION-20260810-01.md`
  `git diff --check -- tasks/postdemo/v8/FPMS-V8-APPLICATION-DRAFT-SUCCESSOR-ACTIVATION-20260810-01.md tasks/batches/FPMS-POSTDEMO-V8-APPLICATION-DRAFT-GATE-20260712-01.md backend/tests/test_v8_application_draft_manifest_contract.py`
- Task gate:
  `./scripts/task_validate.sh FPMS-V8-APPLICATION-DRAFT-SUCCESSOR-ACTIVATION-20260810-01`
- Atomic evidence:
  `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-APPLICATION-DRAFT-SUCCESSOR-ACTIVATION-20260810-01 --required-step lint --required-step test --required-step independent_review --required-step scope --required-step task_gate`

Do not run product tests, SQLite-writing tests, repo-wide checks, broad Playwright or release gates.

## Evidence Path

- `artifacts/FPMS-V8-APPLICATION-DRAFT-SUCCESSOR-ACTIVATION-20260810-01/**`

Required PASS evidence:

- `task.json`, `results.jsonl`, `summary.md`, `git/diff.patch`, command logs and complete dirty
  baseline artifacts;
- RED log proving only the old second-row path, then final GREEN and scoped Ruff logs;
- hash log proving the Scheme A source remains
  `e6cfd648f1d366e27bde3f74310f00033a6db60ce55d850d2e668764745faace` and the successor task
  remains `2a04bd220a0d1c96b61b5d7bb027add302cb55fc1ba69575b8724503215a9937`;
- scope evidence proving only this task file, the one accepted lane manifest, the focused test and
  this evidence tree changed after dirty-baseline subtraction;
- a manifest semantic diff proving exactly one product-row replacement plus only its directly
  corresponding execution-order wording, with all immutable values unchanged;
- one independent HIGH reviewer, not the implementer, with a single final
  `Verdict: APPROVED`, `P0: 0`, `P1: 0`, `P2: 0`, binding the final baseline-subtracted patch hash,
  current task hash, summary hash, manifest hash and focused-test hash;
- latest successful `lint`, `test`, `scope`, `independent_review`, `task_gate`, and
  `atomic_evidence` results.

## Done Definition

The accepted preimage and successor task hashes were verified; the exact old-row RED is preserved;
the manifest contains exactly the existing activation controller followed by the successor product
row and no old product row; every Scheme A source/version/hash, dependency and lane invariant is
unchanged; focused GREEN, scoped Ruff, scope and task gates pass; the independent HIGH review has
zero findings and binds current hashes; atomic evidence validates. Only then may this activation
report PASS and unblock the successor product task. Contract creation alone may report only
`TASK_CONTRACT_READY`.
