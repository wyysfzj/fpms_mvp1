from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "docs/postdemo/demo-lifecycle-customer-v6.html"
RUNBOOK = ROOT / "docs/postdemo/demo-lifecycle-customer-v6-runbook.md"
SPEC = (
    ROOT
    / "FPMS_Automation_Skeleton_Pack"
    / "playwright_ts"
    / "src"
    / "tests"
    / "demo-integrated-v6.live-backend.spec.ts"
)
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


def _read(path: Path) -> str:
    if not path.is_file():
        raise RuntimeError(f"缺少 V6 演示产物：{path}")
    return path.read_text(encoding="utf-8")


def check() -> None:
    html = _read(HTML)
    runbook = _read(RUNBOOK)
    spec = _read(SPEC)
    html_stages = tuple(re.findall(r'data-stage="(\d{2})"', html))
    runbook_matches = list(re.finditer(r"^## 阶段 (\d{2})", runbook, re.MULTILINE))
    runbook_stages = tuple(match.group(1) for match in runbook_matches)
    if html_stages != EXPECTED_STAGES or runbook_stages != EXPECTED_STAGES:
        raise RuntimeError("V6 lifecycle/runbook 阶段必须严格为 01–11")
    for index, match in enumerate(runbook_matches):
        end = runbook_matches[index + 1].start() if index + 1 < len(runbook_matches) else len(runbook)
        body = runbook[match.start() : end]
        missing = [field for field in REQUIRED_RUNBOOK_FIELDS if f"**{field}**" not in body]
        if missing:
            raise RuntimeError(f"阶段 {match.group(1)} 缺少字段：{missing}")
    combined = html + runbook + spec
    for token in (
        "候选预览，尚未形成缴费义务",
        "调整数量",
        "已登记，待官方凭证核验",
        "PARTIALLY_SETTLED",
        "SETTLED",
        "同案双轨费用概览",
        "SYNTHETIC_TEST_ONLY",
    ):
        if token not in combined:
            raise RuntimeError(f"V6 产物缺少事实边界：{token}")
    for forbidden in ("DEMO-CASE-", "客户决策", "/demo/abc"):
        if forbidden in html or forbidden in runbook:
            raise RuntimeError(f"客户材料包含禁止内容：{forbidden}")


if __name__ == "__main__":
    check()
    print("customer demo lifecycle V6: PASS")
