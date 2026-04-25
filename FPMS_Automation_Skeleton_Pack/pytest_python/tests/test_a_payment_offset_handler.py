from __future__ import annotations

import inspect

from handlers import wave_a


def test_tc_a_021_handler_implemented_and_scoped() -> None:
    assert not getattr(wave_a.handle_tc_a_021, "_is_skeleton", False)
    source = inspect.getsource(wave_a.handle_tc_a_021)
    assert "/payments" in source
    assert "/offsets" in source
    assert "/receipts" in source


def test_tc_a_022_handler_implemented_and_scoped() -> None:
    assert not getattr(wave_a.handle_tc_a_022, "_is_skeleton", False)
    source = inspect.getsource(wave_a.handle_tc_a_022)
    assert "PAYMENT_AMOUNT_INVALID" in source
    assert "PAYMENT_DATE_INVALID" in source
    assert "PAYMENT_PAY_NO_DUPLICATE" in source
    assert "OFFSET_EXCEEDS_PAYMENT_BALANCE" in source
    assert "OFFSET_EXCEEDS_BILL_BALANCE" in source
    assert "is_prepayment" in source
    assert not getattr(wave_a.handle_tc_a_024, "_is_skeleton", False)
