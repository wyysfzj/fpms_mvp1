from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
COMPARATOR = ROOT / "scripts" / "compare_demo_v6_ui_receipts.py"
CONTRACT = (
    ROOT
    / "FPMS_Automation_Skeleton_Pack"
    / "data"
    / "testcases"
    / "demo_v6_ui_parity_v1.json"
)


def _comparator_module():
    assert COMPARATOR.exists(), f"receipt comparator is absent: {COMPARATOR}"
    spec = importlib.util.spec_from_file_location("compare_demo_v6_ui_receipts", COMPARATOR)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _receipt(actor: str) -> dict:
    suffix = actor.lower()
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    input_ledger = [
        {
            "stage": stage["stage"],
            "field_key": row["field_key"],
            "classification": row["classification"],
            "normalization": row["normalization"],
            "source_selector": row["source_selector"],
            "normalized_value": row["value_rule"],
        }
        for stage in contract["stages"]
        for row in stage["inputs"]
    ]
    output_ledger = [
        {
            "stage": stage["stage"],
            "field_key": row["field_key"],
            "classification": row["classification"],
            "normalization": row["normalization"],
            "observable": row["observable"],
            "expected_rule": row["expected_rule"],
            "normalized_value": row["value_rule"],
        }
        for stage in contract["stages"]
        for row in stage["outputs"]
    ]
    return {
        "schema_id": "fpms.demo-v6-ui-parity/v1",
        "status": "PASS",
        "actor": actor,
        "account_id": f"account-{suffix}",
        "run_id": f"run-{suffix}",
        "run_root": f"/tmp/run-{suffix}",
        "database_path": f"/tmp/run-{suffix}/fpms.db",
        "candidate_commit": "a" * 40,
        "candidate_tree": "b" * 40,
        "contract_version": "fpms.demo-v6-ui-parity/v1",
        "bundle_manifest_sha256": "c" * 64,
        "authority_sha256": "d" * 64,
        "allowed_differences": [
            "run suffix",
            "UUID/autoincrement ID",
            "database/file path",
            "dynamic credential",
            "idempotency key",
            "system timestamp",
        ],
        "input_ledger": input_ledger,
        "output_ledger": output_ledger,
        "mutation_ledger": [
            {
                "stage": "01",
                "action_id": "stage-01-create-customer",
                "method": "POST",
                "path": "/api/v1/clients",
                "status": 201,
            }
        ],
        "screenshots": [
            {
                "stage": f"{stage:02d}",
                "path": f"stage-{stage:02d}.png",
                "sha256": "e" * 64,
            }
            for stage in range(1, 12)
        ],
        "network_errors": [],
        "console_errors": [],
    }


def _valid_pair() -> tuple[dict, dict]:
    return _receipt("HUMAN"), _receipt("CODEX")


def _candidate() -> dict:
    return {"commit": "a" * 40, "tree": "b" * 40, "status": "CLEAN"}


@pytest.mark.parametrize(
    ("name", "mutate"),
    [
        ("actor reuse", lambda h, c: c.__setitem__("actor", "HUMAN")),
        ("shared run", lambda h, c: c.__setitem__("run_id", h["run_id"])),
        ("shared database", lambda h, c: c.__setitem__("database_path", h["database_path"])),
        ("candidate drift", lambda h, c: c.__setitem__("candidate_commit", "f" * 40)),
        ("tree drift", lambda h, c: c.__setitem__("candidate_tree", "f" * 40)),
        ("contract drift", lambda h, c: c.__setitem__("contract_version", "wrong")),
        ("bundle drift", lambda h, c: c.__setitem__("bundle_manifest_sha256", "f" * 64)),
        ("missing field", lambda h, c: c.pop("status")),
        ("extra field", lambda h, c: c.__setitem__("unexpected", True)),
        (
            "business difference",
            lambda h, c: c["output_ledger"][0].__setitem__("normalized_value", "不同客户"),
        ),
        ("missing screenshot", lambda h, c: c.__setitem__("screenshots", [])),
        ("missing mutation", lambda h, c: c.__setitem__("mutation_ledger", [])),
        ("network error", lambda h, c: c["network_errors"].append({"url": "/failed"})),
        ("console error", lambda h, c: c["console_errors"].append({"text": "boom"})),
    ],
    ids=lambda value: value if isinstance(value, str) else None,
)
def test_comparator_rejects_named_negative_fixtures(name, mutate):
    module = _comparator_module()
    human, codex = _valid_pair()
    mutate(human, codex)

    with pytest.raises(module.ReceiptComparisonError):
        module.compare_receipts(_candidate(), copy.deepcopy(human), copy.deepcopy(codex))


def test_comparator_accepts_one_human_and_one_different_account_codex():
    module = _comparator_module()
    human, codex = _valid_pair()

    result = module.compare_receipts(_candidate(), human, codex)

    assert result["schema_id"] == "fpms.demo-v6-ui-parity/v1"
    assert result["status"] == "PASS"
    assert result["actors"] == ["HUMAN", "CODEX"]


def test_comparator_rejects_candidate_binding_drift():
    module = _comparator_module()
    human, codex = _valid_pair()
    candidate = _candidate()
    candidate["tree"] = "f" * 40

    with pytest.raises(module.ReceiptComparisonError):
        module.compare_receipts(candidate, human, codex)


@pytest.mark.parametrize(
    "mutate_both",
    [
        lambda receipt: receipt["input_ledger"].pop(),
        lambda receipt: receipt["input_ledger"].append(
            copy.deepcopy(receipt["input_ledger"][0])
        ),
        lambda receipt: receipt["input_ledger"][0].__setitem__(
            "classification", "SOURCE_BOUND"
        ),
        lambda receipt: receipt["input_ledger"][0].__setitem__(
            "normalization", "WRONG"
        ),
        lambda receipt: receipt["output_ledger"].pop(),
        lambda receipt: receipt["output_ledger"][0].__setitem__(
            "expected_rule", "wrong"
        ),
        lambda receipt: receipt["screenshots"].append(
            copy.deepcopy(receipt["screenshots"][0])
        ),
    ],
    ids=[
        "same missing input",
        "same extra input",
        "same input classification drift",
        "same input normalization drift",
        "same missing output",
        "same output rule drift",
        "same duplicate screenshot",
    ],
)
def test_comparator_rejects_equally_incomplete_or_drifted_ledgers(mutate_both):
    module = _comparator_module()
    human, codex = _valid_pair()
    mutate_both(human)
    mutate_both(codex)

    with pytest.raises(module.ReceiptComparisonError):
        module.compare_receipts(_candidate(), human, codex)
