from __future__ import annotations

import inspect

from handlers import wave_b


def test_tc_b_010_handler_implemented_and_scoped() -> None:
    assert not getattr(wave_b.handle_tc_b_010, "_is_skeleton", False)
    source = inspect.getsource(wave_b.handle_tc_b_010)
    assert "/pay-lists/from-fee-items" in source
    assert "/gov-payments" in source
    assert "SERVICE item entered official pay list" in source


def test_tc_b_011_handler_implemented_and_scoped() -> None:
    assert not getattr(wave_b.handle_tc_b_011, "_is_skeleton", False)
    source = inspect.getsource(wave_b.handle_tc_b_011)
    assert "_create_oa_bill" in source
    assert "_pay_oa_bill" in source
    assert "/receipts" in source


def test_tc_b_012_handler_implemented_and_scoped() -> None:
    assert not getattr(wave_b.handle_tc_b_012, "_is_skeleton", False)
    source = inspect.getsource(wave_b.handle_tc_b_012)
    assert "_ensure_oa_commission_rule" in source
    assert '"/commission"' in source
    assert "base_fee" in source


def test_tc_b_013_handler_implemented_and_scoped() -> None:
    assert not getattr(wave_b.handle_tc_b_013, "_is_skeleton", False)
    source = inspect.getsource(wave_b.handle_tc_b_013)
    assert "DOCUMENT_REPLY_TASK_ACTION_REQUIRED" in source
    assert "reply_task_action" in source
    assert "CANCELLED" in source


def test_only_tc_b_005_remains_skeleton_in_partial_b_wave() -> None:
    assert getattr(wave_b.handle_tc_b_005, "_is_skeleton", False)
    for handler in (
        wave_b.handle_tc_b_009,
        wave_b.handle_tc_b_010,
        wave_b.handle_tc_b_011,
        wave_b.handle_tc_b_012,
        wave_b.handle_tc_b_013,
    ):
        assert not getattr(handler, "_is_skeleton", False)
