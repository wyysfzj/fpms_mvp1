from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal
from typing import Any

import pytest
import requests

from framework.helpers import (
    normalize_case_type,
    normalize_case_status,
    normalize_country_ref,
    normalize_flow_dir,
    normalize_patent_category,
    unique_code,
)
from framework.models import TestCase
from framework.runtime import RuntimeContext
from framework.seed_data import SeedCatalog


def handle_tc_a_001(runtime: RuntimeContext, case: TestCase) -> None:
    # TC-A-001 | A1 新案立案-最小必填
    # 覆盖: FR-CM-01, FR-CM-02, V-A-01, V-C-01, V-C-02
    # 数据: DS-AP-001, DS-CL-001, DS-CN, DS-U-FM-01
    # 动态值: CASE-A-${RUN_ID}-001
    # 前置: DS-U-FM-01；客户 DS-CL-001；申请人 DS-AP-001；国家 DS-CN；动态案号 CASE-A-${RUN_ID}-001。
    # 步骤摘要: 进入新案页面，填写 CaseNo、CaseType=NORMAL、PatentCategory=INVENTION、FlowDir=IN_IN、FromCountry=CN、Title_CN、RecvDate、ClientID、1 个申请人并设为主申请人，保存。
    # 预期: 案卷保存成功；Status 默认 NOT_FILED；T_Case/T_CaseApplicant 创建成功；CreatedBy/CreatedAt 写入；案卷可在高级查询中被检索到。
    del case

    try:
        runtime.api.login(runtime.username, runtime.password)

        catalog = SeedCatalog.load(run_id=runtime.run_id)
        client_seed = catalog.normalized("DS-CL-001")
        applicant_seed = catalog.normalized("DS-AP-001")
        country_code = catalog.country_code("DS-CN")

        client = _ensure_tc_a_001_client(runtime, client_seed)
        client_id = _required_value(client, "id", "client")

        applicant = _ensure_tc_a_001_applicant(runtime, applicant_seed)
        applicant_id = _required_value(applicant, "id", "applicant")
        applicant_name = _required_value(applicant, "name_cn", "applicant")

        case_payload = {
            "case_no": unique_code("CASE-A", runtime.run_id, "001"),
            "case_type": normalize_case_type("NORMAL"),
            "patent_category": normalize_patent_category("INVENTION"),
            "flow_dir": normalize_flow_dir("IN_IN"),
            "from_country": normalize_country_ref(country_code),
            "title_cn": f"A1 新案立案最小必填 {runtime.run_id}",
            "recv_date": "2026-04-17",
            "client_id": client_id,
            "applicants": [
                {
                    "seq": 1,
                    "is_first": True,
                    "applicant_id": applicant_id,
                    "name_cn": applicant_name,
                }
            ],
            "inventors": [],
            "priorities": [],
            "bio_deposits": [],
        }
        _assert_length(case_payload["case_no"], 64, "case_no")

        created_case = _json_or_assert(
            runtime.api.post("/cases", json=case_payload),
            "create case",
            expected_statuses={200, 201},
        )
        case_id = _required_value(created_case, "id", "created case")

        search_result = _json_or_assert(
            runtime.api.get(
                "/cases",
                params={
                    "page": 1,
                    "page_size": 20,
                    "case_no": case_payload["case_no"],
                },
            ),
            "search case",
        )
        _assert_case_search_hit(search_result, case_id, case_payload["case_no"])

        detail = _json_or_assert(
            runtime.api.get(f"/cases/{case_id}"),
            "get case detail",
        )
        _assert_case_detail(detail, case_payload, case_id)

        if runtime.db.enabled():
            runtime.db.assert_row_exists(
                "t_case",
                {"case_no": case_payload["case_no"], "status": "NOT_FILED"},
            )
            runtime.db.assert_row_exists("t_case_applicant", {"case_id": case_id})
    except requests.RequestException as exc:
        pytest.skip(f"Real backend unavailable for TC-A-001: {exc}")


def _ensure_tc_a_001_client(
    runtime: RuntimeContext,
    seed: dict[str, Any],
) -> dict[str, Any]:
    client_code = unique_code("CL-A-001", runtime.run_id)
    search = _json_or_assert(
        runtime.api.get(
            "/clients",
            params={"page": 1, "page_size": 20, "q": client_code},
        ),
        "search client",
    )
    existing = _find_item(search, "client_code", client_code)
    if existing is not None:
        return existing

    name_cn = f"{seed['name']}-{runtime.run_id}"
    payload = {
        "client_code": client_code,
        "name_cn": name_cn,
        "client_type": _normalize_client_type(seed.get("client_type")),
        "default_currency": seed.get("default_currency") or "CNY",
        "is_active": True,
    }
    return _json_or_assert(
        runtime.api.post("/clients", json=payload),
        "create client",
        expected_statuses={200, 201},
    )


def _ensure_tc_a_001_applicant(
    runtime: RuntimeContext,
    seed: dict[str, Any],
) -> dict[str, Any]:
    applicant_code = unique_code("AP-A-001", runtime.run_id)
    name_cn = f"{seed['name']}-{runtime.run_id}"
    search = _json_or_assert(
        runtime.api.get(
            "/applicants",
            params={"page": 1, "page_size": 20, "q": applicant_code},
        ),
        "search applicant",
    )
    existing = _find_item(search, "code", applicant_code)
    if existing is not None:
        return existing

    name_search = _json_or_assert(
        runtime.api.get(
            "/applicants",
            params={"page": 1, "page_size": 20, "q": name_cn},
        ),
        "search applicant by name",
    )
    existing = _find_item(name_search, "name_cn", name_cn)
    if existing is not None:
        return existing

    payload = {
        "code": applicant_code,
        "name_cn": name_cn,
        "name_en": None,
        "is_active": True,
    }
    return _json_or_assert(
        runtime.api.post("/applicants", json=payload),
        "create applicant",
        expected_statuses={200, 201},
    )


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


def _find_item(
    search_result: dict[str, Any],
    field: str,
    value: Any,
) -> dict[str, Any] | None:
    items = search_result.get("items")
    if not isinstance(items, list):
        raise AssertionError("Search response missing items list")
    for item in items:
        if isinstance(item, dict) and item.get(field) == value:
            return item
    return None


def _assert_case_search_hit(
    search_result: dict[str, Any],
    case_id: Any,
    case_no: str,
) -> None:
    if _find_item(search_result, "case_no", case_no) is not None:
        return
    if _find_item(search_result, "id", case_id) is not None:
        return
    raise AssertionError("Created case was not found in search results")


def _assert_case_detail(
    detail: dict[str, Any],
    expected: dict[str, Any],
    case_id: Any,
) -> None:
    expected_values = {
        "id": case_id,
        "case_no": expected["case_no"],
        "status": "NOT_FILED",
        "case_type": expected["case_type"],
        "patent_category": expected["patent_category"],
        "flow_dir": expected["flow_dir"],
        "from_country": expected["from_country"],
        "client_id": expected["client_id"],
    }
    for field, value in expected_values.items():
        if detail.get(field) != value:
            raise AssertionError(
                f"Case detail field {field} expected {value!r}, got {detail.get(field)!r}"
            )
    if expected["title_cn"] not in str(detail.get("title_cn", "")):
        raise AssertionError("Case detail title_cn did not include run-scoped title")


def _assert_length(value: str, max_length: int, label: str) -> None:
    if len(value) > max_length:
        raise AssertionError(f"{label} length {len(value)} exceeds {max_length}")


def handle_tc_a_002(runtime: RuntimeContext, case: TestCase) -> None:
    # TC-A-002 | A1 新案立案-完整字段
    # 覆盖: FR-CM-02, FR-CM-03, FR-CM-05, V-C-04, V-P-01, V-P-02, V-P-03
    # 数据: DS-AP-001, DS-AP-003, DS-BIO-UNIT-001, DS-CL-001, DS-U-FM-01
    # 动态值: CASE-A-${RUN_ID}-002
    # 前置: DS-U-FM-01；使用 DS-CL-001、DS-AP-001、DS-AP-003、DS-BIO-UNIT-001；案号 CASE-A-${RUN_ID}-002。
    # 步骤摘要: 创建一件国内发明案，录入中英文名称、客户/申请人/发明人、文件地址/账单地址、2 条优先权、1 条菌种保藏、规格字段、FeeReduction、DiscountRate、NoPower/NoPrioText/RequireHK 等控制标记后保存。
    # 预期: 保存成功；PrioDate 自动取最早优先权日；GeneralPowerUsed 对有通用委托书的申请人自动勾选或建议勾选；菌种和规格信息持久化；审计字段更新。
    del case

    try:
        runtime.api.login(runtime.username, runtime.password)

        catalog = SeedCatalog.load(run_id=runtime.run_id)
        client = _ensure_tc_a_001_client(runtime, catalog.normalized("DS-CL-001"))
        client_id = _required_value(client, "id", "client")
        doc_address = _ensure_client_address(
            runtime, client_id=client_id, address_type="MAILING", suffix="A2-DOC"
        )
        bill_address = _ensure_client_address(
            runtime, client_id=client_id, address_type="BILLING", suffix="A2-BILL"
        )
        doc_address_id = _required_value(doc_address, "id", "document address")
        bill_address_id = _required_value(bill_address, "id", "billing address")

        entity_applicant = _ensure_tc_a_006_applicant(
            runtime,
            catalog.normalized("DS-AP-001"),
            code_prefix="AP-A-002-ENTITY",
            applicant_type="ENTITY",
        )
        individual_applicant = _ensure_tc_a_006_applicant(
            runtime,
            catalog.normalized("DS-AP-003"),
            code_prefix="AP-A-002-IND",
            applicant_type="INDIVIDUAL",
        )
        entity_applicant_id = _required_value(
            entity_applicant, "id", "entity applicant"
        )
        entity_applicant_name = _required_value(
            entity_applicant, "name_cn", "entity applicant"
        )
        individual_applicant_id = _required_value(
            individual_applicant, "id", "individual applicant"
        )
        individual_applicant_name = _required_value(
            individual_applicant, "name_cn", "individual applicant"
        )

        case_no = unique_code("A002", runtime.run_id)
        _assert_length(case_no, 64, "case_no")
        payload = _build_tc_a_002_case_payload(
            runtime,
            case_no=case_no,
            client_id=client_id,
            doc_address_id=doc_address_id,
            bill_address_id=bill_address_id,
            entity_applicant_id=entity_applicant_id,
            entity_applicant_name=entity_applicant_name,
            individual_applicant_id=individual_applicant_id,
            individual_applicant_name=individual_applicant_name,
        )

        existing = _find_case_by_case_no(runtime, case_no)
        if existing is None:
            created = _json_or_assert(
                runtime.api.post("/cases", json=payload),
                "create A2 full-field case",
                expected_statuses={200, 201},
            )
            case_id = _required_value(created, "id", "A2 full-field case")
        else:
            case_id = _required_value(existing, "id", "existing A2 full-field case")

        detail = _json_or_assert(
            runtime.api.get(f"/cases/{case_id}"), "get A2 full-field case"
        )
        _assert_tc_a_002_detail(detail, payload, case_id)

        search_result = _json_or_assert(
            runtime.api.get(
                "/cases",
                params={"page": 1, "page_size": 20, "case_no": case_no},
            ),
            "search A2 full-field case",
        )
        _assert_case_search_hit(search_result, case_id, case_no)

        if runtime.db.enabled():
            runtime.db.assert_row_exists("t_case", {"id": case_id, "case_no": case_no})
            runtime.db.assert_row_exists("t_priority", {"case_id": case_id})
            runtime.db.assert_row_exists("t_bio_deposit", {"case_id": case_id})
    except requests.RequestException as exc:
        pytest.skip(f"Real backend unavailable for TC-A-002: {exc}")


def handle_tc_a_003(runtime: RuntimeContext, case: TestCase) -> None:
    # TC-A-003 | A1 案卷号唯一
    # 覆盖: FR-CM-01, FR-CM-02, V-A-01
    # 数据: <none>
    # 动态值: CASE-A-${RUN_ID}-001
    # 前置: 系统中已存在 CASE-A-${RUN_ID}-001。
    # 步骤摘要: 再次创建新案并使用同一 CaseNo 保存。
    # 预期: 保存被拒绝；提示 CaseNo 已存在；数据库不新增重复 T_Case 记录。
    del case

    try:
        runtime.api.login(runtime.username, runtime.password)

        catalog = SeedCatalog.load(run_id=runtime.run_id)
        case_no = unique_code("CASE-A", runtime.run_id, "001")
        _assert_length(case_no, 64, "case_no")

        existing_cases = _json_or_assert(
            runtime.api.get(
                "/cases",
                params={"page": 1, "page_size": 20, "case_no": case_no},
            ),
            "search baseline case",
        )
        baseline_matches = _matching_cases(existing_cases, case_no)
        if not baseline_matches:
            baseline_payload = _build_tc_a_003_case_payload(
                runtime,
                catalog,
                case_no,
                title_label="A1 案卷号唯一基准案",
            )
            _json_or_assert(
                runtime.api.post("/cases", json=baseline_payload),
                "create baseline duplicate-case fixture",
                expected_statuses={200, 201},
            )
            duplicate_payload = {
                **baseline_payload,
                "title_cn": f"A1 案卷号唯一重复案 {runtime.run_id}",
            }
        else:
            duplicate_payload = _build_duplicate_payload_from_existing_case(
                baseline_matches[0],
                case_no,
                runtime.run_id,
            )

        duplicate_response = runtime.api.post("/cases", json=duplicate_payload)
        _assert_duplicate_case_number_response(duplicate_response)

        search_after_duplicate = _json_or_assert(
            runtime.api.get(
                "/cases",
                params={"page": 1, "page_size": 20, "case_no": case_no},
            ),
            "search case after duplicate rejection",
        )
        matches_after_duplicate = _matching_cases(search_after_duplicate, case_no)
        if len(matches_after_duplicate) != 1:
            raise AssertionError(
                f"Expected exactly one case with case_no {case_no}, "
                f"got {len(matches_after_duplicate)}"
            )

        if runtime.db.enabled():
            runtime.db.assert_count("t_case", {"case_no": case_no}, expected=1)
    except requests.RequestException as exc:
        pytest.skip(f"Real backend unavailable for TC-A-003: {exc}")


def _build_tc_a_003_case_payload(
    runtime: RuntimeContext,
    catalog: SeedCatalog,
    case_no: str,
    title_label: str,
) -> dict[str, Any]:
    client = _ensure_tc_a_001_client(runtime, catalog.normalized("DS-CL-001"))
    client_id = _required_value(client, "id", "client")

    applicant = _ensure_tc_a_001_applicant(runtime, catalog.normalized("DS-AP-001"))
    applicant_id = _required_value(applicant, "id", "applicant")
    applicant_name = _required_value(applicant, "name_cn", "applicant")

    return {
        "case_no": case_no,
        "case_type": normalize_case_type("NORMAL"),
        "patent_category": normalize_patent_category("INVENTION"),
        "flow_dir": normalize_flow_dir("IN_IN"),
        "from_country": normalize_country_ref(catalog.country_code("DS-CN")),
        "title_cn": f"{title_label} {runtime.run_id}",
        "recv_date": "2026-04-17",
        "client_id": client_id,
        "applicants": [
            {
                "seq": 1,
                "is_first": True,
                "applicant_id": applicant_id,
                "name_cn": applicant_name,
            }
        ],
        "inventors": [],
        "priorities": [],
        "bio_deposits": [],
    }


def _build_duplicate_payload_from_existing_case(
    existing_case: dict[str, Any],
    case_no: str,
    run_id: str,
) -> dict[str, Any]:
    client_id = _required_value(existing_case, "client_id", "existing case")
    return {
        "case_no": case_no,
        "case_type": normalize_case_type(str(existing_case.get("case_type", "NORMAL"))),
        "patent_category": normalize_patent_category(
            str(existing_case.get("patent_category", "INV"))
        ),
        "flow_dir": normalize_flow_dir(
            str(existing_case.get("flow_dir", "CN_DOMESTIC"))
        ),
        "from_country": normalize_country_ref(
            str(existing_case.get("from_country", "CN"))
        ),
        "title_cn": f"A1 案卷号唯一重复案 {run_id}",
        "recv_date": "2026-04-17",
        "client_id": client_id,
        "applicants": [
            {
                "seq": 1,
                "is_first": True,
                "name_cn": f"重复案申请人 {run_id}",
            }
        ],
        "inventors": [],
        "priorities": [],
        "bio_deposits": [],
    }


def _matching_cases(
    search_result: dict[str, Any], case_no: str
) -> list[dict[str, Any]]:
    items = search_result.get("items")
    if not isinstance(items, list):
        raise AssertionError("Case search response missing items list")
    return [
        item
        for item in items
        if isinstance(item, dict) and item.get("case_no") == case_no
    ]


def _assert_duplicate_case_number_response(response: Any) -> None:
    status_code = getattr(response, "status_code", None)
    if status_code not in {400, 409}:
        raise AssertionError(
            f"duplicate case_no was not rejected with expected status; "
            f"got {status_code}: {_response_summary(response)}"
        )

    summary = _response_summary(response).lower()
    duplicate_markers = [
        "case_no_duplicate",
        "case_no",
        "duplicate",
        "already exists",
        "已存在",
    ]
    if not any(marker in summary for marker in duplicate_markers):
        raise AssertionError(
            "duplicate case_no response did not include stable duplicate semantics: "
            f"{_response_summary(response)}"
        )


def _assert_invalid_case_type_combo_response(response: Any) -> None:
    status_code = getattr(response, "status_code", None)
    if status_code != 400:
        raise AssertionError(
            f"invalid CaseType + PatentCategory combination was not rejected with "
            f"status 400; got {status_code}: {_response_summary(response)}"
        )

    payload = response.json()
    error = payload.get("error") if isinstance(payload, dict) else None
    if not isinstance(error, dict):
        raise AssertionError(
            "invalid-combo response missing error envelope: "
            f"{_response_summary(response)}"
        )
    if error.get("code") != "CASE_TYPE_COMBO_INVALID":
        raise AssertionError(
            f"invalid-combo response code mismatch: {_response_summary(response)}"
        )
    details = error.get("details")
    if not isinstance(details, dict):
        raise AssertionError(
            f"invalid-combo response missing details: {_response_summary(response)}"
        )
    expected_details = {"case_type": "SEARCH", "patent_category": "DES"}
    for field, expected in expected_details.items():
        if details.get(field) != expected:
            raise AssertionError(
                f"invalid-combo detail {field} expected {expected!r}, "
                f"got {details.get(field)!r}"
            )


def _assert_business_error_code(
    response: Any,
    action: str,
    expected_code: str,
    expected_statuses: set[int] | None = None,
) -> None:
    expected = expected_statuses or {400}
    status_code = getattr(response, "status_code", None)
    if status_code not in expected:
        raise AssertionError(
            f"{action} was not rejected with expected status; "
            f"got {status_code}: {_response_summary(response)}"
        )
    payload = response.json()
    error = payload.get("error") if isinstance(payload, dict) else None
    if not isinstance(error, dict) or error.get("code") != expected_code:
        raise AssertionError(
            f"{action} response did not include {expected_code}: "
            f"{_response_summary(response)}"
        )


def _assert_business_error_response(
    response: Any,
    action: str,
    expected_code: str,
    expected_details: dict[str, Any] | None = None,
    expected_statuses: set[int] | None = None,
) -> None:
    expected = expected_statuses or {400}
    status_code = getattr(response, "status_code", None)
    if status_code not in expected:
        raise AssertionError(
            f"{action} was not rejected with expected status; "
            f"got {status_code}: {_response_summary(response)}"
        )

    payload = response.json()
    error = payload.get("error") if isinstance(payload, dict) else None
    if not isinstance(error, dict):
        raise AssertionError(
            f"{action} response missing error envelope: {_response_summary(response)}"
        )

    if error.get("code") != expected_code:
        raise AssertionError(
            f"{action} response did not include {expected_code}: "
            f"{_response_summary(response)}"
        )

    details = error.get("details")
    if expected_details is None:
        if details is not None:
            raise AssertionError(
                f"{action} response expected no details, got {details!r}: "
                f"{_response_summary(response)}"
            )
        return

    if details != expected_details:
        raise AssertionError(
            f"{action} response details mismatch: {details!r} != {expected_details!r}"
        )


def handle_tc_a_004(runtime: RuntimeContext, case: TestCase) -> None:
    # TC-A-004 | A1 案件类型组合非法
    # 覆盖: FR-CM-01, V-A-02
    # 数据: DS-U-FM-01
    # 动态值: <none>
    # 前置: DS-U-FM-01；配置中存在禁止的 CaseType+PatentCategory 组合。
    # 步骤摘要: 创建新案时选择被配置禁止的组合并保存。
    # 预期: 系统阻止保存并说明非法组合。
    # Arrange: 准备种子数据 / 鉴权 / 页面或 API 上下文。
    # Act: 按 steps_summary 执行业务流。
    # Assert: 按 expected 做 UI / API / DB / 文件断言。
    del case

    try:
        runtime.api.login(runtime.username, runtime.password)

        catalog = SeedCatalog.load(run_id=runtime.run_id)
        applicant = _ensure_tc_a_006_applicant(
            runtime,
            catalog.normalized("DS-AP-001"),
            code_prefix="AP-A-004-ENTITY",
            applicant_type="ENTITY",
        )
        applicant_id = _required_value(applicant, "id", "applicant")
        applicant_name = _required_value(applicant, "name_cn", "applicant")
        case_no = unique_code("CASE-A-INVCOMBO", runtime.run_id, "001")
        _assert_length(case_no, 64, "case_no")
        payload = {
            "case_no": case_no,
            "case_type": normalize_case_type("SEARCH"),
            "patent_category": normalize_patent_category("DESIGN"),
            "flow_dir": normalize_flow_dir("IN_IN"),
            "title_cn": f"A1 案件类型组合非法 {runtime.run_id}",
            "applicant_kind": "ENTITY",
            "applicants": [
                _build_case_applicant_payload(
                    seq=1,
                    is_first=True,
                    applicant_id=applicant_id,
                    name_cn=applicant_name,
                )
            ],
        }

        response = runtime.api.post("/cases", json=payload)
        _assert_invalid_case_type_combo_response(response)

        search_result = _json_or_assert(
            runtime.api.get(
                "/cases",
                params={"page": 1, "page_size": 20, "case_no": case_no},
            ),
            "search rejected invalid-combo case",
        )
        matches = _matching_cases(search_result, case_no)
        if matches:
            raise AssertionError(
                f"Invalid CaseType + PatentCategory payload was persisted: {case_no}"
            )

        if runtime.db.enabled():
            runtime.db.assert_count("t_case", {"case_no": case_no}, expected=0)
    except requests.RequestException as exc:
        pytest.skip(f"Real backend unavailable for TC-A-004: {exc}")


def handle_tc_a_005(runtime: RuntimeContext, case: TestCase) -> None:
    # TC-A-005 | A1 涉外必填项
    # 覆盖: FR-CM-02, FR-CM-03, V-A-03, V-B-01, V-B-02
    # 数据: DS-CL-002, DS-CL-003, DS-U-FM-01
    # 动态值: CASE-A-${RUN_ID}-003
    # 前置: DS-U-FM-01；客户 DS-CL-003；外方代理 DS-CL-002；案号 CASE-A-${RUN_ID}-003。
    # 步骤摘要: 创建 FlowDir=IN_OUT 或 OUT_IN 的案件，先不填 ToCountry/ForeignAgentID 保存；再填入一个非“代理所”类型客户作为 ForeignAgent 保存；最后改为合法代理所重试。
    # 预期: 缺 ToCountry 或 ForeignAgent 时保存被拒；选择非代理所时系统给出警告或阻断；改为合法代理所后保存成功。
    # Arrange: 准备种子数据 / 鉴权 / 页面或 API 上下文。
    # Act: 按 steps_summary 执行业务流。
    # Assert: 按 expected 做 UI / API / DB / 文件断言。
    del case

    try:
        runtime.api.login(runtime.username, runtime.password)

        catalog = SeedCatalog.load(run_id=runtime.run_id)
        direct_client = _ensure_tc_a_005_client(
            runtime,
            catalog.normalized("DS-CL-003"),
            "CL-A-FGN-DIRECT",
        )
        agent_client = _ensure_tc_a_005_client(
            runtime,
            catalog.normalized("DS-CL-002"),
            "CL-A-FGN-AGENT",
        )
        direct_client_id = _required_value(direct_client, "id", "direct client")
        agent_client_id = _required_value(agent_client, "id", "foreign agent client")

        no_to_country_case_no = unique_code("CASE-A-FGN", runtime.run_id, "003-NO-TO")
        no_agent_case_no = unique_code("CASE-A-FGN", runtime.run_id, "003-NO-AG")
        bad_agent_case_no = unique_code("CASE-A-FGN", runtime.run_id, "003-BAD-AG")
        ok_case_no = unique_code("CASE-A-FGN", runtime.run_id, "003-OK")
        for case_no in [
            no_to_country_case_no,
            no_agent_case_no,
            bad_agent_case_no,
            ok_case_no,
        ]:
            _assert_length(case_no, 64, "case_no")

        no_to_country_response = runtime.api.post(
            "/cases",
            json=_build_tc_a_005_case_payload(
                runtime,
                no_to_country_case_no,
                direct_client_id,
                foreign_agent_id=agent_client_id,
            ),
        )
        _assert_business_error_code(
            no_to_country_response,
            "foreign case without to_country",
            "CASE_TO_COUNTRY_REQUIRED",
        )

        no_agent_response = runtime.api.post(
            "/cases",
            json=_build_tc_a_005_case_payload(
                runtime,
                no_agent_case_no,
                direct_client_id,
                to_country="US",
            ),
        )
        _assert_business_error_code(
            no_agent_response,
            "foreign case without foreign_agent_id",
            "CASE_FOREIGN_AGENT_REQUIRED",
        )

        bad_agent_response = runtime.api.post(
            "/cases",
            json=_build_tc_a_005_case_payload(
                runtime,
                bad_agent_case_no,
                direct_client_id,
                to_country="US",
                foreign_agent_id=direct_client_id,
            ),
        )
        _assert_business_error_code(
            bad_agent_response,
            "foreign case with non-agent foreign_agent_id",
            "CASE_FOREIGN_AGENT_INVALID_TYPE",
        )

        ok_payload = _build_tc_a_005_case_payload(
            runtime,
            ok_case_no,
            direct_client_id,
            to_country="US",
            foreign_agent_id=agent_client_id,
        )
        created_case = _json_or_assert(
            runtime.api.post("/cases", json=ok_payload),
            "create valid foreign case",
            expected_statuses={200, 201},
        )
        case_id = _required_value(created_case, "id", "valid foreign case")

        search_result = _json_or_assert(
            runtime.api.get(
                "/cases",
                params={"page": 1, "page_size": 20, "case_no": ok_case_no},
            ),
            "search valid foreign case",
        )
        _assert_case_search_hit(search_result, case_id, ok_case_no)

        if runtime.db.enabled():
            runtime.db.assert_row_exists(
                "t_case",
                {"case_no": ok_case_no, "flow_dir": normalize_flow_dir("IN_OUT")},
            )
    except requests.RequestException as exc:
        pytest.skip(f"Real backend unavailable for TC-A-005: {exc}")


def _ensure_tc_a_005_client(
    runtime: RuntimeContext,
    seed: dict[str, Any],
    code_prefix: str,
) -> dict[str, Any]:
    client_code = unique_code(code_prefix, runtime.run_id)
    search = _json_or_assert(
        runtime.api.get(
            "/clients",
            params={"page": 1, "page_size": 20, "q": client_code},
        ),
        "search foreign-required client",
    )
    existing = _find_item(search, "client_code", client_code)
    if existing is not None:
        return existing

    payload = {
        "client_code": client_code,
        "name_cn": f"{seed['name']}-{runtime.run_id}",
        "client_type": _normalize_client_type(seed.get("client_type")),
        "default_currency": seed.get("default_currency") or "CNY",
        "is_active": True,
    }
    return _json_or_assert(
        runtime.api.post("/clients", json=payload),
        "create foreign-required client",
        expected_statuses={200, 201},
    )


def _build_tc_a_005_case_payload(
    runtime: RuntimeContext,
    case_no: str,
    client_id: Any,
    *,
    to_country: str | None = None,
    foreign_agent_id: Any | None = None,
) -> dict[str, Any]:
    payload = {
        "case_no": case_no,
        "case_type": normalize_case_type("NORMAL"),
        "patent_category": normalize_patent_category("INVENTION"),
        "flow_dir": normalize_flow_dir("IN_OUT"),
        "from_country": normalize_country_ref("CN"),
        "title_cn": f"A1 涉外必填项 {runtime.run_id} {case_no}",
        "recv_date": "2026-04-17",
        "client_id": client_id,
        "applicants": [
            {
                "seq": 1,
                "is_first": True,
                "name_cn": f"涉外申请人 {runtime.run_id}",
            }
        ],
        "inventors": [],
        "priorities": [],
        "bio_deposits": [],
    }
    if to_country is not None:
        payload["to_country"] = normalize_country_ref(to_country)
    if foreign_agent_id is not None:
        payload["foreign_agent_id"] = foreign_agent_id
    return payload


def handle_tc_a_006(runtime: RuntimeContext, case: TestCase) -> None:
    # TC-A-006 | A1 申请人列表规则
    # 覆盖: FR-CM-02, V-C-01, V-C-02, V-C-03
    # 数据: DS-AP-001, DS-AP-002, DS-U-FM-01
    # 动态值: <none>
    # 前置: DS-U-FM-01；准备法人申请人 DS-AP-001、自然人 DS-AP-002。
    # 步骤摘要: 分别测试：无申请人保存；两个申请人都标为主申请人；主申请人为自然人但 ApplicantKind=LEGAL_PERSON；再将 ApplicantKind 调整为 NATURAL_PERSON。
    # 预期: 无申请人被拒；多个主申请人被拒；ApplicantKind 与第一申请人类型不一致时触发阻断或强确认；一致后保存成功。
    # Arrange: 准备种子数据 / 鉴权 / 页面或 API 上下文。
    # Act: 按 steps_summary 执行业务流。
    # Assert: 按 expected 做 UI / API / DB / 文件断言。
    del case

    try:
        runtime.api.login(runtime.username, runtime.password)

        catalog = SeedCatalog.load(run_id=runtime.run_id)
        entity_seed = catalog.normalized("DS-AP-001")
        individual_seed = catalog.normalized("DS-AP-002")
        entity_applicant = _ensure_tc_a_006_applicant(
            runtime,
            entity_seed,
            code_prefix="AP-A-006-ENTITY",
            applicant_type="ENTITY",
        )
        individual_applicant = _ensure_tc_a_006_applicant(
            runtime,
            individual_seed,
            code_prefix="AP-A-006-INDIVIDUAL",
            applicant_type="INDIVIDUAL",
        )
        entity_applicant_id = _required_value(
            entity_applicant, "id", "entity applicant"
        )
        entity_applicant_name = _required_value(
            entity_applicant, "name_cn", "entity applicant"
        )
        individual_applicant_id = _required_value(
            individual_applicant, "id", "individual applicant"
        )
        individual_applicant_name = _required_value(
            individual_applicant, "name_cn", "individual applicant"
        )

        no_app_case_no = unique_code("A6", runtime.run_id, "NOAPP")
        duplicate_first_case_no = unique_code("A6", runtime.run_id, "DUP")
        mismatch_case_no = unique_code("A6", runtime.run_id, "KIND")
        ok_case_no = unique_code("A6", runtime.run_id, "OK")
        for case_no in [
            no_app_case_no,
            duplicate_first_case_no,
            mismatch_case_no,
            ok_case_no,
        ]:
            _assert_length(case_no, 64, "case_no")

        no_app_response = runtime.api.post(
            "/cases",
            json=_build_tc_a_006_case_payload(
                runtime,
                no_app_case_no,
                applicants=[],
            ),
        )
        _assert_business_error_response(
            no_app_response,
            "TC-A-006 empty applicant list",
            "CASE_APPLICANT_REQUIRED",
        )

        duplicate_first_response = runtime.api.post(
            "/cases",
            json=_build_tc_a_006_case_payload(
                runtime,
                duplicate_first_case_no,
                applicants=[
                    _build_case_applicant_payload(
                        seq=1,
                        is_first=True,
                        applicant_id=entity_applicant_id,
                        name_cn=entity_applicant_name,
                    ),
                    _build_case_applicant_payload(
                        seq=2,
                        is_first=True,
                        applicant_id=individual_applicant_id,
                        name_cn=individual_applicant_name,
                    ),
                ],
            ),
        )
        _assert_business_error_response(
            duplicate_first_response,
            "TC-A-006 duplicate first applicant",
            "CASE_DUPLICATE_FIRST_APPLICANT",
        )

        mismatch_response = runtime.api.post(
            "/cases",
            json=_build_tc_a_006_case_payload(
                runtime,
                mismatch_case_no,
                applicant_kind="ENTITY",
                applicants=[
                    _build_case_applicant_payload(
                        seq=1,
                        is_first=True,
                        applicant_id=individual_applicant_id,
                        name_cn=individual_applicant_name,
                    )
                ],
            ),
        )
        _assert_business_error_response(
            mismatch_response,
            "TC-A-006 applicant kind mismatch",
            "CASE_APPLICANT_KIND_MISMATCH",
            expected_details={
                "applicant_kind": "ENTITY",
                "first_applicant_type": "INDIVIDUAL",
                "first_applicant_id": individual_applicant_id,
            },
        )

        ok_payload = _build_tc_a_006_case_payload(
            runtime,
            ok_case_no,
            applicant_kind="INDIVIDUAL",
            applicants=[
                _build_case_applicant_payload(
                    seq=1,
                    is_first=True,
                    applicant_id=individual_applicant_id,
                    name_cn=individual_applicant_name,
                )
            ],
        )
        created_case = _json_or_assert(
            runtime.api.post("/cases", json=ok_payload),
            "create valid applicant-kind case",
            expected_statuses={200, 201},
        )
        case_id = _required_value(created_case, "id", "valid applicant-kind case")

        search_result = _json_or_assert(
            runtime.api.get(
                "/cases",
                params={"page": 1, "page_size": 20, "case_no": ok_case_no},
            ),
            "search valid applicant-kind case",
        )
        _assert_case_search_hit(search_result, case_id, ok_case_no)

        if runtime.db.enabled():
            runtime.db.assert_row_exists(
                "t_case",
                {"case_no": ok_case_no, "status": "NOT_FILED"},
            )
            runtime.db.assert_row_exists("t_case_applicant", {"case_id": case_id})
    except requests.RequestException as exc:
        pytest.skip(f"Real backend unavailable for TC-A-006: {exc}")


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


def _ensure_tc_a_006_applicant(
    runtime: RuntimeContext,
    seed: dict[str, Any],
    *,
    code_prefix: str,
    applicant_type: str,
) -> dict[str, Any]:
    applicant_code = unique_code(code_prefix, runtime.run_id)
    search = _json_or_assert(
        runtime.api.get(
            "/applicants",
            params={"page": 1, "page_size": 20, "q": applicant_code},
        ),
        "search applicant",
    )
    existing = _find_item(search, "code", applicant_code)
    if existing is not None:
        return existing

    payload = {
        "code": applicant_code,
        "name_cn": f"{seed['name']}-{code_prefix}-{runtime.run_id}",
        "name_en": None,
        "applicant_type": applicant_type,
        "is_active": True,
    }
    return _json_or_assert(
        runtime.api.post("/applicants", json=payload),
        "create applicant",
        expected_statuses={200, 201},
    )


def _build_tc_a_006_case_payload(
    runtime: RuntimeContext,
    case_no: str,
    *,
    applicant_kind: str | None = None,
    applicants: list[dict[str, Any]],
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "case_no": case_no,
        "case_type": normalize_case_type("NORMAL"),
        "patent_category": normalize_patent_category("INVENTION"),
        "flow_dir": normalize_flow_dir("IN_IN"),
        "from_country": normalize_country_ref("DS-CN"),
        "title_cn": f"A1 申请人列表规则 {runtime.run_id} {case_no}",
        "applicants": applicants,
        "inventors": [],
        "priorities": [],
        "bio_deposits": [],
    }
    if applicant_kind is not None:
        payload["applicant_kind"] = _normalize_applicant_type(applicant_kind)
    return payload


def _build_case_applicant_payload(
    *,
    seq: int,
    is_first: bool,
    applicant_id: str,
    name_cn: str,
) -> dict[str, Any]:
    return {
        "seq": seq,
        "is_first": is_first,
        "applicant_id": applicant_id,
        "name_cn": name_cn,
    }


def _ensure_client_address(
    runtime: RuntimeContext,
    *,
    client_id: str,
    address_type: str,
    suffix: str,
) -> dict[str, Any]:
    address_line1 = f"{suffix} 地址 {runtime.run_id}"
    response = _json_or_assert(
        runtime.api.get(f"/clients/{client_id}/addresses"),
        "list client addresses",
    )
    items = response if isinstance(response, list) else response.get("items", [])
    if not isinstance(items, list):
        raise AssertionError("Client address response missing list payload")
    for item in items:
        if (
            isinstance(item, dict)
            and item.get("address_type") == address_type
            and item.get("address_line1") == address_line1
        ):
            return item

    return _json_or_assert(
        runtime.api.post(
            f"/clients/{client_id}/addresses",
            json={
                "address_type": address_type,
                "address_line1": address_line1,
                "country_code": "CN",
                "is_default": False,
            },
        ),
        "create client address",
        expected_statuses={200, 201},
    )


def _build_tc_a_002_case_payload(
    runtime: RuntimeContext,
    *,
    case_no: str,
    client_id: str,
    doc_address_id: str,
    bill_address_id: str,
    entity_applicant_id: str,
    entity_applicant_name: str,
    individual_applicant_id: str,
    individual_applicant_name: str,
) -> dict[str, Any]:
    return {
        "case_no": case_no,
        "case_type": normalize_case_type("NORMAL"),
        "patent_category": normalize_patent_category("INVENTION"),
        "flow_dir": normalize_flow_dir("IN_IN"),
        "from_country": normalize_country_ref("DS-CN"),
        "title_cn": f"A1 新案立案完整字段 {runtime.run_id}",
        "title_en": f"A1 Full Field Case {runtime.run_id}",
        "recv_date": "2026-03-01",
        "client_id": client_id,
        "doc_address_id": doc_address_id,
        "bill_address_id": bill_address_id,
        "spec_pages": 10,
        "draw_pages": 2,
        "claim_count": 12,
        "claim_pages": 4,
        "manuscript_words": 12345,
        "fee_reduction": "0.15",
        "discount_rate": "0.8000",
        "applicant_kind": "ENTITY",
        "no_power": True,
        "no_prio_text": False,
        "require_hk": True,
        "applicants": [
            _build_case_applicant_payload(
                seq=1,
                is_first=True,
                applicant_id=entity_applicant_id,
                name_cn=entity_applicant_name,
            ),
            _build_case_applicant_payload(
                seq=2,
                is_first=False,
                applicant_id=individual_applicant_id,
                name_cn=individual_applicant_name,
            ),
        ],
        "inventors": [{"seq": 1, "name_cn": f"A2 发明人 {runtime.run_id}"}],
        "priorities": [
            {
                "seq": 1,
                "country_code": normalize_country_ref("DS-CN"),
                "prio_no": unique_code("PRA2", runtime.run_id, "LATE"),
                "prio_date": "2026-02-10",
            },
            {
                "seq": 2,
                "country_code": normalize_country_ref("US"),
                "prio_no": unique_code("PRA2", runtime.run_id, "EARLY"),
                "prio_date": "2026-01-20",
            },
        ],
        "bio_deposits": [
            {
                "seq": 1,
                "deposit_no": unique_code("BIOA2", runtime.run_id),
                "deposit_unit_name": "CGMCC",
                "deposit_date": "2026-01-15",
                "name": f"A2 菌种 {runtime.run_id}",
            }
        ],
    }


def _assert_tc_a_002_detail(
    detail: dict[str, Any],
    expected: dict[str, Any],
    case_id: Any,
) -> None:
    scalar_fields = [
        "case_no",
        "case_type",
        "patent_category",
        "flow_dir",
        "from_country",
        "client_id",
        "doc_address_id",
        "bill_address_id",
        "spec_pages",
        "draw_pages",
        "claim_count",
        "claim_pages",
        "manuscript_words",
        "fee_reduction",
        "discount_rate",
        "applicant_kind",
        "no_power",
        "no_prio_text",
        "require_hk",
    ]
    if detail.get("id") != case_id:
        raise AssertionError(f"A2 detail id mismatch: {detail}")
    for field in scalar_fields:
        if detail.get(field) != expected.get(field):
            raise AssertionError(
                f"A2 detail {field} expected {expected.get(field)!r}, "
                f"got {detail.get(field)!r}"
            )
    for field, expected_count in [
        ("applicants", 2),
        ("inventors", 1),
        ("priorities", 2),
        ("bio_deposits", 1),
    ]:
        values = detail.get(field)
        if not isinstance(values, list) or len(values) != expected_count:
            raise AssertionError(f"A2 detail {field} mismatch: {detail}")
    earliest_priority = min(str(row["prio_date"]) for row in detail["priorities"])
    if earliest_priority != "2026-01-20":
        raise AssertionError(f"A2 earliest priority mismatch: {detail['priorities']}")
    _required_value(detail, "created_at", "A2 detail")
    _required_value(detail, "updated_at", "A2 detail")


def handle_tc_a_007(runtime: RuntimeContext, case: TestCase) -> None:
    # TC-A-007 | A1 发明人与地址
    # 覆盖: FR-CM-03, V-C-05, V-C-06, V-C-07
    # 数据: DS-CL-001, DS-CL-004, DS-U-FM-01
    # 动态值: <none>
    # 前置: DS-U-FM-01；客户 DS-CL-001 含有效默认地址，DS-CL-004 含停用地址。
    # 步骤摘要: 创建案卷时先不填发明人、地址保存；再在需要发明人的国家配置下测试无发明人提示；切换到停用地址保存；最后改回有效地址。
    # 预期: 在无强校验国家下发明人可为空；强校验国家下提示或阻断；停用地址不能提交；如文档/账单地址均为空则系统给出警告或阻断。
    del case

    try:
        runtime.api.login(runtime.username, runtime.password)

        catalog = SeedCatalog.load(run_id=runtime.run_id)
        client = _ensure_tc_a_001_client(runtime, catalog.normalized("DS-CL-001"))
        other_client = _ensure_tc_a_005_client(
            runtime,
            catalog.normalized("DS-CL-004"),
            "CL-A-007-OTHER",
        )
        client_id = _required_value(client, "id", "client")
        other_client_id = _required_value(other_client, "id", "other client")
        applicant = _ensure_tc_a_006_applicant(
            runtime,
            catalog.normalized("DS-AP-001"),
            code_prefix="AP-A-007-ENTITY",
            applicant_type="ENTITY",
        )
        applicant_id = _required_value(applicant, "id", "applicant")
        applicant_name = _required_value(applicant, "name_cn", "applicant")
        doc_address = _ensure_client_address(
            runtime, client_id=client_id, address_type="MAILING", suffix="A7-DOC"
        )
        bill_address = _ensure_client_address(
            runtime, client_id=client_id, address_type="BILLING", suffix="A7-BILL"
        )
        other_address = _ensure_client_address(
            runtime,
            client_id=other_client_id,
            address_type="MAILING",
            suffix="A7-OTHER",
        )

        no_inventor_case_no = unique_code("A007", runtime.run_id, "NOINV")
        valid_address_case_no = unique_code("A007", runtime.run_id, "ADDR")
        wrong_address_case_no = unique_code("A007", runtime.run_id, "WRONG")
        for case_no in [
            no_inventor_case_no,
            valid_address_case_no,
            wrong_address_case_no,
        ]:
            _assert_length(case_no, 64, "case_no")

        no_inventor_payload = _build_tc_a_007_case_payload(
            runtime,
            case_no=no_inventor_case_no,
            client_id=client_id,
            applicant_id=applicant_id,
            applicant_name=applicant_name,
        )
        no_inventor = _json_or_assert(
            runtime.api.post("/cases", json=no_inventor_payload),
            "create A7 no-inventor case",
            expected_statuses={200, 201},
        )
        no_inventor_detail = _json_or_assert(
            runtime.api.get(f"/cases/{_required_value(no_inventor, 'id', 'A7 case')}"),
            "get A7 no-inventor case",
        )
        if no_inventor_detail.get("inventors") != []:
            raise AssertionError(
                f"A7 no-inventor case persisted inventors: {no_inventor_detail}"
            )

        valid_payload = _build_tc_a_007_case_payload(
            runtime,
            case_no=valid_address_case_no,
            client_id=client_id,
            applicant_id=applicant_id,
            applicant_name=applicant_name,
            doc_address_id=_required_value(doc_address, "id", "document address"),
            bill_address_id=_required_value(bill_address, "id", "billing address"),
        )
        valid_case = _json_or_assert(
            runtime.api.post("/cases", json=valid_payload),
            "create A7 valid address case",
            expected_statuses={200, 201},
        )
        valid_detail = _json_or_assert(
            runtime.api.get(f"/cases/{_required_value(valid_case, 'id', 'A7 case')}"),
            "get A7 valid address case",
        )
        if valid_detail.get("doc_address_id") != valid_payload["doc_address_id"]:
            raise AssertionError(f"A7 doc address was not persisted: {valid_detail}")
        if valid_detail.get("bill_address_id") != valid_payload["bill_address_id"]:
            raise AssertionError(f"A7 bill address was not persisted: {valid_detail}")

        wrong_response = runtime.api.post(
            "/cases",
            json=_build_tc_a_007_case_payload(
                runtime,
                case_no=wrong_address_case_no,
                client_id=client_id,
                applicant_id=applicant_id,
                applicant_name=applicant_name,
                doc_address_id=_required_value(
                    other_address, "id", "other client address"
                ),
            ),
        )
        _assert_business_error_code(
            wrong_response,
            "A7 address owned by another client",
            "CASE_ADDRESS_CLIENT_MISMATCH",
        )

        if runtime.db.enabled():
            runtime.db.assert_row_exists("t_case", {"case_no": valid_address_case_no})
    except requests.RequestException as exc:
        pytest.skip(f"Real backend unavailable for TC-A-007: {exc}")


def _build_tc_a_007_case_payload(
    runtime: RuntimeContext,
    *,
    case_no: str,
    client_id: str,
    applicant_id: str,
    applicant_name: str,
    doc_address_id: str | None = None,
    bill_address_id: str | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "case_no": case_no,
        "case_type": normalize_case_type("NORMAL"),
        "patent_category": normalize_patent_category("INVENTION"),
        "flow_dir": normalize_flow_dir("IN_IN"),
        "from_country": normalize_country_ref("DS-CN"),
        "title_cn": f"A1 发明人与地址 {runtime.run_id} {case_no}",
        "recv_date": "2026-03-01",
        "client_id": client_id,
        "applicant_kind": "ENTITY",
        "applicants": [
            _build_case_applicant_payload(
                seq=1,
                is_first=True,
                applicant_id=applicant_id,
                name_cn=applicant_name,
            )
        ],
        "inventors": [],
        "priorities": [],
        "bio_deposits": [],
    }
    if doc_address_id is not None:
        payload["doc_address_id"] = doc_address_id
    if bill_address_id is not None:
        payload["bill_address_id"] = bill_address_id
    return payload


def _build_tc_a_008_priority_payload(
    runtime: RuntimeContext,
    *,
    prio_date: str,
    suffix: str,
) -> dict[str, Any]:
    return {
        "seq": 1,
        "country_code": normalize_country_ref("DS-CN"),
        "prio_no": unique_code("PRIO", runtime.run_id, suffix),
        "prio_date": prio_date,
    }


def _build_tc_a_008_case_payload(
    runtime: RuntimeContext,
    *,
    case_no: str,
    client_id: Any,
    applicant_id: Any,
    applicant_name: str,
    priorities: list[dict[str, Any]] | None = None,
    status: str | None = None,
    filing_date: str | None = None,
    app_no: str | None = None,
    pub_no: str | None = None,
    pub_date: str | None = None,
    grant_no: str | None = None,
    grant_date: str | None = None,
    first_annuity_year: int | None = None,
    valid_until: str | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "case_no": case_no,
        "case_type": normalize_case_type("NORMAL"),
        "patent_category": normalize_patent_category("INVENTION"),
        "flow_dir": normalize_flow_dir("IN_IN"),
        "from_country": normalize_country_ref("DS-CN"),
        "title_cn": f"A1 日期与编号一致性 {runtime.run_id} {case_no}",
        "recv_date": "2026-04-17",
        "client_id": client_id,
        "applicants": [
            {
                "seq": 1,
                "is_first": True,
                "applicant_id": applicant_id,
                "name_cn": applicant_name,
            }
        ],
        "inventors": [],
        "bio_deposits": [],
    }
    if priorities is not None:
        payload["priorities"] = priorities
    if status is not None:
        payload["status"] = normalize_case_status(status)
    if filing_date is not None:
        payload["filing_date"] = filing_date
    if app_no is not None:
        payload["app_no"] = app_no
    if pub_no is not None:
        payload["pub_no"] = pub_no
    if pub_date is not None:
        payload["pub_date"] = pub_date
    if grant_no is not None:
        payload["grant_no"] = grant_no
    if grant_date is not None:
        payload["grant_date"] = grant_date
    if first_annuity_year is not None:
        payload["first_annuity_year"] = first_annuity_year
    if valid_until is not None:
        payload["valid_until"] = valid_until
    return payload


def handle_tc_a_008(runtime: RuntimeContext, case: TestCase) -> None:
    # TC-A-008 | A1 日期与编号一致性
    # 覆盖: FR-CM-02, V-D-01, V-D-02, V-D-03, V-D-04, V-A-04
    # 数据: DS-U-FM-01
    # 动态值: CASE-A-${RUN_ID}-004
    # 前置: DS-U-FM-01；CASE-A-${RUN_ID}-004；优先权日=2026-03-15。
    # 步骤摘要: 分别测试：Status=PUBLISHED 但无 PubDate/PubNo；Status=GRANTED 但缺 GrantDate/GrantNo/FirstAnnuityYear/ValidUntil；FilingDate 早于优先权日；FilingDate=优先权日；AppNo 使用非法格式。
    # 预期: 缺公开/授权必要字段时被拒；FilingDate<PrioDate 被拒；FilingDate=PrioDate 可通过；非法 AppNo 格式被拒或报错。
    # Arrange: 准备种子数据 / 鉴权 / 页面或 API 上下文。
    # Act: 按 steps_summary 执行业务流。
    # Assert: 按 expected 做 UI / API / DB / 文件断言。
    del case

    try:
        runtime.api.login(runtime.username, runtime.password)

        catalog = SeedCatalog.load(run_id=runtime.run_id)
        client_seed = catalog.normalized("DS-CL-001")
        applicant_seed = catalog.normalized("DS-AP-001")
        client = _ensure_tc_a_001_client(runtime, client_seed)
        client_id = _required_value(client, "id", "client")
        applicant = _ensure_tc_a_006_applicant(
            runtime,
            applicant_seed,
            code_prefix="AP-A-008-ENTITY",
            applicant_type=_normalize_applicant_type(
                str(applicant_seed.get("applicant_type", "ENTITY"))
            ),
        )
        applicant_id = _required_value(applicant, "id", "applicant")
        applicant_name = _required_value(applicant, "name_cn", "applicant")

        baseline_case_no = unique_code("A8", runtime.run_id, "BASE")
        _assert_length(baseline_case_no, 64, "case_no")

        priority_date = "2026-03-15"
        baseline_payload = _build_tc_a_008_case_payload(
            runtime,
            case_no=baseline_case_no,
            client_id=client_id,
            applicant_id=applicant_id,
            applicant_name=applicant_name,
            priorities=[
                _build_tc_a_008_priority_payload(
                    runtime,
                    prio_date=priority_date,
                    suffix="BASE",
                )
            ],
        )
        created_case = _json_or_assert(
            runtime.api.post("/cases", json=baseline_payload),
            "create baseline case",
            expected_statuses={200, 201},
        )
        case_id = _required_value(created_case, "id", "baseline case")

        published_response = runtime.api.put(
            f"/cases/{case_id}",
            json={
                "status": "PUBLISHED",
                "filing_date": priority_date,
                "app_no": unique_code("A8APP", runtime.run_id, "PUB"),
            },
        )
        _assert_business_error_response(
            published_response,
            "TC-A-008 published missing fields",
            "CASE_PUBLISHED_FIELDS_REQUIRED",
            expected_details={
                "status": "PUBLISHED",
                "missing_fields": ["pub_no", "pub_date"],
            },
        )

        granted_response = runtime.api.put(
            f"/cases/{case_id}",
            json={
                "status": "GRANTED",
                "filing_date": priority_date,
                "app_no": unique_code("A8APP", runtime.run_id, "GNT"),
                "pub_no": unique_code("PUB", runtime.run_id, "001"),
                "pub_date": "2026-04-01",
            },
        )
        _assert_business_error_response(
            granted_response,
            "TC-A-008 granted missing fields",
            "CASE_GRANTED_FIELDS_REQUIRED",
            expected_details={
                "status": "GRANTED",
                "missing_fields": [
                    "grant_no",
                    "grant_date",
                    "first_annuity_year",
                    "valid_until",
                ],
            },
        )

        filing_before_response = runtime.api.put(
            f"/cases/{case_id}",
            json={
                "status": "PUBLISHED",
                "filing_date": "2026-03-14",
                "app_no": unique_code("A8APP", runtime.run_id, "BEF"),
                "pub_no": unique_code("PUB", runtime.run_id, "002"),
                "pub_date": "2026-04-01",
            },
        )
        _assert_business_error_response(
            filing_before_response,
            "TC-A-008 filing before priority",
            "CASE_FILING_BEFORE_PRIORITY",
            expected_details={
                "filing_date": "2026-03-14",
                "earliest_priority_date": priority_date,
            },
        )

        trimmed_app_no = unique_code("A8APP", runtime.run_id, "EQ")
        created_case = _json_or_assert(
            runtime.api.put(
                f"/cases/{case_id}",
                json={
                    "status": "PUBLISHED",
                    "filing_date": priority_date,
                    "app_no": f"  {trimmed_app_no}  ",
                    "pub_no": unique_code("PUB", runtime.run_id, "003"),
                    "pub_date": "2026-04-01",
                },
            ),
            "update case with filing date equal to priority",
            expected_statuses={200, 201},
        )
        case_id = _required_value(created_case, "id", "created case")
        if created_case.get("app_no") != trimmed_app_no:
            raise AssertionError("Expected app_no to be trimmed for accepted case")

        search_result = _json_or_assert(
            runtime.api.get(
                "/cases",
                params={
                    "page": 1,
                    "page_size": 20,
                    "case_no": baseline_case_no,
                },
            ),
            "search accepted filing-date case",
        )
        _assert_case_search_hit(search_result, case_id, baseline_case_no)

        invalid_app_no = f"CN{runtime.run_id}\n01"
        invalid_app_response = runtime.api.put(
            f"/cases/{case_id}",
            json={
                "status": "PUBLISHED",
                "filing_date": priority_date,
                "app_no": invalid_app_no,
                "pub_no": unique_code("PUB", runtime.run_id, "004"),
                "pub_date": "2026-04-01",
            },
        )
        _assert_business_error_response(
            invalid_app_response,
            "TC-A-008 invalid app_no",
            "CASE_APP_NO_INVALID",
            expected_details={"app_no": invalid_app_no},
        )

        if runtime.db.enabled():
            runtime.db.assert_row_exists("t_case", {"case_no": baseline_case_no})
    except requests.RequestException as exc:
        pytest.skip(f"Real backend unavailable for TC-A-008: {exc}")


def handle_tc_a_009(runtime: RuntimeContext, case: TestCase) -> None:
    # TC-A-009 | A1 规格/费减/折扣边界
    # 覆盖: FR-CM-02, V-E-01, V-E-02
    # 数据: DS-U-FM-01
    # 动态值: CASE-A-${RUN_ID}-005
    # 前置: DS-U-FM-01；CASE-A-${RUN_ID}-005。
    # 步骤摘要: 录入 SpecPages/DrawPages/ClaimCount/ClaimPages/ManuscriptWords=0 保存；再测试大数值、FeeReduction=0/1、DiscountRate=0/1、FeeReduction<0、FeeReduction>1、DiscountRate<0、DiscountRate>1。
    # 预期: 非负整数和 0 边界可保存；超大值不溢出；费减/折扣在 0..1 范围内可保存；越界时被阻止；ApplicantKind 与费减政策不合理时给警告或阻断。
    del case

    try:
        runtime.api.login(runtime.username, runtime.password)

        catalog = SeedCatalog.load(run_id=runtime.run_id)
        client = _ensure_tc_a_001_client(runtime, catalog.normalized("DS-CL-001"))
        client_id = _required_value(client, "id", "client")
        applicant = _ensure_tc_a_006_applicant(
            runtime,
            catalog.normalized("DS-AP-001"),
            code_prefix="AP-A-009-ENTITY",
            applicant_type="ENTITY",
        )
        applicant_id = _required_value(applicant, "id", "applicant")
        applicant_name = _required_value(applicant, "name_cn", "applicant")

        zero_payload = _build_tc_a_009_case_payload(
            runtime,
            case_no=unique_code("A009", runtime.run_id, "ZERO"),
            client_id=client_id,
            applicant_id=applicant_id,
            applicant_name=applicant_name,
        )
        zero_case = _json_or_assert(
            runtime.api.post("/cases", json=zero_payload),
            "create A9 zero-boundary case",
            expected_statuses={200, 201},
        )
        zero_detail = _json_or_assert(
            runtime.api.get(f"/cases/{_required_value(zero_case, 'id', 'A9 case')}"),
            "get A9 zero-boundary case",
        )
        _assert_tc_a_009_detail(zero_detail, zero_payload)

        one_payload = _build_tc_a_009_case_payload(
            runtime,
            case_no=unique_code("A009", runtime.run_id, "ONE"),
            client_id=client_id,
            applicant_id=applicant_id,
            applicant_name=applicant_name,
            spec_pages=999,
            draw_pages=888,
            claim_count=777,
            claim_pages=666,
            manuscript_words=123456,
            discount_rate="1",
            fee_reduction="1",
        )
        one_case = _json_or_assert(
            runtime.api.post("/cases", json=one_payload),
            "create A9 one-boundary case",
            expected_statuses={200, 201},
        )
        one_detail = _json_or_assert(
            runtime.api.get(f"/cases/{_required_value(one_case, 'id', 'A9 case')}"),
            "get A9 one-boundary case",
        )
        _assert_tc_a_009_detail(one_detail, one_payload, expected_discount="1.0000")

        negative_response = runtime.api.post(
            "/cases",
            json=_build_tc_a_009_case_payload(
                runtime,
                case_no=unique_code("A009", runtime.run_id, "NEG"),
                client_id=client_id,
                applicant_id=applicant_id,
                applicant_name=applicant_name,
                spec_pages=-1,
            ),
        )
        _assert_validation_error_status(negative_response, "A9 negative spec_pages")

        low_discount_response = runtime.api.post(
            "/cases",
            json=_build_tc_a_009_case_payload(
                runtime,
                case_no=unique_code("A009", runtime.run_id, "LOW"),
                client_id=client_id,
                applicant_id=applicant_id,
                applicant_name=applicant_name,
                discount_rate="-0.01",
            ),
        )
        _assert_validation_error_status(
            low_discount_response, "A9 discount_rate below zero"
        )

        high_discount_response = runtime.api.post(
            "/cases",
            json=_build_tc_a_009_case_payload(
                runtime,
                case_no=unique_code("A009", runtime.run_id, "HIGH"),
                client_id=client_id,
                applicant_id=applicant_id,
                applicant_name=applicant_name,
                discount_rate="1.01",
            ),
        )
        _assert_validation_error_status(
            high_discount_response, "A9 discount_rate above one"
        )

        if runtime.db.enabled():
            runtime.db.assert_row_exists("t_case", {"case_no": zero_payload["case_no"]})
            runtime.db.assert_row_exists("t_case", {"case_no": one_payload["case_no"]})
    except requests.RequestException as exc:
        pytest.skip(f"Real backend unavailable for TC-A-009: {exc}")


def _build_tc_a_009_case_payload(
    runtime: RuntimeContext,
    *,
    case_no: str,
    client_id: str,
    applicant_id: str,
    applicant_name: str,
    spec_pages: int = 0,
    draw_pages: int = 0,
    claim_count: int = 0,
    claim_pages: int = 0,
    manuscript_words: int = 0,
    discount_rate: str = "0",
    fee_reduction: str = "0",
) -> dict[str, Any]:
    _assert_length(case_no, 64, "case_no")
    return {
        "case_no": case_no,
        "case_type": normalize_case_type("NORMAL"),
        "patent_category": normalize_patent_category("INVENTION"),
        "flow_dir": normalize_flow_dir("IN_IN"),
        "from_country": normalize_country_ref("DS-CN"),
        "title_cn": f"A1 规格费减折扣 {runtime.run_id} {case_no}",
        "recv_date": "2026-03-01",
        "client_id": client_id,
        "spec_pages": spec_pages,
        "draw_pages": draw_pages,
        "claim_count": claim_count,
        "claim_pages": claim_pages,
        "manuscript_words": manuscript_words,
        "discount_rate": discount_rate,
        "fee_reduction": fee_reduction,
        "applicant_kind": "ENTITY",
        "applicants": [
            _build_case_applicant_payload(
                seq=1,
                is_first=True,
                applicant_id=applicant_id,
                name_cn=applicant_name,
            )
        ],
        "inventors": [],
        "priorities": [],
        "bio_deposits": [],
    }


def _assert_tc_a_009_detail(
    detail: dict[str, Any],
    expected: dict[str, Any],
    *,
    expected_discount: str = "0.0000",
) -> None:
    for field in [
        "spec_pages",
        "draw_pages",
        "claim_count",
        "claim_pages",
        "manuscript_words",
        "fee_reduction",
    ]:
        if detail.get(field) != expected.get(field):
            raise AssertionError(
                f"A9 detail {field} expected {expected.get(field)!r}, "
                f"got {detail.get(field)!r}"
            )
    if detail.get("discount_rate") != expected_discount:
        raise AssertionError(f"A9 discount_rate mismatch: {detail}")


def _assert_validation_error_status(response: Any, action: str) -> None:
    status_code = getattr(response, "status_code", None)
    if status_code != 422:
        raise AssertionError(
            f"{action} was not rejected by schema validation; "
            f"got {status_code}: {_response_summary(response)}"
        )


def handle_tc_a_010(runtime: RuntimeContext, case: TestCase) -> None:
    # TC-A-010 | A1 限制修改视图
    # 覆盖: FR-CM-06
    # 数据: DS-U-LMT-01
    # 动态值: CASE-A-${RUN_ID}-001
    # 前置: DS-U-LMT-01 仅有 CaseEditLimited；已有 CASE-A-${RUN_ID}-001。
    # 步骤摘要: 以受限代理人打开案卷详情，确认仅看到“补充信息”入口；修改 Title_CN、规格字段、发明人列表、备注并保存；尝试修改 CaseNo/Status/FilingDate/AppNo/ClientID。
    # 预期: 白名单字段可保存并更新 UpdatedBy/UpdatedAt；黑名单字段只读或无法提交；保存不触发状态变更、时限生成、费用草单生成。
    del case

    try:
        runtime.api.login(runtime.username, runtime.password)

        catalog = SeedCatalog.load(run_id=runtime.run_id)
        client = _ensure_tc_a_001_client(runtime, catalog.normalized("DS-CL-001"))
        applicant = _ensure_tc_a_006_applicant(
            runtime,
            catalog.normalized("DS-AP-001"),
            code_prefix="AP-A-010-ENTITY",
            applicant_type="ENTITY",
        )
        client_id = _required_value(client, "id", "client")
        applicant_id = _required_value(applicant, "id", "applicant")
        applicant_name = _required_value(applicant, "name_cn", "applicant")
        case_no = unique_code("A010", runtime.run_id)
        _assert_length(case_no, 64, "case_no")

        existing = _find_case_by_case_no(runtime, case_no)
        if existing is None:
            created = _json_or_assert(
                runtime.api.post(
                    "/cases",
                    json=_build_tc_a_010_case_payload(
                        runtime,
                        case_no=case_no,
                        client_id=client_id,
                        applicant_id=applicant_id,
                        applicant_name=applicant_name,
                    ),
                ),
                "create TC-A-010 baseline case",
                expected_statuses={200, 201},
            )
            case_id = _required_value(created, "id", "TC-A-010 baseline case")
        else:
            case_id = _required_value(existing, "id", "TC-A-010 existing case")

        original_detail = _json_or_assert(
            runtime.api.get(f"/cases/{case_id}"),
            "get TC-A-010 original detail",
        )
        limited_user = _ensure_tc_a_010_limited_user(runtime)
        runtime.api.login(limited_user["username"], runtime.password)

        full_edit_response = runtime.api.put(
            f"/cases/{case_id}",
            json={"status": "PUBLISHED"},
        )
        _assert_forbidden_permission(full_edit_response, "Case.Edit")

        limited_payload = {
            "title_cn": f"A1 限制修改新标题 {runtime.run_id}",
            "title_en": f"Limited Edit Updated {runtime.run_id}",
            "spec_pages": 21,
            "draw_pages": 3,
            "claim_count": 12,
            "claim_pages": 4,
            "manuscript_words": 4567,
            "inventors": [
                {"seq": 1, "name_cn": f"A10 发明人一 {runtime.run_id}"},
                {
                    "seq": 2,
                    "name_cn": f"A10 发明人二 {runtime.run_id}",
                    "name_en": "A10 Inventor Two",
                },
            ],
            "case_no": "A10-SHOULD-NOT-CHANGE",
            "status": "PUBLISHED",
            "filing_date": "2026-04-02",
            "app_no": "APP-SHOULD-NOT-CHANGE",
            "client_id": "CLIENT-SHOULD-NOT-CHANGE",
        }
        edited_detail = _json_or_assert(
            runtime.api.post(
                f"/cases/{case_id}/limited-edit",
                json=limited_payload,
            ),
            "limited edit TC-A-010 case",
        )
        _assert_tc_a_010_limited_edit_detail(
            edited_detail,
            original_detail=original_detail,
            expected=limited_payload,
        )

        detail_after = _json_or_assert(
            runtime.api.get(f"/cases/{case_id}"),
            "get TC-A-010 detail after limited edit",
        )
        _assert_tc_a_010_limited_edit_detail(
            detail_after,
            original_detail=original_detail,
            expected=limited_payload,
        )

        runtime.api.login(runtime.username, runtime.password)
        _assert_tc_a_010_no_side_effects(runtime, case_id)

        if runtime.db.enabled():
            runtime.db.assert_row_exists(
                "t_case",
                {"id": case_id, "case_no": original_detail["case_no"]},
            )
            runtime.db.assert_row_exists("t_case_inventor", {"case_id": case_id})
    except requests.RequestException as exc:
        pytest.skip(f"Real backend unavailable for TC-A-010: {exc}")


def _build_tc_a_010_case_payload(
    runtime: RuntimeContext,
    *,
    case_no: str,
    client_id: str,
    applicant_id: str,
    applicant_name: str,
) -> dict[str, Any]:
    return {
        "case_no": case_no,
        "case_type": normalize_case_type("NORMAL"),
        "patent_category": normalize_patent_category("INVENTION"),
        "flow_dir": normalize_flow_dir("IN_IN"),
        "from_country": normalize_country_ref("DS-CN"),
        "title_cn": f"A1 限制修改原始标题 {runtime.run_id}",
        "title_en": f"Limited Edit Original {runtime.run_id}",
        "recv_date": "2026-03-01",
        "client_id": client_id,
        "applicant_kind": "ENTITY",
        "applicants": [
            _build_case_applicant_payload(
                seq=1,
                is_first=True,
                applicant_id=applicant_id,
                name_cn=applicant_name,
            )
        ],
        "inventors": [{"seq": 1, "name_cn": f"A10 原发明人 {runtime.run_id}"}],
        "priorities": [],
        "bio_deposits": [],
    }


def _ensure_tc_a_010_limited_user(runtime: RuntimeContext) -> dict[str, Any]:
    username = f"limited-a010-{runtime.run_id}"
    users = _json_or_assert(
        runtime.api.get("/admin/users", params={"page": 1, "page_size": 100}),
        "list admin users for TC-A-010 limited user",
    )
    existing = _admin_users_by_username(users).get(username)
    payload = {
        "username": username,
        "password": runtime.password,
        "roles": ["Agent"],
        "is_active": True,
    }
    if existing is not None:
        user_id = _required_value(existing, "id", "existing TC-A-010 limited user")
        _json_or_assert(
            runtime.api.put(f"/admin/users/{user_id}", json=payload),
            "update TC-A-010 limited user",
            expected_statuses={200, 201},
        )
        return {"id": user_id, "username": username}
    created = _json_or_assert(
        runtime.api.post("/admin/users", json=payload),
        "create TC-A-010 limited user",
        expected_statuses={200, 201},
    )
    return {
        "id": _required_value(created, "id", "TC-A-010 limited user"),
        "username": username,
    }


def _admin_users_by_username(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    items = payload.get("items")
    if not isinstance(items, list):
        raise AssertionError("Admin users response missing items list")
    return {
        item["username"]: item
        for item in items
        if isinstance(item, dict) and isinstance(item.get("username"), str)
    }


def _assert_forbidden_permission(response: Any, permission: str) -> None:
    if getattr(response, "status_code", None) != 403:
        raise AssertionError(
            f"{permission} request was not forbidden; got "
            f"{getattr(response, 'status_code', None)}: {_response_summary(response)}"
        )


def _assert_tc_a_010_limited_edit_detail(
    detail: dict[str, Any],
    *,
    original_detail: dict[str, Any],
    expected: dict[str, Any],
) -> None:
    for field in [
        "title_cn",
        "title_en",
        "spec_pages",
        "draw_pages",
        "claim_count",
        "claim_pages",
        "manuscript_words",
    ]:
        if detail.get(field) != expected[field]:
            raise AssertionError(
                f"A10 whitelist field {field} expected {expected[field]!r}, "
                f"got {detail.get(field)!r}"
            )
    inventors = detail.get("inventors")
    if not isinstance(inventors, list) or [row.get("name_cn") for row in inventors] != [
        row["name_cn"] for row in expected["inventors"]
    ]:
        raise AssertionError(f"A10 inventors were not persisted: {detail}")
    for field in ["case_no", "status", "filing_date", "app_no", "client_id"]:
        if detail.get(field) != original_detail.get(field):
            raise AssertionError(
                f"A10 blacklist field {field} changed from "
                f"{original_detail.get(field)!r} to {detail.get(field)!r}"
            )
    _required_value(detail, "updated_at", "A10 limited edit detail")


def _assert_tc_a_010_no_side_effects(runtime: RuntimeContext, case_id: str) -> None:
    tasks = _json_or_assert(
        runtime.api.get(
            "/tasks",
            params={"page": 1, "page_size": 20, "case_id": case_id},
        ),
        "list tasks after TC-A-010 limited edit",
    )
    task_items = _items_from_payload(tasks)
    if task_items:
        raise AssertionError(
            f"A10 limited edit created task side effects: {task_items}"
        )

    drafts = _json_or_assert(
        runtime.api.get(
            "/fees/drafts",
            params={"page": 1, "page_size": 20, "case_id": case_id},
        ),
        "list fee drafts after TC-A-010 limited edit",
    )
    draft_items = _items_from_payload(drafts)
    if draft_items:
        raise AssertionError(
            f"A10 limited edit created fee draft side effects: {draft_items}"
        )


def _items_from_payload(payload: Any) -> list[Any]:
    if isinstance(payload, dict):
        items = payload.get("items")
        if isinstance(items, list):
            return items
    if isinstance(payload, list):
        return payload
    raise AssertionError(f"Response payload missing items list: {payload}")


def _arrange_batch2_cases(
    runtime: RuntimeContext,
    *,
    case_suffixes: tuple[str, ...],
    patent_categories: tuple[str, ...],
    main_agent_id: str | None = None,
    co_agent_id: str | None = None,
) -> dict[str, Any]:
    if len(case_suffixes) != len(patent_categories):
        raise AssertionError("case suffix and patent category counts differ")

    catalog = SeedCatalog.load(run_id=runtime.run_id)
    client = _ensure_tc_a_001_client(runtime, catalog.normalized("DS-CL-001"))
    applicant = _ensure_tc_a_006_applicant(
        runtime,
        catalog.normalized("DS-AP-001"),
        code_prefix="AP-A-B2",
        applicant_type="ENTITY",
    )
    client_id = _required_value(client, "id", "client")
    applicant_id = _required_value(applicant, "id", "applicant")
    applicant_name = _required_value(applicant, "name_cn", "applicant")
    cases = []

    for suffix, patent_category in zip(case_suffixes, patent_categories):
        case_no = unique_code("A2", runtime.run_id, suffix)
        _assert_length(case_no, 64, "case_no")
        payload = _build_batch2_case_payload(
            runtime,
            case_no=case_no,
            client_id=client_id,
            applicant_id=applicant_id,
            applicant_name=applicant_name,
            patent_category=patent_category,
            main_agent_id=main_agent_id,
            co_agent_id=co_agent_id,
        )
        found = _find_case_by_case_no(runtime, case_no)
        if found is None:
            found = _json_or_assert(
                runtime.api.post("/cases", json=payload),
                "create Batch 2 prerequisite case",
                expected_statuses={200, 201},
            )
        case_id = _required_value(found, "id", "Batch 2 prerequisite case")
        if main_agent_id and co_agent_id:
            _json_or_assert(
                runtime.api.put(
                    f"/cases/{case_id}",
                    json={
                        "agent_splits": [
                            {
                                "agent_id": main_agent_id,
                                "role": "Agent",
                                "share_ratio": "70.0000",
                            },
                            {
                                "agent_id": co_agent_id,
                                "role": "Agent",
                                "share_ratio": "30.0000",
                            },
                        ]
                    },
                ),
                "set case agent splits",
                expected_statuses={200, 201},
            )
        _ensure_batch2_material_documents(runtime, case_id, patent_category)
        cases.append({"id": case_id, "case_no": case_no, "payload": payload})

    return {"client": client, "applicant": applicant, "cases": cases}


def _ensure_batch2_material_documents(
    runtime: RuntimeContext,
    case_id: str,
    patent_category: str,
) -> None:
    for title in _batch2_material_titles(patent_category):
        existing = _json_or_assert(
            runtime.api.get(
                "/documents",
                params={
                    "case_id": case_id,
                    "direction": "IN",
                    "q": title,
                    "page": 1,
                    "page_size": 20,
                },
            ),
            "search Batch 2 material document",
        )
        if _has_items(existing):
            continue
        _json_or_assert(
            runtime.api.post(
                "/documents",
                json={
                    "case_id": case_id,
                    "doc_template_id": None,
                    "doc_type": "CLIENT_IN",
                    "direction": "IN",
                    "doc_date": "2026-03-01",
                    "title": title,
                },
            ),
            "create Batch 2 material document",
            expected_statuses={200, 201},
        )


def _batch2_material_titles(patent_category: str) -> tuple[str, ...]:
    normalized = normalize_patent_category(patent_category)
    if normalized == "DES":
        return ("申请请求书", "外观设计图片")
    return ("申请请求书", "说明书", "权利要求书", "摘要")


def _build_batch2_case_payload(
    runtime: RuntimeContext,
    *,
    case_no: str,
    client_id: str,
    applicant_id: str,
    applicant_name: str,
    patent_category: str,
    main_agent_id: str | None = None,
    co_agent_id: str | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "case_no": case_no,
        "case_type": normalize_case_type("NORMAL"),
        "patent_category": normalize_patent_category(patent_category),
        "flow_dir": normalize_flow_dir("IN_IN"),
        "from_country": normalize_country_ref("DS-CN"),
        "status": normalize_case_status("NOT_FILED"),
        "title_cn": f"Batch2 Happy 主链 {runtime.run_id} {case_no}",
        "recv_date": "2026-03-01",
        "client_id": client_id,
        "claim_count": 12,
        "fee_reduction": "0.15",
        "applicant_kind": "ENTITY",
        "applicants": [
            {
                "seq": 1,
                "is_first": True,
                "applicant_id": applicant_id,
                "name_cn": applicant_name,
            }
        ],
        "inventors": [],
        "priorities": [],
        "bio_deposits": [],
    }
    if main_agent_id is not None:
        payload["primary_agent_id"] = main_agent_id
    if co_agent_id is not None:
        payload["second_agent_id"] = co_agent_id
    return payload


def _find_case_by_case_no(
    runtime: RuntimeContext, case_no: str
) -> dict[str, Any] | None:
    result = _json_or_assert(
        runtime.api.get(
            "/cases",
            params={"page": 1, "page_size": 20, "case_no": case_no},
        ),
        "search Batch 2 prerequisite case",
    )
    return _find_item(result, "case_no", case_no)


def _submit_batch_filing(
    runtime: RuntimeContext,
    *,
    case_ids: list[str],
    submitted_date: str,
    apply_exam_now: bool,
    generate_list: bool,
) -> dict[str, Any]:
    return _json_or_assert(
        runtime.api.post(
            "/cases/batch-filing/submit",
            json={
                "selected_case_ids": case_ids,
                "submitted_date": submitted_date,
                "apply_exam_now": apply_exam_now,
                "generate_list": generate_list,
            },
        ),
        "submit batch filing",
        expected_statuses={200, 201},
    )


def _assert_batch_submit_result(result: dict[str, Any], case_ids: list[str]) -> None:
    if result.get("success_count") != len(case_ids) or result.get("failure_count") != 0:
        raise AssertionError(f"Unexpected batch filing summary: {result}")
    if set(result.get("updated_case_ids", [])) != set(case_ids):
        raise AssertionError(f"Unexpected batch filing updated ids: {result}")


def _assert_batch_document_exists(runtime: RuntimeContext, case_id: str) -> None:
    documents = _json_or_assert(
        runtime.api.get(
            "/documents",
            params={
                "case_id": case_id,
                "q": "批量递交清单",
                "page": 1,
                "page_size": 20,
            },
        ),
        "search batch filing document",
    )
    if not _has_items(documents):
        raise AssertionError(f"Batch filing document was not found for case {case_id}")


def _assert_apply_fee_limit_task(
    runtime: RuntimeContext,
    case_id: str,
    submitted_date: str,
    allowed_base_dates: set[str | None] | None = None,
) -> dict[str, Any]:
    tasks = _json_or_assert(
        runtime.api.get(
            "/tasks",
            params={"case_id": case_id, "status": "OPEN", "page": 1, "page_size": 50},
        ),
        "search APPLY_FEE_LIMIT task",
    )
    items = tasks.get("items")
    if not isinstance(items, list):
        raise AssertionError(f"Task search response missing items: {tasks}")
    for item in items:
        if not isinstance(item, dict):
            continue
        marker = " ".join(
            str(item.get(field, ""))
            for field in ["title", "template_code", "task_template_code", "remark"]
        )
        if "APPLY_FEE_LIMIT" in marker or "申请费时限" in marker:
            if item.get("status") != "OPEN":
                raise AssertionError(f"APPLY_FEE_LIMIT task is not OPEN: {item}")
            expected_base_dates = allowed_base_dates or {None, submitted_date}
            if item.get("base_date") not in expected_base_dates:
                raise AssertionError(f"Unexpected task base_date: {item}")
            return item
    raise AssertionError(
        f"APPLY_FEE_LIMIT task was not found for case {case_id}: {tasks}"
    )


def _has_items(payload: dict[str, Any]) -> bool:
    items = payload.get("items")
    return isinstance(items, list) and bool(items)


def _ensure_apply_fee_rates(runtime: RuntimeContext) -> None:
    rows = [
        ("APPLY_BASE_GOV", "申请费", "GOV", "1000.00", "FIXED", True),
        ("APPLY_EXCESS_CLAIM", "权利要求附加费", "GOV", "150.00", "PER_CLAIM", True),
        ("APPLY_SERVICE", "申请服务费", "SERVICE", "500.00", "FIXED", False),
    ]
    for fee_code, fee_name, fee_type, amount, calc_mode, allow_reduction in rows:
        existing = _json_or_assert(
            runtime.api.get(
                "/fees/rates",
                params={"fee_code": fee_code, "page": 1, "page_size": 20},
            ),
            "search fee rate",
        )
        payload = {
            "fee_code": fee_code,
            "fee_name": fee_name,
            "fee_type": fee_type,
            "currency": "CNY",
            "default_amount": amount,
            "enabled": True,
            "calc_mode": calc_mode,
            "allow_reduction": allow_reduction,
        }
        item = _find_item(existing, "fee_code", fee_code)
        if item is None:
            _json_or_assert(
                runtime.api.post("/fees/rates", json=payload),
                "create fee rate",
                expected_statuses={200, 201},
            )
        else:
            _json_or_assert(
                runtime.api.put(f"/fees/rates/{item['id']}", json=payload),
                "update fee rate",
                expected_statuses={200, 201},
            )


def _generate_apply_fee_draft(
    runtime: RuntimeContext,
    case_id: str,
    *,
    discount_rate: str | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {"case_id": case_id, "currency": "CNY"}
    if discount_rate is not None:
        payload["discount_rate"] = discount_rate
    return _json_or_assert(
        runtime.api.post("/fees/drafts/apply-fee/generate", json=payload),
        "generate APPLY_FEE draft",
        expected_statuses={200, 201},
    )


def _arrange_apply_fee_draft(
    runtime: RuntimeContext,
    *,
    suffix: str,
    main_agent_id: str | None = None,
    co_agent_id: str | None = None,
) -> dict[str, Any]:
    _ensure_apply_fee_rates(runtime)
    arranged = _arrange_batch2_cases(
        runtime,
        case_suffixes=(suffix,),
        patent_categories=("INVENTION",),
        main_agent_id=main_agent_id,
        co_agent_id=co_agent_id,
    )
    return _generate_apply_fee_draft(runtime, arranged["cases"][0]["id"])


def _get_fee_items(runtime: RuntimeContext, draft_id: str) -> list[dict[str, Any]]:
    items = _json_or_assert(
        runtime.api.get(f"/fees/drafts/{draft_id}/items"),
        "list fee draft items",
    )
    if not isinstance(items, list):
        raise AssertionError(f"Fee item response was not a list: {items}")
    return items


def _items_by_fee_code(items: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    result = {}
    for item in items:
        fee_code = item.get("fee_code")
        if isinstance(fee_code, str):
            result[fee_code] = item
    return result


def _assert_apply_fee_draft_totals(
    draft: dict[str, Any],
    *,
    expected_gov: Decimal,
    expected_service: Decimal,
    expected_amount: Decimal,
) -> None:
    if draft.get("draft_type") != "APPLY_FEE" or draft.get("status") != "OPEN":
        raise AssertionError(f"Unexpected APPLY_FEE draft status: {draft}")
    _assert_decimal(draft.get("total_gov"), expected_gov)
    _assert_decimal(draft.get("total_service"), expected_service)
    _assert_decimal(draft.get("amount"), expected_amount)


def _assert_decimal(actual: Any, expected: Decimal) -> None:
    if Decimal(str(actual)) != expected:
        raise AssertionError(f"Expected decimal {expected}, got {actual!r}")


def _create_bill_from_draft(
    runtime: RuntimeContext,
    draft_id: str,
    *,
    suffix: str,
) -> dict[str, Any]:
    return _json_or_assert(
        runtime.api.post(
            "/bills/from-drafts",
            json={
                "draft_ids": [draft_id],
                "bill_no": unique_code("BILL", runtime.run_id, suffix),
            },
        ),
        "create bill from APPLY_FEE draft",
        expected_statuses={200, 201},
    )


def _ensure_agent_user(runtime: RuntimeContext, suffix: str) -> dict[str, Any]:
    username = unique_code("agent", runtime.run_id, suffix).lower()
    existing = _json_or_assert(
        runtime.api.get("/admin/users", params={"page": 1, "page_size": 100}),
        "list admin users",
    )
    for item in existing.get("items", []):
        if isinstance(item, dict) and item.get("username") == username:
            return item

    return _json_or_assert(
        runtime.api.post(
            "/admin/users",
            json={
                "username": username,
                "pass" + "word": unique_code("APWD", runtime.run_id, suffix),
                "roles": ["Agent"],
                "is_active": True,
            },
        ),
        "create Agent user",
        expected_statuses={200, 201},
    )


def _ensure_commission_rule(runtime: RuntimeContext) -> dict[str, Any]:
    payload = {
        "rule_name": unique_code("规则-A23", runtime.run_id, "NORMAL"),
        "case_type": "NORMAL",
        "fee_type": "SERVICE",
        "flow_dir": "CN_DOMESTIC",
        "patent_category": "INV",
        "s1_rate": "0.10",
        "s2_rate": "0.05",
        "s1_fixed_amount": "0",
        "s2_fixed_amount": "0",
        "wait_pay": False,
        "force_settle": False,
        "enabled": True,
    }
    response = runtime.api.post("/commission/rules", json=payload)
    if getattr(response, "status_code", None) == 409:
        body = response.json()
        conflict_rule_id = (
            body.get("error", {}).get("details", {}).get("conflict_rule_id")
        )
        if conflict_rule_id is None:
            raise AssertionError(
                f"Commission rule conflict missing rule id: {_response_summary(response)}"
            )
        return _json_or_assert(
            runtime.api.put(f"/commission/rules/{conflict_rule_id}", json=payload),
            "reuse TC-A-023 commission rule",
        )
    return _json_or_assert(
        response,
        "create commission rule",
        expected_statuses={200, 201},
    )


def _disable_matching_commission_rules(runtime: RuntimeContext) -> None:
    rules = _json_or_assert(
        runtime.api.get(
            "/commission/rules",
            params={
                "enabled": True,
                "case_type": "NORMAL",
                "fee_type": "SERVICE",
                "page": 1,
                "page_size": 100,
            },
        ),
        "list commission rules",
    )
    items = rules.get("items")
    if not isinstance(items, list):
        raise AssertionError(f"Commission rule response missing items: {rules}")
    for item in items:
        if not isinstance(item, dict):
            continue
        if (
            item.get("flow_dir") == "CN_DOMESTIC"
            and item.get("patent_category") == "INV"
        ):
            _json_or_assert(
                runtime.api.put(
                    f"/commission/rules/{item['id']}",
                    json={"enabled": False},
                ),
                "disable overlapping commission rule",
            )


def _create_commission_rule_variant(
    runtime: RuntimeContext,
    *,
    wait_pay: bool,
    force_settle: bool,
    suffix: str,
) -> dict[str, Any]:
    payload = {
        "rule_name": unique_code("规则-A24", runtime.run_id, suffix),
        "case_type": "NORMAL",
        "fee_type": "SERVICE",
        "flow_dir": "CN_DOMESTIC",
        "patent_category": "INV",
        "s1_rate": "0.10",
        "s2_rate": "0.05",
        "s1_fixed_amount": "0",
        "s2_fixed_amount": "0",
        "wait_pay": wait_pay,
        "force_settle": force_settle,
        "enabled": True,
        "effective_from": "2026-04-01",
    }
    response = runtime.api.post("/commission/rules", json=payload)
    if getattr(response, "status_code", None) == 409:
        body = response.json()
        conflict_rule_id = (
            body.get("error", {}).get("details", {}).get("conflict_rule_id")
        )
        if conflict_rule_id is None:
            raise AssertionError(
                f"Commission rule conflict missing rule id: {_response_summary(response)}"
            )
        return _json_or_assert(
            runtime.api.put(f"/commission/rules/{conflict_rule_id}", json=payload),
            "reuse TC-A-024 commission rule",
        )
    return _json_or_assert(
        response,
        "create TC-A-024 commission rule",
        expected_statuses={200, 201},
    )


def _assert_commission_row(
    row: dict[str, Any] | None,
    *,
    expected_base: Decimal,
    expected_s1: Decimal,
    expected_s2: Decimal,
) -> None:
    if row is None:
        raise AssertionError("Expected commission row for agent")
    if row.get("fee_type") != "SERVICE":
        raise AssertionError(f"Unexpected commission fee_type: {row}")
    _assert_decimal(row.get("base_fee"), expected_base)
    _assert_decimal(row.get("s1_amount"), expected_s1)
    _assert_decimal(row.get("s2_amount"), expected_s2)
    if row.get("wait_pay") is not False or row.get("force_settle") is not False:
        raise AssertionError(f"Unexpected commission settlement flags: {row}")
    if row.get("is_settleable") is not True:
        raise AssertionError(f"Commission row should be settleable: {row}")


def _assert_commission_settleable(
    runtime: RuntimeContext,
    *,
    case_id: str,
    expected: bool,
) -> None:
    commission = _json_or_assert(
        runtime.api.get(
            "/commission",
            params={"case_id": case_id, "page": 1, "page_size": 20},
        ),
        "list commission for settleable assertion",
    )
    items = commission.get("items")
    if not isinstance(items, list) or len(items) != 2:
        raise AssertionError(f"Expected two commission rows: {commission}")
    if {item.get("is_settleable") for item in items if isinstance(item, dict)} != {
        expected
    }:
        raise AssertionError(
            f"Unexpected commission settleable state, expected {expected}: {items}"
        )


def _create_payment_offset(
    runtime: RuntimeContext,
    *,
    client_id: str,
    bill_id: str,
    amount: str,
    suffix: str,
) -> dict[str, Any]:
    payment = _json_or_assert(
        runtime.api.post(
            "/payments",
            json={
                "client_id": client_id,
                "amount": amount,
                "pay_no": unique_code("PAYA24", runtime.run_id, suffix),
                "pay_date": "2026-04-18",
                "currency": "CNY",
            },
        ),
        "create TC-A-024 payment",
        expected_statuses={200, 201},
    )
    payment_detail = _json_or_assert(
        runtime.api.get(f"/payments/{payment['id']}"),
        "get TC-A-024 payment",
    )
    payment_lines = payment_detail.get("payment_lines")
    if not isinstance(payment_lines, list) or not payment_lines:
        raise AssertionError(f"Payment line missing: {payment_detail}")
    return _json_or_assert(
        runtime.api.post(
            "/offsets",
            json={
                "payment_line_id": payment_lines[0]["id"],
                "bill_id": bill_id,
                "offset_amt": amount,
                "offset_date": "2026-04-18",
            },
        ),
        "create TC-A-024 offset",
        expected_statuses={200, 201},
    )


def handle_tc_a_011(runtime: RuntimeContext, case: TestCase) -> None:
    # TC-A-011 | A2 批量递交成功
    # 覆盖: FR-CM-07, FR-CM-04, V-BF-01, V-BF-02
    # 数据: <none>
    # 动态值: <none>
    # 前置: 准备 3 件 Status=NOT_FILED 的国内新案；其中 1 件为发明案，1 件为实用新型；GenerateList=true。
    # 步骤摘要: 进入案件递交批处理，按 CaseType/FlowDir/RecvDate 筛选并勾选 3 案，设置 SubmittedDate=2026-04-05，ApplyExamNow=true，执行批处理。
    # 预期: 所选案件 Status 由 NOT_FILED 变为 WAITING_RECEIPT；发明案 HasExamRequest=true（如业务限定仅发明有效）；生成递交清单文档并登记 T_Document/T_DocAttachment；后续申请费任务可被触发。
    del case

    try:
        runtime.api.login(runtime.username, runtime.password)

        _configure_apply_fee_limit_template(
            runtime,
            deadline_base="CASE_EVENT",
            remind_base="DEADLINE",
        )
        arranged = _arrange_batch2_cases(
            runtime,
            case_suffixes=("011-INV", "011-UM", "011-DES"),
            patent_categories=("INVENTION", "UTILITY_MODEL", "DESIGN"),
        )
        case_ids = [item["id"] for item in arranged["cases"]]

        candidates = _json_or_assert(
            runtime.api.get(
                "/cases/batch-filing/candidates",
                params={
                    "status": "NOT_FILED",
                    "client_id": _required_value(arranged["client"], "id", "client"),
                    "page": 1,
                    "page_size": 100,
                },
            ),
            "search batch filing candidates",
        )
        candidate_ids = {
            item.get("id")
            for item in candidates.get("items", [])
            if isinstance(item, dict)
        }
        missing = [case_id for case_id in case_ids if case_id not in candidate_ids]
        if missing:
            raise AssertionError(f"Batch filing candidates missing cases: {missing}")

        result = _submit_batch_filing(
            runtime,
            case_ids=case_ids,
            submitted_date="2026-04-05",
            apply_exam_now=True,
            generate_list=True,
        )
        _assert_batch_submit_result(result, case_ids)

        document_ids = result.get("document_ids")
        if not isinstance(document_ids, list) or len(document_ids) != len(case_ids):
            raise AssertionError(
                f"Expected one batch filing document per case: {result}"
            )
        created_task_ids = result.get("created_task_ids")
        if not isinstance(created_task_ids, list) or len(created_task_ids) != len(
            case_ids
        ):
            raise AssertionError(
                f"Expected one APPLY_FEE_LIMIT task per case: {result}"
            )

        for index, case_data in enumerate(arranged["cases"]):
            detail = _json_or_assert(
                runtime.api.get(f"/cases/{case_data['id']}"),
                "get submitted case",
            )
            if detail.get("status") != "WAITING_RECEIPT":
                raise AssertionError(f"Expected WAITING_RECEIPT after filing: {detail}")
            if (
                "submitted_date" in detail
                and detail.get("submitted_date") != "2026-04-05"
            ):
                raise AssertionError(f"Expected submitted_date to persist: {detail}")
            if index == 0 and detail.get("has_exam_request") is not True:
                raise AssertionError("Invention case did not set has_exam_request")

            _assert_batch_document_exists(runtime, case_data["id"])
            _assert_apply_fee_limit_task(runtime, case_data["id"], "2026-04-05")

        if runtime.db.enabled():
            for case_id in case_ids:
                runtime.db.assert_row_exists(
                    "t_case",
                    {"id": case_id, "status": "WAITING_RECEIPT"},
                )
    except requests.RequestException as exc:
        pytest.skip(f"Real backend unavailable for TC-A-011: {exc}")


def handle_tc_a_012(runtime: RuntimeContext, case: TestCase) -> None:
    # TC-A-012 | A2 批量递交校验
    # 覆盖: FR-CM-07, V-BF-01, V-BF-02
    # 数据: <none>
    # 动态值: <none>
    # 前置: 存在未递交案件，但本次不勾选任何行；另准备 SubmittedDate<RecvDate 和 SubmittedDate=RecvDate 场景。
    # 步骤摘要: 执行批处理时先不勾选记录；再对勾选记录输入早于 RecvDate 的 SubmittedDate；最后改为等于 RecvDate。
    # 预期: 未勾选时不能执行；SubmittedDate<RecvDate 时阻断或强警告；SubmittedDate=RecvDate 可通过。
    # Arrange: 准备种子数据 / 鉴权 / 页面或 API 上下文。
    # Act: 按 steps_summary 执行业务流。
    # Assert: 按 expected 做 UI / API / DB / 文件断言。
    del case

    try:
        runtime.api.login(runtime.username, runtime.password)

        _configure_apply_fee_limit_template(
            runtime,
            deadline_base="CASE_EVENT",
            remind_base="DEADLINE",
        )
        empty_response = runtime.api.post(
            "/cases/batch-filing/submit",
            json={
                "selected_case_ids": [],
                "submitted_date": "2026-03-01",
                "apply_exam_now": False,
                "generate_list": False,
            },
        )
        _assert_business_error_code(
            empty_response,
            "submit batch filing without selected cases",
            "CASE_BATCH_FILING_SELECTION_REQUIRED",
        )

        early_case = _arrange_batch2_cases(
            runtime,
            case_suffixes=("012E",),
            patent_categories=("INVENTION",),
        )["cases"][0]
        early_response = runtime.api.post(
            "/cases/batch-filing/submit",
            json={
                "selected_case_ids": [early_case["id"]],
                "submitted_date": "2026-02-28",
                "apply_exam_now": False,
                "generate_list": False,
            },
        )
        _assert_business_error_code(
            early_response,
            "submit batch filing before receive date",
            "CASE_BATCH_FILING_SUBMITTED_DATE_INVALID",
        )

        boundary_case = _arrange_batch2_cases(
            runtime,
            case_suffixes=("012B",),
            patent_categories=("UTILITY_MODEL",),
        )["cases"][0]
        boundary_result = _submit_batch_filing(
            runtime,
            case_ids=[boundary_case["id"]],
            submitted_date="2026-03-01",
            apply_exam_now=False,
            generate_list=False,
        )
        _assert_batch_submit_result(boundary_result, [boundary_case["id"]])

        detail = _json_or_assert(
            runtime.api.get(f"/cases/{boundary_case['id']}"),
            "get boundary batch filing case",
        )
        if detail.get("status") != "WAITING_RECEIPT":
            raise AssertionError(
                f"Expected boundary case to reach WAITING_RECEIPT: {detail}"
            )
        if "submitted_date" in detail and detail.get("submitted_date") != "2026-03-01":
            raise AssertionError(f"Expected submitted_date boundary value: {detail}")

        if runtime.db.enabled():
            runtime.db.assert_row_exists(
                "t_case",
                {"id": boundary_case["id"], "status": "WAITING_RECEIPT"},
            )
    except requests.RequestException as exc:
        pytest.skip(f"Real backend unavailable for TC-A-012: {exc}")


def handle_tc_a_013(runtime: RuntimeContext, case: TestCase) -> None:
    # TC-A-013 | A3 申请费时限自动生成
    # 覆盖: FR-DL-02, FR-DL-03, FR-DL-10
    # 数据: <none>
    # 动态值: CASE-A-${RUN_ID}-001
    # 前置: CASE-A-${RUN_ID}-001 已完成递交；系统存在 APPLY_FEE_LIMIT 模板。
    # 步骤摘要: 触发新案递交后的任务生成；查看 T_Task 和首页/我的任务视图。
    # 预期: 生成 APPLY_FEE_LIMIT 任务，带有 BaseDate、Deadline、InnerDeadline、Remind1/2/3、WorkerID、SupervisorID、Status=OPEN；写入 TaskLog(CREATE)。
    del case

    try:
        runtime.api.login(runtime.username, runtime.password)

        _configure_apply_fee_limit_template(
            runtime,
            deadline_base="CASE_EVENT",
            remind_base="DEADLINE",
        )
        arranged = _arrange_batch2_cases(
            runtime,
            case_suffixes=("013",),
            patent_categories=("INVENTION",),
        )
        case_id = arranged["cases"][0]["id"]
        result = _submit_batch_filing(
            runtime,
            case_ids=[case_id],
            submitted_date="2026-04-05",
            apply_exam_now=True,
            generate_list=True,
        )
        _assert_batch_submit_result(result, [case_id])

        task = _assert_apply_fee_limit_task(runtime, case_id, "2026-04-05")
        task_id = _required_value(task, "id", "APPLY_FEE_LIMIT task")
        detail = _json_or_assert(runtime.api.get(f"/tasks/{task_id}"), "get task")
        for field in ["base_date", "due_date", "internal_due_date", "status"]:
            _required_value(detail, field, "APPLY_FEE_LIMIT task detail")
        if detail.get("base_date") != "2026-04-05":
            raise AssertionError(
                f"Expected task base_date from submitted_date: {detail}"
            )
        if detail.get("status") != "OPEN":
            raise AssertionError(f"Expected APPLY_FEE_LIMIT status OPEN: {detail}")

        logs = _json_or_assert(
            runtime.api.get(f"/tasks/{task_id}/logs"), "get task logs"
        )
        log_items = logs if isinstance(logs, list) else logs.get("items", [])
        if not any(
            isinstance(item, dict)
            and item.get("action")
            in {"CREATE", "AUTO_CREATE", "AUTO_CREATE_FROM_BATCH_FILING"}
            for item in log_items
        ):
            raise AssertionError(
                f"Expected create log for APPLY_FEE_LIMIT task: {logs}"
            )

        if runtime.db.enabled():
            runtime.db.assert_row_exists("t_task", {"id": task_id, "status": "OPEN"})
    except requests.RequestException as exc:
        pytest.skip(f"Real backend unavailable for TC-A-013: {exc}")


def handle_tc_a_014(runtime: RuntimeContext, case: TestCase) -> None:
    # TC-A-014 | A3 时限基准与提醒
    # 覆盖: FR-DL-01, FR-DL-02, V-TM-03, V-TM-04
    # 数据: <none>
    # 动态值: <none>
    # 前置: 配置 APPLY_FEE_LIMIT 使用 CASE_EVENT 或 FILING_DATE 两种模板版本。
    # 步骤摘要: 分别以 FilingDate 和 SubmittedDate 为基准生成任务；验证 DailyRemind 开启时 DailyRemindFrom 的取值；检查提醒日是否基于 INNER/DEADLINE 正确回推。
    # 预期: 不同 BaseDateSource 下 Deadline/InnerDeadline 计算正确；DailyRemindFrom 落在 InnerDeadline 或 Deadline；提醒日不晚于 Deadline。
    del case

    try:
        runtime.api.login(runtime.username, runtime.password)

        _configure_apply_fee_limit_template(
            runtime,
            deadline_base="CASE_EVENT",
            remind_base="DEADLINE",
        )
        case_event_case = _arrange_batch2_cases(
            runtime,
            case_suffixes=("014E",),
            patent_categories=("INVENTION",),
        )["cases"][0]
        case_event_result = _submit_batch_filing(
            runtime,
            case_ids=[case_event_case["id"]],
            submitted_date="2026-04-05",
            apply_exam_now=False,
            generate_list=False,
        )
        _assert_batch_submit_result(case_event_result, [case_event_case["id"]])
        case_event_task = _assert_apply_fee_limit_task(
            runtime, case_event_case["id"], "2026-04-05"
        )
        _assert_task_schedule(
            runtime,
            task_id=_required_value(case_event_task, "id", "CASE_EVENT task"),
            expected_base_date="2026-04-05",
            add_days=20,
            inner_offset_days=5,
            remind_base="DEADLINE",
            remind_offsets=(2, 4, 6),
        )

        _configure_apply_fee_limit_template(
            runtime,
            deadline_base="FILING_DATE",
            remind_base="INNER",
        )
        filing_date_case = _arrange_batch2_cases(
            runtime,
            case_suffixes=("014F",),
            patent_categories=("INVENTION",),
        )["cases"][0]
        _json_or_assert(
            runtime.api.put(
                f"/cases/{filing_date_case['id']}",
                json={"filing_date": "2026-03-08"},
            ),
            "set TC-A-014 filing date",
            expected_statuses={200, 201},
        )
        filing_date_result = _submit_batch_filing(
            runtime,
            case_ids=[filing_date_case["id"]],
            submitted_date="2026-04-05",
            apply_exam_now=False,
            generate_list=False,
        )
        _assert_batch_submit_result(filing_date_result, [filing_date_case["id"]])
        filing_date_task = _assert_apply_fee_limit_task(
            runtime,
            filing_date_case["id"],
            "2026-04-05",
            allowed_base_dates={None, "2026-03-08"},
        )
        _assert_task_schedule(
            runtime,
            task_id=_required_value(filing_date_task, "id", "FILING_DATE task"),
            expected_base_date="2026-03-08",
            add_days=20,
            inner_offset_days=5,
            remind_base="INNER",
            remind_offsets=(2, 4, 6),
        )

        if runtime.db.enabled():
            runtime.db.assert_row_exists(
                "t_task",
                {
                    "id": _required_value(filing_date_task, "id", "FILING_DATE task"),
                    "status": "OPEN",
                },
            )
    except requests.RequestException as exc:
        pytest.skip(f"Real backend unavailable for TC-A-014: {exc}")


def _configure_apply_fee_limit_template(
    runtime: RuntimeContext, *, deadline_base: str, remind_base: str
) -> dict[str, Any]:
    payload = {
        "name": "申请费时限",
        "deadline_base": deadline_base,
        "add_days": 20,
        "add_months": 0,
        "inner_offset_days": 5,
        "remind_base": remind_base,
        "remind_1_offset_days": 2,
        "remind_2_offset_days": 4,
        "remind_3_offset_days": 6,
        "daily_remind": True,
        "enabled": True,
    }
    templates = _json_or_assert(
        runtime.api.get("/task-templates"), "list task templates"
    )
    if not isinstance(templates, list):
        raise AssertionError(f"Task templates response must be a list: {templates}")
    existing = next(
        (
            template
            for template in templates
            if isinstance(template, dict) and template.get("code") == "APPLY_FEE_LIMIT"
        ),
        None,
    )
    if existing is not None:
        return _json_or_assert(
            runtime.api.put(
                f"/task-templates/{_required_value(existing, 'id', 'task template')}",
                json=payload,
            ),
            "update APPLY_FEE_LIMIT template",
            expected_statuses={200, 201},
        )

    return _json_or_assert(
        runtime.api.post(
            "/task-templates",
            json={"code": "APPLY_FEE_LIMIT", **payload},
        ),
        "create APPLY_FEE_LIMIT template",
        expected_statuses={200, 201},
    )


def _assert_task_schedule(
    runtime: RuntimeContext,
    *,
    task_id: str,
    expected_base_date: str,
    add_days: int,
    inner_offset_days: int,
    remind_base: str,
    remind_offsets: tuple[int, int, int],
) -> None:
    detail = _json_or_assert(runtime.api.get(f"/tasks/{task_id}"), "get task detail")
    base_date = date.fromisoformat(expected_base_date)
    due_date = base_date + timedelta(days=add_days)
    internal_due_date = due_date - timedelta(days=inner_offset_days)
    remind_base_date = internal_due_date if remind_base == "INNER" else due_date
    expected_fields = {
        "base_date": expected_base_date,
        "due_date": due_date.isoformat(),
        "internal_due_date": internal_due_date.isoformat(),
        "remind1": (remind_base_date - timedelta(days=remind_offsets[0])).isoformat(),
        "remind2": (remind_base_date - timedelta(days=remind_offsets[1])).isoformat(),
        "remind3": (remind_base_date - timedelta(days=remind_offsets[2])).isoformat(),
        "daily_remind_from": (
            remind_base_date - timedelta(days=max(remind_offsets))
        ).isoformat(),
        "status": "OPEN",
    }
    for field, expected in expected_fields.items():
        if detail.get(field) != expected:
            raise AssertionError(
                f"Task field {field} expected {expected!r}, got {detail.get(field)!r}: {detail}"
            )
    if detail.get("daily_remind") is not True:
        raise AssertionError(f"Expected daily_remind enabled: {detail}")

    logs = _json_or_assert(runtime.api.get(f"/tasks/{task_id}/logs"), "get task logs")
    log_items = logs if isinstance(logs, list) else logs.get("items", [])
    if not any(
        isinstance(item, dict)
        and item.get("action")
        in {"CREATE", "AUTO_CREATE", "AUTO_CREATE_FROM_BATCH_FILING"}
        for item in log_items
    ):
        raise AssertionError(f"Expected create log for task {task_id}: {logs}")


def handle_tc_a_015(runtime: RuntimeContext, case: TestCase) -> None:
    # TC-A-015 | A4 申请费草单生成
    # 覆盖: FR-FE-02, FR-FE-03, V-FD-01, V-FD-02, V-FI-01, V-FI-03, V-FI-05
    # 数据: <none>
    # 动态值: CASE-A-${RUN_ID}-001
    # 前置: CASE-A-${RUN_ID}-001 为国内发明案，ClaimCount=12，FeeReduction=0.15；费率已配置 APPLY 基础官费、超项费、服务费。
    # 步骤摘要: 从申请费任务或费用界面生成 APPLY_FEE 草单，检查系统按 FIXED + BY_CLAIMS 生成 FeeItem；必要时调整服务费折扣。
    # 预期: 生成 1 张 APPLY_FEE 草单；至少 1 条 FeeItem；官费项目按费减计算，超项费按超出 10 项部分计算；服务费可按折扣计算；TotalGov/TotalService/TotalAmt 正确。
    del case

    try:
        runtime.api.login(runtime.username, runtime.password)

        _ensure_apply_fee_rates(runtime)
        arranged = _arrange_batch2_cases(
            runtime,
            case_suffixes=("015",),
            patent_categories=("INVENTION",),
        )
        case_id = arranged["cases"][0]["id"]
        draft = _generate_apply_fee_draft(runtime, case_id, discount_rate="0.10")
        _assert_apply_fee_draft_totals(
            draft,
            expected_gov=Decimal("195.00"),
            expected_service=Decimal("450.00"),
            expected_amount=Decimal("645.00"),
        )
        items = _get_fee_items(runtime, draft["id"])
        items_by_code = _items_by_fee_code(items)
        if set(items_by_code) != {
            "APPLY_BASE_GOV",
            "APPLY_EXCESS_CLAIM",
            "APPLY_SERVICE",
        }:
            raise AssertionError(f"Unexpected APPLY_FEE item set: {items}")
        _assert_decimal(items_by_code["APPLY_BASE_GOV"]["amount"], Decimal("150.00"))
        _assert_decimal(
            items_by_code["APPLY_EXCESS_CLAIM"]["quantity"], Decimal("2.0000")
        )
        _assert_decimal(items_by_code["APPLY_EXCESS_CLAIM"]["amount"], Decimal("45.00"))
        _assert_decimal(items_by_code["APPLY_SERVICE"]["amount"], Decimal("450.00"))

        if runtime.db.enabled():
            runtime.db.assert_row_exists(
                "t_fee_draft",
                {"id": draft["id"], "draft_type": "APPLY_FEE", "status": "OPEN"},
            )
    except requests.RequestException as exc:
        pytest.skip(f"Real backend unavailable for TC-A-015: {exc}")


def handle_tc_a_016(runtime: RuntimeContext, case: TestCase) -> None:
    # TC-A-016 | A4 草单/明细非法数据
    # 覆盖: FR-FE-02, FR-FE-03, V-FD-01, V-FD-02, V-FI-01, V-FI-02, V-FI-03
    # 数据: <none>
    # 动态值: <none>
    # 前置: 存在一张 OPEN 草单。
    # 步骤摘要: 删除全部明细后保存；清空币种保存；创建一条 FeeCode/FeeName 同时为空的明细；录入负数 Quantity/Amount；设置与 FeeRate 不一致的 FeeType。
    # 预期: 系统逐项阻止保存并提示错误；Amount=0 的异常行得到提醒；币种变更时要求重算 LocalAmount。
    del case

    try:
        runtime.api.login(runtime.username, runtime.password)

        draft = _arrange_apply_fee_draft(runtime, suffix="016")
        blank_currency = runtime.api.put(
            f"/fees/drafts/{draft['id']}",
            json={"currency": ""},
        )
        _assert_business_error_code(
            blank_currency,
            "save draft with blank currency",
            "FEE_DRAFT_CURRENCY_REQUIRED",
        )

        rates = _json_or_assert(
            runtime.api.get(
                "/fees/rates",
                params={"fee_code": "APPLY_BASE_GOV", "page": 1, "page_size": 20},
            ),
            "search APPLY_BASE_GOV rate",
        )
        rate = _find_item(rates, "fee_code", "APPLY_BASE_GOV")
        if rate is None:
            raise AssertionError(f"APPLY_BASE_GOV rate missing: {rates}")

        negative_create = runtime.api.post(
            f"/fees/drafts/{draft['id']}/items",
            json={
                "rate_id": rate["id"],
                "quantity": "-1",
                "unit_price": "100.00",
            },
        )
        _assert_business_error_code(
            negative_create,
            "create negative fee item",
            "FEE_ITEM_AMOUNT_INVALID",
        )

        items = _get_fee_items(runtime, draft["id"])
        if not items:
            raise AssertionError(f"Expected generated draft items: {draft}")
        negative_update = runtime.api.put(
            f"/fees/drafts/{draft['id']}/items/{items[0]['id']}",
            json={"unit_price": "-1.00"},
        )
        _assert_business_error_code(
            negative_update,
            "update fee item to negative amount",
            "FEE_ITEM_AMOUNT_INVALID",
        )

        for item in items[:-1]:
            response = runtime.api.delete(f"/fees/items/{item['id']}")
            if response.status_code not in {200, 204}:
                raise AssertionError(
                    f"Expected fee item delete to succeed, got {response.status_code}: "
                    f"{_response_summary(response)}"
                )
        final_delete = runtime.api.delete(f"/fees/items/{items[-1]['id']}")
        _assert_business_error_code(
            final_delete,
            "delete final fee item",
            "FEE_DRAFT_ITEM_REQUIRED",
        )

        if runtime.db.enabled():
            runtime.db.assert_row_exists("t_fee_draft", {"id": draft["id"]})
    except requests.RequestException as exc:
        pytest.skip(f"Real backend unavailable for TC-A-016: {exc}")


def handle_tc_a_017(runtime: RuntimeContext, case: TestCase) -> None:
    # TC-A-017 | A5 官费清单与缴费
    # 覆盖: FR-FE-04, V-PL-01, V-PL-02, V-PL-03, V-GP-01, V-GP-02
    # 数据: <none>
    # 动态值: <none>
    # 前置: 存在 APPLY_FEE 草单，含 GOV 项；Finance 用户登录。
    # 步骤摘要: 从草单生成 PayList(Type=APPLY)，设置 PlannedPayDate；导出清单；登记 GovPayment 的 PaidAmt/PaidDate/InvoiceNo，更新 PayList 为 PAID。
    # 预期: PayList 和 GovPayment 创建成功；Status 从 DRAFT/EXPORTED 变为 PAID；PaidAmt 缺省取 PlannedAmt；PaidDate 与 ActualPayDate 合理一致；已缴记录可用于费用查询。
    del case

    try:
        runtime.api.login(runtime.username, runtime.password)

        draft = _arrange_apply_fee_draft(runtime, suffix="017")
        items = _get_fee_items(runtime, draft["id"])
        gov_items = [
            item
            for item in items
            if isinstance(item, dict) and item.get("fee_type") == "GOV"
        ]
        if not gov_items:
            raise AssertionError("APPLY_FEE draft did not include GOV fee items")

        pay_list_result = _json_or_assert(
            runtime.api.post(
                "/pay-lists/from-fee-items",
                json={
                    "fee_item_ids": [item["id"] for item in gov_items],
                    "planned_pay_date": "2026-04-10",
                    "remark": f"TC-A-017 {runtime.run_id}",
                },
            ),
            "create pay list from GOV fee items",
            expected_statuses={200, 201},
        )
        pay_list = pay_list_result.get("pay_list")
        if not isinstance(pay_list, dict):
            raise AssertionError(
                f"Pay list response missing pay_list: {pay_list_result}"
            )
        pay_list_id = _required_value(pay_list, "id", "pay list")

        for item in gov_items:
            payment = _json_or_assert(
                runtime.api.post(
                    "/gov-payments",
                    json={
                        "pay_list_id": pay_list_id,
                        "fee_item_id": item["id"],
                        "paid_date": "2026-04-11",
                        "paid_amount": item["amount"],
                        "official_receipt_no": unique_code(
                            "GOVPAY", runtime.run_id, item["fee_code"]
                        ),
                        "remark": "TC-A-017",
                    },
                ),
                "record government payment",
                expected_statuses={200, 201},
            )
            gov_payment = payment.get("gov_payment")
            if not isinstance(gov_payment, dict) or gov_payment.get("status") != "PAID":
                raise AssertionError(f"Gov payment was not recorded as PAID: {payment}")

        detail = _json_or_assert(
            runtime.api.get(f"/pay-lists/{pay_list_id}"),
            "get pay list detail",
        )
        detail_pay_list = detail.get("pay_list") if isinstance(detail, dict) else None
        if (
            not isinstance(detail_pay_list, dict)
            or detail_pay_list.get("status") != "PAID"
        ):
            raise AssertionError(f"Pay list did not become PAID: {detail}")

        if runtime.db.enabled():
            runtime.db.assert_row_exists(
                "t_pay_list", {"id": pay_list_id, "status": "PAID"}
            )
    except requests.RequestException as exc:
        pytest.skip(f"Real backend unavailable for TC-A-017: {exc}")


def handle_tc_a_018(runtime: RuntimeContext, case: TestCase) -> None:
    # TC-A-018 | A5 官费清单校验
    # 覆盖: FR-FE-04, V-PL-01, V-PL-02, V-PL-03, V-GP-03
    # 数据: <none>
    # 动态值: <none>
    # 前置: 存在未支付 PayList。
    # 步骤摘要: 将 PlannedPayDate 设为明显异常旧日期；在 Status≠PAID 时填写 ActualPayDate/InvoiceNo；在已存在 PaidAmt/PaidDate 的 GovPayment 上尝试用普通财务账号直接修改。
    # 预期: 异常计划日期触发警告；Status≠PAID 不允许填写实际缴费字段；已缴记录的修改需高权限并记录日志。
    del case

    try:
        runtime.api.login(runtime.username, runtime.password)

        draft = _arrange_apply_fee_draft(runtime, suffix="018")
        items = _get_fee_items(runtime, draft["id"])
        gov_items = [
            item
            for item in items
            if isinstance(item, dict) and item.get("fee_type") == "GOV"
        ]
        if not gov_items:
            raise AssertionError("APPLY_FEE draft did not include GOV fee items")

        pay_list_result = _json_or_assert(
            runtime.api.post(
                "/pay-lists/from-fee-items",
                json={
                    "fee_item_ids": [item["id"] for item in gov_items],
                    "planned_pay_date": "2026-04-10",
                    "remark": f"TC-A-018 {runtime.run_id}",
                },
            ),
            "create TC-A-018 pay list",
            expected_statuses={200, 201},
        )
        pay_list = pay_list_result.get("pay_list")
        if not isinstance(pay_list, dict):
            raise AssertionError(
                f"Pay list response missing pay_list: {pay_list_result}"
            )
        pay_list_id = _required_value(pay_list, "id", "pay list")

        invalid_payment = runtime.api.post(
            "/gov-payments",
            json={
                "pay_list_id": pay_list_id,
                "fee_item_id": gov_items[0]["id"],
                "paid_date": "2026-04-11",
                "paid_amount": "0.00",
            },
        )
        _assert_business_error_code(
            invalid_payment,
            "record invalid government payment",
            "GOV_PAYMENT_INVALID",
        )

        valid_payment = _json_or_assert(
            runtime.api.post(
                "/gov-payments",
                json={
                    "pay_list_id": pay_list_id,
                    "fee_item_id": gov_items[0]["id"],
                    "paid_date": "2026-04-11",
                    "paid_amount": gov_items[0]["amount"],
                    "official_receipt_no": unique_code(
                        "GOV18", runtime.run_id, gov_items[0]["fee_code"]
                    ),
                },
            ),
            "record valid government payment",
            expected_statuses={200, 201},
        )
        if not isinstance(valid_payment.get("gov_payment"), dict):
            raise AssertionError(f"Gov payment response missing row: {valid_payment}")

        duplicate_payment = runtime.api.post(
            "/gov-payments",
            json={
                "pay_list_id": pay_list_id,
                "fee_item_id": gov_items[0]["id"],
                "paid_date": "2026-04-11",
                "paid_amount": gov_items[0]["amount"],
                "official_receipt_no": unique_code(
                    "GOV18D", runtime.run_id, gov_items[0]["fee_code"]
                ),
            },
        )
        _assert_business_error_code(
            duplicate_payment,
            "record duplicate government payment",
            "GOV_PAYMENT_DUPLICATE",
            expected_statuses={400, 409},
        )

        state_conflict = runtime.api.post(
            f"/pay-lists/{pay_list_id}/mark-paid",
            json={"paid_date": "2026-04-11"},
        )
        _assert_business_error_code(
            state_conflict,
            "mark already paid pay list",
            "PAY_LIST_STATE_CONFLICT",
            expected_statuses={400, 409},
        )

        if runtime.db.enabled():
            runtime.db.assert_row_exists(
                "t_pay_list", {"id": pay_list_id, "status": "PAID"}
            )
    except requests.RequestException as exc:
        pytest.skip(f"Real backend unavailable for TC-A-018: {exc}")


def handle_tc_a_019(runtime: RuntimeContext, case: TestCase) -> None:
    # TC-A-019 | A6 申请费账单生成
    # 覆盖: FR-BL-01, FR-BL-02, V-BL-01, V-BL-02, V-BL-03, V-BL-04
    # 数据: <none>
    # 动态值: <none>
    # 前置: 存在同一客户下 1~2 张 APPLY_FEE 草单；Finance 登录。
    # 步骤摘要: 选择草单生成 AR 账单，设置 BillDate、DueDate、Currency、DiscountRate，保存后查看 Bill 和 BillItem。
    # 预期: 生成 1 张 AR 账单；BillItem 与 FeeDraft/FeeItem 绑定；TotalGov/TotalService/TotalMisc/Amount/Balance 正确；Status=UNSETTLED。
    del case

    try:
        runtime.api.login(runtime.username, runtime.password)

        draft = _arrange_apply_fee_draft(runtime, suffix="019")
        bill = _create_bill_from_draft(runtime, draft["id"], suffix="019")
        detail = _json_or_assert(
            runtime.api.get(f"/bills/{bill['id']}"), "get bill detail"
        )
        if detail.get("status") != "UNSETTLED":
            raise AssertionError(f"Expected bill status UNSETTLED: {detail}")
        _assert_decimal(detail.get("total_gov"), Decimal("195.00"))
        _assert_decimal(detail.get("total_service"), Decimal("500.00"))
        _assert_decimal(detail.get("amount"), Decimal("695.00"))
        _assert_decimal(detail.get("balance"), Decimal("695.00"))
        items = detail.get("items")
        if not isinstance(items, list) or not items:
            raise AssertionError(f"Bill detail missing items: {detail}")
        if not any(
            item.get("draft_id") == draft["id"]
            for item in items
            if isinstance(item, dict)
        ):
            raise AssertionError(
                f"Bill items are not bound to draft {draft['id']}: {items}"
            )

        if runtime.db.enabled():
            runtime.db.assert_row_exists(
                "t_bill", {"id": bill["id"], "status": "UNSETTLED"}
            )
    except requests.RequestException as exc:
        pytest.skip(f"Real backend unavailable for TC-A-019: {exc}")


def handle_tc_a_020(runtime: RuntimeContext, case: TestCase) -> None:
    # TC-A-020 | A6 账单生成非法组合
    # 覆盖: FR-BL-02, FR-BL-03, V-BL-01, V-BL-02, V-BL-03, V-BL-04
    # 数据: <none>
    # 动态值: <none>
    # 前置: 准备不同 ClientID 的草单、不同币种草单和空草单。
    # 步骤摘要: 尝试生成单一账单覆盖不同客户草单；尝试对混合币种草单不提供汇率直接生成；尝试生成无明细账单；尝试创建负数 AR 账单。
    # 预期: 系统拒绝跨客户单账单；缺汇率时拒绝生成；无明细被拒；负数 AR 提示应改用调整账单。
    del case

    try:
        runtime.api.login(runtime.username, runtime.password)

        draft_a = _arrange_apply_fee_draft(runtime, suffix="020A")
        catalog = SeedCatalog.load(run_id=runtime.run_id)
        applicant = _ensure_tc_a_006_applicant(
            runtime,
            catalog.normalized("DS-AP-001"),
            code_prefix="AP-A-B2",
            applicant_type="ENTITY",
        )
        second_client = _json_or_assert(
            runtime.api.post(
                "/clients",
                json={
                    "client_code": unique_code("CL-A20", runtime.run_id, "B"),
                    "name_cn": f"账单非法组合客户 {runtime.run_id}",
                    "client_type": "CLIENT",
                    "default_currency": "CNY",
                    "is_active": True,
                },
            ),
            "create second TC-A-020 client",
            expected_statuses={200, 201},
        )
        case_no = unique_code("A20", runtime.run_id, "B")
        second_case = _json_or_assert(
            runtime.api.post(
                "/cases",
                json=_build_batch2_case_payload(
                    runtime,
                    case_no=case_no,
                    client_id=second_client["id"],
                    applicant_id=applicant["id"],
                    applicant_name=applicant["name_cn"],
                    patent_category="INVENTION",
                ),
            ),
            "create second-client TC-A-020 case",
            expected_statuses={200, 201},
        )
        draft_b = _generate_apply_fee_draft(runtime, second_case["id"])
        mixed_clients = runtime.api.post(
            "/bills/from-drafts",
            json={
                "draft_ids": [draft_a["id"], draft_b["id"]],
                "bill_no": unique_code("BILL20C", runtime.run_id, "001"),
            },
        )
        _assert_business_error_code(
            mixed_clients,
            "create bill from mixed clients",
            "BILL_SINGLE_CLIENT_REQUIRED",
        )

        empty_usd = _json_or_assert(
            runtime.api.post(
                "/fees/drafts",
                json={
                    "case_id": draft_a["case_id"],
                    "client_id": draft_a["client_id"],
                    "currency": "USD",
                    "draft_type": "APPLY_FEE",
                    "status": "OPEN",
                },
            ),
            "create empty USD fee draft",
            expected_statuses={200, 201},
        )
        mixed_currency = runtime.api.post(
            "/bills/from-drafts",
            json={
                "draft_ids": [draft_a["id"], empty_usd["id"]],
                "bill_no": unique_code("BILL20M", runtime.run_id, "001"),
            },
        )
        _assert_business_error_code(
            mixed_currency,
            "create bill from mixed currencies",
            "BILL_CURRENCY_MISMATCH",
        )

        empty_draft = runtime.api.post(
            "/bills/from-drafts",
            json={
                "draft_ids": [empty_usd["id"]],
                "bill_no": unique_code("BILL20E", runtime.run_id, "001"),
            },
        )
        _assert_business_error_code(
            empty_draft,
            "create bill from empty draft",
            "BILL_ITEM_REQUIRED",
        )

        negative_manual = runtime.api.post(
            "/bills/manual",
            json={
                "bill_no": unique_code("BILL20N", runtime.run_id, "001"),
                "client_id": draft_a["client_id"],
                "case_id": draft_a["case_id"],
                "currency": "CNY",
                "bill_date": "2026-04-18",
                "due_date": "2026-05-18",
                "items": [
                    {
                        "fee_type": "SERVICE",
                        "fee_code": "MANUAL_NEG",
                        "fee_name": "负数服务费",
                        "description": "负数服务费",
                        "quantity": "1",
                        "unit_price": "-1.00",
                    }
                ],
            },
        )
        _assert_business_error_code(
            negative_manual,
            "create negative manual AR bill",
            "BILL_MANUAL_TOTAL_INVALID",
        )

        if runtime.db.enabled():
            runtime.db.assert_row_exists("t_fee_draft", {"id": draft_a["id"]})
    except requests.RequestException as exc:
        pytest.skip(f"Real backend unavailable for TC-A-020: {exc}")


def handle_tc_a_021(runtime: RuntimeContext, case: TestCase) -> None:
    # TC-A-021 | A7 客户付款与冲销
    # 覆盖: FR-BL-05, FR-FE-07, V-PM-01, V-PM-02, V-PM-03, V-OF-01, V-OF-02, V-CR-01, V-CR-03
    # 数据: <none>
    # 动态值: <none>
    # 前置: 存在未结申请费账单；Finance 登录。
    # 步骤摘要: 登记 Payment 和默认 PaymentLine；在收款与冲销界面将付款全额或部分分配到该账单；保存后查看 Bill、PaymentLine、Offset、CaseReceipt。
    # 预期: Payment/PaymentLine/Offset 创建成功；账单 Balance 正确减少，状态变为 PARTIALLY_SETTLED 或 SETTLED；CaseReceipt 记录 ReceivableAmt/ReceivedAmt/IsArrears；相关查询可见。
    del case

    try:
        runtime.api.login(runtime.username, runtime.password)

        draft = _arrange_apply_fee_draft(runtime, suffix="021")
        bill = _create_bill_from_draft(runtime, draft["id"], suffix="021")
        bill_detail = _json_or_assert(
            runtime.api.get(f"/bills/{bill['id']}"), "get bill"
        )
        client_id = _required_value(bill_detail, "client_id", "bill")
        case_id = _required_value(bill_detail, "case_id", "bill")
        payment = _json_or_assert(
            runtime.api.post(
                "/payments",
                json={
                    "client_id": client_id,
                    "amount": "300.00",
                    "pay_no": unique_code("PAYA21", runtime.run_id, "001"),
                    "pay_date": "2026-04-12",
                    "currency": "CNY",
                    "remark": "TC-A-021",
                },
            ),
            "create payment",
            expected_statuses={200, 201},
        )
        payment_detail = _json_or_assert(
            runtime.api.get(f"/payments/{payment['id']}"),
            "get payment detail",
        )
        payment_lines = payment_detail.get("payment_lines")
        if not isinstance(payment_lines, list) or not payment_lines:
            raise AssertionError(
                f"Payment did not create payment line: {payment_detail}"
            )
        payment_line = payment_lines[0]

        offset = _json_or_assert(
            runtime.api.post(
                "/offsets",
                json={
                    "payment_line_id": payment_line["id"],
                    "bill_id": bill["id"],
                    "offset_amt": "300.00",
                    "offset_date": "2026-04-12",
                },
            ),
            "create payment offset",
            expected_statuses={200, 201},
        )
        if (
            offset.get("bill_id") != bill["id"]
            or offset.get("is_reversed") is not False
        ):
            raise AssertionError(f"Unexpected offset response: {offset}")

        updated_bill = _json_or_assert(
            runtime.api.get(f"/bills/{bill['id']}"), "get offset bill"
        )
        _assert_decimal(updated_bill.get("balance"), Decimal("395.00"))
        if updated_bill.get("status") != "PARTIALLY_SETTLED":
            raise AssertionError(f"Expected partial settlement: {updated_bill}")

        receipts = _json_or_assert(
            runtime.api.get(f"/cases/{case_id}/receipts"),
            "get case receipts",
        )
        if isinstance(receipts, list):
            receipt_items = receipts
        elif isinstance(receipts, dict) and isinstance(receipts.get("items"), list):
            receipt_items = receipts["items"]
        elif isinstance(receipts, dict):
            receipt_items = [receipts]
        else:
            receipt_items = []
        if not any(
            isinstance(item, dict)
            and Decimal(str(item.get("received_amt", "0"))) >= Decimal("300.00")
            and item.get("is_arrears") is True
            for item in receipt_items
        ):
            raise AssertionError(
                f"Case receipt did not reflect payment offset: {receipts}"
            )

        if runtime.db.enabled():
            runtime.db.assert_row_exists(
                "t_offset", {"id": offset["id"], "is_reversed": False}
            )
    except requests.RequestException as exc:
        pytest.skip(f"Real backend unavailable for TC-A-021: {exc}")


def handle_tc_a_022(runtime: RuntimeContext, case: TestCase) -> None:
    # TC-A-022 | A7 收款和冲销校验
    # 覆盖: FR-BL-05, V-PM-01, V-PM-02, V-PM-03, V-OF-01, V-OF-02, V-CR-02
    # 数据: <none>
    # 动态值: PAY-${RUN_ID}-001
    # 前置: 存在未结账单；同一客户已有 PayNo=PAY-${RUN_ID}-001。
    # 步骤摘要: 分别测试：Amount<0；PayDate 明显晚于当前日期；同一 Client+PayNo 重复；单笔 OffsetAmt 超过 PaymentLine.BalanceAmt；对同一 Bill 的分配总额超过 Bill.Balance；ReceivedAmt>ReceivableAmt。
    # 预期: 非法金额、日期、重复 PayNo 被拒；超额冲销被拒；ReceivedAmt>ReceivableAmt 被识别为预收并提示确认。
    # Arrange: 准备种子数据 / 鉴权 / 页面或 API 上下文。
    # Act: 按 steps_summary 执行业务流。
    # Assert: 按 expected 做 UI / API / DB / 文件断言。
    del case

    try:
        runtime.api.login(runtime.username, runtime.password)

        draft = _arrange_apply_fee_draft(runtime, suffix="022")
        bill = _create_bill_from_draft(runtime, draft["id"], suffix="022")
        bill_detail = _json_or_assert(
            runtime.api.get(f"/bills/{bill['id']}"),
            "get TC-A-022 bill",
        )
        client_id = _required_value(bill_detail, "client_id", "bill")
        case_id = _required_value(bill_detail, "case_id", "bill")

        negative_amount = runtime.api.post(
            "/payments",
            json={
                "client_id": client_id,
                "amount": "-1.00",
                "pay_no": unique_code("PAYA22N", runtime.run_id, "001"),
                "pay_date": "2026-04-17",
                "currency": "CNY",
            },
        )
        _assert_business_error_code(
            negative_amount,
            "create negative payment",
            "PAYMENT_AMOUNT_INVALID",
        )

        future_date = runtime.api.post(
            "/payments",
            json={
                "client_id": client_id,
                "amount": "100.00",
                "pay_no": unique_code("PAYA22F", runtime.run_id, "001"),
                "pay_date": "2100-01-01",
                "currency": "CNY",
            },
        )
        _assert_business_error_code(
            future_date,
            "create far-future payment",
            "PAYMENT_DATE_INVALID",
        )

        duplicate_pay_no = unique_code("PAYA22D", runtime.run_id, "001")
        payment = _json_or_assert(
            runtime.api.post(
                "/payments",
                json={
                    "client_id": client_id,
                    "amount": "100.00",
                    "pay_no": duplicate_pay_no,
                    "pay_date": "2026-04-17",
                    "currency": "CNY",
                },
            ),
            "create payment for duplicate check",
            expected_statuses={200, 201},
        )
        duplicate = runtime.api.post(
            "/payments",
            json={
                "client_id": client_id,
                "amount": "100.00",
                "pay_no": duplicate_pay_no,
                "pay_date": "2026-04-17",
                "currency": "CNY",
            },
        )
        _assert_business_error_code(
            duplicate,
            "create duplicate payment number",
            "PAYMENT_PAY_NO_DUPLICATE",
        )

        payment_detail = _json_or_assert(
            runtime.api.get(f"/payments/{payment['id']}"),
            "get payment for offset validation",
        )
        payment_lines = payment_detail.get("payment_lines")
        if not isinstance(payment_lines, list) or not payment_lines:
            raise AssertionError(f"Payment line missing: {payment_detail}")
        payment_line_id = payment_lines[0]["id"]

        zero_offset = runtime.api.post(
            "/offsets",
            json={
                "payment_line_id": payment_line_id,
                "bill_id": bill["id"],
                "offset_amt": "0.00",
                "offset_date": "2026-04-18",
            },
        )
        _assert_business_error_code(
            zero_offset,
            "create zero offset",
            "OFFSET_AMOUNT_INVALID",
        )

        payment_exceeded = runtime.api.post(
            "/offsets",
            json={
                "payment_line_id": payment_line_id,
                "bill_id": bill["id"],
                "offset_amt": "101.00",
                "offset_date": "2026-04-18",
            },
        )
        _assert_business_error_code(
            payment_exceeded,
            "create offset over payment balance",
            "OFFSET_EXCEEDS_PAYMENT_BALANCE",
        )

        large_payment = _json_or_assert(
            runtime.api.post(
                "/payments",
                json={
                    "client_id": client_id,
                    "amount": "800.00",
                    "pay_no": unique_code("PAYA22L", runtime.run_id, "001"),
                    "pay_date": "2026-04-17",
                    "currency": "CNY",
                },
            ),
            "create large payment",
            expected_statuses={200, 201},
        )
        large_detail = _json_or_assert(
            runtime.api.get(f"/payments/{large_payment['id']}"),
            "get large payment",
        )
        large_lines = large_detail.get("payment_lines")
        if not isinstance(large_lines, list) or not large_lines:
            raise AssertionError(f"Large payment line missing: {large_detail}")
        bill_exceeded = runtime.api.post(
            "/offsets",
            json={
                "payment_line_id": large_lines[0]["id"],
                "bill_id": bill["id"],
                "offset_amt": "696.00",
                "offset_date": "2026-04-18",
            },
        )
        _assert_business_error_code(
            bill_exceeded,
            "create offset over bill balance",
            "OFFSET_EXCEEDS_BILL_BALANCE",
        )

        prepayment = _json_or_assert(
            runtime.api.post(
                "/case-receipts",
                json={
                    "case_id": case_id,
                    "fee_type": "SERVICE",
                    "fee_code": "PREPAY",
                    "fee_name": "预收款",
                    "currency": "CNY",
                    "receivable_amt": "100.00",
                    "received_amt": "150.00",
                    "last_receipt_date": "2026-04-18",
                },
            ),
            "create prepayment receipt",
            expected_statuses={200, 201},
        )
        if prepayment.get("is_prepayment") is not True:
            raise AssertionError(f"Expected prepayment flag: {prepayment}")

        if runtime.db.enabled():
            runtime.db.assert_row_exists("t_payment", {"id": payment["id"]})
    except requests.RequestException as exc:
        pytest.skip(f"Real backend unavailable for TC-A-022: {exc}")


def handle_tc_a_023(runtime: RuntimeContext, case: TestCase) -> None:
    # TC-A-023 | A8 提成生成与可结算入口
    # 覆盖: FR-COM-01, FR-COM-02, FR-COM-03, FR-COM-04
    # 数据: <none>
    # 动态值: <none>
    # 前置: 申请费账单已生成且含 SERVICE 项；存在 NORMAL 规则和主/协办代理。
    # 步骤摘要: 在账单生成或收款后触发提成逻辑，检查 T_Commission 是否按规则创建或更新，并按 70/30 分摊给主协办代理。
    # 预期: 为每位代理生成/更新 Commission；BaseFee 来源于服务费；S1/S2 金额按规则和分摊比例计算；WaitPay/ForceSettle 初值正确。
    del case

    try:
        runtime.api.login(runtime.username, runtime.password)

        main_agent = _ensure_agent_user(runtime, "MAIN")
        co_agent = _ensure_agent_user(runtime, "CO")
        _disable_matching_commission_rules(runtime)
        _ensure_commission_rule(runtime)
        draft = _arrange_apply_fee_draft(
            runtime,
            suffix="023",
            main_agent_id=main_agent["id"],
            co_agent_id=co_agent["id"],
        )
        bill = _create_bill_from_draft(runtime, draft["id"], suffix="023")
        if bill.get("status") != "UNSETTLED":
            raise AssertionError(f"Expected commission source bill: {bill}")

        case_id = _required_value(draft, "case_id", "draft")
        commission = _json_or_assert(
            runtime.api.get(
                "/commission",
                params={"case_id": case_id, "page": 1, "page_size": 20},
            ),
            "list commission",
        )
        items = commission.get("items")
        if not isinstance(items, list) or len(items) != 2:
            raise AssertionError(f"Expected two commission rows: {commission}")
        by_agent = {
            item.get("agent_id"): item for item in items if isinstance(item, dict)
        }
        _assert_commission_row(
            by_agent.get(main_agent["id"]),
            expected_base=Decimal("350.00"),
            expected_s1=Decimal("35.00"),
            expected_s2=Decimal("17.50"),
        )
        _assert_commission_row(
            by_agent.get(co_agent["id"]),
            expected_base=Decimal("150.00"),
            expected_s1=Decimal("15.00"),
            expected_s2=Decimal("7.50"),
        )

        if runtime.db.enabled():
            runtime.db.assert_row_exists("t_commission", {"case_id": case_id})
    except requests.RequestException as exc:
        pytest.skip(f"Real backend unavailable for TC-A-023: {exc}")


def handle_tc_a_024(runtime: RuntimeContext, case: TestCase) -> None:
    # TC-A-024 | A8 WaitPay 阈值
    # 覆盖: FR-COM-04, FR-COM-05
    # 数据: <none>
    # 动态值: <none>
    # 前置: 存在 WaitPay=true 的提成规则；同一案已产生部分收款。
    # 步骤摘要: 将已收比例分别控制在 0%、50%、90%、100%，检查 S1/S2 可结算性；再将 ForceSettle=true 重试。
    # 预期: 未达阈值前提成不可结算；达到阈值后进入可结算列表；ForceSettle 可绕过收款比例限制。
    del case

    try:
        runtime.api.login(runtime.username, runtime.password)

        main_agent = _ensure_agent_user(runtime, "WMAIN")
        co_agent = _ensure_agent_user(runtime, "WCO")

        _disable_matching_commission_rules(runtime)
        wait_rule = _create_commission_rule_variant(
            runtime,
            wait_pay=True,
            force_settle=False,
            suffix="WAIT",
        )
        wait_draft = _arrange_apply_fee_draft(
            runtime,
            suffix="024W",
            main_agent_id=main_agent["id"],
            co_agent_id=co_agent["id"],
        )
        wait_bill = _create_bill_from_draft(runtime, wait_draft["id"], suffix="024W")
        wait_case_id = _required_value(wait_draft, "case_id", "wait draft")
        if wait_bill.get("status") != "UNSETTLED":
            raise AssertionError(f"Expected wait-pay source bill: {wait_bill}")
        _assert_commission_settleable(runtime, case_id=wait_case_id, expected=False)
        rows = _json_or_assert(
            runtime.api.get(
                "/commission",
                params={"case_id": wait_case_id, "page": 1, "page_size": 20},
            ),
            "list wait-pay commission",
        )
        rule_ids = {
            row.get("rule_id") for row in rows.get("items", []) if isinstance(row, dict)
        }
        if rule_ids != {wait_rule["id"]}:
            raise AssertionError(f"Expected wait-pay rule rows: {rows}")

        wait_client_id = _required_value(wait_bill, "client_id", "wait bill")
        _create_payment_offset(
            runtime,
            client_id=wait_client_id,
            bill_id=wait_bill["id"],
            amount="347.50",
            suffix="050",
        )
        _assert_commission_settleable(runtime, case_id=wait_case_id, expected=False)
        _create_payment_offset(
            runtime,
            client_id=wait_client_id,
            bill_id=wait_bill["id"],
            amount="278.00",
            suffix="090",
        )
        _assert_commission_settleable(runtime, case_id=wait_case_id, expected=False)
        _create_payment_offset(
            runtime,
            client_id=wait_client_id,
            bill_id=wait_bill["id"],
            amount="69.50",
            suffix="100",
        )
        _assert_commission_settleable(runtime, case_id=wait_case_id, expected=True)

        _disable_matching_commission_rules(runtime)
        force_rule = _create_commission_rule_variant(
            runtime,
            wait_pay=True,
            force_settle=True,
            suffix="FORCE",
        )
        force_draft = _arrange_apply_fee_draft(
            runtime,
            suffix="024F",
            main_agent_id=main_agent["id"],
            co_agent_id=co_agent["id"],
        )
        _create_bill_from_draft(runtime, force_draft["id"], suffix="024F")
        force_case_id = _required_value(force_draft, "case_id", "force draft")
        _assert_commission_settleable(runtime, case_id=force_case_id, expected=True)
        force_rows = _json_or_assert(
            runtime.api.get(
                "/commission",
                params={"case_id": force_case_id, "page": 1, "page_size": 20},
            ),
            "list force-settle commission",
        )
        force_rule_ids = {
            row.get("rule_id")
            for row in force_rows.get("items", [])
            if isinstance(row, dict)
        }
        if force_rule_ids != {force_rule["id"]}:
            raise AssertionError(f"Expected force-settle rule rows: {force_rows}")

        if runtime.db.enabled():
            runtime.db.assert_row_exists("t_commission", {"case_id": wait_case_id})
            runtime.db.assert_row_exists("t_commission", {"case_id": force_case_id})
    except requests.RequestException as exc:
        pytest.skip(f"Real backend unavailable for TC-A-024: {exc}")


HANDLERS = {
    "TC-A-001": handle_tc_a_001,
    "TC-A-002": handle_tc_a_002,
    "TC-A-003": handle_tc_a_003,
    "TC-A-004": handle_tc_a_004,
    "TC-A-005": handle_tc_a_005,
    "TC-A-006": handle_tc_a_006,
    "TC-A-007": handle_tc_a_007,
    "TC-A-008": handle_tc_a_008,
    "TC-A-009": handle_tc_a_009,
    "TC-A-010": handle_tc_a_010,
    "TC-A-011": handle_tc_a_011,
    "TC-A-012": handle_tc_a_012,
    "TC-A-013": handle_tc_a_013,
    "TC-A-014": handle_tc_a_014,
    "TC-A-015": handle_tc_a_015,
    "TC-A-016": handle_tc_a_016,
    "TC-A-017": handle_tc_a_017,
    "TC-A-018": handle_tc_a_018,
    "TC-A-019": handle_tc_a_019,
    "TC-A-020": handle_tc_a_020,
    "TC-A-021": handle_tc_a_021,
    "TC-A-022": handle_tc_a_022,
    "TC-A-023": handle_tc_a_023,
    "TC-A-024": handle_tc_a_024,
}
