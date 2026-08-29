from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GUIDE = ROOT / "docs/postdemo/demo-v6-colleague-clone-start-guide.md"
HANDOFF = ROOT / "docs/postdemo/demo-v6-clone-deploy-handoff.md"
RUNBOOK = ROOT / "docs/postdemo/demo-lifecycle-customer-v6-runbook.md"
SEED_GUIDE = ROOT / "docs/postdemo/demo-lifecycle-customer-v6-seed-data.md"
HTML = ROOT / "docs/postdemo/demo-lifecycle-customer-v6.html"
CONTRACT = (
    ROOT / "FPMS_Automation_Skeleton_Pack/data/testcases/demo_v6_ui_parity_v1.json"
)
EXPECTED_TAG = "demo-v6-customer-20260829-r1"
EXPECTED_STAGES = tuple(f"{index:02d}" for index in range(1, 12))
REQUIRED_RUNBOOK_FIELDS = (
    "演示话术",
    "UI/操作",
    "输入",
    "屏幕输出",
    "期待结果",
    "验证方法",
    "事实边界",
    "停止条件",
    "最近新增",
)
STALE_CANDIDATES = (
    "90d9c560cd2d8687fddb038dcd8c3f51cd8af72b",
    "codex/demo-v6-ui-parity-candidate-20260826",
)


def _read(path: Path) -> str:
    if not path.is_file():
        raise RuntimeError(f"缺少 V6 演示产物：{path}")
    return path.read_text(encoding="utf-8")


def _require_tokens(text: str, tokens: tuple[str, ...], label: str) -> None:
    missing = [token for token in tokens if token not in text]
    if missing:
        raise RuntimeError(f"{label} 缺少当前合同：{missing}")


def check() -> None:
    documents = {
        "Guide": _read(GUIDE),
        "Handoff": _read(HANDOFF),
        "Runbook": _read(RUNBOOK),
        "Seed": _read(SEED_GUIDE),
        "HTML": _read(HTML),
    }
    contract = json.loads(_read(CONTRACT))
    combined = "\n".join(documents.values())

    for label in ("Guide", "Handoff"):
        if EXPECTED_TAG not in documents[label]:
            raise RuntimeError(f"{label} 未绑定统一不可变 tag")
    for stale in STALE_CANDIDATES:
        if stale in combined:
            raise RuntimeError(f"V6 文档仍引用旧 candidate：{stale}")

    html_stages = tuple(re.findall(r'data-stage="(\d{2})"', documents["HTML"]))
    runbook_matches = list(
        re.finditer(r"^## 阶段 (\d{2})", documents["Runbook"], re.MULTILINE)
    )
    if html_stages != EXPECTED_STAGES or tuple(
        match.group(1) for match in runbook_matches
    ) != EXPECTED_STAGES:
        raise RuntimeError("V6 lifecycle/runbook 阶段必须严格为 01–11")
    for index, match in enumerate(runbook_matches):
        end = (
            runbook_matches[index + 1].start()
            if index + 1 < len(runbook_matches)
            else len(documents["Runbook"])
        )
        body = documents["Runbook"][match.start() : end]
        missing = [
            field for field in REQUIRED_RUNBOOK_FIELDS if f"**{field}**" not in body
        ]
        if missing:
            raise RuntimeError(f"阶段 {match.group(1)} 缺少字段：{missing}")

    stages = contract.get("stages", [])
    if [stage.get("stage") for stage in stages] != list(EXPECTED_STAGES):
        raise RuntimeError("JSON contract 阶段顺序必须为 01–11")
    input_count = sum(len(stage.get("inputs", [])) for stage in stages)
    output_count = sum(len(stage.get("outputs", [])) for stage in stages)
    if (input_count, output_count, len(stages)) != (103, 30, 11):
        raise RuntimeError(
            f"JSON contract 计数漂移：inputs={input_count}, outputs={output_count}, stages={len(stages)}"
        )

    _require_tokens(
        documents["Handoff"],
        (
            "--strict-ui",
            "--runs 1",
            "--headless",
            "HUMAN：待完成",
            "CODEX：待完成",
            "Comparator：待完成",
            "upload-manifest.json",
        ),
        "Handoff",
    )
    _require_tokens(
        documents["Runbook"],
        (
            "客户名称面包屑",
            "第5阶段/5 · 授权登记",
            "结构化文书字段",
            "历史首次申请递交材料核验",
            "预览官费",
            "确认官费",
            "现在是什么状态",
            "最近发生了什么",
            "下一步是什么",
            "查看完整历史",
            "审计信息",
        ),
        "Runbook",
    )
    _require_tokens(
        documents["Seed"],
        ("upload-manifest.json", "12 行", "valid_until=2026-09-30"),
        "Seed guide",
    )
    _require_tokens(
        documents["HTML"],
        (
            "客户名称面包屑",
            "结构化文书字段",
            "当前事实优先",
            "查看完整历史",
            "技术标识、摘要和原始状态默认隐藏",
        ),
        "Customer HTML",
    )
    for forbidden in (
        "persisted-only",
        "revision-aware",
        "network-idle",
        "digest-bound",
        "PARTIALLY_SETTLED",
        "SETTLED",
        "DEMO-CASE-",
        "/demo/abc",
    ):
        if forbidden in documents["HTML"]:
            raise RuntimeError(f"客户 HTML 包含禁止技术文本：{forbidden}")

    projection = json.dumps(stages, ensure_ascii=False)
    _require_tokens(
        projection,
        (
            "customer-name breadcrumb",
            "case-list current stage and workflow status",
            "structured document fields",
            "historical initial-filing gate",
            "official fee preview and confirmation actions are visible and enabled",
            "current-first three-lane summary",
            "full history is collapsed by default",
            "raw identifiers, hashes, and English statuses remain hidden until audit disclosure is expanded",
        ),
        "JSON contract",
    )


if __name__ == "__main__":
    check()
    print("customer demo lifecycle V6: PASS")
