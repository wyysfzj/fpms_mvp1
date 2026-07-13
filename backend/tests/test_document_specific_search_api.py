from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient

CASE_BASE = "/api/v1/cases"
CLIENT_BASE = "/api/v1/clients"
DOC_BASE = "/api/v1/documents"
DOC_TEMPLATE_BASE = "/api/v1/doc-templates"


def _unique(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex[:8].upper()}"


def _create_client(client: TestClient, auth_headers: dict[str, str], *, name: str) -> dict:
    resp = client.post(
        CLIENT_BASE,
        headers=auth_headers,
        json={
            "client_code": _unique("CLI"),
            "name_cn": name,
        },
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def _create_case(
    client: TestClient,
    auth_headers: dict[str, str],
    *,
    client_id: str,
    case_no: str,
) -> dict:
    resp = client.post(
        CASE_BASE,
        headers=auth_headers,
        json={
            "case_no": case_no,
            "case_type": "NORMAL",
            "patent_category": "INV",
            "flow_dir": "CN_DOMESTIC",
            "client_id": client_id,
            "title_cn": f"专项查询案件-{case_no}",
        },
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def _get_template_by_code(client: TestClient, auth_headers: dict[str, str], code: str) -> dict:
    resp = client.get(
        DOC_TEMPLATE_BASE,
        headers=auth_headers,
        params={"q": code, "page": 1, "page_size": 100},
    )
    assert resp.status_code == 200, resp.text
    items = resp.json()["items"]
    matches = [item for item in items if item["code"] == code]
    assert matches, f"template {code} not found"
    return matches[0]


def _create_document(
    client: TestClient,
    auth_headers: dict[str, str],
    *,
    case_id: str,
    template_id: str,
    doc_type: str,
    direction: str,
    doc_date: str,
    title: str,
    official_due_date: str | None = None,
) -> dict:
    deadline_fields = {}
    if official_due_date is not None:
        deadline_fields = {
            "official_due_date": official_due_date,
            "official_due_date_source": "MANUAL_OFFICIAL_NOTICE",
            "official_due_date_status": "CONFIRMED",
        }
    resp = client.post(
        DOC_BASE,
        headers=auth_headers,
        json={
            "case_id": case_id,
            "doc_template_id": template_id,
            "doc_type": doc_type,
            "direction": direction,
            "doc_date": doc_date,
            "title": title,
            **deadline_fields,
        },
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def _add_attachment(
    client: TestClient,
    auth_headers: dict[str, str],
    *,
    document_id: str,
    file_name: str,
) -> dict:
    resp = client.post(
        f"{DOC_BASE}/{document_id}/attachments",
        headers=auth_headers,
        files={"file": (file_name, b"attachment-bytes", "text/plain")},
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def test_document_specific_search_filters_by_case_no_template_code_and_doc_name(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    tag = uuid4().hex[:8]
    client_row = _create_client(client, auth_headers, name=f"中间文件客户-{tag}")
    target_case = _create_case(
        client, auth_headers, client_id=client_row["id"], case_no=f"DOCSPEC-{tag}"
    )
    other_case = _create_case(
        client, auth_headers, client_id=client_row["id"], case_no=f"OTHER-{tag}"
    )

    oa_in = _get_template_by_code(client, auth_headers, "OA_IN")
    client_in = _get_template_by_code(client, auth_headers, "CLIENT_IN")

    target_doc = _create_document(
        client,
        auth_headers,
        case_id=target_case["id"],
        template_id=oa_in["id"],
        doc_type="OFFICIAL_IN",
        direction="IN",
        doc_date="2026-02-01",
        title=f"审查意见通知书-{tag}",
        official_due_date="2026-06-30",
    )
    _create_document(
        client,
        auth_headers,
        case_id=target_case["id"],
        template_id=client_in["id"],
        doc_type="CLIENT_IN",
        direction="IN",
        doc_date="2026-02-02",
        title=f"客户来文-{tag}",
    )
    _create_document(
        client,
        auth_headers,
        case_id=other_case["id"],
        template_id=oa_in["id"],
        doc_type="OFFICIAL_IN",
        direction="IN",
        doc_date="2026-02-03",
        title=f"审查意见通知书-其他-{tag}",
        official_due_date="2026-06-30",
    )

    resp = client.get(
        DOC_BASE,
        headers=auth_headers,
        params={
            "case_no": target_case["case_no"],
            "template_code": "OA_IN",
            "doc_name": f"审查意见通知书-{tag}",
        },
    )

    assert resp.status_code == 200, resp.text
    payload = resp.json()
    assert payload["total"] == 1
    item = payload["items"][0]
    assert item["id"] == target_doc["id"]
    assert item["case_no"] == target_case["case_no"]
    assert item["template_code"] == "OA_IN"
    assert item["title"] == f"审查意见通知书-{tag}"


def test_document_specific_search_filters_need_reply_and_replied(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    tag = uuid4().hex[:8]
    client_row = _create_client(client, auth_headers, name=f"回复客户-{tag}")
    case_row = _create_case(client, auth_headers, client_id=client_row["id"], case_no=f"R-{tag}")
    oa_in = _get_template_by_code(client, auth_headers, "OA_IN")

    pending_doc = _create_document(
        client,
        auth_headers,
        case_id=case_row["id"],
        template_id=oa_in["id"],
        doc_type="OFFICIAL_IN",
        direction="IN",
        doc_date="2026-03-01",
        title=f"待回复来文-{tag}",
        official_due_date="2026-06-30",
    )
    replied_doc = _create_document(
        client,
        auth_headers,
        case_id=case_row["id"],
        template_id=oa_in["id"],
        doc_type="OFFICIAL_IN",
        direction="IN",
        doc_date="2026-03-02",
        title=f"已回复来文-{tag}",
        official_due_date="2026-06-30",
    )

    update_resp = client.put(
        f"{DOC_BASE}/{replied_doc['id']}",
        headers=auth_headers,
        json={"reply_date": "2026-03-10"},
    )
    assert update_resp.status_code == 200, update_resp.text

    resp = client.get(
        DOC_BASE,
        headers=auth_headers,
        params={
            "need_reply": True,
            "replied": False,
            "direction": "IN",
            "template_code": "OA_IN",
        },
    )

    assert resp.status_code == 200, resp.text
    payload = resp.json()
    ids = [item["id"] for item in payload["items"]]
    assert pending_doc["id"] in ids
    assert replied_doc["id"] not in ids
    for item in payload["items"]:
        assert item["need_reply"] is True
        assert item["reply_date"] is None
        assert item["template_code"] == "OA_IN"


def test_document_specific_search_filters_by_independent_doctype_multi_select(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    tag = uuid4().hex[:8]
    client_row = _create_client(client, auth_headers, name=f"文档类型客户-{tag}")
    case_row = _create_case(client, auth_headers, client_id=client_row["id"], case_no=f"DT-{tag}")
    oa_in = _get_template_by_code(client, auth_headers, "OA_IN")
    client_in = _get_template_by_code(client, auth_headers, "CLIENT_IN")

    official_in_doc = _create_document(
        client,
        auth_headers,
        case_id=case_row["id"],
        template_id=oa_in["id"],
        doc_type="OFFICIAL_IN",
        direction="IN",
        doc_date="2026-03-11",
        title=f"官方来文-{tag}",
        official_due_date="2026-06-30",
    )
    _create_document(
        client,
        auth_headers,
        case_id=case_row["id"],
        template_id=client_in["id"],
        doc_type="OFFICIAL_OUT",
        direction="OUT",
        doc_date="2026-03-12",
        title=f"官方去文-{tag}",
    )
    client_in_doc = _create_document(
        client,
        auth_headers,
        case_id=case_row["id"],
        template_id=client_in["id"],
        doc_type="CLIENT_IN",
        direction="IN",
        doc_date="2026-03-13",
        title=f"客户来文-{tag}",
    )

    resp = client.get(
        DOC_BASE,
        headers=auth_headers,
        params=[("doc_type", "OFFICIAL_IN"), ("doc_type", "CLIENT_IN")],
    )

    assert resp.status_code == 200, resp.text
    payload = resp.json()
    ids = [item["id"] for item in payload["items"]]
    assert official_in_doc["id"] in ids
    assert client_in_doc["id"] in ids
    for item in payload["items"]:
        if item["id"] in {official_in_doc["id"], client_in_doc["id"]}:
            assert item["doc_type"] in {"OFFICIAL_IN", "CLIENT_IN"}


def test_document_specific_search_filters_by_has_attachment_true(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    tag = uuid4().hex[:8]
    client_row = _create_client(client, auth_headers, name=f"附件过滤客户-{tag}")
    case_row = _create_case(client, auth_headers, client_id=client_row["id"], case_no=f"ATT-{tag}")
    oa_in = _get_template_by_code(client, auth_headers, "OA_IN")

    attached_doc = _create_document(
        client,
        auth_headers,
        case_id=case_row["id"],
        template_id=oa_in["id"],
        doc_type="OFFICIAL_IN",
        direction="IN",
        doc_date="2026-03-21",
        title=f"有附件来文-{tag}",
        official_due_date="2026-06-30",
    )
    _add_attachment(
        client,
        auth_headers,
        document_id=attached_doc["id"],
        file_name=f"attached-{tag}.txt",
    )
    _create_document(
        client,
        auth_headers,
        case_id=case_row["id"],
        template_id=oa_in["id"],
        doc_type="OFFICIAL_IN",
        direction="IN",
        doc_date="2026-03-22",
        title=f"无附件来文-{tag}",
        official_due_date="2026-06-30",
    )

    resp = client.get(
        DOC_BASE,
        headers=auth_headers,
        params={"case_no": case_row["case_no"], "has_attachment": True},
    )

    assert resp.status_code == 200, resp.text
    payload = resp.json()
    assert payload["total"] == 1
    assert [item["id"] for item in payload["items"]] == [attached_doc["id"]]


def test_document_specific_search_filters_by_has_attachment_false(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    tag = uuid4().hex[:8]
    client_row = _create_client(client, auth_headers, name=f"无附件过滤客户-{tag}")
    case_row = _create_case(client, auth_headers, client_id=client_row["id"], case_no=f"ATTN-{tag}")
    oa_in = _get_template_by_code(client, auth_headers, "OA_IN")

    attached_doc = _create_document(
        client,
        auth_headers,
        case_id=case_row["id"],
        template_id=oa_in["id"],
        doc_type="OFFICIAL_IN",
        direction="IN",
        doc_date="2026-03-23",
        title=f"有附件来文-否-{tag}",
        official_due_date="2026-06-30",
    )
    _add_attachment(
        client,
        auth_headers,
        document_id=attached_doc["id"],
        file_name=f"attached-no-{tag}.txt",
    )
    unattached_doc = _create_document(
        client,
        auth_headers,
        case_id=case_row["id"],
        template_id=oa_in["id"],
        doc_type="OFFICIAL_IN",
        direction="IN",
        doc_date="2026-03-24",
        title=f"无附件来文-否-{tag}",
        official_due_date="2026-06-30",
    )

    resp = client.get(
        DOC_BASE,
        headers=auth_headers,
        params={"case_no": case_row["case_no"], "has_attachment": False},
    )

    assert resp.status_code == 200, resp.text
    payload = resp.json()
    assert payload["total"] == 1
    assert [item["id"] for item in payload["items"]] == [unattached_doc["id"]]


def test_document_specific_search_without_has_attachment_keeps_all_matching_rows(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    tag = uuid4().hex[:8]
    client_row = _create_client(client, auth_headers, name=f"附件省略客户-{tag}")
    case_row = _create_case(client, auth_headers, client_id=client_row["id"], case_no=f"ATTO-{tag}")
    oa_in = _get_template_by_code(client, auth_headers, "OA_IN")

    attached_doc = _create_document(
        client,
        auth_headers,
        case_id=case_row["id"],
        template_id=oa_in["id"],
        doc_type="OFFICIAL_IN",
        direction="IN",
        doc_date="2026-03-25",
        title=f"有附件来文-省略-{tag}",
        official_due_date="2026-06-30",
    )
    _add_attachment(
        client,
        auth_headers,
        document_id=attached_doc["id"],
        file_name=f"attached-omit-{tag}.txt",
    )
    unattached_doc = _create_document(
        client,
        auth_headers,
        case_id=case_row["id"],
        template_id=oa_in["id"],
        doc_type="OFFICIAL_IN",
        direction="IN",
        doc_date="2026-03-26",
        title=f"无附件来文-省略-{tag}",
        official_due_date="2026-06-30",
    )

    resp = client.get(DOC_BASE, headers=auth_headers, params={"case_no": case_row["case_no"]})

    assert resp.status_code == 200, resp.text
    payload = resp.json()
    assert payload["total"] == 2
    assert {item["id"] for item in payload["items"]} == {attached_doc["id"], unattached_doc["id"]}


def test_document_create_and_update_persist_independent_doctype(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    tag = uuid4().hex[:8]
    client_row = _create_client(client, auth_headers, name=f"独立类型客户-{tag}")
    case_row = _create_case(client, auth_headers, client_id=client_row["id"], case_no=f"KEEP-{tag}")
    template = _get_template_by_code(client, auth_headers, "OA_IN")

    create_resp = client.post(
        DOC_BASE,
        headers=auth_headers,
        json={
            "case_id": case_row["id"],
            "doc_template_id": template["id"],
            "doc_type": "OFFICIAL_IN",
            "direction": "IN",
            "doc_date": "2026-03-20",
            "title": f"独立类型文件-{tag}",
            "ref_no": "REF-KEEP-001",
            "official_due_date": "2026-06-30",
            "official_due_date_source": "MANUAL_OFFICIAL_NOTICE",
            "official_due_date_status": "CONFIRMED",
        },
    )
    assert create_resp.status_code == 201, create_resp.text
    created = create_resp.json()
    assert created["doc_type"] == "OFFICIAL_IN"
    assert created["ref_no"] == "REF-KEEP-001"

    update_resp = client.put(
        f"{DOC_BASE}/{created['id']}",
        headers=auth_headers,
        json={"doc_type": "CLIENT_OUT", "ref_no": "REF-KEEP-002"},
    )
    assert update_resp.status_code == 200, update_resp.text
    updated = update_resp.json()
    assert updated["doc_type"] == "CLIENT_OUT"
    assert updated["ref_no"] == "REF-KEEP-002"
