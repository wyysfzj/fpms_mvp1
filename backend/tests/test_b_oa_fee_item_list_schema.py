from __future__ import annotations

import json
import uuid

from fastapi.testclient import TestClient

from tests.test_b3_fee_linking import (
    _create_case,
    _create_doc_template,
    _create_document_raw,
)


def test_oa_fee_items_without_rate_id_are_listed(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    fee_items_json = json.dumps(
        [
            {
                "fee_code": "OA_SERVICE",
                "fee_name": "OA服务费",
                "fee_type": "SERVICE",
                "amount": "800.00",
            },
            {
                "fee_code": "OA_GOV",
                "fee_name": "OA官费",
                "fee_type": "GOV",
                "amount": "120.00",
            },
        ],
        ensure_ascii=False,
    )
    template = _create_doc_template(
        client,
        auth_headers,
        code=f"OA-FEE-LIST-{uuid.uuid4().hex[:8].upper()}",
        name="OA费用清单模板",
        direction="OUT",
        fee_draft_type="OA_FEE",
        fee_item_list=fee_items_json,
    )
    case = _create_case(client, auth_headers)
    document_response = _create_document_raw(
        client,
        auth_headers,
        case["id"],
        direction="OUT",
        doc_template_id=template["id"],
        title="OA费用清单答复",
    )
    assert document_response.status_code == 201, document_response.text
    draft_id = document_response.headers.get("X-Auto-Fee-Draft-Created")
    assert draft_id is not None

    response = client.get(f"/api/v1/fees/drafts/{draft_id}/items", headers=auth_headers)
    assert response.status_code == 200, response.text
    items = sorted(response.json(), key=lambda item: item["fee_code"])

    assert [item["fee_code"] for item in items] == ["OA_GOV", "OA_SERVICE"]
    assert [item["fee_type"] for item in items] == ["GOV", "SERVICE"]
    assert [item["rate_id"] for item in items] == [None, None]
    assert {item["case_id"] for item in items} == {case["id"]}
    assert {item["draft_id"] for item in items} == {draft_id}
