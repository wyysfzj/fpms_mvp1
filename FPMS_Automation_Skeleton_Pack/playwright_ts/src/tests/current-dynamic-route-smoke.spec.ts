import { expect, test } from "@playwright/test";
import type { APIRequestContext } from "@playwright/test";

const apiBaseUrl = (process.env.FPMS_API_URL || "http://localhost:8000/api/v1").replace(/\/$/, "");
const username = process.env.FPMS_USERNAME || "admin";
const password = process.env.FPMS_PASSWORD || "admin123";
const runId = process.env.FPMS_RUN_ID || "DYNROUTE";

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

type DocumentRecord = {
  id: string;
};

type DunningRecord = {
  id: number;
};

type DynamicRoute = {
  sourceRoute: string;
  componentName: string;
  resolvePath: (fixture: DynamicRouteFixture) => string;
};

type DynamicRouteFixture = {
  clientId: string;
  documentId: string;
  dunningId: number;
};

const dynamicRoutes: DynamicRoute[] = [
  {
    sourceRoute: "/clients/:id/edit",
    componentName: "ClientForm",
    resolvePath: (fixture) => `/clients/${fixture.clientId}/edit`,
  },
  {
    sourceRoute: "/documents/:id/envelope",
    componentName: "DocumentEnvelopePrint",
    resolvePath: (fixture) => `/documents/${fixture.documentId}/envelope`,
  },
  {
    sourceRoute: "/documents/:id/edit",
    componentName: "DocumentEdit",
    resolvePath: (fixture) => `/documents/${fixture.documentId}/edit`,
  },
  {
    sourceRoute: "/collections/dunning/:id",
    componentName: "DunningDetail",
    resolvePath: (fixture) => `/collections/dunning/${fixture.dunningId}`,
  },
];

async function apiPost<T>(
  request: APIRequestContext,
  path: string,
  token: string,
  data: unknown,
  expectedStatus: number
): Promise<T> {
  const response = await request.post(`${apiBaseUrl}/${path.replace(/^\//, "")}`, {
    data,
    headers: { Authorization: `Bearer ${token}` },
  });
  expect(response.status(), `${path} status`).toBe(expectedStatus);
  return response.json() as Promise<T>;
}

async function createClient(request: APIRequestContext, token: string, suffix: string): Promise<ClientRecord> {
  return apiPost<ClientRecord>(
    request,
    "/clients",
    token,
    {
      client_code: `PW-DYN-${suffix}`,
      name_cn: `动态路由客户-${suffix}`,
      client_type: "CLIENT",
      default_currency: "CNY",
      is_active: true,
    },
    201
  );
}

async function createApplicant(request: APIRequestContext, token: string, suffix: string): Promise<ApplicantRecord> {
  return apiPost<ApplicantRecord>(
    request,
    "/applicants",
    token,
    {
      code: `PW-DYN-AP-${suffix}`,
      name_cn: `动态路由申请人-${suffix}`,
      applicant_type: "ENTITY",
      is_active: true,
    },
    201
  );
}

async function createCase(
  request: APIRequestContext,
  token: string,
  suffix: string,
  clientId: string,
  applicant: ApplicantRecord
): Promise<CaseRecord> {
  return apiPost<CaseRecord>(
    request,
    "/cases",
    token,
    {
      case_no: `PW-DYN-CASE-${suffix}`,
      app_no: `PW-DYN-APP-${suffix}`,
      case_type: "NORMAL",
      patent_category: "INV",
      flow_dir: "CN_DOMESTIC",
      title_cn: `动态路由案卷-${suffix}`,
      status: "NOT_FILED",
      client_id: clientId,
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
    },
    201
  );
}

async function createDocument(
  request: APIRequestContext,
  token: string,
  caseData: CaseRecord,
  suffix: string
): Promise<DocumentRecord> {
  return apiPost<DocumentRecord>(
    request,
    "/documents",
    token,
    {
      case_id: caseData.id,
      doc_template_id: null,
      doc_type: "CLIENT_IN",
      direction: "IN",
      doc_date: "2026-05-09",
      title: `动态路由文档-${suffix}`,
      extra_data: `case_no=${caseData.case_no}`,
    },
    201
  );
}

async function createDunningBatch(
  request: APIRequestContext,
  token: string,
  clientId: string,
  caseId: string,
  suffix: string
): Promise<DunningRecord> {
  await apiPost<Record<string, unknown>>(
    request,
    "/bills/manual",
    token,
    {
      client_id: clientId,
      case_id: caseId,
      currency: "CNY",
      direction: "AR",
      status: "UNSETTLED",
      bill_date: "2026-01-10",
      due_date: "2026-01-20",
      items: [
        {
          description: `动态路由催款账单-${suffix}`,
          quantity: 1,
          unit_price: "1200.00",
          fee_type: "SERVICE",
        },
      ],
      notes: `dynamic route smoke ${suffix}`,
    },
    201
  );

  const result = await apiPost<{ batches: DunningRecord[] }>(
    request,
    "/dunning",
    token,
    {
      to_date: "2026-02-01",
      client_id: clientId,
      include_statuses: ["UNSETTLED"],
    },
    200
  );
  expect(result.batches.length).toBeGreaterThan(0);
  return result.batches[0];
}

test("@P1 current dynamic frontend routes render without page errors", async ({ page, request }) => {
  const login = await request.post(`${apiBaseUrl}/auth/login`, {
    data: { username, password },
  });
  expect(login.ok()).toBeTruthy();
  const token = (await login.json()).access_token as string;
  expect(token).toBeTruthy();

  const suffix = `${runId}-${Date.now()}`.toUpperCase();
  const client = await createClient(request, token, suffix);
  const applicant = await createApplicant(request, token, suffix);
  const caseData = await createCase(request, token, suffix, client.id, applicant);
  const document = await createDocument(request, token, caseData, suffix);
  const dunning = await createDunningBatch(request, token, client.id, caseData.id, suffix);

  const fixture: DynamicRouteFixture = {
    clientId: client.id,
    documentId: document.id,
    dunningId: dunning.id,
  };
  const pageErrors: string[] = [];
  page.on("pageerror", (error) => pageErrors.push(error.message));

  await page.addInitScript((value) => {
    window.localStorage.setItem("fpms_token", value);
  }, token);

  for (const route of dynamicRoutes) {
    await page.goto(route.resolvePath(fixture), { waitUntil: "domcontentloaded" });
    await expect(page.locator("#app"), `${route.sourceRoute} #app`).toBeVisible();
    await expect(page.locator("body"), `${route.componentName} body`).toContainText(/\S/);
  }

  expect(pageErrors).toEqual([]);
});
