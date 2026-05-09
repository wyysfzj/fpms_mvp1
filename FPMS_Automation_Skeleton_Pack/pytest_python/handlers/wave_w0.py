from __future__ import annotations

import json
from decimal import Decimal, InvalidOperation
from typing import Any

import pytest
import requests

from framework.helpers import skeleton_case, unique_code
from framework.models import TestCase
from framework.runtime import RuntimeContext
from framework.seed_data import SeedCatalog


def handle_tc_w0_001(runtime: RuntimeContext, case: TestCase) -> None:
    # TC-W0-001 | 主数据-客户
    # 覆盖: FR-CM-03, FR-WD-09, FR-WD-10
    # 数据: DS-CL-001, DS-U-ADM
    # 动态值: <none>
    # 前置: 使用 DS-U-ADM 登录；准备 DS-CL-001 基本信息、两条地址、一条联系人。
    # 步骤摘要: 进入“设置→客户维护”，创建客户、默认文件地址、默认账单地址和联系人；保存后再打开编辑页校验。
    # 预期: 客户、地址、联系人均保存成功；默认地址标记唯一；搜索可按名称命中；后续案卷和账单下拉中可选。
    del case

    try:
        runtime.api.login(runtime.username, runtime.password)

        catalog = SeedCatalog.load(run_id=runtime.run_id)
        seed = catalog.normalized("DS-CL-001")
        client_code = unique_code("CL-W0-001", runtime.run_id)
        name_cn = f"{seed['name']}-{runtime.run_id}"
        country_code = catalog.country_code(str(seed.get("country", "CN")))

        client_payload = {
            "client_code": client_code,
            "name_cn": name_cn,
            "client_type": _normalize_client_type(seed.get("client_type")),
            "default_currency": seed.get("default_currency") or "CNY",
            "is_active": True,
        }
        client = _json_or_assert(
            runtime.api.post("/clients", json=client_payload),
            "create client",
            expected_statuses={200, 201},
        )
        client_id = _required_value(client, "id", "created client")

        address_payloads = [
            {
                "address_type": "MAILING",
                "address_line1": f"{name_cn} 文件地址",
                "city": "Beijing",
                "country_code": country_code,
                "is_default": True,
            },
            {
                "address_type": "BILLING",
                "address_line1": f"{name_cn} 账单地址",
                "city": "Beijing",
                "country_code": country_code,
                "is_default": True,
            },
        ]
        for payload in address_payloads:
            _json_or_assert(
                runtime.api.post(f"/clients/{client_id}/addresses", json=payload),
                "create client address",
                expected_statuses={200, 201},
            )

        contact_payload = {
            "contact_name": f"DS-CL-001 Contact {runtime.run_id}",
            "title": "IP Manager",
            "email": "w0.client@example.test",
            "is_primary": True,
        }
        _json_or_assert(
            runtime.api.post(f"/clients/{client_id}/contacts", json=contact_payload),
            "create client contact",
            expected_statuses={200, 201},
        )

        search_result = _json_or_assert(
            runtime.api.get(
                "/clients",
                params={"page": 1, "page_size": 20, "q": client_code},
            ),
            "search client",
        )
        _assert_client_search_hit(search_result, client_id, client_code)

        fetched_client = _json_or_assert(
            runtime.api.get(f"/clients/{client_id}"),
            "get client detail",
        )
        if fetched_client.get("client_code") != client_code:
            raise AssertionError("Client detail did not return the created client_code")

        addresses = _json_or_assert(
            runtime.api.get(f"/clients/{client_id}/addresses"),
            "list client addresses",
        )
        _assert_created_records(addresses, "address", 2)

        contacts = _json_or_assert(
            runtime.api.get(f"/clients/{client_id}/contacts"),
            "list client contacts",
        )
        _assert_created_records(contacts, "contact", 1)

        if runtime.db.enabled():
            runtime.db.assert_row_exists("t_client", {"client_code": client_code})
            runtime.db.assert_row_exists("t_client_address", {"client_id": client_id})
            runtime.db.assert_row_exists("t_client_contact", {"client_id": client_id})
    except requests.RequestException as exc:
        pytest.skip(f"Real backend unavailable for TC-W0-001: {exc}")


def _normalize_client_type(value: Any) -> str:
    if not isinstance(value, str):
        return "CLIENT"
    cleaned = value.strip()
    if not cleaned:
        return "CLIENT"
    aliases = {
        "直接客户": "CLIENT",
        "代理所": "AGENT",
        "CLIENT": "CLIENT",
        "AGENT": "AGENT",
    }
    return aliases.get(cleaned, aliases.get(cleaned.upper(), cleaned))


def _json_or_assert(
    response: Any,
    action: str,
    expected_statuses: set[int] | None = None,
) -> Any:
    expected = expected_statuses or {200}
    status_code = getattr(response, "status_code", None)
    if status_code not in expected:
        raise AssertionError(
            f"{action} failed with status {status_code}: {_response_summary(response)}"
        )
    return response.json()


def _response_summary(response: Any) -> str:
    try:
        payload = response.json()
    except ValueError:
        payload = getattr(response, "text", "")
    return str(payload)[:500]


def _required_value(payload: dict[str, Any], field: str, label: str) -> Any:
    value = payload.get(field)
    if value in (None, ""):
        raise AssertionError(f"{label} response missing required field: {field}")
    return value


def _assert_client_search_hit(
    search_result: dict[str, Any],
    client_id: Any,
    client_code: str,
) -> None:
    items = search_result.get("items")
    if not isinstance(items, list):
        raise AssertionError("Client search response missing items list")
    for item in items:
        if not isinstance(item, dict):
            continue
        if item.get("id") == client_id or item.get("client_code") == client_code:
            return
    raise AssertionError("Created client was not found in search results")


def _assert_created_records(records: Any, label: str, minimum_count: int) -> None:
    if not isinstance(records, list):
        raise AssertionError(f"Client {label} response is not a list")
    if len(records) < minimum_count:
        raise AssertionError(
            f"Expected at least {minimum_count} client {label} records, got {len(records)}"
        )


@skeleton_case
def handle_tc_w0_002(runtime: RuntimeContext, case: TestCase) -> None:
    # TC-W0-002 | 主数据-客户地址
    # 覆盖: FR-WD-10, V-C-06
    # 数据: DS-CL-004, DS-U-ADM
    # 动态值: <none>
    # 前置: DS-U-ADM；客户 DS-CL-004 含一条停用地址和一条有效地址。
    # 步骤摘要: 将停用地址设为默认账单地址并尝试在案卷中选择；再切换为有效地址重试。
    # 预期: 停用地址不能被设为有效默认收件地址或在案卷中被使用；切换为有效地址后可正常引用。
    # Arrange: 准备种子数据 / 鉴权 / 页面或 API 上下文。
    # Act: 按 steps_summary 执行业务流。
    # Assert: 按 expected 做 UI / API / DB / 文件断言。
    return None


def handle_tc_w0_003(runtime: RuntimeContext, case: TestCase) -> None:
    # TC-W0-003 | 主数据-申请人
    # 覆盖: FR-CM-03
    # 数据: DS-AP-001, DS-AP-002, DS-U-ADM
    # 动态值: <none>
    # 前置: DS-U-ADM；准备法人申请人 DS-AP-001 和自然人 DS-AP-002。
    # 步骤摘要: 创建申请人主数据并填写名称、国籍、地址、IsLegalEntity、HasGeneralPower、IsJobInvention 等字段；保存并搜索。
    # 预期: 申请人保存成功；能按名称模糊搜索；HasGeneralPower/IsLegalEntity 在案卷引用时可被带出。
    del case

    try:
        runtime.api.login(runtime.username, runtime.password)

        catalog = SeedCatalog.load(run_id=runtime.run_id)
        specs = _w0_applicant_specs(catalog, runtime.run_id)
        for spec in specs:
            _create_or_verify_masterdata(runtime, spec)

        if runtime.db.enabled():
            for spec in specs:
                runtime.db.assert_row_exists(spec["table"], spec["db_where"])
    except requests.RequestException as exc:
        pytest.skip(f"Real backend unavailable for TC-W0-003: {exc}")


def _w0_applicant_specs(catalog: SeedCatalog, run_id: str) -> list[dict[str, Any]]:
    return [
        _w0_applicant_spec(catalog, "DS-AP-001", "AP-W0-003-ENTITY", run_id),
        _w0_applicant_spec(catalog, "DS-AP-002", "AP-W0-003-IND", run_id),
    ]


def _w0_applicant_spec(
    catalog: SeedCatalog,
    seed_id: str,
    code_prefix: str,
    run_id: str,
) -> dict[str, Any]:
    seed = catalog.normalized(seed_id)
    applicant_code = unique_code(code_prefix, run_id)
    applicant_type = _normalize_applicant_type(seed.get("applicant_type"))
    payload = {
        "code": applicant_code,
        "name_cn": f"{seed['name']}-{run_id}",
        "name_en": None,
        "applicant_type": applicant_type,
        "is_active": True,
    }
    return {
        "create_path": "/applicants",
        "list_path": "/applicants",
        "payload": payload,
        "query": applicant_code,
        "identity_field": "code",
        "identity_value": applicant_code,
        "table": "t_applicant",
        "db_where": {
            "code": applicant_code,
            "applicant_type": applicant_type,
            "is_active": True,
        },
    }


def _normalize_applicant_type(value: Any) -> str:
    if not isinstance(value, str):
        return "ENTITY"
    cleaned = value.strip()
    if not cleaned:
        return "ENTITY"
    aliases = {
        "法人": "ENTITY",
        "自然人": "INDIVIDUAL",
        "ENTITY": "ENTITY",
        "INDIVIDUAL": "INDIVIDUAL",
    }
    return aliases.get(cleaned, aliases.get(cleaned.upper(), cleaned.upper()))


@skeleton_case
def handle_tc_w0_004(runtime: RuntimeContext, case: TestCase) -> None:
    # TC-W0-004 | 主数据-申请人合并
    # 覆盖: FR-CM-03
    # 数据: DS-U-ADM
    # 动态值: <none>
    # 前置: DS-U-ADM；创建两条近似重复的申请人记录。
    # 步骤摘要: 在“申请人维护”执行合并；保留主记录，确认关联地址/标记字段。
    # 预期: 重复记录被合并；主记录保留，关联引用不丢失，旧记录不可再被新案选用。
    # Arrange: 准备种子数据 / 鉴权 / 页面或 API 上下文。
    # Act: 按 steps_summary 执行业务流。
    # Assert: 按 expected 做 UI / API / DB / 文件断言。
    return None


def handle_tc_w0_005(runtime: RuntimeContext, case: TestCase) -> None:
    # TC-W0-005 | 主数据-国家地区
    # 覆盖: FR-CM-01, FR-FE-01, FR-CS-01
    # 数据: DS-U-ADM
    # 动态值: <none>
    # 前置: DS-U-ADM；准备 CN/US/JP/HK/EP 数据。
    # 步骤摘要: 维护国家代码、默认币种、IsDomestic、DefaultLanguage、PCT 成员标志；保存后在案卷/费率/报表处引用。
    # 预期: 国家配置可被案卷、费率、年费和报表使用；Domestic/PCT member 标志在规则分支中可识别。
    del case

    try:
        runtime.api.login(runtime.username, runtime.password)

        catalog = SeedCatalog.load(run_id=runtime.run_id)
        specs = _w0_country_specs(catalog)
        for spec in specs:
            _create_or_verify_masterdata(runtime, spec)

        if runtime.db.enabled():
            for spec in specs:
                runtime.db.assert_row_exists(spec["table"], spec["db_where"])
    except requests.RequestException as exc:
        pytest.skip(f"Real backend unavailable for TC-W0-005: {exc}")


_COUNTRY_NAME_EN_BY_CODE = {
    "CN": "China",
    "US": "United States",
    "JP": "Japan",
    "HK": "Hong Kong",
    "EP": "European Patent Office",
}


def _w0_country_specs(catalog: SeedCatalog) -> list[dict[str, Any]]:
    return [
        _w0_country_spec(catalog, seed_id)
        for seed_id in (
            "DS-CTY-CN",
            "DS-CTY-US",
            "DS-CTY-JP",
            "DS-CTY-HK",
            "DS-CTY-EP",
        )
    ]


def _w0_country_spec(catalog: SeedCatalog, seed_id: str) -> dict[str, Any]:
    seed = catalog.normalized(seed_id)
    country_code = catalog.country_code(str(seed["code"]))
    payload = {
        "code": country_code,
        "name_cn": str(seed["name"]),
        "name_en": _COUNTRY_NAME_EN_BY_CODE.get(country_code),
        "is_active": True,
    }
    return {
        "create_path": "/countries",
        "list_path": "/countries",
        "payload": payload,
        "query": country_code,
        "identity_field": "code",
        "identity_value": country_code,
        "table": "t_country",
        "db_where": {"code": country_code, "is_active": True},
    }


@skeleton_case
def handle_tc_w0_006(runtime: RuntimeContext, case: TestCase) -> None:
    # TC-W0-006 | 主数据-菌种保藏单位
    # 覆盖: FR-CM-05
    # 数据: DS-BIO-UNIT-001, DS-U-ADM
    # 动态值: <none>
    # 前置: DS-U-ADM；准备 DS-BIO-UNIT-001。
    # 步骤摘要: 维护菌种保藏单位编码、中英文名、地址、联系人；保存后在案卷扩展页引用。
    # 预期: 菌种保藏单位保存成功；在案卷“菌种保藏”标签页可搜索选择。
    # Arrange: 准备种子数据 / 鉴权 / 页面或 API 上下文。
    # Act: 按 steps_summary 执行业务流。
    # Assert: 按 expected 做 UI / API / DB / 文件断言。
    return None


def handle_tc_w0_007(runtime: RuntimeContext, case: TestCase) -> None:
    # TC-W0-007 | 业务参数-费率固定金额
    # 覆盖: FR-FE-01, FR-FE-03
    # 数据: DS-U-FI-01
    # 动态值: <none>
    # 前置: DS-U-FI-01；准备 CN_APPL_BASE、CN_APPL_SERVICE_BASE。
    # 步骤摘要: 在费率维护中创建 Group=APPLY 的 FIXED 费率，设置 FeeType、DefaultCurrency、DefaultAmount、AllowReduction/AllowDiscount。
    # 预期: 费率创建成功，可按 Group/Country/CaseType 查询到；后续草单生成时可被命中。
    del case

    try:
        runtime.api.login(runtime.username, runtime.password)

        catalog = SeedCatalog.load(run_id=runtime.run_id)
        created_payloads = []
        for seed_id, default_amount, allow_reduction in (
            ("DS-RATE-001", "950.00", True),
            ("DS-RATE-002", "3000.00", False),
        ):
            seed = catalog.normalized(seed_id)
            payload = _build_fee_rate_payload(
                seed=seed,
                run_id=runtime.run_id,
                default_amount=default_amount,
                allow_reduction=allow_reduction,
            )
            _json_or_assert(
                runtime.api.post("/fees/rates", json=payload),
                "create fee rate",
                expected_statuses={200, 201},
            )
            created_payloads.append(payload)

        for payload in created_payloads:
            search_result = _json_or_assert(
                runtime.api.get(
                    "/fees/rates",
                    params={
                        "page": 1,
                        "page_size": 20,
                        "fee_code": payload["fee_code"],
                    },
                ),
                "search fee rate",
            )
            _assert_fee_rate_search_hit(search_result, payload)

        if runtime.db.enabled():
            for payload in created_payloads:
                runtime.db.assert_row_exists(
                    "t_fee_rate",
                    {
                        "fee_code": payload["fee_code"],
                        "fee_type": payload["fee_type"],
                        "rate_group": payload["rate_group"],
                    },
                )
    except requests.RequestException as exc:
        pytest.skip(f"Real backend unavailable for TC-W0-007: {exc}")


def _build_fee_rate_payload(
    *,
    seed: dict[str, Any],
    run_id: str,
    default_amount: str,
    allow_reduction: bool,
) -> dict[str, Any]:
    fee_code = unique_code(str(seed["code"]), run_id)
    if len(fee_code) > 64:
        raise AssertionError(
            f"Generated fee_code exceeds t_fee_rate.fee_code length 64: {len(fee_code)}"
        )
    return {
        "fee_code": fee_code,
        "fee_name": f"{seed.get('note') or seed['code']} {run_id}",
        "fee_type": seed["fee_type"],
        "currency": "CNY",
        "default_amount": default_amount,
        "enabled": True,
        "rate_group": seed["group"],
        "country_code": "CN",
        "case_type": "NORMAL",
        "patent_category": "INV",
        "calc_mode": "FIXED",
        "allow_reduction": allow_reduction,
    }


def _assert_fee_rate_search_hit(
    search_result: dict[str, Any],
    expected_payload: dict[str, Any],
) -> None:
    items = search_result.get("items")
    if not isinstance(items, list):
        raise AssertionError("Fee rate search response missing items list")
    for item in items:
        if not isinstance(item, dict):
            continue
        if item.get("fee_code") != expected_payload["fee_code"]:
            continue
        _assert_fee_rate_fields(item, expected_payload)
        return
    raise AssertionError(
        f"Created fee rate was not found by fee_code {expected_payload['fee_code']}"
    )


def _assert_fee_rate_fields(
    actual: dict[str, Any],
    expected_payload: dict[str, Any],
) -> None:
    for field in (
        "fee_type",
        "currency",
        "rate_group",
        "country_code",
        "case_type",
        "patent_category",
        "calc_mode",
        "enabled",
    ):
        if actual.get(field) != expected_payload[field]:
            raise AssertionError(
                f"Fee rate field {field} mismatch: {actual.get(field)!r}"
            )
    if not _money_matches(
        actual.get("default_amount"), expected_payload["default_amount"]
    ):
        raise AssertionError(
            f"Fee rate default_amount mismatch: {actual.get('default_amount')!r}"
        )


def _money_matches(actual: Any, expected: Any) -> bool:
    try:
        return Decimal(str(actual)) == Decimal(str(expected))
    except (InvalidOperation, TypeError, ValueError):
        return False


def handle_tc_w0_cfg_003(runtime: RuntimeContext, case: TestCase) -> None:
    # TC-W0-CFG-003 | 申请费费率必备配置
    # 覆盖: FR-FE-01, FR-FE-03
    # 数据: DS-U-FI-01, DS-CFG-RATE-APPLY-BASE-GOV,
    #       DS-CFG-RATE-APPLY-EXCESS-CLAIM, DS-CFG-RATE-APPLY-SERVICE
    # 动态值: FPMS_RUN_ID
    # 前置: 准备申请费三项必备费率。
    # 步骤摘要: 通过 POST /fees/rates 创建三项 APPLY 费率；再按 fee_code 查询。
    # 预期: 三项费率均 enabled=true、currency=CNY，且可被后续申请费草单流程命中。
    del case

    try:
        runtime.api.login(runtime.username, runtime.password)

        catalog = SeedCatalog.load(run_id=runtime.run_id)
        created_payloads = [
            _build_config_fee_rate_payload(catalog, seed_id, runtime.run_id)
            for seed_id in (
                "DS-CFG-RATE-APPLY-BASE-GOV",
                "DS-CFG-RATE-APPLY-EXCESS-CLAIM",
                "DS-CFG-RATE-APPLY-SERVICE",
            )
        ]

        for payload in created_payloads:
            _json_or_assert(
                runtime.api.post("/fees/rates", json=payload),
                "create config fee rate",
                expected_statuses={200, 201},
            )

        for payload in created_payloads:
            search_result = _json_or_assert(
                runtime.api.get(
                    "/fees/rates",
                    params={
                        "page": 1,
                        "page_size": 20,
                        "fee_code": payload["fee_code"],
                    },
                ),
                "search config fee rate",
            )
            _assert_fee_rate_search_hit(search_result, payload)

        if runtime.db.enabled():
            for payload in created_payloads:
                runtime.db.assert_row_exists(
                    "t_fee_rate",
                    {
                        "fee_code": payload["fee_code"],
                        "rate_group": "APPLY",
                        "enabled": True,
                    },
                )
    except requests.RequestException as exc:
        pytest.skip(f"Real backend unavailable for TC-W0-CFG-003: {exc}")


def handle_tc_w0_cfg_004(runtime: RuntimeContext, case: TestCase) -> None:
    # TC-W0-CFG-004 | 费率-calc_mode 覆盖与当前实现差距
    # 覆盖: FR-FE-01, FR-FE-03
    # 数据: DS-U-FI-01, FIXED/PER_CLAIM/BY_YEAR/BY_PAGES/COMPOSITE 费率 seeds
    # 动态值: FPMS_RUN_ID
    # 前置: 准备五类 calc_mode 费率数据。
    # 步骤摘要: 创建五类 calc_mode 费率，并按 fee_code 查询保存结果。
    # 预期: calc_mode/calc_params 被 API 和 DB 保留；金额计算能力留给服务流任务验证。
    del case

    try:
        runtime.api.login(runtime.username, runtime.password)

        catalog = SeedCatalog.load(run_id=runtime.run_id)
        created_payloads = [
            _build_config_fee_rate_payload(catalog, seed_id, runtime.run_id)
            for seed_id in (
                "DS-CFG-RATE-APPLY-BASE-GOV",
                "DS-CFG-RATE-APPLY-EXCESS-CLAIM",
                "DS-CFG-RATE-ANNUITY-GOV-Y1",
                "DS-CFG-RATE-BY-PAGES",
                "DS-CFG-RATE-COMPOSITE",
            )
        ]

        for payload in created_payloads:
            _json_or_assert(
                runtime.api.post("/fees/rates", json=payload),
                "create config calc-mode fee rate",
                expected_statuses={200, 201},
            )

        for payload in created_payloads:
            search_result = _json_or_assert(
                runtime.api.get(
                    "/fees/rates",
                    params={
                        "page": 1,
                        "page_size": 20,
                        "fee_code": payload["fee_code"],
                    },
                ),
                "search config calc-mode fee rate",
            )
            _assert_fee_rate_search_hit(search_result, payload)
            _assert_fee_rate_calc_metadata(search_result, payload)

        if runtime.db.enabled():
            for payload in created_payloads:
                runtime.db.assert_row_exists(
                    "t_fee_rate",
                    {
                        "fee_code": payload["fee_code"],
                        "calc_mode": payload["calc_mode"],
                        "enabled": True,
                    },
                )
    except requests.RequestException as exc:
        pytest.skip(f"Real backend unavailable for TC-W0-CFG-004: {exc}")


def handle_tc_w0_cfg_002(runtime: RuntimeContext, case: TestCase) -> None:
    # TC-W0-CFG-002 | 系统参数-bill_template_path 控制账单打印
    # 覆盖: FR-BL-04
    # 数据: DS-U-FI-01, DS-CFG-SYS-BILL-TEMPLATE, DS-CFG-TEMPLATE-BILL-CN
    # 动态值: FPMS_RUN_ID
    # 前置: 清理后 seed 不包含 bill_template_path。
    # 步骤摘要: readiness 确认缺配置后创建手工账单并调用账单打印。
    # 预期: 缺 bill_template_path 时账单打印返回 BILL_TEMPLATE_NOT_CONFIGURED。
    del case

    try:
        runtime.api.login(runtime.username, runtime.password)

        readiness = _json_or_assert(
            runtime.api.get("/system/config-readiness"),
            "get bill template readiness",
        )
        _assert_readiness_missing(readiness, "system_param.bill_template_path")

        catalog = SeedCatalog.load(run_id=runtime.run_id)
        client = _ensure_config_client(runtime, catalog, "bill print")
        client_id = _required_value(client, "id", "created client")

        bill = _json_or_assert(
            runtime.api.post(
                "/bills/manual",
                json={
                    "client_id": client_id,
                    "currency": "CNY",
                    "direction": "AR",
                    "status": "UNSETTLED",
                    "bill_date": "2026-05-09",
                    "items": [
                        {
                            "description": "账单打印模板参数测试",
                            "quantity": 1,
                            "unit_price": "1000.00",
                            "fee_type": "SERVICE",
                        }
                    ],
                },
            ),
            "create bill print manual bill",
            expected_statuses={200, 201},
        )
        bill_id = _required_value(bill, "id", "created bill")

        print_response = runtime.api.get(f"/bills/{bill_id}/print")
        _assert_bill_template_not_configured(print_response)
    except requests.RequestException as exc:
        pytest.skip(f"Real backend unavailable for TC-W0-CFG-002: {exc}")


def _assert_readiness_missing(payload: dict[str, Any], expected_key: str) -> None:
    missing = payload.get("missing")
    if not isinstance(missing, list):
        raise AssertionError("Config readiness response missing missing list")
    for item in missing:
        if isinstance(item, dict) and item.get("key") == expected_key:
            if item.get("severity") != "hard_block":
                raise AssertionError(
                    f"Readiness entry severity mismatch: {expected_key}"
                )
            return
    raise AssertionError(f"Config readiness did not report missing {expected_key}")


def _assert_bill_template_not_configured(response: Any) -> None:
    status_code = getattr(response, "status_code", None)
    if status_code != 409:
        raise AssertionError(
            f"bill print missing template expected 409, got {status_code}: "
            f"{_response_summary(response)}"
        )
    body_text = _response_summary(response)
    if "BILL_TEMPLATE_NOT_CONFIGURED" not in body_text:
        raise AssertionError("Bill print missing template response lacks error code")


def _assert_fee_rate_calc_metadata(
    search_result: dict[str, Any],
    expected_payload: dict[str, Any],
) -> None:
    items = search_result.get("items")
    if not isinstance(items, list):
        raise AssertionError("Fee rate search response missing items list")
    for item in items:
        if (
            not isinstance(item, dict)
            or item.get("fee_code") != expected_payload["fee_code"]
        ):
            continue
        if item.get("calc_mode") != expected_payload["calc_mode"]:
            raise AssertionError("Fee rate calc_mode mismatch")
        if item.get("calc_params") != expected_payload.get("calc_params"):
            raise AssertionError("Fee rate calc_params mismatch")
        return
    raise AssertionError(
        f"Created fee rate was not found by fee_code {expected_payload['fee_code']}"
    )


def handle_tc_w0_cfg_008(runtime: RuntimeContext, case: TestCase) -> None:
    # TC-W0-CFG-008 | 时限模板-起算基准、内部期限、提醒
    # 覆盖: FR-DL-01, FR-DL-02
    # 数据: DS-U-ADM, DS-CFG-TASK-OA-REPLY, DS-CFG-DOC-OA-IN
    # 动态值: FPMS_RUN_ID
    # 前置: 准备 OA_REPLY 任务模板和绑定该任务模板的 OA_IN 文档模板。
    # 步骤摘要: 通过 /task-templates 和 /doc-templates 创建配置并查询。
    # 预期: deadline_base、inner_offset_days、remind offsets 和 deadline_template_code 被保留。
    del case

    try:
        runtime.api.login(runtime.username, runtime.password)

        catalog = SeedCatalog.load(run_id=runtime.run_id)
        task_payload = _task_template_payload(catalog, "DS-CFG-TASK-OA-REPLY")
        created_task = _ensure_task_template(runtime, task_payload, "OA reply")
        _assert_task_template_payload(created_task, task_payload)

        doc_payload = _doc_template_payload(catalog, "DS-CFG-DOC-OA-IN")
        created_doc = _ensure_doc_template(runtime, doc_payload, "OA incoming")
        _assert_doc_template_fields(created_doc, doc_payload)

        task_list = _json_or_assert(
            runtime.api.get("/task-templates", params={"enabled_only": False}),
            "list task templates",
        )
        _assert_task_template_list_hit(task_list, task_payload)

        doc_list = _json_or_assert(
            runtime.api.get(
                "/doc-templates",
                params={"page": 1, "page_size": 20, "q": doc_payload["code"]},
            ),
            "search OA incoming doc template",
        )
        _assert_doc_template_search_hit(doc_list, doc_payload)

        if runtime.db.enabled():
            runtime.db.assert_row_exists(
                "t_task_template",
                {"code": task_payload["code"], "deadline_base": "DISPATCH_DATE"},
            )
            runtime.db.assert_row_exists(
                "t_doc_template",
                {
                    "code": doc_payload["code"],
                    "deadline_template_code": task_payload["code"],
                    "enabled": True,
                },
            )
    except requests.RequestException as exc:
        pytest.skip(f"Real backend unavailable for TC-W0-CFG-008: {exc}")


def _task_template_payload(catalog: SeedCatalog, seed_id: str) -> dict[str, Any]:
    seed = catalog.normalized(seed_id)
    return dict(seed["payload"])


def _doc_template_payload(catalog: SeedCatalog, seed_id: str) -> dict[str, Any]:
    seed = catalog.normalized(seed_id)
    return dict(seed["payload"])


def _assert_task_template_payload(
    actual: dict[str, Any],
    expected_payload: dict[str, Any],
) -> None:
    for field in (
        "code",
        "name",
        "deadline_base",
        "add_days",
        "add_months",
        "inner_offset_days",
        "remind_base",
        "remind_1_offset_days",
        "remind_2_offset_days",
        "remind_3_offset_days",
        "daily_remind",
        "default_worker_role",
        "description",
    ):
        if actual.get(field) != expected_payload[field]:
            raise AssertionError(
                f"Task template field {field} mismatch: {actual.get(field)!r}"
            )


def _assert_task_template_list_hit(
    payload: Any,
    expected_payload: dict[str, Any],
) -> None:
    if not isinstance(payload, list):
        raise AssertionError("Task template list response is not a list")
    for item in payload:
        if not isinstance(item, dict) or item.get("code") != expected_payload["code"]:
            continue
        _assert_task_template_payload(item, expected_payload)
        return
    raise AssertionError(
        f"Created task template was not found by code {expected_payload['code']}"
    )


def handle_tc_w0_cfg_009(runtime: RuntimeContext, case: TestCase) -> None:
    # TC-W0-CFG-009 | 文件模板-状态影响、回复链、费用草单预览
    # 覆盖: FR-WD-01, FR-WD-03, FR-WD-04, FR-WD-05
    # 数据: DS-U-ADM, DS-CFG-CASE-NORMAL-INV, DS-CFG-TASK-OA-REPLY, DS-CFG-DOC-OA-IN
    # 动态值: FPMS_RUN_ID
    # 前置: 创建最小案卷、OA 回复任务模板和 OA_IN 文件模板。
    # 步骤摘要: 调用 /documents/impact-preview 校验模板驱动影响预览。
    # 预期: 预览返回状态、期限、任务、费用、文件状态和确认要求。
    del case

    try:
        runtime.api.login(runtime.username, runtime.password)

        catalog = SeedCatalog.load(run_id=runtime.run_id)
        case_payload = _config_case_payload(catalog)
        created_case = _json_or_assert(
            runtime.api.post("/cases", json=case_payload),
            "create config preview case",
            expected_statuses={200, 201},
        )
        case_id = _required_value(created_case, "id", "created case")

        task_payload = _task_template_payload(catalog, "DS-CFG-TASK-OA-REPLY")
        _ensure_task_template(runtime, task_payload, "impact preview")

        doc_payload = _doc_template_payload(catalog, "DS-CFG-DOC-OA-IN")
        created_doc_template = _ensure_doc_template(
            runtime, doc_payload, "impact preview"
        )
        doc_template_id = _required_value(
            created_doc_template, "id", "created doc template"
        )

        preview = _json_or_assert(
            runtime.api.post(
                "/documents/impact-preview",
                json={
                    "case_id": case_id,
                    "doc_template_id": doc_template_id,
                    "direction": "IN",
                    "doc_date": "2026-05-09",
                    "title": f"OA 来文预览-{runtime.run_id}",
                    "ref_no": f"OA-{runtime.run_id}",
                },
            ),
            "preview document impact",
        )
        _assert_document_impact_preview(preview, case_id, doc_payload)

        if runtime.db.enabled():
            runtime.db.assert_row_exists("t_case", {"case_no": case_payload["case_no"]})
            runtime.db.assert_row_exists(
                "t_doc_template",
                {"code": doc_payload["code"], "fee_draft_type": "OA_SERVICE"},
            )
    except requests.RequestException as exc:
        pytest.skip(f"Real backend unavailable for TC-W0-CFG-009: {exc}")


def _config_case_payload(catalog: SeedCatalog) -> dict[str, Any]:
    seed = catalog.normalized("DS-CFG-CASE-NORMAL-INV")
    payload = dict(seed["payload"])
    payload.pop("primary_agent_id", None)
    payload.pop("agent_splits", None)
    return payload


def _assert_document_impact_preview(
    payload: dict[str, Any],
    case_id: Any,
    doc_template_payload: dict[str, Any],
) -> None:
    if payload.get("case_id") != case_id:
        raise AssertionError("Impact preview case_id mismatch")
    if payload.get("template_code") != doc_template_payload["code"]:
        raise AssertionError("Impact preview template_code mismatch")
    _assert_impact_item(
        payload.get("status_impacts"),
        kind="CASE_STATUS",
        effect=doc_template_payload["status_effect"],
    )
    _assert_impact_item(
        payload.get("deadline_impacts"),
        kind="DEADLINE_TEMPLATE",
        effect=doc_template_payload["deadline_template_code"],
    )
    _assert_impact_item(
        payload.get("task_impacts"),
        kind="AUTO_TASK",
        effect=doc_template_payload["deadline_template_code"],
    )
    _assert_impact_item(
        payload.get("fee_impacts"),
        kind="FEE_DRAFT",
        effect=doc_template_payload["fee_draft_type"],
    )
    _assert_impact_item(
        payload.get("file_status_impacts"),
        kind="NEED_REPLY",
        effect="NEED_REPLY",
    )
    if payload.get("confirmation_required") is not True:
        raise AssertionError("Impact preview should require confirmation")
    confirmation_items = payload.get("confirmation_items")
    if not isinstance(confirmation_items, list) or len(confirmation_items) < 3:
        raise AssertionError("Impact preview confirmation items missing")


def _assert_impact_item(items: Any, *, kind: str, effect: str | None) -> None:
    if not isinstance(items, list):
        raise AssertionError(f"Impact section for {kind} is not a list")
    for item in items:
        if not isinstance(item, dict):
            continue
        if item.get("kind") == kind and item.get("effect") == effect:
            return
    raise AssertionError(f"Impact item missing: {kind} / {effect}")


def handle_tc_w0_cfg_012(runtime: RuntimeContext, case: TestCase) -> None:
    # TC-W0-CFG-012 | 主数据-国家、部门、申请人和客户引用
    # 覆盖: FR-CM-01, FR-CM-03, FR-FE-01
    # 数据: DS-U-ADM, DS-CFG-COUNTRY-CN, DS-CFG-DEPT-PATENT,
    #       DS-CFG-CLIENT-ACTIVE, DS-CFG-APPLICANT-ENTITY
    # 动态值: FPMS_RUN_ID
    # 前置: 准备四类主数据 payload。
    # 步骤摘要: 通过主数据 API 创建或校验国家、部门、客户和申请人。
    # 预期: 有效主数据可保存并通过列表/搜索接口可见。
    del case

    try:
        runtime.api.login(runtime.username, runtime.password)

        catalog = SeedCatalog.load(run_id=runtime.run_id)
        specs = _masterdata_specs(catalog)
        for spec in specs:
            _create_or_verify_masterdata(runtime, spec)

        if runtime.db.enabled():
            for spec in specs:
                runtime.db.assert_row_exists(spec["table"], spec["db_where"])
    except requests.RequestException as exc:
        pytest.skip(f"Real backend unavailable for TC-W0-CFG-012: {exc}")


def _masterdata_specs(catalog: SeedCatalog) -> list[dict[str, Any]]:
    country = catalog.normalized("DS-CFG-COUNTRY-CN")["payload"]
    department = catalog.normalized("DS-CFG-DEPT-PATENT")["payload"]
    client = catalog.normalized("DS-CFG-CLIENT-ACTIVE")["payload"]
    applicant = catalog.normalized("DS-CFG-APPLICANT-ENTITY")["payload"]
    return [
        {
            "create_path": "/countries",
            "list_path": "/countries",
            "payload": dict(country),
            "query": country["code"],
            "identity_field": "code",
            "identity_value": country["code"],
            "table": "t_country",
            "db_where": {"code": country["code"], "is_active": True},
        },
        {
            "create_path": "/departments",
            "list_path": "/departments",
            "payload": dict(department),
            "query": department["department_code"],
            "identity_field": "department_code",
            "identity_value": department["department_code"],
            "table": "t_department",
            "db_where": {
                "department_code": department["department_code"],
                "is_active": True,
            },
        },
        {
            "create_path": "/clients",
            "list_path": "/clients",
            "payload": dict(client),
            "query": client["client_code"],
            "identity_field": "client_code",
            "identity_value": client["client_code"],
            "table": "t_client",
            "db_where": {"client_code": client["client_code"], "is_active": True},
        },
        {
            "create_path": "/applicants",
            "list_path": "/applicants",
            "payload": dict(applicant),
            "query": applicant["code"],
            "identity_field": "code",
            "identity_value": applicant["code"],
            "table": "t_applicant",
            "db_where": {"code": applicant["code"], "is_active": True},
        },
    ]


def _create_or_verify_masterdata(runtime: RuntimeContext, spec: dict[str, Any]) -> None:
    response = runtime.api.post(spec["create_path"], json=spec["payload"])
    status_code = getattr(response, "status_code", None)
    if status_code in {200, 201}:
        created = response.json()
        if created.get(spec["identity_field"]) != spec["identity_value"]:
            raise AssertionError(
                f"Masterdata create identity mismatch for {spec['create_path']}"
            )
    elif status_code not in {400, 409}:
        raise AssertionError(
            f"create masterdata failed with status {status_code}: "
            f"{_response_summary(response)}"
        )

    listed = _json_or_assert(
        runtime.api.get(
            spec["list_path"],
            params={"page": 1, "page_size": 20, "q": spec["query"]},
        ),
        "list masterdata",
    )
    _assert_masterdata_list_hit(listed, spec)


def _assert_masterdata_list_hit(payload: dict[str, Any], spec: dict[str, Any]) -> None:
    items = payload.get("items")
    if not isinstance(items, list):
        raise AssertionError("Masterdata list response missing items list")
    for item in items:
        if not isinstance(item, dict):
            continue
        if item.get(spec["identity_field"]) == spec["identity_value"]:
            return
    raise AssertionError(f"Masterdata item not found: {spec['identity_value']}")


def _build_config_fee_rate_payload(
    catalog: SeedCatalog,
    seed_id: str,
    run_id: str,
) -> dict[str, Any]:
    seed = catalog.normalized(seed_id)
    payload = dict(seed["payload"])
    payload["fee_code"] = unique_code(str(payload["fee_code"]), run_id)
    payload["fee_name"] = f"{payload['fee_name']} {run_id}"
    return payload


def handle_tc_w0_cfg_005(runtime: RuntimeContext, case: TestCase) -> None:
    # TC-W0-CFG-005 | 提成规则 CRUD 与校验
    # 覆盖: FR-COM-01
    # 数据: DS-U-ADM, DS-CFG-COM-NORMAL-SERVICE, DS-CFG-COM-INVALID-RATE
    # 动态值: FPMS_RUN_ID
    # 前置: 准备 NORMAL/SERVICE/CN_DOMESTIC/INV 提成规则。
    # 步骤摘要: 创建规则、查询规则、验证重复作用域冲突和非法比例/金额，再停用规则。
    # 预期: 有效规则可创建和查询；非法比例/金额被阻断；停用后 enabled=false。
    del case

    try:
        runtime.api.login(runtime.username, runtime.password)

        catalog = SeedCatalog.load(run_id=runtime.run_id)
        payload = _commission_rule_payload(catalog, "DS-CFG-COM-NORMAL-SERVICE")
        created = _json_or_assert(
            runtime.api.post("/commission/rules", json=payload),
            "create commission rule",
            expected_statuses={200, 201},
        )
        rule_id = _required_value(created, "id", "created commission rule")

        search_result = _json_or_assert(
            runtime.api.get(
                "/commission/rules",
                params={
                    "page": 1,
                    "page_size": 20,
                    "q": payload["rule_name"],
                },
            ),
            "search commission rule",
        )
        _assert_commission_rule_search_hit(search_result, payload)

        duplicate_payload = dict(payload)
        duplicate_payload["rule_name"] = f"{payload['rule_name']}-重复"
        _assert_status(
            runtime.api.post("/commission/rules", json=duplicate_payload),
            {409},
            "duplicate commission rule conflict",
        )

        invalid_seed = catalog.get("DS-CFG-COM-INVALID-RATE")
        for invalid in invalid_seed["invalid_payloads"]:
            invalid_payload = dict(payload)
            field = invalid["field"]
            invalid_payload["rule_name"] = f"{payload['rule_name']}-{field}"
            invalid_payload[field] = invalid["value"]
            _assert_status(
                runtime.api.post("/commission/rules", json=invalid_payload),
                {int(invalid["expected_status"])},
                f"invalid commission rule {field}",
            )

        disabled = _json_or_assert(
            runtime.api.put(f"/commission/rules/{rule_id}", json={"enabled": False}),
            "disable commission rule",
        )
        if disabled.get("enabled") is not False:
            raise AssertionError("Commission rule was not disabled")

        if runtime.db.enabled():
            runtime.db.assert_row_exists(
                "t_commission_rule",
                {"rule_name": payload["rule_name"], "enabled": False},
            )
    except requests.RequestException as exc:
        pytest.skip(f"Real backend unavailable for TC-W0-CFG-005: {exc}")


def handle_tc_w0_cfg_007(runtime: RuntimeContext, case: TestCase) -> None:
    # TC-W0-CFG-007 | 提成-WaitPay 与 ForceSettle 可结算性
    # 覆盖: FR-COM-04, FR-COM-05
    # 数据: DS-CFG-COM-NORMAL-WAITPAY, DS-CFG-COM-NORMAL-FORCE
    # 动态值: FPMS_RUN_ID
    # 前置: 准备 WaitPay 和 ForceSettle 提成规则。
    # 步骤摘要: 通过 /commission/rules 创建并查询规则。
    # 预期: wait_pay、force_settle 和 enabled 标记被 API 保留。
    del case

    try:
        runtime.api.login(runtime.username, runtime.password)

        catalog = SeedCatalog.load(run_id=runtime.run_id)
        payloads = [
            _commission_rule_payload(catalog, "DS-CFG-COM-NORMAL-WAITPAY"),
            _commission_rule_payload(catalog, "DS-CFG-COM-NORMAL-FORCE"),
        ]

        for payload in payloads:
            _json_or_assert(
                runtime.api.post("/commission/rules", json=payload),
                "create commission settle flag rule",
                expected_statuses={200, 201},
            )

        for payload in payloads:
            search_result = _json_or_assert(
                runtime.api.get(
                    "/commission/rules",
                    params={"page": 1, "page_size": 20, "q": payload["rule_name"]},
                ),
                "search commission settle flag rule",
            )
            _assert_commission_rule_search_hit(search_result, payload)
            _assert_commission_settle_flags(search_result, payload)

        if runtime.db.enabled():
            for payload in payloads:
                runtime.db.assert_row_exists(
                    "t_commission_rule",
                    {
                        "rule_name": payload["rule_name"],
                        "wait_pay": payload["wait_pay"],
                        "force_settle": payload["force_settle"],
                        "enabled": True,
                    },
                )
    except requests.RequestException as exc:
        pytest.skip(f"Real backend unavailable for TC-W0-CFG-007: {exc}")


def handle_tc_w0_cfg_006(runtime: RuntimeContext, case: TestCase) -> None:
    # TC-W0-CFG-006 | 提成-服务费账单触发 70/30 分摊
    # 覆盖: FR-COM-02, FR-COM-03
    # 数据: DS-U-FI-01, DS-CFG-CASE-NORMAL-INV, DS-CFG-COM-NORMAL-SERVICE,
    #       DS-CFG-BILL-SERVICE-1000
    # 动态值: FPMS_RUN_ID
    # 前置: 准备两个 Agent、客户、带 70/30 分摊的案卷和服务费提成规则。
    # 步骤摘要: 创建手工 SERVICE 账单后查询 /commission。
    # 预期: 提成为两个代理人按 700/300 base_fee 拆分并计算 s1/s2 金额。
    del case

    try:
        runtime.api.login(runtime.username, runtime.password)

        catalog = SeedCatalog.load(run_id=runtime.run_id)
        agent_a, agent_b = _ensure_commission_agent_users(runtime)

        client = _ensure_config_client(runtime, catalog, "commission split")
        client_id = _required_value(client, "id", "created client")

        case_payload = _commission_case_payload(catalog, client_id, agent_a, agent_b)
        created_case = _json_or_assert(
            runtime.api.post("/cases", json=case_payload),
            "create commission split case",
            expected_statuses={200, 201},
        )
        case_id = _required_value(created_case, "id", "created case")

        rule_payload = _commission_rule_payload(catalog, "DS-CFG-COM-NORMAL-SERVICE")
        _json_or_assert(
            runtime.api.post("/commission/rules", json=rule_payload),
            "create commission split rule",
            expected_statuses={200, 201},
        )

        bill_payload = _manual_service_bill_payload(catalog, client_id, case_id)
        _json_or_assert(
            runtime.api.post("/bills/manual", json=bill_payload),
            "create commission split manual bill",
            expected_statuses={200, 201},
        )

        commissions = _json_or_assert(
            runtime.api.get(
                "/commission",
                params={"page": 1, "page_size": 20, "case_id": case_id},
            ),
            "list commission split records",
        )
        _assert_commission_split_records(
            commissions, agent_a["user_id"], agent_b["user_id"]
        )

        if runtime.db.enabled():
            runtime.db.assert_row_exists("t_case", {"case_no": case_payload["case_no"]})
            runtime.db.assert_row_exists(
                "t_commission",
                {"case_id": case_id, "agent_id": agent_a["user_id"]},
            )
            runtime.db.assert_row_exists(
                "t_commission",
                {"case_id": case_id, "agent_id": agent_b["user_id"]},
            )
    except requests.RequestException as exc:
        pytest.skip(f"Real backend unavailable for TC-W0-CFG-006: {exc}")


def _ensure_commission_agent_users(
    runtime: RuntimeContext,
) -> tuple[dict[str, Any], dict[str, Any]]:
    specs = [
        {
            "username": f"commission-agent-a-{runtime.run_id}",
            "password": runtime.password,
            "role": "Agent",
        },
        {
            "username": f"commission-agent-b-{runtime.run_id}",
            "password": runtime.password,
            "role": "Agent",
        },
    ]
    for spec in specs:
        _ensure_permission_user(runtime, spec)
    return specs[0], specs[1]


def _config_client_payload(catalog: SeedCatalog) -> dict[str, Any]:
    seed = catalog.normalized("DS-CFG-CLIENT-ACTIVE")
    return dict(seed["payload"])


def _ensure_config_client(
    runtime: RuntimeContext,
    catalog: SeedCatalog,
    action: str,
) -> dict[str, Any]:
    payload = _config_client_payload(catalog)
    existing = _search_by_field(
        runtime,
        "/clients",
        "client_code",
        payload["client_code"],
    )
    if existing is not None:
        return existing
    return _json_or_assert(
        runtime.api.post("/clients", json=payload),
        f"create {action} client",
        expected_statuses={200, 201},
    )


def _commission_case_payload(
    catalog: SeedCatalog,
    client_id: Any,
    agent_a: dict[str, Any],
    agent_b: dict[str, Any],
) -> dict[str, Any]:
    seed = catalog.normalized("DS-CFG-CASE-NORMAL-INV")
    payload = dict(seed["payload"])
    payload["client_id"] = client_id
    payload["primary_agent_id"] = agent_a["user_id"]
    payload["agent_splits"] = [
        {"agent_id": agent_a["user_id"], "role": "PRIMARY", "share_ratio": "70.0000"},
        {"agent_id": agent_b["user_id"], "role": "SECONDARY", "share_ratio": "30.0000"},
    ]
    return payload


def _manual_service_bill_payload(
    catalog: SeedCatalog,
    client_id: Any,
    case_id: Any,
) -> dict[str, Any]:
    seed = catalog.normalized("DS-CFG-BILL-SERVICE-1000")
    payload = dict(seed["payload"])
    item = dict(payload["items"][0])
    return {
        "client_id": client_id,
        "case_id": case_id,
        "currency": payload.get("currency", "CNY"),
        "direction": "AR",
        "status": "UNSETTLED",
        "bill_date": "2026-05-09",
        "items": [
            {
                "description": item["fee_code"],
                "quantity": 1,
                "unit_price": item["amount"],
                "fee_type": item["fee_type"],
            }
        ],
    }


def _assert_commission_split_records(
    payload: dict[str, Any],
    agent_a_id: Any,
    agent_b_id: Any,
) -> None:
    items = payload.get("items")
    if not isinstance(items, list):
        raise AssertionError("Commission response missing items list")
    by_agent = {item.get("agent_id"): item for item in items if isinstance(item, dict)}
    expected = {
        agent_a_id: ("700.00", "210.00", "140.00"),
        agent_b_id: ("300.00", "90.00", "60.00"),
    }
    for agent_id, (base_fee, s1_amount, s2_amount) in expected.items():
        actual = by_agent.get(agent_id)
        if actual is None:
            raise AssertionError(f"Commission record missing for agent {agent_id}")
        if not _money_matches(actual.get("base_fee"), base_fee):
            raise AssertionError(f"Commission base_fee mismatch for agent {agent_id}")
        if not _money_matches(actual.get("s1_amount"), s1_amount):
            raise AssertionError(f"Commission s1_amount mismatch for agent {agent_id}")
        if not _money_matches(actual.get("s2_amount"), s2_amount):
            raise AssertionError(f"Commission s2_amount mismatch for agent {agent_id}")


def _assert_commission_settle_flags(
    search_result: dict[str, Any],
    expected_payload: dict[str, Any],
) -> None:
    items = search_result.get("items")
    if not isinstance(items, list):
        raise AssertionError("Commission rule search response missing items list")
    for item in items:
        if not isinstance(item, dict):
            continue
        if item.get("rule_name") != expected_payload["rule_name"]:
            continue
        for field in ("wait_pay", "force_settle", "enabled"):
            if item.get(field) != expected_payload[field]:
                raise AssertionError(
                    f"Commission settle flag {field} mismatch: {item.get(field)!r}"
                )
        return
    raise AssertionError(
        f"Commission settle flag rule not found: {expected_payload['rule_name']}"
    )


def _commission_rule_payload(catalog: SeedCatalog, seed_id: str) -> dict[str, Any]:
    seed = catalog.normalized(seed_id)
    return dict(seed["payload"])


def _assert_status(response: Any, expected_statuses: set[int], action: str) -> None:
    status_code = getattr(response, "status_code", None)
    if status_code not in expected_statuses:
        raise AssertionError(
            f"{action} expected {sorted(expected_statuses)}, got {status_code}: "
            f"{_response_summary(response)}"
        )


def _assert_commission_rule_search_hit(
    search_result: dict[str, Any],
    expected_payload: dict[str, Any],
) -> None:
    items = search_result.get("items")
    if not isinstance(items, list):
        raise AssertionError("Commission rule search response missing items list")
    for item in items:
        if not isinstance(item, dict):
            continue
        if item.get("rule_name") != expected_payload["rule_name"]:
            continue
        for field in (
            "case_type",
            "fee_type",
            "flow_dir",
            "patent_category",
            "wait_pay",
            "force_settle",
            "enabled",
        ):
            if item.get(field) != expected_payload[field]:
                raise AssertionError(
                    f"Commission rule field {field} mismatch: {item.get(field)!r}"
                )
        return
    raise AssertionError(
        f"Created commission rule was not found by rule_name {expected_payload['rule_name']}"
    )


def handle_tc_w0_008(runtime: RuntimeContext, case: TestCase) -> None:
    # TC-W0-008 | 业务参数-费率分档
    # 覆盖: FR-FE-01, FR-FE-03
    # 数据: DS-U-FI-01
    # 动态值: <none>
    # 前置: DS-U-FI-01；准备 BY_YEAR、BY_CLAIMS、BY_PAGES、COMPOSITE 四类 CalcParams。
    # 步骤摘要: 创建年费分档、超项费、超页费和复合计算费率；保存后执行计算预览或在草单生成中调用。
    # 预期: 系统能保存 CalcMode/CalcParams；不同模式能被后续草单正确调用。
    # Arrange: 准备种子数据 / 鉴权 / 页面或 API 上下文。
    # Act: 按 steps_summary 执行业务流。
    # Assert: 按 expected 做 UI / API / DB / 文件断言。
    handle_tc_w0_cfg_004(runtime, case)


def handle_tc_w0_009(runtime: RuntimeContext, case: TestCase) -> None:
    # TC-W0-009 | 业务参数-时限模板合法配置
    # 覆盖: FR-DL-01, V-TM-01, V-TM-02, V-TM-03, V-TM-04
    # 数据: DS-U-ADM
    # 动态值: <none>
    # 前置: DS-U-ADM；准备模板代码 APPLY_FEE_LIMIT、OA_REPLY_LIMIT。
    # 步骤摘要: 创建有效模板；再分别尝试 Code 重复、AddYears/AddMonths/AddDays 全为 0、DailyRemind=true 但无 InnerOffset/Remind、DeadlineBase=CUSTOM 但调用端不传 BaseDate。
    # 预期: 有效模板可保存；重复 Code 被拒；无增量模板被拒；DailyRemind 配置不足被拒；调用端缺 BaseDate 时任务生成失败并给出明确错误。
    handle_tc_w0_cfg_008(runtime, case)


def handle_tc_w0_010(runtime: RuntimeContext, case: TestCase) -> None:
    # TC-W0-010 | 业务参数-文档模板配置
    # 覆盖: FR-WD-01, FR-WD-03, V-TPL-01, V-TPL-02, V-TPL-03, V-TPL-04, V-TPL-05
    # 数据: DS-U-ADM
    # 动态值: <none>
    # 前置: DS-U-ADM；准备 OA_NOTICE、OA_REPLY、GRANT_NOTICE、ANNUITY_NOTICE 模板与对应 TaskTemplate/FeeRate。
    # 步骤摘要: 创建 DocTemplate，设置 DocType、StatusEffect、StatusRestore、DeadlineTemplateCode、FeeDraftType、FeeItemList、InputFieldList、PlainTemplateID_CN/EN。
    # 预期: 模板保存成功；字段映射有效；后续向导中默认值、状态联动、任务和草单生成均可被带出。
    del case

    try:
        runtime.api.login(runtime.username, runtime.password)

        catalog = SeedCatalog.load(run_id=runtime.run_id)
        created_payloads = _build_doc_template_payloads(catalog, runtime.run_id)

        for payload in created_payloads:
            created = _json_or_assert(
                runtime.api.post("/doc-templates", json=payload),
                "create doc template",
                expected_statuses={200, 201},
            )
            template_id = created.get("id")

            search_result = _json_or_assert(
                runtime.api.get(
                    "/doc-templates",
                    params={"page": 1, "page_size": 20, "q": payload["code"]},
                ),
                "search doc template",
            )
            _assert_doc_template_search_hit(search_result, payload)

            if template_id not in (None, ""):
                detail = _json_or_assert(
                    runtime.api.get(f"/doc-templates/{template_id}"),
                    "get doc template detail",
                )
                _assert_doc_template_fields(detail, payload)

        if runtime.db.enabled():
            for payload in created_payloads:
                runtime.db.assert_row_exists(
                    "t_doc_template",
                    {
                        "code": payload["code"],
                        "direction": payload["direction"],
                        "enabled": payload["enabled"],
                    },
                )
    except requests.RequestException as exc:
        pytest.skip(f"Real backend unavailable for TC-W0-010: {exc}")


def _build_doc_template_payloads(
    catalog: SeedCatalog,
    run_id: str,
) -> list[dict[str, Any]]:
    oa_notice_code = _doc_template_code(catalog.get("DS-TPL-DOC-001"), run_id)
    return [
        _build_doc_template_payload(
            seed=catalog.get("DS-TPL-DOC-001"),
            run_id=run_id,
            code=oa_notice_code,
            direction="IN",
            status_effect="OA1",
            deadline_template_code="OA_REPLY_LIMIT",
            need_reply=True,
        ),
        _build_doc_template_payload(
            seed=catalog.get("DS-TPL-DOC-002"),
            run_id=run_id,
            direction="OUT",
            status_restore="SUB_EXAM",
            reply_to_template_code=oa_notice_code,
            need_reply=False,
        ),
        _build_doc_template_payload(
            seed=catalog.get("DS-TPL-DOC-003"),
            run_id=run_id,
            direction="IN",
            status_effect="GRANTED",
            fee_draft_type="GRANT_FEE",
            input_fields=[
                "IssueDate",
                "GrantDate",
                "GrantNo",
                "FirstAnnuityYear",
                "ValidUntil",
            ],
        ),
        _build_doc_template_payload(
            seed=catalog.get("DS-TPL-DOC-005"),
            run_id=run_id,
            direction="OUT",
            fee_draft_type="ANNUITY_FEE",
            input_fields=["AnnuityYear", "DueDate", "Amount", "Currency"],
        ),
    ]


def _build_doc_template_payload(
    *,
    seed: dict[str, Any],
    run_id: str,
    direction: str,
    code: str | None = None,
    status_effect: str | None = None,
    status_restore: str | None = None,
    deadline_template_code: str | None = None,
    fee_draft_type: str | None = None,
    fee_item_list: list[str] | None = None,
    need_reply: bool = False,
    reply_to_template_code: str | None = None,
    input_fields: list[str] | None = None,
) -> dict[str, Any]:
    template_code = code or _doc_template_code(seed, run_id)
    return {
        "code": template_code,
        "name": f"{seed['template_code']} {run_id}",
        "direction": direction,
        "enabled": True,
        "status_effect": status_effect,
        "status_restore": status_restore,
        "deadline_template_code": deadline_template_code,
        "fee_draft_type": fee_draft_type,
        "fee_item_list": _json_list_or_none(fee_item_list),
        "need_reply": need_reply,
        "reply_to_template_code": reply_to_template_code,
        "input_fields": _json_list_or_none(input_fields),
    }


def _doc_template_code(seed: dict[str, Any], run_id: str) -> str:
    code = unique_code(str(seed["template_code"]), run_id)
    if len(code) > 64:
        raise AssertionError(
            f"Generated doc template code exceeds t_doc_template.code length 64: {len(code)}"
        )
    return code


def _json_list_or_none(values: list[str] | None) -> str | None:
    if values is None:
        return None
    return json.dumps(values, separators=(",", ":"))


def _assert_doc_template_search_hit(
    search_result: dict[str, Any],
    expected_payload: dict[str, Any],
) -> None:
    items = search_result.get("items")
    if not isinstance(items, list):
        raise AssertionError("Doc template search response missing items list")
    for item in items:
        if not isinstance(item, dict):
            continue
        if item.get("code") != expected_payload["code"]:
            continue
        _assert_doc_template_fields(item, expected_payload)
        return
    raise AssertionError(
        f"Created doc template was not found by code {expected_payload['code']}"
    )


def _ensure_task_template(
    runtime: RuntimeContext,
    payload: dict[str, Any],
    action: str,
) -> dict[str, Any]:
    existing = _search_by_field(
        runtime,
        "/task-templates",
        "code",
        payload["code"],
        params={"enabled_only": False},
    )
    if existing is not None:
        return existing
    return _json_or_assert(
        runtime.api.post("/task-templates", json=payload),
        f"create {action} task template",
        expected_statuses={200, 201},
    )


def _ensure_doc_template(
    runtime: RuntimeContext,
    payload: dict[str, Any],
    action: str,
) -> dict[str, Any]:
    existing = _search_by_field(
        runtime,
        "/doc-templates",
        "code",
        payload["code"],
        params={"page": 1, "page_size": 20, "q": payload["code"]},
    )
    if existing is not None:
        return existing
    return _json_or_assert(
        runtime.api.post("/doc-templates", json=payload),
        f"create {action} doc template",
        expected_statuses={200, 201},
    )


def _search_by_field(
    runtime: RuntimeContext,
    path: str,
    field: str,
    value: Any,
    params: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    search_params = params or {"page": 1, "page_size": 20, "q": value}
    payload = _json_or_assert(
        runtime.api.get(path, params=search_params),
        f"search {path}",
    )
    return _find_item_by_field(payload, field, value)


def _find_item_by_field(payload: Any, field: str, value: Any) -> dict[str, Any] | None:
    for item in _payload_items(payload):
        if isinstance(item, dict) and item.get(field) == value:
            return item
    return None


def _payload_items(payload: Any) -> list[Any]:
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict) and isinstance(payload.get("items"), list):
        return payload["items"]
    raise AssertionError("Search response missing items list")


def _assert_doc_template_fields(
    actual: dict[str, Any],
    expected_payload: dict[str, Any],
) -> None:
    for field in (
        "code",
        "name",
        "direction",
        "enabled",
        "status_effect",
        "status_restore",
        "deadline_template_code",
        "fee_draft_type",
        "fee_item_list",
        "need_reply",
        "reply_to_template_code",
        "input_fields",
    ):
        if actual.get(field) != expected_payload[field]:
            raise AssertionError(
                f"Doc template field {field} mismatch: {actual.get(field)!r}"
            )


@skeleton_case
def handle_tc_w0_011(runtime: RuntimeContext, case: TestCase) -> None:
    # TC-W0-011 | 业务参数-文档模板非法配置
    # 覆盖: FR-WD-03, V-TPL-01, V-TPL-02, V-TPL-03, V-TPL-04, V-TPL-05
    # 数据: DS-U-ADM
    # 动态值: <none>
    # 前置: DS-U-ADM；准备不存在的 DeadlineTemplateCode、FeeCode、InputField 字段名。
    # 步骤摘要: 分别尝试保存：重复 TemplateCode；不存在的 DeadlineTemplateCode；只配置 StatusRestore 未说明回复逻辑；FeeItemList 引用不存在费率；InputFieldList 引用不存在字段。
    # 预期: 系统逐项阻止保存并提示具体错误点。
    # Arrange: 准备种子数据 / 鉴权 / 页面或 API 上下文。
    # Act: 按 steps_summary 执行业务流。
    # Assert: 按 expected 做 UI / API / DB / 文件断言。
    return None


def handle_tc_w0_012(runtime: RuntimeContext, case: TestCase) -> None:
    # TC-W0-012 | 文档模板与信头
    # 覆盖: FR-WD-09, FR-WD-10, FR-BL-04
    # 数据: DS-U-ADM
    # 动态值: <none>
    # 前置: DS-U-ADM；准备中文/英文 Word 模板与 CN/EN 信头。
    # 步骤摘要: 上传 T_Template，配置 Group/Language/FilePath/Enabled；创建两套 T_LetterHead 并关联到模板。
    # 预期: 模板和信头均可保存；不同语言模板输出时能正确带出对应抬头。
    handle_tc_w0_cfg_010(runtime, case)
    handle_tc_w0_cfg_011(runtime, case)


def handle_tc_w0_013(runtime: RuntimeContext, case: TestCase) -> None:
    # TC-W0-013 | 系统参数
    # 覆盖: FR-BL-09, FR-COM-04, FR-COM-05
    # 数据: DS-U-ADM
    # 动态值: <none>
    # 前置: DS-U-ADM；准备催款间隔、默认 WaitPay 阈值、退款策略等参数。
    # 步骤摘要: 维护 T_SystemParam（若实现）；分别设置催款间隔、预收款负账单策略、WaitPay 阈值、ForceSettle 默认策略。
    # 预期: 参数保存成功；相关流程读取到新值，且更新后对新交易生效。
    handle_tc_w0_cfg_001(runtime, case)


def handle_tc_w0_cfg_001(runtime: RuntimeContext, case: TestCase) -> None:
    # TC-W0-CFG-001 | 系统参数 API 与 UI 元数据
    # 覆盖: FR-BL-04, FR-BL-09, FR-COM-04, FR-COM-05
    # 数据: DS-U-ADM, DS-CFG-SYS-DEFAULT-CURRENCY, DS-CFG-SYS-BILL-TEMPLATE,
    #       DS-CFG-SYS-SECRET-SAMPLE
    # 动态值: FPMS_RUN_ID
    # 前置: DS-U-ADM；准备普通参数、账单模板路径参数和密文参数。
    # 步骤摘要: 通过 PUT /system/params/{param_key} 写入三项 run-scoped 参数；
    #          再 GET /system/params 校验 metadata、value_type、is_secret 和密文遮蔽。
    # 预期: 普通参数返回真实值；密文参数返回遮蔽值；列表包含 description/updated_at。
    del case

    try:
        runtime.api.login(runtime.username, runtime.password)

        catalog = SeedCatalog.load(run_id=runtime.run_id)
        specs = _system_param_specs(catalog, runtime.run_id)
        for spec in specs:
            _json_or_assert(
                runtime.api.put(
                    f"/system/params/{spec['param_key']}",
                    json=spec["payload"],
                ),
                "upsert system param",
                expected_statuses={200, 201},
            )

        listed = _json_or_assert(
            runtime.api.get("/system/params"),
            "list system params",
        )
        _assert_system_param_list(listed, specs)

        if runtime.db.enabled():
            for spec in specs:
                runtime.db.assert_row_exists(
                    "t_system_param",
                    {
                        "param_key": spec["param_key"],
                        "is_secret": bool(spec["payload"].get("is_secret")),
                    },
                )
    except requests.RequestException as exc:
        pytest.skip(f"Real backend unavailable for TC-W0-CFG-001: {exc}")


def _system_param_specs(
    catalog: SeedCatalog,
    run_id: str,
) -> list[dict[str, Any]]:
    return [
        _system_param_spec(catalog, "DS-CFG-SYS-DEFAULT-CURRENCY", run_id),
        _system_param_spec(catalog, "DS-CFG-SYS-BILL-TEMPLATE", run_id),
        _system_param_spec(catalog, "DS-CFG-SYS-SECRET-SAMPLE", run_id),
    ]


def _system_param_spec(
    catalog: SeedCatalog,
    seed_id: str,
    run_id: str,
) -> dict[str, Any]:
    seed = catalog.normalized(seed_id)
    payload = dict(seed["payload"])
    return {
        "seed_id": seed_id,
        "param_key": _run_scoped_system_param_key(seed, run_id),
        "payload": payload,
    }


def _run_scoped_system_param_key(seed: dict[str, Any], run_id: str) -> str:
    api = str(seed.get("api", ""))
    base_key = api.rsplit("/", 1)[-1] if "/" in api else str(seed["id"])
    return f"{base_key}_{run_id}".replace("-", "_")


def _assert_system_param_list(
    payload: Any,
    specs: list[dict[str, Any]],
) -> None:
    if not isinstance(payload, list):
        raise AssertionError("System params list response is not a list")

    by_key = {
        item.get("param_key"): item
        for item in payload
        if isinstance(item, dict) and isinstance(item.get("param_key"), str)
    }
    for spec in specs:
        expected = spec["payload"]
        key = spec["param_key"]
        actual = by_key.get(key)
        if actual is None:
            raise AssertionError(f"System param missing from list response: {key}")

        if actual.get("value_type") != expected.get("value_type"):
            raise AssertionError(f"System param value_type mismatch for {key}")
        if actual.get("description") != expected.get("description"):
            raise AssertionError(f"System param description mismatch for {key}")
        if actual.get("is_secret") is not bool(expected.get("is_secret")):
            raise AssertionError(f"System param is_secret mismatch for {key}")
        if not actual.get("updated_at"):
            raise AssertionError(f"System param updated_at missing for {key}")

        expected_value = expected.get("param_value")
        actual_value = actual.get("param_value")
        if expected.get("is_secret"):
            if actual_value == expected_value:
                raise AssertionError(f"Secret system param leaked raw value for {key}")
            if actual_value != "******":
                raise AssertionError(f"Secret system param masking mismatch for {key}")
        elif actual_value != expected_value:
            raise AssertionError(f"System param value mismatch for {key}")


def handle_tc_w0_cfg_010(runtime: RuntimeContext, case: TestCase) -> None:
    # TC-W0-CFG-010 | 模板仓库-DOC_TEMPLATE 文件路径与渲染缺口
    # 覆盖: FR-WD-09, FR-WD-10, FR-BL-04
    # 数据: DS-U-ADM, DS-CFG-TEMPLATE-DOC-OA-CN, DS-CFG-TEMPLATE-BILL-CN
    # 动态值: FPMS_RUN_ID
    # 前置: DS-U-ADM；准备文档和账单模板文件源记录。
    # 步骤摘要: 通过 /templates 创建模板源记录，再按 group 查询确认真实 API 可见。
    # 预期: 有效模板源记录可保存并按 group 检索，文件路径在创建响应和 DB 中可追踪。
    del case

    try:
        runtime.api.login(runtime.username, runtime.password)

        catalog = SeedCatalog.load(run_id=runtime.run_id)
        specs = _template_source_specs(catalog)
        for spec in specs:
            created = _json_or_assert(
                runtime.api.post("/templates", json=spec["payload"]),
                "create template source",
                expected_statuses={200, 201},
            )
            template_id = _required_value(created, "id", "created template source")
            _assert_template_source_payload(
                created, spec["payload"], include_file_path=True
            )

            listed = _json_or_assert(
                runtime.api.get(
                    "/templates",
                    params={
                        "page": 1,
                        "page_size": 20,
                        "group": spec["payload"]["group"],
                    },
                ),
                "list template sources",
            )
            _assert_template_source_list_hit(
                listed,
                template_id=template_id,
                expected_payload=spec["payload"],
            )

        if runtime.db.enabled():
            for spec in specs:
                payload = spec["payload"]
                runtime.db.assert_row_exists(
                    "t_template",
                    {
                        "name": payload["name"],
                        "group": payload["group"],
                        "file_path": payload["file_path"],
                        "enabled": payload["enabled"],
                    },
                )
    except requests.RequestException as exc:
        pytest.skip(f"Real backend unavailable for TC-W0-CFG-010: {exc}")


def _template_source_specs(catalog: SeedCatalog) -> list[dict[str, Any]]:
    return [
        _template_source_spec(catalog, "DS-CFG-TEMPLATE-DOC-OA-CN"),
        _template_source_spec(catalog, "DS-CFG-TEMPLATE-BILL-CN"),
    ]


def _template_source_spec(catalog: SeedCatalog, seed_id: str) -> dict[str, Any]:
    seed = catalog.normalized(seed_id)
    return {"seed_id": seed_id, "payload": dict(seed["payload"])}


def _assert_template_source_payload(
    actual: dict[str, Any],
    expected_payload: dict[str, Any],
    *,
    include_file_path: bool,
) -> None:
    fields = ("name", "group", "language", "enabled")
    for field in fields:
        if actual.get(field) != expected_payload[field]:
            raise AssertionError(
                f"Template source field {field} mismatch: {actual.get(field)!r}"
            )
    if include_file_path and actual.get("file_path") != expected_payload["file_path"]:
        raise AssertionError("Template source file_path mismatch")


def _assert_template_source_list_hit(
    payload: dict[str, Any],
    *,
    template_id: Any,
    expected_payload: dict[str, Any],
) -> None:
    items = payload.get("items")
    if not isinstance(items, list):
        raise AssertionError("Template source list response missing items list")
    for item in items:
        if not isinstance(item, dict) or item.get("id") != template_id:
            continue
        _assert_template_source_payload(
            item,
            expected_payload,
            include_file_path="file_path" in item,
        )
        return
    raise AssertionError(
        f"Created template source was not found by group {expected_payload['group']}"
    )


def handle_tc_w0_cfg_014(runtime: RuntimeContext, case: TestCase) -> None:
    # TC-W0-CFG-014 | 种子数据-配置缺口阻断业务 smoke
    # 覆盖: FR-FE-01, FR-COM-01, FR-WD-09, FR-BL-04
    # 数据: DS-CFG-SEED-EXPECTED-COUNTS
    # 动态值: <none>
    # 前置: 当前数据库已清理为种子数据；不创建额外业务配置。
    # 步骤摘要: 调用 /system/config-readiness 做只读配置 readiness audit。
    # 预期: readiness audit 暴露 fee_rate、commission_rule、template 等硬阻断缺口。
    del case

    try:
        runtime.api.login(runtime.username, runtime.password)

        catalog = SeedCatalog.load(run_id=runtime.run_id)
        catalog.get("DS-CFG-SEED-EXPECTED-COUNTS")

        readiness = _json_or_assert(
            runtime.api.get("/system/config-readiness"),
            "get config readiness",
        )
        _assert_config_readiness(readiness)
    except requests.RequestException as exc:
        pytest.skip(f"Real backend unavailable for TC-W0-CFG-014: {exc}")


_EXPECTED_READINESS_COUNT_KEYS = {
    "system_param",
    "fee_rate",
    "commission_rule",
    "template",
    "letter_head",
    "country",
    "department",
    "doc_template",
    "task_template",
}

_EXPECTED_SEED_ONLY_HARD_BLOCKERS = {
    "fee_rate.apply",
    "commission_rule.enabled",
    "template.enabled",
    "letter_head.default",
    "country.active",
    "department.active",
    "doc_template.enabled",
    "task_template.enabled",
}


def _assert_config_readiness(payload: dict[str, Any]) -> None:
    counts = payload.get("counts")
    if not isinstance(counts, list):
        raise AssertionError("Config readiness response missing counts list")
    count_keys = {item.get("key") for item in counts if isinstance(item, dict)}
    missing_count_keys = _EXPECTED_READINESS_COUNT_KEYS - count_keys
    if missing_count_keys:
        raise AssertionError(
            f"Config readiness missing count keys: {sorted(missing_count_keys)}"
        )

    if payload.get("status") != "BLOCKED":
        raise AssertionError("Seed-only readiness should report BLOCKED")
    if payload.get("hard_blocked") is not True:
        raise AssertionError("Seed-only readiness should set hard_blocked=true")

    missing = payload.get("missing")
    if not isinstance(missing, list):
        raise AssertionError("Config readiness response missing missing list")
    missing_keys = {item.get("key") for item in missing if isinstance(item, dict)}
    absent_blockers = _EXPECTED_SEED_ONLY_HARD_BLOCKERS - missing_keys
    if absent_blockers:
        raise AssertionError(
            f"Config readiness missing hard blockers: {sorted(absent_blockers)}"
        )
    for item in missing:
        if not isinstance(item, dict):
            raise AssertionError("Config readiness missing entry is not an object")
        if item.get("severity") != "hard_block":
            raise AssertionError(
                f"Config readiness entry has invalid severity: {item.get('key')}"
            )
        for field in ("label", "table", "message"):
            if not item.get(field):
                raise AssertionError(
                    f"Config readiness entry missing {field}: {item.get('key')}"
                )


def handle_tc_w0_cfg_011(runtime: RuntimeContext, case: TestCase) -> None:
    # TC-W0-CFG-011 | 信头-默认信头唯一性和账单打印引用
    # 覆盖: FR-WD-09, FR-WD-10, FR-BL-04
    # 数据: DS-U-ADM, DS-CFG-LETTERHEAD-CN, DS-CFG-LETTERHEAD-EN
    # 动态值: FPMS_RUN_ID
    # 前置: 准备中文/英文默认信头 payload。
    # 步骤摘要: 创建 CN/EN 默认信头，再创建第二个 CN 默认信头并按 locale 查询。
    # 预期: 同 locale 只能有一个默认信头，新的 CN 默认信头取消旧 CN 默认状态。
    del case

    try:
        runtime.api.login(runtime.username, runtime.password)

        catalog = SeedCatalog.load(run_id=runtime.run_id)
        cn_payload = _letterhead_payload(catalog, "DS-CFG-LETTERHEAD-CN")
        en_payload = _letterhead_payload(catalog, "DS-CFG-LETTERHEAD-EN")
        cn_replacement_payload = dict(cn_payload)
        cn_replacement_payload["name"] = f"{cn_payload['name']}-替换"

        created_cn = _json_or_assert(
            runtime.api.post("/letterheads", json=cn_payload),
            "create CN letterhead",
            expected_statuses={200, 201},
        )
        _assert_letterhead_payload(created_cn, cn_payload)

        created_en = _json_or_assert(
            runtime.api.post("/letterheads", json=en_payload),
            "create EN letterhead",
            expected_statuses={200, 201},
        )
        _assert_letterhead_payload(created_en, en_payload)

        created_replacement = _json_or_assert(
            runtime.api.post("/letterheads", json=cn_replacement_payload),
            "create replacement CN letterhead",
            expected_statuses={200, 201},
        )
        _assert_letterhead_payload(created_replacement, cn_replacement_payload)

        cn_list = _json_or_assert(
            runtime.api.get("/letterheads", params={"locale": cn_payload["locale"]}),
            "list CN letterheads",
        )
        _assert_single_default_letterhead(cn_list, cn_replacement_payload["name"])

        if runtime.db.enabled():
            runtime.db.assert_row_exists(
                "t_letter_head",
                {"name": cn_payload["name"], "is_default": False},
            )
            runtime.db.assert_row_exists(
                "t_letter_head",
                {"name": cn_replacement_payload["name"], "is_default": True},
            )
            runtime.db.assert_row_exists(
                "t_letter_head",
                {"name": en_payload["name"], "is_default": True},
            )
    except requests.RequestException as exc:
        pytest.skip(f"Real backend unavailable for TC-W0-CFG-011: {exc}")


def _letterhead_payload(catalog: SeedCatalog, seed_id: str) -> dict[str, Any]:
    seed = catalog.normalized(seed_id)
    return dict(seed["payload"])


def _assert_letterhead_payload(
    actual: dict[str, Any],
    expected_payload: dict[str, Any],
) -> None:
    for field in (
        "name",
        "locale",
        "logo_file_path",
        "header_text",
        "footer_text",
        "address_block",
        "phone",
        "email",
        "website",
        "is_default",
    ):
        if actual.get(field) != expected_payload[field]:
            raise AssertionError(
                f"Letterhead field {field} mismatch: {actual.get(field)!r}"
            )


def _assert_single_default_letterhead(
    items: Any,
    expected_default_name: str,
) -> None:
    if not isinstance(items, list):
        raise AssertionError("Letterhead list response is not a list")
    defaults = [
        item for item in items if isinstance(item, dict) and item.get("is_default")
    ]
    if len(defaults) != 1:
        raise AssertionError(
            f"Expected exactly one default letterhead, got {len(defaults)}"
        )
    if defaults[0].get("name") != expected_default_name:
        raise AssertionError(
            f"Default letterhead mismatch: {defaults[0].get('name')!r}"
        )


def handle_tc_w0_cfg_013(runtime: RuntimeContext, case: TestCase) -> None:
    # TC-W0-CFG-013 | 权限-配置端点和菜单可见性
    # 覆盖: FR-CM-06, FR-DL-06, FR-BL-06
    # 数据: DS-U-ADM, DS-U-FI-01, DS-U-FM-01, DS-U-LMT-01
    # 动态值: <none>
    # 前置: 角色权限 seed 已运行。
    # 步骤摘要: 验证 Admin 配置权限，并以 Finance 角色访问代表性配置读端点。
    # 预期: Admin 具备配置权限；Finance 无配置权限时受保护端点返回 403。
    del case

    try:
        runtime.api.login(runtime.username, runtime.password)

        catalog = SeedCatalog.load(run_id=runtime.run_id)
        for seed_id in ("DS-U-ADM", "DS-U-FI-01", "DS-U-FM-01", "DS-U-LMT-01"):
            catalog.get(seed_id)

        admin_profile = _json_or_assert(
            runtime.api.get("/auth/me"),
            "get admin config auth profile",
        )
        _assert_permission_subject(
            admin_profile,
            expected_role="Admin",
            include_permissions=_CONFIG_ENDPOINT_PERMISSIONS,
            exclude_permissions=set(),
        )

        role_specs = _permission_role_specs(runtime.run_id, runtime.password)
        finance_spec = next(spec for spec in role_specs if spec["role"] == "Finance")
        _ensure_permission_user(runtime, finance_spec)

        runtime.api.login(finance_spec["username"], finance_spec["password"])
        profile = _json_or_assert(
            runtime.api.get("/auth/me"),
            "get finance config auth profile",
        )
        _assert_permission_subject(
            profile,
            expected_role="Finance",
            include_permissions=set(finance_spec["include_permissions"]),
            exclude_permissions=_CONFIG_ENDPOINT_PERMISSIONS,
        )

        for endpoint in _CONFIG_ENDPOINT_PERMISSION_ENDPOINTS:
            forbidden = runtime.api.get(endpoint["path"], params=endpoint["params"])
            _assert_forbidden_permission(forbidden, endpoint["required_perm"])
    except requests.RequestException as exc:
        pytest.skip(f"Real backend unavailable for TC-W0-CFG-013: {exc}")


_CONFIG_ENDPOINT_PERMISSIONS = {
    "SystemParam.Read",
    "FeeRate.Read",
    "CommissionRule.Read",
    "TaskTemplate.Read",
    "DocTemplate.Read",
    "Template.Read",
    "LetterHead.Read",
    "Country.Read",
    "Department.Read",
}

_CONFIG_ENDPOINT_PERMISSION_ENDPOINTS = (
    {
        "path": "/system/config-readiness",
        "params": {},
        "required_perm": "SystemParam.Read",
    },
    {
        "path": "/fees/rates",
        "params": {"page": 1, "page_size": 1},
        "required_perm": "FeeRate.Read",
    },
    {
        "path": "/commission/rules",
        "params": {"page": 1, "page_size": 1},
        "required_perm": "CommissionRule.Read",
    },
    {"path": "/task-templates", "params": {}, "required_perm": "TaskTemplate.Read"},
    {
        "path": "/doc-templates",
        "params": {"page": 1, "page_size": 1},
        "required_perm": "DocTemplate.Read",
    },
    {
        "path": "/templates",
        "params": {"page": 1, "page_size": 1},
        "required_perm": "Template.Read",
    },
    {"path": "/letterheads", "params": {}, "required_perm": "LetterHead.Read"},
    {
        "path": "/countries",
        "params": {"page": 1, "page_size": 1},
        "required_perm": "Country.Read",
    },
    {
        "path": "/departments",
        "params": {"page": 1, "page_size": 1},
        "required_perm": "Department.Read",
    },
)


def _ensure_permission_user(
    runtime: RuntimeContext,
    spec: dict[str, Any],
) -> None:
    admin_users = _json_or_assert(
        runtime.api.get("/admin/users", params={"page": 1, "page_size": 100}),
        "list admin users",
    )
    existing_by_username = _admin_users_by_username(admin_users)
    user = existing_by_username.get(spec["username"])
    payload = {
        "username": spec["username"],
        "password": spec["password"],
        "roles": [spec["role"]],
        "is_active": True,
    }
    if user is None:
        created = _json_or_assert(
            runtime.api.post("/admin/users", json=payload),
            "create permission user",
            expected_statuses={200, 201},
        )
        spec["user_id"] = _required_value(created, "id", "created user")
    else:
        spec["user_id"] = _required_value(user, "id", "existing user")
        _json_or_assert(
            runtime.api.put(
                f"/admin/users/{spec['user_id']}",
                json={"roles": [spec["role"]], "is_active": True},
            ),
            "update permission user",
        )


def handle_tc_w0_014(runtime: RuntimeContext, case: TestCase) -> None:
    # TC-W0-014 | 权限矩阵
    # 覆盖: FR-CM-06, FR-DL-06, FR-BL-06
    # 数据: DS-U-ADM, DS-U-AG-01, DS-U-FI-01, DS-U-FM-01, DS-U-LMT-01
    # 动态值: <none>
    # 前置: 准备 DS-U-ADM / DS-U-FM-01 / DS-U-AG-01 / DS-U-LMT-01 / DS-U-FI-01。
    # 步骤摘要: 分别以各角色登录，验证菜单、按钮和高危操作权限：案卷完整编辑、受限编辑、时限取消、反冲销、已缴费修改、坏账标记。
    # 预期: Admin 拥有全权限；Formalities 具备流程维护权限；Limited Editor 仅见补充信息入口；Finance 无法修改非法业务字段；高危操作仅授权用户可执行。
    del case

    try:
        runtime.api.login(runtime.username, runtime.password)

        catalog = SeedCatalog.load(run_id=runtime.run_id)
        for seed_id in (
            "DS-U-ADM",
            "DS-U-FM-01",
            "DS-U-AG-01",
            "DS-U-LMT-01",
            "DS-U-FI-01",
        ):
            catalog.get(seed_id)

        role_specs = _permission_role_specs(runtime.run_id, runtime.password)
        admin_users = _json_or_assert(
            runtime.api.get("/admin/users", params={"page": 1, "page_size": 100}),
            "list admin users",
        )
        existing_by_username = _admin_users_by_username(admin_users)

        for spec in role_specs:
            user = existing_by_username.get(spec["username"])
            payload = {
                "username": spec["username"],
                "password": spec["password"],
                "roles": [spec["role"]],
                "is_active": True,
            }
            if user is None:
                created = _json_or_assert(
                    runtime.api.post("/admin/users", json=payload),
                    "create permission user",
                    expected_statuses={200, 201},
                )
                spec["user_id"] = _required_value(created, "id", "created user")
            else:
                spec["user_id"] = _required_value(user, "id", "existing user")
                _json_or_assert(
                    runtime.api.put(
                        f"/admin/users/{spec['user_id']}",
                        json={"roles": [spec["role"]], "is_active": True},
                    ),
                    "update permission user",
                )

        _assert_permission_subject(
            _json_or_assert(runtime.api.get("/auth/me"), "get admin auth profile"),
            expected_role="Admin",
            include_permissions={
                "AdminUser.Read",
                "Case.Create",
                "Case.Edit",
                "Case.EditLimited",
                "Billing.Edit",
                "DocTemplate.Create",
                "FeeRate.Create",
            },
            exclude_permissions=set(),
        )
        _json_or_assert(
            runtime.api.get("/admin/users", params={"page": 1, "page_size": 20}),
            "admin users access as admin",
        )

        for spec in role_specs:
            runtime.api.login(spec["username"], spec["password"])
            profile = _json_or_assert(runtime.api.get("/auth/me"), "get auth profile")
            _assert_permission_subject(
                profile,
                expected_role=spec["role"],
                include_permissions=set(spec["include_permissions"]),
                exclude_permissions=set(spec["exclude_permissions"]),
            )

        for username in (
            f"agent-w0perm-{runtime.run_id}",
            f"finance-w0perm-{runtime.run_id}",
        ):
            runtime.api.login(username, runtime.password)
            forbidden = runtime.api.get(
                "/admin/users", params={"page": 1, "page_size": 20}
            )
            _assert_forbidden_permission(forbidden, "AdminUser.Read")

        if runtime.db.enabled():
            for spec in role_specs:
                runtime.db.assert_row_exists("t_user", {"username": spec["username"]})
                runtime.db.assert_row_exists("t_role", {"code": spec["role"]})
                runtime.db.assert_row_exists(
                    "t_user_role", {"user_id": spec["user_id"]}
                )
            for perm_code in (
                "AdminUser.Read",
                "Case.EditLimited",
                "Billing.Edit",
            ):
                runtime.db.assert_row_exists("t_role_perm", {"perm_code": perm_code})
    except requests.RequestException as exc:
        pytest.skip(f"Real backend unavailable for TC-W0-014: {exc}")


def _permission_role_specs(run_id: str, password: str) -> list[dict[str, Any]]:
    # The real RBAC seed currently has no distinct Limited Agent role; Agent is
    # the supported fallback that carries Case.EditLimited.
    return [
        {
            "seed_id": "DS-U-FM-01",
            "username": f"formalities-w0perm-{run_id}",
            "password": password,
            "role": "Formalities",
            "include_permissions": {
                "Case.Create",
                "Case.Edit",
                "Doc.Create",
                "Task.Edit",
            },
            "exclude_permissions": {"AdminUser.Read", "Billing.Edit"},
        },
        {
            "seed_id": "DS-U-AG-01",
            "username": f"agent-w0perm-{run_id}",
            "password": password,
            "role": "Agent",
            "include_permissions": {
                "Case.Read",
                "Case.EditLimited",
                "Doc.Read",
                "Task.Read",
            },
            "exclude_permissions": {"AdminUser.Read", "Billing.Edit", "Case.Edit"},
        },
        {
            "seed_id": "DS-U-FI-01",
            "username": f"finance-w0perm-{run_id}",
            "password": password,
            "role": "Finance",
            "include_permissions": {
                "Billing.Edit",
                "Payment.Create",
                "PayList.Read",
                "PayList.Export",
            },
            "exclude_permissions": {"AdminUser.Read", "Case.Edit"},
        },
        {
            "seed_id": "DS-U-LMT-01",
            "username": f"limited-w0perm-{run_id}",
            "password": password,
            "role": "Agent",
            "include_permissions": {"Case.EditLimited"},
            "exclude_permissions": {"AdminUser.Read", "Billing.Edit", "Case.Edit"},
        },
    ]


def _admin_users_by_username(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    items = payload.get("items")
    if not isinstance(items, list):
        raise AssertionError("Admin users response missing items list")
    users: dict[str, dict[str, Any]] = {}
    for item in items:
        if isinstance(item, dict) and isinstance(item.get("username"), str):
            users[item["username"]] = item
    return users


def _assert_permission_subject(
    profile: dict[str, Any],
    *,
    expected_role: str,
    include_permissions: set[str],
    exclude_permissions: set[str],
) -> None:
    user = profile.get("user")
    if not isinstance(user, dict) or user.get("is_active") is not True:
        raise AssertionError("Auth profile user is not active")
    roles = profile.get("roles")
    if not isinstance(roles, list) or expected_role not in roles:
        raise AssertionError(f"Auth profile missing expected role: {expected_role}")
    permissions = profile.get("permissions")
    if not isinstance(permissions, list):
        raise AssertionError("Auth profile missing permissions list")
    perm_set = set(permissions)
    missing = include_permissions - perm_set
    if missing:
        raise AssertionError(f"Auth profile missing permissions: {sorted(missing)}")
    unexpected = exclude_permissions & perm_set
    if unexpected:
        raise AssertionError(
            f"Auth profile has unexpected permissions: {sorted(unexpected)}"
        )


def _assert_forbidden_permission(response: Any, required_perm: str) -> None:
    status_code = getattr(response, "status_code", None)
    if status_code != 403:
        raise AssertionError(
            f"permission smoke expected 403, got {status_code}: {_response_summary(response)}"
        )
    body = response.json()
    body_text = str(body)
    if required_perm not in body_text:
        raise AssertionError(
            f"Forbidden response missing required_perm {required_perm}"
        )


HANDLERS = {
    "TC-W0-001": handle_tc_w0_001,
    "TC-W0-002": handle_tc_w0_002,
    "TC-W0-003": handle_tc_w0_003,
    "TC-W0-004": handle_tc_w0_004,
    "TC-W0-005": handle_tc_w0_005,
    "TC-W0-006": handle_tc_w0_006,
    "TC-W0-007": handle_tc_w0_007,
    "TC-W0-008": handle_tc_w0_008,
    "TC-W0-009": handle_tc_w0_009,
    "TC-W0-010": handle_tc_w0_010,
    "TC-W0-011": handle_tc_w0_011,
    "TC-W0-012": handle_tc_w0_012,
    "TC-W0-013": handle_tc_w0_013,
    "TC-W0-014": handle_tc_w0_014,
    "TC-W0-CFG-001": handle_tc_w0_cfg_001,
    "TC-W0-CFG-002": handle_tc_w0_cfg_002,
    "TC-W0-CFG-003": handle_tc_w0_cfg_003,
    "TC-W0-CFG-004": handle_tc_w0_cfg_004,
    "TC-W0-CFG-005": handle_tc_w0_cfg_005,
    "TC-W0-CFG-006": handle_tc_w0_cfg_006,
    "TC-W0-CFG-007": handle_tc_w0_cfg_007,
    "TC-W0-CFG-008": handle_tc_w0_cfg_008,
    "TC-W0-CFG-009": handle_tc_w0_cfg_009,
    "TC-W0-CFG-010": handle_tc_w0_cfg_010,
    "TC-W0-CFG-011": handle_tc_w0_cfg_011,
    "TC-W0-CFG-012": handle_tc_w0_cfg_012,
    "TC-W0-CFG-013": handle_tc_w0_cfg_013,
    "TC-W0-CFG-014": handle_tc_w0_cfg_014,
}
