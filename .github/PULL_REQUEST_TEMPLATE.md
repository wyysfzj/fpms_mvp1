# PR: <TaskID> — <Short Title>

## Task file
- Link: `tasks/<backend|frontend>/<TaskID>.md`

## Summary
- What was implemented:
- Why:

## Acceptance checklist (copy from task file)
- [ ] Only target file was changed/created.
- [ ] Prompt requirements implemented exactly.
- [ ] ...

## Validation commands (paste outputs or confirm run)
### Backend (if applicable)
```bash
cd backend
ruff check .
pytest -q
python -m py_compile <file>
```

### Frontend (if applicable)
```bash
cd frontend
npm run build
npm run dev
```

## Notes / Follow-ups
- TODO:
