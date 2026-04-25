# FE Completeness Residual Gaps Readiness

## Scope

This readiness pass covers residual gaps from `docs/frontend/FE_COMPLETENESS_REMEDIATION_CLOSE_AUDIT.md`:

- `FE-CASE-RELATED-SELECTORS-01`
- `PRODUCT-FE-DOCUMENT-WIZARD-REAL-WRITE-CONTRACT-01`
- `BE-FE-COMMISSION-QUERY-READINESS-01`
- `FE-MENU-ROUTE-DISCOVERABILITY-02`

## Capability Matrix

| Gap | Capability | Backend exists | FE page exists | FE task required | Product/backend blocker | Readiness |
| --- | --- | --- | --- | --- | --- | --- |
| FE-MENU-ROUTE-DISCOVERABILITY-02 | Existing routes are reachable from sidebar or list actions | yes | yes | yes | no | ready |
| PRODUCT-FE-DOCUMENT-WIZARD-REAL-WRITE-CONTRACT-01 | Document wizard final write semantics are clear | yes | partial | contract first | yes, UX/product semantics | product task required |
| BE-FE-COMMISSION-QUERY-READINESS-01 | Commission can be searched by business identifiers | partial | partial | after backend | bill-no linkage unclear | backend/product blocker |
| FE-CASE-RELATED-SELECTORS-01 | Raw IDs are replaced by business selectors | mixed | mixed | split tasks | agent/user role source unclear | split required |

## Route / Menu Matrix

| Route | Current state | Required action |
| --- | --- | --- |
| `/documents` | route exists, no sidebar entry | add menu entry with `Doc.Read` |
| `/documents/wizard` | route exists, only direct URL | add document list action with `Doc.Create` semantics |
| `/documents/dispatch` | route exists, only direct URL | add document list action with `Doc.Edit` semantics |
| `/fees/rates` | route exists, no menu entry | add finance menu entry with `FeeRate.Read` |
| `/system/letterheads` | route exists, no menu entry | add settings menu entry with `LetterHead.Read` |
| `/settings/masterdata` | route exists, no menu entry | add settings menu entry |
| `/settings/masterdata/departments` | route exists and menu entry exists | add missing masterdata home card |

## Product / Backend Blocker Matrix

| Blocker | Reason | Proposed task |
| --- | --- | --- |
| Document wizard submit semantics | The current wizard can perform real writes, but Step 2 and Step 5 submit semantics are ambiguous. | PRODUCT-FE-DOCUMENT-WIZARD-REAL-WRITE-CONTRACT-01 |
| Commission bill number search | `Commission` has `case_id` but no stable `bill_id` or `bill_no` carrier. | PRODUCT-COMMISSION-BILL-NO-QUERY-CONTRACT-01 |
| Commission case number search | Backend list filters by `case_id`, not `case_no`. | BE-FE-COMMISSION-QUERY-READINESS-01 |
| Agent/worker selectors | FE lacks a role-scoped user source for agent-safe selection. | PRODUCT-FE-AGENT-USER-SELECTOR-CONTRACT-01 or BE-FE-USER-ROLE-SELECTOR-READINESS-01 |

## Raw-ID Selector Matrix

| Area | Safe FE-only now | Notes |
| --- | --- | --- |
| Case original-case selector | yes | Existing `getCases()` can support a case selector. |
| Case address selector | mostly | Existing `getClientAddresses(clientId)` can support selected-client address choices. |
| Case agent/split/worker selector | no | Requires role-filtered user source or product acceptance of generic users. |
| Billing bill/payment client and bill selectors | yes | Existing `getClients()`, `getCases()`, and `getBills()` are available. |
| PayList client/case selectors | yes | Existing `getClients()` and `getCases()` are available. |
| Manual fee item selector | no | No case/pay-list-scoped eligible fee item source was found. |
| Document edit/wizard reply source | yes | Existing `getCases()` and `getDocuments({ case_id })` are available. |
| Task case selector | yes | Existing `getCases()` is available. |
| Task worker selector | no | Requires role/active-user selector decision. |

## Allowlist Matrix

| Task ID | Closure slice | Allowed files | Serialization |
| --- | --- | --- | --- |
| PRODUCT-FE-DOCUMENT-WIZARD-REAL-WRITE-CONTRACT-01 | Freeze wizard write semantics | `tasks/product/**`, `docs/product/**`, `artifacts/**` | independent |
| FE-MENU-ROUTE-DISCOVERABILITY-02 | Add discoverable entries for existing routes | `frontend/src/constants/menu.ts`, `frontend/src/constants/perms.ts`, `DocumentList.vue`, `MasterDataHome.vue` | serialized shared menu |
| BE-FE-COMMISSION-QUERY-READINESS-01 | Add backend `case_no` query support | commission backend API/tests | backend serialized |
| FE-CASE-RELATED-SELECTORS-01-SPLIT | Split raw-ID selector work into narrow tasks | task-specific | depends on selector source |

## Blocker Drain Manifest

Immediate execution order:

1. `PRODUCT-FE-DOCUMENT-WIZARD-REAL-WRITE-CONTRACT-01`
2. `FE-MENU-ROUTE-DISCOVERABILITY-02`

Deferred until product/backend decisions:

1. `PRODUCT-COMMISSION-BILL-NO-QUERY-CONTRACT-01`
2. `BE-FE-COMMISSION-QUERY-READINESS-01`
3. `FE-CASE-RELATED-SELECTORS-01-SPLIT`

## Automation / Walkthrough Readiness

After `FE-MENU-ROUTE-DISCOVERABILITY-02`, existing document, fee-rate, letterhead, and masterdata pages are discoverable through normal UI entry points. Raw-ID selector completeness remains open but is now mapped into smaller follow-up slices instead of a broad task.
