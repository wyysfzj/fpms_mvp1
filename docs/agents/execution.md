# FPMS Atomic Execution

### Rule GOV-SCOPE-001 — Exact task ownership and surgical scope

Every implementer owns exactly one materialized task-file path, one closure slice, one
explicit non-closure boundary, one allowlist, and one evidence bundle. Without an exact
task or explicit batch manifest, stop at planning. Do not stretch broad wording, absorb a
second slice, edit outside the allowlist, refactor adjacent code, or clean unrelated dirt.
Two agents may not concurrently edit the same source, test, task, or shared ownership file.
Dirty baseline subtraction must include tracked and untracked allowlist state plus exact
outside-dirty paths; recovery never recaptures or absorbs that baseline.

An atomic task defines one exact closure slice, not one module cluster. It records the exact
closure, explicit non-closure, and remaining follow-up task IDs, or `None`. Broad acceptance
wording such as `close the remaining module`, `finish the whole chain`,
`complete backend/frontend parity`, or `close the remaining feasible scope` is prohibited.

The trusted development TCB is the local OS/filesystem, checkout, Git, Python, and
repository scripts unless a separately approved HIGH contract declares a hostile builder.
Ordinary scope gates detect mistakes and stale/incomplete evidence, not a malicious kernel,
toolchain, or privileged operator.

### Rule GOV-RISK-RUNTIME-001 — Repository risk is not runtime capability

LOW covers non-runtime, non-authoritative mechanical work. MEDIUM covers normal frozen
product implementation not classified HIGH. HIGH covers legal/lifecycle/deadline, official
fee or receivable truth, evidence lineage, auth/security, data/migration/destruction,
customer/source activation, authoritative governance, Foundation/Full/Final/Release close,
and unknown or mixed risk. The highest applicable tier controls.

Runtime High is the normal lane for frozen atomic implementation and independent review.
Runtime Ultra/highest capability is reserved for unresolved HIGH semantics, genuine new
architecture, contract freeze, and Foundation/Full/Release audit. Escalate only a concrete
semantic, authority, architecture, dependency, ownership, or contradictory-gate blocker;
lack of programmatic tier switching is not a blocker.

### Rule GOV-RUNBOOK-001 — Contract-frozen fast path and story shape

Unfrozen multi-step work records shared-file density, prerequisite density, backend/frontend
coupling, evidence cost, and one chosen runbook: `P0-single-lane-story`,
`P0-prereq-heavy-story`, `P0-multi-lane-parallel-story`, or `P0-frontend-heavy-story`.
Contract-frozen work reuses the approved task, classification, dependency graph, conflict
map, and immutable input hashes; it does not repeat source analysis, brainstorming, design,
planning, or materialization without a concrete changed input or explicit request.

Use targeted TDD. An immutable acceptance matrix may run one contract-complete RED tranche,
the minimum implementation, focused diagnostic reruns, and one complete canonical GREEN.
A hidden prerequisite pauses only affected lanes. If it changes closure or risk, split or
replan rather than absorb it.

### Rule GOV-LIVENESS-001 — Transport reconciliation and bounded replacement

Treat an explicit disconnect first as `TRANSPORT_FAILURE`, reconcile durable state, then
resume from the first incomplete ordinal without repeating completed edits, tests, evidence,
review, or gates. Classify live state in order: `RUNNING_VERIFICATION` when verification or
the serialization lock is active; `DURABLE_PROGRESS` when allowlist/evidence/results advance;
`ACTIVE_PREFLIGHT` for rollout-only progress; otherwise `TRUE_STALL` only after two negative
observations at least 30 seconds apart and at least 90 seconds since the latest positive
signal. Never interrupt active preflight or verification solely because no diff exists.

After two same-session transport failures before durable action, reconcile and retire it,
then permit one minimal-context replacement. If that replacement also reaches TRUE_STALL,
stop retries, reconcile processes/locks/ownership, and transfer only the exact task to an
otherwise-unassigned lead or report the blocker. A completion-boundary follow-up waits for
durable completion and requires a new started turn as delivery proof.

### Rule GOV-LINT-001 — Scoped check-only verification

Task-level final Ruff verification is `ruff check` on allowlisted Python files. Mutating
`ruff check --fix` or `ruff format` runs only intentionally on task-owned edits, followed by
the scoped check-only command. Repo-wide lint/test/build, broad Playwright, write formatting,
and release gates run only at an explicit task/manifest close point or user request, under
serialized ownership. Imports remain minimal and ordered.

### Rule GOV-REPORT-001 — Evidence-backed outcomes

Report the exact task/runbook and role, modified files, commands and observed status codes,
evidence path, actual `PASS|FAIL|BLOCKED` state, exact closure, respected non-closure, and
blockers. Multi-task controllers also report agent mapping, waves, serialized owners, and
per-task outcomes. Never claim PASS, fixed, complete, or ready without fresh verification,
required evidence, scope compliance, completed closure, and no absorbed second slice.

### Rule GOV-MULTIAGENT-001 — Conflict-free waves and independent acceptance

One agent owns at most one active task. Reuse is sequential only after durable terminal
verdict and ownership release. A lead may coordinate an explicit batch, but each row maps
one task to one owner, dependency/conflict notes, and wave. Shared routers, schemas,
permission registries, exports, frontend API/types/routes/stores/constants, migrations,
SQLite-writing verification, and repo-wide checks are serialized. Review is per task;
implementers cannot approve themselves, and representative slices cannot mark an item or
batch covered without an item-to-slice ledger.

Rule-Ref: GOV-BEHAVIOR-001
Rule-Ref: GOV-EVIDENCE-001
Rule-Ref: GOV-RELEASE-001
Rule-Ref: GOV-SKILLS-001
