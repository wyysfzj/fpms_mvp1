from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CATALOG_PATH = ROOT / "docs/product/v8/catalog.frozen.json"
LEDGER_PATH = ROOT / "docs/product/v8/coverage-ledger.json"
MATRIX_PATH = ROOT / "docs/product/v8/inherited-regression-matrix.json"
STORY_PATH = ROOT / "docs/product/v8/stories/V8-INHERITED-REGRESSION-MATRIX-CLOSE.md"
CHECKER_PATH = ROOT / "scripts/v8_lean_coverage_check.py"
FOUNDATION_CONTRACT_PATH = (
    ROOT / "backend/tests/test_v8_foundation_inherited_regression_matrix_contract.py"
)

ROW199_ID = "FPMS-V8-FULL-MANIFEST-ACTIVATION-20260712-01"
ROW278_ID = "FPMS-V8-OFFICIAL-WORKBOOK-REAL-UI-E2E-20260712-01"
ROW281_ID = "FPMS-V8-INHERITED-REGRESSION-MATRIX-20260712-01"
STORY_ID = "V8-FULL-INHERITED-REGRESSION-MATRIX-CURRENT-ADOPTION"
REVIEW_REF = (
    "docs/product/v8/reviews/"
    "V8-INHERITED-REGRESSION-MATRIX-CURRENT-ADOPTION.md"
)
ROW281_CANDIDATE_SHA = "2e32394ad356c7a743b010e75306a7b1ceba0ce1"
ROW281_ADOPTION_SHA = "cf81ba4"
CANDIDATE_PATHS = [
    "backend/tests/test_addgap_document_create_atomicity.py",
    "backend/tests/test_addgap_document_deadline_create_api.py",
    "backend/tests/test_addgap_document_deadline_impact_preview.py",
    "backend/tests/test_addgap_document_deadline_read_projection.py",
    "backend/tests/test_addgap_document_deadline_update_api.py",
    "backend/tests/test_addgap_document_wizard_deadline_backend.py",
    "backend/tests/test_addgap_filing_ensure_service.py",
    "backend/tests/test_addgap_filing_resolve_api.py",
    "backend/tests/test_addgap_grant_auto_draft_gate.py",
    "backend/tests/test_addgap_grant_preview_no_auto_draft.py",
    "backend/tests/test_addgap_legacy_deadline_task_sync.py",
    "backend/tests/test_addgap_notice_catalog_reference_gate.py",
    "backend/tests/test_addgap_notice_grant_activation.py",
    "backend/tests/test_addgap_notice_oa_acceptance_activation.py",
    "backend/tests/test_addgap_oa_alias_reply_validation.py",
    "backend/tests/test_addgap_oa_deadline_fail_closed.py",
    "backend/tests/test_addgap_oa_out_keeps_task_open.py",
    "backend/tests/test_b2_reply_chain.py",
    "backend/tests/test_b3_fee_linking.py",
    "backend/tests/test_b_official_due_date_task_generation.py",
    "backend/tests/test_case_missing_fields_crud.py",
    "backend/tests/test_document_generated_attachment_persist.py",
    "backend/tests/test_document_specific_search_api.py",
    "backend/tests/test_document_wizard_task_preview.py",
    "backend/tests/test_grant_fee_draft_linkage_api.py",
    "backend/tests/test_grant_fee_notice_document_api.py",
    "backend/tests/test_grant_fee_notice_task_creation.py",
    "backend/tests/test_grant_fee_state_machine_api.py",
    "backend/tests/test_grant_fee_worklist_api.py",
    "backend/tests/test_spec_alignment_e2e.py",
    "backend/tests/test_task_template.py",
    "backend/tests/test_v8_future_annuity_exception_carrier_schema.py",
    "backend/tests/test_v8_future_annuity_reduction_lineage_carrier.py",
    "backend/tests/test_v8_grant_evidence_source_carrier_schema.py",
    "backend/tests/test_v8_grant_manual_review_role_carrier_schema.py",
    "backend/tests/test_v8_grant_official_copy_verification_carrier_schema.py",
    "backend/tests/test_v8_grant_review_gate_manifest_contract.py",
    "backend/tests/test_v8_grant_source_gate_manifest_contract.py",
    "backend/tests/test_v8_input_activation_decoupling_contract.py",
    "backend/tests/test_v8_lifecycle_evidence_kind_capacity.py",
    "backend/tests/test_v8_official_rate_book_schema.py",
    "backend/tests/test_v8_overlay_warning_conflict_migration.py",
    "backend/tests/test_v8_pay_list_export_artifact_schema.py",
    "backend/tests/test_v8_payment_workbook_input_version.py",
    "tasks/postdemo/v8/FPMS-V8-CURRENT-HEAD-MIGRATION-TEST-ALIGNMENT-20260813-01.md",
    "tasks/postdemo/v8/FPMS-V8-CURRENT-TASK-HASH-TEST-ALIGNMENT-20260813-01.md",
    "tasks/postdemo/v8/FPMS-V8-INHERITED-CASE-CREATE-INPUT-TEST-ALIGNMENT-20260813-01.md",
    "tasks/postdemo/v8/FPMS-V8-INHERITED-DECLARED-CASE-CREATE-INPUT-TEST-ALIGNMENT-20260813-01.md",
    "tasks/postdemo/v8/FPMS-V8-INHERITED-FILING-PREPARATION-TEST-ALIGNMENT-20260813-01.md",
    "tasks/postdemo/v8/FPMS-V8-INHERITED-GRANT-LIFECYCLE-TEST-ALIGNMENT-20260813-01.md",
    "tasks/postdemo/v8/FPMS-V8-INHERITED-NOTICE-SEED-TEST-ALIGNMENT-20260813-01.md",
    "tasks/postdemo/v8/FPMS-V8-INHERITED-OA-REPLY-PROJECTION-TEST-ALIGNMENT-20260813-01.md",
    "tasks/postdemo/v8/FPMS-V8-INHERITED-REGRESSION-MATRIX-20260712-01.md",
    "tasks/postdemo/v8/FPMS-V8-INHERITED-REGRESSION-MATRIX-CLOSE-20260813-01.md",
    "backend/tests/test_v8_inherited_regression_matrix_contract.py",
    "docs/product/v8/inherited-regression-matrix.json",
    "docs/product/v8/stories/V8-INHERITED-REGRESSION-MATRIX-CLOSE.md",
    "FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-format-letter-in-source-ui.spec.ts",
    "FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-case-detail-gates-warnings.spec.ts",
    "tasks/postdemo/v8/FPMS-V8-INHERITED-FORMAT-LETTER-ERROR-LOCATOR-TEST-ALIGNMENT-20260813-01.md",
    "tasks/postdemo/v8/FPMS-V8-INHERITED-OVERLAY-READ-COUNT-TEST-ALIGNMENT-20260813-01.md",
    "scripts/run_v8_playwright_mock_isolated.py",
    "scripts/run_v8_lifecycle_overlay_live_isolated.py",
]

EXPECTED_COMMAND_SHA256 = {
    "backend_tasks01_70": "fdf2035825aea26c56e7d3830bca449418aadc3bf800255e3d13818cac04e703",
    "backend_current_v8": "a6dcab940c3877585809583e17d30c614e9feec70f88fcb9e19b65419b599c43",
    "backend_declared_nonoverlap": "75a67fca63743a286108dbb5a39280a849e79aa1b112332f69c7dad82d4bd119",
    "full_successor_contracts": "02ce2b4047c9482aa69e43ea98075a29003380beb5f21d37682e22d69a88b6b7",
    "lean_governance_contract": "4518d87c582e26b78f26a7e551b0b9ed2df5d69c2668c019a4c02ac1339c4865",
    "frontend_typecheck": "7ba6caf345c7a61a919ae6cafa1fbe8f1732d9ed757d4ba619ed3727764f1bda",
    "frontend_contracts": "330cdc03e0dcec09c8b0e0460553fc58c1467995d44fd978a6eaf941417d26d6",
    "playwright_tasks01_70_mock": "8093c4d346d309dfd0360db6f2fd83c918bad3181469e67add190a8e2ebfd03a",
    "playwright_declared_primary": "b36611be6cf6be0bf1de43768076bdaf888c12951901d9b0b91816315c10d326",
    "playwright_lifecycle_live": "dffe792f381cdbca981bf715ea4692e4e60f75589bada384f5f5deb2dc001c50",
    "playwright_workbook_live": "155a54a11c9b6db4a168377837e9ab3a8b6b22adfde343f7ed48b191cdd41692",
    "focused_contract": "89848a5f77160c10c462267b0cfbe8c5c9b9c85c5f188b3785c2c372bbfb3747",
}


def _load_checker():
    spec = importlib.util.spec_from_file_location("v8_lean_coverage_check", CHECKER_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_foundation_contract():
    spec = importlib.util.spec_from_file_location(
        "v8_foundation_inherited_regression_matrix_contract",
        FOUNDATION_CONTRACT_PATH,
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _dependency_sha256(task_ids: list[str]) -> str:
    payload = json.dumps(task_ids, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


def _path_set_sha256(paths: list[str]) -> str:
    payload = json.dumps(paths, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


def _unresolved_ordinals(ledger: dict[str, object]) -> list[int]:
    return [
        ordinal
        for ordinal, row in enumerate(ledger["rows"], start=1)
        if row["disposition"] not in {"CURRENT_VERIFIED", "SUPERSEDED_BY_STORY"}
    ]


def _ordered_unique(values: list[str]) -> list[str]:
    return list(dict.fromkeys(values))


def test_matrix_is_exactly_derived_from_the_frozen_full_dependencies() -> None:
    catalog = json.loads(CATALOG_PATH.read_text())
    ledger = json.loads(LEDGER_PATH.read_text())
    matrix = json.loads(MATRIX_PATH.read_text())
    tasks = catalog["tasks"]
    by_id = {task["task_id"]: task for task in tasks}
    row281 = tasks[280]

    assert len(tasks) == 283
    assert [task["ordinal"] for task in tasks] == list(range(1, 284))
    assert row281["task_id"] == ROW281_ID
    effective_dependencies = _ordered_unique([*row281["depends_on"], ROW278_ID])
    assert len(row281["depends_on"]) == 242
    assert len(effective_dependencies) == 243
    assert effective_dependencies[-1] == ROW278_ID
    assert matrix["effective_dependency_count"] == len(effective_dependencies)
    assert matrix["effective_dependency_sha256"] == _dependency_sha256(
        effective_dependencies
    )

    primary_paths = _ordered_unique(
        [
            path
            for task_id in effective_dependencies
            for path in by_id[task_id]["primary_tests"]
        ]
    )
    regression_paths = _ordered_unique(
        [
            path
            for task_id in effective_dependencies
            for path in by_id[task_id]["regression_inputs"]
        ]
    )
    expected_backend = sorted(
        path for path in regression_paths if path.startswith("backend/")
    )
    expected_playwright = sorted(
        path
        for path in regression_paths
        if path.startswith("FPMS_Automation_Skeleton_Pack/")
    )
    expected_frontend = sorted(
        path for path in regression_paths if path.startswith("frontend/")
    )
    assert matrix["targeted_regressions"] == {
        "backend": {
            "count": len(expected_backend),
            "paths_sha256": _path_set_sha256(expected_backend),
        },
        "frontend": {
            "count": len(expected_frontend),
            "paths_sha256": _path_set_sha256(expected_frontend),
        },
        "playwright": {
            "count": len(expected_playwright),
            "paths_sha256": _path_set_sha256(expected_playwright),
        },
    }
    assert matrix["counts"]["targeted_regressions"] == len(regression_paths)
    assert matrix["counts"]["backend_targeted"] == len(expected_backend)
    assert matrix["counts"]["frontend_targeted"] == len(expected_frontend)
    assert matrix["counts"]["playwright_targeted"] == len(expected_playwright)
    assert all((ROOT / path).is_file() for path in regression_paths)
    combined_paths = sorted(_ordered_unique([*primary_paths, *regression_paths]))
    missing = [path for path in combined_paths if not (ROOT / path).is_file()]
    assert missing == ["backend/tests/test_v8_full_manifest_activation_contract.py"]
    assert matrix["declared_input_audit"] == {
        "combined": {
            "count": len(combined_paths),
            "paths_sha256": _path_set_sha256(combined_paths),
        },
        "primary": {
            "backend_python": _summary(
                path
                for path in primary_paths
                if path.startswith("backend/") and path.endswith(".py")
            ),
            "playwright": _summary(
                path
                for path in primary_paths
                if path.startswith("FPMS_Automation_Skeleton_Pack/")
            ),
            "frontend": _summary(
                path for path in primary_paths if path.startswith("frontend/")
            ),
            "fixture": _summary(path for path in primary_paths if path.endswith(".xlsm")),
        },
        "regression": {
            "backend": _summary(
                path for path in regression_paths if path.startswith("backend/")
            ),
            "playwright": _summary(
                path
                for path in regression_paths
                if path.startswith("FPMS_Automation_Skeleton_Pack/")
            ),
        },
    }
    assert matrix["row199_primary_test_substitution"] == {
        "missing_historical_path": missing[0],
        "current_paths": [
            "scripts/tests/test_v8_full_config_required_successor.py",
            "scripts/tests/test_v8_full_capability_manifest_close.py",
        ],
    }
    assert all(
        (ROOT / path).is_file()
        for path in matrix["row199_primary_test_substitution"]["current_paths"]
    )

    for task_id in effective_dependencies:
        ordinal = by_id[task_id]["ordinal"]
        assert ledger["rows"][ordinal - 1]["disposition"] in {
            "CURRENT_VERIFIED",
            "SUPERSEDED_BY_STORY",
        }
    assert ledger["rows"][198]["catalog_id"] == ROW199_ID
    assert ledger["rows"][198]["story_id"] == (
        "V8-FULL-CAPABILITY-MANIFEST-CURRENT-ADOPTION"
    )
    assert ledger["rows"][277]["catalog_id"] == ROW278_ID
    assert ledger["rows"][277]["disposition"] == "CURRENT_VERIFIED"


def _summary(paths) -> dict[str, object]:
    ordered = sorted(paths)
    return {"count": len(ordered), "paths_sha256": _path_set_sha256(ordered)}


def _tasks01_70_paths() -> dict[str, list[str]]:
    foundation = _load_foundation_contract()
    task_ids = [
        task_id
        for group in foundation.INHERITED_TASK_GROUPS.values()
        for task_id in group
    ]
    assert len(task_ids) == len(set(task_ids)) == 70
    paths = sorted(
        {
            path
            for task_id in task_ids
            for path in foundation._resolved_task_authority(task_id)["verification_paths"]
        }
    )
    return {
        "backend": [path for path in paths if path.startswith("backend/")],
        "playwright": [
            path
            for path in paths
            if path.startswith("FPMS_Automation_Skeleton_Pack/")
        ],
        "scripts": [path for path in paths if path.startswith("scripts/")],
    }


def _current_v8_backend_paths() -> list[str]:
    inherited_backend = set(_tasks01_70_paths()["backend"])
    paths = subprocess.run(
        ["git", "ls-tree", "-r", "--name-only", ROW281_CANDIDATE_SHA, "--", "backend/tests"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()
    return sorted(
        path
        for path in paths
        if Path(path).name.startswith("test_v8_")
        and Path(path).suffix == ".py"
        and Path(path).name != "test_v8_inherited_regression_matrix_contract.py"
        and path not in inherited_backend
    )


def _declared_primary_playwright_paths() -> list[str]:
    catalog = json.loads(CATALOG_PATH.read_text())
    tasks = catalog["tasks"]
    by_id = {task["task_id"]: task for task in tasks}
    row281 = tasks[280]
    effective_dependencies = _ordered_unique([*row281["depends_on"], ROW278_ID])
    return sorted(
        {
            path
            for task_id in effective_dependencies
            for path in by_id[task_id]["primary_tests"]
            if path.startswith("FPMS_Automation_Skeleton_Pack/")
        }
    )


def test_matrix_reuses_the_exact_current_tasks01_70_authority_map() -> None:
    matrix = json.loads(MATRIX_PATH.read_text())
    groups = _tasks01_70_paths()
    assert matrix["tasks01_70"] == {
        "authority_contract": str(FOUNDATION_CONTRACT_PATH.relative_to(ROOT)),
        "task_count": 70,
        "groups": {name: _summary(paths) for name, paths in groups.items()},
    }
    assert all((ROOT / path).is_file() for paths in groups.values() for path in paths)


def test_matrix_binds_the_current_v8_and_frontend_compile_surfaces() -> None:
    matrix = json.loads(MATRIX_PATH.read_text())
    expected_v8 = _current_v8_backend_paths()
    expected_contracts = sorted(
        str(path.relative_to(ROOT))
        for path in (ROOT / "frontend/src/api/contracts").glob("v8_*.contract.ts")
    )

    assert matrix["current_v8_backend"] == {
        "count": len(expected_v8),
        "paths_sha256": _path_set_sha256(expected_v8),
        "selection": (
            "backend/tests/test_v8_*.py excluding the Row281 focused contract "
            "and Tasks01-70 backend paths"
        ),
    }
    assert matrix["frontend_contracts"] == {
        "count": len(expected_contracts),
        "paths_sha256": _path_set_sha256(expected_contracts),
        "pattern": "frontend/src/api/contracts/v8_*.contract.ts",
    }
    assert matrix["counts"]["current_v8_backend"] == len(expected_v8)
    assert matrix["counts"]["frontend_contracts"] == len(expected_contracts)
    assert matrix["production_inputs"] == {
        "DG-PAYMENT-WORKBOOK:GLOBAL": "CONFIG_REQUIRED",
        "DG-SERVICE-RATE-VERSION:GLOBAL": "CONFIG_REQUIRED",
    }
    assert matrix["source_decision_status"] == {
        "DG-PAYMENT-WORKBOOK:GLOBAL": "PENDING",
        "DG-SERVICE-RATE-VERSION:GLOBAL": "PENDING",
    }
    assert matrix["production_failure"] == "409 / NO WRITE"
    assert matrix["production_activation_claimed"] is False
    primary_playwright = _declared_primary_playwright_paths()
    workbook_live = [
        "FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/"
        "v8-official-workbook-live.spec.ts"
    ]
    primary_mocked = sorted(set(primary_playwright) - set(workbook_live))
    tasks01_70_playwright = _tasks01_70_paths()["playwright"]
    lifecycle_live = [
        "FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/"
        "v8-lifecycle-overlay-live.spec.ts"
    ]
    tasks01_70_mocked = sorted(set(tasks01_70_playwright) - set(lifecycle_live))
    assert matrix["playwright_execution_audit"] == {
        "declared_primary": _summary(primary_playwright),
        "primary_mocked": _summary(primary_mocked),
        "primary_live": _summary(workbook_live),
        "tasks01_70_mock": _summary(tasks01_70_mocked),
        "tasks01_70_lifecycle_live": _summary(lifecycle_live),
    }
    assert set(primary_mocked).isdisjoint(tasks01_70_mocked)
    assert sorted([*primary_mocked, *workbook_live]) == primary_playwright


def test_matrix_records_fresh_successful_serialized_results() -> None:
    matrix = json.loads(MATRIX_PATH.read_text())
    results = matrix["results"]
    assert [result["lane"] for result in results] == [
        "backend_tasks01_70",
        "backend_current_v8",
        "backend_declared_nonoverlap",
        "full_successor_contracts",
        "lean_governance_contract",
        "frontend_typecheck",
        "frontend_contracts",
        "playwright_tasks01_70_mock",
        "playwright_declared_primary",
        "playwright_lifecycle_live",
        "playwright_workbook_live",
        "focused_contract",
    ]
    for result in results:
        assert result["status"] == "PASS"
        assert result["return_code"] == 0
        assert result["command"]
        assert result["observed"]
        assert "<" not in result["command"]
        assert not result["command"].startswith("run ")
        assert hashlib.sha256(result["command"].encode()).hexdigest() == (
            EXPECTED_COMMAND_SHA256[result["lane"]]
        )
    assert len(_declared_primary_playwright_paths()) == 21
    assert matrix["failures"] == []
    assert matrix["product_fixes"] == []

    story = STORY_PATH.read_text(encoding="utf-8")
    for result in results:
        assert f"`{result['lane']}`" in story
        assert f"`{result['observed']}`" in story
    assert "CONFIG_REQUIRED" in story
    assert "PENDING" in story
    assert "409 / NO WRITE" in story
    assert "Rows282 and 283" in story


def test_ledger_adopts_only_row281_with_reviewed_matrix_metadata() -> None:
    ledger = json.loads(
        subprocess.run(
            ["git", "show", f"{ROW281_ADOPTION_SHA}:docs/product/v8/coverage-ledger.json"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout
    )
    assert _unresolved_ordinals(ledger) == [282, 283]
    row281 = ledger["rows"][280]
    assert row281 == {
        "catalog_id": ROW281_ID,
        "phase": "deferred",
        "disposition": "CURRENT_VERIFIED",
        "story_id": STORY_ID,
        "successor_story_id": None,
        "blocker": None,
    }
    for ordinal in (282, 283):
        assert ledger["rows"][ordinal - 1]["disposition"] == "PENDING"
        assert ledger["rows"][ordinal - 1]["story_id"] is None

    story = next(item for item in ledger["stories"] if item["story_id"] == STORY_ID)
    assert story["status"] == "CURRENT_VERIFIED"
    assert story["paths"] == CANDIDATE_PATHS
    assert story["review_class"] == "PROTECTED"
    assert story["review_ref"] == REVIEW_REF
    assert story["verification_ref"] == REVIEW_REF
    assert story["pre_adoption_unresolved_rows"] == [281, 282, 283]
    assert story["post_adoption_unresolved_rows"] == [282, 283]
    assert story["production_activation_claimed"] is False

    checker = _load_checker()
    candidate_sha = story["commits"][-1]
    assert story["tree_sha256"] == checker.compute_tree_fingerprint(
        ROOT,
        candidate_sha,
        CANDIDATE_PATHS,
    )
