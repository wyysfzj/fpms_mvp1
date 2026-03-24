# FB2 Batch — Task Plan

## Goal
Create client detail page with tabbed layout. Add address and contact sub-resource management (CRUD) using backend A2 APIs.

## Backend Dependency
**Backend A2 (Client Address/Contact APIs) — CONFIRMED COMPLETE**
- `GET/POST /clients/{id}/addresses` ✅
- `PUT/DELETE /clients/{id}/addresses/{addr_id}` ✅
- `GET/POST /clients/{id}/contacts` ✅
- `PUT/DELETE /clients/{id}/contacts/{contact_id}` ✅

## File Allowlist (STRICT)
| File | Action |
|------|--------|
| `frontend/src/api/clients.ts` | modify |
| `frontend/src/api/clients.types.ts` | modify |
| `frontend/src/modules/clients/pages/ClientDetail.vue` | new |
| `frontend/src/modules/clients/components/AddressTable.vue` | new |
| `frontend/src/modules/clients/components/ContactTable.vue` | new |
| `frontend/src/router/index.ts` | modify |

## Task Decomposition

### T1 — API Types (clients.types.ts)
Add `ClientAddress`, `ClientContact`, and their create/update payload types.

### T2 — API Functions (clients.ts)
Add CRUD functions for addresses and contacts.

### T3 — AddressTable.vue (new component)
el-table with el-dialog for add/edit, el-popconfirm for delete.

### T4 — ContactTable.vue (new component)
Same pattern as AddressTable.

### T5 — ClientDetail.vue (new page)
Tabbed layout: Basic Info, Addresses, Contacts, Related Cases.

### T6 — Router (index.ts)
Add route `/clients/:id` → ClientDetail.

## Assignment
- **Frontend Agent**: T1 → T2 → T3 → T4 → T5 → T6 (sequential)
- **Reviewer Agent**: After all tasks complete

## Status
- [ ] Architect Plan approved
- [ ] T1–T6 implemented
- [ ] Quality Gate passed
- [ ] Review Report generated
