from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from framework.models import TestCase as SkeletonTestCase
from handlers.wave_w0 import (
    handle_tc_w0_cfg_005,
    handle_tc_w0_cfg_006,
    handle_tc_w0_cfg_007,
)


class FakeResponse:
    def __init__(self, status_code: int, payload: Any) -> None:
        self.status_code = status_code
        self._payload = payload
        self.text = str(payload)

    @property
    def ok(self) -> bool:
        return 200 <= self.status_code < 400

    def json(self) -> Any:
        return self._payload


class FakeApi:
    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []
        self.rules: list[dict[str, Any]] = []
        self.users: dict[str, dict[str, Any]] = {}
        self.clients: list[dict[str, Any]] = []
        self.cases: list[dict[str, Any]] = []
        self.commissions: list[dict[str, Any]] = []

    def login(self, username: str, password: str) -> str:
        self.calls.append(
            {"method": "LOGIN", "username": username, "password": password}
        )
        return "fake-token"

    def post(self, path: str, **kwargs: Any) -> FakeResponse:
        self.calls.append({"method": "POST", "path": path, "kwargs": kwargs})
        if path == "/admin/users":
            payload = kwargs["json"]
            user = {
                "id": f"user-{len(self.users) + 1}",
                "username": payload["username"],
                "password": payload["password"],
                "roles": payload["roles"],
                "is_active": payload.get("is_active", True),
            }
            self.users[user["username"]] = user
            return FakeResponse(201, user)
        if path == "/clients":
            payload = kwargs["json"]
            client = {"id": f"client-{len(self.clients) + 1}", **payload}
            self.clients.append(client)
            return FakeResponse(201, client)
        if path == "/cases":
            payload = kwargs["json"]
            case = {"id": f"case-{len(self.cases) + 1}", **payload}
            self.cases.append(case)
            return FakeResponse(201, case)
        if path == "/bills/manual":
            payload = kwargs["json"]
            bill = {"id": "bill-1", **payload}
            self._generate_commissions_from_bill(payload)
            return FakeResponse(201, bill)
        if path != "/commission/rules":
            return FakeResponse(404, {"message": "not found"})

        payload = kwargs["json"]
        invalid = self._invalid_payload(payload)
        if invalid:
            return FakeResponse(400, {"error": {"code": "COMMISSION_RULE_INVALID"}})
        conflict = self._find_conflict(payload)
        if conflict is not None:
            return FakeResponse(
                409,
                {
                    "error": {
                        "code": "COMMISSION_RULE_CONFLICT",
                        "details": {"conflict_rule_id": conflict["id"]},
                    }
                },
            )

        rule = {
            "id": len(self.rules) + 1,
            "created_at": "2026-05-09T00:00:00",
            "updated_at": "2026-05-09T00:00:00",
            **payload,
        }
        self.rules.append(rule)
        return FakeResponse(201, rule)

    def get(self, path: str, **kwargs: Any) -> FakeResponse:
        self.calls.append({"method": "GET", "path": path, "kwargs": kwargs})
        if path == "/admin/users":
            items = [
                {
                    "id": user["id"],
                    "username": user["username"],
                    "is_active": user["is_active"],
                    "roles": user["roles"],
                }
                for user in self.users.values()
            ]
            return FakeResponse(
                200, {"items": items, "page": 1, "page_size": 100, "total": len(items)}
            )
        if path == "/commission":
            params = kwargs.get("params") or {}
            case_id = params.get("case_id")
            items = [
                item
                for item in self.commissions
                if not case_id or item["case_id"] == case_id
            ]
            return FakeResponse(
                200, {"items": items, "page": 1, "page_size": 20, "total": len(items)}
            )
        if path == "/clients":
            params = kwargs.get("params") or {}
            q = params.get("q")
            items = [
                item
                for item in self.clients
                if not q or item.get("client_code") == q or item.get("name_cn") == q
            ]
            return FakeResponse(
                200, {"items": items, "page": 1, "page_size": 20, "total": len(items)}
            )
        if path != "/commission/rules":
            return FakeResponse(404, {"message": "not found"})
        params = kwargs.get("params") or {}
        q = params.get("q")
        items = [
            rule
            for rule in self.rules
            if not q or str(q).lower() in rule["rule_name"].lower()
        ]
        return FakeResponse(
            200, {"items": items, "page": 1, "page_size": 20, "total": len(items)}
        )

    def put(self, path: str, **kwargs: Any) -> FakeResponse:
        self.calls.append({"method": "PUT", "path": path, "kwargs": kwargs})
        prefix = "/commission/rules/"
        if not path.startswith(prefix):
            return FakeResponse(404, {"message": "not found"})
        rule_id = int(path.removeprefix(prefix))
        for rule in self.rules:
            if rule["id"] == rule_id:
                rule.update(kwargs["json"])
                return FakeResponse(200, rule)
        return FakeResponse(404, {"message": "not found"})

    def _generate_commissions_from_bill(self, payload: dict[str, Any]) -> None:
        case = self.cases[-1]
        splits = case["agent_splits"]
        amount = Decimal(str(payload["items"][0]["unit_price"]))
        rule = self.rules[-1]
        for split in splits:
            ratio = Decimal(str(split["share_ratio"]))
            base_fee = (amount * ratio / Decimal("100")).quantize(Decimal("0.01"))
            self.commissions.append(
                {
                    "case_id": payload["case_id"],
                    "agent_id": split["agent_id"],
                    "rule_id": rule["id"],
                    "fee_type": "SERVICE",
                    "base_fee": str(base_fee),
                    "s1_amount": str(
                        (base_fee * Decimal(str(rule["s1_rate"]))).quantize(
                            Decimal("0.01")
                        )
                    ),
                    "s2_amount": str(
                        (base_fee * Decimal(str(rule["s2_rate"]))).quantize(
                            Decimal("0.01")
                        )
                    ),
                    "wait_pay": rule["wait_pay"],
                    "force_settle": rule["force_settle"],
                    "status": "OPEN",
                }
            )

    def _find_conflict(self, payload: dict[str, Any]) -> dict[str, Any] | None:
        scope = (
            payload.get("case_type"),
            payload.get("fee_type"),
            payload.get("flow_dir"),
            payload.get("patent_category"),
            payload.get("wait_pay"),
            payload.get("force_settle"),
        )
        for rule in self.rules:
            if scope == (
                rule.get("case_type"),
                rule.get("fee_type"),
                rule.get("flow_dir"),
                rule.get("patent_category"),
                rule.get("wait_pay"),
                rule.get("force_settle"),
            ):
                return rule
        return None

    def _invalid_payload(self, payload: dict[str, Any]) -> bool:
        for field in ("s1_rate", "s2_rate"):
            value = Decimal(str(payload[field]))
            if value < Decimal("0") or value > Decimal("1"):
                return True
        for field in ("s1_fixed_amount", "s2_fixed_amount"):
            if Decimal(str(payload[field])) < Decimal("0"):
                return True
        return False


class FakeDb:
    def __init__(self, enabled: bool = False) -> None:
        self.rows: list[tuple[str, dict[str, Any]]] = []
        self._enabled = enabled

    def enabled(self) -> bool:
        return self._enabled

    def assert_row_exists(self, table: str, where: dict[str, Any]) -> dict[str, Any]:
        self.rows.append((table, where))
        return {"id": "row-id", **where}


@dataclass
class FakeRuntime:
    username: str
    password: str
    run_id: str
    api: FakeApi
    db: FakeDb


def _case() -> SkeletonTestCase:
    return SkeletonTestCase(
        id="TC-W0-CFG-005",
        wave="W0",
        wave_title="W0 基础配置",
        context="",
        priority="P0",
        categories=["Happy", "Unhappy"],
        topic="提成规则-比例、固定额、启停和冲突校验",
        stage_code=None,
        stage_name="提成规则",
        coverage_ids=[],
        requirement_ids=[],
        validation_ids=[],
        preconditions="",
        steps_summary="",
        expected="",
        automation_recommendation="",
        data_refs=[
            "DS-U-ADM",
            "DS-CFG-COM-NORMAL-SERVICE",
            "DS-CFG-COM-INVALID-RATE",
        ],
    )


def _settle_flags_case() -> SkeletonTestCase:
    return SkeletonTestCase(
        id="TC-W0-CFG-007",
        wave="W0",
        wave_title="W0 基础配置",
        context="提成 WaitPay / ForceSettle",
        priority="P1",
        categories=["Boundary"],
        topic="提成-WaitPay 与 ForceSettle 可结算性",
        stage_code=None,
        stage_name="提成规则",
        coverage_ids=[],
        requirement_ids=[],
        validation_ids=[],
        preconditions="",
        steps_summary="",
        expected="",
        automation_recommendation="",
        data_refs=[
            "DS-CFG-COM-NORMAL-WAITPAY",
            "DS-CFG-COM-NORMAL-FORCE",
            "DS-CFG-BILL-SERVICE-1000",
        ],
    )


def _split_case() -> SkeletonTestCase:
    return SkeletonTestCase(
        id="TC-W0-CFG-006",
        wave="W0",
        wave_title="W0 基础配置",
        context="提成生成与代理人分摊",
        priority="P0",
        categories=["Happy"],
        topic="提成-服务费账单触发 70/30 分摊",
        stage_code=None,
        stage_name="提成规则",
        coverage_ids=[],
        requirement_ids=[],
        validation_ids=[],
        preconditions="",
        steps_summary="",
        expected="",
        automation_recommendation="",
        data_refs=[
            "DS-U-FI-01",
            "DS-CFG-CASE-NORMAL-INV",
            "DS-CFG-COM-NORMAL-SERVICE",
            "DS-CFG-BILL-SERVICE-1000",
        ],
    )


def test_tc_w0_cfg_005_handler_creates_validates_and_disables_rule() -> None:
    runtime = FakeRuntime(
        username="admin",
        password="dummy-password",
        run_id="RUN-W0-COM",
        api=FakeApi(),
        db=FakeDb(enabled=False),
    )

    handle_tc_w0_cfg_005(runtime, _case())  # type: ignore[arg-type]

    post_calls = [call for call in runtime.api.calls if call["method"] == "POST"]
    assert len(post_calls) == 5
    assert all(call["path"] == "/commission/rules" for call in post_calls)

    created_payload = post_calls[0]["kwargs"]["json"]
    assert created_payload["rule_name"] == "普通申请服务费提成-RUN-W0-COM"
    assert created_payload["case_type"] == "NORMAL"
    assert created_payload["fee_type"] == "SERVICE"
    assert created_payload["flow_dir"] == "CN_DOMESTIC"
    assert created_payload["patent_category"] == "INV"
    assert created_payload["s1_rate"] == "0.30"
    assert created_payload["s2_rate"] == "0.20"
    assert created_payload["enabled"] is True

    invalid_payloads = [call["kwargs"]["json"] for call in post_calls[2:]]
    assert [payload["s1_rate"] for payload in invalid_payloads] == [
        "-0.01",
        "0.30",
        "0.30",
    ]
    assert invalid_payloads[1]["s2_rate"] == "1.01"
    assert invalid_payloads[2]["s1_fixed_amount"] == "-1.00"

    put_calls = [call for call in runtime.api.calls if call["method"] == "PUT"]
    assert put_calls == [
        {
            "method": "PUT",
            "path": "/commission/rules/1",
            "kwargs": {"json": {"enabled": False}},
        }
    ]
    assert runtime.db.rows == []


def test_tc_w0_cfg_007_handler_preserves_settleability_flags() -> None:
    runtime = FakeRuntime(
        username="admin",
        password="dummy-password",
        run_id="RUN-W0-COM-FLAG",
        api=FakeApi(),
        db=FakeDb(enabled=False),
    )

    handle_tc_w0_cfg_007(runtime, _settle_flags_case())  # type: ignore[arg-type]

    post_calls = [call for call in runtime.api.calls if call["method"] == "POST"]
    assert [call["path"] for call in post_calls] == [
        "/commission/rules",
        "/commission/rules",
    ]
    payloads = [call["kwargs"]["json"] for call in post_calls]
    assert [payload["rule_name"] for payload in payloads] == [
        "普通申请款到后提成-RUN-W0-COM-FLAG",
        "普通申请强制可结算-RUN-W0-COM-FLAG",
    ]
    assert [(payload["wait_pay"], payload["force_settle"]) for payload in payloads] == [
        (True, False),
        (True, True),
    ]
    assert all(payload["enabled"] is True for payload in payloads)

    get_calls = [call for call in runtime.api.calls if call["method"] == "GET"]
    assert [call["kwargs"]["params"]["q"] for call in get_calls] == [
        "普通申请款到后提成-RUN-W0-COM-FLAG",
        "普通申请强制可结算-RUN-W0-COM-FLAG",
    ]
    assert runtime.db.rows == []


def test_tc_w0_cfg_006_handler_creates_split_commissions() -> None:
    runtime = FakeRuntime(
        username="admin",
        password="dummy-password",
        run_id="RUN-W0-COM-SPLIT",
        api=FakeApi(),
        db=FakeDb(enabled=False),
    )

    handle_tc_w0_cfg_006(runtime, _split_case())  # type: ignore[arg-type]

    post_paths = [
        call["path"] for call in runtime.api.calls if call["method"] == "POST"
    ]
    assert post_paths == [
        "/admin/users",
        "/admin/users",
        "/clients",
        "/cases",
        "/commission/rules",
        "/bills/manual",
    ]
    case_payload = [
        call["kwargs"]["json"]
        for call in runtime.api.calls
        if call["method"] == "POST" and call["path"] == "/cases"
    ][0]
    assert case_payload["client_id"] == "client-1"
    assert case_payload["primary_agent_id"] == "user-1"
    assert case_payload["agent_splits"] == [
        {"agent_id": "user-1", "role": "PRIMARY", "share_ratio": "70.0000"},
        {"agent_id": "user-2", "role": "SECONDARY", "share_ratio": "30.0000"},
    ]

    assert [
        (item["agent_id"], item["base_fee"]) for item in runtime.api.commissions
    ] == [
        ("user-1", "700.00"),
        ("user-2", "300.00"),
    ]
    assert [
        (item["s1_amount"], item["s2_amount"]) for item in runtime.api.commissions
    ] == [
        ("210.00", "140.00"),
        ("90.00", "60.00"),
    ]
    assert runtime.db.rows == []


def test_tc_w0_cfg_006_handler_reuses_existing_config_client() -> None:
    runtime = FakeRuntime(
        username="admin",
        password="dummy-password",
        run_id="RUN-W0-COM-SPLIT-REUSE",
        api=FakeApi(),
        db=FakeDb(enabled=False),
    )
    runtime.api.clients.append(
        {
            "id": "client-existing",
            "client_code": "CL-CFG-RUN-W0-COM-SPLIT-REUSE",
            "name_cn": "配置测试客户-RUN-W0-COM-SPLIT-REUSE",
            "client_type": "DIRECT",
            "default_currency": "CNY",
            "is_active": True,
        }
    )

    handle_tc_w0_cfg_006(runtime, _split_case())  # type: ignore[arg-type]

    post_paths = [
        call["path"] for call in runtime.api.calls if call["method"] == "POST"
    ]
    assert "/clients" not in post_paths
    case_payload = [
        call["kwargs"]["json"]
        for call in runtime.api.calls
        if call["method"] == "POST" and call["path"] == "/cases"
    ][0]
    assert case_payload["client_id"] == "client-existing"


def test_tc_w0_cfg_006_handler_reuses_rule_disabled_by_cfg_005() -> None:
    runtime = FakeRuntime(
        username="admin",
        password="dummy-password",
        run_id="RUN-W0-COM-RULE-REUSE",
        api=FakeApi(),
        db=FakeDb(enabled=False),
    )

    handle_tc_w0_cfg_005(runtime, _case())  # type: ignore[arg-type]
    rule_post_count = len(
        [
            call
            for call in runtime.api.calls
            if call["method"] == "POST" and call["path"] == "/commission/rules"
        ]
    )
    assert runtime.api.rules[0]["enabled"] is False

    handle_tc_w0_cfg_006(runtime, _split_case())  # type: ignore[arg-type]

    rule_post_paths = [
        call["path"]
        for call in runtime.api.calls
        if call["method"] == "POST" and call["path"] == "/commission/rules"
    ]
    assert len(rule_post_paths) == rule_post_count
    rule_puts = [
        call
        for call in runtime.api.calls
        if call["method"] == "PUT" and call["path"] == "/commission/rules/1"
    ]
    assert rule_puts[-1]["kwargs"]["json"] == {"enabled": True}
    assert runtime.api.rules[0]["enabled"] is True
    assert len(runtime.api.commissions) == 2


def test_tc_w0_cfg_005_handler_runs_db_asserts_when_enabled() -> None:
    runtime = FakeRuntime(
        username="admin",
        password="dummy-password",
        run_id="RUN-W0-COM-DB",
        api=FakeApi(),
        db=FakeDb(enabled=True),
    )

    handle_tc_w0_cfg_005(runtime, _case())  # type: ignore[arg-type]

    assert runtime.db.rows == [
        (
            "t_commission_rule",
            {"rule_name": "普通申请服务费提成-RUN-W0-COM-DB", "enabled": False},
        )
    ]


def test_tc_w0_cfg_006_handler_runs_db_asserts_when_enabled() -> None:
    runtime = FakeRuntime(
        username="admin",
        password="dummy-password",
        run_id="RUN-W0-COM-SPLIT-DB",
        api=FakeApi(),
        db=FakeDb(enabled=True),
    )

    handle_tc_w0_cfg_006(runtime, _split_case())  # type: ignore[arg-type]

    assert runtime.db.rows == [
        ("t_case", {"case_no": "CASE-CFG-RUN-W0-COM-SPLIT-DB-001"}),
        ("t_commission", {"case_id": "case-1", "agent_id": "user-1"}),
        ("t_commission", {"case_id": "case-1", "agent_id": "user-2"}),
    ]


def test_tc_w0_cfg_007_handler_runs_db_asserts_when_enabled() -> None:
    runtime = FakeRuntime(
        username="admin",
        password="dummy-password",
        run_id="RUN-W0-COM-FLAG-DB",
        api=FakeApi(),
        db=FakeDb(enabled=True),
    )

    handle_tc_w0_cfg_007(runtime, _settle_flags_case())  # type: ignore[arg-type]

    assert runtime.db.rows == [
        (
            "t_commission_rule",
            {
                "rule_name": "普通申请款到后提成-RUN-W0-COM-FLAG-DB",
                "wait_pay": True,
                "force_settle": False,
                "enabled": True,
            },
        ),
        (
            "t_commission_rule",
            {
                "rule_name": "普通申请强制可结算-RUN-W0-COM-FLAG-DB",
                "wait_pay": True,
                "force_settle": True,
                "enabled": True,
            },
        ),
    ]
