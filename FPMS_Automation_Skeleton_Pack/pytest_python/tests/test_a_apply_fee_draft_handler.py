from __future__ import annotations

import inspect

from handlers import wave_a


def test_tc_a_015_handler_implemented_and_scoped() -> None:
    assert not getattr(wave_a.handle_tc_a_015, "_is_skeleton", False)
    source = inspect.getsource(wave_a.handle_tc_a_015)
    assert "/fees/drafts/apply-fee/generate" in inspect.getsource(
        wave_a._generate_apply_fee_draft
    )
    assert "APPLY_EXCESS_CLAIM" in source
    assert "total_service" in inspect.getsource(wave_a._assert_apply_fee_draft_totals)


def test_tc_a_016_handler_implemented_and_scoped() -> None:
    assert not getattr(wave_a.handle_tc_a_016, "_is_skeleton", False)
    source = inspect.getsource(wave_a.handle_tc_a_016)
    assert "FEE_DRAFT_CURRENCY_REQUIRED" in source
    assert "FEE_ITEM_AMOUNT_INVALID" in source
    assert "FEE_DRAFT_ITEM_REQUIRED" in source
