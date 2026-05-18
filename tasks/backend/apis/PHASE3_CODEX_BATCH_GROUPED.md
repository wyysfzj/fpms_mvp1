# Phase 3 Codex Batch Execution Checklist (Grouped by Module)

This checklist is generated from `apis.zip`. Execute tasks in order. Each module's first task includes an explicit router include checkpoint.


## Module: BE-APIv4-001

**Router include checkpoint (module-level, run once per module):**

1) Check whether paths for this module are present:
```bash
PYTHONPATH=backend python -c "from app.main import app; print('\n'.join(sorted({r.path for r in app.routes if hasattr(r,'path')})))" | grep -i -E '/BE-APIv4-001(/|$)' || true
```

2) If nothing is printed, you must include this module router **once** in `backend/app/api/router.py`:
- Import: `from app.modules.<...>.api import router as BE-APIv4-001_router`
- Include: `api_router.include_router(BE-APIv4-001_router, tags=["Be Apiv4 001"])`

After wiring, re-run step (1) until module paths appear.

### TASK_FILE: __MACOSX/apis/._BE-APIv4-001_clients_get_clients.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT place Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run the Verify commands.
```


## Module: clients

**Router include checkpoint (module-level, run once per module):**

1) Check whether paths for this module are present:
```bash
PYTHONPATH=backend python -c "from app.main import app; print('\n'.join(sorted({r.path for r in app.routes if hasattr(r,'path')})))" | grep -i -E '/clients(/|$)' || true
```

2) If nothing is printed, you must include this module router **once** in `backend/app/api/router.py`:
- Import: `from app.modules.<...>.api import router as clients_router`
- Include: `api_router.include_router(clients_router, tags=["Clients"])`

After wiring, re-run step (1) until module paths appear.

### TASK_FILE: apis/BE-APIv4-001_clients_get_clients.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT place Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run the Verify commands.
```

### TASK_FILE: apis/BE-APIv4-002_clients_post_clients.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT place Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run the Verify commands.
```

### TASK_FILE: apis/BE-APIv4-003_clients_put_clients_id.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT place Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run the Verify commands.
```

### TASK_FILE: apis/BE-APIv4-004_clients_put_clients_id_deactivate.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT place Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run the Verify commands.
```


## Module: BE-APIv4-002

**Router include checkpoint (module-level, run once per module):**

1) Check whether paths for this module are present:
```bash
PYTHONPATH=backend python -c "from app.main import app; print('\n'.join(sorted({r.path for r in app.routes if hasattr(r,'path')})))" | grep -i -E '/BE-APIv4-002(/|$)' || true
```

2) If nothing is printed, you must include this module router **once** in `backend/app/api/router.py`:
- Import: `from app.modules.<...>.api import router as BE-APIv4-002_router`
- Include: `api_router.include_router(BE-APIv4-002_router, tags=["Be Apiv4 002"])`

After wiring, re-run step (1) until module paths appear.

### TASK_FILE: __MACOSX/apis/._BE-APIv4-002_clients_post_clients.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT place Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run the Verify commands.
```


## Module: BE-APIv4-003

**Router include checkpoint (module-level, run once per module):**

1) Check whether paths for this module are present:
```bash
PYTHONPATH=backend python -c "from app.main import app; print('\n'.join(sorted({r.path for r in app.routes if hasattr(r,'path')})))" | grep -i -E '/BE-APIv4-003(/|$)' || true
```

2) If nothing is printed, you must include this module router **once** in `backend/app/api/router.py`:
- Import: `from app.modules.<...>.api import router as BE-APIv4-003_router`
- Include: `api_router.include_router(BE-APIv4-003_router, tags=["Be Apiv4 003"])`

After wiring, re-run step (1) until module paths appear.

### TASK_FILE: __MACOSX/apis/._BE-APIv4-003_clients_put_clients_id.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT place Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run the Verify commands.
```


## Module: BE-APIv4-004

**Router include checkpoint (module-level, run once per module):**

1) Check whether paths for this module are present:
```bash
PYTHONPATH=backend python -c "from app.main import app; print('\n'.join(sorted({r.path for r in app.routes if hasattr(r,'path')})))" | grep -i -E '/BE-APIv4-004(/|$)' || true
```

2) If nothing is printed, you must include this module router **once** in `backend/app/api/router.py`:
- Import: `from app.modules.<...>.api import router as BE-APIv4-004_router`
- Include: `api_router.include_router(BE-APIv4-004_router, tags=["Be Apiv4 004"])`

After wiring, re-run step (1) until module paths appear.

### TASK_FILE: __MACOSX/apis/._BE-APIv4-004_clients_put_clients_id_deactivate.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT place Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run the Verify commands.
```


## Module: BE-APIv4-005

**Router include checkpoint (module-level, run once per module):**

1) Check whether paths for this module are present:
```bash
PYTHONPATH=backend python -c "from app.main import app; print('\n'.join(sorted({r.path for r in app.routes if hasattr(r,'path')})))" | grep -i -E '/BE-APIv4-005(/|$)' || true
```

2) If nothing is printed, you must include this module router **once** in `backend/app/api/router.py`:
- Import: `from app.modules.<...>.api import router as BE-APIv4-005_router`
- Include: `api_router.include_router(BE-APIv4-005_router, tags=["Be Apiv4 005"])`

After wiring, re-run step (1) until module paths appear.

### TASK_FILE: __MACOSX/apis/._BE-APIv4-005_cases_get_cases.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT place Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run the Verify commands.
```


## Module: cases

**Router include checkpoint (module-level, run once per module):**

1) Check whether paths for this module are present:
```bash
PYTHONPATH=backend python -c "from app.main import app; print('\n'.join(sorted({r.path for r in app.routes if hasattr(r,'path')})))" | grep -i -E '/cases(/|$)' || true
```

2) If nothing is printed, you must include this module router **once** in `backend/app/api/router.py`:
- Import: `from app.modules.<...>.api import router as cases_router`
- Include: `api_router.include_router(cases_router, tags=["Cases"])`

After wiring, re-run step (1) until module paths appear.

### TASK_FILE: apis/BE-APIv4-005_cases_get_cases.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT place Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run the Verify commands.
```

### TASK_FILE: apis/BE-APIv4-006_cases_post_cases.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT place Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run the Verify commands.
```

### TASK_FILE: apis/BE-APIv4-007_cases_get_cases_case_id.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT place Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run the Verify commands.
```

### TASK_FILE: apis/BE-APIv4-008_cases_put_cases_case_id.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT place Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run the Verify commands.
```

### TASK_FILE: apis/BE-APIv4-009_cases_post_cases_case_id_limited-edit.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT place Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run the Verify commands.
```

### TASK_FILE: apis/BE-APIv4-010_cases_get_cases_export.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT place Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run the Verify commands.
```


## Module: BE-APIv4-006

**Router include checkpoint (module-level, run once per module):**

1) Check whether paths for this module are present:
```bash
PYTHONPATH=backend python -c "from app.main import app; print('\n'.join(sorted({r.path for r in app.routes if hasattr(r,'path')})))" | grep -i -E '/BE-APIv4-006(/|$)' || true
```

2) If nothing is printed, you must include this module router **once** in `backend/app/api/router.py`:
- Import: `from app.modules.<...>.api import router as BE-APIv4-006_router`
- Include: `api_router.include_router(BE-APIv4-006_router, tags=["Be Apiv4 006"])`

After wiring, re-run step (1) until module paths appear.

### TASK_FILE: __MACOSX/apis/._BE-APIv4-006_cases_post_cases.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT place Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run the Verify commands.
```


## Module: BE-APIv4-007

**Router include checkpoint (module-level, run once per module):**

1) Check whether paths for this module are present:
```bash
PYTHONPATH=backend python -c "from app.main import app; print('\n'.join(sorted({r.path for r in app.routes if hasattr(r,'path')})))" | grep -i -E '/BE-APIv4-007(/|$)' || true
```

2) If nothing is printed, you must include this module router **once** in `backend/app/api/router.py`:
- Import: `from app.modules.<...>.api import router as BE-APIv4-007_router`
- Include: `api_router.include_router(BE-APIv4-007_router, tags=["Be Apiv4 007"])`

After wiring, re-run step (1) until module paths appear.

### TASK_FILE: __MACOSX/apis/._BE-APIv4-007_cases_get_cases_case_id.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT place Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run the Verify commands.
```


## Module: BE-APIv4-008

**Router include checkpoint (module-level, run once per module):**

1) Check whether paths for this module are present:
```bash
PYTHONPATH=backend python -c "from app.main import app; print('\n'.join(sorted({r.path for r in app.routes if hasattr(r,'path')})))" | grep -i -E '/BE-APIv4-008(/|$)' || true
```

2) If nothing is printed, you must include this module router **once** in `backend/app/api/router.py`:
- Import: `from app.modules.<...>.api import router as BE-APIv4-008_router`
- Include: `api_router.include_router(BE-APIv4-008_router, tags=["Be Apiv4 008"])`

After wiring, re-run step (1) until module paths appear.

### TASK_FILE: __MACOSX/apis/._BE-APIv4-008_cases_put_cases_case_id.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT place Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run the Verify commands.
```


## Module: BE-APIv4-009

**Router include checkpoint (module-level, run once per module):**

1) Check whether paths for this module are present:
```bash
PYTHONPATH=backend python -c "from app.main import app; print('\n'.join(sorted({r.path for r in app.routes if hasattr(r,'path')})))" | grep -i -E '/BE-APIv4-009(/|$)' || true
```

2) If nothing is printed, you must include this module router **once** in `backend/app/api/router.py`:
- Import: `from app.modules.<...>.api import router as BE-APIv4-009_router`
- Include: `api_router.include_router(BE-APIv4-009_router, tags=["Be Apiv4 009"])`

After wiring, re-run step (1) until module paths appear.

### TASK_FILE: __MACOSX/apis/._BE-APIv4-009_cases_post_cases_case_id_limited-edit.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT place Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run the Verify commands.
```


## Module: BE-APIv4-010

**Router include checkpoint (module-level, run once per module):**

1) Check whether paths for this module are present:
```bash
PYTHONPATH=backend python -c "from app.main import app; print('\n'.join(sorted({r.path for r in app.routes if hasattr(r,'path')})))" | grep -i -E '/BE-APIv4-010(/|$)' || true
```

2) If nothing is printed, you must include this module router **once** in `backend/app/api/router.py`:
- Import: `from app.modules.<...>.api import router as BE-APIv4-010_router`
- Include: `api_router.include_router(BE-APIv4-010_router, tags=["Be Apiv4 010"])`

After wiring, re-run step (1) until module paths appear.

### TASK_FILE: __MACOSX/apis/._BE-APIv4-010_cases_get_cases_export.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT place Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run the Verify commands.
```


## Module: BE-APIv4-011

**Router include checkpoint (module-level, run once per module):**

1) Check whether paths for this module are present:
```bash
PYTHONPATH=backend python -c "from app.main import app; print('\n'.join(sorted({r.path for r in app.routes if hasattr(r,'path')})))" | grep -i -E '/BE-APIv4-011(/|$)' || true
```

2) If nothing is printed, you must include this module router **once** in `backend/app/api/router.py`:
- Import: `from app.modules.<...>.api import router as BE-APIv4-011_router`
- Include: `api_router.include_router(BE-APIv4-011_router, tags=["Be Apiv4 011"])`

After wiring, re-run step (1) until module paths appear.

### TASK_FILE: __MACOSX/apis/._BE-APIv4-011_documents_get_documents.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT place Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run the Verify commands.
```


## Module: documents

**Router include checkpoint (module-level, run once per module):**

1) Check whether paths for this module are present:
```bash
PYTHONPATH=backend python -c "from app.main import app; print('\n'.join(sorted({r.path for r in app.routes if hasattr(r,'path')})))" | grep -i -E '/documents(/|$)' || true
```

2) If nothing is printed, you must include this module router **once** in `backend/app/api/router.py`:
- Import: `from app.modules.<...>.api import router as documents_router`
- Include: `api_router.include_router(documents_router, tags=["Documents"])`

After wiring, re-run step (1) until module paths appear.

### TASK_FILE: apis/BE-APIv4-011_documents_get_documents.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT place Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run the Verify commands.
```

### TASK_FILE: apis/BE-APIv4-012_documents_post_documents.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT place Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run the Verify commands.
```

### TASK_FILE: apis/BE-APIv4-013_documents_get_documents_id.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT place Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run the Verify commands.
```

### TASK_FILE: apis/BE-APIv4-014_documents_put_documents_id.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT place Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run the Verify commands.
```

### TASK_FILE: apis/BE-APIv4-015_documents_post_documents_id_attachments.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT place Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run the Verify commands.
```

### TASK_FILE: apis/BE-APIv4-016_documents_get_documents_id_attachments_att_id_download.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT place Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run the Verify commands.
```


## Module: BE-APIv4-012

**Router include checkpoint (module-level, run once per module):**

1) Check whether paths for this module are present:
```bash
PYTHONPATH=backend python -c "from app.main import app; print('\n'.join(sorted({r.path for r in app.routes if hasattr(r,'path')})))" | grep -i -E '/BE-APIv4-012(/|$)' || true
```

2) If nothing is printed, you must include this module router **once** in `backend/app/api/router.py`:
- Import: `from app.modules.<...>.api import router as BE-APIv4-012_router`
- Include: `api_router.include_router(BE-APIv4-012_router, tags=["Be Apiv4 012"])`

After wiring, re-run step (1) until module paths appear.

### TASK_FILE: __MACOSX/apis/._BE-APIv4-012_documents_post_documents.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT place Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run the Verify commands.
```


## Module: BE-APIv4-013

**Router include checkpoint (module-level, run once per module):**

1) Check whether paths for this module are present:
```bash
PYTHONPATH=backend python -c "from app.main import app; print('\n'.join(sorted({r.path for r in app.routes if hasattr(r,'path')})))" | grep -i -E '/BE-APIv4-013(/|$)' || true
```

2) If nothing is printed, you must include this module router **once** in `backend/app/api/router.py`:
- Import: `from app.modules.<...>.api import router as BE-APIv4-013_router`
- Include: `api_router.include_router(BE-APIv4-013_router, tags=["Be Apiv4 013"])`

After wiring, re-run step (1) until module paths appear.

### TASK_FILE: __MACOSX/apis/._BE-APIv4-013_documents_get_documents_id.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT place Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run the Verify commands.
```


## Module: BE-APIv4-014

**Router include checkpoint (module-level, run once per module):**

1) Check whether paths for this module are present:
```bash
PYTHONPATH=backend python -c "from app.main import app; print('\n'.join(sorted({r.path for r in app.routes if hasattr(r,'path')})))" | grep -i -E '/BE-APIv4-014(/|$)' || true
```

2) If nothing is printed, you must include this module router **once** in `backend/app/api/router.py`:
- Import: `from app.modules.<...>.api import router as BE-APIv4-014_router`
- Include: `api_router.include_router(BE-APIv4-014_router, tags=["Be Apiv4 014"])`

After wiring, re-run step (1) until module paths appear.

### TASK_FILE: __MACOSX/apis/._BE-APIv4-014_documents_put_documents_id.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT place Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run the Verify commands.
```


## Module: BE-APIv4-015

**Router include checkpoint (module-level, run once per module):**

1) Check whether paths for this module are present:
```bash
PYTHONPATH=backend python -c "from app.main import app; print('\n'.join(sorted({r.path for r in app.routes if hasattr(r,'path')})))" | grep -i -E '/BE-APIv4-015(/|$)' || true
```

2) If nothing is printed, you must include this module router **once** in `backend/app/api/router.py`:
- Import: `from app.modules.<...>.api import router as BE-APIv4-015_router`
- Include: `api_router.include_router(BE-APIv4-015_router, tags=["Be Apiv4 015"])`

After wiring, re-run step (1) until module paths appear.

### TASK_FILE: __MACOSX/apis/._BE-APIv4-015_documents_post_documents_id_attachments.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT place Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run the Verify commands.
```


## Module: BE-APIv4-016

**Router include checkpoint (module-level, run once per module):**

1) Check whether paths for this module are present:
```bash
PYTHONPATH=backend python -c "from app.main import app; print('\n'.join(sorted({r.path for r in app.routes if hasattr(r,'path')})))" | grep -i -E '/BE-APIv4-016(/|$)' || true
```

2) If nothing is printed, you must include this module router **once** in `backend/app/api/router.py`:
- Import: `from app.modules.<...>.api import router as BE-APIv4-016_router`
- Include: `api_router.include_router(BE-APIv4-016_router, tags=["Be Apiv4 016"])`

After wiring, re-run step (1) until module paths appear.

### TASK_FILE: __MACOSX/apis/._BE-APIv4-016_documents_get_documents_id_attachments_att_id_download.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT place Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run the Verify commands.
```


## Module: BE-APIv4-017

**Router include checkpoint (module-level, run once per module):**

1) Check whether paths for this module are present:
```bash
PYTHONPATH=backend python -c "from app.main import app; print('\n'.join(sorted({r.path for r in app.routes if hasattr(r,'path')})))" | grep -i -E '/BE-APIv4-017(/|$)' || true
```

2) If nothing is printed, you must include this module router **once** in `backend/app/api/router.py`:
- Import: `from app.modules.<...>.api import router as BE-APIv4-017_router`
- Include: `api_router.include_router(BE-APIv4-017_router, tags=["Be Apiv4 017"])`

After wiring, re-run step (1) until module paths appear.

### TASK_FILE: __MACOSX/apis/._BE-APIv4-017_tasks_get_tasks.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT place Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run the Verify commands.
```


## Module: tasks

**Router include checkpoint (module-level, run once per module):**

1) Check whether paths for this module are present:
```bash
PYTHONPATH=backend python -c "from app.main import app; print('\n'.join(sorted({r.path for r in app.routes if hasattr(r,'path')})))" | grep -i -E '/tasks(/|$)' || true
```

2) If nothing is printed, you must include this module router **once** in `backend/app/api/router.py`:
- Import: `from app.modules.<...>.api import router as tasks_router`
- Include: `api_router.include_router(tasks_router, tags=["Tasks"])`

After wiring, re-run step (1) until module paths appear.

### TASK_FILE: apis/BE-APIv4-017_tasks_get_tasks.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT place Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run the Verify commands.
```

### TASK_FILE: apis/BE-APIv4-018_tasks_post_tasks.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT place Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run the Verify commands.
```

### TASK_FILE: apis/BE-APIv4-019_tasks_get_tasks_id.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT place Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run the Verify commands.
```

### TASK_FILE: apis/BE-APIv4-020_tasks_put_tasks_id.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT place Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run the Verify commands.
```

### TASK_FILE: apis/BE-APIv4-021_tasks_post_tasks_id_close.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT place Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run the Verify commands.
```

### TASK_FILE: apis/BE-APIv4-022_tasks_post_tasks_id_reopen.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT place Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run the Verify commands.
```

### TASK_FILE: apis/BE-APIv4-023_tasks_post_tasks_id_cancel.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT place Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run the Verify commands.
```

### TASK_FILE: apis/BE-APIv4-024_tasks_get_tasks_today_as_worker_supervisor.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT place Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run the Verify commands.
```


## Module: BE-APIv4-018

**Router include checkpoint (module-level, run once per module):**

1) Check whether paths for this module are present:
```bash
PYTHONPATH=backend python -c "from app.main import app; print('\n'.join(sorted({r.path for r in app.routes if hasattr(r,'path')})))" | grep -i -E '/BE-APIv4-018(/|$)' || true
```

2) If nothing is printed, you must include this module router **once** in `backend/app/api/router.py`:
- Import: `from app.modules.<...>.api import router as BE-APIv4-018_router`
- Include: `api_router.include_router(BE-APIv4-018_router, tags=["Be Apiv4 018"])`

After wiring, re-run step (1) until module paths appear.

### TASK_FILE: __MACOSX/apis/._BE-APIv4-018_tasks_post_tasks.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT place Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run the Verify commands.
```


## Module: BE-APIv4-019

**Router include checkpoint (module-level, run once per module):**

1) Check whether paths for this module are present:
```bash
PYTHONPATH=backend python -c "from app.main import app; print('\n'.join(sorted({r.path for r in app.routes if hasattr(r,'path')})))" | grep -i -E '/BE-APIv4-019(/|$)' || true
```

2) If nothing is printed, you must include this module router **once** in `backend/app/api/router.py`:
- Import: `from app.modules.<...>.api import router as BE-APIv4-019_router`
- Include: `api_router.include_router(BE-APIv4-019_router, tags=["Be Apiv4 019"])`

After wiring, re-run step (1) until module paths appear.

### TASK_FILE: __MACOSX/apis/._BE-APIv4-019_tasks_get_tasks_id.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT place Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run the Verify commands.
```


## Module: BE-APIv4-020

**Router include checkpoint (module-level, run once per module):**

1) Check whether paths for this module are present:
```bash
PYTHONPATH=backend python -c "from app.main import app; print('\n'.join(sorted({r.path for r in app.routes if hasattr(r,'path')})))" | grep -i -E '/BE-APIv4-020(/|$)' || true
```

2) If nothing is printed, you must include this module router **once** in `backend/app/api/router.py`:
- Import: `from app.modules.<...>.api import router as BE-APIv4-020_router`
- Include: `api_router.include_router(BE-APIv4-020_router, tags=["Be Apiv4 020"])`

After wiring, re-run step (1) until module paths appear.

### TASK_FILE: __MACOSX/apis/._BE-APIv4-020_tasks_put_tasks_id.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT place Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run the Verify commands.
```


## Module: BE-APIv4-021

**Router include checkpoint (module-level, run once per module):**

1) Check whether paths for this module are present:
```bash
PYTHONPATH=backend python -c "from app.main import app; print('\n'.join(sorted({r.path for r in app.routes if hasattr(r,'path')})))" | grep -i -E '/BE-APIv4-021(/|$)' || true
```

2) If nothing is printed, you must include this module router **once** in `backend/app/api/router.py`:
- Import: `from app.modules.<...>.api import router as BE-APIv4-021_router`
- Include: `api_router.include_router(BE-APIv4-021_router, tags=["Be Apiv4 021"])`

After wiring, re-run step (1) until module paths appear.

### TASK_FILE: __MACOSX/apis/._BE-APIv4-021_tasks_post_tasks_id_close.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT place Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run the Verify commands.
```


## Module: BE-APIv4-022

**Router include checkpoint (module-level, run once per module):**

1) Check whether paths for this module are present:
```bash
PYTHONPATH=backend python -c "from app.main import app; print('\n'.join(sorted({r.path for r in app.routes if hasattr(r,'path')})))" | grep -i -E '/BE-APIv4-022(/|$)' || true
```

2) If nothing is printed, you must include this module router **once** in `backend/app/api/router.py`:
- Import: `from app.modules.<...>.api import router as BE-APIv4-022_router`
- Include: `api_router.include_router(BE-APIv4-022_router, tags=["Be Apiv4 022"])`

After wiring, re-run step (1) until module paths appear.

### TASK_FILE: __MACOSX/apis/._BE-APIv4-022_tasks_post_tasks_id_reopen.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT place Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run the Verify commands.
```


## Module: BE-APIv4-023

**Router include checkpoint (module-level, run once per module):**

1) Check whether paths for this module are present:
```bash
PYTHONPATH=backend python -c "from app.main import app; print('\n'.join(sorted({r.path for r in app.routes if hasattr(r,'path')})))" | grep -i -E '/BE-APIv4-023(/|$)' || true
```

2) If nothing is printed, you must include this module router **once** in `backend/app/api/router.py`:
- Import: `from app.modules.<...>.api import router as BE-APIv4-023_router`
- Include: `api_router.include_router(BE-APIv4-023_router, tags=["Be Apiv4 023"])`

After wiring, re-run step (1) until module paths appear.

### TASK_FILE: __MACOSX/apis/._BE-APIv4-023_tasks_post_tasks_id_cancel.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT place Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run the Verify commands.
```


## Module: BE-APIv4-024

**Router include checkpoint (module-level, run once per module):**

1) Check whether paths for this module are present:
```bash
PYTHONPATH=backend python -c "from app.main import app; print('\n'.join(sorted({r.path for r in app.routes if hasattr(r,'path')})))" | grep -i -E '/BE-APIv4-024(/|$)' || true
```

2) If nothing is printed, you must include this module router **once** in `backend/app/api/router.py`:
- Import: `from app.modules.<...>.api import router as BE-APIv4-024_router`
- Include: `api_router.include_router(BE-APIv4-024_router, tags=["Be Apiv4 024"])`

After wiring, re-run step (1) until module paths appear.

### TASK_FILE: __MACOSX/apis/._BE-APIv4-024_tasks_get_tasks_today_as_worker_supervisor.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT place Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run the Verify commands.
```


## Module: BE-APIv4-025

**Router include checkpoint (module-level, run once per module):**

1) Check whether paths for this module are present:
```bash
PYTHONPATH=backend python -c "from app.main import app; print('\n'.join(sorted({r.path for r in app.routes if hasattr(r,'path')})))" | grep -i -E '/BE-APIv4-025(/|$)' || true
```

2) If nothing is printed, you must include this module router **once** in `backend/app/api/router.py`:
- Import: `from app.modules.<...>.api import router as BE-APIv4-025_router`
- Include: `api_router.include_router(BE-APIv4-025_router, tags=["Be Apiv4 025"])`

After wiring, re-run step (1) until module paths appear.

### TASK_FILE: __MACOSX/apis/._BE-APIv4-025_fees_get_fees_drafts.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT place Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run the Verify commands.
```


## Module: fees

**Router include checkpoint (module-level, run once per module):**

1) Check whether paths for this module are present:
```bash
PYTHONPATH=backend python -c "from app.main import app; print('\n'.join(sorted({r.path for r in app.routes if hasattr(r,'path')})))" | grep -i -E '/fees(/|$)' || true
```

2) If nothing is printed, you must include this module router **once** in `backend/app/api/router.py`:
- Import: `from app.modules.<...>.api import router as fees_router`
- Include: `api_router.include_router(fees_router, tags=["Fees"])`

After wiring, re-run step (1) until module paths appear.

### TASK_FILE: apis/BE-APIv4-025_fees_get_fees_drafts.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT place Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run the Verify commands.
```

### TASK_FILE: apis/BE-APIv4-026_fees_post_fees_drafts.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT place Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run the Verify commands.
```

### TASK_FILE: apis/BE-APIv4-027_fees_get_fees_drafts_id.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT place Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run the Verify commands.
```

### TASK_FILE: apis/BE-APIv4-028_fees_put_fees_drafts_id.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT place Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run the Verify commands.
```

### TASK_FILE: apis/BE-APIv4-029_fees_post_fees_drafts_id_lock.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT place Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run the Verify commands.
```

### TASK_FILE: apis/BE-APIv4-030_fees_post_fees_drafts_id_unlock.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT place Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run the Verify commands.
```

### TASK_FILE: apis/BE-APIv4-031_fees_post_fees_drafts_id_items.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT place Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run the Verify commands.
```

### TASK_FILE: apis/BE-APIv4-032_fees_put_fees_items_item_id.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT place Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run the Verify commands.
```

### TASK_FILE: apis/BE-APIv4-033_fees_delete_fees_items_item_id.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT place Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run the Verify commands.
```

### TASK_FILE: apis/BE-APIv4-034_fees_get_fees_rates.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT place Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run the Verify commands.
```

### TASK_FILE: apis/BE-APIv4-035_fees_post_fees_rates.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT place Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run the Verify commands.
```

### TASK_FILE: apis/BE-APIv4-036_fees_put_fees_rates_id.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT place Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run the Verify commands.
```


## Module: BE-APIv4-026

**Router include checkpoint (module-level, run once per module):**

1) Check whether paths for this module are present:
```bash
PYTHONPATH=backend python -c "from app.main import app; print('\n'.join(sorted({r.path for r in app.routes if hasattr(r,'path')})))" | grep -i -E '/BE-APIv4-026(/|$)' || true
```

2) If nothing is printed, you must include this module router **once** in `backend/app/api/router.py`:
- Import: `from app.modules.<...>.api import router as BE-APIv4-026_router`
- Include: `api_router.include_router(BE-APIv4-026_router, tags=["Be Apiv4 026"])`

After wiring, re-run step (1) until module paths appear.

### TASK_FILE: __MACOSX/apis/._BE-APIv4-026_fees_post_fees_drafts.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT place Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run the Verify commands.
```


## Module: BE-APIv4-027

**Router include checkpoint (module-level, run once per module):**

1) Check whether paths for this module are present:
```bash
PYTHONPATH=backend python -c "from app.main import app; print('\n'.join(sorted({r.path for r in app.routes if hasattr(r,'path')})))" | grep -i -E '/BE-APIv4-027(/|$)' || true
```

2) If nothing is printed, you must include this module router **once** in `backend/app/api/router.py`:
- Import: `from app.modules.<...>.api import router as BE-APIv4-027_router`
- Include: `api_router.include_router(BE-APIv4-027_router, tags=["Be Apiv4 027"])`

After wiring, re-run step (1) until module paths appear.

### TASK_FILE: __MACOSX/apis/._BE-APIv4-027_fees_get_fees_drafts_id.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT place Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run the Verify commands.
```


## Module: BE-APIv4-028

**Router include checkpoint (module-level, run once per module):**

1) Check whether paths for this module are present:
```bash
PYTHONPATH=backend python -c "from app.main import app; print('\n'.join(sorted({r.path for r in app.routes if hasattr(r,'path')})))" | grep -i -E '/BE-APIv4-028(/|$)' || true
```

2) If nothing is printed, you must include this module router **once** in `backend/app/api/router.py`:
- Import: `from app.modules.<...>.api import router as BE-APIv4-028_router`
- Include: `api_router.include_router(BE-APIv4-028_router, tags=["Be Apiv4 028"])`

After wiring, re-run step (1) until module paths appear.

### TASK_FILE: __MACOSX/apis/._BE-APIv4-028_fees_put_fees_drafts_id.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT place Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run the Verify commands.
```


## Module: BE-APIv4-029

**Router include checkpoint (module-level, run once per module):**

1) Check whether paths for this module are present:
```bash
PYTHONPATH=backend python -c "from app.main import app; print('\n'.join(sorted({r.path for r in app.routes if hasattr(r,'path')})))" | grep -i -E '/BE-APIv4-029(/|$)' || true
```

2) If nothing is printed, you must include this module router **once** in `backend/app/api/router.py`:
- Import: `from app.modules.<...>.api import router as BE-APIv4-029_router`
- Include: `api_router.include_router(BE-APIv4-029_router, tags=["Be Apiv4 029"])`

After wiring, re-run step (1) until module paths appear.

### TASK_FILE: __MACOSX/apis/._BE-APIv4-029_fees_post_fees_drafts_id_lock.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT place Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run the Verify commands.
```


## Module: BE-APIv4-030

**Router include checkpoint (module-level, run once per module):**

1) Check whether paths for this module are present:
```bash
PYTHONPATH=backend python -c "from app.main import app; print('\n'.join(sorted({r.path for r in app.routes if hasattr(r,'path')})))" | grep -i -E '/BE-APIv4-030(/|$)' || true
```

2) If nothing is printed, you must include this module router **once** in `backend/app/api/router.py`:
- Import: `from app.modules.<...>.api import router as BE-APIv4-030_router`
- Include: `api_router.include_router(BE-APIv4-030_router, tags=["Be Apiv4 030"])`

After wiring, re-run step (1) until module paths appear.

### TASK_FILE: __MACOSX/apis/._BE-APIv4-030_fees_post_fees_drafts_id_unlock.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT place Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run the Verify commands.
```


## Module: BE-APIv4-031

**Router include checkpoint (module-level, run once per module):**

1) Check whether paths for this module are present:
```bash
PYTHONPATH=backend python -c "from app.main import app; print('\n'.join(sorted({r.path for r in app.routes if hasattr(r,'path')})))" | grep -i -E '/BE-APIv4-031(/|$)' || true
```

2) If nothing is printed, you must include this module router **once** in `backend/app/api/router.py`:
- Import: `from app.modules.<...>.api import router as BE-APIv4-031_router`
- Include: `api_router.include_router(BE-APIv4-031_router, tags=["Be Apiv4 031"])`

After wiring, re-run step (1) until module paths appear.

### TASK_FILE: __MACOSX/apis/._BE-APIv4-031_fees_post_fees_drafts_id_items.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT place Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run the Verify commands.
```


## Module: BE-APIv4-032

**Router include checkpoint (module-level, run once per module):**

1) Check whether paths for this module are present:
```bash
PYTHONPATH=backend python -c "from app.main import app; print('\n'.join(sorted({r.path for r in app.routes if hasattr(r,'path')})))" | grep -i -E '/BE-APIv4-032(/|$)' || true
```

2) If nothing is printed, you must include this module router **once** in `backend/app/api/router.py`:
- Import: `from app.modules.<...>.api import router as BE-APIv4-032_router`
- Include: `api_router.include_router(BE-APIv4-032_router, tags=["Be Apiv4 032"])`

After wiring, re-run step (1) until module paths appear.

### TASK_FILE: __MACOSX/apis/._BE-APIv4-032_fees_put_fees_items_item_id.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT place Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run the Verify commands.
```


## Module: BE-APIv4-033

**Router include checkpoint (module-level, run once per module):**

1) Check whether paths for this module are present:
```bash
PYTHONPATH=backend python -c "from app.main import app; print('\n'.join(sorted({r.path for r in app.routes if hasattr(r,'path')})))" | grep -i -E '/BE-APIv4-033(/|$)' || true
```

2) If nothing is printed, you must include this module router **once** in `backend/app/api/router.py`:
- Import: `from app.modules.<...>.api import router as BE-APIv4-033_router`
- Include: `api_router.include_router(BE-APIv4-033_router, tags=["Be Apiv4 033"])`

After wiring, re-run step (1) until module paths appear.

### TASK_FILE: __MACOSX/apis/._BE-APIv4-033_fees_delete_fees_items_item_id.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT place Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run the Verify commands.
```


## Module: BE-APIv4-034

**Router include checkpoint (module-level, run once per module):**

1) Check whether paths for this module are present:
```bash
PYTHONPATH=backend python -c "from app.main import app; print('\n'.join(sorted({r.path for r in app.routes if hasattr(r,'path')})))" | grep -i -E '/BE-APIv4-034(/|$)' || true
```

2) If nothing is printed, you must include this module router **once** in `backend/app/api/router.py`:
- Import: `from app.modules.<...>.api import router as BE-APIv4-034_router`
- Include: `api_router.include_router(BE-APIv4-034_router, tags=["Be Apiv4 034"])`

After wiring, re-run step (1) until module paths appear.

### TASK_FILE: __MACOSX/apis/._BE-APIv4-034_fees_get_fees_rates.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT place Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run the Verify commands.
```


## Module: BE-APIv4-035

**Router include checkpoint (module-level, run once per module):**

1) Check whether paths for this module are present:
```bash
PYTHONPATH=backend python -c "from app.main import app; print('\n'.join(sorted({r.path for r in app.routes if hasattr(r,'path')})))" | grep -i -E '/BE-APIv4-035(/|$)' || true
```

2) If nothing is printed, you must include this module router **once** in `backend/app/api/router.py`:
- Import: `from app.modules.<...>.api import router as BE-APIv4-035_router`
- Include: `api_router.include_router(BE-APIv4-035_router, tags=["Be Apiv4 035"])`

After wiring, re-run step (1) until module paths appear.

### TASK_FILE: __MACOSX/apis/._BE-APIv4-035_fees_post_fees_rates.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT place Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run the Verify commands.
```


## Module: BE-APIv4-036

**Router include checkpoint (module-level, run once per module):**

1) Check whether paths for this module are present:
```bash
PYTHONPATH=backend python -c "from app.main import app; print('\n'.join(sorted({r.path for r in app.routes if hasattr(r,'path')})))" | grep -i -E '/BE-APIv4-036(/|$)' || true
```

2) If nothing is printed, you must include this module router **once** in `backend/app/api/router.py`:
- Import: `from app.modules.<...>.api import router as BE-APIv4-036_router`
- Include: `api_router.include_router(BE-APIv4-036_router, tags=["Be Apiv4 036"])`

After wiring, re-run step (1) until module paths appear.

### TASK_FILE: __MACOSX/apis/._BE-APIv4-036_fees_put_fees_rates_id.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT place Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run the Verify commands.
```


## Module: BE-APIv4-037

**Router include checkpoint (module-level, run once per module):**

1) Check whether paths for this module are present:
```bash
PYTHONPATH=backend python -c "from app.main import app; print('\n'.join(sorted({r.path for r in app.routes if hasattr(r,'path')})))" | grep -i -E '/BE-APIv4-037(/|$)' || true
```

2) If nothing is printed, you must include this module router **once** in `backend/app/api/router.py`:
- Import: `from app.modules.<...>.api import router as BE-APIv4-037_router`
- Include: `api_router.include_router(BE-APIv4-037_router, tags=["Be Apiv4 037"])`

After wiring, re-run step (1) until module paths appear.

### TASK_FILE: __MACOSX/apis/._BE-APIv4-037_billing_get_bills.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT place Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run the Verify commands.
```


## Module: billing

**Router include checkpoint (module-level, run once per module):**

1) Check whether paths for this module are present:
```bash
PYTHONPATH=backend python -c "from app.main import app; print('\n'.join(sorted({r.path for r in app.routes if hasattr(r,'path')})))" | grep -i -E '/billing(/|$)' || true
```

2) If nothing is printed, you must include this module router **once** in `backend/app/api/router.py`:
- Import: `from app.modules.<...>.api import router as billing_router`
- Include: `api_router.include_router(billing_router, tags=["Billing"])`

After wiring, re-run step (1) until module paths appear.

### TASK_FILE: apis/BE-APIv4-037_billing_get_bills.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT place Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run the Verify commands.
```

### TASK_FILE: apis/BE-APIv4-038_billing_post_bills_from-drafts.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT place Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run the Verify commands.
```

### TASK_FILE: apis/BE-APIv4-039_billing_post_bills_manual.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT place Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run the Verify commands.
```

### TASK_FILE: apis/BE-APIv4-040_billing_get_bills_id.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT place Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run the Verify commands.
```

### TASK_FILE: apis/BE-APIv4-041_billing_get_bills_id_print.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT place Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run the Verify commands.
```

### TASK_FILE: apis/BE-APIv4-042_billing_get_payments.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT place Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run the Verify commands.
```

### TASK_FILE: apis/BE-APIv4-043_billing_post_payments.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT place Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run the Verify commands.
```

### TASK_FILE: apis/BE-APIv4-044_billing_get_payments_id.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT place Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run the Verify commands.
```

### TASK_FILE: apis/BE-APIv4-045_billing_post_offsets.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT place Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run the Verify commands.
```

### TASK_FILE: apis/BE-APIv4-046_billing_post_offsets_id_reverse.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT place Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run the Verify commands.
```

### TASK_FILE: apis/BE-APIv4-047_billing_get_cases_case_id_receipts.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT place Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run the Verify commands.
```


## Module: BE-APIv4-038

**Router include checkpoint (module-level, run once per module):**

1) Check whether paths for this module are present:
```bash
PYTHONPATH=backend python -c "from app.main import app; print('\n'.join(sorted({r.path for r in app.routes if hasattr(r,'path')})))" | grep -i -E '/BE-APIv4-038(/|$)' || true
```

2) If nothing is printed, you must include this module router **once** in `backend/app/api/router.py`:
- Import: `from app.modules.<...>.api import router as BE-APIv4-038_router`
- Include: `api_router.include_router(BE-APIv4-038_router, tags=["Be Apiv4 038"])`

After wiring, re-run step (1) until module paths appear.

### TASK_FILE: __MACOSX/apis/._BE-APIv4-038_billing_post_bills_from-drafts.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT place Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run the Verify commands.
```


## Module: BE-APIv4-039

**Router include checkpoint (module-level, run once per module):**

1) Check whether paths for this module are present:
```bash
PYTHONPATH=backend python -c "from app.main import app; print('\n'.join(sorted({r.path for r in app.routes if hasattr(r,'path')})))" | grep -i -E '/BE-APIv4-039(/|$)' || true
```

2) If nothing is printed, you must include this module router **once** in `backend/app/api/router.py`:
- Import: `from app.modules.<...>.api import router as BE-APIv4-039_router`
- Include: `api_router.include_router(BE-APIv4-039_router, tags=["Be Apiv4 039"])`

After wiring, re-run step (1) until module paths appear.

### TASK_FILE: __MACOSX/apis/._BE-APIv4-039_billing_post_bills_manual.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT place Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run the Verify commands.
```


## Module: BE-APIv4-040

**Router include checkpoint (module-level, run once per module):**

1) Check whether paths for this module are present:
```bash
PYTHONPATH=backend python -c "from app.main import app; print('\n'.join(sorted({r.path for r in app.routes if hasattr(r,'path')})))" | grep -i -E '/BE-APIv4-040(/|$)' || true
```

2) If nothing is printed, you must include this module router **once** in `backend/app/api/router.py`:
- Import: `from app.modules.<...>.api import router as BE-APIv4-040_router`
- Include: `api_router.include_router(BE-APIv4-040_router, tags=["Be Apiv4 040"])`

After wiring, re-run step (1) until module paths appear.

### TASK_FILE: __MACOSX/apis/._BE-APIv4-040_billing_get_bills_id.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT place Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run the Verify commands.
```


## Module: BE-APIv4-041

**Router include checkpoint (module-level, run once per module):**

1) Check whether paths for this module are present:
```bash
PYTHONPATH=backend python -c "from app.main import app; print('\n'.join(sorted({r.path for r in app.routes if hasattr(r,'path')})))" | grep -i -E '/BE-APIv4-041(/|$)' || true
```

2) If nothing is printed, you must include this module router **once** in `backend/app/api/router.py`:
- Import: `from app.modules.<...>.api import router as BE-APIv4-041_router`
- Include: `api_router.include_router(BE-APIv4-041_router, tags=["Be Apiv4 041"])`

After wiring, re-run step (1) until module paths appear.

### TASK_FILE: __MACOSX/apis/._BE-APIv4-041_billing_get_bills_id_print.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT place Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run the Verify commands.
```


## Module: BE-APIv4-042

**Router include checkpoint (module-level, run once per module):**

1) Check whether paths for this module are present:
```bash
PYTHONPATH=backend python -c "from app.main import app; print('\n'.join(sorted({r.path for r in app.routes if hasattr(r,'path')})))" | grep -i -E '/BE-APIv4-042(/|$)' || true
```

2) If nothing is printed, you must include this module router **once** in `backend/app/api/router.py`:
- Import: `from app.modules.<...>.api import router as BE-APIv4-042_router`
- Include: `api_router.include_router(BE-APIv4-042_router, tags=["Be Apiv4 042"])`

After wiring, re-run step (1) until module paths appear.

### TASK_FILE: __MACOSX/apis/._BE-APIv4-042_billing_get_payments.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT place Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run the Verify commands.
```


## Module: BE-APIv4-043

**Router include checkpoint (module-level, run once per module):**

1) Check whether paths for this module are present:
```bash
PYTHONPATH=backend python -c "from app.main import app; print('\n'.join(sorted({r.path for r in app.routes if hasattr(r,'path')})))" | grep -i -E '/BE-APIv4-043(/|$)' || true
```

2) If nothing is printed, you must include this module router **once** in `backend/app/api/router.py`:
- Import: `from app.modules.<...>.api import router as BE-APIv4-043_router`
- Include: `api_router.include_router(BE-APIv4-043_router, tags=["Be Apiv4 043"])`

After wiring, re-run step (1) until module paths appear.

### TASK_FILE: __MACOSX/apis/._BE-APIv4-043_billing_post_payments.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT place Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run the Verify commands.
```


## Module: BE-APIv4-044

**Router include checkpoint (module-level, run once per module):**

1) Check whether paths for this module are present:
```bash
PYTHONPATH=backend python -c "from app.main import app; print('\n'.join(sorted({r.path for r in app.routes if hasattr(r,'path')})))" | grep -i -E '/BE-APIv4-044(/|$)' || true
```

2) If nothing is printed, you must include this module router **once** in `backend/app/api/router.py`:
- Import: `from app.modules.<...>.api import router as BE-APIv4-044_router`
- Include: `api_router.include_router(BE-APIv4-044_router, tags=["Be Apiv4 044"])`

After wiring, re-run step (1) until module paths appear.

### TASK_FILE: __MACOSX/apis/._BE-APIv4-044_billing_get_payments_id.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT place Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run the Verify commands.
```


## Module: BE-APIv4-045

**Router include checkpoint (module-level, run once per module):**

1) Check whether paths for this module are present:
```bash
PYTHONPATH=backend python -c "from app.main import app; print('\n'.join(sorted({r.path for r in app.routes if hasattr(r,'path')})))" | grep -i -E '/BE-APIv4-045(/|$)' || true
```

2) If nothing is printed, you must include this module router **once** in `backend/app/api/router.py`:
- Import: `from app.modules.<...>.api import router as BE-APIv4-045_router`
- Include: `api_router.include_router(BE-APIv4-045_router, tags=["Be Apiv4 045"])`

After wiring, re-run step (1) until module paths appear.

### TASK_FILE: __MACOSX/apis/._BE-APIv4-045_billing_post_offsets.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT place Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run the Verify commands.
```


## Module: BE-APIv4-046

**Router include checkpoint (module-level, run once per module):**

1) Check whether paths for this module are present:
```bash
PYTHONPATH=backend python -c "from app.main import app; print('\n'.join(sorted({r.path for r in app.routes if hasattr(r,'path')})))" | grep -i -E '/BE-APIv4-046(/|$)' || true
```

2) If nothing is printed, you must include this module router **once** in `backend/app/api/router.py`:
- Import: `from app.modules.<...>.api import router as BE-APIv4-046_router`
- Include: `api_router.include_router(BE-APIv4-046_router, tags=["Be Apiv4 046"])`

After wiring, re-run step (1) until module paths appear.

### TASK_FILE: __MACOSX/apis/._BE-APIv4-046_billing_post_offsets_id_reverse.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT place Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run the Verify commands.
```


## Module: BE-APIv4-047

**Router include checkpoint (module-level, run once per module):**

1) Check whether paths for this module are present:
```bash
PYTHONPATH=backend python -c "from app.main import app; print('\n'.join(sorted({r.path for r in app.routes if hasattr(r,'path')})))" | grep -i -E '/BE-APIv4-047(/|$)' || true
```

2) If nothing is printed, you must include this module router **once** in `backend/app/api/router.py`:
- Import: `from app.modules.<...>.api import router as BE-APIv4-047_router`
- Include: `api_router.include_router(BE-APIv4-047_router, tags=["Be Apiv4 047"])`

After wiring, re-run step (1) until module paths appear.

### TASK_FILE: __MACOSX/apis/._BE-APIv4-047_billing_get_cases_case_id_receipts.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT place Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run the Verify commands.
```


## Module: README.md

**Router include checkpoint (module-level, run once per module):**

1) Check whether paths for this module are present:
```bash
PYTHONPATH=backend python -c "from app.main import app; print('\n'.join(sorted({r.path for r in app.routes if hasattr(r,'path')})))" | grep -i -E '/README.md(/|$)' || true
```

2) If nothing is printed, you must include this module router **once** in `backend/app/api/router.py`:
- Import: `from app.modules.<...>.api import router as README.md_router`
- Include: `api_router.include_router(README.md_router, tags=["Readme.Md"])`

After wiring, re-run step (1) until module paths appear.

### TASK_FILE: __MACOSX/apis/._README.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT place Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run the Verify commands.
```


## Module: misc

**Router include checkpoint (module-level, run once per module):**

1) Check whether paths for this module are present:
```bash
PYTHONPATH=backend python -c "from app.main import app; print('\n'.join(sorted({r.path for r in app.routes if hasattr(r,'path')})))" | grep -i -E '/misc(/|$)' || true
```

2) If nothing is printed, you must include this module router **once** in `backend/app/api/router.py`:
- Import: `from app.modules.<...>.api import router as misc_router`
- Include: `api_router.include_router(misc_router, tags=["Misc"])`

After wiring, re-run step (1) until module paths appear.

### TASK_FILE: apis/README.md
```text
Open TASK_FILE and implement EXACTLY ONE endpoint per the task.

Hard requirements:
- No schema changes; ORM models only.
- Lint-safe permission enforcement:
    _perm: None = Depends(require_perm("<FROM_TASK>"))
  (Do NOT place Depends(require_perm(...)) in decorator dependencies.)
- Keep imports minimal and ordered; avoid unused imports.
- Do NOT invent new response envelopes; follow existing project patterns.

After implementation, run the Verify commands.
```



## Verify (run after each task)
```bash
ruff check --fix .
ruff format .
ruff check .
PYTHONPATH=backend python -c "from app.main import app; print('OK: app import')"
```

**Optional sanity (recommended after the FIRST task of each module):**
```bash
PYTHONPATH=backend python -c "from app.main import app; print('\n'.join(sorted({r.path for r in app.routes if hasattr(r,'path')})))" | head -n 120
curl -s http://localhost:8000/openapi.json | grep -i -n "<MODULE_KEYWORD>" | head
```
