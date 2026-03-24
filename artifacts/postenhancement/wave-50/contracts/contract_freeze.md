# Wave 50 Contract Freeze

## Task Scope
- Wave: `50`
- Role: Architect / Designer
- Frozen tasks:
  - `tasks/postenhancement/frontend/PE-FE-QA-02.md`
  - `tasks/postenhancement/frontend/PE-FE-QA-03.md`
- Current execution freeze: `PE-FE-QA-03` (doc-only).
- Scope intent:
  - `PE-FE-QA-02`: freeze responsive and a11y minimum standards for new frontend pages.
  - `PE-FE-QA-03`: freeze smoke-doc/manual-guide coverage for new business chains with explicit a11y and Simplified Chinese compliance checks.

## Global FE Constraints (Mandatory)
- Task isolation:
  - Execute exactly one atomic task file per implementation run.
  - `PE-FE-QA-02` implementation allowlist:
    - `frontend/src/modules/**/pages/*.vue` (new pages only)
    - `frontend/src/styles/*.css` (minimal necessary changes)
  - `PE-FE-QA-03` implementation allowlist:
    - `docs/frontend_smoke_flows.md`
    - `docs/FPMS_Frontend_Manual_Test_User_Guide.md`
- Existing architecture must be preserved:
  - no router rewiring unless task explicitly requires it
  - no backend/schema/migration changes
  - no cross-module refactor outside allowlist
- All user-facing UI text MUST be Simplified Chinese.

## PE-FE-QA-02 Freeze (Responsive + A11y Baseline)

### 1) Responsive Minimum Contract (Desktop + Mobile)
- New pages must be usable on both desktop and mobile viewports.
- Layout contract:
  - no horizontal overflow at common widths (`>=1280`, `768`, `390` reference widths)
  - primary actions remain visible/reachable without layout break
  - tables/forms must degrade safely (wrap/stack/scroll strategy) without clipping core content
- Interaction contract:
  - touch targets for primary controls must remain operable on mobile
  - no critical operation is blocked by fixed headers/footers/overlays

### 2) Keyboard Reachability Contract
- Every interactive control on new pages must be keyboard reachable.
- Required behaviors:
  - logical tab order follows visual/form order
  - all actionable controls are focusable (`button`, `a`, valid form controls, or explicit tabindex where justified)
  - keyboard activation works for core actions (submit/search/open/close) via standard key behavior
  - focus is not trapped unintentionally on regular page flow
- Dialog/overlay (if present):
  - initial focus lands on meaningful control
  - close path is keyboard-operable
  - focus returns to trigger control after close

### 3) Semantic Labels + Readable Error Contract
- Form semantics:
  - each input/select/textarea must have a clear associated label (visible label preferred)
  - icon-only controls must provide semantic accessible name
- Error readability:
  - validation/business errors must be user-readable and context-specific
  - error messages must not expose raw backend internals to end users
  - inline error text must be visually distinguishable and remain readable on small screens
  - error summary/banner (if used) must not replace field-level hints where field mapping exists

### 4) Simplified Chinese UI Text Compliance Contract
- All user-facing text introduced or changed in task scope must be Simplified Chinese, including:
  - page titles
  - buttons and action labels
  - form labels/placeholders/helper text
  - validation/error/empty-state/toast text
- English is allowed only for technical non-UI values (IDs, enum/code values, API fields, logs).

## Frozen Error Semantics Baseline
- UI error presentation must preserve backend status semantics:
  - `400`: business validation failure, readable Chinese message
  - `401`: unauthenticated flow messaging
  - `403`: permission denied messaging
  - `404`: resource-not-found messaging
  - `409`: conflict/missing configuration messaging
  - `422`: request validation messaging (prefer field-level mapping)
- Unknown/network failures must fall back to generic Chinese failure message.

## Acceptance Checklist (PE-FE-QA-02)
- [ ] Changes remain strictly within PE-FE-QA-02 allowlist.
- [ ] New pages meet responsive minimum standards on desktop and mobile.
- [ ] Core interactions are keyboard reachable with sane focus behavior.
- [ ] Inputs/controls have semantic labels; error messages are readable and contextual.
- [ ] All user-visible copy in scope is Simplified Chinese.
- [ ] Frontend verification target for implementation phase:
  - `cd frontend && npm run lint`
  - `cd frontend && npm run typecheck`
  - `cd frontend && npm run build`
- [ ] Manual QA target for implementation phase:
  - keyboard-only pass on key flows
  - responsive pass on desktop/mobile reference widths
  - error readability pass (field + page-level)

## PE-FE-QA-03 Freeze (补充新增业务链路手工冒烟文档)

### Task / Allowlist
- Task ID: `PE-FE-QA-03`
- Task file: `tasks/postenhancement/frontend/PE-FE-QA-03.md`
- Type: `doc`
- In-scope files for implementation:
  - `docs/frontend_smoke_flows.md`
  - `docs/FPMS_Frontend_Manual_Test_User_Guide.md`
- Out of scope:
  - all frontend product code (`frontend/src/**`)
  - backend/schema/migration/test changes
  - unrelated documentation refactor outside the two allowlisted docs

### Coverage Matrix Contract (Mandatory)
- Documentation updates must explicitly cover all required new business chains:
  - `annuity`
  - `collections`
  - `commission`
  - `consulting`
  - `expense`
- Each module coverage must include at least:
  - route entry point(s)
  - core user action flow steps
  - expected API endpoint(s) with status semantics baseline
  - expected UI outcomes
  - failure behavior baseline (`400/401/403/404/409/422`)

### Required Route-Level Coverage Baseline
- `annuity`:
  - `/annuity/tasks`
  - `/annuity/pay-lists`
  - `/annuity/gov-payments/new`
- `collections`:
  - `/collections/dunning`
  - `/collections/dunning/new`
  - `/collections/dunning/:id`
- `commission`:
  - `/commission`
  - `/commission/rules`
  - `/commission/settlements`
- `consulting`:
  - `/consulting/cases/new`
  - `/consulting/fee-drafts/new`
  - `/consulting/profitability`
- `expense`:
  - `/expenses`
  - `/expenses/new`

### A11y + Responsive Doc Checklist Contract
- For each of the five modules above, smoke docs must include manual checkpoints for:
  - keyboard reachability of primary interactions (tab/focus/submit)
  - semantic label validation for key inputs/actions
  - readable error presentation (field-level and/or page-level)
  - desktop + mobile usability checks (no critical overflow/blocking)
- Checkpoints can be embedded in per-module sections or consolidated in one matrix, but must map back to each module.

### Simplified Chinese UI Text Compliance Contract
- QA-03 docs must define explicit verification for Simplified Chinese UI text on new pages:
  - page titles
  - action/button labels
  - form labels/placeholders
  - validation/error/empty-state texts
- English is allowed only for technical values (route paths, IDs, API fields, enum/code values).
- If docs include English button labels for legacy compatibility, they must provide clear Chinese equivalence in the same section.

### Dual-Document Alignment Contract
- `docs/frontend_smoke_flows.md` and `docs/FPMS_Frontend_Manual_Test_User_Guide.md` must stay consistent on:
  - module coverage set (`annuity/collections/commission/consulting/expense`)
  - key route references
  - status/error semantics baseline
  - evidence expectations (requestId and pass/fail recording)
- No contradiction between the two docs on required test outcomes.

## Acceptance Checklist (PE-FE-QA-03)
- [ ] Changes stay strictly within QA-03 doc allowlist.
- [ ] Both docs explicitly cover `annuity/collections/commission/consulting/expense` chains.
- [ ] Route-level coverage includes frozen baseline routes for each module.
- [ ] a11y/responsive checkpoints are documented for each required module.
- [ ] Simplified Chinese UI text compliance checks are explicitly documented.
- [ ] The two docs remain semantically aligned (no contradictory instructions).
- [ ] Verification target for implementation phase:
  - 文档自检（结构、路由、状态码、术语一致性）
