from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

SCHEMA_ID = "fpms.demo-v6-ui-parity/v1"
ROOT = Path(__file__).resolve().parents[1]
CONTRACT = (
    ROOT
    / "FPMS_Automation_Skeleton_Pack"
    / "data"
    / "testcases"
    / "demo_v6_ui_parity_v1.json"
)
ALLOWED_DIFFERENCES = [
    "run suffix",
    "UUID/autoincrement ID",
    "database/file path",
    "dynamic credential",
    "idempotency key",
    "system timestamp",
]
RECEIPT_FIELDS = frozenset(
    {
        "schema_id",
        "status",
        "actor",
        "account_id",
        "run_id",
        "run_root",
        "database_path",
        "candidate_commit",
        "candidate_tree",
        "contract_version",
        "bundle_manifest_sha256",
        "authority_sha256",
        "allowed_differences",
        "input_ledger",
        "output_ledger",
        "mutation_ledger",
        "screenshots",
        "network_errors",
        "console_errors",
    }
)


class ReceiptComparisonError(ValueError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ReceiptComparisonError(message)


def _canonical_ledgers() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    _require(contract.get("schema_id") == SCHEMA_ID, "canonical contract schema drift")
    inputs = [
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
    outputs = [
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
    return inputs, outputs


def _validate_receipt(receipt: dict[str, Any]) -> None:
    _require(set(receipt) == RECEIPT_FIELDS, "receipt fields differ from strict v1 schema")
    _require(receipt["schema_id"] == SCHEMA_ID, "schema_id drift")
    _require(receipt["contract_version"] == SCHEMA_ID, "contract version drift")
    _require(receipt["status"] == "PASS", "receipt is not PASS")
    _require(receipt["actor"] in {"HUMAN", "CODEX"}, "unsupported actor")
    _require(receipt["allowed_differences"] == ALLOWED_DIFFERENCES, "allowed differences drift")
    _require(not receipt["network_errors"], "network errors are present")
    _require(not receipt["console_errors"], "console errors are present")

    expected_inputs, expected_outputs = _canonical_ledgers()
    _require(
        receipt["input_ledger"] == expected_inputs,
        "input ledger is incomplete or differs from the canonical field contract",
    )
    _require(
        receipt["output_ledger"] == expected_outputs,
        "output ledger is incomplete or differs from the canonical field contract",
    )

    mutations = [row.get("action_id") for row in receipt["mutation_ledger"]]
    _require(mutations and len(mutations) == len(set(mutations)), "mutation correlation is missing or duplicated")

    stages = {stage["stage"] for stage in json.loads(CONTRACT.read_text(encoding="utf-8"))["stages"]}
    screenshot_stages = {row.get("stage") for row in receipt["screenshots"]}
    _require(
        stages == screenshot_stages and len(receipt["screenshots"]) == len(stages),
        "stage screenshot correlation is incomplete or duplicated",
    )
    _require(
        all(row.get("path") and row.get("sha256") for row in receipt["screenshots"]),
        "screenshot identity is incomplete",
    )


def compare_receipts(
    candidate: dict[str, Any], human: dict[str, Any], codex: dict[str, Any]
) -> dict[str, Any]:
    _validate_receipt(human)
    _validate_receipt(codex)
    _require([human["actor"], codex["actor"]] == ["HUMAN", "CODEX"], "expected HUMAN then CODEX")
    _require(human["account_id"] != codex["account_id"], "actors reused one account")
    _require(human["run_id"] != codex["run_id"], "actors reused one run")
    _require(human["run_root"] != codex["run_root"], "actors reused one run root")
    _require(human["database_path"] != codex["database_path"], "actors reused one database")
    _require(candidate.get("status") == "CLEAN", "candidate is not clean")
    _require(candidate.get("commit") == human["candidate_commit"], "candidate commit drift")
    _require(candidate.get("tree") == human["candidate_tree"], "candidate tree drift")

    for field in (
        "candidate_commit",
        "candidate_tree",
        "contract_version",
        "bundle_manifest_sha256",
        "authority_sha256",
        "allowed_differences",
        "input_ledger",
        "output_ledger",
        "mutation_ledger",
    ):
        _require(human[field] == codex[field], f"non-whitelisted difference: {field}")

    return {"schema_id": SCHEMA_ID, "status": "PASS", "actors": ["HUMAN", "CODEX"]}


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare frozen FPMS V6 HUMAN and CODEX UI receipts")
    parser.add_argument("--candidate", required=True, type=Path)
    parser.add_argument("--human", required=True, type=Path)
    parser.add_argument("--codex", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    result = compare_receipts(
        json.loads(args.candidate.read_text(encoding="utf-8")),
        json.loads(args.human.read_text(encoding="utf-8")),
        json.loads(args.codex.read_text(encoding="utf-8")),
    )
    args.output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
