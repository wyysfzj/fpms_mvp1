from __future__ import annotations

GRANT_FEE_TASK_PERMISSION_CODES = ("GrantFeeTask.Read", "GrantFeeTask.Write")


def get_grant_fee_module_contract() -> dict[str, object]:
    return {
        "module": "grant_fees",
        "permission_namespace": "GrantFeeTask",
        "permission_codes": list(GRANT_FEE_TASK_PERMISSION_CODES),
        "status": "ok",
    }
