# FPMS-DEMO-CUSTOMER-V5-REALISTIC-SCENARIO-20260822-02

Status: ACTIVE
Risk-Class: PROTECTED
Dependency: customer-presentation candidate `823d17f1d17f40f826ce6c62f56ec3fe346be94c` and the customer approval `approve` following the reviewed minimum approach on 2026-08-22.

## Exact Closure Slice

Make the customer-facing V5 technical rehearsal use one coherent, realistic-shaped but wholly
synthetic Chinese patent-agency scenario instead of `IA-*`, `DEMO-*`, `虚构集成演示客户`,
`虚构主联系人`, and generic `虚构...` business titles. Keep the synthetic authority boundary
explicit outside ordinary business fields. Align the customer-shared runbook choreography with the
V5 HTML's exact stages 01 through 09 and with what the canonical runner actually proves:

- backstage preflight is not a tenth customer stage;
- stage 02 verifies template provenance, catalog behavior, and filing-package reuse, without
  claiming an unimplemented runtime-template preview;
- stage 07 separates the presenter-only obligation command from normal fee/draft UI actions;
- stage 08 separates presenter-only finance commands from customer-visible authoritative reads;
- stage 09 is an explicit spoken/configuration boundary, not an observed template/annuity UI claim;
- every stage has talk track, UI/action, input, screen output, expected result, verification, fact
  boundary, local stop condition, and recent-change content.

The canonical rehearsal and focused contracts must bind the same scenario values and stage order.

## Explicit Non-Closure

No production/customer activation; no legal, lifecycle, deadline, official-fee, service-price,
payment, evidence-lineage, API, permission, schema, migration, seed, or transaction semantic change.
Do not add runtime-template preview, a new fixture framework, a new customer page, new routing,
new backend endpoints, or broader demo capabilities. Preserve `SYNTHETIC_TEST_ONLY`, `DEMO_ONLY`,
`FICTIONAL_DEMO_EVIDENCE`, `.example`/`.test` contact safety, customer activation false, synthetic
confirmed-date disclaimers, official-fee no-write, internal `/demo/*` routes, IA checkpoint names,
UUIDs, and idempotency keys. No broad, product, release, deploy, or production gate.

## Catalog IDs

- N/A — this story changes customer-rehearsal presentation data and orchestration only; it does not
  alter catalog identities or dispositions.

## Allowed Files

- `tasks/postdemo/FPMS-DEMO-CUSTOMER-V5-REALISTIC-SCENARIO-20260822-02.md`
- `docs/postdemo/demo-lifecycle-customer-v5.html`
- `docs/postdemo/demo-lifecycle-customer-v5-runbook.md`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/demo-integrated-a.live-backend.spec.ts`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/demo-integrated-a-static-contract.mjs`
- `scripts/run_demo_integrated_a_rehearsal.py`
- `backend/tests/test_demo_abc_runtime_bundle.py`
- `backend/tests/test_demo_abc_runtime_service_draft.py`
- `backend/tests/test_demo_integrated_a_runner.py`
- `backend/tests/test_demo_integrated_first_oa.py`
- `frontend/src/modules/demo/pages/DemoAbc.vue`
- `frontend/src/modules/demo/demo.api.ts`
- `frontend/src/api/fees.ts`
- `frontend/tests/demo-abc-contract.mjs`
- `artifacts/FPMS-DEMO-CUSTOMER-V5-REALISTIC-SCENARIO-20260822-02/**`

## Approved Task Amendment — 2026-08-23

The task owner approved adding only `frontend/src/api/fees.ts` to the exact allowlist after the
headed rehearsal exposed an existing projection mismatch on the normal fee-draft page. The lock
endpoint truthfully returns `OkOut` (`{"status":"ok"}`), while `lockFeeDraft` treated that
acknowledgement as `FeeDraftDetail`, corrupting the page projection after a successful lock. The
minimum amendment makes that existing adapter read the authoritative draft through the existing GET
after the successful POST. It does not change this task's closure, non-closure, endpoint, route,
schema, permission, transaction, or domain semantics, and it does not absorb the unlock adapter.

Final provisional High review identified the remaining accepted-design §6 failure path: an unknown
lock-POST transport outcome must reconcile durable state before reporting failure. The task owner
approved the minimum failure-only amendment in the same normal-page adapter. Only an error with
`status=0` and `code=UNKNOWN_ERROR` triggers one existing authoritative draft GET; that read is
accepted only for the exact requested draft already in `LOCKED` state. Deterministic failures,
failed or mismatched reads, and every other state rethrow the original POST error. This amendment
does not change backend, unlock, runner, documentation, endpoint, or domain behavior.

The task owner later approved only `backend/tests/test_demo_abc_runtime_service_draft.py` as an
additional focused contract after provisional High review found the Integrated A customer screenshot
still exposed the technical-looking fee code `DEMO_INTEGRATED_SERVICE_1`. The narrow remediation
changes only that integrated synthetic fixture identity and its expected assertions to the
realistic-shaped business code `FWSQDJ001`. It preserves `DEMO_ONLY`,
`SERVICE_DEMO_PRICE`, all synthetic authority boundaries, and legacy ABC v1 `DEMO_SERVICE_1`.

The same provisional High review found customer attachment surfaces still exposed ordinal/role
slugs and OA reply artifacts still exposed `oa1-*`/`oa2-*` basenames. The approved remediation only
renames the twelve Integrated A synthetic evidence files and six generated OA reply files to their
natural Chinese business titles; roles, classifications, metadata, content hashes, endpoints, and
domain behavior remain unchanged. Runbook section 10 is explicitly relabeled as a historical
baseline record rather than evidence for this candidate.

The final fixture-only audit approved natural business-shaped document notes, receipt numbers,
submitter, auxiliary case identity, received-file names, grant source titles, replacement reference,
replacement description, and service item code. These are presentation-data substitutions only;
their existing dates, ownership/source mismatch checks, roles, classifications, and domain behavior
remain unchanged. Pre-existing raw UUID aliases in product UI and localization of official-workflow
labels or XML placeholder text are outside this fixture/runbook closure; this task does not invent a
new carrier for them.

The initially proposed hyphenated code `FW-SQDJ-001` produced the required RED against the existing
bundle code contract, which permits only uppercase letters, digits, and underscores. The task owner
therefore selected `FWSQDJ001`; the product validator and its allowlist remain unchanged.

## Required Scenario

- Customer: `澄岳智造技术（苏州）有限公司`
- Customer code: a fresh-run-safe `CYZN-<run suffix>` value
- Primary contact: `周岚`, title `知识产权经理`, reserved non-deliverable email
- Primary internal case number: a fresh-run-safe `CYIP-CN-INV-<run suffix>` value
- Case title: `一种柔性制造产线中视觉检测工位的自适应标定方法`
- Natural Chinese document titles for filing, receipt, acceptance, examination, two OA cycles, and
  original/replacement grant-registration sources; technical roles remain unchanged
- Service item display: `授权登记阶段代理服务费`; amount remains the exact active synthetic bundle
  amount and is never described as an official fee or customer quotation
- Customer-visible bill/payment/bank-reference values use `AR-CYZN-*`, `RCPT-CYZN-*`, and
  `BTR-CYZN-*`, not `DEMO-*`

The customer-shared screen and customer talk track must not expose raw UUIDs as business meaning or
use `IA-CASE`, `DEMO-AR`, `DEMO-PAY`, `DEMO-BANK`, `虚构集成演示客户`, `虚构主联系人`, or
`集成演示服务费` as customer-facing values. Technical metadata and logs may retain their truthful
internal classifications.

## Verification Commands

- RED first: extend the existing frontend/static/backend focused contracts to require the approved
  scenario values, exact HTML/runbook 01–09 order, truthful backstage boundaries, and absence of the
  rejected customer-visible placeholders; observe failure against the pre-change implementation.
- GREEN:
  - `node frontend/tests/demo-abc-contract.mjs`
  - `node FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/demo-integrated-a-static-contract.mjs`
  - focused backend pytest for `test_demo_integrated_a_runner.py`,
    `test_demo_abc_runtime_bundle.py`, and `test_demo_integrated_first_oa.py`
  - frontend typecheck and scoped ESLint for changed Vue/TypeScript files
  - scoped Ruff for changed Python files
  - `git diff --check`
  - one fresh headed canonical rehearsal with `--runs 1`; verify IA-00 through IA-18, customer-visible
    scenario values, screenshot, checksums, cleanup, and no leaked local listeners
- Independent High review of the exact committed range with `P0/P1/P2 = 0/0/0`.

## Evidence Path

- `artifacts/FPMS-DEMO-CUSTOMER-V5-REALISTIC-SCENARIO-20260822-02/**`

## Risk and Rollback

PROTECTED because the rehearsal visibly traverses lifecycle evidence and customer finance, although
their semantics are frozen and out of closure. Roll back the task's exact commit range. Do not edit,
delete, or reinterpret prior Integrated A evidence or accepted runtime inputs.

## Remaining Follow-Up Task IDs

- `FPMS-DEMO-INTEGRATED-A-DEPLOY-PREFLIGHT-20260822-11`
- Formal customer runtime bundle activation remains external and unmaterialized.
