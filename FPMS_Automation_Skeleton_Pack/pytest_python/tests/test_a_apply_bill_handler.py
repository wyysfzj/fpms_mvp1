from __future__ import annotations

import inspect

from handlers import wave_a


def test_tc_a_019_handler_implemented_and_scoped() -> None:
    assert not getattr(wave_a.handle_tc_a_019, "_is_skeleton", False)
    source = inspect.getsource(wave_a.handle_tc_a_019)
    assert "/bills/from-drafts" in inspect.getsource(wave_a._create_bill_from_draft)
    assert "UNSETTLED" in source
    assert "draft_id" in source


def test_tc_a_020_handler_implemented_and_scoped() -> None:
    assert not getattr(wave_a.handle_tc_a_020, "_is_skeleton", False)
    source = inspect.getsource(wave_a.handle_tc_a_020)
    assert "BILL_SINGLE_CLIENT_REQUIRED" in source
    assert "BILL_CURRENCY_MISMATCH" in source
    assert "BILL_ITEM_REQUIRED" in source
    assert "BILL_MANUAL_TOTAL_INVALID" in source
