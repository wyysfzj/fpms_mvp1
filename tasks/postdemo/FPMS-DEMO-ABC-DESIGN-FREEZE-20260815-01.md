# FPMS-DEMO-ABC-DESIGN-FREEZE-20260815-01

Status: REVIEW
Risk: PROTECTED
Role: Architect / default
Outcome: freeze the customer-approved local ABC end-to-end demo contract before product changes.

## Authority

- `AGENTS.md`
- `docs/product/v8/domain-contract.md`
- `docs/product/v8/source-decision-registry.md`
- `docs/product/v8/customer-decisions/2026-08-15-local-demo-abc.txt`
- Independent High audit bound to `d1df69e649f5d28cb192d347d25c8d775663aaf2`
- Existing V7 lifecycle design/script/runbook

## Catalog and requirements

- Preserve V8 service-price rows 223–229 and live-path row 278 as capability references; this
  task changes no catalog or coverage-ledger disposition.
- Preserve the already adopted filing/OA/receipt/obligation stories reached by the V7 path.
- Customer AR requirements: TXX pages 131–137 and SPEC 2.0 bill/payment/offset lineage.
- Audit remediation IDs: `DEPLOY-PKG-002`, `STATE-UI-002`, `EVID-RETRY-003`,
  `TXN-DOCFEE-008`, `FIN-BILL-001`, `FIN-OFFSET-001`, `FIN-DASH-004`,
  `FIN-ADAPTER-005`.

## Exact closure

Record the exact user decision and freeze one written design covering:

- clean baseline and local-only runtime topology;
- seven customer-visible ABC checkpoints;
- immutable `DEMO_ONLY` bundle validation/provider/no-fallback behavior;
- dynamic runtime service-price selection through source activity, obligation, customer
  instruction and locked draft;
- unique/idempotent bill, truthful/idempotent payment, atomic/idempotent offset;
- strict monetary adapters, authoritative CNY dashboard and real-browser acceptance;
- implementation slices, dependency order, evidence, rollback and explicit non-goals.

## Explicit non-closure

No backend/frontend/test/schema/migration/seed/runner implementation. No runtime bundle contents,
production input activation, official fee/payment, security remediation, remote deployment,
catalog/ledger edit, broad/release gate, or claim of `DEMO_READY`.

## Allowed files

- `docs/product/v8/customer-decisions/2026-08-15-local-demo-abc.txt`
- `docs/product/v8/source-decision-registry.md`
- `docs/superpowers/specs/2026-08-15-fpms-local-demo-abc-design.md`
- `tasks/postdemo/FPMS-DEMO-ABC-DESIGN-FREEZE-20260815-01.md`

## Verification

- Confirm exact decision bytes, size and SHA-256.
- Assert the design contains authority, three considered approaches, seven checkpoints, runtime
  bundle, lifecycle, bill/payment/offset, error handling, tests, non-goals and rollback.
- `git diff --check` over the exact allowlist.
- Confirm no changed path falls outside the allowlist.
- Commit the exact design and obtain one independent High review with P0/P1/P2 = 0/0/0.
- Obtain customer confirmation of the written specification before implementation planning.

## Follow-up slices

- `ABC-DEMO-BUNDLE-PARSER`
- `ABC-DEMO-LOCAL-BOOT`
- `ABC-DEMO-RUNTIME-PROVIDERS`
- `ABC-DEMO-LIFECYCLE`
- `ABC-FIN-BILL`
- `ABC-FIN-PAYMENT`
- `ABC-FIN-OFFSET`
- `ABC-FIN-ADAPTER-DASH`
- `ABC-DEMO-LIVE-E2E`
- `ABC-DEMO-READY`

## Rollback

Revert the exact design commit. This removes only the written demo decision/design/task bytes and
does not mutate production configuration or business data.

## Done definition

Only the four allowed files differ from the baseline; all content/diff checks pass; an independent
High reviewer approves the exact commit with zero findings; and the customer confirms the written
specification. Until then this task remains `REVIEW`.
