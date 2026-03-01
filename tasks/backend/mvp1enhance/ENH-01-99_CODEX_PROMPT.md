# ENH-01-99 — CODEX PROMPT (Run This)

You are executing **one and only one** atomic task file: `tasks/backend/mvp1enhance/ENH-01-99.md`.

Follow the task EXACTLY. Do not expand scope.

Key requirements:
- Create `backend/scripts/scan_perms.py` which prints:
  - ALL_CODES
  - ADMIN_MISSING
  - ROLE_MISSING (report only)
- Patch Admin list in ROLE_PERMISSIONS to include ALL_CODES
- Do NOT modify other roles

MUST run EOS evidence scripts listed in the task and ensure `task_validate.sh ENH-01-99` passes.
