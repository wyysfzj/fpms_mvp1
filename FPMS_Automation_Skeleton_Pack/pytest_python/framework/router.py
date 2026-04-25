from __future__ import annotations

import pytest

from framework.runtime import RuntimeContext
from framework.models import BoundaryCase, TestCase
from handlers.wave_w0 import HANDLERS as w0_handlers
from handlers.wave_a import HANDLERS as a_handlers
from handlers.wave_b import HANDLERS as b_handlers
from handlers.wave_c import HANDLERS as c_handlers
from handlers.wave_g0 import HANDLERS as g0_handlers
from handlers.wave_d import HANDLERS as d_handlers
from handlers.wave_e import HANDLERS as e_handlers
from handlers.wave_f import HANDLERS as f_handlers
from handlers.wave_g import HANDLERS as g_handlers
from handlers.wave_h import HANDLERS as h_handlers
from handlers.wave_x import HANDLERS as x_handlers
from handlers.boundary import HANDLERS as boundary_handlers

ALL_HANDLERS = {
    **w0_handlers,
    **a_handlers,
    **b_handlers,
    **c_handlers,
    **g0_handlers,
    **d_handlers,
    **e_handlers,
    **f_handlers,
    **g_handlers,
    **h_handlers,
    **x_handlers,
    **boundary_handlers,
}


def execute_case(case: TestCase, runtime: RuntimeContext) -> None:
    handler = ALL_HANDLERS.get(case.id)
    if handler is None or getattr(handler, "_is_skeleton", False):
        pytest.skip(f"Skeleton only: {case.id} | {case.topic}")
    handler(runtime, case)


def execute_boundary_case(case: BoundaryCase, runtime: RuntimeContext) -> None:
    handler = ALL_HANDLERS.get(case.id)
    if handler is None or getattr(handler, "_is_skeleton", False):
        pytest.skip(f"Boundary skeleton only: {case.id} | {case.object}")
    handler(runtime, case)
