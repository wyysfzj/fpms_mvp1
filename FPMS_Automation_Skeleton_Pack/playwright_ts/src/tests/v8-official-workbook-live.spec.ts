import { execFileSync, spawn, type ChildProcess } from "node:child_process";
import { createHash } from "node:crypto";
import { mkdtempSync, mkdirSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";

import { expect, test } from "@playwright/test";
import type { APIRequestContext, APIResponse, Page } from "@playwright/test";

const repoRoot = resolve(process.cwd(), "../..");
const backendRoot = join(repoRoot, "backend");
const frontendRoot = join(repoRoot, "frontend");
const backendPython = join(backendRoot, ".venv", "bin", "python");
const apiBaseUrl = "http://127.0.0.1:8000/api/v1";
const liveRoot = mkdtempSync(join(tmpdir(), "fpms-row278-"));
const databasePath = join(liveRoot, "row278.db");
const storagePath = join(liveRoot, "storage");
const proofPath = join(liveRoot, "controlled-upload-proof.txt");
const templatePath = join(
  backendRoot,
  "tests",
  "fixtures",
  "v8_verified_official_payment_template.xlsm",
);
const databaseUrl = `sqlite:///${databasePath}`;
const processEnv = {
  ...process.env,
  DATABASE_URL: databaseUrl,
  FPMS_ENV: "test",
  STORAGE_DIR: storagePath,
  PYTHONPATH: backendRoot,
  NO_PROXY: "127.0.0.1,localhost",
  no_proxy: "127.0.0.1,localhost",
};

let backend: ChildProcess | undefined;
let frontend: ChildProcess | undefined;

type Json = Record<string, unknown>;
type IdRecord = { id: string };
type ApplicantRecord = IdRecord & { name_cn: string };
type CaseRecord = IdRecord & { case_no: string };
type DocumentRecord = IdRecord;
type FeeDraftRecord = IdRecord;
type FeeItemRecord = IdRecord & { fee_type: string };
type PayListCreateResult = { pay_list: { id: number; pay_list_no: string; status: string } };
type PayListDetail = {
  pay_list: { id: number; status: string };
  gov_payments: Array<{ status: string; official_receipt_no: string | null }>;
  official_workbook?: { status: string };
  export_artifacts?: Array<{
    id: string;
    status: string;
    content_sha256: string;
    official_acceptance_evidence_ref: string | null;
  }>;
};

function runBackendPython(script: string, args: string[] = []): string {
  return execFileSync(backendPython, ["-c", script, ...args], {
    cwd: backendRoot,
    encoding: "utf8",
    env: processEnv,
  }).trim();
}

async function waitForHttp(url: string): Promise<void> {
  const deadline = Date.now() + 30_000;
  while (Date.now() < deadline) {
    try {
      const response = await fetch(url);
      if (response.status > 0) return;
    } catch {
      // Process startup is intentionally polled without weakening the final assertion.
    }
    await new Promise((resolvePromise) => setTimeout(resolvePromise, 200));
  }
  throw new Error(`Timed out waiting for ${url}`);
}

function initializeControlledInput(): void {
  mkdirSync(storagePath, { recursive: true });
  writeFileSync(proofPath, "TEST_ONLY controlled upload proof for row 278\n", "utf8");
  execFileSync(join(backendRoot, ".venv", "bin", "alembic"), ["upgrade", "head"], {
    cwd: backendRoot,
    env: processEnv,
    stdio: "pipe",
  });
  execFileSync(backendPython, ["scripts/seed_dev.py"], {
    cwd: backendRoot,
    env: processEnv,
    stdio: "pipe",
  });

  const templateHash = createHash("sha256")
    .update(execFileSync("/bin/cat", [templatePath]))
    .digest("hex");
  const proofHash = createHash("sha256")
    .update(execFileSync("/bin/cat", [proofPath]))
    .digest("hex");
  const script = `
import sys
from datetime import datetime
from sqlalchemy import select
from app.db.session import SessionLocal
from app.modules.auth.models import T_User
from app.modules.annuity.official_payment_workbook_input_service import (
    RegisterWorkbookInputCommand, ReviewWorkbookInputCommand,
    ValidateWorkbookInputCommand, register_workbook_input,
    review_workbook_input, validate_workbook_input,
)
from app.core.security import get_password_hash

template_path, template_hash, proof_path, proof_hash = sys.argv[1:5]
with SessionLocal() as db:
    uploader = db.scalar(select(T_User).where(T_User.username == "admin"))
    if uploader is None:
        raise RuntimeError("admin fixture missing")
    reviewer = db.scalar(select(T_User).where(T_User.username == "row278-reviewer"))
    if reviewer is None:
        reviewer = T_User(
            username="row278-reviewer", display_name="Row 278 Reviewer",
            password_hash=get_password_hash("not-used"), is_active=True,
        )
        db.add(reviewer)
        db.flush()
    registered = register_workbook_input(db, RegisterWorkbookInputCommand(
        template_version="ROW278-TEST-ONLY",
        template_storage_path=template_path,
        expected_template_hash=template_hash,
        upload_proof_storage_path=proof_path,
        expected_upload_proof_hash=proof_hash,
        effective_from=datetime(2026, 1, 1), effective_to=None,
        source_classification="TEST_ONLY", actor_id=uploader.id,
        idempotency_key="row278-test-input", runtime_profile="test",
    ))
    validate_workbook_input(db, ValidateWorkbookInputCommand(
        version_id=registered.version_id, actor_id=uploader.id,
    ))
    review_workbook_input(db, ReviewWorkbookInputCommand(
        version_id=registered.version_id, decision="APPROVE",
        reason="row278 controlled TEST_ONLY review", actor_id=reviewer.id,
    ))
    db.commit()
`;
  runBackendPython(script, [templatePath, templateHash, proofPath, proofHash]);
}

async function jsonResponse<T>(response: APIResponse, expectedStatus: number): Promise<T> {
  const body = await response.text();
  expect(response.status(), body).toBe(expectedStatus);
  return JSON.parse(body) as T;
}

async function postJson<T>(
  request: APIRequestContext,
  token: string,
  path: string,
  data: unknown,
  expectedStatus: number,
): Promise<T> {
  return jsonResponse<T>(
    await request.post(`${apiBaseUrl}${path}`, {
      data,
      headers: { Authorization: `Bearer ${token}` },
    }),
    expectedStatus,
  );
}

async function getJson<T>(
  request: APIRequestContext,
  token: string,
  path: string,
): Promise<T> {
  return jsonResponse<T>(
    await request.get(`${apiBaseUrl}${path}`, {
      headers: { Authorization: `Bearer ${token}` },
    }),
    200,
  );
}

function recognizeFixtureObligation(caseId: string, documentId: string, suffix: string): string {
  const script = `
import sys
from datetime import date
from decimal import Decimal
from sqlalchemy import select
from app.db.session import SessionLocal
from app.modules.auth.models import T_User
from app.modules.cases.models import CaseActivityEvent
from app.modules.fees.obligation_contracts import (
    FeeDifferenceReviewState, FeeDomain, FeeObligationLineInput, FeeSourceStatus,
    RecognizeFeeObligationCommand,
)
from app.modules.fees.obligation_service import recognize_obligation

case_id, document_id, suffix = sys.argv[1:4]
with SessionLocal() as db:
    source = db.scalar(select(CaseActivityEvent).where(
        CaseActivityEvent.case_id == case_id,
        CaseActivityEvent.activity_type == "CASE_OPENED",
    ))
    actor = db.scalar(select(T_User).where(T_User.username == "admin"))
    result = recognize_obligation(RecognizeFeeObligationCommand(
        case_id=case_id, source_activity_id=source.id, source_document_id=document_id,
        fee_domain=FeeDomain.GOV, obligation_type="PATENT_APPLICATION",
        due_date=date(2026, 8, 31), currency="CNY",
        source_status=FeeSourceStatus.VERIFIED,
        lines=(FeeObligationLineInput(
            fee_code="ROW278_GOV", fee_name="第278行测试官费", fee_year_key=0,
            official_full_amount=Decimal("900.00"), reduction_ratio=Decimal("0"),
            payable_amount=Decimal("900.00"), source_amount=Decimal("900.00"),
            source_date=date(2026, 8, 13),
            difference_review_state=FeeDifferenceReviewState.MATCHED,
        ),), actor_id=actor.id, idempotency_key=f"row278:{suffix}:recognize",
        supersedes_obligation_id=None, supersede_reason=None,
    ), db)
    db.commit()
    print(result.obligation.id)
`;
  return runBackendPython(script, [caseId, documentId, suffix]);
}

function assertProductionConfigRequired(payListId: number): Json {
  const script = `
import json, sys
from datetime import datetime
from sqlalchemy import func, select
from app.core.errors import BusinessError
from app.db.session import SessionLocal
from app.modules.annuity.models import PayListExportArtifact
from app.modules.annuity.service import GenerateOfficialPaymentWorkbookCommand, generate_official_payment_workbook
from app.modules.annuity.verified_official_payment_workbook import OfficialPaymentRow

pay_list_id = int(sys.argv[1])
with SessionLocal() as db:
    before = db.scalar(select(func.count()).select_from(PayListExportArtifact))
    try:
        generate_official_payment_workbook(GenerateOfficialPaymentWorkbookCommand(
            pay_list_id=pay_list_id,
            rows=(OfficialPaymentRow(
                sequence_number=1, application_number="CN2026000278",
                business_type="发明专利", invoice_title="测试申请人有限公司",
                unified_social_credit_code="91110000TEST000278", fee_type="申请费",
                foreign_currency_amount=None, amount_cny=900, remark="production-negative",
            ),), actor_id="00000000-0000-4000-8000-000000000278",
            idempotency_key="row278-production-negative",
            generated_at=datetime(2026, 8, 13, 12, 0), runtime_profile="production",
        ), db)
        raise RuntimeError("production generation unexpectedly succeeded")
    except BusinessError as exc:
        after = db.scalar(select(func.count()).select_from(PayListExportArtifact))
        print(json.dumps({"code": exc.code, "status": exc.status_code, "before": before, "after": after}))
`;
  return JSON.parse(runBackendPython(script, [String(payListId)])) as Json;
}

function openTestOnlyUiGate(payListId: number): void {
  const script = `
import sqlite3, sys

with sqlite3.connect(sys.argv[1]) as db:
    cursor = db.execute(
        """
        UPDATE t_pay_list
        SET official_upload_template_status = 'ACTIVE',
            official_upload_template_name = 'ROW278-TEST-ONLY',
            official_upload_batch_limit = 1,
            official_pay_list_boundary_note = 'TEST_ONLY controlled UI capability gate'
        WHERE id = ?
        """,
        (int(sys.argv[2]),),
    )
    if cursor.rowcount != 1:
        raise RuntimeError("row278 PayList is missing")
`;
  runBackendPython(script, [databasePath, String(payListId)]);
}

async function fillGenerationForm(page: Page): Promise<void> {
  const panel = page.getByTestId("official-workbook-panel");
  await panel.getByTestId("official-workbook-application-number").fill("CN2026000278");
  await panel.getByTestId("official-workbook-business-type").fill("发明专利");
  await panel.getByTestId("official-workbook-invoice-title").fill("测试申请人有限公司");
  await panel.getByTestId("official-workbook-credit-code").fill("91110000TEST000278");
  await panel.getByTestId("official-workbook-fee-type").fill("申请费");
  await panel.getByTestId("official-workbook-amount-cny").fill("900");
  await panel.getByTestId("official-workbook-remark").fill("第278行真实路径");
}

test.beforeAll(async () => {
  test.setTimeout(120_000);
  initializeControlledInput();
  backend = spawn(backendPython, ["-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"], {
    cwd: backendRoot,
    env: processEnv,
    stdio: "ignore",
  });
  frontend = spawn(join(frontendRoot, "node_modules", ".bin", "vite"), ["--host", "127.0.0.1", "--port", "5173"], {
    cwd: frontendRoot,
    env: { ...processEnv, VITE_API_BASE_URL: apiBaseUrl },
    stdio: "ignore",
  });
  await Promise.all([
    waitForHttp("http://127.0.0.1:8000/docs"),
    waitForHttp("http://127.0.0.1:5173"),
  ]);
});

test.afterAll(() => {
  backend?.kill("SIGTERM");
  frontend?.kill("SIGTERM");
  rmSync(liveRoot, { recursive: true, force: true });
});

test("real workbook path keeps generated, accepted, paid and ticket facts distinct", async ({
  page,
  request,
}) => {
  test.setTimeout(120_000);
  const login = await postJson<{ access_token: string }>(
    request,
    "",
    "/auth/login",
    { username: "admin", password: "admin123" },
    200,
  );
  const token = login.access_token;
  const suffix = `ROW278${Date.now()}`;
  const client = await postJson<IdRecord>(request, token, "/clients", {
    client_code: suffix,
    name_cn: `第278行测试客户-${suffix}`,
    client_type: "企业客户",
    default_currency: "CNY",
    is_active: true,
  }, 201);
  const applicant = await postJson<ApplicantRecord>(request, token, "/applicants", {
    code: `${suffix}-AP`, name_cn: `第278行申请人-${suffix}`,
    applicant_type: "ENTITY", is_active: true,
  }, 201);
  const caseRecord = await postJson<CaseRecord>(request, token, "/cases", {
    case_no: `${suffix}-CASE`, case_type: "NORMAL", patent_category: "INV",
    flow_dir: "CN_DOMESTIC", client_id: client.id, title_cn: `第278行真实路径-${suffix}`,
    recv_date: "2026-08-13", claim_count: 10, fee_reduction: "0",
    applicants: [{ seq: 1, is_first: true, applicant_id: applicant.id, name_cn: applicant.name_cn }],
  }, 201);
  const sourceDocument = await postJson<DocumentRecord>(request, token, "/documents", {
    case_id: caseRecord.id,
    doc_template_id: null,
    direction: "IN",
    doc_date: "2026-08-13",
    title: `第278行官费来源-${suffix}`,
  }, 201);
  const obligationId = recognizeFixtureObligation(caseRecord.id, sourceDocument.id, suffix);
  await postJson<Json>(request, token, `/fees/obligations/${obligationId}/instruction`, {
    instruction: "PAY", idempotency_key: `row278:${suffix}:instruction`,
  }, 200);
  const draft = await postJson<FeeDraftRecord>(request, token, "/fees/drafts", {
    case_id: caseRecord.id, client_id: client.id, draft_type: "GENERIC",
    currency: "CNY", obligation_id: obligationId,
  }, 201);
  const items = await getJson<FeeItemRecord[]>(request, token, `/fees/drafts/${draft.id}/items`);
  const created = await postJson<PayListCreateResult>(request, token, "/pay-lists/from-fee-items", {
    fee_item_ids: items.filter((item) => item.fee_type === "GOV").map((item) => item.id),
    planned_pay_date: "2026-08-31", remark: `row278 ${suffix}`,
  }, 200);
  const payListId = created.pay_list.id;

  const productionProbe = assertProductionConfigRequired(payListId);
  expect(productionProbe).toMatchObject({
    code: "PAYMENT_WORKBOOK_INPUT_CONFIG_REQUIRED", status: 409,
  });
  expect(productionProbe.after).toBe(productionProbe.before);
  openTestOnlyUiGate(payListId);

  await page.addInitScript((value) => localStorage.setItem("fpms_token", value), token);
  await page.goto(`/fee-management/pay-lists/${payListId}`, { waitUntil: "domcontentloaded" });
  await expect(page.getByRole("heading", { name: "官费清单详情" })).toBeVisible();
  const workbookPanel = page.getByTestId("official-workbook-panel");
  await expect(workbookPanel).toBeVisible();
  await expect(workbookPanel.getByText("ACTIVE", { exact: true })).toBeVisible();

  await fillGenerationForm(page);
  const generateButton = page.getByRole("button", { name: "生成并下载官方工作簿" });
  await expect(generateButton).toBeEnabled();
  const generationResponse = page.waitForResponse((response) => (
    response.request().method() === "POST"
      && response.url().endsWith(`/pay-lists/${payListId}/official-workbook`)
  ));
  const download = page.waitForEvent("download", { timeout: 15_000 });
  await generateButton.click();
  const generated = await generationResponse;
  expect([200, 201], await generated.text()).toContain(generated.status());
  expect((await download).suggestedFilename()).toBe(`${created.pay_list.pay_list_no}-official.xlsm`);
  await expect(page.getByText("服务端生成状态：已生成")).toBeVisible();

  const detailAfterGeneration = await getJson<PayListDetail>(
    request,
    token,
    `/pay-lists/${payListId}`,
  );
  const artifact = detailAfterGeneration.export_artifacts?.find(
    (item) => item.status === "GENERATED",
  );
  expect(artifact).toBeDefined();
  expect(detailAfterGeneration.pay_list.status).toBe("DRAFT");
  expect(detailAfterGeneration.gov_payments.every((item) => item.status === "PLANNED")).toBe(true);

  const artifactRow = page.getByTestId(`official-acceptance-artifact-${artifact?.id}`);
  await artifactRow.getByRole("button", { name: "登记官方页面接受" }).click();
  await page.getByTestId("official-acceptance-evidence-ref").fill(`official-site/row278/${suffix}`);
  await page.getByTestId("official-acceptance-evidence-sha256").fill("a".repeat(64));
  await page.getByTestId("official-acceptance-accepted-at").fill("2026-08-13T18:00");
  const acceptButton = page.getByRole("button", { name: "提交官方页面接受" });
  await expect(acceptButton).toBeEnabled();
  const acceptanceResponse = page.waitForResponse((response) => (
    response.request().method() === "POST"
      && response.url().endsWith(`/pay-lists/${payListId}/official-workbook/acceptance`)
  ));
  await acceptButton.click();
  const accepted = await acceptanceResponse;
  expect([200, 201], await accepted.text()).toContain(accepted.status());

  const result = page.getByTestId("official-acceptance-result");
  await expect(result.getByText("官方页面接受：已接受")).toBeVisible();
  await expect(result.getByText("支付：未支付")).toBeVisible();
  await expect(result.getByText("票据核验：未核验")).toBeVisible();
  const finalDetail = await getJson<PayListDetail>(request, token, `/pay-lists/${payListId}`);
  expect(finalDetail.export_artifacts?.find((item) => item.id === artifact?.id)?.status).toBe(
    "OFFICIAL_SITE_ACCEPTED",
  );
  expect(finalDetail.pay_list.status).toBe("DRAFT");
  expect(finalDetail.gov_payments.every((item) => item.status === "PLANNED")).toBe(true);
  expect(finalDetail.gov_payments.every((item) => item.official_receipt_no === null)).toBe(true);
});
