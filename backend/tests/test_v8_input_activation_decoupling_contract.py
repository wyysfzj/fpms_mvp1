import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


ADOPTION_PATH = ROOT / (
    "docs/product/v8/reviews/"
    "V8-INPUT-ACTIVATION-DECOUPLING-CURRENT-ADOPTION.md"
)

ADOPTION_TASK = ROOT / (
    "tasks/postdemo/v8/"
    "FPMS-V8-INPUT-ACTIVATION-DECOUPLING-ADOPTION-20260813-01.md"
)

SUCCESSOR_TASKS = {
    "FPMS-V8-PAYMENT-WORKBOOK-INPUT-VERSION-CARRIER-20260812-01": (
        "tasks/postdemo/v8/"
        "FPMS-V8-PAYMENT-WORKBOOK-INPUT-VERSION-CARRIER-20260812-01.md"
    ),
    "FPMS-V8-PAYMENT-WORKBOOK-INPUT-GOVERNANCE-SERVICE-20260812-01": (
        "tasks/postdemo/v8/"
        "FPMS-V8-PAYMENT-WORKBOOK-INPUT-GOVERNANCE-SERVICE-20260812-01.md"
    ),
    "FPMS-V8-PAYMENT-WORKBOOK-INPUT-ADMIN-API-20260812-01": (
        "tasks/postdemo/v8/"
        "FPMS-V8-PAYMENT-WORKBOOK-INPUT-ADMIN-API-20260812-01.md"
    ),
    "FPMS-V8-INPUT-ACTIVATION-CAPABILITY-CLOSE-20260813-01": (
        "tasks/postdemo/v8/"
        "FPMS-V8-INPUT-ACTIVATION-CAPABILITY-CLOSE-20260813-01.md"
    ),
}

AFFECTED_TASK_BASELINES = {
    "tasks/postdemo/v8/FPMS-V8-PAYMENT-WORKBOOK-MANIFEST-ACTIVATION-20260712-01.md": "310deda1924d2175a9371803f5ffe5acc7b1c35434a6fdd09da2f655c2a2133f",
    "tasks/postdemo/v8/FPMS-V8-SERVICE-RATE-MANIFEST-ACTIVATION-20260712-01.md": "a8605063088bee21920fd9640b810c340ca3027618261f5fc49bbb5b98fd39a9",
    "tasks/postdemo/v8/FPMS-V8-OFFICIAL-PAYMENT-WORKBOOK-ADAPTER-20260712-01.md": "050d6214c11ce6f38296ccd7a402896b14bf121660f194715e9e9107e8310d20",
    "tasks/postdemo/v8/FPMS-V8-OFFICIAL-PAYMENT-WORKBOOK-GENERATION-SERVICE-20260712-01.md": "ad7010e1fd79f8dd695b45cc9f5c01f1f1be430df10a1117cc47ff11f0612eb9",
    "tasks/postdemo/v8/FPMS-V8-OFFICIAL-PAYMENT-WORKBOOK-HTTP-20260712-01.md": "cb0342f0f9b8ccbfe325c2fb6928dd94727d616887a8b80f8a099dd4806c7819",
    "tasks/postdemo/v8/FPMS-V8-OFFICIAL-PAYMENT-WORKBOOK-FE-ADAPTER-20260712-01.md": "663d7bb2a048502f8366917e80dd7193ff96c9e847c21c95476a9ea201859e66",
    "tasks/postdemo/v8/FPMS-V8-OFFICIAL-PAYMENT-WORKBOOK-UI-20260712-01.md": "c59c316bc1de0d66a44650d1e96ef97d6fe8cfd37728ff65cd753f84c8c7a477",
    "tasks/postdemo/v8/FPMS-V8-OFFICIAL-WORKBOOK-ACCEPTANCE-EVIDENCE-SERVICE-20260712-01.md": "3eedef2d9b793ab5276ac8531ce5756dffe4e1c81d2617da0cfef445bc75b06b",
    "tasks/postdemo/v8/FPMS-V8-OFFICIAL-WORKBOOK-ACCEPTANCE-EVIDENCE-API-20260712-01.md": "ff8bcf9697c7d52afd21565fb084a0a85b237c29249b979db6df576755912b9e",
    "tasks/postdemo/v8/FPMS-V8-OFFICIAL-WORKBOOK-ACCEPTANCE-FE-ADAPTER-20260712-01.md": "4e1de405e3ddf2e0ca5589f48f184808786c2abab91e9725fb85777d81f5ff93",
    "tasks/postdemo/v8/FPMS-V8-OFFICIAL-WORKBOOK-ACCEPTANCE-EVIDENCE-UI-20260712-01.md": "8e8987fd049d883a92fc464007b5929d8e7112b296988df27a921f4171f83cb9",
    "tasks/postdemo/v8/FPMS-V8-SERVICE-PRICE-BOOK-CARRIER-20260712-01.md": "946124252c986e2b40aada04897f0e1b4ea577bc71da6cf4aa18be80eb58762d",
    "tasks/postdemo/v8/FPMS-V8-SERVICE-PRICE-BOOK-IMPORT-SERVICE-20260712-01.md": "8fe960b522cdfedd758d2601ad41a21ae0079ff733de70bb5d7d0b2665070e5b",
    "tasks/postdemo/v8/FPMS-V8-SERVICE-PRICE-BOOK-IMPORT-API-20260712-01.md": "ccb11ba33b5ff50f7c5e4575f1bc524b35878975e47734731ef4cad510c014fa",
    "tasks/postdemo/v8/FPMS-V8-SERVICE-PRICE-BOOK-ACTIVATION-20260712-01.md": "2629a5291b9fd50e3eeba5ed05fbc1e84f62c15003729c26acd3ade0618c2d70",
    "tasks/postdemo/v8/FPMS-V8-SERVICE-PRICE-BOOK-ACTIVATION-API-20260712-01.md": "dfb3d6fbe29dc2cc57920b778ef8bb54c702dab0974a8ac40b6c0cba0897157a",
    "tasks/postdemo/v8/FPMS-V8-SERVICE-RECEIVABLE-OBLIGATION-20260712-01.md": "60d7228f3522b23d81522efbcf1037531e834f2bf7640f930e2ca9d0c18e764d",
    "tasks/postdemo/v8/FPMS-V8-SERVICE-RECEIVABLE-OBLIGATION-API-20260712-01.md": "f252a775971e1453110f0e9b4af84dfad64a472aeecb2ae71392d834a3690c69",
    "tasks/postdemo/v8/FPMS-V8-OFFICIAL-WORKBOOK-REAL-UI-E2E-20260712-01.md": "4c58ce034d28a0343b1320c202f293ac038489c164fb2284d0d09289064bd4c7",
    "tasks/postdemo/v8/FPMS-V8-INHERITED-REGRESSION-MATRIX-20260712-01.md": "bdc8302bfc474ed8877e7b32cd3b777e2c16cc1711a421e8a9099c2a636851f1",
    "tasks/postdemo/v8/FPMS-V8-FINAL-ITEM-SLICE-LEDGER-20260712-01.md": "edfd182c7d15944b68e41bb3d2c552c15e21b5b69c8f0479643e3d9b7dd50041",
    "tasks/postdemo/v8/FPMS-V8-FINAL-CLOSE-20260712-01.md": "b1f2f715d91a8702031da3300cde7a2645bd3753dd8500d5f12b9f5ded5d2c59",
}

APPENDIX_MARKER = "\n## Latest-Wins Input Activation Dependency Interpretation"
FULL_PAYMENT_SPINE = (
    "FPMS-V8-PAYMENT-WORKBOOK-MANIFEST-ACTIVATION-20260712-01 (row175) -> "
    "WB-I1 -> row214 -> WB-I2 -> WB-I3 -> rows215-222 -> row278"
)
DESIGN_COMMIT = "bd88cb3e38d88ef83359f4b2c70e2454bb27aeb4"
DESIGN_PATCH_SHA256 = "8f471d53690b91a222591c991c6b602cae65f827c37a8c01d3ab77578cea3b0c"
FROZEN_CATALOG_SHA256 = "72c849825c9cbd39cb25f743d448b67a2a31bfccf7cfb68a3d2557c7bda178bf"


def test_input_activation_decoupling_successor_is_adopted() -> None:
    assert ADOPTION_PATH.is_file(), f"missing successor adoption: {ADOPTION_PATH}"

    adoption = ADOPTION_PATH.read_text(encoding="utf-8")
    task = ADOPTION_TASK.read_text(encoding="utf-8")
    for required in (
        DESIGN_COMMIT,
        DESIGN_PATCH_SHA256,
        "Customer written adoption: 2026-08-13",
        "rows 175, 176, 214-229, 278, 281-283",
        "CAPABILITY_READY",
        "CONFIG_REQUIRED",
        "409 / NO WRITE",
        "TEST_ONLY",
        "DG-PAYMENT-WORKBOOK:GLOBAL",
        "DG-SERVICE-RATE-VERSION:GLOBAL",
        FULL_PAYMENT_SPINE,
        "never claims production activation",
    ):
        assert required in adoption
        assert required in task


def test_successor_task_cards_freeze_atomic_owners_and_order() -> None:
    texts = {}
    for task_id, relative_path in SUCCESSOR_TASKS.items():
        path = ROOT / relative_path
        assert path.is_file(), f"missing successor task: {relative_path}"
        text = path.read_text(encoding="utf-8")
        texts[task_id] = text
        for heading in (
            "## Exact Closure Slice",
            "## Explicit Non-Closure",
            "## Dependencies",
            "## Allowed Files",
            "## Targeted RED / GREEN",
            "## Serialized Ownership",
            "## Evidence Path",
            "## Rollback Boundary",
            "## Independent Close",
        ):
            assert heading in text
        assert task_id in text

    carrier = " ".join(
        texts["FPMS-V8-PAYMENT-WORKBOOK-INPUT-VERSION-CARRIER-20260812-01"].split()
    )
    for required in (
        "GLOBAL",
        "PRODUCTION|TEST_ONLY",
        "row175 terminal PASS",
        "external successor prerequisite, not a row175 manifest member",
        "backend/alembic/versions/v8_payment_workbook_input_version.py",
        "backend/app/modules/annuity/models.py",
        "backend/app/models/__init__.py",
        "backend/tests/test_v8_payment_workbook_input_version.py",
        "forward-only migration and data compatibility",
        "no destructive downgrade or data deletion",
    ):
        assert required in carrier

    service = " ".join(
        texts[
            "FPMS-V8-PAYMENT-WORKBOOK-INPUT-GOVERNANCE-SERVICE-20260812-01"
        ].split()
    )
    for required in (
        "registers DRAFT input",
        "WB-I1 and row 214 independently accepted before RED",
        "backend/app/modules/annuity/official_payment_workbook_input_service.py",
        "backend/tests/test_v8_payment_workbook_input_service.py",
        "Remove only the owned service and focused test",
        "TEST_ONLY",
        "409 / NO WRITE",
    ):
        assert required in service

    api = " ".join(
        texts["FPMS-V8-PAYMENT-WORKBOOK-INPUT-ADMIN-API-20260812-01"].split()
    )
    for required in (
        "multipart register, review, activate, and retire",
        "WB-I2 independently accepted after WB-I1 and row 214",
        "backend/app/modules/annuity/api.py",
        "backend/app/modules/annuity/official_payment_workbook_input_schemas.py",
        "backend/tests/test_v8_payment_workbook_input_api.py",
        "Remove only the owned router/schema changes and focused API test",
        "Fee.Edit",
        "409 / NO WRITE",
    ):
        assert required in api

    capability_close = " ".join(
        texts[
            "FPMS-V8-INPUT-ACTIVATION-CAPABILITY-CLOSE-20260813-01"
        ].split()
    )
    for required in (
        "Task Contract Profile: `TC-QA`",
        "QA-only",
        "CAPABILITY_READY + CONFIG_REQUIRED",
        "Both exact lane manifests and all their original members independently accepted",
        "tasks/postdemo/v8/FPMS-V8-INPUT-ACTIVATION-CAPABILITY-CLOSE-20260813-01.md",
        "docs/product/v8/reviews/V8-INPUT-ACTIVATION-CAPABILITY-CURRENT-ADOPTION.md",
        "backend/tests/test_v8_input_activation_capability_close.py",
        "Remove only the owned QA task update, current-adoption record, and focused capability-close test",
        "never claims production activation",
    ):
        assert required in capability_close

    for text in texts.values():
        assert (
            "Revert only this task's exact commit and owned paths before dependent tasks start."
            in text
        )
        assert "Leave accepted predecessors and production inputs untouched." in text

def test_latest_wins_appendix_changes_only_prerequisite_interpretation() -> None:
    assert len(AFFECTED_TASK_BASELINES) == 22
    appendices = {}
    for relative_path, baseline_sha256 in AFFECTED_TASK_BASELINES.items():
        text = (ROOT / relative_path).read_text(encoding="utf-8")
        assert text.count(APPENDIX_MARKER) == 1, relative_path
        original, appendix = text.split(APPENDIX_MARKER, maxsplit=1)
        assert hashlib.sha256(original.encode()).hexdigest() == baseline_sha256
        appendices[relative_path] = appendix
        for required in (
            "Development prerequisite",
            "Production prerequisite",
            "409 / NO WRITE",
            "CAPABILITY_READY",
            "Existing closure, non-closure, allowlist, permissions, primary tests and evidence remain intact",
        ):
            assert required in appendix, relative_path

    paths = tuple(AFFECTED_TASK_BASELINES)
    payment_manifest = appendices[paths[0]]
    service_manifest = appendices[paths[1]]
    assert "exactly 11 members" in payment_manifest
    assert "exactly 8 members" in service_manifest
    for text in (payment_manifest, service_manifest):
        assert "WB-I1/WB-I2/WB-I3 are external successor prerequisites" in text

    for appendix in tuple(appendices.values())[2:]:
        assert "exactly 11 members" not in appendix
        assert "exactly 8 members" not in appendix

    full_final_appendices = tuple(appendices.values())[-3:]
    for appendix in full_final_appendices:
        assert "CONFIG_REQUIRED is acceptable only with verified negative-path evidence" in appendix
        assert "never claims production activation" in appendix
    for appendix in tuple(appendices.values())[:-3]:
        assert "CONFIG_REQUIRED is acceptable only with verified negative-path evidence" not in appendix


def test_frozen_catalog_bytes_are_unchanged() -> None:
    catalog = ROOT / "docs/product/v8/catalog.frozen.json"
    actual = hashlib.sha256(catalog.read_bytes()).hexdigest()
    assert actual == FROZEN_CATALOG_SHA256
