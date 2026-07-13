import { expect, test } from "@playwright/test";
import type { Request } from "@playwright/test";

const caseId = "7bc5774b-dde9-4da8-82b5-3fc82b4df856";
const packageId = "filing-package-resolved";
const pagePath = "/official-workflows/filing-preparation";
const resolvePath = `**/api/v1/cases/${caseId}/official-work-packages/filing-preparation/resolve`;

test.beforeEach(async ({ page }) => {
  await page.route("**/api/v1/auth/me", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        permissions: ["Case.Read", "Doc.Read", "OfficialWorkflow.Update"],
      }),
    });
  });

  await page.addInitScript(() => {
    window.localStorage.setItem("fpms_token", "filing-page-resolve-test-token");
  });
});

test("FilingPreparation resolves case_id and replaces the route with package_id", async ({
  page,
}) => {
  let resolveRequest: Request | null = null;
  let packageGetCount = 0;

  await page.route(resolvePath, async (route) => {
    resolveRequest = route.request();
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(filingPackage()),
    });
  });
  await page.route(
    `**/api/v1/official-work-packages/${packageId}/filing-preparation`,
    async (route) => {
      packageGetCount += 1;
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(filingPackage()),
      });
    },
  );

  await page.goto(`${pagePath}?case_id=${caseId}`, { waitUntil: "domcontentloaded" });

  await expect(page.getByRole("heading", { name: "新申请递交准备" })).toBeVisible();
  await expect.poll(() => resolveRequest).not.toBeNull();
  expect(resolveRequest?.method()).toBe("POST");
  expect(resolveRequest?.postData()).toBeNull();
  await expect.poll(() => new URL(page.url()).searchParams.get("package_id")).toBe(packageId);
  expect(new URL(page.url()).searchParams.has("case_id")).toBe(false);
  await expect(page.getByText(`工作包 ${packageId}`)).toBeVisible();
  expect(packageGetCount).toBe(0);
});

for (const scenario of [
  {
    status: 404,
    code: "CASE_NOT_FOUND",
    backendMessage: "Case not found",
    expectedMessage: "未找到对应案件，无法进入新申请递交准备。",
  },
  {
    status: 409,
    code: "FILING_PREPARATION_CASE_STATE_INVALID",
    backendMessage: "Filing preparation package can only be created for a NOT_FILED case",
    expectedMessage: "当前案件状态或工作包配置不允许进入新申请递交准备。",
  },
  {
    status: 422,
    code: "REQUEST_VALIDATION_ERROR",
    backendMessage: "Request validation failed",
    expectedMessage: "案件标识格式无效，请从案件详情重新进入。",
  },
]) {
  test(`FilingPreparation shows Simplified Chinese feedback for resolve ${scenario.status}`, async ({
    page,
  }) => {
    await page.route(resolvePath, async (route) => {
      await route.fulfill({
        status: scenario.status,
        contentType: "application/json",
        body: JSON.stringify({
          error: {
            code: scenario.code,
            message: scenario.backendMessage,
            details: null,
          },
        }),
      });
    });

    await page.goto(`${pagePath}?case_id=${caseId}`, { waitUntil: "domcontentloaded" });

    await expect(page.getByText(scenario.expectedMessage)).toBeVisible();
    expect(new URL(page.url()).searchParams.get("case_id")).toBe(caseId);
    expect(new URL(page.url()).searchParams.has("package_id")).toBe(false);
  });
}

function filingPackage(): Record<string, unknown> {
  return {
    package: {
      id: packageId,
      case_id: caseId,
      package_kind: "FILING_PREP",
      status: "NEEDS_MAINTENANCE",
      source_document_id: null,
      reply_document_id: null,
      external_system: "CNIPA_WEB",
      remark: null,
    },
    official_field_summary: {
      status: "NEEDS_MAINTENANCE",
      missing_codes: [],
      items: [],
    },
    technical_disclosure_gate: {
      role: "TECHNICAL_DISCLOSURE",
      required: true,
      status: "MISSING",
      attachment_id: null,
      file_name: null,
    },
    commission_instruction_gate: {
      role: "COMMISSION_INSTRUCTION",
      required: false,
      status: "MISSING",
      attachment_id: null,
      file_name: null,
    },
    filing_file_roles: [],
    official_page_checklist: [],
    xml_zip: {
      status: "MISSING",
      attachment_id: null,
      file_name: null,
      placeholder: "待引用",
    },
    merged_pdf_archive_status: "MISSING",
    fee_summary: {
      draft_count: 0,
      pay_list_count: 0,
      official_template_ready: false,
      blocker_count: 1,
    },
  };
}
