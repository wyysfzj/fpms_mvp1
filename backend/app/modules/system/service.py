from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.letter_head import LetterHead
from app.models.system_param import SystemParam
from app.modules.commission.models import CommissionRule
from app.modules.documents.models import DocTemplate
from app.modules.fees.models import FeeRate
from app.modules.masterdata.countries.models import Country
from app.modules.masterdata.departments.models import Department
from app.modules.system.schemas import SystemParamUpsertIn
from app.modules.tasks.models import TaskTemplate
from app.modules.templates.models import Template

CONFIG_READINESS_COUNTS = (
    ("system_param", "系统参数", SystemParam),
    ("fee_rate", "费率", FeeRate),
    ("commission_rule", "提成规则", CommissionRule),
    ("template", "模板文件源", Template),
    ("letter_head", "信头", LetterHead),
    ("country", "国家地区", Country),
    ("department", "部门", Department),
    ("doc_template", "文件模板", DocTemplate),
    ("task_template", "任务模板", TaskTemplate),
)


def list_system_params(db: Session) -> list[SystemParam]:
    stmt = select(SystemParam).order_by(SystemParam.param_key.asc())
    return db.execute(stmt).scalars().all()


def get_system_param(db: Session, key: str) -> SystemParam | None:
    return db.execute(select(SystemParam).where(SystemParam.param_key == key)).scalar_one_or_none()


def upsert_system_param(
    db: Session,
    *,
    param_key: str,
    data: SystemParamUpsertIn,
    actor_id: str | None,
) -> SystemParam:
    param = db.execute(
        select(SystemParam).where(SystemParam.param_key == param_key)
    ).scalar_one_or_none()
    if not param:
        param = SystemParam(
            param_key=param_key,
            param_value=str(data.param_value),
            value_type=data.value_type or "string",
            description=data.description,
            is_secret=bool(data.is_secret) if data.is_secret is not None else False,
        )
        db.add(param)
    else:
        param.param_value = str(data.param_value)
        if data.value_type is not None:
            param.value_type = data.value_type
        if data.description is not None:
            param.description = data.description
        if data.is_secret is not None:
            param.is_secret = data.is_secret

    db.commit()
    db.refresh(param)
    return param


def mask_secret_param_value(param: SystemParam) -> str:
    if param.is_secret:
        return "******"
    return param.param_value


def build_config_readiness(db: Session) -> dict[str, Any]:
    counts = [
        {"key": key, "label": label, "count": _table_count(db, model)}
        for key, label, model in CONFIG_READINESS_COUNTS
    ]
    missing = _config_readiness_missing(db)
    return {
        "status": "BLOCKED" if missing else "READY",
        "hard_blocked": bool(missing),
        "checked_at": datetime.utcnow(),
        "counts": counts,
        "missing": missing,
    }


def _table_count(db: Session, model: type[Any]) -> int:
    return int(db.execute(select(func.count()).select_from(model)).scalar_one())


def _config_readiness_missing(db: Session) -> list[dict[str, str]]:
    checks = [
        (
            "system_param.default_currency",
            "默认币种",
            "t_system_param",
            _system_param_exists(db, "default_currency"),
            "缺少 default_currency，费用、客户或账单默认币种无法确认。",
        ),
        (
            "system_param.bill_template_path",
            "账单打印模板路径",
            "t_system_param",
            _system_param_exists(db, "bill_template_path"),
            "缺少 bill_template_path，账单打印应阻断而不是进入 500。",
        ),
        (
            "fee_rate.apply",
            "申请费费率",
            "t_fee_rate",
            _enabled_count(db, FeeRate, FeeRate.rate_group == "APPLY") > 0,
            "缺少 APPLY 费率，申请费草单无法按配置生成。",
        ),
        (
            "commission_rule.enabled",
            "启用提成规则",
            "t_commission_rule",
            _enabled_count(db, CommissionRule) > 0,
            "缺少启用提成规则，服务费无法生成提成。",
        ),
        (
            "template.enabled",
            "启用模板文件源",
            "t_template",
            _enabled_count(db, Template) > 0,
            "缺少启用模板文件源，文档或账单渲染无法定位模板。",
        ),
        (
            "letter_head.default",
            "默认信头",
            "t_letter_head",
            _enabled_count(db, LetterHead, LetterHead.is_default.is_(True)) > 0,
            "缺少默认信头，账单或文档打印抬头无法确认。",
        ),
        (
            "country.active",
            "启用国家地区",
            "t_country",
            _enabled_count(db, Country) > 0,
            "缺少启用国家地区，案卷和费率主数据引用不完整。",
        ),
        (
            "department.active",
            "启用部门",
            "t_department",
            _enabled_count(db, Department) > 0,
            "缺少启用部门，业务归属和报表维度不完整。",
        ),
        (
            "doc_template.enabled",
            "启用文件模板",
            "t_doc_template",
            _enabled_count(db, DocTemplate) > 0,
            "缺少启用文件模板，文件向导无法按配置联动。",
        ),
        (
            "task_template.enabled",
            "启用任务模板",
            "t_task_template",
            _enabled_count(db, TaskTemplate) > 0,
            "缺少启用任务模板，来文自动任务无法生成。",
        ),
    ]
    return [
        {
            "key": key,
            "label": label,
            "table": table,
            "severity": "hard_block",
            "message": message,
        }
        for key, label, table, present, message in checks
        if not present
    ]


def _system_param_exists(db: Session, key: str) -> bool:
    return (
        db.execute(select(SystemParam.id).where(SystemParam.param_key == key)).first() is not None
    )


def _enabled_count(db: Session, model: type[Any], *criteria: Any) -> int:
    stmt = select(func.count()).select_from(model)
    if hasattr(model, "enabled"):
        stmt = stmt.where(model.enabled.is_(True))
    elif hasattr(model, "is_active"):
        stmt = stmt.where(model.is_active.is_(True))
    for criterion in criteria:
        stmt = stmt.where(criterion)
    return int(db.execute(stmt).scalar_one())
