from __future__ import annotations

import os

import pytest

from framework.data_loader import load_wave_cases
from framework.helpers import build_case_params
from framework.router import execute_case

CASES = load_wave_cases("G0", run_id=os.getenv("FPMS_RUN_ID", "LOCAL-RUN-001"))

@pytest.mark.parametrize("case", build_case_params(CASES))
def test_wave_g0(case, runtime):
    execute_case(case, runtime)
