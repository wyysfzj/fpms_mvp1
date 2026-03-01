# ENH-08-05-01 — CODEX PROMPT (AI‑EOS)

Execute exactly ONE atomic task:
- `ENH-08-05-01.md`

Hard rules:
- Create or modify ONLY: `backend/app/modules/system/service.py`
- Do NOT touch api.py/schemas.py/models/migrations
- Implement exactly the three functions specified:
  - list_system_params
  - upsert_system_param
  - mask_secret_param_value
- Run EOS evidence commands and ensure task_validate passes
- STOP if any other file is required
