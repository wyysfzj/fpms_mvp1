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


@skeleton_case
def handle_tc_w0_003(runtime: RuntimeContext, case: TestCase) -> None:
    # TC-W0-003 | 主数据-申请人
    # 覆盖: FR-CM-03
    # 数据: DS-AP-001, DS-AP-002, DS-U-ADM
    # 动态值: <none>
    # 前置: DS-U-ADM；准备法人申请人 DS-AP-001 和自然人 DS-AP-002。
    # 步骤摘要: 创建申请人主数据并填写名称、国籍、地址、IsLegalEntity、HasGeneralPower、IsJobInvention 等字段；保存并搜索。
    # 预期: 申请人保存成功；能按名称模糊搜索；HasGeneralPower/IsLegalEntity 在案卷引用时可被带出。
    # Arrange: 准备种子数据 / 鉴权 / 页面或 API 上下文。
    # Act: 按 steps_summary 执行业务流。
    # Assert: 按 expected 做 UI / API / DB / 文件断言。
    return None


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


@skeleton_case
def handle_tc_w0_005(runtime: RuntimeContext, case: TestCase) -> None:
    # TC-W0-005 | 主数据-国家地区
    # 覆盖: FR-CM-01, FR-FE-01, FR-CS-01
    # 数据: DS-U-ADM
    # 动态值: <none>
    # 前置: DS-U-ADM；准备 CN/US/JP/HK/EP 数据。
    # 步骤摘要: 维护国家代码、默认币种、IsDomestic、DefaultLanguage、PCT 成员标志；保存后在案卷/费率/报表处引用。
    # 预期: 国家配置可被案卷、费率、年费和报表使用；Domestic/PCT member 标志在规则分支中可识别。
    # Arrange: 准备种子数据 / 鉴权 / 页面或 API 上下文。
    # Act: 按 steps_summary 执行业务流。
    # Assert: 按 expected 做 UI / API / DB / 文件断言。
    return None


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


@skeleton_case
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
    return None


@skeleton_case
def handle_tc_w0_009(runtime: RuntimeContext, case: TestCase) -> None:
    # TC-W0-009 | 业务参数-时限模板合法配置
    # 覆盖: FR-DL-01, V-TM-01, V-TM-02, V-TM-03, V-TM-04
    # 数据: DS-U-ADM
    # 动态值: <none>
    # 前置: DS-U-ADM；准备模板代码 APPLY_FEE_LIMIT、OA_REPLY_LIMIT。
    # 步骤摘要: 创建有效模板；再分别尝试 Code 重复、AddYears/AddMonths/AddDays 全为 0、DailyRemind=true 但无 InnerOffset/Remind、DeadlineBase=CUSTOM 但调用端不传 BaseDate。
    # 预期: 有效模板可保存；重复 Code 被拒；无增量模板被拒；DailyRemind 配置不足被拒；调用端缺 BaseDate 时任务生成失败并给出明确错误。
    # Arrange: 准备种子数据 / 鉴权 / 页面或 API 上下文。
    # Act: 按 steps_summary 执行业务流。
    # Assert: 按 expected 做 UI / API / DB / 文件断言。
    return None


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


@skeleton_case
def handle_tc_w0_012(runtime: RuntimeContext, case: TestCase) -> None:
    # TC-W0-012 | 文档模板与信头
    # 覆盖: FR-WD-09, FR-WD-10, FR-BL-04
    # 数据: DS-U-ADM
    # 动态值: <none>
    # 前置: DS-U-ADM；准备中文/英文 Word 模板与 CN/EN 信头。
    # 步骤摘要: 上传 T_Template，配置 Group/Language/FilePath/Enabled；创建两套 T_LetterHead 并关联到模板。
    # 预期: 模板和信头均可保存；不同语言模板输出时能正确带出对应抬头。
    # Arrange: 准备种子数据 / 鉴权 / 页面或 API 上下文。
    # Act: 按 steps_summary 执行业务流。
    # Assert: 按 expected 做 UI / API / DB / 文件断言。
    return None


@skeleton_case
def handle_tc_w0_013(runtime: RuntimeContext, case: TestCase) -> None:
    # TC-W0-013 | 系统参数
    # 覆盖: FR-BL-09, FR-COM-04, FR-COM-05
    # 数据: DS-U-ADM
    # 动态值: <none>
    # 前置: DS-U-ADM；准备催款间隔、默认 WaitPay 阈值、退款策略等参数。
    # 步骤摘要: 维护 T_SystemParam（若实现）；分别设置催款间隔、预收款负账单策略、WaitPay 阈值、ForceSettle 默认策略。
    # 预期: 参数保存成功；相关流程读取到新值，且更新后对新交易生效。
    # Arrange: 准备种子数据 / 鉴权 / 页面或 API 上下文。
    # Act: 按 steps_summary 执行业务流。
    # Assert: 按 expected 做 UI / API / DB / 文件断言。
    return None


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
}
