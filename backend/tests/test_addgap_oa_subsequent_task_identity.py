from __future__ import annotations

from sqlalchemy import delete, select
from sqlalchemy.orm import sessionmaker

from app.modules.tasks.models import TaskTemplate
from scripts.seed_dev import seed_task_templates


def _template_state(template: TaskTemplate) -> tuple[object, ...]:
    return (
        template.name,
        template.enabled,
        template.deadline_base,
        template.add_days,
        template.add_months,
        template.inner_offset_days,
        template.description,
    )


def test_seed_adds_subsequent_oa_identity_without_calculable_deadline_fallback(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as db:
        first_oa = db.execute(
            select(TaskTemplate).where(TaskTemplate.code == "OA_REPLY")
        ).scalar_one()
        first_oa_before = _template_state(first_oa)

        seed_task_templates(db)

        subsequent = db.execute(
            select(TaskTemplate).where(TaskTemplate.code == "OA_REPLY_SUBSEQUENT")
        ).scalar_one_or_none()
        assert subsequent is not None, "seed must create the subsequent OA task identity"
        assert subsequent.name == "后续审查意见答复期限"
        assert subsequent.enabled is True
        assert subsequent.deadline_base is None
        assert subsequent.add_days is None
        assert subsequent.add_months == 0
        assert subsequent.inner_offset_days is None
        assert subsequent.description == (
            "第二次及以后审查意见答复任务；截止日必须使用官文载明的明确期限"
        )

        db.refresh(first_oa)
        assert _template_state(first_oa) == first_oa_before


def test_task_template_seed_is_bootstrap_safe_and_idempotent(
    session_factory: sessionmaker,
) -> None:
    with session_factory() as db:
        db.execute(delete(TaskTemplate))
        db.commit()

        seed_task_templates(db)
        first_seed = db.execute(
            select(TaskTemplate).where(TaskTemplate.code == "OA_REPLY_SUBSEQUENT")
        ).scalar_one_or_none()
        assert first_seed is not None
        first_seed_id = first_seed.id

        seed_task_templates(db)

        templates = (
            db.execute(select(TaskTemplate).order_by(TaskTemplate.code.asc())).scalars().all()
        )
        by_code = {template.code: template for template in templates}
        assert {"OA_REPLY", "OA_REPLY_SUBSEQUENT", "GRANT_FEE"} <= set(by_code)
        assert by_code["OA_REPLY_SUBSEQUENT"].id == first_seed_id
        assert by_code["OA_REPLY_SUBSEQUENT"].add_days is None
        assert by_code["OA_REPLY_SUBSEQUENT"].add_months == 0
        assert sum(template.code == "OA_REPLY_SUBSEQUENT" for template in templates) == 1
