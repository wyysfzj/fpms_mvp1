import { expect, test } from "@playwright/test";
import type { Request } from "@playwright/test";

const documentId = "df79bb52-9af7-4237-9ddc-6dc7f4f9733d";
const caseId = "a23ebfab-37d8-4df9-b539-0e92c78b6061";
const packageId = "oa-package-resolved";
const pagePath = "/official-workflows/oa-reply";
const resolvePath =
  `**/api/v1/official-documents/${documentId}/official-work-packages/oa-reply/resolve`;

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
    window.localStorage.setItem("fpms_token", "oa-page-resolve-test-token");
  });
});

test("OAReplyPackage resolves document_id and replaces the route with package_id", async ({
  page,
}) => {
  let resolveRequest: Request | null = null;
  let packageGetCount = 0;

  await page.route(resolvePath, async (route) => {
    resolveRequest = route.request();
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(oaReplyPackage()),
    });
  });
  await page.route(`**/api/v1/official-work-packages/${packageId}/oa-reply`, async (route) => {
    packageGetCount += 1;
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(oaReplyPackage()),
    });
  });

  await page.goto(`${pagePath}?document_id=${documentId}`, { waitUntil: "domcontentloaded" });

  await expect(page.getByRole("heading", { name: "OA答复工作包" })).toBeVisible();
  await expect.poll(() => resolveRequest).not.toBeNull();
  expect(resolveRequest?.method()).toBe("POST");
  expect(resolveRequest?.postData()).toBeNull();
  await expect.poll(() => new URL(page.url()).searchParams.get("package_id")).toBe(packageId);
  expect(new URL(page.url()).searchParams.has("document_id")).toBe(false);
  await expect(page.getByText(`工作包 ${packageId}`)).toBeVisible();
  await expect(page.getByText("第一次审查意见通知书").first()).toBeVisible();
  expect(packageGetCount).toBe(0);
});

for (const scenario of [
  {
    status: 404,
    code: "DOCUMENT_NOT_FOUND",
    backendMessage: "Document not found",
    expectedMessage: "未找到对应官文，无法进入OA答复工作包。",
  },
  {
    status: 400,
    code: "OA_REPLY_SOURCE_DIRECTION_INVALID",
    backendMessage: "OA reply package source must be an incoming document",
    expectedMessage: "当前文书方向不支持进入OA答复工作包。",
  },
  {
    status: 409,
    code: "OA_REPLY_SOURCE_SEMANTICS_INVALID",
    backendMessage: "Document does not have executable OA reply semantics",
    expectedMessage: "当前官文状态、语义或工作包配置不允许进入OA答复工作包。",
  },
  {
    status: 422,
    code: "REQUEST_VALIDATION_ERROR",
    backendMessage: "Request validation failed",
    expectedMessage: "官文标识格式无效，请从文书详情重新进入。",
  },
]) {
  test(`OAReplyPackage shows Simplified Chinese feedback for resolve ${scenario.status}`, async ({
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

    await page.goto(`${pagePath}?document_id=${documentId}`, { waitUntil: "domcontentloaded" });

    await expect(page.getByText(scenario.expectedMessage)).toBeVisible();
    expect(new URL(page.url()).searchParams.get("document_id")).toBe(documentId);
    expect(new URL(page.url()).searchParams.has("package_id")).toBe(false);
  });
}

function oaReplyPackage(): Record<string, unknown> {
  return {
    package: {
      id: packageId,
      case_id: caseId,
      package_kind: "OA_REPLY",
      status: "NEEDS_MAINTENANCE",
      source_document_id: documentId,
      reply_document_id: null,
      external_system: "CNIPA_WEB",
      remark: null,
    },
    source_document: {
      id: documentId,
      title: "第一次审查意见通知书",
      template_code: "OA_IN",
      direction: "IN",
      doc_date: "2026-07-10",
      ref_no: "210401",
      reply_to_id: null,
      need_reply: true,
      reply_date: null,
    },
    reply_document: null,
    application_no: "CN202610000012.3",
    applicant_display: "测试申请人",
    notice_code: "210401",
    notice_name: "第一次审查意见通知书",
    issue_sequence: "1",
    issue_date: "2026-07-10",
    official_due_date: "2026-11-10",
    internal_due_date: "2026-10-27",
    reply_status: "WAITING_REPLY_DOCUMENT",
    statement_text: null,
    statement_word: {
      role: "OA_STATEMENT_WORD",
      status: "MISSING",
      attachment_id: null,
      file_name: null,
      external_upload_position: null,
    },
    statement_pdf: {
      role: "OA_STATEMENT_PDF",
      status: "MISSING",
      attachment_id: null,
      file_name: null,
      external_upload_position: null,
    },
    modified_claim_files: [],
    comparison_page: {
      role: "OA_AMENDMENT_COMPARISON",
      status: "MISSING",
      attachment_id: null,
      file_name: null,
      external_upload_position: null,
    },
    proof_files: [],
    experiment_data_submitted: false,
    official_page_checklist: [],
    oa_file_roles: [],
  };
}
