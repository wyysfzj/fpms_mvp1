from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class GateConclusion(str, Enum):
    PASS = "PASS"
    WARNING = "WARNING"
    BLOCKED = "BLOCKED"


@dataclass(frozen=True)
class GateCaseContext:
    case_type: str
    patent_category: str
    flow_dir: str
    has_exam_request: bool | None = None
    no_power: bool | None = None
    has_priority: bool | None = None


@dataclass(frozen=True)
class GateDocumentInput:
    id: str
    title: str | None = None
    doc_type: str | None = None
    direction: str | None = None
    template_code: str | None = None
    role_code: str | None = None
    has_attachment: bool = True
    extra_data: str | None = None


@dataclass(frozen=True)
class MaterialRequirement:
    code: str
    name: str
    role: str
    blocks_submission: bool
    afterfill_allowed: bool
    template_codes: tuple[str, ...] = ()
    title_tokens: tuple[str, ...] = ()
    doc_types: tuple[str, ...] = ()


@dataclass(frozen=True)
class MatchedDocument:
    id: str
    title: str | None
    doc_type: str | None
    template_code: str | None


@dataclass(frozen=True)
class MaterialCheckItem:
    requirement_code: str
    requirement_name: str
    role: str
    blocks_submission: bool
    afterfill_allowed: bool
    matched_documents: list[MatchedDocument] = field(default_factory=list)


@dataclass(frozen=True)
class MissingMaterialItem:
    requirement_code: str
    requirement_name: str
    role: str
    blocks_submission: bool
    afterfill_allowed: bool


@dataclass(frozen=True)
class MaterialGateResult:
    requirements: list[MaterialRequirement]
    checks: list[MaterialCheckItem]
    missing_items: list[MissingMaterialItem]
    material_count: int
    conclusion: GateConclusion
    hard_block: bool
    afterfill_audit_required: bool
    suggested_actions: list[str]


@dataclass(frozen=True)
class ExecutionPreviewItem:
    kind: str
    label: str
    enabled: bool
    detail: str | None = None


def derive_material_requirements(context: GateCaseContext) -> list[MaterialRequirement]:
    case_type = _norm_code(context.case_type)
    patent_category = _norm_code(context.patent_category)
    if case_type in {"CONSULTING", "SEARCH"}:
        return [
            MaterialRequirement(
                code="CLIENT_INSTRUCTION",
                name="客户指示文件",
                role="收案依据",
                blocks_submission=True,
                afterfill_allowed=False,
                template_codes=("CLIENT_INSTRUCTION",),
                title_tokens=("客户指示", "委托事项"),
                doc_types=("CLIENT_IN",),
            )
        ]

    requirements = [
        MaterialRequirement(
            code="APPLICATION_REQUEST",
            name="申请请求书",
            role="递交主文件",
            blocks_submission=True,
            afterfill_allowed=False,
            template_codes=("APPLICATION_REQUEST", "REQUEST"),
            title_tokens=("请求书", "申请书"),
            doc_types=("CLIENT_IN",),
        )
    ]

    if patent_category in {"INV", "UM"}:
        requirements.extend(
            [
                MaterialRequirement(
                    code="SPECIFICATION",
                    name="说明书",
                    role="技术文件",
                    blocks_submission=True,
                    afterfill_allowed=False,
                    template_codes=("SPECIFICATION", "SPEC"),
                    title_tokens=("说明书",),
                    doc_types=("CLIENT_IN",),
                ),
                MaterialRequirement(
                    code="CLAIMS",
                    name="权利要求书",
                    role="保护范围文件",
                    blocks_submission=True,
                    afterfill_allowed=False,
                    template_codes=("CLAIMS",),
                    title_tokens=("权利要求",),
                    doc_types=("CLIENT_IN",),
                ),
                MaterialRequirement(
                    code="ABSTRACT",
                    name="摘要",
                    role="公开文件",
                    blocks_submission=True,
                    afterfill_allowed=False,
                    template_codes=("ABSTRACT",),
                    title_tokens=("摘要",),
                    doc_types=("CLIENT_IN",),
                ),
            ]
        )
    elif patent_category == "DES":
        requirements.append(
            MaterialRequirement(
                code="DESIGN_PICTURES",
                name="外观设计图片或照片",
                role="外观设计文件",
                blocks_submission=True,
                afterfill_allowed=False,
                template_codes=("DESIGN_PICTURES", "DESIGN_PHOTOS"),
                title_tokens=("外观设计", "图片", "照片"),
                doc_types=("CLIENT_IN",),
            )
        )

    if not context.no_power:
        requirements.append(
            MaterialRequirement(
                code="POWER_OF_ATTORNEY",
                name="委托书",
                role="授权文件",
                blocks_submission=False,
                afterfill_allowed=True,
                template_codes=("POWER_OF_ATTORNEY", "POA"),
                title_tokens=("委托书", "授权委托"),
                doc_types=("CLIENT_IN",),
            )
        )

    if context.has_priority:
        requirements.append(
            MaterialRequirement(
                code="PRIORITY",
                name="优先权证明",
                role="优先权文件",
                blocks_submission=False,
                afterfill_allowed=True,
                template_codes=("PRIORITY", "PRIORITY_CERT"),
                title_tokens=("优先权",),
                doc_types=("CLIENT_IN",),
            )
        )

    if context.has_exam_request and patent_category == "INV":
        requirements.append(
            MaterialRequirement(
                code="EXAM_REQUEST",
                name="实质审查请求书",
                role="实审文件",
                blocks_submission=False,
                afterfill_allowed=True,
                template_codes=("EXAM_REQUEST",),
                title_tokens=("实质审查", "实审"),
                doc_types=("CLIENT_IN",),
            )
        )

    return requirements


def evaluate_material_gate(
    context: GateCaseContext,
    *,
    documents: list[GateDocumentInput],
) -> MaterialGateResult:
    requirements = derive_material_requirements(context)
    checks: list[MaterialCheckItem] = []
    missing_items: list[MissingMaterialItem] = []
    matched_document_ids: set[str] = set()

    for requirement in requirements:
        matched = [
            MatchedDocument(
                id=document.id,
                title=document.title,
                doc_type=document.doc_type,
                template_code=document.template_code,
            )
            for document in documents
            if _matches_requirement(requirement, document)
        ]
        matched_document_ids.update(document.id for document in matched)
        checks.append(
            MaterialCheckItem(
                requirement_code=requirement.code,
                requirement_name=requirement.name,
                role=requirement.role,
                blocks_submission=requirement.blocks_submission,
                afterfill_allowed=requirement.afterfill_allowed,
                matched_documents=matched,
            )
        )
        if not matched:
            missing_items.append(
                MissingMaterialItem(
                    requirement_code=requirement.code,
                    requirement_name=requirement.name,
                    role=requirement.role,
                    blocks_submission=requirement.blocks_submission,
                    afterfill_allowed=requirement.afterfill_allowed,
                )
            )

    hard_block = any(item.blocks_submission for item in missing_items)
    afterfill_audit_required = bool(missing_items) and not hard_block
    if hard_block:
        conclusion = GateConclusion.BLOCKED
        suggested_actions = ["补齐硬性递交材料后再递交"]
    elif afterfill_audit_required:
        conclusion = GateConclusion.WARNING
        suggested_actions = ["登记后补材料并保留审计记录"]
    else:
        conclusion = GateConclusion.PASS
        suggested_actions = ["材料已满足当前节点要求"]

    return MaterialGateResult(
        requirements=requirements,
        checks=checks,
        missing_items=missing_items,
        material_count=len(matched_document_ids),
        conclusion=conclusion,
        hard_block=hard_block,
        afterfill_audit_required=afterfill_audit_required,
        suggested_actions=suggested_actions,
    )


def build_batch_execution_preview(
    gate: MaterialGateResult,
    *,
    apply_exam_now: bool,
    generate_list: bool,
) -> list[ExecutionPreviewItem]:
    if gate.hard_block:
        return [
            ExecutionPreviewItem(
                kind="BLOCK_SUBMIT",
                label="阻止递交",
                enabled=False,
                detail="存在硬性缺失材料，不能进入批量递交事务",
            )
        ]

    preview = [
        ExecutionPreviewItem(
            kind="CASE_STATUS",
            label="案件状态更新为等待回执",
            enabled=True,
        ),
        ExecutionPreviewItem(
            kind="DOCUMENT",
            label="生成批量递交清单文件",
            enabled=generate_list,
        ),
        ExecutionPreviewItem(
            kind="TASK",
            label="生成申请费时限任务",
            enabled=True,
        ),
    ]
    if apply_exam_now:
        preview.append(
            ExecutionPreviewItem(
                kind="EXAM_REQUEST",
                label="同步标记立即提出实审请求",
                enabled=True,
            )
        )
    if gate.afterfill_audit_required:
        preview.append(
            ExecutionPreviewItem(
                kind="AFTERFILL_AUDIT",
                label="登记后补材料审计要求",
                enabled=True,
            )
        )
    return preview


def _matches_requirement(
    requirement: MaterialRequirement,
    document: GateDocumentInput,
) -> bool:
    if not document.has_attachment:
        return False

    role_code = _norm_code(document.role_code)
    if role_code and role_code == requirement.code:
        return True

    template_code = _norm_code(document.template_code)
    if template_code and template_code in requirement.template_codes:
        return True

    doc_type = _norm_code(document.doc_type)
    searchable_text = f"{document.title or ''} {document.extra_data or ''}"
    return bool(
        doc_type in requirement.doc_types
        and any(token in searchable_text for token in requirement.title_tokens)
    )


def _norm_code(value: str | None) -> str:
    return (value or "").strip().upper()
