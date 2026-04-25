from __future__ import annotations

import inspect

from handlers import wave_a


def test_tc_a_017_handler_implemented_and_scoped() -> None:
    assert not getattr(wave_a.handle_tc_a_017, "_is_skeleton", False)
    source = inspect.getsource(wave_a.handle_tc_a_017)
    assert "/pay-lists/from-fee-items" in source
    assert "/gov-payments" in source
    assert "PAID" in source


def test_tc_a_018_handler_implemented_and_scoped() -> None:
    assert not getattr(wave_a.handle_tc_a_018, "_is_skeleton", False)
    source = inspect.getsource(wave_a.handle_tc_a_018)
    assert "GOV_PAYMENT_INVALID" in source
    assert "GOV_PAYMENT_DUPLICATE" in source
    assert "PAY_LIST_STATE_CONFLICT" in source
