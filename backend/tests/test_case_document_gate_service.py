from __future__ import annotations

from app.modules.cases.document_gate_service import (
    GateCaseContext,
    GateConclusion,
    GateDocumentInput,
    build_batch_execution_preview,
    evaluate_material_gate,
)


def _mandatory_invention_documents() -> list[GateDocumentInput]:
    return [
        GateDocumentInput(
            id="doc-request",
            title="发明专利请求书",
            doc_type="CLIENT_IN",
            direction="IN",
            template_code="APPLICATION_REQUEST",
            has_attachment=True,
        ),
        GateDocumentInput(
            id="doc-spec",
            title="说明书",
            doc_type="CLIENT_IN",
            direction="IN",
            template_code="SPECIFICATION",
            has_attachment=True,
        ),
        GateDocumentInput(
            id="doc-claims",
            title="权利要求书",
            doc_type="CLIENT_IN",
            direction="IN",
            template_code="CLAIMS",
            has_attachment=True,
        ),
        GateDocumentInput(
            id="doc-abstract",
            title="摘要",
            doc_type="CLIENT_IN",
            direction="IN",
            template_code="ABSTRACT",
            has_attachment=True,
        ),
    ]


def test_invention_gate_hard_blocks_when_mandatory_documents_are_missing() -> None:
    gate = evaluate_material_gate(
        GateCaseContext(
            case_type="NORMAL",
            patent_category="INV",
            flow_dir="CN_DOMESTIC",
            has_exam_request=False,
            no_power=True,
            has_priority=False,
        ),
        documents=[],
    )

    assert gate.conclusion == GateConclusion.BLOCKED
    assert gate.hard_block is True
    assert gate.afterfill_audit_required is False
    assert gate.material_count == 0
    assert {
        missing.requirement_code for missing in gate.missing_items if missing.blocks_submission
    } == {"APPLICATION_REQUEST", "SPECIFICATION", "CLAIMS", "ABSTRACT"}
    assert gate.suggested_actions == ["补齐硬性递交材料后再递交"]


def test_gate_warns_when_only_afterfill_material_is_missing() -> None:
    gate = evaluate_material_gate(
        GateCaseContext(
            case_type="NORMAL",
            patent_category="INV",
            flow_dir="CN_DOMESTIC",
            has_exam_request=False,
            no_power=False,
            has_priority=False,
        ),
        documents=_mandatory_invention_documents(),
    )

    assert gate.conclusion == GateConclusion.WARNING
    assert gate.hard_block is False
    assert gate.afterfill_audit_required is True
    assert gate.material_count == 4
    assert [item.requirement_code for item in gate.missing_items] == ["POWER_OF_ATTORNEY"]
    assert gate.suggested_actions == ["登记后补材料并保留审计记录"]


def test_gate_passes_when_required_and_afterfill_materials_are_matched() -> None:
    gate = evaluate_material_gate(
        GateCaseContext(
            case_type="NORMAL",
            patent_category="INV",
            flow_dir="CN_DOMESTIC",
            has_exam_request=True,
            no_power=False,
            has_priority=True,
        ),
        documents=[
            *_mandatory_invention_documents(),
            GateDocumentInput(
                id="doc-poa",
                title="委托书",
                doc_type="CLIENT_IN",
                direction="IN",
                template_code="POWER_OF_ATTORNEY",
                has_attachment=True,
            ),
            GateDocumentInput(
                id="doc-priority",
                title="优先权证明",
                doc_type="CLIENT_IN",
                direction="IN",
                template_code="PRIORITY_CERT",
                has_attachment=True,
            ),
            GateDocumentInput(
                id="doc-exam",
                title="实质审查请求书",
                doc_type="CLIENT_IN",
                direction="IN",
                template_code="EXAM_REQUEST",
                has_attachment=True,
            ),
        ],
    )

    assert gate.conclusion == GateConclusion.PASS
    assert gate.hard_block is False
    assert gate.afterfill_audit_required is False
    assert gate.material_count == 7
    assert gate.missing_items == []
    assert gate.suggested_actions == ["材料已满足当前节点要求"]


def test_execution_preview_reflects_hard_block_and_afterfill_audit() -> None:
    blocked_gate = evaluate_material_gate(
        GateCaseContext(
            case_type="NORMAL",
            patent_category="INV",
            flow_dir="CN_DOMESTIC",
            no_power=True,
        ),
        documents=[],
    )
    blocked_preview = build_batch_execution_preview(
        blocked_gate,
        apply_exam_now=True,
        generate_list=True,
    )

    assert blocked_preview[0].kind == "BLOCK_SUBMIT"
    assert blocked_preview[0].enabled is False

    warning_gate = evaluate_material_gate(
        GateCaseContext(
            case_type="NORMAL",
            patent_category="INV",
            flow_dir="CN_DOMESTIC",
            no_power=False,
        ),
        documents=_mandatory_invention_documents(),
    )
    warning_preview = build_batch_execution_preview(
        warning_gate,
        apply_exam_now=False,
        generate_list=True,
    )

    assert [item.kind for item in warning_preview] == [
        "CASE_STATUS",
        "DOCUMENT",
        "TASK",
        "AFTERFILL_AUDIT",
    ]
    assert all(item.enabled for item in warning_preview)
