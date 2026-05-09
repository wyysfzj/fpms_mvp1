from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any

import pytest
import requests

from framework.helpers import skeleton_case, unique_code
from framework.models import TestCase
from framework.runtime import RuntimeContext


def handle_tc_x_001(runtime: RuntimeContext, case: TestCase) -> None:
    # TC-X-001 | 高级案件查询-基本维度
    # 覆盖: FR-CM-01
    # 数据: <none>
    # 动态值: <none>
    # 前置: 系统中存在 NORMAL/PCT/INVALIDATION/CONSULTING 等多类案件。
    # 步骤摘要: 按 CaseNo、AppNo、CaseType、PatentCategory、FlowDir、Status、RecvDate/FilingDate/GrantDate 等组合查询。
    # 预期: 结果集准确，字段列完整，可跳转案卷详情。
    del case
    try:
        runtime.api.login(runtime.username, runtime.password)
        client = _ensure_x_client(runtime, "001")
        applicant = _ensure_x_applicant(runtime, "001")
        case_data = _ensure_x_query_case(runtime, client, applicant)
        case_id = _required_value(case_data, "id", "X1 case")
        case_no = _required_value(case_data, "case_no", "X1 case")
        app_no = _required_value(case_data, "app_no", "X1 case")

        _assert_case_query_hit(
            runtime,
            "case_no",
            {"case_no": case_no, "page": 1, "page_size": 20},
            case_id,
        )
        _assert_case_query_hit(
            runtime,
            "app_no",
            {"app_no": app_no, "page": 1, "page_size": 20},
            case_id,
        )
        _assert_case_query_hit(
            runtime,
            "basic dimensions",
            {
                "case_type": "NORMAL",
                "patent_category": "INV",
                "flow_dir": "CN_DOMESTIC",
                "status": "NOT_FILED",
                "client_id": client["id"],
                "filing_date_from": "2026-02-01",
                "filing_date_to": "2026-02-28",
                "page": 1,
                "page_size": 100,
            },
            case_id,
        )
        _assert_case_export_hit(
            runtime,
            "case export",
            {
                "case_no": case_no,
                "page": 1,
                "page_size": 20,
            },
            case_id,
        )

        detail = _json_or_assert(runtime.api.get(f"/cases/{case_id}"), "get X1 case")
        _assert_equal(detail.get("case_no"), case_no, "detail case_no")
        _assert_equal(detail.get("app_no"), app_no, "detail app_no")
        _assert_equal(detail.get("case_type"), "NORMAL", "detail case_type")
        _assert_equal(detail.get("patent_category"), "INV", "detail patent_category")
        _assert_equal(detail.get("flow_dir"), "CN_DOMESTIC", "detail flow_dir")
        if runtime.db.enabled():
            runtime.db.assert_row_exists("t_case", {"id": case_id, "case_no": case_no})
    except requests.RequestException as exc:
        pytest.skip(f"Real backend unavailable for TC-X-001: {exc}")


def _ensure_x_query_case(
    runtime: RuntimeContext,
    client: dict[str, Any],
    applicant: dict[str, Any],
) -> dict[str, Any]:
    case_no = unique_code("CASE-X", runtime.run_id, "001")
    existing = _find_item(
        _json_or_assert(
            runtime.api.get(
                "/cases",
                params={"case_no": case_no, "page": 1, "page_size": 20},
            ),
            "search X1 case",
        ),
        "case_no",
        case_no,
    )
    if existing is not None:
        return _json_or_assert(
            runtime.api.get(f"/cases/{existing['id']}"), "get X1 case"
        )

    payload = {
        "case_no": case_no,
        "case_type": "NORMAL",
        "patent_category": "INV",
        "flow_dir": "CN_DOMESTIC",
        "status": "NOT_FILED",
        "client_id": client["id"],
        "title_cn": f"X1 高级案件查询案卷 {runtime.run_id}",
        "app_no": unique_code("APP-X", runtime.run_id, "001"),
        "filing_date": "2026-02-10",
        "from_country": "CN",
        "applicants": [
            {
                "seq": 1,
                "is_first": True,
                "applicant_id": applicant["id"],
                "name_cn": applicant["name_cn"],
            }
        ],
    }
    return _json_or_assert(
        runtime.api.post("/cases", json=payload),
        "create X1 case",
        expected_statuses={201},
    )


def _ensure_x_client(runtime: RuntimeContext, suffix: str) -> dict[str, Any]:
    code = unique_code("CL-X", runtime.run_id, suffix)
    existing = _find_item(
        _json_or_assert(
            runtime.api.get("/clients", params={"page": 1, "page_size": 20, "q": code}),
            "search X client",
        ),
        "client_code",
        code,
    )
    if existing is not None:
        return existing
    return _json_or_assert(
        runtime.api.post(
            "/clients",
            json={
                "client_code": code,
                "name_cn": f"X波查询客户-{suffix}-{runtime.run_id}",
                "client_type": "CLIENT",
                "default_currency": "CNY",
                "is_active": True,
            },
        ),
        "create X client",
        expected_statuses={201},
    )


def _ensure_x_applicant(runtime: RuntimeContext, suffix: str) -> dict[str, Any]:
    code = unique_code("AP-X", runtime.run_id, suffix)
    existing = _find_item(
        _json_or_assert(
            runtime.api.get(
                "/applicants", params={"page": 1, "page_size": 20, "q": code}
            ),
            "search X applicant",
        ),
        "code",
        code,
    )
    if existing is not None:
        return existing
    return _json_or_assert(
        runtime.api.post(
            "/applicants",
            json={
                "code": code,
                "name_cn": f"X波查询申请人-{suffix}-{runtime.run_id}",
                "is_active": True,
            },
        ),
        "create X applicant",
        expected_statuses={201},
    )


def _assert_case_query_hit(
    runtime: RuntimeContext,
    label: str,
    params: dict[str, Any],
    case_id: str,
) -> None:
    payload = _json_or_assert(
        runtime.api.get("/cases", params=params), f"query {label}"
    )
    items = payload.get("items")
    if not isinstance(items, list):
        raise AssertionError(f"{label} query missing items: {payload}")
    if not any(isinstance(item, dict) and item.get("id") == case_id for item in items):
        raise AssertionError(f"{label} query did not return case {case_id}: {payload}")


def _assert_case_export_hit(
    runtime: RuntimeContext,
    label: str,
    params: dict[str, Any],
    case_id: str,
) -> None:
    payload = _json_or_assert(
        runtime.api.get("/cases/export", params=params), f"export {label}"
    )
    items = _items_or_assert(payload, label)
    if not any(item.get("id") == case_id for item in items):
        raise AssertionError(f"{label} did not export case {case_id}: {payload}")


def _ensure_x_fee_overview_case(
    runtime: RuntimeContext,
    client: dict[str, Any],
    applicant: dict[str, Any],
) -> dict[str, Any]:
    case_no = unique_code("CASE-X", runtime.run_id, "004")
    existing = _find_item(
        _json_or_assert(
            runtime.api.get(
                "/cases",
                params={"case_no": case_no, "page": 1, "page_size": 20},
            ),
            "search X4 case",
        ),
        "case_no",
        case_no,
    )
    if existing is not None:
        return _json_or_assert(
            runtime.api.get(f"/cases/{existing['id']}"), "get X4 case"
        )

    payload = {
        "case_no": case_no,
        "case_type": "NORMAL",
        "patent_category": "INV",
        "flow_dir": "CN_DOMESTIC",
        "status": "NOT_FILED",
        "client_id": client["id"],
        "title_cn": f"X4 费用情况查询案卷 {runtime.run_id}",
        "app_no": unique_code("APP-X", runtime.run_id, "004"),
        "filing_date": "2026-04-03",
        "from_country": "CN",
        "applicants": [
            {
                "seq": 1,
                "is_first": True,
                "applicant_id": applicant["id"],
                "name_cn": applicant["name_cn"],
            }
        ],
    }
    return _json_or_assert(
        runtime.api.post("/cases", json=payload),
        "create X4 case",
        expected_statuses={201},
    )


def _ensure_x_case_receipt(runtime: RuntimeContext, case_id: str) -> dict[str, Any]:
    fee_code = unique_code("RCPT-X", runtime.run_id, "004")
    existing = _find_fee_overview_case_receipt(
        _json_or_assert(
            runtime.api.get(
                "/fee-overview/case-receipts",
                params={"fee_type": "SERVICE", "page": 1, "page_size": 100},
            ),
            "search X4 case receipt overview",
        ),
        fee_code,
    )
    if existing is not None:
        return {"id": existing["receipt_id"]}

    return _json_or_assert(
        runtime.api.post(
            "/case-receipts",
            json={
                "case_id": case_id,
                "fee_type": "SERVICE",
                "fee_code": fee_code,
                "fee_name": "X4 服务费",
                "currency": "CNY",
                "receivable_amt": "300.00",
                "received_amt": "200.00",
                "last_receipt_date": "2026-04-12",
                "due_date": "2026-04-20",
                "is_arrears": True,
                "is_prepayment": False,
                "is_commissionable": True,
                "invoice_no": unique_code("INV-X", runtime.run_id, "004"),
            },
        ),
        "create X4 case receipt",
        expected_statuses={201},
    )


def _find_fee_overview_case_receipt(
    payload: dict[str, Any],
    fee_code: str,
) -> dict[str, Any] | None:
    for item in _items_or_assert(payload, "fee overview case receipts"):
        if item.get("fee_code") == fee_code:
            return item
    return None


def _ensure_x_gov_payment(
    runtime: RuntimeContext,
    client: dict[str, Any],
    case_id: str,
) -> dict[str, Any]:
    fee_code = unique_code("GOV-X", runtime.run_id, "004")
    existing = _find_fee_overview_gov_payment(
        _json_or_assert(
            runtime.api.get(
                "/fee-overview/gov-payments",
                params={"fee_type": "ANNUITY_FEE", "page": 1, "page_size": 100},
            ),
            "search X4 gov payment overview",
        ),
        fee_code,
    )
    if existing is not None:
        return {"id": existing["gov_payment_id"]}

    rate = _ensure_x_fee_rate(runtime, fee_code)
    draft = _json_or_assert(
        runtime.api.post(
            "/fees/drafts",
            json={
                "case_id": case_id,
                "client_id": client["id"],
                "draft_type": "ANNUITY_FEE",
                "currency": "CNY",
            },
        ),
        "create X4 gov fee draft",
        expected_statuses={201},
    )
    item = _json_or_assert(
        runtime.api.post(
            f"/fees/drafts/{draft['id']}/items",
            json={"rate_id": rate["id"], "quantity": "1", "unit_price": "180.00"},
        ),
        "create X4 gov fee item",
        expected_statuses={201},
    )
    pay_list_result = _json_or_assert(
        runtime.api.post(
            "/pay-lists/from-fee-items",
            json={
                "fee_item_ids": [item["id"]],
                "planned_pay_date": "2026-04-10",
                "remark": "X4 费用情况查询官费清单",
            },
        ),
        "create X4 pay list",
    )
    pay_list = pay_list_result.get("pay_list")
    if not isinstance(pay_list, dict):
        raise AssertionError(f"pay list response missing pay_list: {pay_list_result}")
    payment_result = _json_or_assert(
        runtime.api.post(
            "/gov-payments",
            json={
                "pay_list_id": pay_list["id"],
                "fee_item_id": item["id"],
                "paid_date": "2026-04-11",
                "paid_amount": "180.00",
                "official_receipt_no": unique_code("OFF-X", runtime.run_id, "004"),
            },
        ),
        "create X4 gov payment",
    )
    gov_payment = payment_result.get("gov_payment")
    if not isinstance(gov_payment, dict):
        raise AssertionError(
            f"gov payment response missing gov_payment: {payment_result}"
        )
    return gov_payment


def _ensure_x_fee_rate(runtime: RuntimeContext, fee_code: str) -> dict[str, Any]:
    existing = _find_item(
        _json_or_assert(
            runtime.api.get(
                "/fees/rates",
                params={"fee_code": fee_code, "page": 1, "page_size": 20},
            ),
            "search X4 fee rate",
        ),
        "fee_code",
        fee_code,
    )
    payload = {
        "fee_code": fee_code,
        "fee_name": "X4 官费",
        "fee_type": "GOV",
        "currency": "CNY",
        "default_amount": "180.00",
        "enabled": True,
        "calc_mode": "FIXED",
        "allow_reduction": False,
    }
    if existing is not None:
        return _json_or_assert(
            runtime.api.put(f"/fees/rates/{existing['id']}", json=payload),
            "update X4 fee rate",
        )
    return _json_or_assert(
        runtime.api.post("/fees/rates", json=payload),
        "create X4 fee rate",
        expected_statuses={201},
    )


def _find_fee_overview_gov_payment(
    payload: dict[str, Any],
    fee_code: str,
) -> dict[str, Any] | None:
    for item in _items_or_assert(payload, "fee overview gov payments"):
        if item.get("fee_code") == fee_code:
            return item
    return None


def _assert_fee_overview_case_receipt_hit(
    runtime: RuntimeContext,
    label: str,
    params: dict[str, Any],
    receipt_id: str,
) -> None:
    payload = _json_or_assert(
        runtime.api.get("/fee-overview/case-receipts", params=params),
        f"query {label}",
    )
    items = _items_or_assert(payload, label)
    if not any(item.get("receipt_id") == receipt_id for item in items):
        raise AssertionError(f"{label} did not return receipt {receipt_id}: {payload}")


def _assert_fee_overview_gov_payment_hit(
    runtime: RuntimeContext,
    label: str,
    params: dict[str, Any],
    gov_payment_id: int,
) -> None:
    payload = _json_or_assert(
        runtime.api.get("/fee-overview/gov-payments", params=params),
        f"query {label}",
    )
    items = _items_or_assert(payload, label)
    if not any(item.get("gov_payment_id") == gov_payment_id for item in items):
        raise AssertionError(
            f"{label} did not return gov payment {gov_payment_id}: {payload}"
        )


def _items_or_assert(payload: dict[str, Any], label: str) -> list[dict[str, Any]]:
    items = payload.get("items")
    if not isinstance(items, list):
        raise AssertionError(f"{label} missing items: {payload}")
    if not all(isinstance(item, dict) for item in items):
        raise AssertionError(f"{label} contains non-object item: {payload}")
    return items


def _ensure_x_task_case(
    runtime: RuntimeContext,
    client: dict[str, Any],
    applicant: dict[str, Any],
    *,
    suffix: str = "017",
    title_label: str = "我的任务与监督任务案卷",
) -> dict[str, Any]:
    case_no = unique_code("CASE-X", runtime.run_id, suffix)
    existing = _find_item(
        _json_or_assert(
            runtime.api.get(
                "/cases",
                params={"case_no": case_no, "page": 1, "page_size": 20},
            ),
            f"search X{suffix} case",
        ),
        "case_no",
        case_no,
    )
    if existing is not None:
        return _json_or_assert(
            runtime.api.get(f"/cases/{existing['id']}"), f"get X{suffix} case"
        )

    payload = {
        "case_no": case_no,
        "case_type": "NORMAL",
        "patent_category": "INV",
        "flow_dir": "CN_DOMESTIC",
        "status": "NOT_FILED",
        "client_id": client["id"],
        "title_cn": f"X{suffix} {title_label} {runtime.run_id}",
        "app_no": unique_code("APP-X", runtime.run_id, suffix),
        "filing_date": date.today().isoformat(),
        "from_country": "CN",
        "applicants": [
            {
                "seq": 1,
                "is_first": True,
                "applicant_id": applicant["id"],
                "name_cn": applicant["name_cn"],
            }
        ],
    }
    return _json_or_assert(
        runtime.api.post("/cases", json=payload),
        f"create X{suffix} case",
        expected_statuses={201},
    )


def _ensure_x_today_task(
    runtime: RuntimeContext,
    case_id: str,
    user_id: str,
) -> dict[str, Any]:
    title = unique_code("X17 今日任务", runtime.run_id, "001")
    existing = _find_item(
        _json_or_assert(
            runtime.api.get(
                "/tasks",
                params={
                    "case_id": case_id,
                    "status": "OPEN",
                    "page": 1,
                    "page_size": 100,
                },
            ),
            "search X17 task",
        ),
        "title",
        title,
    )
    if existing is not None:
        return existing

    today = date.today().isoformat()
    return _json_or_assert(
        runtime.api.post(
            "/tasks",
            json={
                "case_id": case_id,
                "title": title,
                "base_date": today,
                "due_date": today,
                "internal_due_date": today,
                "worker_id": user_id,
                "supervisor_id": user_id,
                "remark": "X17 automation task",
            },
        ),
        "create X17 task",
        expected_statuses={201},
    )


def _ensure_x_special_task_case(
    runtime: RuntimeContext,
    client: dict[str, Any],
    applicant: dict[str, Any],
    *,
    suffix: str = "005",
    title_label: str = "申请费时限检索案卷",
    extra_payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    case_no = unique_code("CASE-X", runtime.run_id, suffix)
    existing = _find_item(
        _json_or_assert(
            runtime.api.get(
                "/cases",
                params={"case_no": case_no, "page": 1, "page_size": 20},
            ),
            f"search X{suffix} case",
        ),
        "case_no",
        case_no,
    )
    if existing is not None:
        return _json_or_assert(
            runtime.api.get(f"/cases/{existing['id']}"), f"get X{suffix} case"
        )

    payload = {
        "case_no": case_no,
        "case_type": "NORMAL",
        "patent_category": "INV",
        "flow_dir": "CN_DOMESTIC",
        "status": "NOT_FILED",
        "client_id": client["id"],
        "title_cn": f"X{suffix} {title_label} {runtime.run_id}",
        "app_no": unique_code("APP-X", runtime.run_id, suffix),
        "filing_date": date.today().isoformat(),
        "from_country": "CN",
        "applicants": [
            {
                "seq": 1,
                "is_first": True,
                "applicant_id": applicant["id"],
                "name_cn": applicant["name_cn"],
            }
        ],
    }
    if extra_payload:
        payload.update(extra_payload)
    return _json_or_assert(
        runtime.api.post("/cases", json=payload),
        f"create X{suffix} case",
        expected_statuses={201},
    )


def _ensure_x_task_template(runtime: RuntimeContext, code: str) -> dict[str, Any]:
    templates = _json_or_assert(
        runtime.api.get("/task-templates"), "list task templates"
    )
    if not isinstance(templates, list):
        raise AssertionError(f"Task template list response was not a list: {templates}")
    for template in templates:
        if isinstance(template, dict) and template.get("code") == code:
            return template
    return _json_or_assert(
        runtime.api.post(
            "/task-templates",
            json={
                "code": code,
                "name": f"X波专项期限模板-{code}",
                "description": "Created by Skeleton Pack X-wave coverage handler",
            },
        ),
        f"create task template {code}",
        expected_statuses={201},
    )


def _ensure_x_special_search_task(
    runtime: RuntimeContext,
    case_id: str,
    task_template_id: str,
    *,
    suffix: str = "005",
    title_prefix: str = "X5 申请费时限任务",
    remark: str = "X5 automation apply fee limit task",
) -> dict[str, Any]:
    title = unique_code(title_prefix, runtime.run_id, "001")
    existing = _find_item(
        _json_or_assert(
            runtime.api.get(
                "/tasks",
                params={
                    "case_id": case_id,
                    "status": "OPEN",
                    "page": 1,
                    "page_size": 100,
                },
            ),
            f"search X{suffix} special-search task",
        ),
        "title",
        title,
    )
    if existing is not None:
        return existing

    today = date.today().isoformat()
    return _json_or_assert(
        runtime.api.post(
            "/tasks",
            json={
                "case_id": case_id,
                "task_template_id": task_template_id,
                "title": title,
                "base_date": today,
                "due_date": today,
                "internal_due_date": today,
                "remark": remark,
            },
        ),
        f"create X{suffix} special-search task",
        expected_statuses={201},
    )


def _assert_special_search_hit(
    runtime: RuntimeContext,
    label: str,
    params: dict[str, Any],
    task_id: str,
) -> None:
    payload = _json_or_assert(
        runtime.api.get("/tasks/special/search", params=params),
        f"query {label}",
    )
    items = _items_or_assert(payload, label)
    if not any(item.get("task_id") == task_id for item in items):
        raise AssertionError(f"{label} did not return task {task_id}: {payload}")


def _assert_task_list_hit(
    runtime: RuntimeContext,
    label: str,
    path: str,
    params: dict[str, Any],
    task_id: str,
) -> None:
    payload = _json_or_assert(runtime.api.get(path, params=params), f"query {label}")
    items = _items_or_assert(payload, label)
    if not any(item.get("id") == task_id for item in items):
        raise AssertionError(f"{label} did not return task {task_id}: {payload}")


def _assert_output_response(response: Any, label: str, content_type_hint: str) -> None:
    status_code = getattr(response, "status_code", None)
    if status_code != 200:
        raise AssertionError(f"{label} failed with status {status_code}: {response!r}")
    headers = getattr(response, "headers", {})
    content_type = str(headers.get("content-type", "")).lower()
    if content_type_hint not in content_type:
        raise AssertionError(
            f"{label} expected content type containing {content_type_hint!r}, "
            f"got {content_type!r}"
        )


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


def _find_item(
    payload: dict[str, Any],
    field: str,
    value: Any,
) -> dict[str, Any] | None:
    items = payload.get("items")
    if not isinstance(items, list):
        raise AssertionError(f"List response missing items: {payload}")
    for item in items:
        if isinstance(item, dict) and item.get(field) == value:
            return item
    return None


def _required_value(payload: dict[str, Any], field: str, label: str) -> Any:
    value = payload.get(field)
    if value in (None, ""):
        raise AssertionError(f"{label} missing required field: {field}")
    return value


def _assert_equal(actual: Any, expected: Any, label: str) -> None:
    if actual != expected:
        raise AssertionError(f"{label} expected {expected!r}, got {actual!r}")


@skeleton_case
def handle_tc_x_002(runtime: RuntimeContext, case: TestCase) -> None:
    # TC-X-002 | 高级案件查询-控制标记与费用维度
    # 覆盖: FR-DL-07, FR-FE-09
    # 数据: <none>
    # 动态值: <none>
    # 前置: 系统中存在有/无费减、有/无年费监视、有/无未结账单的案件。
    # 步骤摘要: 按 IsFeeMonitor、ApplicantKind、HasExamRequest、NoPower、NoPrioText、FeeReduction、未结账单、年费欠款等维度查询。
    # 预期: 联查条件生效，结果准确。
    # Arrange: 准备种子数据 / 鉴权 / 页面或 API 上下文。
    # Act: 按 steps_summary 执行业务流。
    # Assert: 按 expected 做 UI / API / DB / 文件断言。
    return None


def handle_tc_x_003(runtime: RuntimeContext, case: TestCase) -> None:
    # TC-X-003 | 中间文件查询与清单导出
    # 覆盖: FR-WD-07
    # 数据: <none>
    # 动态值: <none>
    # 前置: 存在多种 DocType 和模板的文档。
    # 步骤摘要: 按 DocType、TemplateCode、CaseNo、Client、DispatchDate、NeedReply/ReplyDate 查询并导出清单/证书清单。
    # 预期: 查询结果正确；导出文件内容与过滤条件一致。
    del case
    try:
        runtime.api.login(runtime.username, runtime.password)
        client = _ensure_x_client(runtime, "003")
        applicant = _ensure_x_applicant(runtime, "003")
        case_data = _ensure_x_special_task_case(
            runtime,
            client,
            applicant,
            suffix="003",
            title_label="中间文件查询案卷",
        )
        document = _ensure_x_outbound_document(runtime, case_data["id"], "003")
        document_id = _required_value(document, "id", "X3 document")
        title = _required_value(document, "title", "X3 document")
        case_no = _required_value(case_data, "case_no", "X3 case")

        _assert_document_query_hit(
            runtime,
            "title query",
            {"q": title, "page": 1, "page_size": 20},
            document_id,
        )
        _assert_document_query_hit(
            runtime,
            "case number query",
            {"case_no": case_no, "page": 1, "page_size": 20},
            document_id,
        )
        _assert_document_query_hit(
            runtime,
            "client and document type query",
            {
                "client_id": client["id"],
                "direction": "OUT",
                "doc_type": ["CLIENT_OUT"],
                "date_from": "2026-05-01",
                "date_to": "2026-05-31",
                "page": 1,
                "page_size": 20,
            },
            document_id,
        )
    except requests.RequestException as exc:
        pytest.skip(f"Real backend unavailable for TC-X-003: {exc}")


def _assert_document_query_hit(
    runtime: RuntimeContext,
    label: str,
    params: dict[str, Any],
    document_id: str,
) -> None:
    payload = _json_or_assert(
        runtime.api.get("/documents", params=params), f"query X3 documents by {label}"
    )
    if not any(
        item.get("id") == document_id for item in _items_or_assert(payload, "documents")
    ):
        raise AssertionError(
            f"{label} did not include document {document_id}: {payload}"
        )


def handle_tc_x_004(runtime: RuntimeContext, case: TestCase) -> None:
    # TC-X-004 | 费用情况查询双表
    # 覆盖: FR-FE-09
    # 数据: <none>
    # 动态值: <none>
    # 前置: 存在 GovPayment 和 CaseReceipt 数据。
    # 步骤摘要: 进入费用情况查询，按 CaseNo/AppNo/Client/日期范围检索。
    # 预期: 上半表显示官费缴费一览，下半表显示个案收款一览；字段与金额对应正确。
    del case
    try:
        runtime.api.login(runtime.username, runtime.password)
        client = _ensure_x_client(runtime, "004")
        applicant = _ensure_x_applicant(runtime, "004")
        case_data = _ensure_x_fee_overview_case(runtime, client, applicant)
        case_id = _required_value(case_data, "id", "X4 case")
        case_no = _required_value(case_data, "case_no", "X4 case")
        applicant_name = applicant["name_cn"]

        receipt = _ensure_x_case_receipt(runtime, case_id)
        _assert_fee_overview_case_receipt_hit(
            runtime,
            "case receipt case_no",
            {"case_no": case_no, "page": 1, "page_size": 20},
            receipt["id"],
        )
        _assert_fee_overview_case_receipt_hit(
            runtime,
            "case receipt applicant/date",
            {
                "applicant_name": applicant_name,
                "receipt_date_from": "2026-04-01",
                "receipt_date_to": "2026-04-30",
                "fee_type": "SERVICE",
                "page": 1,
                "page_size": 20,
            },
            receipt["id"],
        )

        gov_payment = _ensure_x_gov_payment(runtime, client, case_id)
        _assert_fee_overview_gov_payment_hit(
            runtime,
            "gov payment case_no",
            {"case_no": case_no, "page": 1, "page_size": 20},
            gov_payment["id"],
        )
        _assert_fee_overview_gov_payment_hit(
            runtime,
            "gov payment applicant/date",
            {
                "applicant_name": applicant_name,
                "paid_date_from": "2026-04-01",
                "paid_date_to": "2026-04-30",
                "fee_type": "ANNUITY_FEE",
                "page": 1,
                "page_size": 20,
            },
            gov_payment["id"],
        )
        if runtime.db.enabled():
            runtime.db.assert_row_exists("t_case_receipt", {"id": receipt["id"]})
    except requests.RequestException as exc:
        pytest.skip(f"Real backend unavailable for TC-X-004: {exc}")


def handle_tc_x_005(runtime: RuntimeContext, case: TestCase) -> None:
    # TC-X-005 | 申请费时限检索
    # 覆盖: FR-DL-07
    # 数据: <none>
    # 动态值: <none>
    # 前置: 存在 OPEN 的 APPLY_FEE_LIMIT 任务，部分已有草单或清单。
    # 步骤摘要: 按 Deadline 区间、CaseType、Client、Agent 查询申请费时限。
    # 预期: 仅未完成申请费时限返回；可看到是否已有草单/官费清单等辅助字段。
    del case
    try:
        runtime.api.login(runtime.username, runtime.password)
        client = _ensure_x_client(runtime, "005")
        applicant = _ensure_x_applicant(runtime, "005")
        case_data = _ensure_x_special_task_case(runtime, client, applicant)
        case_id = _required_value(case_data, "id", "X5 case")
        case_no = _required_value(case_data, "case_no", "X5 case")
        template = _ensure_x_task_template(runtime, "APPLY_FEE_LIMIT")
        template_id = _required_value(template, "id", "APPLY_FEE_LIMIT template")
        task = _ensure_x_special_search_task(runtime, case_id, template_id)
        task_id = _required_value(task, "id", "X5 apply-fee task")
        due_date = _required_value(task, "due_date", "X5 apply-fee task")

        _assert_special_search_hit(
            runtime,
            "apply-fee special search by case and deadline",
            {
                "task_code": "APPLY_FEE_LIMIT",
                "status": "OPEN",
                "case_no": case_no,
                "due_date_from": due_date,
                "due_date_to": due_date,
                "page": 1,
                "page_size": 20,
            },
            task_id,
        )
        _assert_special_search_hit(
            runtime,
            "apply-fee special search by client",
            {
                "task_code": "APPLY_FEE_LIMIT",
                "client_name": client["name_cn"],
                "is_overdue": False,
                "page": 1,
                "page_size": 20,
            },
            task_id,
        )
        _assert_output_response(
            runtime.api.get(
                "/tasks/special/search/export",
                params={"task_code": "APPLY_FEE_LIMIT", "status": "OPEN"},
            ),
            "apply-fee special search export",
            "spreadsheet",
        )
        _assert_output_response(
            runtime.api.get(
                "/tasks/special/search/print",
                params={"task_code": "APPLY_FEE_LIMIT", "status": "OPEN"},
            ),
            "apply-fee special search print",
            "text/html",
        )
        if runtime.db.enabled():
            runtime.db.assert_row_exists("t_task", {"id": task_id, "status": "OPEN"})
    except requests.RequestException as exc:
        pytest.skip(f"Real backend unavailable for TC-X-005: {exc}")


def handle_tc_x_006(runtime: RuntimeContext, case: TestCase) -> None:
    # TC-X-006 | 实审请求时限检索
    # 覆盖: FR-DL-07
    # 数据: <none>
    # 动态值: <none>
    # 前置: 存在 EXAM_REQUEST_LIMIT 任务，部分案件 HasExamRequest=true。
    # 步骤摘要: 按 Deadline 区间和 HasExamRequest=false 条件查询。
    # 预期: 仅尚未提实审且任务未完成的案件被返回。
    del case
    try:
        runtime.api.login(runtime.username, runtime.password)
        client = _ensure_x_client(runtime, "006")
        applicant = _ensure_x_applicant(runtime, "006")
        case_data = _ensure_x_special_task_case(
            runtime,
            client,
            applicant,
            suffix="006",
            title_label="实审请求时限检索案卷",
            extra_payload={"has_exam_request": False},
        )
        case_id = _required_value(case_data, "id", "X6 case")
        case_no = _required_value(case_data, "case_no", "X6 case")
        template = _ensure_x_task_template(runtime, "EXAM_REQUEST_LIMIT")
        template_id = _required_value(template, "id", "EXAM_REQUEST_LIMIT template")
        task = _ensure_x_special_search_task(
            runtime,
            case_id,
            template_id,
            suffix="006",
            title_prefix="X6 实审请求时限任务",
            remark="X6 automation exam request limit task",
        )
        task_id = _required_value(task, "id", "X6 exam-request task")
        due_date = _required_value(task, "due_date", "X6 exam-request task")

        _assert_special_search_hit(
            runtime,
            "exam-request special search by case and deadline",
            {
                "task_code": "EXAM_REQUEST_LIMIT",
                "status": "OPEN",
                "case_no": case_no,
                "due_date_from": due_date,
                "due_date_to": due_date,
                "page": 1,
                "page_size": 20,
            },
            task_id,
        )
        _assert_special_search_hit(
            runtime,
            "exam-request special search by client",
            {
                "task_code": "EXAM_REQUEST_LIMIT",
                "client_name": client["name_cn"],
                "is_overdue": False,
                "page": 1,
                "page_size": 20,
            },
            task_id,
        )
        _assert_output_response(
            runtime.api.get(
                "/tasks/special/search/export",
                params={"task_code": "EXAM_REQUEST_LIMIT", "status": "OPEN"},
            ),
            "exam-request special search export",
            "spreadsheet",
        )
        _assert_output_response(
            runtime.api.get(
                "/tasks/special/search/print",
                params={"task_code": "EXAM_REQUEST_LIMIT", "status": "OPEN"},
            ),
            "exam-request special search print",
            "text/html",
        )
        if runtime.db.enabled():
            runtime.db.assert_row_exists("t_task", {"id": task_id, "status": "OPEN"})
    except requests.RequestException as exc:
        pytest.skip(f"Real backend unavailable for TC-X-006: {exc}")


def handle_tc_x_007(runtime: RuntimeContext, case: TestCase) -> None:
    # TC-X-007 | 案件统计报表
    # 覆盖: FR-CM-04
    # 数据: <none>
    # 动态值: <none>
    # 前置: 系统中有多客户、多国别、多代理人、多状态案件。
    # 步骤摘要: 生成按客户/国别/代理人/年度的案件统计报表。
    # 预期: 新案数、授权数、终止/无效数、在审数量等指标正确。
    del case
    try:
        runtime.api.login(runtime.username, runtime.password)
        client = _ensure_x_client(runtime, "007")
        applicant = _ensure_x_applicant(runtime, "007")
        _ensure_x_special_task_case(
            runtime,
            client,
            applicant,
            suffix="007G",
            title_label="案件统计授权案卷",
            extra_payload={
                "status": "GRANTED",
                "from_country": "CN",
                "to_country": "US",
                "grant_date": "2026-05-01",
            },
        )
        _ensure_x_special_task_case(
            runtime,
            client,
            applicant,
            suffix="007T",
            title_label="案件统计终止案卷",
            extra_payload={
                "status": "TERMINATED",
                "from_country": "CN",
                "to_country": "JP",
                "terminated_date": "2026-05-02",
            },
        )
        _ensure_x_special_task_case(
            runtime,
            client,
            applicant,
            suffix="007P",
            title_label="案件统计在审案卷",
            extra_payload={
                "status": "PENDING",
                "from_country": "CN",
                "to_country": "KR",
                "filing_date": "2026-05-03",
            },
        )
        report = _json_or_assert(
            runtime.api.get(
                "/cases",
                params={"client_id": client["id"], "page": 1, "page_size": 100},
            ),
            "query X7 case report",
        )
        _assert_x_case_report_summary(report, client["id"])
    except requests.RequestException as exc:
        pytest.skip(f"Real backend unavailable for TC-X-007: {exc}")


def _assert_x_case_report_summary(payload: dict[str, Any], client_id: str) -> None:
    summary = payload.get("summary")
    if not isinstance(summary, dict):
        raise AssertionError(f"Case report response missing summary: {payload}")
    if int(summary.get("total_case_count") or 0) < 3:
        raise AssertionError(f"Case report total too low: {payload}")

    status_counts = _count_map(summary.get("status_counts"), "status_counts")
    for status_key in ("GRANTED", "TERMINATED", "PENDING"):
        if status_counts.get(status_key, 0) < 1:
            raise AssertionError(f"Case report missing status {status_key}: {payload}")

    client_counts = _count_map(summary.get("client_counts"), "client_counts")
    if client_counts.get(client_id, 0) < 3:
        raise AssertionError(f"Case report missing client count {client_id}: {payload}")

    country_counts = _count_map(summary.get("country_counts"), "country_counts")
    for country_key in ("US", "JP", "KR"):
        if country_counts.get(country_key, 0) < 1:
            raise AssertionError(
                f"Case report missing country {country_key}: {payload}"
            )


def _count_map(raw_items: Any, label: str) -> dict[str, int]:
    if not isinstance(raw_items, list):
        raise AssertionError(f"Case report {label} is not a list: {raw_items}")
    return {
        str(item.get("key")): int(item.get("count") or 0)
        for item in raw_items
        if isinstance(item, dict)
    }


@skeleton_case
def handle_tc_x_008(runtime: RuntimeContext, case: TestCase) -> None:
    # TC-X-008 | 费用与收入报表
    # 覆盖: FR-FE-09, FR-BL-01
    # 数据: <none>
    # 动态值: <none>
    # 前置: 存在多类型账单和回款。
    # 步骤摘要: 生成按客户、案件类型、国别、时间段的费用与收入报表。
    # 预期: 服务费、官费、未收金额汇总正确；可选仅已收/部分收口径也正确。
    # Arrange: 准备种子数据 / 鉴权 / 页面或 API 上下文。
    # Act: 按 steps_summary 执行业务流。
    # Assert: 按 expected 做 UI / API / DB / 文件断言。
    return None


@skeleton_case
def handle_tc_x_009(runtime: RuntimeContext, case: TestCase) -> None:
    # TC-X-009 | 年费统计报表
    # 覆盖: FR-FE-06
    # 数据: <none>
    # 动态值: <none>
    # 前置: 存在多年度 T_AnnuityTask、GovPayment、CaseReceipt。
    # 步骤摘要: 生成按国别/客户/年份的年费统计报表。
    # 预期: 应缴/实缴/客户实收/放弃终止等指标正确。
    # Arrange: 准备种子数据 / 鉴权 / 页面或 API 上下文。
    # Act: 按 steps_summary 执行业务流。
    # Assert: 按 expected 做 UI / API / DB / 文件断言。
    return None


@skeleton_case
def handle_tc_x_010(runtime: RuntimeContext, case: TestCase) -> None:
    # TC-X-010 | 应收/逾期/坏账报表
    # 覆盖: FR-BL-07, FR-BL-08
    # 数据: <none>
    # 动态值: <none>
    # 前置: 存在 UNSETTLED/PARTIALLY_SETTLED/BAD_DEBT 账单和催款批次。
    # 步骤摘要: 生成应收账款、逾期账款、坏账和催款效果报表。
    # 预期: 账龄区间、坏账金额、催款后 30/60/90 天回款量正确。
    # Arrange: 准备种子数据 / 鉴权 / 页面或 API 上下文。
    # Act: 按 steps_summary 执行业务流。
    # Assert: 按 expected 做 UI / API / DB / 文件断言。
    return None


@skeleton_case
def handle_tc_x_011(runtime: RuntimeContext, case: TestCase) -> None:
    # TC-X-011 | 提成报表
    # 覆盖: FR-COM-07
    # 数据: <none>
    # 动态值: <none>
    # 前置: 存在多代理人、多案件、多结算批次提成数据。
    # 步骤摘要: 生成按代理人/案件/时间区间的提成报表。
    # 预期: BaseFee、S1_Amt、S2_Amt、SettleNo、SettleDate 等字段准确可导出。
    # Arrange: 准备种子数据 / 鉴权 / 页面或 API 上下文。
    # Act: 按 steps_summary 执行业务流。
    # Assert: 按 expected 做 UI / API / DB / 文件断言。
    return None


def handle_tc_x_012(runtime: RuntimeContext, case: TestCase) -> None:
    # TC-X-012 | 任务操作日志
    # 覆盖: FR-DL-10
    # 数据: <none>
    # 动态值: <none>
    # 前置: 准备一条手工任务或官方任务。
    # 步骤摘要: 依次执行 CREATE、UPDATE、CHANGE_WORKER、CHANGE_SUPERVISOR、MARK_DONE、UNMARK_DONE、CANCEL、RESTORE。
    # 预期: T_TaskLog 记录 8 类动作，OldValue/NewValue/ActionBy/ActionAt 完整。
    del case
    try:
        runtime.api.login(runtime.username, runtime.password)
        user_id = _x_current_user_id(runtime)
        client = _ensure_x_client(runtime, "012")
        applicant = _ensure_x_applicant(runtime, "012")
        case_data = _ensure_x_task_case(
            runtime,
            client,
            applicant,
            suffix="012",
            title_label="任务操作日志案卷",
        )
        task = _ensure_x_log_task(runtime, case_data["id"], user_id)
        task_id = _required_value(task, "id", "X12 task")

        _json_or_assert(
            runtime.api.post(
                f"/tasks/{task_id}/assign",
                json={
                    "worker_id": user_id,
                    "supervisor_id": user_id,
                    "remark": "X12 assign log",
                },
            ),
            "assign X12 task",
        )
        _json_or_assert(
            runtime.api.post(
                f"/tasks/{task_id}/close",
                json={"remark": "X12 close log"},
            ),
            "close X12 task",
        )
        _json_or_assert(
            runtime.api.post(
                f"/tasks/{task_id}/reopen",
                json={"remark": "X12 reopen log"},
            ),
            "reopen X12 task",
        )
        _json_or_assert(
            runtime.api.post(
                f"/tasks/{task_id}/cancel",
                json={"remark": "X12 cancel log"},
            ),
            "cancel X12 task",
        )

        logs = _json_or_assert(
            runtime.api.get(f"/tasks/{task_id}/logs"),
            "list X12 task logs",
        )
        _assert_task_logs_include_actions(
            logs,
            {"CREATE", "ASSIGN", "CLOSE", "REOPEN", "CANCEL"},
        )

        if runtime.db.enabled():
            runtime.db.assert_row_exists("t_task_log", {"task_id": task_id})
    except requests.RequestException as exc:
        pytest.skip(f"Real backend unavailable for TC-X-012: {exc}")


def _x_current_user_id(runtime: RuntimeContext) -> str:
    payload = _json_or_assert(runtime.api.get("/auth/me"), "get current user")
    user = payload.get("user") if isinstance(payload, dict) else None
    if not isinstance(user, dict) or not user.get("id"):
        raise AssertionError(f"auth me missing user id: {payload}")
    return str(user["id"])


def _ensure_x_log_task(
    runtime: RuntimeContext,
    case_id: str,
    user_id: str,
) -> dict[str, Any]:
    title = unique_code("X12 日志任务", runtime.run_id, "001")
    existing = _find_item(
        _json_or_assert(
            runtime.api.get(
                "/tasks",
                params={
                    "case_id": case_id,
                    "status": "OPEN",
                    "page": 1,
                    "page_size": 100,
                },
            ),
            "search X12 log task",
        ),
        "title",
        title,
    )
    if existing is not None:
        return existing

    today = date.today().isoformat()
    return _json_or_assert(
        runtime.api.post(
            "/tasks",
            json={
                "case_id": case_id,
                "title": title,
                "base_date": today,
                "due_date": today,
                "internal_due_date": today,
                "worker_id": user_id,
                "supervisor_id": user_id,
                "remark": "X12 create log",
            },
        ),
        "create X12 log task",
        expected_statuses={201},
    )


def _assert_task_logs_include_actions(logs: Any, expected_actions: set[str]) -> None:
    if not isinstance(logs, list):
        raise AssertionError(f"Task logs response is not a list: {logs}")
    actions = {item.get("action") for item in logs if isinstance(item, dict)}
    missing = expected_actions - actions
    if missing:
        raise AssertionError(f"Task logs missing actions: {sorted(missing)}")


def handle_tc_x_013(runtime: RuntimeContext, case: TestCase) -> None:
    # TC-X-013 | 反冲销
    # 覆盖: FR-BL-06
    # 数据: <none>
    # 动态值: <none>
    # 前置: 存在 1 条可反冲销 Offset 和 1 条超过允许窗口的 Offset。
    # 步骤摘要: 对两条 Offset 分别执行反冲销。
    # 预期: 可反冲销记录被标记 IsReversed=true，并回滚 Bill/PaymentLine 余额；超窗口记录被阻止。
    del case
    try:
        runtime.api.login(runtime.username, runtime.password)
        client = _ensure_x_client(runtime, "013")
        bill = _create_x_offset_reverse_bill(runtime, client["id"])
        payment_line = _create_x_offset_reverse_payment_line(runtime, client["id"])
        offset = _create_x_offset_reverse_offset(
            runtime,
            payment_line_id=payment_line["id"],
            bill_id=bill["id"],
        )
        if offset.get("is_reversed") is not False:
            raise AssertionError(f"Offset should start unreversed: {offset}")

        reversed_offset = _json_or_assert(
            runtime.api.post(f"/offsets/{offset['id']}/reverse"),
            "reverse X13 offset",
        )
        _assert_equal(reversed_offset.get("id"), offset["id"], "X13 offset id")
        _assert_equal(reversed_offset.get("is_reversed"), True, "X13 offset reversed")
        _assert_x_offset_list_contains(runtime, bill["id"], offset["id"])

        bill_detail = _json_or_assert(
            runtime.api.get(f"/bills/{bill['id']}"), "get X13 restored bill"
        )
        if Decimal(str(bill_detail.get("balance"))) != Decimal("500.00"):
            raise AssertionError(f"Bill balance was not restored: {bill_detail}")
        _assert_equal(bill_detail.get("status"), "UNSETTLED", "X13 bill status")

        payment_detail = _json_or_assert(
            runtime.api.get(f"/payments/{payment_line['payment_id']}"),
            "get X13 restored payment",
        )
        _assert_x_payment_line_balance(payment_detail, payment_line["id"], "500.00")

        _json_or_assert(
            runtime.api.post(f"/offsets/{offset['id']}/reverse"),
            "reject duplicate X13 offset reverse",
            expected_statuses={400},
        )

        if runtime.db.enabled():
            runtime.db.assert_row_exists(
                "t_offset",
                {"id": offset["id"], "is_reversed": True},
            )
    except requests.RequestException as exc:
        pytest.skip(f"Real backend unavailable for TC-X-013: {exc}")


def _create_x_offset_reverse_bill(
    runtime: RuntimeContext,
    client_id: str,
) -> dict[str, Any]:
    return _json_or_assert(
        runtime.api.post(
            "/bills/manual",
            json={
                "client_id": client_id,
                "currency": "CNY",
                "direction": "AR",
                "status": "UNSETTLED",
                "bill_date": "2026-05-09",
                "due_date": "2026-06-08",
                "items": [
                    {
                        "description": f"X13 反冲销服务费 {runtime.run_id}",
                        "quantity": 1,
                        "unit_price": "500.00",
                        "fee_type": "SERVICE",
                    }
                ],
            },
        ),
        "create X13 offset reverse bill",
        expected_statuses={201},
    )


def _create_x_offset_reverse_payment_line(
    runtime: RuntimeContext,
    client_id: str,
) -> dict[str, Any]:
    payment = _json_or_assert(
        runtime.api.post(
            "/payments",
            json={
                "client_id": client_id,
                "amount": "500.00",
                "currency": "CNY",
                "pay_date": "2026-05-09",
                "remark": f"X13 offset reverse {runtime.run_id}",
            },
        ),
        "create X13 offset reverse payment",
        expected_statuses={200, 201},
    )
    detail = _json_or_assert(
        runtime.api.get(f"/payments/{payment['id']}"),
        "get X13 offset reverse payment",
    )
    lines = detail.get("payment_lines")
    if not isinstance(lines, list) or not lines:
        raise AssertionError(f"Payment line missing: {detail}")
    line = dict(lines[0])
    line["payment_id"] = payment["id"]
    return line


def _create_x_offset_reverse_offset(
    runtime: RuntimeContext,
    *,
    payment_line_id: str,
    bill_id: str,
) -> dict[str, Any]:
    return _json_or_assert(
        runtime.api.post(
            "/offsets",
            json={
                "payment_line_id": payment_line_id,
                "bill_id": bill_id,
                "offset_amt": "500.00",
                "offset_date": "2026-05-09",
            },
        ),
        "create X13 offset",
        expected_statuses={201},
    )


def _assert_x_offset_list_contains(
    runtime: RuntimeContext,
    bill_id: str,
    offset_id: str,
) -> None:
    payload = _json_or_assert(
        runtime.api.get(
            "/offsets",
            params={
                "bill_id": bill_id,
                "is_reversed": True,
                "page": 1,
                "page_size": 20,
            },
        ),
        "list X13 reversed offsets",
    )
    if not any(
        item.get("id") == offset_id for item in _items_or_assert(payload, "offsets")
    ):
        raise AssertionError(f"Reversed offset {offset_id} was not listed: {payload}")


def _assert_x_payment_line_balance(
    payload: dict[str, Any],
    payment_line_id: str,
    expected_balance: str,
) -> None:
    lines = payload.get("payment_lines")
    if not isinstance(lines, list):
        raise AssertionError(f"Payment detail missing lines: {payload}")
    for line in lines:
        if isinstance(line, dict) and line.get("id") == payment_line_id:
            if Decimal(str(line.get("balance_amt"))) != Decimal(expected_balance):
                raise AssertionError(
                    f"Payment line balance was not restored: {payload}"
                )
            return
    raise AssertionError(f"Payment line {payment_line_id} was not found: {payload}")


def handle_tc_x_014(runtime: RuntimeContext, case: TestCase) -> None:
    # TC-X-014 | 手工 AP 账单
    # 覆盖: FR-BL-03, V-BL-05, V-BL-07
    # 数据: <none>
    # 动态值: <none>
    # 前置: Finance 登录；准备外所/供应商客户。
    # 步骤摘要: 手工创建 Direction=AP 的账单并录入 1~2 条明细。
    # 预期: AP 账单保存成功，Amount=明细 LocalAmount 合计；在客户应收统计中不计入 AR。
    del case
    try:
        runtime.api.login(runtime.username, runtime.password)
        client = _ensure_x_client(runtime, "014")
        bill = _json_or_assert(
            runtime.api.post(
                "/bills/manual",
                json={
                    "client_id": client["id"],
                    "currency": "CNY",
                    "direction": "AP",
                    "status": "UNSETTLED",
                    "bill_date": "2026-05-09",
                    "due_date": "2026-06-08",
                    "items": [
                        {
                            "description": f"X14 外所代理服务费 {runtime.run_id}",
                            "quantity": 1,
                            "unit_price": "400.00",
                            "fee_type": "SERVICE",
                        },
                        {
                            "description": f"X14 外所杂费 {runtime.run_id}",
                            "quantity": 2,
                            "unit_price": "50.00",
                            "fee_type": "MISC",
                        },
                    ],
                },
            ),
            "create X14 manual AP bill",
            expected_statuses={201},
        )
        bill_id = _required_value(bill, "id", "X14 bill")
        detail = _json_or_assert(
            runtime.api.get(f"/bills/{bill_id}"), "get X14 AP bill"
        )
        _assert_manual_ap_bill_detail(detail, expected_amount=Decimal("500.00"))

        if runtime.db.enabled():
            runtime.db.assert_row_exists(
                "t_bill",
                {"id": bill_id, "direction": "AP"},
            )
    except requests.RequestException as exc:
        pytest.skip(f"Real backend unavailable for TC-X-014: {exc}")


def _assert_manual_ap_bill_detail(
    payload: dict[str, Any],
    *,
    expected_amount: Decimal,
) -> None:
    if payload.get("direction") != "AP":
        raise AssertionError(f"Expected AP bill detail: {payload}")
    if Decimal(str(payload.get("amount"))) != expected_amount:
        raise AssertionError(f"Unexpected AP bill amount: {payload}")
    if Decimal(str(payload.get("balance"))) != expected_amount:
        raise AssertionError(f"Unexpected AP bill balance: {payload}")

    items = payload.get("items")
    if not isinstance(items, list) or len(items) != 2:
        raise AssertionError(f"AP bill detail should include two items: {payload}")
    item_total = sum(Decimal(str(item.get("amount"))) for item in items)
    if item_total != expected_amount:
        raise AssertionError(f"AP bill item total mismatch: {payload}")


def handle_tc_x_015(runtime: RuntimeContext, case: TestCase) -> None:
    # TC-X-015 | 非案件账单
    # 覆盖: FR-BL-03, V-BL-06, V-BL-07
    # 数据: <none>
    # 动态值: <none>
    # 前置: Finance 登录。
    # 步骤摘要: 创建手工账单时让 BillItem.CaseID 为空并保存。
    # 预期: 账单保存成功；明细被标记为非案件账单；不进入案件维度统计或需单独分类。
    del case
    try:
        runtime.api.login(runtime.username, runtime.password)
        client = _ensure_x_client(runtime, "015")
        bill = _json_or_assert(
            runtime.api.post(
                "/bills/manual",
                json={
                    "client_id": client["id"],
                    "currency": "CNY",
                    "direction": "AR",
                    "status": "UNSETTLED",
                    "bill_date": "2026-05-09",
                    "due_date": "2026-06-08",
                    "items": [
                        {
                            "description": f"X15 非案件账单服务费 {runtime.run_id}",
                            "quantity": 2,
                            "unit_price": "150.00",
                            "fee_type": "SERVICE",
                        }
                    ],
                },
            ),
            "create X15 non-case manual bill",
            expected_statuses={201},
        )
        bill_id = _required_value(bill, "id", "X15 bill")
        detail = _json_or_assert(
            runtime.api.get(f"/bills/{bill_id}"), "get X15 non-case bill"
        )
        _assert_non_case_bill_detail(detail, expected_amount=Decimal("300.00"))

        if runtime.db.enabled():
            runtime.db.assert_row_exists(
                "t_bill_item",
                {"bill_id": bill_id, "case_id": None},
            )
    except requests.RequestException as exc:
        pytest.skip(f"Real backend unavailable for TC-X-015: {exc}")


def _assert_non_case_bill_detail(
    payload: dict[str, Any],
    *,
    expected_amount: Decimal,
) -> None:
    if payload.get("case_id") is not None:
        raise AssertionError(f"Expected non-case bill detail: {payload}")
    if Decimal(str(payload.get("amount"))) != expected_amount:
        raise AssertionError(f"Unexpected non-case bill amount: {payload}")
    if Decimal(str(payload.get("balance"))) != expected_amount:
        raise AssertionError(f"Unexpected non-case bill balance: {payload}")

    items = payload.get("items")
    if not isinstance(items, list) or not items:
        raise AssertionError(f"Non-case bill detail missing items: {payload}")
    for item in items:
        if not isinstance(item, dict):
            raise AssertionError(f"Non-case bill item is not an object: {payload}")
        if item.get("case_id") is not None:
            raise AssertionError(f"Bill item should not be linked to a case: {payload}")


@skeleton_case
def handle_tc_x_016(runtime: RuntimeContext, case: TestCase) -> None:
    # TC-X-016 | 账单打印/导出
    # 覆盖: FR-BL-04
    # 数据: <none>
    # 动态值: <none>
    # 前置: 存在已保存账单和中英模板。
    # 步骤摘要: 分别导出中文、英文和 Excel 账单。
    # 预期: 模板带出 BillNo、ClientName、费用明细和汇总金额；导出文件可下载；必要时可归档到电子文档。
    # Arrange: 准备种子数据 / 鉴权 / 页面或 API 上下文。
    # Act: 按 steps_summary 执行业务流。
    # Assert: 按 expected 做 UI / API / DB / 文件断言。
    return None


def handle_tc_x_017(runtime: RuntimeContext, case: TestCase) -> None:
    # TC-X-017 | 我的任务与监督任务视图
    # 覆盖: FR-DL-04, FR-DL-05, FR-DL-08, FR-DL-09
    # 数据: <none>
    # 动态值: <none>
    # 前置: 存在当前用户的 Worker 任务和 Supervisor 任务。
    # 步骤摘要: 进入我的任务、监督任务和首页提醒，按内限/绝限、状态、逾期、类型过滤并导出。
    # 预期: 两类视图只显示与当前用户相关任务；排序、筛选、导出和首页提醒正确。
    del case
    try:
        runtime.api.login(runtime.username, runtime.password)
        current_user = _json_or_assert(runtime.api.get("/auth/me"), "get current user")
        user_id = _required_value(current_user, "id", "current user")
        client = _ensure_x_client(runtime, "017")
        applicant = _ensure_x_applicant(runtime, "017")
        case_data = _ensure_x_task_case(runtime, client, applicant)
        task = _ensure_x_today_task(runtime, case_data["id"], user_id)
        task_id = _required_value(task, "id", "X17 task")

        _assert_task_list_hit(
            runtime,
            "worker today tasks",
            "/tasks/today",
            {"as": "worker", "page": 1, "page_size": 20},
            task_id,
        )
        _assert_task_list_hit(
            runtime,
            "supervisor today tasks",
            "/tasks/today",
            {"as": "supervisor", "page": 1, "page_size": 20},
            task_id,
        )
        _assert_output_response(
            runtime.api.get("/tasks/export", params={"as": "worker"}),
            "task export",
            "spreadsheet",
        )
        _assert_output_response(
            runtime.api.get("/tasks/print", params={"as": "supervisor"}),
            "task print",
            "text/html",
        )
        if runtime.db.enabled():
            runtime.db.assert_row_exists("t_task", {"id": task_id, "status": "OPEN"})
    except requests.RequestException as exc:
        pytest.skip(f"Real backend unavailable for TC-X-017: {exc}")


def handle_tc_x_018(runtime: RuntimeContext, case: TestCase) -> None:
    # TC-X-018 | 邮寄信息登记
    # 覆盖: FR-WD-08
    # 数据: <none>
    # 动态值: <none>
    # 前置: 存在多条 OFFICIAL_OUT/CLIENT_OUT 文档。
    # 步骤摘要: 查询待寄出文档，在第一条填写挂号号并执行“复制到全部”，再保存。
    # 预期: OutgoingRegNo 和可选 ForwardDate 批量更新成功；复制逻辑正确。
    del case
    try:
        runtime.api.login(runtime.username, runtime.password)
        client = _ensure_x_client(runtime, "018")
        applicant = _ensure_x_applicant(runtime, "018")
        case_data = _ensure_x_special_task_case(
            runtime,
            client,
            applicant,
            suffix="018",
            title_label="邮寄信息登记案卷",
        )
        document = _ensure_x_outbound_document(runtime, case_data["id"], "018")
        outgoing_reg_no = unique_code("X18-REG", runtime.run_id, "001")

        payload = _json_or_assert(
            runtime.api.post(
                "/documents/dispatch/mailing/batch-register",
                json={
                    "selected_document_ids": [document["id"]],
                    "outgoing_reg_no": outgoing_reg_no,
                    "forward_date": "2026-05-09",
                },
            ),
            "register X18 mailing batch",
        )
        _assert_mailing_batch_registered(payload, document["id"], outgoing_reg_no)

        if runtime.db.enabled():
            runtime.db.assert_row_exists(
                "t_document",
                {"id": document["id"], "outgoing_reg_no": outgoing_reg_no},
            )
    except requests.RequestException as exc:
        pytest.skip(f"Real backend unavailable for TC-X-018: {exc}")


def _ensure_x_outbound_document(
    runtime: RuntimeContext,
    case_id: str,
    suffix: str,
) -> dict[str, Any]:
    title = unique_code("X-OUT-DOC", runtime.run_id, suffix)
    existing = _find_item(
        _json_or_assert(
            runtime.api.get(
                "/documents",
                params={
                    "case_id": case_id,
                    "direction": "OUT",
                    "q": title,
                    "page": 1,
                    "page_size": 20,
                },
            ),
            f"search X{suffix} outbound document",
        ),
        "title",
        title,
    )
    if existing is not None:
        return existing
    return _json_or_assert(
        runtime.api.post(
            "/documents",
            json={
                "case_id": case_id,
                "doc_template_id": None,
                "doc_type": "CLIENT_OUT",
                "direction": "OUT",
                "doc_date": "2026-05-09",
                "title": title,
                "extra_data": f"X{suffix} outbound document",
            },
        ),
        f"create X{suffix} outbound document",
        expected_statuses={201},
    )


def _assert_mailing_batch_registered(
    payload: dict[str, Any],
    document_id: str,
    outgoing_reg_no: str,
) -> None:
    items = payload.get("items")
    if not isinstance(items, list):
        raise AssertionError(f"Mailing batch response missing items: {payload}")
    if not any(
        isinstance(item, dict)
        and item.get("document_id") == document_id
        and item.get("outgoing_reg_no") == outgoing_reg_no
        for item in items
    ):
        raise AssertionError(
            f"Mailing batch response did not include document {document_id}: {payload}"
        )


def handle_tc_x_019(runtime: RuntimeContext, case: TestCase) -> None:
    # TC-X-019 | 文件交接单
    # 覆盖: FR-WD-09
    # 数据: <none>
    # 动态值: <none>
    # 前置: 同一客户同一日期存在多份去文。
    # 步骤摘要: 选择客户+日期生成 Dispatch 单，确认明细后保存并导出 Word。
    # 预期: T_DocDispatch/T_DocDispatchLine 创建成功；导出的交接单列出所有文档与挂号号。
    del case
    try:
        runtime.api.login(runtime.username, runtime.password)
        client = _ensure_x_client(runtime, "019")
        applicant = _ensure_x_applicant(runtime, "019")
        case_data = _ensure_x_special_task_case(
            runtime,
            client,
            applicant,
            suffix="019",
            title_label="文件交接单案卷",
        )
        document = _ensure_x_outbound_document(runtime, case_data["id"], "019")

        dispatch = _json_or_assert(
            runtime.api.post(
                "/documents/dispatches",
                json={
                    "client_id": client["id"],
                    "dispatch_date": "2026-05-09",
                    "selected_document_ids": [document["id"]],
                    "remark": "X19 document dispatch",
                },
            ),
            "create X19 document dispatch",
            expected_statuses={201},
        )
        detail = _json_or_assert(
            runtime.api.get(f"/documents/dispatches/{dispatch['id']}"),
            "get X19 document dispatch",
        )
        _assert_document_dispatch_includes_document(detail, document["id"])

        if runtime.db.enabled():
            runtime.db.assert_row_exists(
                "t_doc_dispatch_line",
                {"dispatch_id": dispatch["id"], "document_id": document["id"]},
            )
    except requests.RequestException as exc:
        pytest.skip(f"Real backend unavailable for TC-X-019: {exc}")


def _assert_document_dispatch_includes_document(
    payload: dict[str, Any],
    document_id: str,
) -> None:
    lines = payload.get("lines")
    if not isinstance(lines, list):
        raise AssertionError(f"Dispatch detail missing lines: {payload}")
    if not any(
        isinstance(line, dict) and line.get("document_id") == document_id
        for line in lines
    ):
        raise AssertionError(
            f"Dispatch detail did not include document {document_id}: {payload}"
        )


def handle_tc_x_020(runtime: RuntimeContext, case: TestCase) -> None:
    # TC-X-020 | 信封打印地址优先级
    # 覆盖: FR-WD-10
    # 数据: <none>
    # 动态值: <none>
    # 前置: 分别准备 Case.DocAddressID、客户默认地址、申请人地址、无地址四类案件。
    # 步骤摘要: 输入 CaseNo/AppNo 打印信封。
    # 预期: 系统按 Case.DocAddressID→客户默认文件地址→第一申请人地址→手工指定 的优先级选地址；缺失时要求人工指定。
    del case
    try:
        runtime.api.login(runtime.username, runtime.password)

        applicant = _ensure_x_applicant(runtime, "020")

        case_doc_client = _ensure_x_client(runtime, "020DA")
        case_doc_address = _ensure_x_client_address(
            runtime,
            case_doc_client["id"],
            "020DA",
            is_default=False,
        )
        case_doc_case = _ensure_x_envelope_case(
            runtime,
            "020DA",
            case_doc_client,
            applicant,
            doc_address_id=case_doc_address["id"],
        )
        case_doc_document = _ensure_x_outbound_document(
            runtime, case_doc_case["id"], "020DA"
        )
        _assert_x_envelope_preview(
            _json_or_assert(
                runtime.api.get(
                    f"/documents/{case_doc_document['id']}/envelope-preview"
                ),
                "preview X20 case doc address envelope",
            ),
            expected_source="CASE_DOC_ADDRESS",
            expected_address_fragment=case_doc_address["address_line1"],
        )

        default_client = _ensure_x_client(runtime, "020DF")
        default_address = _ensure_x_client_address(
            runtime,
            default_client["id"],
            "020DF",
            is_default=True,
        )
        default_case = _ensure_x_envelope_case(
            runtime,
            "020DF",
            default_client,
            applicant,
        )
        default_document = _ensure_x_outbound_document(
            runtime, default_case["id"], "020DF"
        )
        _assert_x_envelope_preview(
            _json_or_assert(
                runtime.api.get(
                    f"/documents/{default_document['id']}/envelope-preview"
                ),
                "preview X20 client default address envelope",
            ),
            expected_source="CLIENT_DEFAULT_ADDRESS",
            expected_address_fragment=default_address["address_line1"],
        )

        applicant_client = _ensure_x_client(runtime, "020FA")
        applicant_case = _ensure_x_envelope_case(
            runtime,
            "020FA",
            applicant_client,
            applicant,
            applicant_address=f"X20 第一申请人地址 {runtime.run_id}",
        )
        applicant_document = _ensure_x_outbound_document(
            runtime, applicant_case["id"], "020FA"
        )
        _assert_x_envelope_preview(
            _json_or_assert(
                runtime.api.get(
                    f"/documents/{applicant_document['id']}/envelope-preview"
                ),
                "preview X20 first applicant address envelope",
            ),
            expected_source="FIRST_APPLICANT_ADDRESS",
            expected_address_fragment=f"X20 第一申请人地址 {runtime.run_id}",
        )

        manual_client = _ensure_x_client(runtime, "020MR")
        manual_case = _ensure_x_envelope_case(
            runtime,
            "020MR",
            manual_client,
            applicant,
        )
        manual_document = _ensure_x_outbound_document(
            runtime, manual_case["id"], "020MR"
        )
        _assert_x_envelope_preview(
            _json_or_assert(
                runtime.api.get(f"/documents/{manual_document['id']}/envelope-preview"),
                "preview X20 manual required envelope",
            ),
            expected_source="MANUAL_REQUIRED",
            expected_address_fragment=None,
        )
    except requests.RequestException as exc:
        pytest.skip(f"Real backend unavailable for TC-X-020: {exc}")


def _ensure_x_client_address(
    runtime: RuntimeContext,
    client_id: str,
    suffix: str,
    *,
    is_default: bool,
) -> dict[str, Any]:
    line1 = unique_code("ADDR-X", runtime.run_id, suffix)
    addresses = _json_or_assert(
        runtime.api.get(f"/clients/{client_id}/addresses"),
        "search X20 client addresses",
    )
    if not isinstance(addresses, list):
        raise AssertionError(f"Client address response is not a list: {addresses}")
    for address in addresses:
        if isinstance(address, dict) and address.get("address_line1") == line1:
            return address

    return _json_or_assert(
        runtime.api.post(
            f"/clients/{client_id}/addresses",
            json={
                "address_type": "DOC",
                "address_line1": line1,
                "city": "上海",
                "province": "上海",
                "postal_code": "200000",
                "country_code": "CN",
                "is_default": is_default,
            },
        ),
        "create X20 client address",
        expected_statuses={201},
    )


def _ensure_x_envelope_case(
    runtime: RuntimeContext,
    suffix: str,
    client: dict[str, Any],
    applicant: dict[str, Any],
    *,
    doc_address_id: str | None = None,
    applicant_address: str | None = None,
) -> dict[str, Any]:
    case_no = unique_code("CASE-X", runtime.run_id, suffix)
    existing = _find_item(
        _json_or_assert(
            runtime.api.get(
                "/cases",
                params={"case_no": case_no, "page": 1, "page_size": 20},
            ),
            "search X20 envelope case",
        ),
        "case_no",
        case_no,
    )
    if existing is not None:
        return _json_or_assert(
            runtime.api.get(f"/cases/{existing['id']}"), "get X20 envelope case"
        )

    payload: dict[str, Any] = {
        "case_no": case_no,
        "case_type": "NORMAL",
        "patent_category": "INV",
        "flow_dir": "CN_DOMESTIC",
        "status": "NOT_FILED",
        "client_id": client["id"],
        "title_cn": f"X20 信封地址优先级 {suffix} {runtime.run_id}",
        "app_no": unique_code("APP-X", runtime.run_id, suffix),
        "filing_date": "2026-05-09",
        "from_country": "CN",
        "applicants": [
            {
                "seq": 1,
                "is_first": True,
                "applicant_id": applicant["id"],
                "name_cn": applicant["name_cn"],
                "address_cn": applicant_address,
            }
        ],
    }
    if doc_address_id is not None:
        payload["doc_address_id"] = doc_address_id
    return _json_or_assert(
        runtime.api.post("/cases", json=payload),
        "create X20 envelope case",
        expected_statuses={201},
    )


def _assert_x_envelope_preview(
    payload: dict[str, Any],
    *,
    expected_source: str,
    expected_address_fragment: str | None,
) -> None:
    if payload.get("address_source") != expected_source:
        raise AssertionError(
            f"Envelope preview source expected {expected_source}: {payload}"
        )
    recipient_address = payload.get("recipient_address")
    if expected_address_fragment is None:
        if recipient_address is not None:
            raise AssertionError(f"Expected manual address requirement: {payload}")
        return
    if (
        not isinstance(recipient_address, str)
        or expected_address_fragment not in recipient_address
    ):
        raise AssertionError(f"Envelope preview missing expected address: {payload}")


@skeleton_case
def handle_tc_x_021(runtime: RuntimeContext, case: TestCase) -> None:
    # TC-X-021 | 附件查看/删除权限
    # 覆盖: FR-WD-06
    # 数据: <none>
    # 动态值: <none>
    # 前置: 存在带多附件的文档；准备 Formalities、Agent、无删除权限用户。
    # 步骤摘要: 查看附件列表并尝试下载/删除。
    # 预期: 有权用户可查看和删除；无权用户只能查看不能删除；删除后附件记录和物理文件状态一致。
    # Arrange: 准备种子数据 / 鉴权 / 页面或 API 上下文。
    # Act: 按 steps_summary 执行业务流。
    # Assert: 按 expected 做 UI / API / DB / 文件断言。
    return None


@skeleton_case
def handle_tc_x_022(runtime: RuntimeContext, case: TestCase) -> None:
    # TC-X-022 | NORMAL/PCT_NATIONAL 状态机
    # 覆盖: FR-CM-04
    # 数据: <none>
    # 动态值: <none>
    # 前置: 准备普通案子案。
    # 步骤摘要: 依次触发 NOT_FILED→WAITING_RECEIPT→SUB_EXAM/OA1→GRANTED→TERMINATED/INVALIDATED 等关键状态事件。
    # 预期: 状态迁移符合状态总表；关键字段同步更新；非法缺字段时不允许进入下一状态。
    # Arrange: 准备种子数据 / 鉴权 / 页面或 API 上下文。
    # Act: 按 steps_summary 执行业务流。
    # Assert: 按 expected 做 UI / API / DB / 文件断言。
    return None


@skeleton_case
def handle_tc_x_023(runtime: RuntimeContext, case: TestCase) -> None:
    # TC-X-023 | PCT_INTL / INVALIDATION / LITIGATION / CONSULTING 状态机
    # 覆盖: FR-CM-04, FR-CS-01
    # 数据: <none>
    # 动态值: <none>
    # 前置: 准备 PCT_INTL、INVALIDATION、LITIGATION、CONSULTING/SEARCH 四类案件。
    # 步骤摘要: 依状态总表分别触发关键事件：PCT 受理/国际公开/国家进入；无效 filed/accepted/hearing/decision；诉讼 filed/accepted/hearing/judgment；顾问 not_started/in_progress/completed/closed。
    # 预期: 每类案卷均按各自状态机迁移，且互不混淆。
    # Arrange: 准备种子数据 / 鉴权 / 页面或 API 上下文。
    # Act: 按 steps_summary 执行业务流。
    # Assert: 按 expected 做 UI / API / DB / 文件断言。
    return None


@skeleton_case
def handle_tc_x_024(runtime: RuntimeContext, case: TestCase) -> None:
    # TC-X-024 | 非法直接跳状态
    # 覆盖: FR-CM-04
    # 数据: <none>
    # 动态值: <none>
    # 前置: 准备处于早期状态的各类案件。
    # 步骤摘要: 尝试手工或接口将 NOT_FILED 直接改为 GRANTED、将 PCT_INTL 直接改为 GRANTED、将顾问案未完成直接 CLOSED。
    # 预期: 系统阻断非法跳转或要求满足前置条件；审计日志记录拒绝/异常。
    # Arrange: 准备种子数据 / 鉴权 / 页面或 API 上下文。
    # Act: 按 steps_summary 执行业务流。
    # Assert: 按 expected 做 UI / API / DB / 文件断言。
    return None


def handle_tc_x_025(runtime: RuntimeContext, case: TestCase) -> None:
    # TC-X-025 | 个案收款手工登记
    # 覆盖: FR-FE-07, V-CR-01, V-CR-02, V-CR-03
    # 数据: <none>
    # 动态值: <none>
    # 前置: 存在一个无账单或历史迁移案件。
    # 步骤摘要: 从个案收款菜单逐案登记 ReceivableAmt/ReceivedAmt/FeeCode/FeeType/ReceiptDate/InvoiceNo。
    # 预期: CaseReceipt 保存成功；Received<Receivable 时标记欠款；Received>Receivable 时识别预收并确认。
    del case
    try:
        runtime.api.login(runtime.username, runtime.password)
        client = _ensure_x_client(runtime, "025")
        applicant = _ensure_x_applicant(runtime, "025")
        case_data = _ensure_x_special_task_case(
            runtime,
            client,
            applicant,
            suffix="025",
            title_label="个案收款手工登记案卷",
        )
        case_id = _required_value(case_data, "id", "X25 case")

        arrears = _create_x_manual_case_receipt(
            runtime,
            case_id,
            "ARR",
            receivable_amt="1000.00",
            received_amt="700.00",
        )
        _assert_x_case_receipt_flag(arrears, "is_arrears")

        prepayment = _create_x_manual_case_receipt(
            runtime,
            case_id,
            "PRE",
            receivable_amt="500.00",
            received_amt="650.00",
        )
        _assert_x_case_receipt_flag(prepayment, "is_prepayment")

        summary = _json_or_assert(
            runtime.api.get(f"/cases/{case_id}/receipts"),
            "get X25 case receipt summary",
        )
        _assert_x_case_receipt_summary(summary)

        if runtime.db.enabled():
            runtime.db.assert_row_exists(
                "t_case_receipt",
                {"id": prepayment["id"], "is_prepayment": True},
            )
    except requests.RequestException as exc:
        pytest.skip(f"Real backend unavailable for TC-X-025: {exc}")


def _create_x_manual_case_receipt(
    runtime: RuntimeContext,
    case_id: str,
    suffix: str,
    *,
    receivable_amt: str,
    received_amt: str,
) -> dict[str, Any]:
    return _json_or_assert(
        runtime.api.post(
            "/case-receipts",
            json={
                "case_id": case_id,
                "fee_type": "SERVICE",
                "fee_code": unique_code("RCPT-X25", runtime.run_id, suffix),
                "fee_name": f"X25 个案收款 {suffix}",
                "currency": "CNY",
                "receivable_amt": receivable_amt,
                "received_amt": received_amt,
                "last_receipt_date": "2026-05-09",
                "due_date": "2026-06-08",
                "invoice_no": unique_code("INV-X25", runtime.run_id, suffix),
                "is_commissionable": True,
            },
        ),
        f"create X25 {suffix} case receipt",
        expected_statuses={201},
    )


def _assert_x_case_receipt_flag(payload: dict[str, Any], field: str) -> None:
    if payload.get(field) is not True:
        raise AssertionError(f"Case receipt did not set {field}: {payload}")


def _assert_x_case_receipt_summary(payload: dict[str, Any]) -> None:
    if Decimal(str(payload.get("receivable_amt"))) != Decimal("1500.00"):
        raise AssertionError(f"Unexpected receipt summary receivable: {payload}")
    if Decimal(str(payload.get("received_amt"))) != Decimal("1350.00"):
        raise AssertionError(f"Unexpected receipt summary received: {payload}")
    if payload.get("is_arrears") is not True:
        raise AssertionError(f"Receipt summary should remain arrears: {payload}")


@skeleton_case
def handle_tc_x_026(runtime: RuntimeContext, case: TestCase) -> None:
    # TC-X-026 | 费率导入导出
    # 覆盖: FR-FE-01
    # 数据: <none>
    # 动态值: <none>
    # 前置: 准备费率 Excel 或 CSV。
    # 步骤摘要: 批量导入标准费率，再导出比对。
    # 预期: 导入成功且字段映射正确；导出结果与数据库一致。
    # Arrange: 准备种子数据 / 鉴权 / 页面或 API 上下文。
    # Act: 按 steps_summary 执行业务流。
    # Assert: 按 expected 做 UI / API / DB / 文件断言。
    return None


@skeleton_case
def handle_tc_x_027(runtime: RuntimeContext, case: TestCase) -> None:
    # TC-X-027 | 手工任务日期与状态校验
    # 覆盖: FR-DL-06, V-TASK-01, V-TASK-02, V-TASK-03, V-TASK-04, V-TASK-05
    # 数据: <none>
    # 动态值: <none>
    # 前置: 任意案件；有任务维护权限的用户。
    # 步骤摘要: 手工创建/编辑任务，分别测试 Deadline<BaseDate、InnerDeadline>Deadline、Remind>Deadline、Status=DONE 但 DoneDate 为空、Status=OPEN 但 DoneDate 非空；再输入合法组合保存。
    # 预期: 非法组合均被拒绝；合法组合可保存；状态与完成日的一致性得到保证。
    # Arrange: 准备种子数据 / 鉴权 / 页面或 API 上下文。
    # Act: 按 steps_summary 执行业务流。
    # Assert: 按 expected 做 UI / API / DB / 文件断言。
    return None


HANDLERS = {
    "TC-X-001": handle_tc_x_001,
    "TC-X-002": handle_tc_x_002,
    "TC-X-003": handle_tc_x_003,
    "TC-X-004": handle_tc_x_004,
    "TC-X-005": handle_tc_x_005,
    "TC-X-006": handle_tc_x_006,
    "TC-X-007": handle_tc_x_007,
    "TC-X-008": handle_tc_x_008,
    "TC-X-009": handle_tc_x_009,
    "TC-X-010": handle_tc_x_010,
    "TC-X-011": handle_tc_x_011,
    "TC-X-012": handle_tc_x_012,
    "TC-X-013": handle_tc_x_013,
    "TC-X-014": handle_tc_x_014,
    "TC-X-015": handle_tc_x_015,
    "TC-X-016": handle_tc_x_016,
    "TC-X-017": handle_tc_x_017,
    "TC-X-018": handle_tc_x_018,
    "TC-X-019": handle_tc_x_019,
    "TC-X-020": handle_tc_x_020,
    "TC-X-021": handle_tc_x_021,
    "TC-X-022": handle_tc_x_022,
    "TC-X-023": handle_tc_x_023,
    "TC-X-024": handle_tc_x_024,
    "TC-X-025": handle_tc_x_025,
    "TC-X-026": handle_tc_x_026,
    "TC-X-027": handle_tc_x_027,
}
