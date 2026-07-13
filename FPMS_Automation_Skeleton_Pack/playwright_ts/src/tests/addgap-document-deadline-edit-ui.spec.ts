import { expect, test } from "@playwright/test";
import type { Page, Request, Route } from "@playwright/test";

const caseId = "deadline-edit-case";
const templateId = "deadline-edit-template";

test.describe.configure({ mode: "serial" });

for (const scenario of [
  { name: "missing", documentId: "deadline-missing", legacyDate: null },
  { name: "legacy", documentId: "deadline-legacy", legacyDate: "2026-10-15" },
] as const) {
  test(`DocumentEdit confirms a ${scenario.name} deadline without changing a legacy date`, async ({
    page,
  }) => {
    let updateRequest: Request | null = null;
    await mockEditApi(page, scenario.documentId, () => scenarioDocument(scenario), (request) => {
      updateRequest = request;
    });

    await page.goto(`/documents/${scenario.documentId}/edit`, { waitUntil: "domcontentloaded" });
    await expect(page.getByRole("heading", { name: "编辑文档" })).toBeVisible();
    await expect(
      page
        .locator(".deadline-lineage-card")
        .getByText(scenario.legacyDate ? "历史待确认" : "未记录", { exact: true })
        .last(),
    ).toBeVisible();

    const dueInput = page.getByPlaceholder("请选择官方截止日");
    if (scenario.legacyDate) {
      await expect(dueInput).toHaveValue(scenario.legacyDate);
      await expect(dueInput).toBeDisabled();
    } else {
      await dueInput.fill("2026-11-20");
    }

    const sourceField = page.locator(".el-form-item").filter({ hasText: "截止日来源" }).first();
    await sourceField.locator(".el-select__wrapper").click();
    await page.getByRole("option", { name: "人工核对官方通知" }).click();
    await page.getByRole("button", { name: "确认官方截止日" }).click();
    await expect(page.getByText("已标记为待保存的确认信息")).toBeVisible();
    await page.getByRole("button", { name: "保存修改" }).click();

    await expect.poll(() => updateRequest?.postDataJSON()).toMatchObject({
      official_due_date: scenario.legacyDate || "2026-11-20",
      official_due_date_source: "MANUAL_OFFICIAL_NOTICE",
      official_due_date_status: "CONFIRMED",
    });
  });
}

test("DocumentEdit keeps a confirmed deadline read-only and omits override fields", async ({
  page,
}) => {
  const documentId = "deadline-confirmed";
  let updateRequest: Request | null = null;
  await mockEditApi(
    page,
    documentId,
    () => confirmedDocument(documentId),
    (request) => {
      updateRequest = request;
    },
  );

  await page.goto(`/documents/${documentId}/edit`, { waitUntil: "domcontentloaded" });
  await expect(
    page.locator(".deadline-lineage-card").getByText("已确认", { exact: true }),
  ).toBeVisible();
  await expect(page.getByPlaceholder("请选择官方截止日")).toHaveValue("2026-12-01");
  await expect(page.getByPlaceholder("请选择官方截止日")).toBeDisabled();
  await expect(page.getByText("已确认的官方截止日保持只读")).toBeVisible();
  await expect(page.getByRole("button", { name: "确认官方截止日" })).toHaveCount(0);

  await page.getByLabel("标题").fill("已确认截止日的普通标题修改");
  await page.getByRole("button", { name: "保存修改" }).click();

  await expect.poll(() => updateRequest?.postDataJSON()).not.toBeUndefined();
  const payload = updateRequest!.postDataJSON();
  expect(payload).not.toHaveProperty("official_due_date");
  expect(payload).not.toHaveProperty("official_due_date_source");
  expect(payload).not.toHaveProperty("official_due_date_status");
});

async function mockEditApi(
  page: Page,
  documentId: string,
  getDocument: () => Record<string, unknown>,
  captureUpdate: (request: Request) => void,
): Promise<void> {
  await page.addInitScript(() => {
    window.localStorage.setItem("fpms_token", "document-deadline-edit-ui-test-token");
  });
  await page.route("**/api/v1/**", async (route) => {
    const request = route.request();
    const url = new URL(request.url());
    const method = request.method();
    const apiPath = url.pathname.replace(/^\/api\/v1/, "");

    if (method === "GET" && apiPath === "/auth/me") {
      return fulfillJson(route, { permissions: ["Doc.Edit", "Doc.Read", "Case.Read"] });
    }
    if (method === "GET" && apiPath === `/documents/${documentId}`) {
      return fulfillJson(route, getDocument());
    }
    if (method === "PUT" && apiPath === `/documents/${documentId}`) {
      captureUpdate(request);
      return fulfillJson(route, { ...getDocument(), ...request.postDataJSON() });
    }
    if (method === "GET" && apiPath === "/cases") {
      return fulfillJson(route, { items: [backendCase()], total: 1, page: 1, page_size: 100 });
    }
    if (method === "GET" && apiPath === "/doc-templates") {
      return fulfillJson(route, {
        items: [backendTemplate()],
        total: 1,
        page: 1,
        page_size: 100,
      });
    }

    return fulfillJson(route, { detail: "未处理的 Task32 模拟请求" }, 404);
  });
}

async function fulfillJson(route: Route, body: unknown, status = 200): Promise<void> {
  await route.fulfill({ status, contentType: "application/json", body: JSON.stringify(body) });
}

function scenarioDocument(scenario: {
  documentId: string;
  legacyDate: string | null;
}): Record<string, unknown> {
  return {
    ...baseDocument(scenario.documentId),
    official_due_date: scenario.legacyDate,
    official_due_date_source: null,
    official_due_date_status: scenario.legacyDate ? "LEGACY_UNVERIFIED" : null,
  };
}

function confirmedDocument(documentId: string): Record<string, unknown> {
  return {
    ...baseDocument(documentId),
    official_due_date: "2026-12-01",
    official_due_date_source: "IMPORTED_OFFICIAL_NOTICE",
    official_due_date_status: "CONFIRMED",
  };
}

function baseDocument(documentId: string): Record<string, unknown> {
  return {
    id: documentId,
    case_id: caseId,
    case_no: "EDIT-DUE-001",
    doc_template_id: templateId,
    template_code: "OA_IN",
    direction: "IN",
    doc_type: "OFFICIAL_IN",
    doc_date: "2026-07-11",
    title: "审查意见通知书",
    description: "截止日 lineage 测试",
    attachments: [],
  };
}

function backendCase(): Record<string, unknown> {
  return {
    id: caseId,
    case_no: "EDIT-DUE-001",
    title_cn: "编辑截止日测试案件",
  };
}

function backendTemplate(): Record<string, unknown> {
  return {
    id: templateId,
    code: "OA_IN",
    name: "审查意见通知书（收文）",
    direction: "IN",
    enabled: true,
    status_effect: "OA1",
    deadline_template_code: "OA_REPLY",
    need_reply: true,
  };
}
