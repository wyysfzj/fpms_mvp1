# ENH-01-16-01 — Ensure admin user is bound to Admin role (idempotent)

## Context / Why
Admin user exists in `t_user` but has no role binding in `t_user_role`,
causing all `require_perm(...)` checks to return FORBIDDEN (403).

This task fixes `seed_dev.py` so that:
- Admin role exists
- Admin user exists
- Admin user is ALWAYS bound to Admin role (idempotent)

## Target (Atomic – FIXED)
Running `python3 scripts/seed_dev.py` guarantees admin ↔ Admin role binding.

## Allowed files (Strict allowlist)
- backend/scripts/seed_dev.py ONLY

## Non-scope
- Do NOT modify models
- Do NOT modify RBAC logic
- Do NOT modify migrations
- Do NOT modify any other scripts

## Required change (EXACT)
After locating or creating:
- Admin role (code = "Admin")
- Admin user (username = "admin")

Add logic:
1. Query `t_user_role` for (admin_user_id, admin_role_id)
2. If missing, INSERT the binding
3. Commit
4. Ensure idempotency (no duplicate rows)

## Acceptance checklist
- [ ] Only seed_dev.py changed
- [ ] Running seed_dev.py succeeds
- [ ] SQL proof shows admin bound to Admin role
- [ ] Running seed twice does not create duplicates

## Validation
```bash
cd backend
python3 scripts/seed_dev.py

sqlite3 fpms_dev.db "
select u.username, r.code
from t_user u
join t_user_role ur on ur.user_id=u.id
join t_role r on r.id=ur.role_id
where u.username='admin';
"
```

---

## Codex / Agent Prompt (AI‑EOS)

Execute exactly one atomic task:
tasks/backend/mvp1enhance/ENH-01-16-01_fix_admin_user_role_binding.md

Rules:
- Modify ONLY backend/scripts/seed_dev.py
- STOP if any other file is required
