# Phase 3 Codex Batch Execution Checklist — Grouped (CLEAN)

Generated from `apis.zip` after removing macOS `__MACOSX/` and `._*` files. Execute tasks in order.


## Module: clients

**Router include checkpoint (run once when you start this module):**

1) Check whether module paths already exist in app routes:
```bash
PYTHONPATH=backend python -c "from app.main import app; print('\n'.join(sorted({r.path for r in app.routes if hasattr(r,'path')})))" | grep -i -E '/clients(/|$)' || true
```

2) If nothing is printed, include this module router ONCE in `backend/app/api/router.py`:
- Import the module router (example):
  `from app.modules.clients.api import router as clients_router`
- Include it:
  `api_router.include_router(clients_router, tags=["Clients"])`

Re-run step (1) until paths appear.

### TASK_FILE: apis/BE-APIv4-001_clients_get_clients.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT put Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run Verify.
```

### TASK_FILE: apis/BE-APIv4-002_clients_post_clients.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT put Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run Verify.
```

### TASK_FILE: apis/BE-APIv4-003_clients_put_clients_id.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT put Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run Verify.
```

### TASK_FILE: apis/BE-APIv4-004_clients_put_clients_id_deactivate.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT put Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run Verify.
```


## Module: cases

**Router include checkpoint (run once when you start this module):**

1) Check whether module paths already exist in app routes:
```bash
PYTHONPATH=backend python -c "from app.main import app; print('\n'.join(sorted({r.path for r in app.routes if hasattr(r,'path')})))" | grep -i -E '/cases(/|$)' || true
```

2) If nothing is printed, include this module router ONCE in `backend/app/api/router.py`:
- Import the module router (example):
  `from app.modules.cases.api import router as cases_router`
- Include it:
  `api_router.include_router(cases_router, tags=["Cases"])`

Re-run step (1) until paths appear.

### TASK_FILE: apis/BE-APIv4-005_cases_get_cases.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT put Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run Verify.
```

### TASK_FILE: apis/BE-APIv4-006_cases_post_cases.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT put Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run Verify.
```

### TASK_FILE: apis/BE-APIv4-007_cases_get_cases_case_id.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT put Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run Verify.
```

### TASK_FILE: apis/BE-APIv4-008_cases_put_cases_case_id.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT put Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run Verify.
```

### TASK_FILE: apis/BE-APIv4-009_cases_post_cases_case_id_limited-edit.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT put Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run Verify.
```

### TASK_FILE: apis/BE-APIv4-010_cases_get_cases_export.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT put Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run Verify.
```


## Module: documents

**Router include checkpoint (run once when you start this module):**

1) Check whether module paths already exist in app routes:
```bash
PYTHONPATH=backend python -c "from app.main import app; print('\n'.join(sorted({r.path for r in app.routes if hasattr(r,'path')})))" | grep -i -E '/documents(/|$)' || true
```

2) If nothing is printed, include this module router ONCE in `backend/app/api/router.py`:
- Import the module router (example):
  `from app.modules.documents.api import router as documents_router`
- Include it:
  `api_router.include_router(documents_router, tags=["Documents"])`

Re-run step (1) until paths appear.

### TASK_FILE: apis/BE-APIv4-011_documents_get_documents.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT put Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run Verify.
```

### TASK_FILE: apis/BE-APIv4-012_documents_post_documents.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT put Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run Verify.
```

### TASK_FILE: apis/BE-APIv4-013_documents_get_documents_id.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT put Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run Verify.
```

### TASK_FILE: apis/BE-APIv4-014_documents_put_documents_id.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT put Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run Verify.
```

### TASK_FILE: apis/BE-APIv4-015_documents_post_documents_id_attachments.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT put Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run Verify.
```

### TASK_FILE: apis/BE-APIv4-016_documents_get_documents_id_attachments_att_id_download.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT put Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run Verify.
```


## Module: tasks

**Router include checkpoint (run once when you start this module):**

1) Check whether module paths already exist in app routes:
```bash
PYTHONPATH=backend python -c "from app.main import app; print('\n'.join(sorted({r.path for r in app.routes if hasattr(r,'path')})))" | grep -i -E '/tasks(/|$)' || true
```

2) If nothing is printed, include this module router ONCE in `backend/app/api/router.py`:
- Import the module router (example):
  `from app.modules.tasks.api import router as tasks_router`
- Include it:
  `api_router.include_router(tasks_router, tags=["Tasks"])`

Re-run step (1) until paths appear.

### TASK_FILE: apis/BE-APIv4-017_tasks_get_tasks.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT put Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run Verify.
```

### TASK_FILE: apis/BE-APIv4-018_tasks_post_tasks.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT put Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run Verify.
```

### TASK_FILE: apis/BE-APIv4-019_tasks_get_tasks_id.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT put Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run Verify.
```

### TASK_FILE: apis/BE-APIv4-020_tasks_put_tasks_id.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT put Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run Verify.
```

### TASK_FILE: apis/BE-APIv4-021_tasks_post_tasks_id_close.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT put Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run Verify.
```

### TASK_FILE: apis/BE-APIv4-022_tasks_post_tasks_id_reopen.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT put Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run Verify.
```

### TASK_FILE: apis/BE-APIv4-023_tasks_post_tasks_id_cancel.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT put Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run Verify.
```

### TASK_FILE: apis/BE-APIv4-024_tasks_get_tasks_today?as=worker|supervisor.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT put Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run Verify.
```


## Module: fees

**Router include checkpoint (run once when you start this module):**

1) Check whether module paths already exist in app routes:
```bash
PYTHONPATH=backend python -c "from app.main import app; print('\n'.join(sorted({r.path for r in app.routes if hasattr(r,'path')})))" | grep -i -E '/fees(/|$)' || true
```

2) If nothing is printed, include this module router ONCE in `backend/app/api/router.py`:
- Import the module router (example):
  `from app.modules.fees.api import router as fees_router`
- Include it:
  `api_router.include_router(fees_router, tags=["Fees"])`

Re-run step (1) until paths appear.

### TASK_FILE: apis/BE-APIv4-025_fees_get_fees_drafts.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT put Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run Verify.
```

### TASK_FILE: apis/BE-APIv4-026_fees_post_fees_drafts.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT put Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run Verify.
```

### TASK_FILE: apis/BE-APIv4-027_fees_get_fees_drafts_id.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT put Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run Verify.
```

### TASK_FILE: apis/BE-APIv4-028_fees_put_fees_drafts_id.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT put Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run Verify.
```

### TASK_FILE: apis/BE-APIv4-029_fees_post_fees_drafts_id_lock.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT put Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run Verify.
```

### TASK_FILE: apis/BE-APIv4-030_fees_post_fees_drafts_id_unlock.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT put Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run Verify.
```

### TASK_FILE: apis/BE-APIv4-031_fees_post_fees_drafts_id_items.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT put Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run Verify.
```

### TASK_FILE: apis/BE-APIv4-032_fees_put_fees_items_item_id.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT put Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run Verify.
```

### TASK_FILE: apis/BE-APIv4-033_fees_delete_fees_items_item_id.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT put Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run Verify.
```

### TASK_FILE: apis/BE-APIv4-034_fees_get_fees_rates.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT put Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run Verify.
```

### TASK_FILE: apis/BE-APIv4-035_fees_post_fees_rates.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT put Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run Verify.
```

### TASK_FILE: apis/BE-APIv4-036_fees_put_fees_rates_id.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT put Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run Verify.
```


## Module: billing

**Router include checkpoint (run once when you start this module):**

1) Check whether module paths already exist in app routes:
```bash
PYTHONPATH=backend python -c "from app.main import app; print('\n'.join(sorted({r.path for r in app.routes if hasattr(r,'path')})))" | grep -i -E '/billing(/|$)' || true
```

2) If nothing is printed, include this module router ONCE in `backend/app/api/router.py`:
- Import the module router (example):
  `from app.modules.billing.api import router as billing_router`
- Include it:
  `api_router.include_router(billing_router, tags=["Billing"])`

Re-run step (1) until paths appear.

### TASK_FILE: apis/BE-APIv4-037_billing_get_bills.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT put Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run Verify.
```

### TASK_FILE: apis/BE-APIv4-038_billing_post_bills_from-drafts.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT put Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run Verify.
```

### TASK_FILE: apis/BE-APIv4-039_billing_post_bills_manual.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT put Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run Verify.
```

### TASK_FILE: apis/BE-APIv4-040_billing_get_bills_id.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT put Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run Verify.
```

### TASK_FILE: apis/BE-APIv4-041_billing_get_bills_id_print.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT put Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run Verify.
```

### TASK_FILE: apis/BE-APIv4-042_billing_get_payments.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT put Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run Verify.
```

### TASK_FILE: apis/BE-APIv4-043_billing_post_payments.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT put Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run Verify.
```

### TASK_FILE: apis/BE-APIv4-044_billing_get_payments_id.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT put Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run Verify.
```

### TASK_FILE: apis/BE-APIv4-045_billing_post_offsets.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT put Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run Verify.
```

### TASK_FILE: apis/BE-APIv4-046_billing_post_offsets_id_reverse.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT put Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run Verify.
```

### TASK_FILE: apis/BE-APIv4-047_billing_get_cases_case_id_receipts.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT put Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run Verify.
```


## Module: misc

**Router include checkpoint (run once when you start this module):**

1) Check whether module paths already exist in app routes:
```bash
PYTHONPATH=backend python -c "from app.main import app; print('\n'.join(sorted({r.path for r in app.routes if hasattr(r,'path')})))" | grep -i -E '/misc(/|$)' || true
```

2) If nothing is printed, include this module router ONCE in `backend/app/api/router.py`:
- Import the module router (example):
  `from app.modules.misc.api import router as misc_router`
- Include it:
  `api_router.include_router(misc_router, tags=["Misc"])`

Re-run step (1) until paths appear.

### TASK_FILE: apis/README.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT put Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run Verify.
```



## Verify (run after each task)
```bash
ruff check --fix .
ruff format .
ruff check .
PYTHONPATH=backend python -c "from app.main import app; print('OK: app import')"
```

**Optional sanity (recommended after first task of each module):**
```bash
PYTHONPATH=backend python -c "from app.main import app; print('\n'.join(sorted({r.path for r in app.routes if hasattr(r,'path')})))" | head -n 160
```
