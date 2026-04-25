from __future__ import annotations

import inspect

from handlers import wave_a


def test_tc_a_011_handler_implemented_and_scoped() -> None:
    assert not getattr(wave_a.handle_tc_a_011, "_is_skeleton", False)
    source = inspect.getsource(wave_a.handle_tc_a_011)
    assert "/cases/batch-filing/submit" in inspect.getsource(
        wave_a._submit_batch_filing
    )
    assert "document_ids" in source
    assert "created_task_ids" in source


def test_tc_a_012_handler_implemented_and_scoped() -> None:
    assert not getattr(wave_a.handle_tc_a_012, "_is_skeleton", False)
    source = inspect.getsource(wave_a.handle_tc_a_012)
    assert "CASE_BATCH_FILING_SELECTION_REQUIRED" in source
    assert "CASE_BATCH_FILING_SUBMITTED_DATE_INVALID" in source
    assert "WAITING_RECEIPT" in source
    assert not getattr(wave_a.handle_tc_a_016, "_is_skeleton", False)
