import { expect, test } from "@playwright/test";
import type { Page, Route } from "@playwright/test";

const caseId = "case-lifecycle-template-binding";
const ordinaryActions = [
  "记录受理通知",
  "开始初步审查",
  "记录初审通过",
  "记录公布通知",
  "开始实质审查",
];

test("document detail binds its loaded template code into lifecycle evidence actions", async ({
  page,
}) => {
  await mockDocumentApi(page);
  await page.addInitScript(() => {
    window.localStorage.setItem("fpms_token", "lifecycle-template-binding-token");
  });

  await page.goto("/documents/document-oa-template-binding", {
    waitUntil: "domcontentloaded",
  });
  await expect(page.getByRole("heading", { name: "映射后无模板代码的 OA 文档" })).toBeVisible();
  const oaPanel = page.locator(".lifecycle-evidence-actions");
  await expect(oaPanel.getByRole("combobox", { name: "已复核证据版本" })).toBeVisible();
  await expect(oaPanel.getByRole("button", { name: "记录审查意见通知" })).toBeVisible();
  await expect(oaPanel.locator(".action-row .el-button")).toHaveText([
    ...ordinaryActions,
    "记录审查意见通知",
  ]);

  await page.goto("/documents/document-ordinary-template-binding", {
    waitUntil: "domcontentloaded",
  });
  await expect(page.getByRole("heading", { name: "映射后无模板代码的普通文档" })).toBeVisible();
  const ordinaryPanel = page.locator(".lifecycle-evidence-actions");
  await expect(ordinaryPanel.getByRole("combobox", { name: "证据文件" })).toBeVisible();
  await expect(ordinaryPanel.getByRole("button", { name: "记录审查意见通知" })).toHaveCount(0);
  await expect(ordinaryPanel.locator(".action-row .el-button")).toHaveText(ordinaryActions);
});

async function mockDocumentApi(page: Page): Promise<void> {
  await page.route("**/api/v1/**", async (route) => {
    const request = route.request();
    const apiPath = new URL(request.url()).pathname.replace(/^\/api\/v1/, "");

    if (request.method() === "GET" && apiPath === "/auth/me") {
      return fulfillJson(route, {
        user: { id: "lifecycle-reviewer", username: "生命周期复核人", is_active: true },
        roles: [],
        permissions: ["Doc.Read", "Doc.Edit"],
      });
    }
    if (request.method() === "GET" && apiPath.startsWith("/documents/")) {
      const documentId = apiPath.slice("/documents/".length);
      return fulfillJson(route, backendDocument(documentId));
    }
    if (request.method() === "GET" && apiPath.startsWith("/doc-templates/")) {
      const templateId = apiPath.slice("/doc-templates/".length);
      return fulfillJson(route, backendTemplate(templateId));
    }

    return fulfillJson(route, { detail: "未处理的生命周期模板绑定模拟请求" }, 404);
  });
}

async function fulfillJson(route: Route, body: unknown, status = 200): Promise<void> {
  await route.fulfill({ status, contentType: "application/json", body: JSON.stringify(body) });
}

function backendDocument(documentId: string): Record<string, unknown> {
  const isOa = documentId === "document-oa-template-binding";
  return {
    id: documentId,
    case_id: caseId,
    case_no: "LIFECYCLE-TEMPLATE-001",
    doc_template_id: isOa ? "template-oa" : "template-ordinary",
    direction: "IN",
    doc_type: "OFFICIAL_IN",
    doc_date: "2026-08-26",
    title: isOa ? "映射后无模板代码的 OA 文档" : "映射后无模板代码的普通文档",
    created_at: "2026-08-26T08:00:00",
    updated_at: "2026-08-26T08:00:00",
    attachments: [
      {
        id: `${documentId}-attachment`,
        document_id: documentId,
        file_name: "已复核证据.pdf",
        file_size: 128,
        mime_type: "application/pdf",
        uploaded_at: "2026-08-26T08:00:00",
        evidence_version_id: `${documentId}-evidence`,
        content_hash: `sha256:${"a".repeat(64)}`,
        role: isOa ? "OA_NOTICE_1" : "ACCEPTANCE_NOTICE",
        creator_id: "evidence-creator",
        reviewer_id: "lifecycle-reviewer",
        review_state: "APPROVED",
        is_current: true,
        is_final: true,
      },
    ],
  };
}

function backendTemplate(templateId: string): Record<string, unknown> {
  const isOa = templateId === "template-oa";
  return {
    id: templateId,
    code: isOa ? "OFFICIAL_NOTICE_003" : "OFFICIAL_NOTICE_001",
    name: isOa ? "第一次审查意见通知书" : "受理通知书",
    direction: "IN",
    enabled: true,
    status_effect: null,
    status_restore: null,
    deadline_template_code: null,
    fee_draft_type: null,
    fee_item_list: null,
    need_reply: isOa,
    reply_to_template_code: null,
    input_fields: null,
    created_at: "2026-08-26T08:00:00",
    updated_at: "2026-08-26T08:00:00",
  };
}
