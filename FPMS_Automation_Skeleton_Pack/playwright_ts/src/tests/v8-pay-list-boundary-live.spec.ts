import { execFileSync } from "node:child_process";
import { resolve } from "node:path";

import { expect, test } from "@playwright/test";
import type { APIRequestContext, APIResponse } from "@playwright/test";

const apiBaseUrl = (process.env.FPMS_API_URL || "http://localhost:8000/api/v1").replace(
  /\/$/,
  "",
);

type Json = Record<string, unknown>;

type ClientRecord = {
  id: string;
};

type ApplicantRecord = {
  id: string;
  name_cn: string;
};

type CaseRecord = {
  id: string;
  case_no: string;
};

type FeeDraftRecord = {
  id: string;
};

type DocumentRecord = {
  id: string;
};

type FeeItemRecord = {
  id: string;
  fee_type: string;
};

type PayListRecord = {
  id: number;
  pay_list_no: string;
  status: string;
};

type PayListCreateResult = {
  pay_list: PayListRecord;
};

type PayListExportArtifact = {
  id: string;
  kind: string;
  status: string;
  content_sha256: string;
  official_acceptance_evidence_ref: string | null;
};

type GovPaymentRecord = {
  case_id: string;
  case_no: string | null;
  status: string;
  paid_amount: string;
  official_receipt_no: string | null;
};

type PayListDetail = {
  pay_list: PayListRecord;
  gov_payments: GovPaymentRecord[];
  export_artifacts?: PayListExportArtifact[];
  official_workbook?: Json;
};

async function login(request: APIRequestContext): Promise<string> {
  const username = process.env.FPMS_ADMIN_USERNAME || "admin";
  const password = process.env.FPMS_ADMIN_PASSWORD || "admin123";
  const response = await request.post(`${apiBaseUrl}/auth/login`, {
    data: { username, password },
  });
  const body = await response.text();
  expect(response.status(), body).toBe(200);
  return (JSON.parse(body) as { access_token: string }).access_token;
}

async function jsonResponse<T>(response: APIResponse, expectedStatus: number): Promise<T> {
  const body = await response.text();
  expect(response.status(), body).toBe(expectedStatus);
  return JSON.parse(body) as T;
}

async function getJson<T>(
  request: APIRequestContext,
  token: string,
  pathName: string,
): Promise<T> {
  return jsonResponse<T>(
    await request.get(`${apiBaseUrl}${pathName}`, {
      headers: { Authorization: `Bearer ${token}` },
    }),
    200,
  );
}

async function postJson<T>(
  request: APIRequestContext,
  token: string,
  pathName: string,
  data: unknown,
  expectedStatus: number,
): Promise<T> {
  return jsonResponse<T>(
    await request.post(`${apiBaseUrl}${pathName}`, {
      data,
      headers: { Authorization: `Bearer ${token}` },
    }),
    expectedStatus,
  );
}

function recognizeFixtureObligation(
  caseId: string,
  documentId: string,
  suffix: string,
): string {
  const script = `
import sys
from datetime import date
from decimal import Decimal
from sqlalchemy import select

from app.db.session import SessionLocal
from app.modules.auth.models import T_User
from app.modules.cases.models import CaseActivityEvent
from app.modules.fees.obligation_contracts import (
    FeeDifferenceReviewState,
    FeeDomain,
    FeeObligationLineInput,
    FeeSourceStatus,
    RecognizeFeeObligationCommand,
)
from app.modules.fees.obligation_service import recognize_obligation

case_id, document_id, suffix = sys.argv[1:4]
with SessionLocal() as transaction:
    source = transaction.scalar(
        select(CaseActivityEvent).where(
            CaseActivityEvent.case_id == case_id,
            CaseActivityEvent.activity_type == "CASE_OPENED",
        )
    )
    actor = transaction.scalar(select(T_User).where(T_User.username == "admin"))
    if source is None or actor is None:
        raise RuntimeError("V8 PayList fixture source is unavailable")
    result = recognize_obligation(
        RecognizeFeeObligationCommand(
            case_id=case_id,
            source_activity_id=source.id,
            source_document_id=document_id,
            fee_domain=FeeDomain.GOV,
            obligation_type="PATENT_APPLICATION",
            due_date=date(2026, 8, 15),
            currency="CNY",
            source_status=FeeSourceStatus.VERIFIED,
            lines=(
                FeeObligationLineInput(
                    fee_code="V8_PAYLIST_BOUNDARY_GOV",
                    fee_name="官费清单边界测试官费",
                    fee_year_key=0,
                    official_full_amount=Decimal("900.00"),
                    reduction_ratio=Decimal("0.0000"),
                    payable_amount=Decimal("900.00"),
                    source_amount=Decimal("900.00"),
                    source_date=date(2026, 8, 9),
                    difference_review_state=FeeDifferenceReviewState.MATCHED,
                ),
            ),
            actor_id=actor.id,
            idempotency_key=f"v8-paylist-boundary:{suffix}:recognize",
            supersedes_obligation_id=None,
            supersede_reason=None,
        ),
        transaction,
    )
    transaction.commit()
    print(result.obligation.id)
`;
  return execFileSync(
    process.env.FPMS_BACKEND_PYTHON || "python3",
    ["-c", script, caseId, documentId, suffix],
    {
      cwd: resolve(process.cwd(), "../../backend"),
      encoding: "utf8",
      env: process.env,
    },
  ).trim();
}

test("real PayList export preserves internal, official, and payment boundaries", async ({
  page,
  request,
}) => {
  const token = await login(request);
  const suffix = `V8PL${Date.now()}`;

  const client = await postJson<ClientRecord>(
    request,
    token,
    "/clients",
    {
      client_code: suffix,
      name_cn: `官费清单边界客户-${suffix}`,
      client_type: "企业客户",
      default_currency: "CNY",
      is_active: true,
    },
    201,
  );
  const applicant = await postJson<ApplicantRecord>(
    request,
    token,
    "/applicants",
    {
      code: `${suffix}-AP`,
      name_cn: `官费清单边界申请人-${suffix}`,
      applicant_type: "ENTITY",
      is_active: true,
    },
    201,
  );
  const caseRecord = await postJson<CaseRecord>(
    request,
    token,
    "/cases",
    {
      case_no: `${suffix}-CASE`,
      case_type: "NORMAL",
      patent_category: "INV",
      flow_dir: "CN_DOMESTIC",
      client_id: client.id,
      title_cn: `官费清单边界测试案件-${suffix}`,
      recv_date: "2026-08-09",
      claim_count: 10,
      fee_reduction: "0",
      applicants: [
        {
          seq: 1,
          is_first: true,
          applicant_id: applicant.id,
          name_cn: applicant.name_cn,
        },
      ],
    },
    201,
  );
  const sourceDocument = await postJson<DocumentRecord>(
    request,
    token,
    "/documents",
    {
      case_id: caseRecord.id,
      doc_template_id: null,
      direction: "IN",
      doc_date: "2026-08-09",
      title: `官费清单边界核验来源-${suffix}`,
    },
    201,
  );
  const obligationId = recognizeFixtureObligation(caseRecord.id, sourceDocument.id, suffix);
  await postJson<Json>(
    request,
    token,
    `/fees/obligations/${obligationId}/instruction`,
    {
      instruction: "PAY",
      idempotency_key: `v8-paylist-boundary:${suffix}:instruction`,
    },
    200,
  );
  const draft = await postJson<FeeDraftRecord>(
    request,
    token,
    "/fees/drafts",
    {
      case_id: caseRecord.id,
      client_id: client.id,
      draft_type: "GENERIC",
      currency: "CNY",
      obligation_id: obligationId,
    },
    201,
  );
  const items = await getJson<FeeItemRecord[]>(
    request,
    token,
    `/fees/drafts/${draft.id}/items`,
  );
  const governmentItems = items.filter((item) => item.fee_type === "GOV");
  expect(governmentItems.length).toBeGreaterThan(0);

  const created = await postJson<PayListCreateResult>(
    request,
    token,
    "/pay-lists/from-fee-items",
    {
      fee_item_ids: governmentItems.map((item) => item.id),
      planned_pay_date: "2026-08-15",
      remark: `V8 PayList boundary ${suffix}`,
    },
    200,
  );
  const before = await getJson<PayListDetail>(
    request,
    token,
    `/pay-lists/${created.pay_list.id}`,
  );
  expect(before.pay_list.status).toBe("DRAFT");
  expect(before.gov_payments.length).toBe(governmentItems.length);
  expect(before.export_artifacts).toBeUndefined();
  expect(before.official_workbook).toBeUndefined();

  await page.addInitScript((value) => {
    window.localStorage.setItem("fpms_token", value);
  }, token);
  await page.goto(`/fee-management/pay-lists/${created.pay_list.id}`, {
    waitUntil: "domcontentloaded",
  });
  await expect(page.getByRole("heading", { name: "官费清单详情" })).toBeVisible();
  await expect(page.getByText("当前没有内部导出产物")).toBeVisible();
  await expect(page.getByText("官方工作簿门禁尚未开放")).toBeVisible();
  await expect(page.getByText("当前没有官方凭证")).toBeVisible();
  await expect(page.getByText(caseRecord.case_no).first()).toBeVisible();

  const downloadPromise = page.waitForEvent("download");
  await page.getByRole("button", { name: "导出清单" }).click();
  const download = await downloadPromise;
  expect(download.suggestedFilename()).toContain(created.pay_list.pay_list_no);
  await expect(page.getByText("官费清单已开始导出。")).toBeVisible();

  const after = await getJson<PayListDetail>(
    request,
    token,
    `/pay-lists/${created.pay_list.id}`,
  );
  const internalArtifacts = (after.export_artifacts || []).filter(
    (artifact) => artifact.kind === "INTERNAL_XLSX",
  );
  const officialEvidence = (after.export_artifacts || []).filter(
    (artifact) => artifact.kind === "OFFICIAL_XLSM",
  );

  expect(after.pay_list.status).toBe("DRAFT");
  expect(internalArtifacts).toHaveLength(1);
  expect(internalArtifacts[0].status).toBe("GENERATED");
  expect(internalArtifacts[0].content_sha256).toMatch(/^[0-9a-f]{64}$/);
  expect(after.official_workbook).toBeUndefined();
  expect(officialEvidence).toEqual([]);
  expect(after.gov_payments).toEqual(before.gov_payments);

  await page.getByRole("button", { name: "刷新" }).click();
  await expect(page.getByText(internalArtifacts[0].content_sha256)).toBeVisible();
  await expect(page.getByText("官方工作簿门禁尚未开放")).toBeVisible();
  await expect(page.getByText("当前没有官方凭证")).toBeVisible();
  await expect(page.getByText(caseRecord.case_no).first()).toBeVisible();
  await expect(page.getByText("已计划").first()).toBeVisible();
});
