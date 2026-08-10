# FPMS-V8-GRANT-SOURCE-SUCCESSOR-ACTIVATION-20260810-01

Status: CONTRACT RE-FROZEN / READY FOR INDEPENDENT HIGH REVIEW
Risk-Tier: HIGH
Closure-Tags: ["customer-decision", "governance", "lineage", "source-authority"]
Task-Path: tasks/postdemo/v8/FPMS-V8-GRANT-SOURCE-SUCCESSOR-ACTIVATION-20260810-01.md
Execution class: `CONTRACT FROZEN`
Chosen runbook: `P0-prereq-heavy-story`
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
  `tasks/batches/FPMS-POSTDEMO-V8-GRANT-SOURCE-GATE-20260712-01.md`
- Accepted activation review:
  `docs/product/v8/reviews/V8-GRANT-SOURCE-GATE-MANIFEST-ACTIVATION-CURRENT-ADOPTION.md`
- Accepted manifest candidate commits:
  `38097fae52db25882fd0204f40892755d349912f` and
  `2887519ff8535eb10b5b349718a61ca6ad8f8c67`
- Accepted manifest adoption commit: `9f7869c85868e5ac78f4682ea0af58a6fa90b4d1`
- Accepted manifest preimage SHA-256:
  `1c85ad98cfa6af6d5715b7f833f847547b0b4c907f7dee1dc43d5a3e5833c182`
- Focused manifest-test preimage SHA-256:
  `b31bb683a972778ae5fa85f42ce10ea634e4e36a2c7aecb059510e16fee506a0`
- Accepted Scheme A customer-decision/current-owner commits:
  `e5a41c8d07f11d1b0dec68891ef7bef53312f883` and
  `72877386974cd57c720b7c622e6b00ca49c03d7d`
- Decision version: `customer-decision:2026-08-10:v8-full-batch-scheme-a:v1`
- Customer-source path:
  `docs/product/v8/customer-decisions/2026-08-10-v8-full-batch-scheme-a.txt`
- Customer-source SHA-256:
  `e6cfd648f1d366e27bde3f74310f00033a6db60ce55d850d2e668764745faace`

The rebind is authorized only while every existing preimage/path/hash above and below remains
exact. Any drift pauses this task for a new independent contract review. Historical acceptance of
the five-row manifest does not approve the successor bytes.

## Current Exact Task-Path Bindings

The current repository contains and binds these exact task files:

| Ordered role | Exact task path | Current SHA-256 |
| --- | --- | --- |
| Existing activation controller | `tasks/postdemo/v8/FPMS-V8-GRANT-SOURCE-GATE-MANIFEST-ACTIVATION-20260712-01.md` | `3236a8ae708ee5740c4e19a49fbeaa377de0354d3b880c249b8c8dacefbd51f7` |
| Source carrier schema | `tasks/postdemo/v8/FPMS-V8-GRANT-EVIDENCE-SOURCE-CARRIER-SCHEMA-20260810-01.md` | `f3ec1e107fb8cba0f4c041d1949eb646c674a6609de78d9533d4784526874eb6` |
| Source carrier service | `tasks/postdemo/v8/FPMS-V8-GRANT-EVIDENCE-SOURCE-CARRIER-SERVICE-20260810-01.md` | `954960141ba75465176b01ab262a257d9b9128ab70303453173db7483429c502` |
| Source carrier API | `tasks/postdemo/v8/FPMS-V8-GRANT-EVIDENCE-SOURCE-CARRIER-API-20260810-01.md` | `252b73f40e21deebeeb1e44f61c94f7a4dee4c9106fc4d82e1a518529c8a3d52` |
| Existing ingestion service | `tasks/postdemo/v8/FPMS-V8-GRANT-EVIDENCE-INGESTION-SERVICE-20260712-01.md` | `82f7fe3ac496716dfe315f6eb698457aebb7966e5d9de083998f11f0ce193230` |
| Existing ingestion API | `tasks/postdemo/v8/FPMS-V8-GRANT-EVIDENCE-INGESTION-API-20260712-01.md` | `537f0defe2e8116af73fdc47fc040c454c32c7fb1871624b5698a4f67ce83445` |
| Existing candidate-read service | `tasks/postdemo/v8/FPMS-V8-GRANT-EVIDENCE-CANDIDATE-READ-SERVICE-20260712-01.md` | `daa6fddb220045e0d0ca4744be50bc5969eb20ae0db93c727106153e91d1e69d` |
| Existing candidate-list API | `tasks/postdemo/v8/FPMS-V8-GRANT-EVIDENCE-CANDIDATE-LIST-API-20260712-01.md` | `6f0c8ff6299f5f36bbdf05c6d5b7719501c7f2b00df64b481945732d9f5d3890` |

The source service, API and re-frozen ingestion-service task files are now materialized,
independently High reviewed with zero findings, committed, and bound by the exact hashes above.
Any later byte drift blocks RED and requires another independent re-freeze; manifest prose cannot
substitute for any task contract.

The current source-carrier implementation commits `35a72b5354cec8a1704a3550daddea9085af093f`
and `14f495db34b537e52441b985c7ab1bae2e5b082c` are evidence inputs only. They do not replace
independent acceptance of the schema task or authorize either missing successor contract.

## Story Shape Classification

- `shared_file_density`: high
- `prereq_dependency_density`: high
- `be_fe_coupling`: low
- `evidence_cost`: high
- `chosen_runbook`: `P0-prereq-heavy-story`

## Exact Closure Slice

Rebind the already accepted grant-source development lane from exactly five rows to exactly eight
ordered rows. Preserve the existing activation controller as row 001 and insert only the three
source-carrier prerequisites before the four existing ingestion/read rows.

After all materialization prerequisites above are hash-bound and independently accepted, the
exact ordered task-file list is:

1. `tasks/postdemo/v8/FPMS-V8-GRANT-SOURCE-GATE-MANIFEST-ACTIVATION-20260712-01.md`
2. `tasks/postdemo/v8/FPMS-V8-GRANT-EVIDENCE-SOURCE-CARRIER-SCHEMA-20260810-01.md`
3. `tasks/postdemo/v8/FPMS-V8-GRANT-EVIDENCE-SOURCE-CARRIER-SERVICE-20260810-01.md`
4. `tasks/postdemo/v8/FPMS-V8-GRANT-EVIDENCE-SOURCE-CARRIER-API-20260810-01.md`
5. `tasks/postdemo/v8/FPMS-V8-GRANT-EVIDENCE-INGESTION-SERVICE-20260712-01.md`
6. `tasks/postdemo/v8/FPMS-V8-GRANT-EVIDENCE-INGESTION-API-20260712-01.md`
7. `tasks/postdemo/v8/FPMS-V8-GRANT-EVIDENCE-CANDIDATE-READ-SERVICE-20260712-01.md`
8. `tasks/postdemo/v8/FPMS-V8-GRANT-EVIDENCE-CANDIDATE-LIST-API-20260712-01.md`

The manifest header changes only `Task count: 5` to `Task count: 8`. Add exact entries for rows
002–004, renumber the four existing child entries to 005–008 without changing their task identity,
and update only execution-wave/shared-ownership prose made false by the inserted prerequisites.
The historical controller task file remains unchanged and is not rewritten to claim it originally
created eight rows.

The focused test is updated, not weakened. It retains every existing Scheme A, no-source,
per-task closure, dependency, allowlist and serialization assertion, then proves the exact eight
paths, count, uniqueness, section order and current task-file hashes.

## Immutable Authority and Fail-Closed Contract

The successor manifest must preserve these values exactly:

- `DG-GRANT-EVIDENCE-SOURCE:GLOBAL`;
- `APPROVED_POLICY / CONFIG_REQUIRED`;
- source/adoption commits, decision version and customer-source SHA-256 frozen above;
- `Product development: ELIGIBLE`;
- `Runtime source configuration: REQUIRED / NOT PROVIDED BY THIS MANIFEST`;
- no concrete CNIPA source, URL, query channel, dataset, file, version, acquisition method,
  effective interval, production source row, role or seed;
- missing, future, expired, revoked, rejected, unreviewed, inactive, scope-mismatched,
  version/hash-mismatched or ambiguous configuration is `409 / NO WRITE / NO LEGAL-STATE CHANGE`;
- candidate ingestion/read availability never proves grant, changes `Case.status`, changes patent
  legal state or emits a lifecycle event;
- every protected child retains targeted TDD, exact allowlist evidence and independent High
  acceptance; the controller and this successor activation cannot approve a child.

The manifest rebind itself changes no schema or runtime behavior. The schema child owns only its
accepted three-carrier schema. The source service owns canonical snapshot/hash validation,
registration, independent review/activation, configuration publication/revocation,
idempotency/CAS and exact `(evidence_scope, as_of)` fail-closed resolution. The source API owns
only authenticated institution-configuration endpoints from the accepted service contract. No
child may start before all of its exact predecessor tasks are terminally accepted.

## Dependencies and Execution Order

Required before this activation may enter RED:

1. The source service/API task contracts and this exact hash-bound revision receive independent
   High zero-finding review.
2. The schema task's current implementation candidate and exact task bytes are independently
   reviewed with zero findings and hash-bound here. Terminal acceptance is deliberately deferred
   until this activation reaches PASS, because this successor manifest is the schema task's
   missing current-owner prerequisite; requiring schema acceptance here would be circular.
3. The accepted manifest preimage, focused-test preimage, Scheme A source and all eight current task
   hashes still match this contract.
4. No other owner edits the grant-source manifest or focused test.

After this activation reaches terminal PASS, the exact child order is:

1. accept the already implemented and independently reviewed source carrier schema candidate on
   its current bytes, without repeating RED/GREEN;
2. source carrier service;
3. source carrier API;
4. ingestion service;
5. ingestion API and candidate-read service under separate non-conflicting owners;
6. candidate-list API after both step 5 tasks pass.

The schema, service and API are required predecessors of ingestion even though the manifest does
not publish a source. Runtime ingestion remains unusable until an administrator later publishes a
valid independently reviewed source/configuration through separately accepted behavior.

Shared ownership remains serialized:

- `GLOBAL_ALEMBIC_HEAD`, `backend/app/modules/system/models.py`,
  `backend/app/modules/documents/models.py` and `backend/app/models/__init__.py` for schema work;
- source carrier service files and their focused tests before any consumer that imports them;
- source carrier API router/schema files before ingestion/list API edits to shared router/schema;
- `grant_evidence_ingestion_service.py`: ingestion service before candidate-read service;
- `documents/api.py` and `grant_evidence_schemas.py`: ingestion API before candidate-list API;
- every SQLite-writing verification and every manifest/shared-file verification.

## Explicit Non-Closure

- No product, schema, migration, model, service, API, UI, permission, role, seed, source,
  decision-gate, ingestion, review, lifecycle or legal-state implementation.
- No customer-source, source-registry, coverage-ledger, catalog, adoption, release or other
  manifest change.
- No edit to any child task contract, accepted activation task or historical evidence bundle.
- No concrete CNIPA source/default and no relaxation of `CONFIG_REQUIRED`.
- No execution of a missing or unaccepted child and no silent replacement of a task hash.
- No product tests, SQLite-writing tests, broad suite, frontend build, Playwright or release gate.

## Remaining Follow-Up Task IDs

- The eight child rows above, executed only in the frozen order after activation PASS.
- `FPMS-V8-GRANT-MANUAL-REVIEW-ROLE-CARRIER-SCHEMA-20260810-01` remains a separate lane before
  manual review or legal-state confirmation.

## Allowed Files

- `tasks/postdemo/v8/FPMS-V8-GRANT-SOURCE-SUCCESSOR-ACTIVATION-20260810-01.md`
- `tasks/batches/FPMS-POSTDEMO-V8-GRANT-SOURCE-GATE-20260712-01.md`
- `backend/tests/test_v8_grant_source_gate_manifest_contract.py`
- `artifacts/FPMS-V8-GRANT-SOURCE-SUCCESSOR-ACTIVATION-20260810-01/**`

No other source, test, task, manifest, ledger, catalog, review or adoption path is authorized.
Preserve and subtract the complete initial tracked/untracked dirty baseline. Concurrent files
outside this allowlist remain other owners' work.

## Verification Commands

Execution is prohibited if either bound source service/API task hash drifts. After this re-freeze
receives independent High approval, test-first order is mandatory:

1. Update `backend/tests/test_v8_grant_source_gate_manifest_contract.py` to define all eight exact
   IDs, paths and hash bindings while preserving every current assertion.
2. Add assertions for task count `8`, exact ordered sections, unique paths, exact inserted
   predecessor order, immutable Scheme A/fail-closed values and exact current task hashes.
3. Run RED against the unchanged accepted five-row manifest. Expected failure is only the exact
   five-versus-eight count/order and missing rows 002–004.
4. Make the minimum manifest changes frozen above, then run one canonical GREEN.

Commands after the materialization/hash-binding start gate passes:

- RED and GREEN:
  `cd backend && .venv/bin/pytest -q tests/test_v8_grant_source_gate_manifest_contract.py`
- Scoped format and check-only lint:
  `cd backend && .venv/bin/ruff check --fix tests/test_v8_grant_source_gate_manifest_contract.py && .venv/bin/ruff format tests/test_v8_grant_source_gate_manifest_contract.py && .venv/bin/ruff check tests/test_v8_grant_source_gate_manifest_contract.py`
- Frozen hashes:
  `shasum -a 256 docs/product/v8/customer-decisions/2026-08-10-v8-full-batch-scheme-a.txt tasks/batches/FPMS-POSTDEMO-V8-GRANT-SOURCE-GATE-20260712-01.md backend/tests/test_v8_grant_source_gate_manifest_contract.py tasks/postdemo/v8/FPMS-V8-GRANT-SOURCE-GATE-MANIFEST-ACTIVATION-20260712-01.md tasks/postdemo/v8/FPMS-V8-GRANT-EVIDENCE-SOURCE-CARRIER-SCHEMA-20260810-01.md tasks/postdemo/v8/FPMS-V8-GRANT-EVIDENCE-SOURCE-CARRIER-SERVICE-20260810-01.md tasks/postdemo/v8/FPMS-V8-GRANT-EVIDENCE-SOURCE-CARRIER-API-20260810-01.md tasks/postdemo/v8/FPMS-V8-GRANT-EVIDENCE-INGESTION-SERVICE-20260712-01.md tasks/postdemo/v8/FPMS-V8-GRANT-EVIDENCE-INGESTION-API-20260712-01.md tasks/postdemo/v8/FPMS-V8-GRANT-EVIDENCE-CANDIDATE-READ-SERVICE-20260712-01.md tasks/postdemo/v8/FPMS-V8-GRANT-EVIDENCE-CANDIDATE-LIST-API-20260712-01.md`
- Scope:
  `git diff --check -- tasks/postdemo/v8/FPMS-V8-GRANT-SOURCE-SUCCESSOR-ACTIVATION-20260810-01.md tasks/batches/FPMS-POSTDEMO-V8-GRANT-SOURCE-GATE-20260712-01.md backend/tests/test_v8_grant_source_gate_manifest_contract.py`
- Task gate:
  `./scripts/task_validate.sh FPMS-V8-GRANT-SOURCE-SUCCESSOR-ACTIVATION-20260810-01`
- Atomic evidence:
  `python3 /Users/cfcc/.codex/skills/atomic-evidence-gates/scripts/evidence_gate.py validate FPMS-V8-GRANT-SOURCE-SUCCESSOR-ACTIVATION-20260810-01 --required-step lint --required-step test --required-step independent_review --required-step scope --required-step task_gate`

## Evidence Path

- `artifacts/FPMS-V8-GRANT-SOURCE-SUCCESSOR-ACTIVATION-20260810-01/**`

Required PASS evidence includes task metadata, complete dirty baseline, RED/GREEN logs, scoped Ruff,
exact preimage/child/source hash logs, baseline-subtracted `git/diff.patch`, summary, scope and task
gate results. One independent High reviewer must bind the final task, manifest, focused-test and
patch hashes with exactly one final `Verdict: APPROVED`, `P0: 0`, `P1: 0`, and `P2: 0`.

The implementer cannot approve this activation. Review of the historical five-row manifest or a
revision that still records either missing child as absent cannot satisfy acceptance.

## Done Definition

The source service/API and re-frozen ingestion contracts are independently reviewed and hash-bound
into this freshly reviewed version of the task; the schema candidate/task is independently
reviewed and hash-bound but not circularly required to be terminal before this activation; every frozen preimage and Scheme A value still matches; the exact old
five-row RED is preserved; the manifest contains exactly the eight ordered paths above; the
focused test retains every prior invariant and proves the new order/hashes; scoped lint, scope,
task gate and atomic evidence pass; one independent High reviewer reports zero findings on current
bytes. Only then may this activation report PASS and unblock the schema child. This initial task
materialization boundary is closed by the exact hashes above.
