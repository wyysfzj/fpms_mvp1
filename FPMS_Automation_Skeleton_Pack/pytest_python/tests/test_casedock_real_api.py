from __future__ import annotations

from uuid import uuid4

import pytest

from framework.runtime import RuntimeContext


def _json(response):
    try:
        return response.json()
    except ValueError:
        return {}


def _assert_ok(response, expected_status: int = 200) -> dict:
    assert response.status_code == expected_status, response.text
    return _json(response)


def _create_applicant(runtime: RuntimeContext, suffix: str) -> dict:
    return _assert_ok(
        runtime.api.post(
            "/applicants",
            json={
                "code": f"CDG-{suffix}",
                "name_cn": f"材料门禁申请人-{suffix}",
                "applicant_type": "ENTITY",
                "is_active": True,
            },
        ),
        201,
    )


def _create_case(runtime: RuntimeContext, suffix: str, *, no_power: bool = True) -> dict:
    applicant = _create_applicant(runtime, suffix)
    return _assert_ok(
        runtime.api.post(
            "/cases",
            json={
                "case_no": f"CDG-{suffix}",
                "case_type": "NORMAL",
                "patent_category": "INV",
                "flow_dir": "CN_DOMESTIC",
                "title_cn": f"材料门禁真实API案件-{suffix}",
                "status": "NOT_FILED",
                "no_power": no_power,
                "has_exam_request": False,
                "applicants": [
                    {
                        "seq": 1,
                        "is_first": True,
                        "applicant_id": applicant["id"],
                        "name_cn": applicant["name_cn"],
                    }
                ],
            },
        ),
        201,
    )


def _create_document(runtime: RuntimeContext, case_id: str, title: str, *, template_id: str | None = None) -> dict:
    return _assert_ok(
        runtime.api.post(
            "/documents",
            json={
                "case_id": case_id,
                "doc_template_id": template_id,
                "doc_type": "CLIENT_IN",
                "direction": "IN",
                "doc_date": "2026-05-01",
                "title": title,
            },
        ),
        201,
    )


def _get_doc_template(runtime: RuntimeContext, code: str) -> dict:
    payload = _assert_ok(
        runtime.api.get("/doc-templates", params={"q": code, "page_size": 100})
    )
    matches = [item for item in payload["items"] if item["code"] == code]
    assert matches, f"doc template {code} not found"
    return matches[0]


def _seed_complete_materials(runtime: RuntimeContext, case_id: str) -> list[dict]:
    return [
        _create_document(runtime, case_id, "发明专利请求书"),
        _create_document(runtime, case_id, "说明书"),
        _create_document(runtime, case_id, "权利要求书"),
        _create_document(runtime, case_id, "摘要"),
    ]


@pytest.mark.p0
@pytest.mark.wave_a
@pytest.mark.wave_b
def test_casedock_real_api_gates_and_batch_submit(runtime: RuntimeContext) -> None:
    runtime.api.login(runtime.username, runtime.password)
    suffix = f"{runtime.run_id}-{uuid4().hex[:8]}".upper()

    complete_case = _create_case(runtime, f"{suffix}-OK", no_power=True)
    hard_block_case = _create_case(runtime, f"{suffix}-BLOCK", no_power=True)
    source_documents = _seed_complete_materials(runtime, complete_case["id"])

    intake_preview = _assert_ok(
        runtime.api.get(
            "/cases/document-gate/intake-preview",
            params=[
                ("case_type", "NORMAL"),
                ("patent_category", "INV"),
                ("flow_dir", "CN_DOMESTIC"),
                ("no_power", "true"),
                ("has_priority", "false"),
                ("has_exam_request", "false"),
                *[("source_document_ids", document["id"]) for document in source_documents],
            ],
        )
    )
    assert intake_preview["conclusion"] == "PASS"
    assert intake_preview["material_count"] >= 4
    assert intake_preview["missing_items"] == []

    case_gate = _assert_ok(runtime.api.get(f"/cases/{complete_case['id']}/document-gate"))
    assert case_gate["conclusion"] == "PASS"
    assert len(case_gate["file_events"]) >= len(source_documents)
    assert {event["event_status"] for event in case_gate["file_events"]} >= {"REGISTERED"}

    oa_in = _get_doc_template(runtime, "OA_IN")
    impact_preview = _assert_ok(
        runtime.api.post(
            "/documents/impact-preview",
            json={
                "case_id": complete_case["id"],
                "doc_template_id": oa_in["id"],
                "doc_type": "OFFICIAL_IN",
                "direction": "IN",
                "doc_date": "2026-05-02",
                "title": "第一次审查意见通知书",
            },
        )
    )
    assert impact_preview["case_id"] == complete_case["id"]
    assert impact_preview["status_impacts"]
    assert impact_preview["deadline_impacts"]
    assert impact_preview["task_impacts"]
    assert impact_preview["confirmation_required"] is True

    candidates = _assert_ok(
        runtime.api.get(
            "/cases/batch-filing/candidates",
            params={"status": "NOT_FILED", "page": 1, "page_size": 100},
        )
    )
    by_id = {item["id"]: item for item in candidates["items"]}
    assert by_id[complete_case["id"]]["final_material_gate"]["conclusion"] == "PASS"
    assert by_id[hard_block_case["id"]]["final_material_gate"]["hard_block"] is True

    rejected = runtime.api.post(
        "/cases/batch-filing/submit",
        json={
            "selected_case_ids": [hard_block_case["id"]],
            "submitted_date": "2026-05-03",
            "apply_exam_now": False,
            "generate_list": False,
        },
    )
    assert rejected.status_code == 400, rejected.text
    payload = rejected.json()
    assert payload["error"]["code"] == "CASE_BATCH_FILING_MATERIAL_GATE_BLOCKED"
