# Evidence Log Template — Post FE‑3 Next (Uvicorn exact)

## Task
- ID:
- Title:
- Date:
- Agent:

## Backend (Uvicorn)
- Command:
```bash
cd backend
uvicorn app.main:app --reload
```
- Uvicorn key log lines:
- Probe:
```bash
curl -i "http://localhost:8000/api/v1/clients?page=1&page_size=1"
```
- Probe status:

## File Allowlist Respected
- ✅ Yes / ❌ No (explain)

## Commands Run
```bash
# Backend (if applicable)
python -m compileall backend/app
pytest -q   # only if repo has pytest configured

# Frontend (if applicable)
cd frontend
npm run lint
npm run typecheck
npm run build
```

## Key Outputs
- backend compile/tests:
- lint:
- typecheck:
- build:

## Reproduction / Verification
### Before
- Steps:
- Result:

### After
- Steps:
- Result:

## API Evidence
- Requests (method + URL + key payload fields):
- Status codes:
- X-Request-ID samples:

## Notes
