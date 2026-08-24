from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _source(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def test_grant_preview_and_confirmation_use_authoritative_fields() -> None:
    types = _source("frontend/src/api/grantFees.types.ts")
    client = _source("frontend/src/api/grantFees.ts")
    page = _source("frontend/src/modules/grantFees/pages/GrantFeeTaskList.vue")

    for field in (
        "preview_digest",
        "reviewed_evidence_version_id",
        "reviewed_evidence_content_hash",
        "source_authority",
        "rate_book_version",
        "rate_book_sha256",
        "confirmed_payable_amount",
    ):
        assert field in types + client
    assert "/official-fee-preview" in client
    assert "/official-fee-confirmation" in client
    assert "候选预览，尚未形成缴费义务" in page
    assert "确认官费并生成草单" in page


def test_draft_source_facts_own_the_edit_boundary() -> None:
    types = _source("frontend/src/api/fees.types.ts")
    client = _source("frontend/src/api/fees.ts")
    detail = _source("frontend/src/modules/fees/pages/FeeDraftDetail.vue")
    table = _source("frontend/src/modules/fees/components/FeeDraftItemsTable.vue")

    for field in (
        "fee_domain",
        "source_authority",
        "source_ref",
        "source_version",
        "effective_date",
        "source_sha256",
        "activation_status",
        "adjustable",
        "adjustment_activity_id",
    ):
        assert field in types
    assert "/source-facts" in client
    assert "/demo-service-adjustment" in client
    assert "计算与来源" in detail
    assert "sourceFacts" in table
    assert "sourceFactsResolved === true" in table
    assert "canAdjustItem" in table
    assert "调整数量" in table
    assert "expected_quantity" in table
    assert "new_quantity" in table


def test_pending_official_evidence_is_not_presented_as_payment_success() -> None:
    types = _source("frontend/src/api/govPayments.types.ts")
    client = _source("frontend/src/api/govPayments.ts")
    pay_list = _source("frontend/src/modules/annuity/pages/PayListDetail.vue")
    registration = _source("frontend/src/modules/annuity/pages/GovPaymentCreate.vue")

    assert "REGISTERED_PENDING_OFFICIAL_EVIDENCE" in types
    assert "/gov-payments/demo-command" in client
    assert "/gov-payments/idempotency/" in client
    assert "已登记，待官方凭证核验" in pay_list
    assert "已登记，待官方凭证核验" in registration
    assert "official_receipt_no: null" in registration
    assert "getDemoGovPaymentCommand(payload.idempotency_key)" in client
    assert client.count("response = await post()") == 2
    assert "response.status === 202" in client
    assert "isPendingOfficialEvidence" in pay_list
    assert "result.value.fact_status === 'REGISTERED_PENDING_OFFICIAL_EVIDENCE'" in registration


def test_customer_finance_pages_distinguish_receipt_offset_and_settlement() -> None:
    billing_types = _source("frontend/src/api/billing.types.ts")
    billing_client = _source("frontend/src/api/billing.ts")
    bill = _source("frontend/src/modules/billing/pages/BillDetail.vue")
    payments = _source("frontend/src/modules/billing/pages/PaymentList.vue")
    offsets = _source("frontend/src/modules/billing/pages/OffsetList.vue")

    assert "PARTIALLY_SETTLED" in billing_types
    assert "SETTLED" in billing_types
    assert "settlementStatusText" in billing_client
    assert "部分结清" in bill
    assert "已结清" in bill
    assert "登记回款不等于账单核销" in payments
    assert "核销记录与客户回款是不同业务对象" in offsets


def test_case_summary_is_chinese_and_host_control_remains_hidden() -> None:
    lane = _source("frontend/src/modules/cases/components/FeeObligationLane.vue")
    menu = _source("frontend/src/constants/menu.ts")
    customer_pages = "\n".join(
        _source(path)
        for path in (
            "frontend/src/modules/grantFees/pages/GrantFeeTaskList.vue",
            "frontend/src/modules/fees/pages/FeeDraftDetail.vue",
            "frontend/src/modules/annuity/pages/PayListDetail.vue",
            "frontend/src/modules/billing/pages/BillDetail.vue",
            "frontend/src/modules/billing/pages/PaymentList.vue",
            "frontend/src/modules/billing/pages/OffsetList.vue",
            "frontend/src/modules/cases/components/FeeObligationLane.vue",
        )
    )

    assert "同案双轨费用概览" in lane
    assert "statusText" in lane
    assert "/demo/abc" not in menu
    assert "ABC" not in customer_pages
    assert "客户决策" not in customer_pages


def test_transport_failure_reconciles_before_one_retry() -> None:
    reconciliation = _source("frontend/src/modules/demo/command-reconcile.ts")
    host_client = _source("frontend/src/modules/demo/demo.api.ts")

    assert "retryMutation" in reconciliation
    assert "先对账，再重试一次" in reconciliation
    assert "reconcileUnknownCommand" in host_client
    assert "/payments/idempotency/" in host_client
    assert "/offsets/idempotency/" in host_client
