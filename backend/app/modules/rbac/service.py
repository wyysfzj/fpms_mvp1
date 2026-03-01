from __future__ import annotations

from uuid import uuid4

from sqlalchemy.orm import Session

from app.modules.auth.models import T_Role, T_UserRole
from app.modules.rbac.models import T_RolePerm

# Permission definitions from docs/02_permissions_rbac.md
ROLE_PERMISSIONS = {
    "Admin": [
        "AdminUser.Create",
        "AdminUser.Edit",
        "AdminUser.Read",
        # Annuity / Collections / Commission / Consulting-Search (post-enhancement)
        "AnnuityTask.Action",
        "AnnuityTask.Read",
        "BadDebt.Action",
        "Bill.Create",
        "Bill.Print",
        "Bill.Read",
        "Billing.Edit",
        "Case.Create",
        "Case.Edit",
        "Case.EditLimited",
        "Case.Export",
        "Case.Read",
        "CaseReceipt.Read",
        "Commission.Read",
        "CommissionReport.Read",
        "CommissionRule.Create",
        "CommissionRule.Edit",
        "CommissionRule.Read",
        "CommissionSettlement.Action",
        "CommissionSettlement.Create",
        "Client.Action",
        "Client.Create",
        "Client.Edit",
        "Client.Read",
        "ConsultingCase.Create",
        "ConsultingFeeDraft.Create",
        "Doc.Attach",
        "Doc.Create",
        "Doc.Edit",
        "Doc.Read",
        "DocTemplate.Create",
        "DocTemplate.Edit",
        "DocTemplate.Read",
        "Dunning.Create",
        "Dunning.Read",
        "Expense.Create",
        "Expense.Read",
        "Fee.Create",
        "Fee.Edit",
        "Fee.Draft.Action",
        "Fee.Draft.Create",
        "Fee.Draft.Edit",
        "Fee.Draft.Read",
        "Fee.Item.Create",
        "Fee.Item.Delete",
        "Fee.Item.Edit",
        "Fee.Lock",
        "Fee.Read",
        "Fee.Rate.Create",
        "Fee.Rate.Edit",
        "Fee.Rate.Read",
        "LetterHead.Create",
        "LetterHead.Read",
        "Payment.Create",
        "Payment.Read",
        "SystemParam.Edit",
        "SystemParam.Read",
        "Task.Action",
        "Task.Create",
        "Task.Edit",
        "Task.Read",
        "TaskTemplate.Create",
        "TaskTemplate.Edit",
        "TaskTemplate.Read",
        "Template.Create",
        "Template.Read",
        "FeeRate.Create",
        "FeeRate.Edit",
        "FeeRate.Read",
        "GovPayment.Create",
        "LetterHead.Edit",
        "Template.Edit",
        "PayList.Create",
    ],
    "Formalities": [
        "Auth.Login",
        "Case.Read",
        "Case.Create",
        "Case.Edit",
        "Doc.Read",
        "Doc.Create",
        "Doc.Edit",
        "Doc.Attach",
        "Doc.TemplateRender",
        "DocTemplate.Read",
        "Task.Read",
        "Task.Create",
        "Task.Edit",
        "Task.Close",
        "Task.Reopen",
        "Task.Assign",
        "Fee.Read",
        "Fee.Draft.Create",
        "Fee.Draft.Edit",
        "Fee.Rate.Manage",
        "Bill.Read",
        "Client.Manage",
    ],
    "Agent": [
        "Auth.Login",
        "Case.Read",
        "Case.EditLimited",
        "Doc.Read",
        "Doc.Create",
        "Doc.Attach",
        "Task.Read",
        "Task.Create",
        "Task.Edit",
        "Task.Close",
        "Task.Reopen",
        "Task.Assign",
        "Fee.Read",
        "Bill.Read",
        "Client.Manage",
    ],
    "Finance": [
        "Auth.Login",
        "Billing.Edit",
        "Case.Read",
        "Doc.Read",
        "Task.Read",
        "Fee.Read",
        "Bill.Read",
        "Bill.CreateFromDraft",
        "Bill.CreateManual",
        "Bill.Print",
        "Payment.Create",
        "Payment.Offset",
        "Client.Manage",
    ],
}


def get_user_permissions(db: Session, user_id: str) -> set[str]:
    """
    Get all permission codes for a user.

    Returns:
        Set of permission code strings (e.g., {"Case.Read", "Bill.Create"})
    """
    user_roles = db.query(T_UserRole).filter(T_UserRole.user_id == user_id).all()

    if not user_roles:
        return set()

    role_ids = [ur.role_id for ur in user_roles]

    role_perms = db.query(T_RolePerm).filter(T_RolePerm.role_id.in_(role_ids)).all()

    return {rp.perm_code for rp in role_perms}


def seed_default_roles_perms(db: Session) -> None:
    """Seed default roles and their permissions. Idempotent."""
    for role_code, perm_codes in ROLE_PERMISSIONS.items():
        role = db.query(T_Role).filter(T_Role.code == role_code).first()
        if not role:
            role = T_Role(
                id=str(uuid4()),
                code=role_code,
                name=role_code,
            )
            db.add(role)
            db.flush()

        existing = db.query(T_RolePerm).filter(T_RolePerm.role_id == role.id).all()
        existing_codes = {ep.perm_code for ep in existing}

        # Deduplicate list entries defensively to avoid duplicate role-perm inserts.
        for perm_code in dict.fromkeys(perm_codes):
            if perm_code not in existing_codes:
                rp = T_RolePerm(
                    id=str(uuid4()),
                    role_id=role.id,
                    perm_code=perm_code,
                )
                db.add(rp)
                existing_codes.add(perm_code)

    db.commit()
