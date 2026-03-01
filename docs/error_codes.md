# FPMS Error Codes

## Error envelope
FPMS currently uses two error response shapes:

1) `BusinessError` / validation envelope:

```json
{
  "error": {
    "code": "SOME_CODE",
    "message": "Human readable message",
    "details": {
      "extra": "optional context"
    }
  }
}
```

2) Legacy FastAPI `HTTPException` envelope (still present in some existing endpoints):

```json
{
  "detail": "Human readable message"
}
```

Typical HTTP statuses:
- 400 (business validation)
- 401 (unauthenticated)
- 403 (permission denied)
- 404 (not found)
- 409 (conflict / locked)
- 422 (validation error)
- 500 (unexpected server errors)

## Envelope constraints for post-enhancement domains (mandatory)
For new domains (`annuity`, `collections`, `commission`, `consulting`):
- Business/domain failures MUST use `BusinessError` and return `{"error":{"code","message","details"}}`.
- Request schema failures MUST return `422` with `error.code = VALIDATION_ERROR`.
- Do not introduce custom envelope shapes.
- `401`/`403` remain cross-cutting auth/permission errors (`AUTH_REQUIRED` / `FORBIDDEN`).

## Common cross-cutting codes
- `AUTH_REQUIRED` (401): missing/invalid/expired token.
- `AUTH_INVALID` (401): invalid username/password.
- `FORBIDDEN` (403): permission denied; `details.required_perm` indicates required permission.
- `VALIDATION_ERROR` (422): request validation failed (FastAPI).

## BusinessError codes (table)

### Auth / RBAC
| Code | Typical HTTP status | Where raised (module/file) | When it happens | How to fix |
| --- | --- | --- | --- | --- |
| AUTH_REQUIRED | 401 (sometimes 404 in core deps) | `app/api/deps.py`, `app/core/dependencies.py` | Missing/invalid token or user inactive | Re-login; ensure JWT secret matches and user is active |
| AUTH_INVALID | 401 | `modules/auth/api.py` | Bad username/password | Use correct credentials or reset password |
| FORBIDDEN | 403 | `app/api/deps.py`, `app/core/dependencies.py` | Token valid but lacks permission | Sync perms (`scripts/scan_perms.py` + `scripts/seed_dev.py`), then re-login |

### Clients
| Code | Typical HTTP status | Where raised (module/file) | When it happens | How to fix |
| --- | --- | --- | --- | --- |
| CLIENT_NOT_FOUND | 404 | `modules/masterdata/clients/service.py` | Client ID not found | Use a valid client ID |
| CLIENT_CODE_DUPLICATE | 400 | `modules/masterdata/clients/service.py` | Duplicate `client_code` | Use a unique client code |

### Cases
| Code | Typical HTTP status | Where raised (module/file) | When it happens | How to fix |
| --- | --- | --- | --- | --- |
| CASE_NOT_FOUND | 404 | `modules/cases/service.py` (also docs/fees/tasks) | Case ID not found | Use a valid case ID |
| CASE_NO_DUPLICATE | 400 | `modules/cases/service.py` | Duplicate case number | Use a unique case number |
| CASE_FIRST_APPLICANT_REQUIRED | 400 | `modules/cases/service.py` | No first applicant provided | Mark one applicant as `is_first=true` |
| CASE_APPLICANT_REQUIRED | 400 | `modules/cases/service.py` | Applicants list is empty | Provide at least one applicant |
| CASE_DUPLICATE_APPLICANT_SEQ | 400 | `modules/cases/service.py` | Duplicate applicant sequence | Ensure unique `seq` per applicant |
| CASE_DUPLICATE_FIRST_APPLICANT | 400 | `modules/cases/service.py` | Multiple first applicants | Only one applicant may be first |

### Documents & Attachments
| Code | Typical HTTP status | Where raised (module/file) | When it happens | How to fix |
| --- | --- | --- | --- | --- |
| DOCUMENT_NOT_FOUND | 404 | `modules/documents/service.py` (also tasks) | Document ID not found | Use a valid document ID |
| DOC_TEMPLATE_NOT_FOUND | 404 | `modules/documents/service.py` | Document template missing | Use an existing template ID |
| ATTACHMENT_NOT_FOUND | 404 | `modules/documents/service.py` | Attachment ID not found | Use a valid attachment ID |
| ATTACHMENT_FILENAME_REQUIRED | 400 | `modules/documents/service.py` | Upload missing filename | Provide a filename |
| ATTACHMENT_TOO_LARGE | 400 | `modules/documents/service.py` | File exceeds size limits | Upload a smaller file |
| ATTACHMENT_EXTENSION_NOT_ALLOWED | 400 | `modules/documents/service.py` | File extension blocked | Use an allowed extension |
| ATTACHMENT_MIME_NOT_ALLOWED | 400 | `modules/documents/service.py` | MIME type blocked | Use an allowed MIME type |

### Tasks
| Code | Typical HTTP status | Where raised (module/file) | When it happens | How to fix |
| --- | --- | --- | --- | --- |
| TASK_NOT_FOUND | 404 | `modules/tasks/service.py` | Task ID not found | Use a valid task ID |
| TASK_INVALID_TRANSITION | 400 | `modules/tasks/service.py` | Invalid status transition | Use a valid transition |
| TASK_TEMPLATE_NOT_FOUND | 404 | `modules/tasks/service.py` | Template ID not found | Use a valid task template ID |
| TASK_TEMPLATE_DISABLED | 400 | `modules/tasks/service.py` | Template is disabled | Enable or choose another template |
| TASK_ASSIGNEE_REQUIRED | 400 | `modules/tasks/service.py` | Assign without worker/supervisor | Provide `worker_id` or `supervisor_id` |
| USER_NOT_FOUND | 404 | `modules/tasks/service.py` | User ID not found | Use a valid user ID |
| DOCUMENT_NOT_FOUND | 404 | `modules/tasks/service.py` | Document ID not found | Use a valid document ID |
| CASE_NOT_FOUND | 404 | `modules/tasks/service.py` | Case ID not found | Use a valid case ID |

### Fees
| Code | Typical HTTP status | Where raised (module/file) | When it happens | How to fix |
| --- | --- | --- | --- | --- |
| FEE_DRAFT_NOT_FOUND | 404 | `modules/fees/service.py` | Draft ID not found | Use a valid draft ID |
| FEE_DRAFT_LOCKED | 409 | `modules/fees/service.py` | Draft is locked | Unlock draft or create a new one |
| FEE_DRAFT_ALREADY_LOCKED | 409 | `modules/fees/service.py` | Draft already locked | No-op or unlock first |
| FEE_DRAFT_NOT_LOCKED | 409 | `modules/fees/service.py` | Draft not locked | Lock draft before expected locked action |
| FEE_RATE_NOT_FOUND | 404 | `modules/fees/service.py` | Fee rate ID not found | Use a valid fee rate ID |
| FEE_RATE_DISABLED | 400 | `modules/fees/service.py` | Fee rate disabled | Enable or choose another rate |
| FEE_ITEM_NOT_FOUND | 404 | `modules/fees/service.py` | Fee item not found | Use a valid fee item ID |
| FEE_CURRENCY_MISMATCH | 400 | `modules/fees/service.py` | Draft currency != rate currency | Use matching currencies |
| CLIENT_NOT_FOUND | 404 | `modules/fees/service.py` | Client ID not found | Use a valid client ID |
| CASE_NOT_FOUND | 404 | `modules/fees/service.py` | Case ID not found | Use a valid case ID |

### Billing / Payments / Offsets
| Code | Typical HTTP status | Where raised (module/file) | When it happens | How to fix |
| --- | --- | --- | --- | --- |
| BILL_NOT_FOUND | 404 | `modules/billing/service.py` | Bill ID not found | Use a valid bill ID |
| BILL_DRAFT_NOT_FOUND | 404 | `modules/billing/service.py` | Drafts missing when billing | Use valid draft IDs |
| BILL_CLIENT_REQUIRED | 400 | `modules/billing/service.py` | Draft missing client | Ensure drafts have `client_id` |
| BILL_SINGLE_CLIENT_REQUIRED | 400 | `modules/billing/service.py` | Drafts span multiple clients | Use drafts from a single client |
| BILL_CURRENCY_MISMATCH | 400 | `modules/billing/service.py` | Bill currency mismatch | Use consistent currency |
| BILL_AMOUNT_INVALID | 400 | `modules/billing/service.py` | Negative bill amount | Provide non-negative totals |
| BILL_ITEM_REQUIRED | 400 | `modules/billing/service.py` | No bill items found | Ensure drafts have items |
| BILL_ITEM_AMOUNT_INVALID | 400 | `modules/billing/service.py` | Item amount negative | Use non-negative amounts |
| BILL_ITEM_FEE_TYPE_INVALID | 400 | `modules/billing/service.py` | Invalid fee type | Use GOV/SERVICE/MISC |
| BILL_ITEM_TOTAL_MISMATCH | 400 | `modules/billing/service.py` | Draft totals != item totals | Recalculate draft/item totals |
| BILL_STATUS_INVALID | 400 | `modules/billing/service.py` | Invalid status value | Use allowed statuses |
| BILL_STATUS_TRANSITION_INVALID | 400 | `modules/billing/service.py` | Invalid status transition | Use a valid transition |
| PAYMENT_NOT_FOUND | 404 | `modules/billing/service.py` | Payment not found | Use a valid payment ID |
| PAYMENT_LINE_NOT_FOUND | 404 | `modules/billing/service.py` | Payment line not found | Use a valid payment line ID |
| PAYMENT_AMOUNT_INVALID | 400 | `modules/billing/service.py` | Negative payment amount | Provide non-negative amount |
| OFFSET_AMOUNT_INVALID | 400 | `modules/billing/service.py` | Offset amount <= 0 | Provide a positive amount |
| OFFSET_CLIENT_MISMATCH | 400 | `modules/billing/service.py` | Payment client != bill client | Use matching client |
| OFFSET_CURRENCY_MISMATCH | 400 | `modules/billing/service.py` | Payment currency != bill currency | Use matching currency |
| OFFSET_EXCEEDS_PAYMENT_BALANCE | 400 | `modules/billing/service.py` | Offset exceeds payment balance | Reduce offset amount |
| OFFSET_EXCEEDS_BILL_BALANCE | 400 | `modules/billing/service.py` | Offset exceeds bill balance | Reduce offset amount |

### Post-enhancement domains (reserved conventions)
As of 2026-02-28, these domains are planned but not yet routed in `app/api/router.py`.
The following mappings are reserved for upcoming implementation tasks and must follow the envelope constraints above.

#### Annuity
| Code | Typical HTTP status | Planned meaning |
| --- | --- | --- |
| ANNUITY_TASK_NOT_FOUND | 404 | Annuity task ID not found |
| ANNUITY_INSTRUCTION_INVALID | 400 | Instruction payload/state invalid |
| ANNUITY_DRAFT_ALREADY_GENERATED | 409 | Fee draft generation is duplicate/conflicting |
| PAY_LIST_SCOPE_INVALID | 400 | Selected items violate single-client/single-currency constraints |
| GOV_PAYMENT_DUPLICATE | 409 | Duplicate gov-payment registration |
| ANNUITY_CONFIG_MISSING | 409 | Required annuity configuration is missing |

#### Collections (Dunning / Bad Debt)
| Code | Typical HTTP status | Planned meaning |
| --- | --- | --- |
| DUNNING_BATCH_NOT_FOUND | 404 | Dunning batch ID not found |
| DUNNING_BATCH_STATE_INVALID | 400 | Dunning operation invalid for current batch status |
| BAD_DEBT_NOT_ALLOWED | 400 | Bill is not eligible for bad-debt action |
| BAD_DEBT_ALREADY_MARKED | 409 | Bill already marked as bad debt |
| BAD_DEBT_RESTORE_INVALID | 409 | Restore requested for bill not in bad-debt state |

#### Commission
| Code | Typical HTTP status | Planned meaning |
| --- | --- | --- |
| COMMISSION_RULE_NOT_FOUND | 404 | Commission rule ID not found |
| COMMISSION_RULE_CONFLICT | 409 | Rule overlaps/conflicts with existing rule dimensions |
| COMMISSION_RECORD_NOT_FOUND | 404 | Commission record ID not found |
| COMMISSION_STATUS_INVALID | 400 | Invalid lifecycle transition/state update |
| COMMISSION_SETTLEMENT_NOT_FOUND | 404 | Settlement batch ID not found |
| COMMISSION_SETTLEMENT_CONFLICT | 409 | Settlement action conflicts with current state |

#### Consulting / Search
| Code | Typical HTTP status | Planned meaning |
| --- | --- | --- |
| CONSULTING_CASE_REQUIRED | 400 | Case type/business context is required for consulting flow |
| CONSULTING_EXPENSE_NOT_FOUND | 404 | Consulting expense record not found |
| CONSULTING_EXPENSE_INVALID | 400 | Expense payload/business rule validation failed |
| SEARCH_REQUEST_NOT_FOUND | 404 | Search request/report not found |
| SEARCH_RESULT_INVALID | 400 | Search result payload is invalid for current workflow |
| CONSULTING_CONFLICT | 409 | Duplicate or conflicting consulting/search operation |

### Templates
| Code | Typical HTTP status | Where raised (module/file) | When it happens | How to fix |
| --- | --- | --- | --- | --- |
| TEMPLATE_NOT_FOUND | 404 | `modules/templates/service.py` | Template ID not found | Use a valid template ID |
| LETTERHEAD_NOT_FOUND | 404 | `modules/templates/service.py` | Letterhead ID not found | Use a valid letterhead ID |

### System
No BusinessError codes are currently raised directly from the System module.

## Notes for clients
- Client code should branch on `error.code`, not the message text.
- `error.details` is for debugging and may change shape over time.
