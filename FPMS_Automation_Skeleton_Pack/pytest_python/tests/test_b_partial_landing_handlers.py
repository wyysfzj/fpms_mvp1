from __future__ import annotations

import inspect

from handlers import wave_b


def test_tc_b_001_handler_implemented_and_scoped() -> None:
    assert not getattr(wave_b.handle_tc_b_001, "_is_skeleton", False)
    source = inspect.getsource(wave_b.handle_tc_b_001)
    assert "/documents/wizard/batch-create" in source
    assert "OA_IN" in source
    assert "OA1" in source


def test_tc_b_002_handler_implemented_and_scoped() -> None:
    assert not getattr(wave_b.handle_tc_b_002, "_is_skeleton", False)
    source = inspect.getsource(wave_b.handle_tc_b_002)
    assert "/documents/wizard/task-preview" in source
    assert "OfficialDueDate" in source
    assert "base_date" in source


def test_tc_b_003_handler_implemented_and_scoped() -> None:
    assert not getattr(wave_b.handle_tc_b_003, "_is_skeleton", False)
    source = inspect.getsource(wave_b.handle_tc_b_003)
    assert "DOCUMENT_OFFICIAL_DUE_DATE_INVALID" in source
    assert "DOC_TEMPLATE_NOT_FOUND" in source
    assert "missing wizard rows" in source


def test_tc_b_004_handler_implemented_and_scoped() -> None:
    assert not getattr(wave_b.handle_tc_b_004, "_is_skeleton", False)
    source = inspect.getsource(wave_b.handle_tc_b_004)
    assert '"/tasks"' in inspect.getsource(wave_b._tasks_for_case)
    assert "AUTO_CREATE_FROM_DOCUMENT" in source
    assert "OPEN" in source


def test_tc_b_006_handler_implemented_and_scoped() -> None:
    assert not getattr(wave_b.handle_tc_b_006, "_is_skeleton", False)
    source = inspect.getsource(wave_b.handle_tc_b_006)
    assert "reply_to_id" in source
    assert "reply_date" in source
    assert "status_restore" in inspect.getsource(wave_b._ensure_oa_out_doc_template)


def test_tc_b_007_handler_implemented_and_scoped() -> None:
    assert not getattr(wave_b.handle_tc_b_007, "_is_skeleton", False)
    source = inspect.getsource(wave_b.handle_tc_b_007)
    assert "REPLY_TO_CASE_MISMATCH" in source
    assert "REPLY_TO_TEMPLATE_MISMATCH" in source
    assert "REPLY_TO_DOC_NOT_FOUND" in source


def test_tc_b_008_handler_implemented_and_scoped() -> None:
    assert not getattr(wave_b.handle_tc_b_008, "_is_skeleton", False)
    source = inspect.getsource(wave_b.handle_tc_b_008)
    assert "AUTO_WRITEOFF" in source
    assert "DONE" in source
    assert "SUB_EXAM" in source


def test_tc_b_009_handler_implemented_and_scoped() -> None:
    assert not getattr(wave_b.handle_tc_b_009, "_is_skeleton", False)
    source = inspect.getsource(wave_b.handle_tc_b_009)
    assert "/documents/wizard/fee-preview" in source
    assert "OA_FEE" in inspect.getsource(wave_b._ensure_oa_fee_doc_template)
    assert "total_service" in source


def test_unlanded_b_handlers_remain_skeleton() -> None:
    assert getattr(wave_b.handle_tc_b_005, "_is_skeleton", False)
