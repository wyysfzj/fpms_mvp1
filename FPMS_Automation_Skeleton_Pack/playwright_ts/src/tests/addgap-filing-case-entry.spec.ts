import { expect, test } from "@playwright/test";
import type { Request, Route } from "@playwright/test";

const caseId = "1e2749f4-e12d-4a2c-a40f-641c2dbdc5d4";
const caseNo = "ADDGAP-CASE-ENTRY-001";
const packageId = "filing-package-from-case-entry";

test("CaseDetail enters filing preparation with the current case_id", async ({ page }) => {
  let resolveRequest: Request | null = null;

  await page.route("**/api/v1/**", async (route) => {
    const request = route.request();
    const url = new URL(request.url());
    const method = request.method();
    const apiPath = url.pathname.replace(/^\/api\/v1/, "");

    if (method === "GET" && apiPath === "/auth/me") {
      return fulfillJson(route, {
        permissions: ["Case.Read", "Doc.Read", "OfficialWorkflow.Update"],
      });
    }
    if (method === "GET" && apiPath === `/cases/${caseId}`) {
      return fulfillJson(route, backendCase());
    }
    if (method === "GET" && apiPath === "/tasks") {
      return fulfillJson(route, { items: [], page: 1, page_size: 50, total: 0 });
    }
    if (
      method === "POST"
      && apiPath === `/cases/${caseId}/official-work-packages/filing-preparation/resolve`
    ) {
      resolveRequest = request;
      return fulfillJson(route, filingPackage());
    }

    return fulfillJson(route, { detail: "Unhandled Task09 mock route" }, 404);
  });

  await page.addInitScript(() => {
    window.localStorage.setItem("fpms_token", "filing-case-entry-test-token");
  });

  await page.goto(`/cases/${caseId}`, { waitUntil: "domcontentloaded" });

  await expect(page.getByRole("heading", { name: "申请前准备入口测试案件" })).toBeVisible();
  const entry = page.getByRole("button", { name: "申请前准备" });
  await expect(entry).toBeVisible();
  await entry.click();

  await expect.poll(() => resolveRequest).not.toBeNull();
  expect(resolveRequest?.method()).toBe("POST");
  expect(resolveRequest?.postData()).toBeNull();
  expect(new URL(resolveRequest!.url()).pathname).toBe(
    `/api/v1/cases/${caseId}/official-work-packages/filing-preparation/resolve`,
  );
  await expect(page.getByRole("heading", { name: "新申请递交准备" })).toBeVisible();
  await expect.poll(() => new URL(page.url()).searchParams.get("package_id")).toBe(packageId);
  expect(new URL(page.url()).searchParams.has("case_id")).toBe(false);
});

async function fulfillJson(route: Route, body: unknown, status = 200): Promise<void> {
  await route.fulfill({
    status,
    contentType: "application/json",
    body: JSON.stringify(body),
  });
}

function backendCase(): Record<string, unknown> {
  return {
    id: caseId,
    case_no: caseNo,
    case_type: "NORMAL",
    patent_category: "INV",
    flow_dir: "CN_DOMESTIC",
    title_cn: "申请前准备入口测试案件",
    status: "NOT_FILED",
    applicants: [],
    inventors: [],
    priorities: [],
    bio_deposits: [],
    agent_splits: [],
  };
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
