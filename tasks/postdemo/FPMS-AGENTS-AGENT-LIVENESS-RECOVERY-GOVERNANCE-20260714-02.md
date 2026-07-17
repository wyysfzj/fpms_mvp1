# FPMS-AGENTS-AGENT-LIVENESS-RECOVERY-GOVERNANCE-20260714-02

Status: PASS / INDEPENDENT REVIEW APPROVED 2026-07-14
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Executor role: Governance Maintainer / worker
Risk tier: `HIGH` (authoritative `AGENTS.md` governance)

## Design References

- `AGENTS.md` section `0.3.5 Progress and context discipline`
- `tasks/postdemo/FPMS-AGENTS-TRANSPORT-RESILIENCE-GOVERNANCE-20260714-01.md` — accepted `PASS`; historical closure remains unchanged
- `artifacts/FPMS-AGENTS-AGENT-LIVENESS-RECOVERY-GOVERNANCE-20260714-02/analysis/agent_liveness_diagnosis.md`
  — immutable controller-observable H3-2/H3-3 diagnosis ledger

## Story Shape Classification

- `shared_file_density`: low — one authoritative governance file
- `prereq_dependency_density`: low — one accepted governance predecessor
- `be_fe_coupling`: none
- `evidence_cost`: medium — deterministic rule checks plus independent review
- `chosen_runbook`: `P0-single-lane-story`

## Task Contract Profile

Task Contract Profile: `TC-QA`

## Exact Closure Slice

Add one agent-liveness and recovery rule set to `AGENTS.md` that closes exactly these four
controller gaps:

1. classify agent state with these exact positive signals:
   - `rollout_positive`: rollout mtime/size growth or a new `task_started`, reasoning,
     message, tool-call or tool-output event since the preceding observation;
   - `verification_positive`: an in-scope verification process is alive or the task owns
     the repository serialization lock;
   - `durable_positive`: allowlist diff/hash, task/artifact mtime, or results/log count has
     advanced since the preceding observation.

   An explicit disconnect/stream error is handled first as `TRANSPORT_FAILURE` and always
   triggers durable-state reconciliation; it may coexist with preserved durable progress
   and is not itself a stall. After that event handling, choose one primary live-state label
   with this precedence: `RUNNING_VERIFICATION` when `verification_positive`;
   `DURABLE_PROGRESS` when `durable_positive`; `ACTIVE_PREFLIGHT` when only
   `rollout_positive`; otherwise `TRUE_STALL` only when two consecutive observations, at
   least 30 seconds apart, both have no positive signal and the second occurs at least
   90 seconds after the most recent positive-signal timestamp. Never interrupt an active
   preflight or verifier solely because no diff/artifact exists;
2. wait for an agent's durable `completed` state before follow-up, and verify a new
   `task_started`/rollout turn before assuming a completion-boundary follow-up was delivered;
3. after two same-session pre-durable-action transport disconnects, reconcile and retire
   that session. Permit one minimal-context replacement. If it also disconnects before
   durable action, stop agent retries and first reconcile/retire the replacement, confirm
   no agent turn or tool command remains active, no verification process remains, the
   repository serialization lock is released, and no other owner holds the task. Record
   the exact ownership transfer without recapturing or absorbing the dirty baseline. The
   lead may then take ownership of only that exact task only when the lead owns no other
   implementation task in the execution; otherwise pause only the affected lane;
4. require a serialized SQLite worker to report `READY_FOR_SERIAL_TEST` and wait for an
   explicit controller `GRANT` before acquiring the repository lock or starting pytest.

For a mechanical recovery step, the controller must issue one exact patch/check at a time
and must not ask the replacement to reread broad history.

## Explicit Non-Closure

No product source, test, schema, migration, approved V8 spec/plan/manifest, existing PASS
task history, proxy/network/Codex configuration, model setting, release gate, commit or push
is changed. This task does not claim to eliminate external transport failures, authorize
concurrent SQLite writers, weaken the two-observation rule, or permit a lead to implement
more than one exact task file in the same execution.

## Dependencies

- `FPMS-AGENTS-TRANSPORT-RESILIENCE-GOVERNANCE-20260714-01` — PASS.

## Remaining Follow-Up Task IDs

None.

## Allowed Files

- `tasks/postdemo/FPMS-AGENTS-AGENT-LIVENESS-RECOVERY-GOVERNANCE-20260714-02.md`
- `AGENTS.md`
- `artifacts/FPMS-AGENTS-AGENT-LIVENESS-RECOVERY-GOVERNANCE-20260714-02/**`

Capture and subtract the dirty baseline. No other task, source, test or evidence family is
owned by this task.

## Verification Commands

- Atomic task-shape check.
- Deterministic semantic check for the exact positive-signal predicates, classification
  precedence, the 30/90-second two-observation requirement, completion-boundary delivery,
  two-plus-one disconnect retirement, replacement quiescence and exact-task ownership
  transfer, mechanical microsteps, and SQLite `READY`/`GRANT` ordering.
- Duplicate/conflict check against existing `0.3.5` rules.
- Baseline-subtracted exact two-file scope check for `AGENTS.md` plus this task contract.
- Independent governance review confirming atomicity, fail-closed behavior, evidence,
  independent review, SQLite serialization and release gates are not weakened.
- Repository task gate and atomic evidence validation.

Product tests, Ruff, migrations, frontend checks, Playwright, repo-wide checks and the
release gate are prohibited.

## Evidence Path

- `artifacts/FPMS-AGENTS-AGENT-LIVENESS-RECOVERY-GOVERNANCE-20260714-02/**`

## Done Definition

The diagnosis ledger distinguishes active preflight from true stall and explicit transport
failure; the exact rule set is added once without rewriting accepted history; dirty baseline,
scoped diff, deterministic checks and an independent governance verdict exist; task gate
and atomic evidence validation pass. Only then may the task report PASS.
