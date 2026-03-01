# ENH-09-03-01 — CODEX PROMPT (AI‑EOS)

Execute exactly ONE atomic task:
- `ENH-09-03-01.md`

Hard rules:
- Modify ONLY `backend/app/core/pagination.py`
- Make `PageResult` a generic Pydantic model: `PageResult[T]`
- Do NOT touch documents module or any other files
- Run evidence commands and ensure `task_validate.sh ENH-09-03-01` passes
