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


def _split_official_codes(code_text: str) -> list[str]:
    return [part.strip() for part in re.split(r"[,，;；]", code_text or "") if part.strip()]


def _official_notice_input_fields(name: str, code_text: str) -> str:
    return json.dumps(
        {
            "catalog_kind": "OFFICIAL_NOTICE",
            "official_notice_name": name,
            "official_doc_codes": _split_official_codes(code_text),
            "official_doc_code_text": code_text,
            "source": OFFICIAL_NOTICE_CATALOG_SOURCE,
        },
        ensure_ascii=False,
        sort_keys=True,
    )


def seed_official_notice_catalog(db: Session) -> int:
    changed = 0
    for index, (name, code_text) in enumerate(OFFICIAL_NOTICE_CATALOG, start=1):
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
            "input_fields": _official_notice_input_fields(name, code_text),
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
