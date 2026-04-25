from __future__ import annotations

import inspect

from handlers import wave_a


def test_tc_a_023_handler_implemented_and_scoped() -> None:
    assert not getattr(wave_a.handle_tc_a_023, "_is_skeleton", False)
    source = inspect.getsource(wave_a.handle_tc_a_023)
    assert "/commission/rules" in inspect.getsource(wave_a._ensure_commission_rule)
    assert "/commission" in source
    assert "70.0000" in inspect.getsource(wave_a._arrange_batch2_cases)


def test_tc_a_024_handler_implemented_and_scoped() -> None:
    assert not getattr(wave_a.handle_tc_a_024, "_is_skeleton", False)
    source = inspect.getsource(wave_a.handle_tc_a_024)
    assert "wait_pay=True" in source
    assert "force_settle=True" in source
    assert "_assert_commission_settleable" in source
