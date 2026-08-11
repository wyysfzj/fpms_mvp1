from __future__ import annotations

import json
import re
from uuid import uuid4

from sqlalchemy.orm import Session

from app.modules.documents.models import DocTemplate

OFFICIAL_NOTICE_CATALOG_SOURCE = "相关流程操作-20260526.docx [P0101] TABLE 001"

OFFICIAL_NOTICE_CATALOG: tuple[tuple[str, str], ...] = (
    ("受理通知-电子", "200101"),
    ("补正通知", "220704,200029,210302,220302,230301"),
    ("第一次审查意见通知书", "210401,210402"),
    ("第一次审查意见通知书（新型）", "220301"),
    ("第二次审查意见通知书", "210403"),
    ("初步审查合格", "210304"),
    ("公布通知书", "210305"),
    ("公布及进入实审通知", "210308"),
    ("授权通知书-电子", "200602"),
    ("专利证书", "400001,400002,400003"),
    ("驳回决定", "210407,200305,210408"),
    ("视为撤回", "200022"),
    ("视为放弃", "200601"),
    ("专利权终止通知", "200702"),
    ("恢复权利通知书", "200026"),
    ("年费缴费通知书", "200701"),
    ("复审请求受理通知书", "200905"),
    ("复审通知书", "200908A,200924"),
    ("复审决定书", "200912"),
    ("复审补正通知书", "200907"),
    ("第三次审查意见通知书", "210403"),
    ("变更手续合格通知", ""),
    ("手续合格通知书", "200028"),
    ("第四次审查意见通知书", "210403"),
    ("延长期限审批通知书", "200024"),
    ("实审期限届满前通知", "210306"),
    ("向外国申请专利保密审查通知", "210326"),
    ("国际申请进入中国通知", "250302"),
    ("第五次审查意见通知书", "210403"),
    ("第一次审查意见通知书（外观）", "220301"),
    ("费用减缓审批通知书", "200021"),
    ("视为未要求优先权通知", "200302"),
    ("进入实审通知", "210307"),
    ("缴纳申请费通知书", "200103"),
    ("PPH审查决定", "210419"),
    ("无效口审通知", ""),
    ("改正译文错误通知书", "210409"),
    ("分案通知", ""),
    ("予以优先审查通知书", ""),
    ("复审案件结案通知书", "200913"),
    ("向外国申请专利保密审查决定书", "21032701"),
    ("办理恢复权利手续补正通知书", "200032"),
    ("审查业务专业便函", "200020;200025;210417"),
    ("视为未提出通知书", "200023"),
    ("专利登记簿副本", ""),
    ("国际申请初审合格", "250304"),
    ("避免重复授予专利权的通知书", "210415"),
    ("PCT检索报告", ""),
    ("修改文件缺陷通知", ""),
    ("国际检索单位书面意见", ""),
    ("传送检索报告和书面意见的通知", ""),
    ("国际申请号和申请日通知", ""),
    ("关于缴纳规定费用通知", ""),
    ("收到记录本通知", ""),
    ("收到检索本的通知", ""),
    ("PCT电子提交收据", ""),
    ("国际公布通知", ""),
    ("传送优先权文件通知", ""),
    ("指定局不适用30个月进入期限的通知", ""),
    ("无其他可适用表格时的通知书", ""),
)

OFFICIAL_NOTICE_OA_ACCEPTANCE_ACTIVATIONS: dict[str, tuple[str, str, str, str | None, bool]] = {
    "受理通知-电子": ("ACCEPTANCE_NOTICE", "ACCEPTANCE_NOTICE", "ACCEPTED", None, False),
    "第一次审查意见通知书": ("OA_REPLY", "OA_IN", "OA1", "OA_REPLY", True),
    "第二次审查意见通知书": (
        "OA_REPLY",
        "OA_IN",
        "OA2",
        "OA_REPLY_SUBSEQUENT",
        True,
    ),
    "第三次审查意见通知书": (
        "OA_REPLY",
        "OA_IN",
        "OA2",
        "OA_REPLY_SUBSEQUENT",
        True,
    ),
    "第四次审查意见通知书": (
        "OA_REPLY",
        "OA_IN",
        "OA2",
        "OA_REPLY_SUBSEQUENT",
        True,
    ),
    "第五次审查意见通知书": (
        "OA_REPLY",
        "OA_IN",
        "OA2",
        "OA_REPLY_SUBSEQUENT",
        True,
    ),
}
OFFICIAL_NOTICE_GRANT_ACTIVATIONS = {
    **OFFICIAL_NOTICE_OA_ACCEPTANCE_ACTIVATIONS,
    "授权通知书-电子": (
        "GRANT_NOTICE",
        "GRANT_NOTICE",
        "GRANT_PENDING",
        None,
        False,
    ),
}
OFFICIAL_NOTICE_APPLICATION_FEE_ACTIVATIONS = {
    **OFFICIAL_NOTICE_GRANT_ACTIVATIONS,
    "缴纳申请费通知书": (
        "APPLICATION_FEE_NOTICE",
        "APPLICATION_FEE_NOTICE",
        None,
        None,
        False,
    ),
}
OFFICIAL_NOTICE_FEE_REDUCTION_APPROVAL_ACTIVATIONS = {
    **OFFICIAL_NOTICE_APPLICATION_FEE_ACTIVATIONS,
    "费用减缓审批通知书": (
        "FEE_REDUCTION_APPROVAL_NOTICE",
        "FEE_REDUCTION_APPROVAL_NOTICE",
        None,
        None,
        False,
    ),
}

_OA_NOTICE_SEQUENCE_BY_TEMPLATE_CODE = {
    "OA_IN": 1,
    "OFFICIAL_NOTICE_003": 1,
    "OFFICIAL_NOTICE_005": 2,
    "OFFICIAL_NOTICE_021": 3,
    "OFFICIAL_NOTICE_024": 4,
    "OFFICIAL_NOTICE_029": 5,
}


def resolve_oa_notice_sequence(template_code: object) -> int | None:
    if type(template_code) is not str:
        return None
    return _OA_NOTICE_SEQUENCE_BY_TEMPLATE_CODE.get(template_code)


def _split_official_codes(code_text: str) -> list[str]:
    return [part.strip() for part in re.split(r"[,，;；]", code_text or "") if part.strip()]


def _official_notice_input_fields(
    name: str,
    code_text: str,
    activation: tuple[str, str, str, str | None, bool] | None = None,
) -> str:
    metadata = {
        "archive_status_restore": None,
        "canonical_template_code": None,
        "catalog_kind": "OFFICIAL_NOTICE",
        "catalog_status": "REFERENCE_ONLY",
        "completion_event": None,
        "deadline_source_policy": None,
        "execution_behavior": None,
        "official_notice_name": name,
        "official_doc_codes": _split_official_codes(code_text),
        "official_doc_code_text": code_text,
        "source": OFFICIAL_NOTICE_CATALOG_SOURCE,
    }
    if activation is not None:
        behavior, canonical_code, _status_effect, _task_code, _need_reply = activation
        metadata.update(
            {
                "canonical_template_code": canonical_code,
                "catalog_status": "EXECUTABLE",
                "execution_behavior": behavior,
            }
        )
        if behavior in {"OA_REPLY", "GRANT_NOTICE", "APPLICATION_FEE_NOTICE"}:
            metadata["deadline_source_policy"] = "EXPLICIT_OFFICIAL_DUE_REQUIRED"
        if behavior == "OA_REPLY":
            metadata.update(
                {
                    "archive_status_restore": "SUB_EXAM",
                    "completion_event": "OFFICIAL_RECEIPT_ARCHIVED",
                }
            )
    return json.dumps(metadata, ensure_ascii=False, sort_keys=True)


def _seed_official_notice_catalog(
    db: Session,
    activations: dict[str, tuple[str, str, str, str | None, bool]],
) -> int:
    changed = 0
    for index, (name, code_text) in enumerate(OFFICIAL_NOTICE_CATALOG, start=1):
        activation = activations.get(name)
        values = {
            "code": f"OFFICIAL_NOTICE_{index:03d}",
            "name": name,
            "direction": "IN",
            "enabled": True,
            "status_effect": None,
            "status_restore": None,
            "deadline_template_code": None,
            "fee_draft_type": None,
            "fee_item_list": None,
            "need_reply": False,
            "reply_to_template_code": None,
            "input_fields": _official_notice_input_fields(name, code_text, activation),
        }
        if activation is not None:
            behavior, _canonical_code, status_effect, task_code, need_reply = activation
            values.update(
                {
                    "status_effect": status_effect,
                    "deadline_template_code": task_code,
                    "need_reply": need_reply,
                }
            )
            if behavior == "GRANT_NOTICE":
                values["fee_draft_type"] = "GRANT_FEE"
            if behavior == "APPLICATION_FEE_NOTICE":
                values["fee_draft_type"] = "APPLICATION_FEE"
        existing = db.query(DocTemplate).filter(DocTemplate.code == values["code"]).first()
        if existing is None:
            db.add(DocTemplate(id=str(uuid4()), **values))
            changed += 1
            continue
        row_changed = False
        for field, value in values.items():
            if getattr(existing, field) != value:
                setattr(existing, field, value)
                row_changed = True
        if row_changed:
            changed += 1
    return changed


def seed_official_notice_catalog(db: Session) -> int:
    return _seed_official_notice_catalog(db, {})


def seed_oa_acceptance_official_notice_catalog(db: Session) -> int:
    return _seed_official_notice_catalog(db, OFFICIAL_NOTICE_OA_ACCEPTANCE_ACTIVATIONS)


def seed_grant_official_notice_catalog(db: Session) -> int:
    return _seed_official_notice_catalog(db, OFFICIAL_NOTICE_GRANT_ACTIVATIONS)


def seed_application_fee_official_notice_catalog(db: Session) -> int:
    return _seed_official_notice_catalog(db, OFFICIAL_NOTICE_APPLICATION_FEE_ACTIVATIONS)


def seed_fee_reduction_approval_official_notice_catalog(db: Session) -> int:
    return _seed_official_notice_catalog(
        db,
        OFFICIAL_NOTICE_FEE_REDUCTION_APPROVAL_ACTIVATIONS,
    )


OFFICIAL_LETTER_OUT_CATALOG_SOURCE = "相关流程操作-20260526.docx [P0102] TABLE 002"
OFFICIAL_LETTER_OUT_DECISION_SOURCE = (
    "docs/product/v8/customer-decisions/2026-08-10-v8-full-batch-scheme-a.txt"
)
OFFICIAL_LETTER_OUT_DECISION_VERSION = "customer-decision:2026-08-10:v8-full-batch-scheme-a:v1"
OFFICIAL_LETTER_OUT_DECISION_SHA256 = (
    "e6cfd648f1d366e27bde3f74310f00033a6db60ce55d850d2e668764745faace"
)

# 客户"致函官方文件清单"22 行（相关流程操作 TABLE 002），作为 OUT 方向文书目录。
OFFICIAL_LETTER_OUT_CATALOG: tuple[str, ...] = (
    "补正答复",
    "一通意见陈述",
    "提前公开请求",
    "实审请求",
    "主动撤回",
    "主动放弃",
    "著录项目变更",
    "复审请求",
    "主动补正",
    "恢复权利请求",
    "复审、无效程序中的意见陈述",
    "复审中的补正",
    "纸件申请转电子申请请求书",
    "费用减缓请求书",
    "改正译文错误请求书",
    "PPH请求",
    "发明主动修改",
    "延长期限请求",
    "二通意见陈述",
    "三通意见陈述",
    "四通意见陈述",
    "办理文件副本请求书",
)
OFFICIAL_LETTER_OUT_FORM_001_CLASSIFICATIONS = {
    "补正答复": ("form-001", "INTERNAL_ONLY"),
}
OFFICIAL_LETTER_OUT_FORM_002_CLASSIFICATIONS = {
    **OFFICIAL_LETTER_OUT_FORM_001_CLASSIFICATIONS,
    "一通意见陈述": ("form-002", "INTERNAL_ONLY"),
}
OFFICIAL_LETTER_OUT_FORM_003_CLASSIFICATIONS = {
    **OFFICIAL_LETTER_OUT_FORM_002_CLASSIFICATIONS,
    "提前公开请求": ("form-003", "INTERNAL_ONLY"),
}
OFFICIAL_LETTER_OUT_FORM_004_CLASSIFICATIONS = {
    **OFFICIAL_LETTER_OUT_FORM_003_CLASSIFICATIONS,
    "实审请求": ("form-004", "INTERNAL_ONLY"),
}
OFFICIAL_LETTER_OUT_FORM_005_CLASSIFICATIONS = {
    **OFFICIAL_LETTER_OUT_FORM_004_CLASSIFICATIONS,
    "主动撤回": ("form-005", "INTERNAL_ONLY"),
}
OFFICIAL_LETTER_OUT_FORM_006_CLASSIFICATIONS = {
    **OFFICIAL_LETTER_OUT_FORM_005_CLASSIFICATIONS,
    "主动放弃": ("form-006", "INTERNAL_ONLY"),
}
OFFICIAL_LETTER_OUT_FORM_007_CLASSIFICATIONS = {
    **OFFICIAL_LETTER_OUT_FORM_006_CLASSIFICATIONS,
    "著录项目变更": ("form-007", "INTERNAL_ONLY"),
}
OFFICIAL_LETTER_OUT_FORM_008_CLASSIFICATIONS = {
    **OFFICIAL_LETTER_OUT_FORM_007_CLASSIFICATIONS,
    "复审请求": ("form-008", "INTERNAL_ONLY"),
}
OFFICIAL_LETTER_OUT_FORM_009_CLASSIFICATIONS = {
    **OFFICIAL_LETTER_OUT_FORM_008_CLASSIFICATIONS,
    "主动补正": ("form-009", "INTERNAL_ONLY"),
}
OFFICIAL_LETTER_OUT_FORM_010_CLASSIFICATIONS = {
    **OFFICIAL_LETTER_OUT_FORM_009_CLASSIFICATIONS,
    "恢复权利请求": ("form-010", "INTERNAL_ONLY"),
}
OFFICIAL_LETTER_OUT_FORM_011_CLASSIFICATIONS = {
    **OFFICIAL_LETTER_OUT_FORM_010_CLASSIFICATIONS,
    "复审、无效程序中的意见陈述": ("form-011", "INTERNAL_ONLY"),
}
OFFICIAL_LETTER_OUT_FORM_012_CLASSIFICATIONS = {
    **OFFICIAL_LETTER_OUT_FORM_011_CLASSIFICATIONS,
    "复审中的补正": ("form-012", "INTERNAL_ONLY"),
}
OFFICIAL_LETTER_OUT_FORM_013_CLASSIFICATIONS = {
    **OFFICIAL_LETTER_OUT_FORM_012_CLASSIFICATIONS,
    "纸件申请转电子申请请求书": ("form-013", "INTERNAL_ONLY"),
}
OFFICIAL_LETTER_OUT_FORM_014_CLASSIFICATIONS = {
    **OFFICIAL_LETTER_OUT_FORM_013_CLASSIFICATIONS,
    "费用减缓请求书": ("form-014", "INTERNAL_ONLY"),
}
OFFICIAL_LETTER_OUT_FORM_015_CLASSIFICATIONS = {
    **OFFICIAL_LETTER_OUT_FORM_014_CLASSIFICATIONS,
    "改正译文错误请求书": ("form-015", "INTERNAL_ONLY"),
}
OFFICIAL_LETTER_OUT_FORM_016_CLASSIFICATIONS = {
    **OFFICIAL_LETTER_OUT_FORM_015_CLASSIFICATIONS,
    "PPH请求": ("form-016", "INTERNAL_ONLY"),
}
OFFICIAL_LETTER_OUT_FORM_017_CLASSIFICATIONS = {
    **OFFICIAL_LETTER_OUT_FORM_016_CLASSIFICATIONS,
    "发明主动修改": ("form-017", "INTERNAL_ONLY"),
}

OFFICIAL_LETTER_OUT_FORM_018_CLASSIFICATIONS = {
    **OFFICIAL_LETTER_OUT_FORM_017_CLASSIFICATIONS,
    "延长期限请求": ("form-018", "INTERNAL_ONLY"),
}

OFFICIAL_LETTER_OUT_FORM_019_CLASSIFICATIONS = {
    **OFFICIAL_LETTER_OUT_FORM_018_CLASSIFICATIONS,
    "二通意见陈述": ("form-019", "INTERNAL_ONLY"),
}

OFFICIAL_LETTER_OUT_FORM_020_CLASSIFICATIONS = {
    **OFFICIAL_LETTER_OUT_FORM_019_CLASSIFICATIONS,
    "三通意见陈述": ("form-020", "INTERNAL_ONLY"),
}

OFFICIAL_LETTER_OUT_FORM_021_CLASSIFICATIONS = {
    **OFFICIAL_LETTER_OUT_FORM_020_CLASSIFICATIONS,
    "四通意见陈述": ("form-021", "INTERNAL_ONLY"),
}


def _official_letter_out_input_fields(
    name: str,
    classification: tuple[str, str] | None = None,
) -> str:
    metadata = {
        "catalog_kind": "OFFICIAL_LETTER_OUT",
        "official_letter_name": name,
        "source": OFFICIAL_LETTER_OUT_CATALOG_SOURCE,
    }
    if classification is not None:
        scope, value = classification
        metadata.update(
            {
                "catalog_status": "REFERENCE_ONLY",
                "decision_source": OFFICIAL_LETTER_OUT_DECISION_SOURCE,
                "decision_source_sha256": OFFICIAL_LETTER_OUT_DECISION_SHA256,
                "decision_version": OFFICIAL_LETTER_OUT_DECISION_VERSION,
                "legacy_form_classification": value,
                "legacy_form_scope": scope,
            }
        )
    return json.dumps(metadata, ensure_ascii=False, sort_keys=True)


def _seed_official_letter_out_catalog(
    db: Session,
    classifications: dict[str, tuple[str, str]],
) -> int:
    changed = 0
    for index, name in enumerate(OFFICIAL_LETTER_OUT_CATALOG, start=1):
        values = {
            "code": f"OFFICIAL_LETTER_OUT_{index:03d}",
            "name": name,
            "direction": "OUT",
            "enabled": True,
            "status_effect": None,
            "status_restore": None,
            "deadline_template_code": None,
            "fee_draft_type": None,
            "fee_item_list": None,
            "need_reply": False,
            "reply_to_template_code": None,
            "input_fields": _official_letter_out_input_fields(
                name,
                classifications.get(name),
            ),
        }
        existing = db.query(DocTemplate).filter(DocTemplate.code == values["code"]).first()
        if existing is None:
            db.add(DocTemplate(id=str(uuid4()), **values))
            changed += 1
            continue
        for field, value in values.items():
            if getattr(existing, field) != value:
                setattr(existing, field, value)
                changed += 1
                break
    return changed


def seed_official_letter_out_catalog(db: Session) -> int:
    return _seed_official_letter_out_catalog(db, {})


def seed_official_letter_out_form_001_catalog(db: Session) -> int:
    return _seed_official_letter_out_catalog(
        db,
        OFFICIAL_LETTER_OUT_FORM_001_CLASSIFICATIONS,
    )


def seed_official_letter_out_form_002_catalog(db: Session) -> int:
    return _seed_official_letter_out_catalog(
        db,
        OFFICIAL_LETTER_OUT_FORM_002_CLASSIFICATIONS,
    )


def seed_official_letter_out_form_003_catalog(db: Session) -> int:
    return _seed_official_letter_out_catalog(
        db,
        OFFICIAL_LETTER_OUT_FORM_003_CLASSIFICATIONS,
    )


def seed_official_letter_out_form_004_catalog(db: Session) -> int:
    return _seed_official_letter_out_catalog(
        db,
        OFFICIAL_LETTER_OUT_FORM_004_CLASSIFICATIONS,
    )


def seed_official_letter_out_form_005_catalog(db: Session) -> int:
    return _seed_official_letter_out_catalog(
        db,
        OFFICIAL_LETTER_OUT_FORM_005_CLASSIFICATIONS,
    )


def seed_official_letter_out_form_006_catalog(db: Session) -> int:
    return _seed_official_letter_out_catalog(
        db,
        OFFICIAL_LETTER_OUT_FORM_006_CLASSIFICATIONS,
    )


def seed_official_letter_out_form_007_catalog(db: Session) -> int:
    return _seed_official_letter_out_catalog(
        db,
        OFFICIAL_LETTER_OUT_FORM_007_CLASSIFICATIONS,
    )


def seed_official_letter_out_form_008_catalog(db: Session) -> int:
    return _seed_official_letter_out_catalog(
        db,
        OFFICIAL_LETTER_OUT_FORM_008_CLASSIFICATIONS,
    )


def seed_official_letter_out_form_009_catalog(db: Session) -> int:
    return _seed_official_letter_out_catalog(
        db,
        OFFICIAL_LETTER_OUT_FORM_009_CLASSIFICATIONS,
    )


def seed_official_letter_out_form_010_catalog(db: Session) -> int:
    return _seed_official_letter_out_catalog(
        db,
        OFFICIAL_LETTER_OUT_FORM_010_CLASSIFICATIONS,
    )


def seed_official_letter_out_form_011_catalog(db: Session) -> int:
    return _seed_official_letter_out_catalog(
        db,
        OFFICIAL_LETTER_OUT_FORM_011_CLASSIFICATIONS,
    )


def seed_official_letter_out_form_012_catalog(db: Session) -> int:
    return _seed_official_letter_out_catalog(
        db,
        OFFICIAL_LETTER_OUT_FORM_012_CLASSIFICATIONS,
    )


def seed_official_letter_out_form_013_catalog(db: Session) -> int:
    return _seed_official_letter_out_catalog(
        db,
        OFFICIAL_LETTER_OUT_FORM_013_CLASSIFICATIONS,
    )


def seed_official_letter_out_form_014_catalog(db: Session) -> int:
    return _seed_official_letter_out_catalog(
        db,
        OFFICIAL_LETTER_OUT_FORM_014_CLASSIFICATIONS,
    )


def seed_official_letter_out_form_015_catalog(db: Session) -> int:
    return _seed_official_letter_out_catalog(
        db,
        OFFICIAL_LETTER_OUT_FORM_015_CLASSIFICATIONS,
    )


def seed_official_letter_out_form_016_catalog(db: Session) -> int:
    return _seed_official_letter_out_catalog(
        db,
        OFFICIAL_LETTER_OUT_FORM_016_CLASSIFICATIONS,
    )


def seed_official_letter_out_form_017_catalog(db: Session) -> int:
    return _seed_official_letter_out_catalog(
        db,
        OFFICIAL_LETTER_OUT_FORM_017_CLASSIFICATIONS,
    )


def seed_official_letter_out_form_018_catalog(db: Session) -> int:
    return _seed_official_letter_out_catalog(
        db,
        OFFICIAL_LETTER_OUT_FORM_018_CLASSIFICATIONS,
    )


def seed_official_letter_out_form_019_catalog(db: Session) -> int:
    return _seed_official_letter_out_catalog(
        db,
        OFFICIAL_LETTER_OUT_FORM_019_CLASSIFICATIONS,
    )


def seed_official_letter_out_form_020_catalog(db: Session) -> int:
    return _seed_official_letter_out_catalog(
        db,
        OFFICIAL_LETTER_OUT_FORM_020_CLASSIFICATIONS,
    )


def seed_official_letter_out_form_021_catalog(db: Session) -> int:
    return _seed_official_letter_out_catalog(
        db,
        OFFICIAL_LETTER_OUT_FORM_021_CLASSIFICATIONS,
    )
