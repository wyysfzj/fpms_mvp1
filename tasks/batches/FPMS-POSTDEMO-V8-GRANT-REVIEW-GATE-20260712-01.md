# FPMS Post-demo V8 Grant-review Gate Lane Manifest

Status: FROZEN CANDIDATE / READY FOR INDEPENDENT HIGH REVIEW
Program: `FPMS-POSTDEMO-V8-MITIGATION-20260712-01`
Manifest phase: `lane`
Task count: 8
Runbook: `P0-prereq-heavy-story`
Activation task: `FPMS-V8-GRANT-REVIEW-GATE-MANIFEST-ACTIVATION-20260712-01`
Gate requirements: `DG-GRANT-EVIDENCE-SOURCE:GLOBAL`, `DG-GRANT-MANUAL-REVIEW:GLOBAL`

## Authority and activation boundary

- Policy status: `APPROVED_POLICY / CONFIG_REQUIRED`.
- Decision version: `customer-decision:2026-08-10:v8-full-batch-scheme-a:v1`.
- Customer-source SHA-256:
  `e6cfd648f1d366e27bde3f74310f00033a6db60ce55d850d2e668764745faace`.
- Product development: ELIGIBLE.
- Runtime source configuration: REQUIRED / NOT PROVIDED BY THIS MANIFEST.
- Runtime role configuration: REQUIRED / NOT PROVIDED BY THIS MANIFEST.

This manifest activates only the exact development lane below. It publishes no source record,
role binding, person assignment, default or seed. Missing, stale, unreviewed, revoked, inactive,
future, expired, scope-mismatched, hash-mismatched or ambiguous source or role authority remains
`409 / NO WRITE / NO LEGAL-STATE CHANGE`. Manifest membership never proves grant, accepts a
candidate or authorizes direct case-status mutation.

Every task retains its exact closure, non-closure, owner, allowlist, targeted verification and
independent protected review. Runtime review and dispatch require the accepted source and role
configuration for the exact effective time and scope, including distinct actual users where the
contract requires two-person control.

## Execution and shared ownership

1. Accept this activation.
2. Reuse the accepted review service; do not repeat its RED/GREEN.
3. Implement the announcement adapter, then the patent-register adapter, serially in
   `backend/app/modules/documents/evidence_policy.py`.
4. Implement accepted dispatch after both adapters, as the successor owner of
   `backend/app/modules/documents/grant_evidence_review_service.py`.
5. Implement the review API after dispatch, serially after existing document-router/schema owners.
6. Implement the frontend adapter, then the UI.

All shared-file and SQLite-writing verification remains serialized. An implementer cannot approve
its own task, and rejection or conflict cannot dispatch a lifecycle event.

## 001. FPMS-V8-GRANT-REVIEW-GATE-MANIFEST-ACTIVATION-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-GRANT-REVIEW-GATE-MANIFEST-ACTIVATION-20260712-01.md`
- Task SHA-256: `daaacaef4655e052e1689c56609af93ea4b6597412be79e2a1d25e0cdcb1bed2`
- Exact closure: Create this manifest containing the activation plus exactly seven review,
  adapter, API, FE and UI tasks.
- Non-closure: No product, schema, runtime configuration, seed, catalog or ledger change.
- Verification: focused manifest contract, scoped Ruff, exact three-path diff and independent
  High review.

## 002. FPMS-V8-GRANT-EVIDENCE-REVIEW-SERVICE-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-GRANT-EVIDENCE-REVIEW-SERVICE-20260712-01.md`
- Task SHA-256: `23926502da9273a8a9244e8b3228b610a41ea40db35d004d9be1dfea75cbdcea`
- Exact closure: Accept or reject one candidate only with proposer/reviewer separation; preserve
  conflicts and dispatch nothing before acceptance.
- Non-closure: No endpoint, UI, schema or adjacent service rule.
- Dependency: this activation, the decision-gate read service and ingestion service.
- Shared owner: `grant_evidence_review_service.py` order key 1; already accepted and reused.

## 003. FPMS-V8-GRANT-ANNOUNCEMENT-EVIDENCE-ADAPTER-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-GRANT-ANNOUNCEMENT-EVIDENCE-ADAPTER-20260712-01.md`
- Task SHA-256: `35ec0e945b3fddfc9c1a2afb888c48c3067aee64a6097c1900b9cb13c618aea1`
- Exact closure: Map one accepted controlled announcement candidate to the announcement lifecycle
  event exactly once, without review-state mutation or direct status write.
- Non-closure: No deep-rule change, second entrypoint or unrelated refactor.
- Dependency: accepted review service, announcement rule, decision gates and direct-status gate.
- Shared owner: `evidence_policy.py` order key 5, before the patent-register adapter.

## 004. FPMS-V8-PATENT-REGISTER-EVIDENCE-ADAPTER-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-PATENT-REGISTER-EVIDENCE-ADAPTER-20260712-01.md`
- Task SHA-256: `f90ad26c621d8d8c580121bae1ea5e2b8cf3e12ca322d2e56f035f719d854aba`
- Exact closure: Map one accepted register candidate to same-status verification/conflict or only
  the specific approved status-change event, without review-state mutation or direct status write.
- Non-closure: No deep-rule change, second entrypoint or unrelated refactor.
- Dependency: accepted review service, exact register/terminal/restoration rules, decision gates
  and direct-status gate.
- Shared owner: `evidence_policy.py` order key 6, after the announcement adapter.

## 005. FPMS-V8-GRANT-EVIDENCE-ACCEPTED-DISPATCH-ADAPTER-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-GRANT-EVIDENCE-ACCEPTED-DISPATCH-ADAPTER-20260712-01.md`
- Task SHA-256: `aa8a2e01707eda7ae47514c843cf31ec96ebc1ca1b97faa05a230d6658598939`
- Exact closure: After accepted review, invoke exactly one announcement/register adapter in the
  same caller-owned transaction; rejection or conflict invokes none.
- Non-closure: No deep-rule change, second entrypoint or unrelated refactor.
- Dependency: accepted review service and both evidence adapters.
- Shared owner: `grant_evidence_review_service.py` order key 2.

## 006. FPMS-V8-GRANT-EVIDENCE-REVIEW-API-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-GRANT-EVIDENCE-REVIEW-API-20260712-01.md`
- Task SHA-256: `fa1bf602a63d74e78a2b3184565a5c178578f8c617f1b5199622a8045fd324dc`
- Exact closure: Expose one `Doc.Edit` POST review endpoint with proposer/reviewer separation,
  accepted dispatch and 409 for role/source/conflict violations.
- Non-closure: No second endpoint, router rewiring, business-rule duplication or frontend work.
- Dependency: accepted dispatch and the existing ingestion API.
- Shared owners: `documents/api.py` order key 16 and `grant_evidence_schemas.py` order key 3.

## 007. FPMS-V8-GRANT-EVIDENCE-REVIEW-FE-ADAPTER-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-GRANT-EVIDENCE-REVIEW-FE-ADAPTER-20260712-01.md`
- Task SHA-256: `a1c664c3faf9b8b7316bda522a78e272468993f970f39c54cb70cfe890481487`
- Exact closure: Type candidate list/review results, proposer/reviewer and conflicts without
  deriving legal state.
- Non-closure: No page behavior, server-state inference or backend change.
- Dependency: candidate-list API, review API and the accepted document-review FE adapter.
- Shared owners: `documents.ts` and `documents.types.ts` order key 2; frontend typecheck order 7.

## 008. FPMS-V8-GRANT-EVIDENCE-REVIEW-UI-20260712-01

- Task file: `tasks/postdemo/v8/FPMS-V8-GRANT-EVIDENCE-REVIEW-UI-20260712-01.md`
- Task SHA-256: `e19b590d4d789575927ae26df21f54e74c5b6b43a02b816d4a6fb61c912dced6`
- Exact closure: Show controlled grant candidates and one second-person approve/reject action;
  conflicts remain visible and no pre-approval legal state appears.
- Non-closure: No backend change, second page capability or frontend business-state calculation.
- Dependency: accepted review FE adapter and the decision gates.

## Lane done boundary

This activation is accepted only after its focused contract, scoped checks and independent High
review pass. Each child closes independently. This manifest does not publish production authority,
approve a child, change legal state, close Full/Final, or run the release gate.
