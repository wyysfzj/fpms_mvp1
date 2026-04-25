from __future__ import annotations

import json
from decimal import Decimal
from typing import Any

import pytest
import requests

from framework.helpers import skeleton_case
from framework.models import TestCase
from framework.runtime import RuntimeContext


def handle_tc_b_001(runtime: RuntimeContext, case: TestCase) -> None:
    # TC-B-001 | B1 OA来文登记
    # 覆盖: FR-WD-01, FR-WD-02, FR-WD-03, FR-WD-04
    # 数据: <none>
    # 动态值: CASE-B-${RUN_ID}-001
    # 前置: 现有一件 Status=SUB_EXAM 的案件 CASE-B-${RUN_ID}-001；配置 OA_NOTICE 模板。
    # 步骤摘要: 在中间文件向导 Step1 选案并选择 OFFICIAL_IN + OA_NOTICE；Step2 填写 DocName、DispatchDate、ReceiveDate、IncomingRegNo、Summary、NeedReply=true 并保存到草稿。
    # 预期: 文档草稿创建成功；默认带出 DocName/NotifyAgent/NeedReply；StatusEffect 准备将案卷置为 OA1；必要字段可编辑。
    # Arrange: 准备种子数据 / 鉴权 / 页面或 API 上下文。
    # Act: 按 steps_summary 执行业务流。
    del case
    try:
        _login(runtime)
        arranged = _arrange_b_case(runtime, "001")
        template = _ensure_doc_template(runtime, "OA_IN")
        payload = _wizard_payload(
            template_id=template["id"],
            case_id=arranged["case"]["id"],
            title=f"OA来文登记-{runtime.run_id}",
            doc_date="2026-01-15",
            ref_no=f"OA-IN-{runtime.run_id}-001",
            extra_data={
                "IncomingRegNo": f"REG-{runtime.run_id}-001",
                "Summary": "OA来文登记",
            },
        )
        created = _json_or_assert(
            runtime.api.post("/documents/wizard/batch-create", json=payload),
            "create OA incoming document through wizard",
            expected_statuses={201},
        )
        document = _single_wizard_document(created)
        _assert_document_basics(
            document,
            case_id=arranged["case"]["id"],
            template_id=template["id"],
            direction="IN",
            title=f"OA来文登记-{runtime.run_id}",
            need_reply=True,
        )
        listed = _list_documents(
            runtime, case_id=arranged["case"]["id"], template_code="OA_IN"
        )
        _assert_contains_id(listed, document["id"], "documents list")
        detail = _json_or_assert(
            runtime.api.get(f"/documents/{document['id']}"), "get document"
        )
        _assert_document_basics(
            detail,
            case_id=arranged["case"]["id"],
            template_id=template["id"],
            direction="IN",
            title=f"OA来文登记-{runtime.run_id}",
            need_reply=True,
        )
        case_detail = _json_or_assert(
            runtime.api.get(f"/cases/{arranged['case']['id']}"),
            "get case after OA incoming document",
        )
        _assert_equal(case_detail.get("status"), "OA1", "case status after OA incoming")
        if runtime.db.enabled():
            runtime.db.assert_row_exists("t_document", {"id": document["id"]})
    except requests.RequestException as exc:
        pytest.skip(f"Real backend unavailable for TC-B-001: {exc}")


def handle_tc_b_002(runtime: RuntimeContext, case: TestCase) -> None:
    # TC-B-002 | B1 官方绝限覆盖
    # 覆盖: FR-WD-04, FR-DL-02
    # 数据: <none>
    # 动态值: CASE-B-${RUN_ID}-001
    # 前置: CASE-B-${RUN_ID}-001；OA_NOTICE 模板配置 DeadlineTemplateCode=OA_REPLY_LIMIT；ExtraData 包含 OfficialDueDate。
    # 步骤摘要: 录入 OA 来文时填写 OfficialDueDate；进入 Step3 查看任务计算结果。
    # 预期: 若官方绝限存在，任务 Deadline 以 OfficialDueDate 为准；BaseDate 仍保留 DispatchDate 供内部限和提醒计算；InnerDeadline/Remind* 正确。
    # Arrange: 准备种子数据 / 鉴权 / 页面或 API 上下文。
    # Act: 按 steps_summary 执行业务流。
    del case
    try:
        _login(runtime)
        arranged = _arrange_b_case(runtime, "002")
        template = _ensure_doc_template(runtime, "OA_IN")
        official_due = "2026-03-20"
        doc_date = "2026-01-10"
        preview_payload = _wizard_payload(
            template_id=template["id"],
            case_id=arranged["case"]["id"],
            title=f"官方绝限覆盖-{runtime.run_id}",
            doc_date=doc_date,
            extra_data={"OfficialDueDate": official_due},
        )
        preview = _json_or_assert(
            runtime.api.post("/documents/wizard/task-preview", json=preview_payload),
            "preview OA task with official due date",
        )
        item = _single_item(preview, "task preview")
        _assert_equal(item.get("base_date"), doc_date, "task base_date")
        _assert_equal(item.get("due_date"), official_due, "task due_date")
        _assert_present(item.get("internal_due_date"), "internal_due_date")
        _assert_present(item.get("task_template_code"), "task_template_code")
        create_payload = dict(preview_payload)
        create_payload["task_rows"] = [
            {
                "row_index": item["row_index"],
                "case_id": arranged["case"]["id"],
                "task_template_code": item["task_template_code"],
                "title": item.get("title") or "OA答复期限",
            }
        ]
        created = _json_or_assert(
            runtime.api.post("/documents/wizard/batch-create", json=create_payload),
            "create OA incoming document with official due date",
            expected_statuses={201},
        )
        document = _single_wizard_document(created)
        tasks = _tasks_for_case(runtime, arranged["case"]["id"])
        task = _find_by(tasks, "document_id", document["id"])
        _assert_present(task, "created task")
        task_detail = _json_or_assert(
            runtime.api.get(f"/tasks/{task['id']}"), "get created task"
        )
        _assert_equal(task_detail["base_date"], doc_date, "created task base_date")
        _assert_equal(task_detail["due_date"], official_due, "created task due_date")
        _assert_equal(task_detail["status"], "OPEN", "created task status")
    except requests.RequestException as exc:
        pytest.skip(f"Real backend unavailable for TC-B-002: {exc}")


def handle_tc_b_003(runtime: RuntimeContext, case: TestCase) -> None:
    # TC-B-003 | B1 文档行校验
    # 覆盖: FR-WD-02, V-DOC-01, V-DOC-02, V-DOC-03, V-DOC-04, V-DOC-05
    # 数据: <none>
    # 动态值: CASE-B-${RUN_ID}-001
    # 前置: CASE-B-${RUN_ID}-001；OA_NOTICE 模板存在。
    # 步骤摘要: 分别测试：DocName 为空；DispatchDate 缺失或明显异常；NeedReply=true 且 Deadline 无法自动算出但为空；挂号号超长；必填 InputField 缺失。
    # 预期: 系统逐项阻止继续完成向导，并提示具体字段错误。
    # Arrange: 准备种子数据 / 鉴权 / 页面或 API 上下文。
    # Act: 按 steps_summary 执行业务流。
    del case
    try:
        _login(runtime)
        arranged = _arrange_b_case(runtime, "003")
        template = _ensure_doc_template(runtime, "OA_IN")
        invalid_official_due = _wizard_payload(
            template_id=template["id"],
            case_id=arranged["case"]["id"],
            title=f"官方绝限非法-{runtime.run_id}",
            doc_date="2026-01-15",
            extra_data={"OfficialDueDate": "not-a-date"},
        )
        _assert_business_error(
            runtime.api.post(
                "/documents/wizard/task-preview", json=invalid_official_due
            ),
            {400},
            "DOCUMENT_OFFICIAL_DUE_DATE_INVALID",
            "invalid OfficialDueDate",
        )
        missing_template = _wizard_payload(
            template_id="missing-doc-template-id",
            case_id=arranged["case"]["id"],
            title=f"模板缺失-{runtime.run_id}",
            doc_date="2026-01-15",
        )
        _assert_business_error(
            runtime.api.post("/documents/wizard/batch-create", json=missing_template),
            {404},
            "DOC_TEMPLATE_NOT_FOUND",
            "missing doc template",
        )
        missing_rows = {
            "defaults": {
                "doc_template_id": template["id"],
                "direction": "IN",
                "doc_date": "2026-01-15",
            },
            "rows": [],
        }
        _assert_business_error(
            runtime.api.post("/documents/wizard/batch-create", json=missing_rows),
            {422},
            None,
            "missing wizard rows",
        )
    except requests.RequestException as exc:
        pytest.skip(f"Real backend unavailable for TC-B-003: {exc}")


def handle_tc_b_004(runtime: RuntimeContext, case: TestCase) -> None:
    # TC-B-004 | B2 OA答复任务生成
    # 覆盖: FR-DL-02, FR-DL-03, FR-DL-10
    # 数据: <none>
    # 动态值: <none>
    # 前置: 完成 TC-B-001；存在 OA_REPLY_LIMIT 模板。
    # 步骤摘要: 完成向导 Step3 并提交；查看 T_Task、TaskLog、我的任务/监督任务视图。
    # 预期: 系统为该 OA 来文创建 OA_REPLY_LIMIT 任务；WorkerID 和 SupervisorID 按规则带出；TaskLog 记录 CREATE。
    # Arrange: 准备种子数据 / 鉴权 / 页面或 API 上下文。
    # Act: 按 steps_summary 执行业务流。
    del case
    try:
        _login(runtime)
        created = _create_oa_in_document(runtime, "004")
        tasks = _tasks_for_document(
            runtime, created["case"]["id"], created["document"]["id"]
        )
        _assert_present(tasks, "OA reply task list")
        task = tasks[0]
        _assert_equal(task["status"], "OPEN", "OA reply task status")
        _assert_present(task.get("due_date"), "OA reply task due_date")
        _assert_present(task.get("title"), "OA reply task title")
        logs = _json_or_assert(
            runtime.api.get(f"/tasks/{task['id']}/logs"), "list task logs"
        )
        actions = {log.get("action") for log in logs}
        if not ({"CREATE", "AUTO_CREATE", "AUTO_CREATE_FROM_DOCUMENT"} & actions):
            raise AssertionError(f"OA reply task missing create log action: {logs}")
        if runtime.db.enabled():
            runtime.db.assert_row_exists("t_task", {"id": task["id"], "status": "OPEN"})
    except requests.RequestException as exc:
        pytest.skip(f"Real backend unavailable for TC-B-004: {exc}")


@skeleton_case
def handle_tc_b_005(runtime: RuntimeContext, case: TestCase) -> None:
    # TC-B-005 | B3 内部准备任务
    # 覆盖: FR-CS-02, FR-DL-06
    # 数据: <none>
    # 动态值: CASE-B-${RUN_ID}-001
    # 前置: CASE-B-${RUN_ID}-001；Agent/Formalities 可手工建任务。
    # 步骤摘要: 在案卷或时限模块手工增加“内部答复准备”任务，设 BaseDate/Deadline/Worker/Supervisor；保存后修改备注和责任人。
    # 预期: 内部任务保存成功；责任人变更写 CHANGE_WORKER/CHANGE_SUPERVISOR 日志；不影响官方答复任务本身。
    # Arrange: 准备种子数据 / 鉴权 / 页面或 API 上下文。
    # Act: 按 steps_summary 执行业务流。
    # Assert: 按 expected 做 UI / API / DB / 文件断言。
    return None


def handle_tc_b_006(runtime: RuntimeContext, case: TestCase) -> None:
    # TC-B-006 | B4 OA答复去文
    # 覆盖: FR-WD-02, FR-WD-03, FR-WD-06
    # 数据: <none>
    # 动态值: <none>
    # 前置: 已有未完成 OA_NOTICE 文档和 OA_REPLY_LIMIT 任务；OA_REPLY 模板已配置 StatusRestore=SUB_EXAM。
    # 步骤摘要: 通过向导或主界面录入 OFFICIAL_OUT + OA_REPLY，填写 ReplyToID 指向对应 OA_NOTICE，上传答复附件或模板生成 docx。
    # 预期: 答复文档保存成功；ReplyToID 关联正确；附件被存档；如模板配置，案件状态准备恢复到 SUB_EXAM。
    # Arrange: 准备种子数据 / 鉴权 / 页面或 API 上下文。
    # Act: 按 steps_summary 执行业务流。
    del case
    try:
        _login(runtime)
        created = _create_oa_in_document(runtime, "006")
        reply = _create_oa_reply_document(runtime, created, "006")
        _assert_equal(reply["case_id"], created["case"]["id"], "reply case_id")
        _assert_equal(reply["reply_to_id"], created["document"]["id"], "reply_to_id")
        _assert_equal(reply["direction"], "OUT", "reply direction")
        original = _json_or_assert(
            runtime.api.get(f"/documents/{created['document']['id']}"),
            "get replied OA document",
        )
        _assert_present(original.get("reply_date"), "original OA reply_date")
    except requests.RequestException as exc:
        pytest.skip(f"Real backend unavailable for TC-B-006: {exc}")


def handle_tc_b_007(runtime: RuntimeContext, case: TestCase) -> None:
    # TC-B-007 | B4 ReplyTo 约束
    # 覆盖: FR-WD-03, FR-WD-04
    # 数据: <none>
    # 动态值: <none>
    # 前置: 存在本案 OA_NOTICE、他案 OA_NOTICE 和非可回复文档。
    # 步骤摘要: 录入 OA_REPLY 时分别将 ReplyToID 指向他案文档、非 OA_NOTICE 文档或已完成无须回复文档。
    # 预期: 系统应只允许选择同案且符合 ReplyToTemplateCode 的文档；非法 ReplyToID 被过滤或阻断。
    # Arrange: 准备种子数据 / 鉴权 / 页面或 API 上下文。
    # Act: 按 steps_summary 执行业务流。
    del case
    try:
        _login(runtime)
        base = _create_oa_in_document(runtime, "007-A")
        other_case = _arrange_b_case(runtime, "007-B")
        out_template = _ensure_oa_out_doc_template(runtime)
        mismatch_payload = {
            "case_id": other_case["case"]["id"],
            "doc_template_id": out_template["id"],
            "direction": "OUT",
            "doc_date": "2026-01-20",
            "title": f"他案答复约束-{runtime.run_id}",
            "reply_to_id": base["document"]["id"],
        }
        _assert_business_error(
            runtime.api.post("/documents", json=mismatch_payload),
            {400},
            "REPLY_TO_CASE_MISMATCH",
            "reply_to different case",
        )
        non_reply_template = _ensure_doc_template(runtime, "CLIENT_IN")
        non_reply_doc = _json_or_assert(
            runtime.api.post(
                "/documents",
                json={
                    "case_id": base["case"]["id"],
                    "doc_template_id": non_reply_template["id"],
                    "direction": "IN",
                    "doc_date": "2026-01-16",
                    "title": f"不可答复文档-{runtime.run_id}",
                },
            ),
            "create non-reply source document",
            expected_statuses={201},
        )
        _assert_business_error(
            runtime.api.post(
                "/documents",
                json={
                    "case_id": base["case"]["id"],
                    "doc_template_id": out_template["id"],
                    "direction": "OUT",
                    "doc_date": "2026-01-20",
                    "title": f"模板不匹配答复-{runtime.run_id}",
                    "reply_to_id": non_reply_doc["id"],
                },
            ),
            {400},
            "REPLY_TO_TEMPLATE_MISMATCH",
            "reply_to template mismatch",
        )
        _assert_business_error(
            runtime.api.post(
                "/documents",
                json={
                    "case_id": base["case"]["id"],
                    "doc_template_id": out_template["id"],
                    "direction": "OUT",
                    "doc_date": "2026-01-20",
                    "title": f"答复不存在文档-{runtime.run_id}",
                    "reply_to_id": "missing-document-id",
                },
            ),
            {404},
            "REPLY_TO_DOC_NOT_FOUND",
            "reply_to not found",
        )
    except requests.RequestException as exc:
        pytest.skip(f"Real backend unavailable for TC-B-007: {exc}")


def handle_tc_b_008(runtime: RuntimeContext, case: TestCase) -> None:
    # TC-B-008 | B5 自动核销任务与状态恢复
    # 覆盖: FR-DL-04, FR-DL-10, FR-CM-04
    # 数据: <none>
    # 动态值: <none>
    # 前置: TC-B-006 成功；对应 OA_REPLY_LIMIT 任务仍为 OPEN。
    # 步骤摘要: 提交 OA_REPLY 后检查任务、TaskLog 和案卷状态。
    # 预期: 系统根据 ReplyToID 找到 OA_REPLY_LIMIT 任务并标记 DONE，DoneDate=ReplyDate；写入 MARK_DONE 日志；Case.Status 从 OA1/OA2 恢复为 SUB_EXAM。
    # Arrange: 准备种子数据 / 鉴权 / 页面或 API 上下文。
    # Act: 按 steps_summary 执行业务流。
    del case
    try:
        _login(runtime)
        created = _create_oa_in_document(runtime, "008")
        open_tasks = _tasks_for_document(
            runtime, created["case"]["id"], created["document"]["id"]
        )
        _assert_present(open_tasks, "open OA reply tasks before reply")
        _create_oa_reply_document(runtime, created, "008")
        done_tasks = _tasks_for_document(
            runtime, created["case"]["id"], created["document"]["id"]
        )
        _assert_present(done_tasks, "OA reply tasks after reply")
        for task in done_tasks:
            _assert_equal(task["status"], "DONE", "auto write-off task status")
            logs = _json_or_assert(
                runtime.api.get(f"/tasks/{task['id']}/logs"), "task logs"
            )
            if "AUTO_WRITEOFF" not in {log.get("action") for log in logs}:
                raise AssertionError(
                    f"task {task['id']} missing AUTO_WRITEOFF log: {logs}"
                )
        case_detail = _json_or_assert(
            runtime.api.get(f"/cases/{created['case']['id']}"),
            "get case after OA reply",
        )
        _assert_equal(
            case_detail.get("status"), "SUB_EXAM", "case status after OA reply"
        )
    except requests.RequestException as exc:
        pytest.skip(f"Real backend unavailable for TC-B-008: {exc}")


def handle_tc_b_009(runtime: RuntimeContext, case: TestCase) -> None:
    # TC-B-009 | B6 OA费用草单
    # 覆盖: FR-WD-05, FR-FE-02, FR-FE-03
    # 数据: <none>
    # 动态值: <none>
    # 前置: OA_REPLY 模板配置 FeeDraftType=OA_FEE，存在 OA 服务费和可选官方费费率。
    # 步骤摘要: 完成向导 Step4 或从费用界面生成 OA_FEE 草单，检查 FeeItem。
    # 预期: 生成 OA_FEE 草单；SERVICE 项来自 OA 服务费；如配置 GOV 项也同步生成；Total* 汇总正确。
    # Arrange: 准备种子数据 / 鉴权 / 页面或 API 上下文。
    # Act: 按 steps_summary 执行业务流。
    del case
    try:
        _login(runtime)
        arranged = _arrange_b_case(runtime, "009")
        template = _ensure_oa_fee_doc_template(runtime)
        preview_payload = _wizard_payload(
            template_id=template["id"],
            case_id=arranged["case"]["id"],
            title=f"OA费用草单-{runtime.run_id}",
            doc_date="2026-01-18",
        )
        preview = _json_or_assert(
            runtime.api.post("/documents/wizard/fee-preview", json=preview_payload),
            "preview OA fee rows",
        )
        fee_preview = _single_item(preview, "OA fee preview")
        fee_items = fee_preview.get("fee_items") or []
        if not isinstance(fee_items, list) or not fee_items:
            raise AssertionError(f"OA fee preview missing fee_items: {preview}")
        create_payload = dict(preview_payload)
        create_payload["fee_rows"] = [
            {
                "row_index": fee_preview["row_index"],
                "case_id": arranged["case"]["id"],
                "fee_draft_type": fee_preview["fee_draft_type"],
                "fee_items": fee_items,
            }
        ]
        _json_or_assert(
            runtime.api.post("/documents/wizard/batch-create", json=create_payload),
            "create OA fee draft through wizard",
            expected_statuses={201},
        )
        drafts = _fee_drafts_for_case(runtime, arranged["case"]["id"])
        draft = _latest_matching(drafts, "amount", Decimal("420.00"))
        _assert_present(draft, "OA fee draft")
        detail = _json_or_assert(
            runtime.api.get(f"/fees/drafts/{draft['id']}"), "fee draft detail"
        )
        _assert_equal(detail["draft_type"], "OA_FEE", "fee draft type")
        _assert_decimal(detail["total_service"], Decimal("300.00"), "total_service")
        _assert_decimal(detail["total_gov"], Decimal("120.00"), "total_gov")
        _assert_decimal(detail["amount"], Decimal("420.00"), "amount")
        items = _json_or_assert(
            runtime.api.get(f"/fees/drafts/{draft['id']}/items"),
            "list OA fee items",
        )
        fee_types = {item.get("fee_type") for item in items}
        if not {"SERVICE", "GOV"}.issubset(fee_types):
            raise AssertionError(f"OA fee draft missing SERVICE/GOV items: {items}")
    except requests.RequestException as exc:
        pytest.skip(f"Real backend unavailable for TC-B-009: {exc}")


def _login(runtime: RuntimeContext) -> None:
    runtime.api.login(runtime.username, runtime.password)


def _arrange_b_case(runtime: RuntimeContext, suffix: str) -> dict[str, dict[str, Any]]:
    client = _ensure_client(runtime, suffix)
    applicant = _ensure_applicant(runtime, suffix)
    case_no = _short_code("CASE-B", runtime.run_id, suffix)
    existing = _find_item(
        _json_or_assert(
            runtime.api.get(
                "/cases", params={"page": 1, "page_size": 20, "case_no": case_no}
            ),
            "search B case",
        ),
        "case_no",
        case_no,
    )
    if existing is not None:
        case_detail = _ensure_case_status_sub_exam(runtime, existing["id"], suffix)
        return {"client": client, "applicant": applicant, "case": case_detail}

    payload = {
        "case_no": case_no,
        "case_type": "NORMAL",
        "patent_category": "INV",
        "flow_dir": "CN_DOMESTIC",
        "client_id": client["id"],
        "title_cn": f"B波OA自动化案卷-{suffix}-{runtime.run_id}",
        "recv_date": "2026-01-05",
        "applicants": [
            {
                "seq": 1,
                "is_first": True,
                "applicant_id": applicant["id"],
                "name_cn": applicant["name_cn"],
            }
        ],
    }
    case_payload = _json_or_assert(
        runtime.api.post("/cases", json=payload),
        "create B case",
        expected_statuses={201},
    )
    case_detail = _ensure_case_status_sub_exam(runtime, case_payload["id"], suffix)
    return {"client": client, "applicant": applicant, "case": case_detail}


def _ensure_case_status_sub_exam(
    runtime: RuntimeContext, case_id: str, suffix: str
) -> dict[str, Any]:
    detail = _json_or_assert(runtime.api.get(f"/cases/{case_id}"), "get B case detail")
    if detail.get("status") == "SUB_EXAM":
        return detail
    payload = {
        "status": "SUB_EXAM",
        "app_no": f"2026{_digits(runtime.run_id, suffix)}.1",
        "filing_date": "2026-01-08",
    }
    return _json_or_assert(
        runtime.api.put(f"/cases/{case_id}", json=payload),
        "move B case to SUB_EXAM",
    )


def _ensure_client(runtime: RuntimeContext, suffix: str) -> dict[str, Any]:
    code = _short_code("CL-B", runtime.run_id, suffix)
    existing = _find_item(
        _json_or_assert(
            runtime.api.get("/clients", params={"page": 1, "page_size": 20, "q": code}),
            "search client",
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
                "name_cn": f"B波客户-{suffix}-{runtime.run_id}",
                "client_type": "CLIENT",
                "default_currency": "CNY",
                "is_active": True,
            },
        ),
        "create client",
        expected_statuses={201},
    )


def _ensure_applicant(runtime: RuntimeContext, suffix: str) -> dict[str, Any]:
    code = _short_code("AP-B", runtime.run_id, suffix)
    existing = _find_item(
        _json_or_assert(
            runtime.api.get(
                "/applicants", params={"page": 1, "page_size": 20, "q": code}
            ),
            "search applicant",
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
                "name_cn": f"B波申请人-{suffix}-{runtime.run_id}",
                "applicant_type": "ENTITY",
                "is_active": True,
            },
        ),
        "create applicant",
        expected_statuses={201},
    )


def _ensure_doc_template(runtime: RuntimeContext, code: str) -> dict[str, Any]:
    existing = _template_by_code(runtime, code)
    if existing is not None:
        return existing

    fallback_payloads = {
        "OA_IN": {
            "code": "OA_IN",
            "name": "OA来文",
            "direction": "IN",
            "enabled": True,
            "status_effect": "OA1",
            "deadline_template_code": "OA_REPLY",
            "need_reply": True,
        },
        "OA_OUT": {
            "code": "OA_OUT",
            "name": "OA答复",
            "direction": "OUT",
            "enabled": True,
            "status_restore": "SUB_EXAM",
            "reply_to_template_code": "OA_IN",
        },
        "CLIENT_IN": {
            "code": "CLIENT_IN",
            "name": "客户来文",
            "direction": "IN",
            "enabled": True,
            "need_reply": False,
        },
    }
    payload = fallback_payloads.get(code)
    if payload is None:
        raise AssertionError(f"Missing required doc template: {code}")
    if code == "OA_IN":
        _ensure_task_template(runtime, "OA_REPLY")
    return _json_or_assert(
        runtime.api.post("/doc-templates", json=payload),
        f"create fallback doc template {code}",
        expected_statuses={201},
    )


def _ensure_task_template(runtime: RuntimeContext, code: str) -> dict[str, Any]:
    templates = _json_or_assert(
        runtime.api.get("/task-templates"), "list task templates"
    )
    for item in templates:
        if item.get("code") == code:
            return item
    return _json_or_assert(
        runtime.api.post(
            "/task-templates",
            json={
                "code": code,
                "name": "OA答复期限",
                "deadline_base": "DISPATCH_DATE",
                "add_days": 120,
                "inner_offset_days": 14,
                "remind_base": "DEADLINE",
                "remind_1_offset_days": 30,
                "remind_2_offset_days": 15,
                "remind_3_offset_days": 7,
                "daily_remind": False,
            },
        ),
        f"create fallback task template {code}",
        expected_statuses={201},
    )


def _ensure_oa_fee_doc_template(runtime: RuntimeContext) -> dict[str, Any]:
    code = _short_code("OA-FEE-T", runtime.run_id, "009")
    existing = _template_by_code(runtime, code)
    if existing is not None:
        return existing
    return _json_or_assert(
        runtime.api.post(
            "/doc-templates",
            json={
                "code": code,
                "name": f"OA费用模板-{runtime.run_id}",
                "direction": "IN",
                "enabled": True,
                "fee_draft_type": "OA_FEE",
                "fee_item_list": json.dumps(
                    [
                        {
                            "fee_code": "OA_SERVICE",
                            "fee_name": "OA服务费",
                            "fee_type": "SERVICE",
                            "amount": "300.00",
                        },
                        {
                            "fee_code": "OA_GOV",
                            "fee_name": "OA官方费",
                            "fee_type": "GOV",
                            "amount": "120.00",
                        },
                    ]
                ),
            },
        ),
        "create OA fee doc template",
        expected_statuses={201},
    )


def _ensure_oa_out_doc_template(runtime: RuntimeContext) -> dict[str, Any]:
    code = _short_code("OA-OUT-T", runtime.run_id, "REPLY")
    existing = _template_by_code(runtime, code)
    if existing is not None:
        return existing
    return _json_or_assert(
        runtime.api.post(
            "/doc-templates",
            json={
                "code": code,
                "name": f"OA答复模板-{runtime.run_id}",
                "direction": "OUT",
                "enabled": True,
                "status_restore": "SUB_EXAM",
                "reply_to_template_code": "OA_IN",
            },
        ),
        "create OA reply doc template",
        expected_statuses={201},
    )


def _template_by_code(runtime: RuntimeContext, code: str) -> dict[str, Any] | None:
    payload = _json_or_assert(
        runtime.api.get("/doc-templates", params={"q": code, "page_size": 100}),
        f"list doc templates for {code}",
    )
    return _find_item(payload, "code", code)


def _create_oa_in_document(runtime: RuntimeContext, suffix: str) -> dict[str, Any]:
    arranged = _arrange_b_case(runtime, suffix)
    template = _ensure_doc_template(runtime, "OA_IN")
    document = _json_or_assert(
        runtime.api.post(
            "/documents",
            json={
                "case_id": arranged["case"]["id"],
                "doc_template_id": template["id"],
                "direction": "IN",
                "doc_date": "2026-01-15",
                "title": f"OA来文-{suffix}-{runtime.run_id}",
                "ref_no": _short_code("OA-IN", runtime.run_id, suffix),
            },
        ),
        "create OA incoming document",
        expected_statuses={201},
    )
    return {"case": arranged["case"], "template": template, "document": document}


def _create_oa_reply_document(
    runtime: RuntimeContext, created: dict[str, Any], suffix: str
) -> dict[str, Any]:
    template = _ensure_oa_out_doc_template(runtime)
    return _json_or_assert(
        runtime.api.post(
            "/documents",
            json={
                "case_id": created["case"]["id"],
                "doc_template_id": template["id"],
                "direction": "OUT",
                "doc_date": "2026-01-22",
                "title": f"OA答复-{suffix}-{runtime.run_id}",
                "reply_to_id": created["document"]["id"],
            },
        ),
        "create OA reply document",
        expected_statuses={201},
    )


def _wizard_payload(
    *,
    template_id: str,
    case_id: str,
    title: str,
    doc_date: str,
    ref_no: str | None = None,
    extra_data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "defaults": {
            "doc_template_id": template_id,
            "direction": "IN",
            "doc_date": doc_date,
            "ref_no": ref_no,
            "extra_data": json.dumps(extra_data, ensure_ascii=False)
            if extra_data
            else None,
        },
        "rows": [{"case_id": case_id, "title": title}],
    }


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


def _assert_business_error(
    response: Any,
    expected_statuses: set[int],
    expected_code: str | None,
    action: str,
) -> None:
    status_code = getattr(response, "status_code", None)
    if status_code not in expected_statuses:
        raise AssertionError(
            f"{action} expected status {expected_statuses}, got {status_code}: "
            f"{_response_summary(response)}"
        )
    if expected_code is None:
        return
    payload = response.json()
    haystack = json.dumps(payload, ensure_ascii=False)
    if expected_code not in haystack:
        raise AssertionError(f"{action} missing error code {expected_code}: {payload}")


def _response_summary(response: Any) -> str:
    try:
        payload = response.json()
    except ValueError:
        payload = getattr(response, "text", "")
    return str(payload)[:500]


def _find_item(
    payload: dict[str, Any], field: str, value: Any
) -> dict[str, Any] | None:
    items = payload.get("items")
    if not isinstance(items, list):
        raise AssertionError(f"List response missing items: {payload}")
    for item in items:
        if isinstance(item, dict) and item.get(field) == value:
            return item
    return None


def _single_wizard_document(payload: dict[str, Any]) -> dict[str, Any]:
    items = payload.get("items")
    if not isinstance(items, list) or len(items) != 1:
        raise AssertionError(f"Expected one wizard document row: {payload}")
    document = items[0].get("document")
    if not isinstance(document, dict):
        raise AssertionError(f"Wizard row missing document: {payload}")
    return document


def _single_item(payload: dict[str, Any], label: str) -> dict[str, Any]:
    items = payload.get("items")
    if not isinstance(items, list) or len(items) != 1:
        raise AssertionError(f"{label} expected exactly one item: {payload}")
    item = items[0]
    if not isinstance(item, dict):
        raise AssertionError(f"{label} item is not an object: {payload}")
    return item


def _list_documents(
    runtime: RuntimeContext, *, case_id: str, template_code: str | None = None
) -> list[dict[str, Any]]:
    params: dict[str, Any] = {"case_id": case_id, "page": 1, "page_size": 100}
    if template_code:
        params["template_code"] = template_code
    payload = _json_or_assert(
        runtime.api.get("/documents", params=params), "list documents"
    )
    items = payload.get("items")
    if not isinstance(items, list):
        raise AssertionError(f"Document list missing items: {payload}")
    return items


def _tasks_for_case(runtime: RuntimeContext, case_id: str) -> list[dict[str, Any]]:
    payload = _json_or_assert(
        runtime.api.get(
            "/tasks", params={"case_id": case_id, "page": 1, "page_size": 100}
        ),
        "list tasks",
    )
    items = payload.get("items")
    if not isinstance(items, list):
        raise AssertionError(f"Task list missing items: {payload}")
    return items


def _tasks_for_document(
    runtime: RuntimeContext, case_id: str, document_id: str
) -> list[dict[str, Any]]:
    return [
        task
        for task in _tasks_for_case(runtime, case_id)
        if task.get("document_id") == document_id
    ]


def _fee_drafts_for_case(runtime: RuntimeContext, case_id: str) -> list[dict[str, Any]]:
    payload = _json_or_assert(
        runtime.api.get(
            "/fees/drafts",
            params={"case_id": case_id, "page": 1, "page_size": 100},
        ),
        "list fee drafts",
    )
    items = payload.get("items")
    if not isinstance(items, list):
        raise AssertionError(f"Fee draft list missing items: {payload}")
    return items


def _create_oa_fee_draft_flow(
    runtime: RuntimeContext, suffix: str, *, primary_agent_id: str | None = None
) -> dict[str, Any]:
    arranged = _arrange_b_case(runtime, suffix)
    if primary_agent_id:
        _json_or_assert(
            runtime.api.put(
                f"/cases/{arranged['case']['id']}",
                json={"primary_agent_id": primary_agent_id},
            ),
            "set primary agent for B case",
        )
        arranged["case"] = _json_or_assert(
            runtime.api.get(f"/cases/{arranged['case']['id']}"),
            "reload B case with primary agent",
        )
    template = _ensure_oa_fee_doc_template(runtime)
    preview_payload = _wizard_payload(
        template_id=template["id"],
        case_id=arranged["case"]["id"],
        title=f"OA费用草单-{suffix}-{runtime.run_id}",
        doc_date="2026-01-18",
    )
    preview = _json_or_assert(
        runtime.api.post("/documents/wizard/fee-preview", json=preview_payload),
        "preview OA fee rows",
    )
    fee_preview = _single_item(preview, "OA fee preview")
    fee_items = fee_preview.get("fee_items") or []
    if not isinstance(fee_items, list) or not fee_items:
        raise AssertionError(f"OA fee preview missing fee_items: {preview}")
    create_payload = dict(preview_payload)
    create_payload["fee_rows"] = [
        {
            "row_index": fee_preview["row_index"],
            "case_id": arranged["case"]["id"],
            "fee_draft_type": fee_preview["fee_draft_type"],
            "fee_items": fee_items,
        }
    ]
    _json_or_assert(
        runtime.api.post("/documents/wizard/batch-create", json=create_payload),
        "create OA fee draft through wizard",
        expected_statuses={201},
    )
    drafts = _fee_drafts_for_case(runtime, arranged["case"]["id"])
    draft = _latest_matching(drafts, "amount", Decimal("420.00"))
    detail = _json_or_assert(
        runtime.api.get(f"/fees/drafts/{draft['id']}"), "fee draft detail"
    )
    items = _json_or_assert(
        runtime.api.get(f"/fees/drafts/{draft['id']}/items"),
        "list OA fee items",
    )
    return {
        "arranged": arranged,
        "draft": detail,
        "items": items,
    }


def _split_fee_items(items: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    result: dict[str, list[dict[str, Any]]] = {}
    for item in items:
        fee_type = str(item.get("fee_type") or "").upper()
        result.setdefault(fee_type, []).append(item)
    return result


def _create_oa_bill(
    runtime: RuntimeContext, draft_id: str, suffix: str
) -> dict[str, Any]:
    bill = _json_or_assert(
        runtime.api.post(
            "/bills/from-drafts",
            json={
                "draft_ids": [draft_id],
                "bill_no": _short_code("BILL-B", runtime.run_id, suffix),
            },
        ),
        "create OA bill from draft",
        expected_statuses={201},
    )
    detail = _json_or_assert(runtime.api.get(f"/bills/{bill['id']}"), "get OA bill")
    _assert_equal(detail["direction"], "AR", "OA bill direction")
    _assert_equal(detail["status"], "UNSETTLED", "OA bill initial status")
    _assert_decimal(detail["total_service"], Decimal("300.00"), "OA bill service")
    _assert_decimal(detail["total_gov"], Decimal("120.00"), "OA bill gov")
    _assert_decimal(detail["amount"], Decimal("420.00"), "OA bill amount")
    _assert_decimal(detail["balance"], Decimal("420.00"), "OA bill balance")
    return detail


def _pay_oa_bill(
    runtime: RuntimeContext, *, client_id: str, bill_id: str, suffix: str
) -> dict[str, Any]:
    payment = _json_or_assert(
        runtime.api.post(
            "/payments",
            json={
                "client_id": client_id,
                "amount": "420.00",
                "pay_no": _short_code("PAY-B", runtime.run_id, suffix),
                "pay_date": "2026-02-20",
                "currency": "CNY",
                "remark": "OA账单收款自动化",
            },
        ),
        "create OA payment",
        expected_statuses={201},
    )
    payment_detail = _json_or_assert(
        runtime.api.get(f"/payments/{payment['id']}"), "get OA payment"
    )
    lines = payment_detail.get("payment_lines") or []
    if not lines:
        raise AssertionError(f"OA payment missing payment_lines: {payment_detail}")
    offset = _json_or_assert(
        runtime.api.post(
            "/offsets",
            json={
                "payment_line_id": lines[0]["id"],
                "bill_id": bill_id,
                "offset_amt": "420.00",
                "offset_date": "2026-02-20",
            },
        ),
        "offset OA payment",
        expected_statuses={201},
    )
    return {"payment": payment_detail, "offset": offset}


def _current_user_id(runtime: RuntimeContext) -> str:
    payload = _json_or_assert(runtime.api.get("/auth/me"), "get current user")
    user = payload.get("user") if isinstance(payload, dict) else None
    if not isinstance(user, dict) or not user.get("id"):
        raise AssertionError(f"auth me missing user id: {payload}")
    return str(user["id"])


def _ensure_oa_commission_rule(runtime: RuntimeContext) -> dict[str, Any]:
    params = {
        "page": 1,
        "page_size": 100,
        "enabled": True,
        "case_type": "NORMAL",
        "fee_type": "SERVICE",
    }
    listed = _json_or_assert(
        runtime.api.get("/commission/rules", params=params), "list commission rules"
    )
    for item in listed.get("items", []):
        if (
            item.get("fee_type") == "SERVICE"
            and item.get("case_type") == "NORMAL"
            and item.get("flow_dir") == "CN_DOMESTIC"
            and item.get("patent_category") == "INV"
            and item.get("wait_pay") is False
            and item.get("force_settle") is False
            and item.get("enabled") is True
        ):
            return item
    payload = {
        "rule_name": _short_code("B-OA-COM", runtime.run_id, "012"),
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
        "remark": "OA服务费提成自动化",
    }
    created = runtime.api.post("/commission/rules", json=payload)
    if created.status_code == 409:
        error = created.json().get("error", {})
        conflict = error.get("details", {}).get("conflict_rule_id")
        if conflict:
            return {"id": conflict}
    return _json_or_assert(
        created,
        "create OA commission rule",
        expected_statuses={201},
    )


def _latest_matching(
    items: list[dict[str, Any]], field: str, value: Decimal
) -> dict[str, Any]:
    for item in reversed(items):
        if Decimal(str(item.get(field, "0"))) == value:
            return item
    raise AssertionError(f"No item with {field}={value}: {items}")


def _find_by(
    items: list[dict[str, Any]], field: str, value: Any
) -> dict[str, Any] | None:
    for item in items:
        if item.get(field) == value:
            return item
    return None


def _assert_document_basics(
    document: dict[str, Any],
    *,
    case_id: str,
    template_id: str,
    direction: str,
    title: str,
    need_reply: bool | None = None,
) -> None:
    _assert_equal(document.get("case_id"), case_id, "document case_id")
    _assert_equal(document.get("doc_template_id"), template_id, "document template")
    _assert_equal(document.get("direction"), direction, "document direction")
    _assert_equal(document.get("title"), title, "document title")
    _assert_present(document.get("id"), "document id")
    if need_reply is not None:
        _assert_equal(document.get("need_reply"), need_reply, "document need_reply")


def _assert_contains_id(items: list[dict[str, Any]], item_id: str, label: str) -> None:
    if not any(item.get("id") == item_id for item in items):
        raise AssertionError(f"{label} does not contain id {item_id}: {items}")


def _assert_present(value: Any, label: str) -> None:
    if value in (None, "", []):
        raise AssertionError(f"{label} is missing")


def _assert_equal(actual: Any, expected: Any, label: str) -> None:
    if actual != expected:
        raise AssertionError(f"{label} expected {expected!r}, got {actual!r}")


def _assert_decimal(actual: Any, expected: Decimal, label: str) -> None:
    normalized = Decimal(str(actual))
    if normalized != expected:
        raise AssertionError(f"{label} expected {expected}, got {actual}")


def _short_code(prefix: str, run_id: str, suffix: str) -> str:
    return f"{prefix}-{_slug(run_id)}-{_slug(suffix)}"[:64].rstrip("-")


def _slug(value: str) -> str:
    cleaned = "".join(ch for ch in str(value).upper() if ch.isalnum())
    return cleaned[-18:] or "X"


def _digits(run_id: str, suffix: str) -> str:
    raw = f"{run_id}{suffix}"
    digits = "".join(ch for ch in raw if ch.isdigit())
    return (digits or "000000000000")[-12:]


def handle_tc_b_010(runtime: RuntimeContext, case: TestCase) -> None:
    # TC-B-010 | B7 OA官方费清单
    # 覆盖: FR-FE-04
    # 数据: <none>
    # 动态值: <none>
    # 前置: 存在 OA_FEE 草单且含 GOV 项。
    # 步骤摘要: 生成 PayList(Type=INTERMEDIATE/OA) 并登记 GovPayment。
    # 预期: 仅 GOV 项进入官费清单；PaidDate/PaidAmt 可查询；不影响 SERVICE 项账单逻辑。
    # Arrange: 准备种子数据 / 鉴权 / 页面或 API 上下文。
    # Act: 按 steps_summary 执行业务流。
    del case
    try:
        _login(runtime)
        flow = _create_oa_fee_draft_flow(runtime, "010")
        fee_items = _split_fee_items(flow["items"])
        gov_items = fee_items.get("GOV") or []
        service_items = fee_items.get("SERVICE") or []
        _assert_present(gov_items, "OA GOV fee items")
        _assert_present(service_items, "OA SERVICE fee items")
        pay_list_result = _json_or_assert(
            runtime.api.post(
                "/pay-lists/from-fee-items",
                json={
                    "fee_item_ids": [item["id"] for item in gov_items],
                    "planned_pay_date": "2026-02-10",
                    "remark": "OA官方费清单自动化",
                },
            ),
            "create OA official pay list",
        )
        pay_list = pay_list_result.get("pay_list")
        if not isinstance(pay_list, dict):
            raise AssertionError(
                f"pay list response missing pay_list: {pay_list_result}"
            )
        _assert_decimal(pay_list["total_amount"], Decimal("120.00"), "pay list total")
        accepted_rows = pay_list_result.get("success") or []
        if len(accepted_rows) != len(gov_items):
            raise AssertionError(
                f"pay list should include only GOV items: {pay_list_result}"
            )
        for item in service_items:
            if any(row.get("fee_item_id") == item["id"] for row in accepted_rows):
                raise AssertionError(f"SERVICE item entered official pay list: {item}")
        for item in gov_items:
            _json_or_assert(
                runtime.api.post(
                    "/gov-payments",
                    json={
                        "pay_list_id": pay_list["id"],
                        "fee_item_id": item["id"],
                        "paid_date": "2026-02-12",
                        "official_receipt_no": _short_code(
                            "GOV-B", runtime.run_id, "010"
                        ),
                    },
                ),
                "register OA official payment",
            )
        detail = _json_or_assert(
            runtime.api.get(f"/pay-lists/{pay_list['id']}"), "get OA pay list"
        )
        _assert_equal(detail["pay_list"]["status"], "PAID", "pay list status")
        _assert_decimal(
            detail["pay_list"]["total_amount"], Decimal("120.00"), "paid pay list total"
        )
        paid_rows = detail.get("gov_payments") or []
        _assert_present(paid_rows, "paid official payment rows")
        for row in paid_rows:
            _assert_equal(row.get("status"), "PAID", "official payment status")
            _assert_decimal(row.get("paid_amount"), Decimal("120.00"), "paid amount")
    except requests.RequestException as exc:
        pytest.skip(f"Real backend unavailable for TC-B-010: {exc}")


def handle_tc_b_011(runtime: RuntimeContext, case: TestCase) -> None:
    # TC-B-011 | B8 OA账单与收款
    # 覆盖: FR-BL-02, FR-BL-05, FR-FE-07
    # 数据: <none>
    # 动态值: <none>
    # 前置: 存在 OA_FEE 草单；Finance 登录。
    # 步骤摘要: 从草单生成 OA 应收账单；登记客户付款并冲销；检查 CaseReceipt。
    # 预期: 账单生成成功；付款后 Balance 正确减少；CaseReceipt 记录本次 OA 服务费/官费收款；费用情况查询能看到。
    # Arrange: 准备种子数据 / 鉴权 / 页面或 API 上下文。
    # Act: 按 steps_summary 执行业务流。
    del case
    try:
        _login(runtime)
        flow = _create_oa_fee_draft_flow(runtime, "011")
        bill = _create_oa_bill(runtime, flow["draft"]["id"], "011")
        _pay_oa_bill(
            runtime,
            client_id=flow["arranged"]["client"]["id"],
            bill_id=bill["id"],
            suffix="011",
        )
        settled = _json_or_assert(
            runtime.api.get(f"/bills/{bill['id']}"), "get settled bill"
        )
        _assert_equal(settled["status"], "SETTLED", "OA bill paid status")
        _assert_decimal(settled["balance"], Decimal("0.00"), "OA bill paid balance")
        receipts = _json_or_assert(
            runtime.api.get(f"/cases/{flow['arranged']['case']['id']}/receipts"),
            "get OA case receipts",
        )
        _assert_decimal(receipts["receivable_amt"], Decimal("420.00"), "receivable")
        _assert_decimal(receipts["received_amt"], Decimal("420.00"), "received")
        _assert_equal(receipts["is_arrears"], False, "receipt arrears status")
    except requests.RequestException as exc:
        pytest.skip(f"Real backend unavailable for TC-B-011: {exc}")


def handle_tc_b_012(runtime: RuntimeContext, case: TestCase) -> None:
    # TC-B-012 | B9 OA服务费计入提成
    # 覆盖: FR-COM-02, FR-COM-03, FR-COM-04
    # 数据: <none>
    # 动态值: <none>
    # 前置: 同案已经存在 A 场景申请费提成；本次 OA 账单含 SERVICE 项。
    # 步骤摘要: 触发提成计算，查看 Commission 是累加 BaseFee 还是新增阶段记录（按规则实现）。
    # 预期: OA 服务费进入 Commission 管道；BaseFee/S1/S2 被新增或累加且可追溯阶段来源 Remark=OA 阶段；多代理人分摊正确。
    # Arrange: 准备种子数据 / 鉴权 / 页面或 API 上下文。
    # Act: 按 steps_summary 执行业务流。
    del case
    try:
        _login(runtime)
        agent_id = _current_user_id(runtime)
        _ensure_oa_commission_rule(runtime)
        flow = _create_oa_fee_draft_flow(runtime, "012", primary_agent_id=agent_id)
        bill = _create_oa_bill(runtime, flow["draft"]["id"], "012")
        _pay_oa_bill(
            runtime,
            client_id=flow["arranged"]["client"]["id"],
            bill_id=bill["id"],
            suffix="012",
        )
        commissions = _json_or_assert(
            runtime.api.get(
                "/commission",
                params={
                    "case_id": flow["arranged"]["case"]["id"],
                    "page": 1,
                    "page_size": 100,
                },
            ),
            "list OA commissions",
        )
        rows = commissions.get("items") or []
        service_rows = [row for row in rows if row.get("fee_type") == "SERVICE"]
        _assert_present(service_rows, "OA service commission rows")
        if not any(
            Decimal(str(row.get("base_fee", "0"))) >= Decimal("300.00")
            for row in service_rows
        ):
            raise AssertionError(
                f"OA service fee not included in commission base: {rows}"
            )
        if not any(row.get("agent_id") == agent_id for row in service_rows):
            raise AssertionError(
                f"OA commission missing primary agent {agent_id}: {rows}"
            )
        for row in service_rows:
            _assert_present(row.get("s1_amount"), "commission s1 amount")
            _assert_present(row.get("s2_amount"), "commission s2 amount")
    except requests.RequestException as exc:
        pytest.skip(f"Real backend unavailable for TC-B-012: {exc}")


def handle_tc_b_013(runtime: RuntimeContext, case: TestCase) -> None:
    # TC-B-013 | 主界面修改 NeedReply/Deadline
    # 覆盖: FR-WD-04, FR-DL-06
    # 数据: <none>
    # 动态值: <none>
    # 前置: 已存在一条 NeedReply=true 且已有 T_Task 的 OA 来文。
    # 步骤摘要: 在文档主界面将 NeedReply 改为 false 或修改 Deadline；保存时选择“更新任务”或“取消任务”（如实现该交互）。
    # 预期: 若改为 false，系统同步取消或关闭对应任务并记录日志；若只修改 Deadline，任务日期同步更新且保留审计痕迹。
    # Arrange: 准备种子数据 / 鉴权 / 页面或 API 上下文。
    # Act: 按 steps_summary 执行业务流。
    del case
    try:
        _login(runtime)
        ambiguous = _create_oa_in_document(runtime, "013A")
        _assert_business_error(
            runtime.api.put(
                f"/documents/{ambiguous['document']['id']}",
                json={"need_reply": False},
            ),
            {400},
            "DOCUMENT_REPLY_TASK_ACTION_REQUIRED",
            "ambiguous NeedReply update",
        )

        update_target = _create_oa_in_document(runtime, "013U")
        update_tasks = _tasks_for_document(
            runtime, update_target["case"]["id"], update_target["document"]["id"]
        )
        _assert_present(update_tasks, "reply task before deadline update")
        task_id = update_tasks[0]["id"]
        _json_or_assert(
            runtime.api.put(
                f"/documents/{update_target['document']['id']}",
                json={
                    "reply_task_action": "UPDATE",
                    "reply_task_due_date": "2026-05-20",
                    "reply_task_internal_due_date": "2026-05-06",
                    "reply_task_remind_1_date": "2026-04-20",
                    "reply_task_remind_2_date": "2026-05-05",
                    "reply_task_remind_3_date": "2026-05-13",
                },
            ),
            "update NeedReply task deadline",
        )
        updated_task = _json_or_assert(
            runtime.api.get(f"/tasks/{task_id}"), "get updated reply task"
        )
        _assert_equal(updated_task["due_date"], "2026-05-20", "updated due date")
        _assert_equal(
            updated_task["internal_due_date"],
            "2026-05-06",
            "updated internal due date",
        )
        logs = _json_or_assert(runtime.api.get(f"/tasks/{task_id}/logs"), "task logs")
        if "UPDATE" not in {log.get("action") for log in logs}:
            raise AssertionError(f"updated reply task missing UPDATE log: {logs}")

        cancel_target = _create_oa_in_document(runtime, "013C")
        cancel_tasks = _tasks_for_document(
            runtime, cancel_target["case"]["id"], cancel_target["document"]["id"]
        )
        _assert_present(cancel_tasks, "reply task before cancel")
        cancel_task_id = cancel_tasks[0]["id"]
        doc = _json_or_assert(
            runtime.api.put(
                f"/documents/{cancel_target['document']['id']}",
                json={"need_reply": False, "reply_task_action": "CANCEL"},
            ),
            "cancel NeedReply task",
        )
        _assert_equal(doc["need_reply"], False, "document need_reply after cancel")
        cancelled_task = _json_or_assert(
            runtime.api.get(f"/tasks/{cancel_task_id}"), "get cancelled reply task"
        )
        _assert_equal(cancelled_task["status"], "CANCELLED", "cancelled task status")
        cancel_logs = _json_or_assert(
            runtime.api.get(f"/tasks/{cancel_task_id}/logs"), "cancel task logs"
        )
        if "CANCEL" not in {log.get("action") for log in cancel_logs}:
            raise AssertionError(
                f"cancelled reply task missing CANCEL log: {cancel_logs}"
            )
    except requests.RequestException as exc:
        pytest.skip(f"Real backend unavailable for TC-B-013: {exc}")


HANDLERS = {
    "TC-B-001": handle_tc_b_001,
    "TC-B-002": handle_tc_b_002,
    "TC-B-003": handle_tc_b_003,
    "TC-B-004": handle_tc_b_004,
    "TC-B-005": handle_tc_b_005,
    "TC-B-006": handle_tc_b_006,
    "TC-B-007": handle_tc_b_007,
    "TC-B-008": handle_tc_b_008,
    "TC-B-009": handle_tc_b_009,
    "TC-B-010": handle_tc_b_010,
    "TC-B-011": handle_tc_b_011,
    "TC-B-012": handle_tc_b_012,
    "TC-B-013": handle_tc_b_013,
}
