import hashlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "tasks/batches/FPMS-POSTDEMO-V8-GRANT-REVIEW-GATE-20260712-01.md"
ACTIVATION_ID = "FPMS-V8-GRANT-REVIEW-GATE-MANIFEST-ACTIVATION-20260712-01"
TASK_IDS = [
    ACTIVATION_ID,
    "FPMS-V8-GRANT-EVIDENCE-REVIEW-SERVICE-20260712-01",
    "FPMS-V8-GRANT-ANNOUNCEMENT-EVIDENCE-ADAPTER-20260712-01",
    "FPMS-V8-PATENT-REGISTER-EVIDENCE-ADAPTER-20260712-01",
    "FPMS-V8-GRANT-EVIDENCE-ACCEPTED-DISPATCH-ADAPTER-20260712-01",
    "FPMS-V8-GRANT-EVIDENCE-REVIEW-API-20260712-01",
    "FPMS-V8-GRANT-EVIDENCE-REVIEW-FE-ADAPTER-20260712-01",
    "FPMS-V8-GRANT-EVIDENCE-REVIEW-UI-20260712-01",
]
TASK_PATHS = [f"tasks/postdemo/v8/{task_id}.md" for task_id in TASK_IDS]
TASK_HASHES = {
    ACTIVATION_ID: "daaacaef4655e052e1689c56609af93ea4b6597412be79e2a1d25e0cdcb1bed2",
    "FPMS-V8-GRANT-EVIDENCE-REVIEW-SERVICE-20260712-01": (
        "23926502da9273a8a9244e8b3228b610a41ea40db35d004d9be1dfea75cbdcea"
    ),
    "FPMS-V8-GRANT-ANNOUNCEMENT-EVIDENCE-ADAPTER-20260712-01": (
        "35ec0e945b3fddfc9c1a2afb888c48c3067aee64a6097c1900b9cb13c618aea1"
    ),
    "FPMS-V8-PATENT-REGISTER-EVIDENCE-ADAPTER-20260712-01": (
        "f90ad26c621d8d8c580121bae1ea5e2b8cf3e12ca322d2e56f035f719d854aba"
    ),
    "FPMS-V8-GRANT-EVIDENCE-ACCEPTED-DISPATCH-ADAPTER-20260712-01": (
        "aa8a2e01707eda7ae47514c843cf31ec96ebc1ca1b97faa05a230d6658598939"
    ),
    "FPMS-V8-GRANT-EVIDENCE-REVIEW-API-20260712-01": (
        "fa1bf602a63d74e78a2b3184565a5c178578f8c617f1b5199622a8045fd324dc"
    ),
    "FPMS-V8-GRANT-EVIDENCE-REVIEW-FE-ADAPTER-20260712-01": (
        "a1c664c3faf9b8b7316bda522a78e272468993f970f39c54cb70cfe890481487"
    ),
    "FPMS-V8-GRANT-EVIDENCE-REVIEW-UI-20260712-01": (
        "e19b590d4d789575927ae26df21f54e74c5b6b43a02b816d4a6fb61c912dced6"
    ),
}


def _text() -> str:
    return MANIFEST.read_text(encoding="utf-8")


def _sections(text: str) -> dict[str, str]:
    matches = list(re.finditer(r"^## \d{3}\. (FPMS-V8-[A-Z0-9-]+)$", text, re.MULTILINE))
    return {
        match.group(1): text[
            match.start() : (matches[index + 1].start() if index + 1 < len(matches) else len(text))
        ]
        for index, match in enumerate(matches)
    }


def test_manifest_has_exact_ordered_membership_and_current_hashes() -> None:
    text = _text()
    paths = re.findall(r"^- Task file: `(tasks/postdemo/v8/[^`]+\.md)`$", text, re.MULTILINE)
    sections = _sections(text)
    assert re.findall(r"^Task count: (\d+)$", text, re.MULTILINE) == ["8"]
    assert paths == TASK_PATHS
    assert list(sections) == TASK_IDS
    for task_id, path in zip(TASK_IDS, TASK_PATHS, strict=True):
        digest = hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
        assert digest == TASK_HASHES[task_id]
        assert f"Task SHA-256: `{digest}`" in sections[task_id]


def test_manifest_activates_development_without_runtime_authority() -> None:
    text = _text()
    required = (
        "DG-GRANT-EVIDENCE-SOURCE:GLOBAL",
        "DG-GRANT-MANUAL-REVIEW:GLOBAL",
        "APPROVED_POLICY / CONFIG_REQUIRED",
        "customer-decision:2026-08-10:v8-full-batch-scheme-a:v1",
        "e6cfd648f1d366e27bde3f74310f00033a6db60ce55d850d2e668764745faace",
        "Product development: ELIGIBLE",
        "Runtime source configuration: REQUIRED / NOT PROVIDED BY THIS MANIFEST",
        "Runtime role configuration: REQUIRED / NOT PROVIDED BY THIS MANIFEST",
        "409 / NO WRITE / NO LEGAL-STATE CHANGE",
        "publishes no source record",
        "role binding",
        "default or seed",
    )
    for value in required:
        assert value in text
    assert "www.cnipa.gov.cn" not in text


def test_manifest_preserves_closure_and_fail_closed_dispatch_order() -> None:
    text = _text()
    sections = _sections(text)
    expected = {
        TASK_IDS[1]: ("proposer/reviewer separation", "dispatch nothing before acceptance"),
        TASK_IDS[2]: ("announcement lifecycle", "direct status write", "order key 5"),
        TASK_IDS[3]: ("same-status verification/conflict", "direct status write", "order key 6"),
        TASK_IDS[4]: ("same caller-owned transaction", "rejection or conflict invokes none"),
        TASK_IDS[5]: ("`Doc.Edit` POST review endpoint", "409 for role/source/conflict"),
        TASK_IDS[6]: ("deriving legal state", "No page behavior"),
        TASK_IDS[7]: ("conflicts remain visible", "no pre-approval legal state"),
    }
    for task_id, contracts in expected.items():
        for contract in contracts:
            assert contract in sections[task_id]
    assert "All shared-file and SQLite-writing verification remains serialized" in text
    assert "cannot approve" in text
    assert "rejection or conflict cannot dispatch" in text
