# ENH-00-07 — Fix seed_dev.py import path (ModuleNotFoundError: app)

## Context / Why
Running the development seed script fails with:

ModuleNotFoundError: No module named 'app'

This happens because `backend/scripts/seed_dev.py` is executed directly via:

python3 scripts/seed_dev.py

which does NOT automatically add `backend/` to `sys.path`, while the script imports modules using absolute imports such as:

from app.core.security import get_password_hash

This task fixes the execution environment for `seed_dev.py` WITHOUT changing business logic or import style.

## Target (Atomic – FIXED)
Make `backend/scripts/seed_dev.py` runnable via:

cd backend
python3 scripts/seed_dev.py

without ModuleNotFoundError.

## Allowed files (Strict allowlist)
- backend/scripts/seed_dev.py ONLY

## Non-scope (explicitly excluded)
- Do NOT change any imports in other files
- Do NOT modify app/core/security.py
- Do NOT refactor authentication or RBAC logic
- Do NOT modify migrations or database schema

## Required change (EXACT)
At the very top of backend/scripts/seed_dev.py, before any app.* imports:

1) Programmatically add the project root (backend/) to sys.path.

Example pattern (behavioral requirement):

```python
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
```

2) Keep all existing imports and logic unchanged after this fix.

## Acceptance checklist
- [ ] Only backend/scripts/seed_dev.py changed
- [ ] python3 scripts/seed_dev.py runs without ModuleNotFoundError
- [ ] Script still imports app.* correctly
- [ ] Ruff + py_compile pass
- [ ] No behavioral change to seeding logic

## Evidence (mandatory)
- git diff showing only seed_dev.py change
- Command output:
  cd backend
  python3 scripts/seed_dev.py
- EOS evidence logs

## Validation commands
```bash
cd backend
ruff check scripts/seed_dev.py
ruff format scripts/seed_dev.py
python3 -m py_compile scripts/seed_dev.py
```

---

## Codex / Agent Execution Prompt (AI-EOS v2)

You are a coding agent executing exactly ONE atomic task.

### Task File (Authoritative)
tasks/backend/mvp1enhance/ENH-00-07_fix_seed_dev_import_path.md

### Hard Rules
- Modify ONLY backend/scripts/seed_dev.py
- Do NOT change any other files
- Do NOT refactor logic
- STOP immediately if any other file change seems required

### Goal
Fix the import path so that seed_dev.py can import app.* modules when executed directly.

### STOP Contract
STOP if:
- The fix would require modifying any file other than seed_dev.py
- Any ambiguity exists beyond adjusting sys.path
