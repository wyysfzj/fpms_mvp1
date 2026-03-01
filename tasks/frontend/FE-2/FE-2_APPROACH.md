# Phase FE‑2: Feature Pages (MVP1) — Approach

## Preconditions
Phase FE‑2 assumes Phase FE‑0 and FE‑1 are complete:
- Auth/session works; API client is centralized and normalizes `{ error: { code, message, details } }`.
- App Shell (MainLayout) exists; tokens are wired; Focus Mode infrastructure exists (or at least `body.mode-immersive` is supported).
- Global error UX exists (401/403/422/409 patterns; requestId is displayable).

## UI Style Source of Truth (Strict)
All FE‑2 pages must strictly match:
- `case_detail.html` layout + interaction cues (Work Mode vs Immersive Mode, spacing, pill search style, floating toggle behavior, two‑column -> single column transition).
- `fpms.css` token spec: `src/styles/variables.css` must contain the exact variable block; FE‑2 must not introduce hardcoded colors/sizes that contradict tokens.

Rules:
- No inline styling/magic numbers in templates.
- Use class + CSS variables + Element Plus variable mapping.
- Case detail and long‑form reading pages MUST support Focus Mode and opt‑in via route meta.

## FE‑2 Delivery Model
FE‑2 is executed as a **sequence of atomic tasks**. Each task implements one “slice”:
- A list page slice (table + pagination + loading/empty/error) OR
- A create/edit slice (form + validation + success flow) OR
- An action slice (close/reopen/lock/print/upload) with clear UX and error handling.

Each task must:
- Use the shared axios client only (no direct fetch).
- Use typed DTOs per module (minimum set).
- Map 422 validation errors to field errors.
- Show requestId when available.

## Page Patterns (Must Reuse)
### A) List Page Pattern
- Page header (title + primary CTA)
- Filter bar (optional, collapsible later; keep minimal)
- Table (compact, high density)
- Row actions in a dropdown (avoid button noise)
- Pagination aligned to `{ page, page_size, total }`
- Empty state with CTA

### B) Detail Page Pattern (Case/Document/Bill/Draft)
- Meta header card aligned to reference (ID in mono, tag badge)
- Tabs
- Work Mode: content grid 2fr/1fr (main + side panel)
- Focus Mode: single-column reading flow (max-width, larger font, line-height)
- Side panel hides in Focus Mode

### C) Form Pattern
- `el-form` with clear grouping (card sections)
- Submit/cancel actions aligned to header
- 422 maps to `el-form-item` errors; non-field errors show a banner.

## Data & Routing Strategy (Minimal, Reliable)
- Keep lists paged server-side.
- Use route query for `page` and `page_size` only if easy; otherwise internal state is acceptable.
- Create/edit uses route params:
  - `/module/new`
  - `/module/:id/edit`
- Detail pages:
  - `/module/:id`
- Do not over-engineer state management; page-local `ref` is fine. Pinia is used where cross-page state is needed (rare in FE‑2).

## Task Order (Business‑critical)
Follow this sequence:
1) Clients (list -> create/edit/deactivate)
2) Cases (list/create -> detail/edit -> limited edit)
3) Tasks (list -> create -> actions -> today reminders)
4) Documents (list/create -> detail/edit -> attachments upload/download)
5) Fees (rates -> drafts -> draft items -> lock/unlock)
6) Billing (bills list/detail -> create -> print -> payments/offsets -> receipts summary)
7) System/Templates (templates -> system params -> letterheads)

## Evidence (AI‑EOS)
For every FE‑2 task:
- Run: `npm run lint`, `npm run typecheck`, `npm run build`
- Write evidence: `task/frontend/FE-2/<task_id>_evidence.md`
- Include manual smoke steps and expected HTTP statuses.
- If an endpoint does not match backend behavior, STOP and propose a smallest atomic fix task.
