# A2 Batch — Findings

## Initial Findings
- Old models in `backend/app/models/client_address.py` and `client_contact.py` use Integer PKs
- `app/models/__init__.py` imports from old model files — must update
- No imports of old models found elsewhere in codebase
- Existing `ClientAddressOut` / `ClientContactOut` in schemas use `id: int` and old field names
- Migration chain: latest is `a1_task_template_01` (chains from `53f7a0c139cc`)
