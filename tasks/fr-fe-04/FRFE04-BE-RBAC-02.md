# FRFE04-BE-RBAC-02 — Register `PayList.Export` permission

- Source spec: `docs/superpowers/specs/2026-03-23-fee-paylist-govpayment-design.md`
- Type: `backend shared ownership / permission contract`
- Status: `Executable`

## Closure Slice

- Exact closure slice: register `PayList.Export` across the RBAC runtime seed surface and authoritative RBAC contract docs so pay-list export endpoints can use `Title.Action`-correct export gating with synchronized documentation.
- Explicit non-closure: does not implement export endpoint behavior, workbook generation, state mutation rules, or frontend menu wiring.
- Remaining follow-up task ids: `FRFE04-BE-04`

## Allowlist

- `backend/app/modules/rbac/service.py`
- `docs/README.md`
- `docs/02_permissions_rbac.md`
- `docs/permissions_matrix.md`

## Verification

- `cd backend && ruff check --fix app/modules/rbac/service.py`
- `cd backend && ruff format app/modules/rbac/service.py`
- `cd backend && ruff check app/modules/rbac/service.py`
- `cd backend && python3 - <<'PY'\nimport ast\nfrom pathlib import Path\nfrom sqlalchemy import create_engine, select\nfrom sqlalchemy.orm import Session\nfrom app.db.base import Base\nfrom app.modules.auth.models import T_Role, T_RolePerm\nfrom app.modules.rbac.service import seed_default_roles_perms\n\nservice_text = Path('app/modules/rbac/service.py').read_text()\nmodule = ast.parse(service_text)\nrole_permissions = None\nfor node in module.body:\n    if isinstance(node, ast.Assign):\n        for target in node.targets:\n            if isinstance(target, ast.Name) and target.id == 'ROLE_PERMISSIONS':\n                role_permissions = ast.literal_eval(node.value)\n                break\n    if role_permissions is not None:\n        break\nassert role_permissions is not None\nassert 'PayList.Export' in role_permissions['Admin']\nassert 'PayList.Export' in role_permissions['Finance']\nassert 'PayList.Export' not in role_permissions['Formalities']\nassert 'PayList.Export' not in role_permissions['Agent']\nrbac_doc = Path('../docs/02_permissions_rbac.md').read_text()\nassert 'PayList.Export' in rbac_doc\nassert '_perm: None = Depends(require_perm(\"Title.Action\"))' in rbac_doc\nreadme_text = Path('../docs/README.md').read_text()\nassert 'including export routes' in readme_text and 'backend/app/modules/rbac/service.py' in readme_text\nmatrix_text = Path('../docs/permissions_matrix.md').read_text()\nassert 'POST /pay-lists/{id}/export' in matrix_text and 'PayList.Export' in matrix_text\nengine = create_engine('sqlite:///:memory:')\nBase.metadata.create_all(engine)\nwith Session(engine) as session:\n    seed_default_roles_perms(session)\n    positive_rows = session.execute(\n        select(T_Role.code, T_RolePerm.perm_code)\n        .join(T_RolePerm, T_Role.id == T_RolePerm.role_id)\n        .where(T_Role.code.in_(['Admin', 'Finance']), T_RolePerm.perm_code == 'PayList.Export')\n    ).all()\n    assert {row[0] for row in positive_rows} == {'Admin', 'Finance'}\n    negative_rows = session.execute(\n        select(T_Role.code)\n        .join(T_RolePerm, T_Role.id == T_RolePerm.role_id)\n        .where(T_Role.code.in_(['Formalities', 'Agent']), T_RolePerm.perm_code == 'PayList.Export')\n    ).all()\n    assert negative_rows == []\nPY`
- `./scripts/task_validate.sh FRFE04-BE-RBAC-02`

## Evidence

- `artifacts/FRFE04-BE-RBAC-02/results.jsonl`
- `artifacts/FRFE04-BE-RBAC-02/summary.md`
- `artifacts/FRFE04-BE-RBAC-02/git/diff.patch`
