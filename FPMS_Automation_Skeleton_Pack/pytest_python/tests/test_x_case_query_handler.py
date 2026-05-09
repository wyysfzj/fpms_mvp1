from __future__ import annotations

import inspect

from handlers import wave_x


def test_tc_x_001_handler_implemented_and_scoped() -> None:
    assert not getattr(wave_x.handle_tc_x_001, "_is_skeleton", False)
    source = inspect.getsource(wave_x.handle_tc_x_001)
    assert "_ensure_x_query_case" in source
    assert "_assert_case_query_hit" in source
    assert "_assert_case_export_hit" in source
    assert '"/cases/{case_id}"' in source
    assert '"/cases/export"' in inspect.getsource(wave_x._assert_case_export_hit)
    assert "case_no" in source
    assert "app_no" in source
    assert "filing_date_from" in source
    assert "filing_date_to" in source
    assert "CN_DOMESTIC" in source


def test_tc_x_001_helper_creates_deterministic_query_data() -> None:
    source = inspect.getsource(wave_x._ensure_x_query_case)
    assert '"/cases"' in source
    assert 'unique_code("CASE-X"' in source
    assert 'unique_code("APP-X"' in source
    assert '"case_type": "NORMAL"' in source
    assert '"patent_category": "INV"' in source


def test_tc_x_004_handler_implemented_and_scoped() -> None:
    assert not getattr(wave_x.handle_tc_x_004, "_is_skeleton", False)
    source = inspect.getsource(wave_x.handle_tc_x_004)
    assert "_ensure_x_case_receipt" in source
    assert "_ensure_x_gov_payment" in source
    assert "_assert_fee_overview_case_receipt_hit" in source
    assert "_assert_fee_overview_gov_payment_hit" in source
    assert "receipt_date_from" in source
    assert "paid_date_from" in source


def test_tc_x_004_helpers_cover_both_fee_overview_endpoints() -> None:
    case_receipt_source = inspect.getsource(wave_x._ensure_x_case_receipt)
    gov_payment_source = inspect.getsource(wave_x._ensure_x_gov_payment)
    assert '"/fee-overview/case-receipts"' in case_receipt_source
    assert '"/case-receipts"' in case_receipt_source
    assert '"/fee-overview/gov-payments"' in gov_payment_source
    assert '"/pay-lists/from-fee-items"' in gov_payment_source
    assert '"/gov-payments"' in gov_payment_source


def test_tc_x_005_handler_implemented_and_scoped() -> None:
    assert not getattr(wave_x.handle_tc_x_005, "_is_skeleton", False)
    source = inspect.getsource(wave_x.handle_tc_x_005)
    assert "APPLY_FEE_LIMIT" in source
    assert '"/tasks/special/search/export"' in source
    assert '"/tasks/special/search/print"' in source
    assert "_assert_special_search_hit" in source
    assert "EXAM_REQUEST_LIMIT" not in source


def test_tc_x_005_helpers_create_apply_fee_special_search_data() -> None:
    template_source = inspect.getsource(wave_x._ensure_x_task_template)
    task_source = inspect.getsource(wave_x._ensure_x_special_search_task)
    assert '"/task-templates"' in template_source
    assert '"task_template_id": task_template_id' in task_source
    assert '"/tasks"' in task_source
    assert "date.today().isoformat()" in task_source


def test_tc_x_006_handler_implemented_and_scoped() -> None:
    assert not getattr(wave_x.handle_tc_x_006, "_is_skeleton", False)
    source = inspect.getsource(wave_x.handle_tc_x_006)
    assert "EXAM_REQUEST_LIMIT" in source
    assert '"/tasks/special/search/export"' in source
    assert '"/tasks/special/search/print"' in source
    assert "_assert_special_search_hit" in source
    assert "APPLY_FEE_LIMIT" not in source


def test_tc_x_006_uses_exam_request_case_data() -> None:
    source = inspect.getsource(wave_x.handle_tc_x_006)
    assert '"has_exam_request": False' in source
    assert 'suffix="006"' in source
    assert "X6 实审请求时限任务" in source


def test_tc_x_017_handler_implemented_and_scoped() -> None:
    assert not getattr(wave_x.handle_tc_x_017, "_is_skeleton", False)
    source = inspect.getsource(wave_x.handle_tc_x_017)
    assert '"/tasks/today"' in source
    assert '"/tasks/export"' in source
    assert '"/tasks/print"' in source
    assert '"worker"' in source
    assert '"supervisor"' in source


def test_tc_x_017_helpers_create_today_task_for_current_user() -> None:
    task_source = inspect.getsource(wave_x._ensure_x_today_task)
    assert '"/tasks"' in task_source
    assert '"worker_id": user_id' in task_source
    assert '"supervisor_id": user_id' in task_source
    assert "date.today().isoformat()" in task_source


def test_other_x_handlers_remain_skeleton() -> None:
    assert getattr(wave_x.handle_tc_x_002, "_is_skeleton", False)
    assert getattr(wave_x.handle_tc_x_016, "_is_skeleton", False)
    assert getattr(wave_x.handle_tc_x_027, "_is_skeleton", False)
