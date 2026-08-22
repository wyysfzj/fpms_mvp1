import { expect, test } from "@playwright/test";
import type { Page, Request, Route } from "@playwright/test";

const sourceDocumentId = "00000000-0000-0000-0000-000000000201";
const contentHash = `sha256:${"a".repeat(64)}`;

test("IN source retries one archive operation and displays the authoritative evidence identity", async ({
  page,
}) => {
  const requests: Request[] = [];
  await mockFormatLetterApi(page, "IN", async (route) => {
    requests.push(route.request());
    if (requests.length === 1) {
      return fulfillJson(
        route,
        { error: { code: "TEMPORARY_FAILURE", message: "temporary failure" } },
        500,
      );
    }
    return fulfillJson(route, archiveResult());
  });

  await openDocument(page);
  const action = page.getByRole("button", { name: "生成并归档格式函" });
  await expect(action).toBeVisible();
  await page.getByPlaceholder("记录本次交接说明").fill("保留本次备注");

  await action.click();
  await expect(page.getByText("temporary failure")).toBeVisible();
  await page
    .locator(".letter-handoff-panel .error-banner")
    .getByRole("button", { name: "✕" })
    .click();
  await action.click();

  await expect.poll(() => requests.length).toBe(2);
  const firstPayload = requests[0].postDataJSON();
  const secondPayload = requests[1].postDataJSON();
  expect(firstPayload).toEqual({
    operation_id: expect.stringMatching(
      /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i,
    ),
    selected_contact_id: null,
    remark: "保留本次备注",
  });
  expect(secondPayload).toEqual(firstPayload);
  expect(requests[0].method()).toBe("POST");
  expect(new URL(requests[0].url()).pathname).toBe(
    `/api/v1/official-documents/${sourceDocumentId}/format-letter-archive`,
  );
  await expect(page.getByText("证据版本 v1")).toBeVisible();
  await expect(page.getByText(contentHash)).toBeVisible();
  await expect(action).toBeDisabled();
});

test("OUT document never exposes the archive action or archive identity", async ({ page }) => {
  let archiveCalls = 0;
  await mockFormatLetterApi(page, "OUT", async (route) => {
    archiveCalls += 1;
    return fulfillJson(route, archiveResult());
  });

  await openDocument(page);

  await expect(page.getByRole("button", { name: "生成并归档格式函" })).toHaveCount(0);
  await expect(page.getByText("证据版本 v1")).toHaveCount(0);
  await expect(page.getByText(contentHash)).toHaveCount(0);
  expect(archiveCalls).toBe(0);
});

async function mockFormatLetterApi(
  page: Page,
  direction: "IN" | "OUT",
  archive: (route: Route) => Promise<void>,
): Promise<void> {
  await page.route("**/api/v1/**", async (route) => {
    const request = route.request();
    const apiPath = new URL(request.url()).pathname.replace(/^\/api\/v1/, "");

    if (request.method() === "GET" && apiPath === "/auth/me") {
      return fulfillJson(route, {
        user: { id: "actor-format-letter-ui", username: "归档测试用户", is_active: true },
        roles: [],
        permissions: ["Doc.Read", "OfficialWorkflow.Read", "OfficialWorkflow.Update"],
      });
    }
    if (request.method() === "GET" && apiPath === `/documents/${sourceDocumentId}`) {
      return fulfillJson(route, backendDocument(direction));
    }
    if (
      request.method() === "GET"
      && apiPath === `/official-documents/${sourceDocumentId}/letter-handoff/preview`
    ) {
      return fulfillJson(route, handoffPreview());
    }
    if (
      request.method() === "POST"
      && apiPath === `/official-documents/${sourceDocumentId}/format-letter-archive`
    ) {
      return archive(route);
    }

    return fulfillJson(route, { detail: "未处理的格式函归档模拟请求" }, 404);
  });
}

async function openDocument(page: Page): Promise<void> {
  await page.addInitScript(() => {
    window.localStorage.setItem("fpms_token", "v8-format-letter-in-source-ui-token");
  });
  await page.goto(`/documents/${sourceDocumentId}`, { waitUntil: "domcontentloaded" });
  await expect(page.getByRole("heading", { name: "格式函归档测试文书" })).toBeVisible();
}

async function fulfillJson(route: Route, body: unknown, status = 200): Promise<void> {
  await route.fulfill({ status, contentType: "application/json", body: JSON.stringify(body) });
}

function backendDocument(direction: "IN" | "OUT"): Record<string, unknown> {
  return {
    id: sourceDocumentId,
    case_id: "case-format-letter-ui",
    case_no: "CASE-LETTER-001",
    title: "格式函归档测试文书",
    direction,
    doc_type: direction === "IN" ? "OFFICIAL_IN" : "CLIENT_OUT",
    doc_date: "2026-08-09",
    created_at: "2026-08-09T08:00:00",
    updated_at: "2026-08-09T08:00:00",
    attachments: [],
  };
}

function handoffPreview(): Record<string, unknown> {
  return {
    source_document_id: sourceDocumentId,
    case_id: "case-format-letter-ui",
    case_no: "CASE-LETTER-001",
    mapping: {
      id: "mapping-format-letter-ui",
      format_letter_template_id: "template-format-letter-ui",
      format_letter_template_code: "FORMAT_LETTER_002",
      output_name_rule: "{case_no}-给申请人的邮件.docx",
      contact_rule_code: "PRIMARY_OR_DEFAULT",
      salutation_rule_code: "CONTACT_TITLE_OR_DEFAULT",
    },
    template_status: "READY",
    client_contact_id: null,
    contact: null,
    contact_selection_source: "NO_CONTACT",
    salutation_source: "DEFAULT",
    salutation_text: "尊敬的客户：",
    generated_word_path: "letters/CASE-LETTER-001/CASE-LETTER-001-给申请人的邮件.docx",
    mail_subject: "格式函归档测试文书",
    mail_body_draft: "尊敬的客户：",
    attachments: [],
  };
}

function archiveResult(): Record<string, unknown> {
  return {
    handoff: {
      id: "00000000-0000-0000-0000-000000000202",
      source_document_id: sourceDocumentId,
      generated_document_id: "00000000-0000-0000-0000-000000000203",
      longxia_handoff_status: "READY",
      remark: "保留本次备注",
      attachments: [],
    },
    evidence_version_id: "00000000-0000-0000-0000-000000000204",
    version_number: 1,
    content_hash: contentHash,
    generated_document_id: "00000000-0000-0000-0000-000000000203",
    attachment_id: "00000000-0000-0000-0000-000000000205",
    file_name: "CASE-LETTER-001-给申请人的邮件.docx",
    role: "CLIENT_LETTER_WORD",
    state: "DRAFT",
    review_state: "PENDING",
    is_current: true,
    reused: false,
  };
}
