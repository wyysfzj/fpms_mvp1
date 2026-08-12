from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CATALOG_PATH = ROOT / "docs/product/v8/catalog.frozen.json"
LEDGER_PATH = ROOT / "docs/product/v8/coverage-ledger.json"
REGISTRY_PATH = ROOT / "docs/product/v8/source-decision-registry.md"
ROW199_TASK_PATH = ROOT / (
    "tasks/postdemo/v8/FPMS-V8-FULL-MANIFEST-ACTIVATION-20260712-01.md"
)
SUCCESSOR_PATH = ROOT / "docs/product/v8/stories/V8-FULL-CONFIG-REQUIRED-SUCCESSOR.md"

CATALOG_SHA256 = "72c849825c9cbd39cb25f743d448b67a2a31bfccf7cfb68a3d2557c7bda178bf"
CAPABILITY_CLOSE_SHA = "a8219b7a39047b819100cc69dd4cffadfc3e170c"
CAPABILITY_ADOPTION_SHA = "03138fbd5b1089634b84d353bf2abffd70777e41"
CONFIG_SUCCESSOR_SHA = "99316d6c83fe9c1c0e93b9703a5ea28509ea1ac6"
CAPABILITY_STORY = "V8-INPUT-ACTIVATION-CAPABILITIES-CURRENT-ADOPTION"
GLOBAL_IDENTITIES = [
    "DG-GRANT-EVIDENCE-SOURCE:GLOBAL",
    "DG-GRANT-MANUAL-REVIEW:GLOBAL",
    "DG-FEE-APPLICATION-DRAFT:GLOBAL",
    "DG-FEE-GRANT-YEAR-DRAFT:GLOBAL",
    "DG-FEE-FUTURE-ANNUITY:GLOBAL",
    "DG-PAYMENT-WORKBOOK:GLOBAL",
    "DG-SERVICE-RATE-VERSION:GLOBAL",
]
FORM_IDENTITIES = [f"DG-LEGACY-FORM-CLASS:form-{number:03d}" for number in range(1, 23)]
TERMINAL_IDS = [
    "FPMS-V8-FULL-MANIFEST-ACTIVATION-20260712-01",
    "FPMS-V8-INHERITED-REGRESSION-MATRIX-20260712-01",
    "FPMS-V8-FINAL-ITEM-SLICE-LEDGER-20260712-01",
    "FPMS-V8-FINAL-CLOSE-20260712-01",
]


def _json_fence(text: str) -> dict[str, object]:
    match = re.search(r"```json\n(.*?)\n```", text, flags=re.DOTALL)
    assert match is not None, "successor must contain one machine-readable contract"
    return json.loads(match.group(1))


def _ledger_at(commit: str) -> dict[str, object]:
    result = subprocess.run(
        ["git", "show", f"{commit}:docs/product/v8/coverage-ledger.json"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def test_row199_identity_and_all_29_requested_gate_identities_remain_frozen() -> None:
    catalog_bytes = CATALOG_PATH.read_bytes()
    assert hashlib.sha256(catalog_bytes).hexdigest() == CATALOG_SHA256
    catalog = json.loads(catalog_bytes)
    row199 = catalog["tasks"][198]

    assert row199["ordinal"] == 199
    assert row199["task_id"] == TERMINAL_IDS[0]
    assert row199["task_path"] == ROW199_TASK_PATH.relative_to(ROOT).as_posix()
    assert row199["profile"] == "TC-QA"
    assert row199["owner_role"] == "Team Lead / default"
    assert row199["phase"] == "deferred"
    assert row199["serialization_groups"] == [
        {"ownership": "FULL_MANIFEST_OWNERSHIP", "order_key": 1}
    ]
    assert row199["gate_requirements"] == [
        *[
            {"code": identity.partition(":")[0], "scope": "GLOBAL"}
            for identity in GLOBAL_IDENTITIES
        ],
        {"code": "DG-LEGACY-FORM-CLASS", "scope": "ALL-22"},
    ]

    task = ROW199_TASK_PATH.read_text(encoding="utf-8")
    for identity in GLOBAL_IDENTITIES + FORM_IDENTITIES:
        assert f"`{identity}`" in task

    successor = _json_fence(SUCCESSOR_PATH.read_text(encoding="utf-8"))
    assert successor["row199_task_id"] == TERMINAL_IDS[0]
    assert successor["requested_gate_identities"] == GLOBAL_IDENTITIES + FORM_IDENTITIES
    assert len(successor["requested_gate_identities"]) == 29


def test_only_two_input_families_use_capability_config_split() -> None:
    successor_text = SUCCESSOR_PATH.read_text(encoding="utf-8")
    successor = _json_fence(successor_text)
    production_inputs = {
        "DG-PAYMENT-WORKBOOK:GLOBAL": "CONFIG_REQUIRED",
        "DG-SERVICE-RATE-VERSION:GLOBAL": "CONFIG_REQUIRED",
    }
    assert successor["capability_close_commit"] == CAPABILITY_CLOSE_SHA
    assert successor["capability_ledger_adoption_commit"] == CAPABILITY_ADOPTION_SHA
    assert successor["capability_story_id"] == CAPABILITY_STORY
    assert successor["production_inputs"] == production_inputs
    assert successor["production_failure"] == "409 / NO WRITE"
    assert successor["production_activation_claimed"] is False

    ledger = json.loads(LEDGER_PATH.read_text())
    capability_story = next(
        story for story in ledger["stories"] if story["story_id"] == CAPABILITY_STORY
    )
    assert capability_story["status"] == "CURRENT_VERIFIED"
    assert capability_story["commits"][0] == CAPABILITY_CLOSE_SHA
    assert capability_story["capability_status"] == "CAPABILITY_READY"
    assert capability_story["production_inputs"] == production_inputs
    assert capability_story["production_failure"] == "409 / NO WRITE"
    assert capability_story["production_activation_claimed"] is False

    for required in (
        "CAPABILITY_READY + CONFIG_REQUIRED",
        "TEST_ONLY",
        "test_missing_or_test_only_production_input_fails_409_without_side_effects",
        "test_test_resolution_rejects_ambiguity_and_production_rejects_test_only",
        "test_malformed_or_test_only_candidate_is_409_without_mutation",
        "test_noncanonical_book_hash_is_409_without_receivable_write",
    ):
        assert required in successor_text

    registry = REGISTRY_PATH.read_text(encoding="utf-8")
    assert "| `DG-PAYMENT-WORKBOOK` | `PENDING` |" in registry
    assert "| `DG-SERVICE-RATE-VERSION` | `PENDING` |" in registry


def test_gate_rows_are_current_but_full_and_terminal_rows_remain_unadopted() -> None:
    ledger = json.loads(LEDGER_PATH.read_text())
    rows = ledger["rows"]
    for ordinal in range(170, 199):
        row = rows[ordinal - 1]
        assert row["disposition"] == "CURRENT_VERIFIED", ordinal
        assert row["story_id"], ordinal

    assert rows[174]["story_id"] == CAPABILITY_STORY
    assert rows[175]["story_id"] == CAPABILITY_STORY
    assert [
        ordinal
        for ordinal in range(170, 199)
        if rows[ordinal - 1]["story_id"] == CAPABILITY_STORY
    ] == [175, 176]
    successor_rows = _ledger_at(CONFIG_SUCCESSOR_SHA)["rows"]
    for ordinal, task_id in zip((199, 281, 282, 283), TERMINAL_IDS, strict=True):
        row = successor_rows[ordinal - 1]
        assert row["catalog_id"] == task_id
        assert row["disposition"] != "CURRENT_VERIFIED"
        assert row["story_id"] is None

    successor = _json_fence(SUCCESSOR_PATH.read_text(encoding="utf-8"))
    assert successor["next_step"] == "ROW199_FULL_CAPABILITY_MANIFEST_CLOSE"
    assert successor["unadopted_catalog_rows"] == [199, 281, 282, 283]
