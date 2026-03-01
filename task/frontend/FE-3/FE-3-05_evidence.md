# FE-3-05 Evidence Log

## Task
- ID: FE-3-05
- Title: Polish: Unify 422 form validation mapping helper + apply to key forms

## File Allowlist Respected
- ✅ Yes
- Files changed:
  - `frontend/src/utils/validation.ts` (new)
  - `frontend/src/modules/clients/pages/ClientForm.vue`
  - `frontend/src/modules/cases/pages/CaseCreate.vue`
  - `frontend/src/modules/cases/pages/CaseEdit.vue`
  - `frontend/src/modules/tasks/pages/TaskCreate.vue`
  - `task/frontend/FE-3/FE-3-05_evidence.md` (new)

## Commands Executed
```bash
# Quality gates
cd frontend && npm run lint
cd frontend && npm run typecheck
cd frontend && npm run build

# UI smoke (client/case create/task create)
cd backend && uvicorn app.main:app --host 127.0.0.1 --port 8000
cd frontend && npm run dev
cd frontend && NODE_PATH=./node_modules node /tmp/fe3_05_ui_smoke.js > /tmp/fe3_05_ui_smoke_results.json

# UI smoke (case edit)
cd backend && uvicorn app.main:app --host 127.0.0.1 --port 8000
cd frontend && npm run dev
cd frontend && NODE_PATH=./node_modules node /tmp/fe3_05_case_edit_smoke.js > /tmp/fe3_05_case_edit_results.json
```

## Outputs (Key Lines)
- `npm run lint`: ✅ passed (`eslint . --max-warnings 0`)
- `npm run typecheck`: ✅ passed (`vue-tsc --noEmit`)
- `npm run build`: ✅ passed (`vite build` complete)
- Smoke output files:
  - `/tmp/fe3_05_ui_smoke_results.json`
  - `/tmp/fe3_05_case_edit_results.json`

## Manual Verification Steps + Results

### Updated forms under test
1. Client create/edit form (`ClientForm.vue`)
2. Case create form (`CaseCreate.vue`)
3. Case edit form (`CaseEdit.vue`)
4. Task create form (`TaskCreate.vue`)

### Step 1: Submit invalid payload to trigger 422
- Client create (`/clients/new`): forced `POST /api/v1/clients -> 422` with dict details.
- Case create (`/cases/new`): forced `POST /api/v1/cases -> 422` with `details.errors` list shape.
- Case edit (`/cases/1/edit`): forced `PUT /api/v1/cases/1 -> 422` with `details.errors` list shape.
- Task create (`/tasks/new`): forced `POST /api/v1/tasks -> 422` with dict details.
- Result: ✅ 422 triggered in each form.

### Step 2: Verify field-level errors render near fields
- Client create: `name`, `email` messages rendered.
- Case create: `case_no`, `client_id` messages rendered.
- Case edit: `title`, `status` messages rendered.
- Task create: `title`, `case_id` messages rendered.
- Result: ✅ passed on all updated forms.

### Step 3: Verify requestId visibility on banner/toast when present
- Added `x-request-id` to each forced 422 response.
- Verified `ApiErrorBanner` displays `Request ID:` line for all tested forms.
- RequestId samples:
  - `fe3-05-client-422-rid`
  - `fe3-05-case-422-rid`
  - `fe3-05-case-edit-422-rid`
  - `fe3-05-task-422-rid`
- Result: ✅ passed.

### Step 4: Verify successful submit still works
- Client create: forced `POST /clients -> 201`, redirect to `/clients`.
- Case create: forced `POST /cases -> 201`, redirect to `/cases`.
- Case edit: forced `PUT /cases/1 -> 200`, redirect to `/cases/1`.
- Task create: forced `POST /tasks -> 201`, redirect to `/tasks`.
- Result: ✅ passed.

## Smoke Summary
From `/tmp/fe3_05_ui_smoke_results.json`:
- `client_create.422_field_mapping_dict_shape`: success=true
- `client_create.success_submit`: success=true
- `case_create.422_field_mapping_errors_list_shape`: success=true
- `case_create.success_submit`: success=true
- `task_create.422_field_mapping_dict_shape`: success=true
- `task_create.success_submit`: success=true

From `/tmp/fe3_05_case_edit_results.json`:
- `case_edit.422_field_mapping_errors_list_shape`: success=true
- `case_edit.success_submit`: success=true

## Key API Statuses Observed
- Auth/login: `200`
- Validation failures: `422`
- Successful creates: `201`
- Successful update: `200`

## Mismatches / Handling
- No scope-breaking mismatch encountered.
- No STOP condition triggered.
