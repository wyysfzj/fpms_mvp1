from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = (
    ROOT
    / "FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests"
    / "demo-integrated-a.live-backend.spec.ts"
)


def _source() -> str:
    return SPEC.read_text(encoding="utf-8")


def test_ia07_to_ia09_are_real_and_next_red_is_ia10() -> None:
    source = _source()
    assert "rejectInvalidReceipts(_caseId" not in source
    assert "archiveOa1(_packageId" not in source
    assert "completeOa2(_caseId" not in source
    assert "return this.red('IA-07')" not in source
    assert "return this.red('IA-08')" not in source
    assert "return this.red('IA-09')" not in source
    assert "return this.red('IA-10')" in source
    for token in (
        "OFFICIAL_WORK_PACKAGE_RECEIPT_CASE_MISMATCH",
        "OA_RECEIPT_ATTACHMENT_SOURCE_INVALID",
        "OFFICIAL_NOTICE_005",
        "OA_NOTICE_2",
        "OA_RECEIPT_2",
        "expect(recorded.body.oa_sequence).toBe(2)",
        "task6-checkpoints.json",
        "FPMS_DEMO_INTEGRATED_OA_REPLY_OUTPUT_JSON",
        "SYNTHETIC_TEST_OUTPUT",
    ):
        assert token in source


def test_second_oa_contract_keeps_exact_identity_and_projection_assertions() -> None:
    source = _source()
    for token in (
        "sequence1_reuse_no_write",
        "incomplete_deadline_no_write",
        "changed_deadline_no_write",
        "x.oa1_history_after).toEqual(x.oa1_history_before)",
        "x.closed_task_ids).toEqual([x.task_id])",
        "PROSECUTION_MANAGEMENT",
        "SUBSTANTIVE_EXAMINATION",
        "APPLICATION_PENDING",
        "legacy_display).toBe('SUB_EXAM')",
        "expect(evidenceRoleMap.size).toBe(10)",
    ):
        assert token in source


def test_cross_case_negative_fixture_does_not_reuse_full_case_initialization() -> None:
    source = _source()
    method = source.split("async rejectInvalidReceipts", 1)[1].split(
        "async archiveOa1", 1
    )[0]
    assert "this.createCase(" not in method
    assert "const auxiliaryResponse = this.operatorPage.waitForResponse" in method
    assert "const auxiliary = await (await auxiliaryResponse).json()" in method


def test_initial_finance_counts_use_visible_empty_lists_not_response_bodies() -> None:
    source = _source()
    method = source.split("async createCase", 1)[1].split("async inspectCatalog", 1)[0]
    assert "billPagePromise" not in method
    assert "paymentPagePromise" not in method
    assert "offsetPagePromise" not in method
    for token in (
        "getByText('暂无账单'",
        "getByText('暂无预收款记录'",
        "getByText('暂无数据'",
        "locator('.el-table__row').count()",
    ):
        assert token in method
