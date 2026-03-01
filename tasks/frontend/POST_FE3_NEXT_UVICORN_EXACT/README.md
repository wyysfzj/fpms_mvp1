# Post‑FE3 Next Tasks — Uvicorn Exact Command Edition

Backend start command is confirmed:

```bash
uvicorn app.main:app --reload
```

These prompts assume the backend code lives under a `backend/` directory and the FastAPI package is `backend/app/`.
So you should start backend from repo root like:

```bash
cd backend
uvicorn app.main:app --reload
```

Base URL:
- `http://localhost:8000/api/v1`

Connectivity probe (expected 401, not 000):
```bash
curl -i "http://localhost:8000/api/v1/clients?page=1&page_size=1"
```

## Tasks Included
1) NEXT‑1: Fix Documents attachments upload 500 (Backend) + ensure `X-Request-ID` and error envelope.
2) NEXT‑2: Configure printing to unblock `/bills/{id}/print` (409 -> 200) via idempotent setup script + docs.
3) NEXT‑3: Close Offsets flow by obtaining valid `payment_line_id` (prefer existing endpoints; otherwise minimal BE exposure) + minimal FE wiring.

## Evidence
Each task must create:
- `task/frontend/POST_FE3_NEXT/<task_id>_evidence.md`

Use the included template.

## UI Constraints (if frontend changes are required)
- Keep `src/styles/variables.css` tokens block unchanged (must match `fpms.css`).
- No inline styles / magic numbers.
- Follow `reference/case_detail.html` layout/immersive behavior.
