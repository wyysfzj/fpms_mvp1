# FPMS Evidence and Acceptance

### Rule GOV-EVIDENCE-001 — Latest scoped evidence and independent review

Initialize task-local evidence before edits through the repository entry point. Each
passing task retains `task.json`, `results.jsonl`, `summary.md`, baseline-subtracted
`git/diff.patch`, outputs/logs, and dirty-baseline artifacts when applicable. Generated
evidence must not contain secrets or PII. Required results are the latest matching results,
have logs, and return zero. Missing or malformed evidence fails closed.

Canonical acceptance step names are `lint`, `test`, `scope`, `independent_review`,
`task_gate`, and `atomic_evidence`; diagnostic steps such as `red` do not replace them.
Scope must include tracked and untracked allowlist changes, subtract the coherent initial
baseline, identify concrete outside dirt, and reject drift or omissions.

The implementer cannot independently approve its own task. Normal frozen HIGH work has one
independent reviewer; unresolved cross-module architecture, hostile-builder work, and
Foundation/Full/Release close use two axes when the contract requires them. The final review
must contain one final `Verdict: APPROVED`, `P0: 0`, `P1: 0`, and `P2: 0`, and bind the
current baseline-subtracted patch hash plus any contract-required task/summary hashes.
Stale hashes, multiple verdicts, missing identity, nonzero findings, or review preceding the
latest patch fail closed.

Task gate and atomic evidence run only after the approved zero-finding review. Release is
last and only at the explicit batch/release close point. A failed close never produces
PASS. Historical tasks already accepted before a later evidence activation remain accepted;
unaccepted historical tasks are not grandfathered and must satisfy the active consumer.
The incomplete historical Evidence Bundle V2 chain is not authority. Evidence 1.1 remains
the active protocol until the Governance Reset activation task reaches terminal PASS.

Rule-Ref: GOV-RELEASE-001
Rule-Ref: GOV-SCOPE-001
