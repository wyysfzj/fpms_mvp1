"""
V3 Case Workflow Stepper — 后端测试

测试范围:
  1. CaseStatus 枚举扩展验证（13 种 V3 法律状态 + 7 种旧状态向后兼容）
  2. GET /cases/{id} 返回完整字段（title_cn, status, filing_date, client_name 等）
  3. GET /cases 列表返回新增字段与状态筛选
  4. V3 状态案件创建与查询
  5. POST /cases 字段保存验证

测试数据: 全部使用简体中文
"""

from __future__ import annotations

from uuid import uuid4

# ---------------------------------------------------------------------------
# §1  CaseStatus 枚举扩展验证
# ---------------------------------------------------------------------------


class TestCaseStatusEnum:
    """验证 CaseStatus 枚举包含所有 V3 所需状态值。"""

    def test_v3_workflow_statuses_exist(self) -> None:
        """BE-02: 所有 13 种 V3 法律状态均在 CaseStatus 枚举中。"""
        from app.modules.cases.enums import CaseStatus

        v3_statuses = [
            "WAITING_RECEIPT",
            "PRELIM_EXAM",
            "PRELIM_PASS",
            "AMENDMENT",
            "PUBLISHED",
            "SUB_EXAM",
            "OA1",
            "OA2",
            "REEXAM",
            "GRANTED",
            "REJECTED",
            "TERMINATED",
            "INVALIDATED",
        ]

        for status_name in v3_statuses:
            assert hasattr(CaseStatus, status_name), f"CaseStatus 缺少 V3 状态: {status_name}"
            assert CaseStatus[status_name].value == status_name

    def test_legacy_statuses_preserved(self) -> None:
        """BE-03: 现有状态值保持向后兼容。"""
        from app.modules.cases.enums import CaseStatus

        legacy_statuses = [
            "NOT_FILED",
            "PENDING",
            "GRANTED",
            "REJECTED",
            "WITHDRAWN",
            "ABANDONED",
            "EXPIRED",
        ]

        for status_name in legacy_statuses:
            assert hasattr(CaseStatus, status_name), f"CaseStatus 丢失旧状态: {status_name}"

    def test_status_string_length_within_32_chars(self) -> None:
        """验证所有状态值长度 ≤ 32，确保与数据库 String(32) 兼容。"""
        from app.modules.cases.enums import CaseStatus

        for member in CaseStatus:
            assert len(member.value) <= 32, f"状态值 '{member.value}' 超过 32 字符限制"


# ---------------------------------------------------------------------------
# §2  辅助函数
# ---------------------------------------------------------------------------


def _create_test_client(client, auth_headers: dict, name_cn: str = "测试客户有限公司") -> str:
    """创建测试客户，返回 client_id。"""
    payload = {
        "client_code": f"V3-C-{uuid4().hex[:8]}",
        "name_cn": name_cn,
        "name_en": "Test Client",
        "client_type": "CLIENT",
        "default_currency": "CNY",
        "is_active": True,
    }
    resp = client.post("/api/v1/clients", json=payload, headers=auth_headers)
    assert resp.status_code == 201, f"创建客户失败: {resp.text}"
    return resp.json()["id"]


def _create_case_via_api(
    client,
    auth_headers: dict,
    case_no: str | None = None,
    client_id: str | None = None,
    title_cn: str | None = None,
) -> str:
    """通过 API 创建案件，返回 case_id。"""
    payload: dict = {
        "case_no": case_no or f"V3-CASE-{uuid4().hex[:8]}",
        "fee_reduction": "0",
        "case_type": "NORMAL",
        "patent_category": "INV",
        "flow_dir": "CN_DOMESTIC",
    }
    if client_id:
        payload["client_id"] = client_id
    if title_cn:
        payload["title_cn"] = title_cn

    resp = client.post("/api/v1/cases", json=payload, headers=auth_headers)
    assert resp.status_code == 201, f"创建案件失败: {resp.text}"
    return resp.json()["id"]


def _create_case_via_orm(
    session_factory,
    case_no: str | None = None,
    client_id: str | None = None,
    title_cn: str | None = None,
    status: str = "NOT_FILED",
    filing_date=None,
    recv_date=None,
) -> str:
    """通过 ORM 直接创建案件（可设置任意状态），返回 case_id。"""
    from app.modules.cases.models import Case

    case_id = str(uuid4())
    with session_factory() as db:
        case = Case(
            id=case_id,
            case_no=case_no or f"V3-ORM-{uuid4().hex[:8]}",
            case_type="NORMAL",
            patent_category="INV",
            flow_dir="CN_DOMESTIC",
            client_id=client_id,
            title_cn=title_cn,
            status=status,
            filing_date=filing_date,
            recv_date=recv_date,
        )
        db.add(case)
        db.commit()
    return case_id


# ---------------------------------------------------------------------------
# §3  GET /cases/{id} 完整字段验证
# ---------------------------------------------------------------------------


class TestCaseDetailFields:
    """验证 GET /cases/{id} 返回完整字段。"""

    def test_detail_returns_title_cn(self, client, auth_headers, session_factory) -> None:
        """BE-04: 详情返回 title_cn 字段。"""
        case_id = _create_case_via_orm(session_factory, title_cn="智能充电桩控制方法及装置")
        resp = client.get(f"/api/v1/cases/{case_id}", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "title_cn" in data
        assert data["title_cn"] == "智能充电桩控制方法及装置"

    def test_detail_returns_status(self, client, auth_headers, session_factory) -> None:
        """BE-05: 详情返回 status 字段，默认 NOT_FILED。"""
        case_id = _create_case_via_orm(session_factory)
        resp = client.get(f"/api/v1/cases/{case_id}", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "status" in data
        assert data["status"] == "NOT_FILED"

    def test_detail_returns_filing_date(self, client, auth_headers, session_factory) -> None:
        """BE-06: 详情返回 filing_date 字段（新建案件为 null）。"""
        case_id = _create_case_via_orm(session_factory)
        resp = client.get(f"/api/v1/cases/{case_id}", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "filing_date" in data

    def test_detail_returns_recv_date(self, client, auth_headers, session_factory) -> None:
        """BE-07: 详情返回 recv_date 字段（新建案件为 null）。"""
        case_id = _create_case_via_orm(session_factory)
        resp = client.get(f"/api/v1/cases/{case_id}", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "recv_date" in data

    def test_detail_returns_client_name(self, client, auth_headers, session_factory) -> None:
        """BE-08: 详情返回 client_name（通过关联客户解析）。"""
        client_id = _create_test_client(client, auth_headers, name_cn="蔚来汽车科技有限公司")
        case_id = _create_case_via_orm(session_factory, client_id=client_id)
        resp = client.get(f"/api/v1/cases/{case_id}", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "client_name" in data
        assert data["client_name"] == "蔚来汽车科技有限公司"

    def test_detail_returns_applicants_list(self, client, auth_headers, session_factory) -> None:
        """BE-09: 详情返回 applicants 列表。"""
        case_id = _create_case_via_orm(session_factory)
        resp = client.get(f"/api/v1/cases/{case_id}", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "applicants" in data
        assert isinstance(data["applicants"], list)

    def test_detail_returns_inventors_list(self, client, auth_headers, session_factory) -> None:
        """BE-10: 详情返回 inventors 列表。"""
        case_id = _create_case_via_orm(session_factory)
        resp = client.get(f"/api/v1/cases/{case_id}", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "inventors" in data
        assert isinstance(data["inventors"], list)

    def test_detail_returns_priorities_list(self, client, auth_headers, session_factory) -> None:
        """BE-11: 详情返回 priorities 列表。"""
        case_id = _create_case_via_orm(session_factory)
        resp = client.get(f"/api/v1/cases/{case_id}", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "priorities" in data
        assert isinstance(data["priorities"], list)

    def test_detail_returns_timestamps(self, client, auth_headers, session_factory) -> None:
        """BE-12: 详情返回 created_at / updated_at。"""
        case_id = _create_case_via_orm(session_factory)
        resp = client.get(f"/api/v1/cases/{case_id}", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "created_at" in data
        assert "updated_at" in data

    def test_detail_client_name_null_when_no_client(
        self, client, auth_headers, session_factory
    ) -> None:
        """BE-13: client_id 为 null 时 client_name 也为 null。"""
        case_id = _create_case_via_orm(session_factory)
        resp = client.get(f"/api/v1/cases/{case_id}", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("client_id") is None
        assert data.get("client_name") is None

    def test_detail_with_v3_status(self, client, auth_headers, session_factory) -> None:
        """详情 API 正确返回 V3 状态值。"""
        case_id = _create_case_via_orm(
            session_factory, title_cn="高性能芯片散热结构", status="SUB_EXAM"
        )
        resp = client.get(f"/api/v1/cases/{case_id}", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "SUB_EXAM"
        assert data["title_cn"] == "高性能芯片散热结构"


# ---------------------------------------------------------------------------
# §4  GET /cases 列表返回字段验证
# ---------------------------------------------------------------------------


class TestCaseListFields:
    """验证 GET /cases 列表返回新增字段。"""

    def test_list_items_include_client_name(self, client, auth_headers) -> None:
        """BE-14: 列表 items 包含 client_name。"""
        client_id = _create_test_client(client, auth_headers, name_cn="百度在线网络技术有限公司")
        case_no = f"V3-LIST-{uuid4().hex[:8]}"
        _create_case_via_api(client, auth_headers, case_no=case_no, client_id=client_id)

        resp = client.get(f"/api/v1/cases?case_no={case_no}", headers=auth_headers)
        assert resp.status_code == 200
        items = resp.json()["items"]
        found = [i for i in items if i["case_no"] == case_no]
        assert len(found) == 1
        assert found[0]["client_name"] == "百度在线网络技术有限公司"

    def test_list_items_include_title_cn(self, client, auth_headers, session_factory) -> None:
        """BE-15: 列表 items 包含 title_cn。"""
        case_no = f"V3-TITLE-{uuid4().hex[:8]}"
        _create_case_via_orm(session_factory, case_no=case_no, title_cn="新型锂电池正极材料")

        resp = client.get(f"/api/v1/cases?case_no={case_no}", headers=auth_headers)
        assert resp.status_code == 200
        items = resp.json()["items"]
        found = [i for i in items if i["case_no"] == case_no]
        assert len(found) == 1
        assert found[0]["title_cn"] == "新型锂电池正极材料"

    def test_list_items_include_status(self, client, auth_headers) -> None:
        """BE-16: 列表 items 包含 status。"""
        case_no = f"V3-STATUS-{uuid4().hex[:8]}"
        _create_case_via_api(client, auth_headers, case_no=case_no)

        resp = client.get(f"/api/v1/cases?case_no={case_no}", headers=auth_headers)
        assert resp.status_code == 200
        items = resp.json()["items"]
        found = [i for i in items if i["case_no"] == case_no]
        assert len(found) == 1
        assert "status" in found[0]

    def test_list_projects_workflow_status_lifecycle_axes_and_updated_at(
        self, client, auth_headers, session_factory
    ) -> None:
        from app.modules.cases.models import Case

        case_no = f"V3-LIFECYCLE-{uuid4().hex[:8]}"
        case_id = _create_case_via_orm(
            session_factory,
            case_no=case_no,
            status="GRANT_PENDING",
        )
        with session_factory() as db:
            case = db.get(Case, case_id)
            assert case is not None
            case.business_stage = "GRANT_REGISTRATION_IN_PROGRESS"
            case.official_procedure_stage = "GRANT_REGISTRATION"
            case.legal_status = "APPLICATION_PENDING"
            db.commit()

        response = client.get(f"/api/v1/cases?case_no={case_no}", headers=auth_headers)

        assert response.status_code == 200, response.text
        item = response.json()["items"][0]
        assert item["status"] == "GRANT_PENDING"
        assert item["workflow_status"] == item["status"]
        assert item["business_stage"] == "GRANT_REGISTRATION_IN_PROGRESS"
        assert item["official_procedure_stage"] == "GRANT_REGISTRATION"
        assert item["legal_status"] == "APPLICATION_PENDING"
        assert item["updated_at"]
        assert item["filing_date"] is None

    def test_list_filter_by_status(self, client, auth_headers) -> None:
        """BE-17: 列表支持 status 参数筛选。"""
        resp = client.get("/api/v1/cases?status=WAITING_RECEIPT", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        for item in data["items"]:
            assert item["status"] == "WAITING_RECEIPT"

    def test_list_items_include_filing_date(self, client, auth_headers) -> None:
        """BE-18: 列表 items 包含 filing_date。"""
        case_no = f"V3-FD-{uuid4().hex[:8]}"
        _create_case_via_api(client, auth_headers, case_no=case_no)

        resp = client.get(f"/api/v1/cases?case_no={case_no}", headers=auth_headers)
        assert resp.status_code == 200
        items = resp.json()["items"]
        found = [i for i in items if i["case_no"] == case_no]
        assert len(found) == 1
        assert "filing_date" in found[0], "列表响应缺少 filing_date 字段"

    def test_list_items_include_recv_date(self, client, auth_headers) -> None:
        """BE-19: 列表 items 包含 recv_date。"""
        case_no = f"V3-RD-{uuid4().hex[:8]}"
        _create_case_via_api(client, auth_headers, case_no=case_no)

        resp = client.get(f"/api/v1/cases?case_no={case_no}", headers=auth_headers)
        assert resp.status_code == 200
        items = resp.json()["items"]
        found = [i for i in items if i["case_no"] == case_no]
        assert len(found) == 1
        assert "recv_date" in found[0], "列表响应缺少 recv_date 字段"


# ---------------------------------------------------------------------------
# §5  POST /cases 字段保存验证
# ---------------------------------------------------------------------------


class TestCaseCreate:
    """验证 POST /cases 保存字段完整性。"""

    def test_post_saves_title_cn(self, client, auth_headers) -> None:
        """POST /cases 正确保存 title_cn。"""
        case_no = f"V3-POST-{uuid4().hex[:8]}"
        _create_case_via_api(
            client, auth_headers, case_no=case_no, title_cn="基于深度学习的图像识别方法"
        )

        resp = client.get(f"/api/v1/cases?case_no={case_no}", headers=auth_headers)
        assert resp.status_code == 200
        items = resp.json()["items"]
        found = [i for i in items if i["case_no"] == case_no]
        assert len(found) == 1
        assert found[0]["title_cn"] == "基于深度学习的图像识别方法"


# ---------------------------------------------------------------------------
# §6  V3 状态案件验证
# ---------------------------------------------------------------------------


class TestV3StatusORM:
    """通过 ORM 设置 V3 状态并验证 API 能正确返回。"""

    def test_v3_status_cases_in_list(self, client, auth_headers, session_factory) -> None:
        """BE-01: 全部 13 种 V3 状态案件可通过列表 API 查询返回。"""
        v3_test_cases = [
            ("WAITING_RECEIPT", "智能充电桩控制方法"),
            ("PRELIM_EXAM", "自动驾驶路径规划系统"),
            ("PRELIM_PASS", "新型锂电池正极材料制备方法"),
            ("AMENDMENT", "柔性显示屏弯折结构改进"),
            ("PUBLISHED", "量子通信密钥分发协议优化方法"),
            ("SUB_EXAM", "高性能芯片散热结构及制造工艺"),
            ("OA1", "基于大语言模型的智能客服对话系统"),
            ("OA2", "光伏组件封装工艺及设备"),
            ("REEXAM", "新型mRNA疫苗递送载体"),
            ("GRANTED", "无人机集群编队飞行控制方法"),
            ("REJECTED", "基于区块链的供应链溯源系统"),
            ("TERMINATED", "石墨烯基超级电容器制备方法"),
            ("INVALIDATED", "基于5G的远程医疗手术导航系统"),
        ]

        unique_prefix = uuid4().hex[:6]
        for i, (status_val, title) in enumerate(v3_test_cases):
            _create_case_via_orm(
                session_factory,
                case_no=f"V3-13-{unique_prefix}-{i:02d}",
                title_cn=title,
                status=status_val,
            )

        for status_val, _title in v3_test_cases:
            resp = client.get(f"/api/v1/cases?status={status_val}", headers=auth_headers)
            assert resp.status_code == 200
            data = resp.json()
            assert data["total"] >= 1, f"状态 {status_val} 应至少有 1 条结果"
            matching = [i for i in data["items"] if i["status"] == status_val]
            assert len(matching) >= 1

    def test_v3_status_readable_via_detail(self, client, auth_headers, session_factory) -> None:
        """V3 状态案件可通过详情 API 读取。"""
        case_id = _create_case_via_orm(
            session_factory, title_cn="测试详情查询", status="WAITING_RECEIPT"
        )
        resp = client.get(f"/api/v1/cases/{case_id}", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "WAITING_RECEIPT"
        assert data["title_cn"] == "测试详情查询"

    def test_all_13_v3_statuses_queryable(self, client, auth_headers, session_factory) -> None:
        """验证所有 13 种 V3 状态均可通过 status 参数查询。"""
        v3_statuses = [
            "WAITING_RECEIPT",
            "PRELIM_EXAM",
            "PRELIM_PASS",
            "AMENDMENT",
            "PUBLISHED",
            "SUB_EXAM",
            "OA1",
            "OA2",
            "REEXAM",
            "GRANTED",
            "REJECTED",
            "TERMINATED",
            "INVALIDATED",
        ]

        unique_prefix = uuid4().hex[:6]
        for i, status_val in enumerate(v3_statuses):
            _create_case_via_orm(
                session_factory,
                case_no=f"V3-ALL13-{unique_prefix}-{i:02d}",
                title_cn=f"测试案件_{status_val}",
                status=status_val,
            )

        for status_val in v3_statuses:
            resp = client.get(f"/api/v1/cases?status={status_val}", headers=auth_headers)
            assert resp.status_code == 200
            data = resp.json()
            assert data["total"] >= 1, (
                f"状态 {status_val} 应至少有 1 条结果，实际为 {data['total']}"
            )
            for item in data["items"]:
                assert item["status"] == status_val

    def test_branch_statuses_separate_from_main(
        self, client, auth_headers, session_factory
    ) -> None:
        """验证分支状态 (REJECTED/TERMINATED/INVALIDATED) 可独立于主干状态查询。"""
        unique = uuid4().hex[:6]

        _create_case_via_orm(
            session_factory,
            case_no=f"V3-MAIN-{unique}",
            title_cn="主干案件：实审中",
            status="SUB_EXAM",
        )
        _create_case_via_orm(
            session_factory,
            case_no=f"V3-BRANCH-{unique}",
            title_cn="分支案件：已驳回",
            status="REJECTED",
        )

        resp = client.get("/api/v1/cases?status=SUB_EXAM", headers=auth_headers)
        assert resp.status_code == 200
        for item in resp.json()["items"]:
            assert item["status"] == "SUB_EXAM"

        resp = client.get("/api/v1/cases?status=REJECTED", headers=auth_headers)
        assert resp.status_code == 200
        for item in resp.json()["items"]:
            assert item["status"] == "REJECTED"


# ---------------------------------------------------------------------------
# §7  综合流程测试
# ---------------------------------------------------------------------------


class TestV3WorkflowFullFlow:
    """综合测试：创建客户 → 创建案件 → 列表/详情验证。"""

    def test_full_case_list_flow(self, client, auth_headers, session_factory) -> None:
        """列表端到端：创建含完整字段的案件 → 通过列表 API 验证。"""
        client_id = _create_test_client(client, auth_headers, name_cn="华为技术有限公司")

        case_no = f"V3-FULL-{uuid4().hex[:8]}"
        _create_case_via_orm(
            session_factory,
            case_no=case_no,
            client_id=client_id,
            title_cn="高性能芯片散热结构及制造工艺",
            status="SUB_EXAM",
        )

        resp = client.get(f"/api/v1/cases?case_no={case_no}", headers=auth_headers)
        assert resp.status_code == 200
        items = resp.json()["items"]
        found = [i for i in items if i["case_no"] == case_no]
        assert len(found) == 1
        assert found[0]["client_name"] == "华为技术有限公司"
        assert found[0]["title_cn"] == "高性能芯片散热结构及制造工艺"
        assert found[0]["status"] == "SUB_EXAM"

    def test_full_case_detail_flow(self, client, auth_headers, session_factory) -> None:
        """详情端到端：创建案件 → 通过详情 API 验证完整字段。"""
        client_id = _create_test_client(client, auth_headers, name_cn="大疆创新科技有限公司")

        case_id = _create_case_via_orm(
            session_factory,
            client_id=client_id,
            title_cn="无人机集群编队飞行控制方法",
            status="GRANTED",
        )

        resp = client.get(f"/api/v1/cases/{case_id}", headers=auth_headers)
        assert resp.status_code == 200
        detail = resp.json()
        assert detail["title_cn"] == "无人机集群编队飞行控制方法"
        assert detail["client_name"] == "大疆创新科技有限公司"
        assert detail["status"] == "GRANTED"
        assert "applicants" in detail
        assert "inventors" in detail
        assert "priorities" in detail
        assert "created_at" in detail
        assert "updated_at" in detail

    def test_case_not_found_returns_404(self, client, auth_headers) -> None:
        """不存在的案件 ID 返回 404。"""
        fake_id = str(uuid4())
        resp = client.get(f"/api/v1/cases/{fake_id}", headers=auth_headers)
        assert resp.status_code == 404

    def test_workflow_status_filter_flow(self, client, auth_headers, session_factory) -> None:
        """模拟前端 workflow 筛选：按阶段查询案件列表。"""
        unique = uuid4().hex[:6]

        test_data = [
            ("WAITING_RECEIPT", "受理阶段案件_甲"),
            ("WAITING_RECEIPT", "受理阶段案件_乙"),
            ("SUB_EXAM", "实审阶段案件_甲"),
            ("SUB_EXAM", "实审阶段案件_乙"),
            ("SUB_EXAM", "实审阶段案件_丙"),
            ("GRANTED", "授权阶段案件_甲"),
        ]

        for i, (status_val, title) in enumerate(test_data):
            _create_case_via_orm(
                session_factory,
                case_no=f"V3-WF-{unique}-{i:02d}",
                title_cn=title,
                status=status_val,
            )

        # 模拟前端点击"受理"卡片 → 筛选
        resp = client.get("/api/v1/cases?status=WAITING_RECEIPT", headers=auth_headers)
        assert resp.status_code == 200
        wr_items = [i for i in resp.json()["items"] if i["status"] == "WAITING_RECEIPT"]
        assert len(wr_items) >= 2

        # 模拟前端点击"实审"卡片 → 筛选
        resp = client.get("/api/v1/cases?status=SUB_EXAM", headers=auth_headers)
        assert resp.status_code == 200
        se_items = [i for i in resp.json()["items"] if i["status"] == "SUB_EXAM"]
        assert len(se_items) >= 3

        # 模拟前端"清除筛选" → 全部案件
        resp = client.get("/api/v1/cases", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["total"] >= 6
