from __future__ import annotations

import inspect

from handlers import wave_a


def test_tc_a_013_handler_implemented_and_scoped() -> None:
    assert not getattr(wave_a.handle_tc_a_013, "_is_skeleton", False)
    source = inspect.getsource(wave_a.handle_tc_a_013)
    assert "/tasks/" in source
    assert "APPLY_FEE_LIMIT" in source
    assert "base_date" in source
    assert not getattr(wave_a.handle_tc_a_014, "_is_skeleton", False)
