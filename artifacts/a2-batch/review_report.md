# A2 Batch — Review Report

## Summary
Client Multi-Address & Contact feature fully implemented with UUID PKs, AuditMixin, spec-compliant field names, full CRUD service + API + tests.

## Files Changed/Created

| # | File | Action | Status |
|---|------|--------|--------|
| 1 | `backend/alembic/versions/a2_client_address_contact.py` | NEW | OK |
| 2 | `backend/app/modules/masterdata/clients/models.py` | MODIFIED | OK |
| 3 | `backend/app/modules/masterdata/clients/schemas.py` | MODIFIED | OK |
| 4 | `backend/app/modules/masterdata/clients/service.py` | MODIFIED | OK |
| 5 | `backend/app/modules/masterdata/clients/api.py` | MODIFIED | OK |
| 6 | `backend/app/models/__init__.py` | MODIFIED | OK |
| 7 | `backend/tests/test_client_address.py` | NEW | OK |
| 8 | `backend/app/models/client_address.py` | DELETED | OK |
| 9 | `backend/app/models/client_contact.py` | DELETED | OK |

## Acceptance Criteria Checklist

- [x] Create client, add 2 addresses (BILLING + MAILING), verify both in GET
- [x] Add 2 contacts to client, verify returned
- [x] Delete an address, verify removed
- [x] Delete a contact, verify removed
- [x] Cross-client sub-resource access → 404
- [x] Quality gate passes (ruff + pytest + alembic + seed)

## Quality Gate Results

| Check | Result |
|-------|--------|
| `ruff check .` | All checks passed |
| `ruff format .` | All files formatted |
| `pytest -q` | 54 passed (12 new + 42 existing) |
| `alembic upgrade head` | Clean rebuild OK (18 migrations) |
| `python scripts/seed_dev.py` | Seeded successfully |

## Migration Details
- Revision: `a2_client_addr_01` chains from `a1_task_template_01`
- Drops old `t_client_contact` and `t_client_address` tables
- Recreates both with UUID PK (String(36)), AuditMixin columns, spec field names
- Indexes on `client_id` for both tables

## Schema Changes
- `ClientAddressOut`: `id: int` → `id: str`, `line1` → `address_line1`, `state` → `province`, `country` → `country_code`, `is_primary` → `is_default`
- `ClientContactOut`: `id: int` → `id: str`, removed `department`, `notes`; added `mobile`
- Added: `ClientAddressCreateIn`, `ClientAddressUpdateIn`, `ClientContactCreateIn`, `ClientContactUpdateIn`

## Endpoints Added (8)
| Method | Path | Perm | Status |
|--------|------|------|--------|
| GET | `/clients/{client_id}/addresses` | Client.Read | 200 |
| POST | `/clients/{client_id}/addresses` | Client.Edit | 201 |
| PUT | `/clients/{client_id}/addresses/{address_id}` | Client.Edit | 200 |
| DELETE | `/clients/{client_id}/addresses/{address_id}` | Client.Edit | 204 |
| GET | `/clients/{client_id}/contacts` | Client.Read | 200 |
| POST | `/clients/{client_id}/contacts` | Client.Edit | 201 |
| PUT | `/clients/{client_id}/contacts/{contact_id}` | Client.Edit | 200 |
| DELETE | `/clients/{client_id}/contacts/{contact_id}` | Client.Edit | 204 |

## Tests (12)
All 12 pass:
- `test_create_address_billing` — BILLING address with all fields
- `test_create_address_mailing` — MAILING address
- `test_list_addresses` — Both returned
- `test_update_address` — Field changes persist
- `test_delete_address` — 204 + removed from list
- `test_create_contact` — Full contact with mobile
- `test_create_second_contact` — Minimal contact
- `test_list_contacts` — Both returned
- `test_update_contact` — Field changes persist
- `test_delete_contact` — 204 + removed from list
- `test_address_404_wrong_client` — Cross-client → 404
- `test_contact_404_wrong_client` — Cross-client → 404

## Verdict: PASS
