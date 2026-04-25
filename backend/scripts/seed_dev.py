#!/usr/bin/env python
"""Seed development database with default roles, permissions, and admin user."""

import sys
from datetime import date
from pathlib import Path
from uuid import uuid4

from sqlalchemy.orm import Session

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.core.security import get_password_hash  # noqa: E402
from app.db.session import SessionLocal  # noqa: E402
from app.models.system_param import SystemParam  # noqa: E402
from app.modules.auth.models import T_Role, T_User, T_UserRole  # noqa: E402
from app.modules.cases.models import Case, T_CaseApplicant, T_CaseInventor  # noqa: E402
from app.modules.documents.models import DocTemplate  # noqa: E402
from app.modules.masterdata.applicants.models import Applicant  # noqa: E402
from app.modules.masterdata.clients.models import Client  # noqa: E402
from app.modules.rbac.service import seed_default_roles_perms  # noqa: E402
from app.modules.tasks.models import TaskTemplate  # noqa: E402


def seed_admin_user(db: Session) -> None:
    """Create default admin user. Idempotent."""
    username = "admin"

    admin_role = db.query(T_Role).filter(T_Role.code == "Admin").first()
    if not admin_role:
        raise RuntimeError("Admin role 'Admin' not found. Seed roles first.")

    admin_user = db.query(T_User).filter(T_User.username == username).first()
    created_user = False
    if not admin_user:
        admin_user = T_User(
            id=str(uuid4()),
            username=username,
            display_name="Administrator",
            password_hash=get_password_hash("admin123"),
            is_active=True,
        )
        db.add(admin_user)
        db.flush()
        created_user = True

    existing_binding = (
        db.query(T_UserRole)
        .filter(
            T_UserRole.user_id == admin_user.id,
            T_UserRole.role_id == admin_role.id,
        )
        .first()
    )
    created_binding = False
    if not existing_binding:
        db.add(T_UserRole(user_id=admin_user.id, role_id=admin_role.id))
        created_binding = True

    db.commit()

    if created_user:
        print(f"Created admin user '{username}' with password 'admin123'")
    elif created_binding:
        print(f"Bound admin user '{username}' to Admin role")
    else:
        print(f"Admin user '{username}' already exists")


def seed_v3_cases(db: Session) -> None:
    """Create V3 workflow stepper test cases covering all 13 statuses. Idempotent."""
    # Check if V3 cases already seeded
    existing = db.query(Case).filter(Case.case_no == "V3-001").first()
    if existing:
        print("V3 test cases already exist, skipping")
        return

    # Create test clients
    clients_data = [
        {"code": "C-NIO", "name_cn": "蔚来汽车科技有限公司", "name_en": "NIO Inc."},
        {"code": "C-BYD", "name_cn": "比亚迪股份有限公司", "name_en": "BYD Company Limited"},
        {"code": "C-HW", "name_cn": "华为技术有限公司", "name_en": "Huawei Technologies Co., Ltd."},
        {"code": "C-XM", "name_cn": "小米科技有限责任公司", "name_en": "Xiaomi Corporation"},
    ]

    client_ids = {}
    for cd in clients_data:
        existing_client = db.query(Client).filter(Client.client_code == cd["code"]).first()
        if existing_client:
            client_ids[cd["code"]] = existing_client.id
        else:
            cid = str(uuid4())
            db.add(
                Client(
                    id=cid,
                    client_code=cd["code"],
                    name_cn=cd["name_cn"],
                    name_en=cd["name_en"],
                )
            )
            client_ids[cd["code"]] = cid
    db.flush()

    # V3 test cases — one per status, all in Simplified Chinese
    v3_cases = [
        {
            "case_no": "V3-001",
            "title_cn": "智能充电桩控制方法及系统",
            "title_en": "Smart Charging Pile Control Method and System",
            "app_no": "202410001001.1",
            "status": "WAITING_RECEIPT",
            "client_code": "C-NIO",
            "filing_date": date(2024, 1, 15),
            "recv_date": date(2024, 1, 10),
            "applicant": "蔚来汽车科技有限公司",
            "inventor": "张伟",
        },
        {
            "case_no": "V3-002",
            "title_cn": "电池热管理温控装置",
            "title_en": "Battery Thermal Management Temperature Control Device",
            "app_no": "202410001002.6",
            "status": "PRELIM_EXAM",
            "client_code": "C-NIO",
            "filing_date": date(2024, 2, 20),
            "recv_date": date(2024, 2, 15),
            "applicant": "蔚来汽车科技有限公司",
            "inventor": "李强",
        },
        {
            "case_no": "V3-003",
            "title_cn": "自动驾驶路径规划算法",
            "title_en": "Autonomous Driving Path Planning Algorithm",
            "app_no": "202410001003.0",
            "status": "PRELIM_PASS",
            "client_code": "C-BYD",
            "filing_date": date(2024, 3, 10),
            "recv_date": date(2024, 3, 5),
            "applicant": "比亚迪股份有限公司",
            "inventor": "王芳",
        },
        {
            "case_no": "V3-004",
            "title_cn": "车载激光雷达信号处理方法",
            "title_en": "Vehicle Lidar Signal Processing Method",
            "app_no": "202410001004.5",
            "status": "AMENDMENT",
            "client_code": "C-BYD",
            "filing_date": date(2024, 3, 25),
            "recv_date": date(2024, 3, 20),
            "applicant": "比亚迪股份有限公司",
            "inventor": "赵敏",
        },
        {
            "case_no": "V3-005",
            "title_cn": "5G基站天线阵列优化设计",
            "title_en": "5G Base Station Antenna Array Optimization Design",
            "app_no": "202410001005.X",
            "status": "PUBLISHED",
            "client_code": "C-HW",
            "filing_date": date(2024, 4, 12),
            "recv_date": date(2024, 4, 8),
            "applicant": "华为技术有限公司",
            "inventor": "陈刚",
        },
        {
            "case_no": "V3-006",
            "title_cn": "分布式数据库一致性协议",
            "title_en": "Distributed Database Consistency Protocol",
            "app_no": "202410001006.4",
            "status": "SUB_EXAM",
            "client_code": "C-HW",
            "filing_date": date(2024, 5, 8),
            "recv_date": date(2024, 5, 3),
            "applicant": "华为技术有限公司",
            "inventor": "刘洋",
        },
        {
            "case_no": "V3-007",
            "title_cn": "手机摄像模组光学防抖方法",
            "title_en": "Smartphone Camera Module OIS Method",
            "app_no": "202410001007.9",
            "status": "OA1",
            "client_code": "C-XM",
            "filing_date": date(2024, 5, 22),
            "recv_date": date(2024, 5, 18),
            "applicant": "小米科技有限责任公司",
            "inventor": "周磊",
        },
        {
            "case_no": "V3-008",
            "title_cn": "智能家居语音控制交互系统",
            "title_en": "Smart Home Voice Control Interaction System",
            "app_no": "202410001008.3",
            "status": "OA2",
            "client_code": "C-XM",
            "filing_date": date(2024, 6, 5),
            "recv_date": date(2024, 6, 1),
            "applicant": "小米科技有限责任公司",
            "inventor": "吴娜",
        },
        {
            "case_no": "V3-009",
            "title_cn": "芯片制造工艺缺陷检测方法",
            "title_en": "Chip Manufacturing Process Defect Detection Method",
            "app_no": "202410001009.8",
            "status": "REEXAM",
            "client_code": "C-HW",
            "filing_date": date(2024, 6, 20),
            "recv_date": date(2024, 6, 15),
            "applicant": "华为技术有限公司",
            "inventor": "孙涛",
        },
        {
            "case_no": "V3-010",
            "title_cn": "新能源汽车能量回收控制策略",
            "title_en": "New Energy Vehicle Energy Recovery Control Strategy",
            "app_no": "202410001010.0",
            "status": "GRANTED",
            "client_code": "C-BYD",
            "filing_date": date(2024, 1, 8),
            "recv_date": date(2024, 1, 3),
            "applicant": "比亚迪股份有限公司",
            "inventor": "郑华",
        },
        {
            "case_no": "V3-011",
            "title_cn": "无线充电效率提升装置",
            "title_en": "Wireless Charging Efficiency Enhancement Device",
            "app_no": "202410001011.5",
            "status": "REJECTED",
            "client_code": "C-XM",
            "filing_date": date(2024, 2, 12),
            "recv_date": date(2024, 2, 8),
            "applicant": "小米科技有限责任公司",
            "inventor": "马超",
        },
        {
            "case_no": "V3-012",
            "title_cn": "固态电池电解质制备方法",
            "title_en": "Solid-State Battery Electrolyte Preparation Method",
            "app_no": "202410001012.X",
            "status": "TERMINATED",
            "client_code": "C-NIO",
            "filing_date": date(2023, 6, 15),
            "recv_date": date(2023, 6, 10),
            "applicant": "蔚来汽车科技有限公司",
            "inventor": "黄丽",
        },
        {
            "case_no": "V3-013",
            "title_cn": "物联网设备安全认证协议",
            "title_en": "IoT Device Security Authentication Protocol",
            "app_no": "202410001013.4",
            "status": "INVALIDATED",
            "client_code": "C-HW",
            "filing_date": date(2023, 3, 20),
            "recv_date": date(2023, 3, 15),
            "applicant": "华为技术有限公司",
            "inventor": "林峰",
        },
    ]

    for c in v3_cases:
        case_id = str(uuid4())
        db.add(
            Case(
                id=case_id,
                case_no=c["case_no"],
                case_type="NORMAL",
                patent_category="INV",
                flow_dir="CN_DOMESTIC",
                client_id=client_ids[c["client_code"]],
                title_cn=c["title_cn"],
                title_en=c["title_en"],
                app_no=c["app_no"],
                status=c["status"],
                filing_date=c["filing_date"],
                recv_date=c["recv_date"],
            )
        )
        # Add one applicant per case
        db.add(
            T_CaseApplicant(
                id=str(uuid4()),
                case_id=case_id,
                seq=1,
                is_first=True,
                name_cn=c["applicant"],
            )
        )
        # Add one inventor per case
        db.add(
            T_CaseInventor(
                id=str(uuid4()),
                case_id=case_id,
                seq=1,
                name_cn=c["inventor"],
            )
        )

    db.commit()
    print(f"Created {len(v3_cases)} V3 test cases covering all 13 statuses")


def seed_masterdata_applicants(db: Session) -> None:
    """Seed core dev applicants with persisted applicant_type values. Idempotent."""
    seed_rows = [
        {
            "code": "DS-AP-001",
            "name_cn": "北京创新科技有限公司",
            "name_en": "Beijing Innovation Technology Co., Ltd.",
            "applicant_type": "ENTITY",
        },
        {
            "code": "DS-AP-002",
            "name_cn": "张三",
            "name_en": "Zhang San",
            "applicant_type": "INDIVIDUAL",
        },
    ]

    created = 0
    updated = 0
    for seed_row in seed_rows:
        existing = db.query(Applicant).filter(Applicant.code == seed_row["code"]).first()
        if not existing:
            db.add(
                Applicant(
                    id=str(uuid4()),
                    code=seed_row["code"],
                    name_cn=seed_row["name_cn"],
                    name_en=seed_row["name_en"],
                    applicant_type=seed_row["applicant_type"],
                    is_active=True,
                )
            )
            created += 1
            continue

        if existing.applicant_type != seed_row["applicant_type"]:
            existing.applicant_type = seed_row["applicant_type"]
            updated += 1

    db.commit()
    if created or updated:
        print(f"Seeded {created} dev applicants and updated {updated} applicant types")
    else:
        print("Dev applicants already seeded, skipping")


def seed_task_templates(db: Session) -> None:
    """Seed starter task templates. Idempotent."""
    templates = [
        {
            "code": "OA_REPLY",
            "name": "OA答复期限",
            "add_days": 120,
            "inner_offset_days": 14,
            "description": "审查意见通知书答复期限自动任务",
        },
        {
            "code": "GRANT_FEE",
            "name": "授权登记费",
            "add_days": 60,
            "inner_offset_days": 7,
            "description": "授权登记费缴纳期限自动任务",
        },
    ]
    created = 0
    for t in templates:
        existing = db.query(TaskTemplate).filter(TaskTemplate.code == t["code"]).first()
        if not existing:
            db.add(
                TaskTemplate(
                    id=str(uuid4()),
                    code=t["code"],
                    name=t["name"],
                    add_days=t["add_days"],
                    inner_offset_days=t["inner_offset_days"],
                    description=t["description"],
                )
            )
            created += 1
    db.commit()
    if created:
        print(f"Created {created} task templates")
    else:
        print("Task templates already exist, skipping")


def seed_doc_templates(db: Session) -> None:
    """Seed default doc templates. Idempotent."""
    templates = [
        {
            "code": "OA_IN",
            "name": "审查意见通知书（收文）",
            "direction": "IN",
            "need_reply": True,
            "deadline_template_code": "OA_REPLY",
            "status_effect": "OA1",
            "status_restore": None,
            "fee_draft_type": None,
            "fee_item_list": None,
            "reply_to_template_code": None,
            "input_fields": None,
        },
        {
            "code": "OA_OUT",
            "name": "审查意见答复书（发文）",
            "direction": "OUT",
            "need_reply": False,
            "deadline_template_code": None,
            "status_effect": None,
            "status_restore": None,
            "fee_draft_type": None,
            "fee_item_list": None,
            "reply_to_template_code": "OA_IN",
            "input_fields": None,
        },
        {
            "code": "ACCEPTANCE_NOTICE",
            "name": "受理通知书",
            "direction": "IN",
            "need_reply": False,
            "deadline_template_code": None,
            "status_effect": "ACCEPTED",
            "status_restore": None,
            "fee_draft_type": None,
            "fee_item_list": None,
            "reply_to_template_code": None,
            "input_fields": None,
        },
        {
            "code": "GRANT_NOTICE",
            "name": "授权通知书",
            "direction": "IN",
            "need_reply": False,
            "deadline_template_code": None,
            "status_effect": "GRANT_PENDING",
            "status_restore": None,
            "fee_draft_type": "GRANT_FEE",
            "fee_item_list": None,
            "reply_to_template_code": None,
            "input_fields": None,
        },
        {
            "code": "CLIENT_IN",
            "name": "客户来函",
            "direction": "IN",
            "need_reply": False,
            "deadline_template_code": None,
            "status_effect": None,
            "status_restore": None,
            "fee_draft_type": None,
            "fee_item_list": None,
            "reply_to_template_code": None,
            "input_fields": None,
        },
    ]
    created = 0
    for t in templates:
        existing = db.query(DocTemplate).filter(DocTemplate.code == t["code"]).first()
        if not existing:
            db.add(DocTemplate(id=str(uuid4()), **t))
            created += 1
    db.commit()
    if created:
        print(f"Created {created} doc templates")
    else:
        print("Doc templates already exist, skipping")


def seed_system_params(db: Session) -> None:
    """Seed default system parameters. Idempotent."""
    defaults = [
        {"param_key": "case_no_prefix", "param_value": "CN", "description": "案号前缀"},
        {"param_key": "default_currency", "param_value": "CNY", "description": "默认币种"},
        {"param_key": "bill_no_prefix", "param_value": "INV", "description": "账单编号前缀"},
        {
            "param_key": "task_sheet_template_path",
            "param_value": "templates/task_sheet.docx",
            "description": "任务单模板路径",
        },
    ]
    created = 0
    for d in defaults:
        existing = db.query(SystemParam).filter(SystemParam.param_key == d["param_key"]).first()
        if not existing:
            db.add(SystemParam(**d))
            created += 1
    db.commit()
    if created:
        print(f"Created {created} system parameters")
    else:
        print("System parameters already exist, skipping")


def main() -> None:
    """Run all dev seeds."""
    with SessionLocal() as db:
        print("Seeding default roles and permissions...")
        seed_default_roles_perms(db)
        print("✓ Roles and permissions seeded")

        print("Seeding admin user...")
        seed_admin_user(db)
        print("✓ Admin user seeded")

        print("Seeding V3 workflow test cases...")
        seed_v3_cases(db)
        print("✓ V3 test cases seeded")

        print("Seeding masterdata applicants...")
        seed_masterdata_applicants(db)
        print("✓ Masterdata applicants seeded")

        print("Seeding task templates...")
        seed_task_templates(db)
        print("✓ Task templates seeded")

        print("Seeding doc templates...")
        seed_doc_templates(db)
        print("✓ Doc templates seeded")

        print("Seeding system parameters...")
        seed_system_params(db)
        print("✓ System parameters seeded")

    print("\n✅ Development database seeded successfully!")
    print("   Login: username='admin', password='admin123'")


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as exc:  # noqa: BLE001
        print(f"Seed failed: {exc}")
        sys.exit(1)
