import { test, expect } from "@playwright/test";
import type { APIRequestContext } from "@playwright/test";

const apiBaseUrl = (process.env.FPMS_API_URL || "http://localhost:8000/api/v1").replace(/\/$/, "");
const username = process.env.FPMS_USERNAME || "admin";
const password = process.env.FPMS_PASSWORD || "admin123";
const runId = process.env.FPMS_RUN_ID || "CASEDOCK-PW";

async function apiPost(request: APIRequestContext, path: string, token: string, data: unknown) {
  return request.post(`${apiBaseUrl}/${path.replace(/^\//, "")}`, {
    data,
    headers: { Authorization: `Bearer ${token}` },
  });
}

async function createApplicant(request: APIRequestContext, token: string, suffix: string) {
  const response = await apiPost(request, "/applicants", token, {
    code: `CDGPW-${suffix}`,
    name_cn: `页面门禁申请人-${suffix}`,
    applicant_type: "ENTITY",
    is_active: true,
  });
  expect(response.status()).toBe(201);
  return response.json();
}

async function createCase(request: APIRequestContext, token: string, suffix: string) {
  const applicant = await createApplicant(request, token, suffix);
  const response = await apiPost(request, "/cases", token, {
    case_no: `CDGPW-${suffix}`,
    case_type: "NORMAL",
    patent_category: "INV",
    flow_dir: "CN_DOMESTIC",
    title_cn: `页面门禁真实API案件-${suffix}`,
    status: "NOT_FILED",
    no_power: true,
    has_exam_request: false,
    applicants: [
      {
        seq: 1,
        is_first: true,
        applicant_id: applicant.id,
        name_cn: applicant.name_cn,
      },
    ],
  });
  expect(response.status()).toBe(201);
  return response.json();
}

async function createDocument(request: APIRequestContext, token: string, caseId: string, title: string) {
  const response = await apiPost(request, "/documents", token, {
    case_id: caseId,
    doc_template_id: null,
    doc_type: "CLIENT_IN",
    direction: "IN",
    doc_date: "2026-05-01",
    title,
  });
  expect(response.status()).toBe(201);
  return response.json();
}

test("@P0 Case Document Gate minimal UI uses real API pages", async ({ page, request }) => {
  const login = await request.post(`${apiBaseUrl}/auth/login`, {
    data: { username, password },
  });
  expect(login.ok()).toBeTruthy();
  const token = (await login.json()).access_token as string;
  expect(token).toBeTruthy();

  const suffix = `${runId}-${Date.now()}`.toUpperCase();
  const caseData = await createCase(request, token, suffix);
  await createDocument(request, token, caseData.id, "发明专利请求书");
  await createDocument(request, token, caseData.id, "说明书");

  const pageErrors: string[] = [];
  page.on("pageerror", (error) => pageErrors.push(error.message));

  await page.addInitScript((value) => {
    window.localStorage.setItem("fpms_token", value);
  }, token);

  const intakeResponse = page.waitForResponse((response) =>
    response.url().includes("/cases/document-gate/intake-preview")
  );
  await page.goto("/cases/new", { waitUntil: "domcontentloaded" });
  expect((await intakeResponse).ok()).toBeTruthy();
  await expect(page.getByText("收案文件与材料核验")).toBeVisible();
  await expect(page.getByText("材料要求")).toBeVisible();

  const caseGateResponse = page.waitForResponse((response) =>
    response.url().includes(`/cases/${caseData.id}/document-gate`)
  );
  await page.goto(`/cases/${caseData.id}`, { waitUntil: "domcontentloaded" });
  await page.getByRole("tab", { name: "往来文件" }).click();
  expect((await caseGateResponse).ok()).toBeTruthy();
  await expect(page.getByText("当前节点文件材料")).toBeVisible();
  await expect(page.getByText("当前建议动作")).toBeVisible();

  await page.goto(`/documents/new?case_id=${caseData.id}&case_no=${caseData.case_no}`, {
    waitUntil: "domcontentloaded",
  });
  const impactResponse = page.waitForResponse((response) =>
    response.url().includes("/documents/impact-preview")
  );
  await page.getByLabel("标题").fill("第一次审查意见通知书");
  expect((await impactResponse).ok()).toBeTruthy();
  await expect(page.getByText("来源文件与影响预览")).toBeVisible();

  const batchResponse = page.waitForResponse((response) =>
    response.url().includes("/cases/batch-filing/candidates")
  );
  await page.goto("/cases/batch-filing", { waitUntil: "domcontentloaded" });
  expect((await batchResponse).ok()).toBeTruthy();
  await expect(page.getByText("最终材料门禁")).toBeVisible();
  await expect(page.getByText("执行预览")).toBeVisible();

  expect(pageErrors).toEqual([]);
});
