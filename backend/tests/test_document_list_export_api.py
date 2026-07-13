from __future__ import annotations

import io
import zipfile
from uuid import uuid4

from fastapi.testclient import TestClient

CASE_BASE = "/api/v1/cases"
CLIENT_BASE = "/api/v1/clients"
DOC_BASE = "/api/v1/documents"


def _unique(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex[:8].upper()}"


def _create_client(client: TestClient, auth_headers: dict[str, str]) -> str:
    resp = client.post(
        CLIENT_BASE,
        headers=auth_headers,
        json={"client_code": _unique("CLI"), "name_cn": "文书导出客户"},
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


def _create_case(client: TestClient, auth_headers: dict[str, str], *, client_id: str) -> dict:
    case_no = _unique("DOCEXP")
    resp = client.post(
        CASE_BASE,
        headers=auth_headers,
        json={
            "case_no": case_no,
            "case_type": "NORMAL",
            "patent_category": "INV",
            "flow_dir": "CN_DOMESTIC",
            "client_id": client_id,
            "title_cn": f"文书导出案件-{case_no}",
        },
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def _create_document(
    client: TestClient,
    auth_headers: dict[str, str],
    *,
    case_id: str,
    title: str,
    direction: str = "IN",
) -> dict:
    resp = client.post(
        DOC_BASE,
        headers=auth_headers,
        json={
            "case_id": case_id,
            "direction": direction,
            "doc_date": "2026-07-01",
            "title": title,
            "ref_no": _unique("REF"),
        },
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def test_document_list_export_returns_filtered_xlsx(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    client_id = _create_client(client, auth_headers)
    case = _create_case(client, auth_headers, client_id=client_id)
    in_title = f"导出收文-{uuid4().hex[:6]}"
    out_title = f"导出发文-{uuid4().hex[:6]}"
    _create_document(client, auth_headers, case_id=case["id"], title=in_title, direction="IN")
    _create_document(client, auth_headers, case_id=case["id"], title=out_title, direction="OUT")

    resp = client.get(
        f"{DOC_BASE}/export",
        headers=auth_headers,
        params={"case_id": case["id"], "direction": "IN"},
    )
    assert resp.status_code == 200, resp.text
    assert (
        resp.headers["content-type"]
        == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    assert "attachment;" in resp.headers["content-disposition"]
    assert resp.content.startswith(b"PK")

    with zipfile.ZipFile(io.BytesIO(resp.content)) as archive:
        sheet_xml = archive.read("xl/worksheets/sheet1.xml").decode("utf-8")

    assert "文书清单导出" in sheet_xml
    assert in_title in sheet_xml
    assert out_title not in sheet_xml  # direction filter applied
    assert case["case_no"] in sheet_xml
    assert "收文" in sheet_xml


def test_document_list_export_requires_permission(client: TestClient) -> None:
    resp = client.get(f"{DOC_BASE}/export")
    assert resp.status_code == 401
