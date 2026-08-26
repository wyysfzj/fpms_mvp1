import { expect, test } from "@playwright/test";
import type { Request, Route } from "@playwright/test";

const caseId = "addgap-document-deadline-case";
const templateId = "oa-in-template";

test("DocumentCreate records a confirmed official deadline and previews its impact", async ({
  page,
}) => {
  const previewPayloads: Array<Record<string, unknown>> = [];
  let releaseOrdinaryPreview = () => {};
  const ordinaryPreviewGate = new Promise<void>((resolve) => {
    releaseOrdinaryPreview = resolve;
  });
  let ordinaryPreviewResponseSent = false;
  let previewRequest: Request | null = null;
  let createRequest: Request | null = null;

  await page.route("**/api/v1/**", async (route) => {
    const request = route.request();
    const url = new URL(request.url());
    const method = request.method();
    const apiPath = url.pathname.replace(/^\/api\/v1/, "");

    if (method === "GET" && apiPath === "/auth/me") {
      return fulfillJson(route, {
        permissions: ["Doc.Create", "Doc.Read", "DocTemplate.Read", "Case.Read"],
      });
    }
    if (method === "GET" && apiPath === `/cases/${caseId}`) {
      return fulfillJson(route, backendCase());
    }
    if (method === "GET" && apiPath === "/doc-templates") {
      return fulfillJson(route, {
        items: [oaTemplate()],
        total: 1,
        page: 1,
        page_size: 100,
      });
    }
    if (method === "GET" && apiPath === "/documents") {
      return fulfillJson(route, { items: [], total: 0, page: 1, page_size: 100 });
    }
    if (method === "POST" && apiPath === "/documents/impact-preview") {
      const payload = request.postDataJSON() as Record<string, unknown>;
      previewPayloads.push(payload);
      if (payload.doc_template_id === templateId && !hasConfirmedDeadline(payload)) {
        return fulfillJson(
          route,
          {
            error: {
              code: "OA_OFFICIAL_DUE_DATE_REQUIRED",
              message: "请填写并确认官方截止日",
              details: { status: payload.official_due_date_status ?? null },
            },
          },
          409,
        );
      }
      if (payload.doc_template_id === null) {
        await ordinaryPreviewGate;
        await fulfillJson(route, {
          ...impactPreview(payload),
          risk_tips: ["过期普通文件预览不得覆盖当前 OA 输入"],
        });
        ordinaryPreviewResponseSent = true;
        return;
      }
      previewRequest = request;
      return fulfillJson(route, impactPreview(payload));
    }
    if (method === "POST" && apiPath === "/documents") {
      createRequest = request;
      return fulfillJson(route, createdDocument(request.postDataJSON()), 201);
    }

    return fulfillJson(route, { detail: "未处理的 Task30 模拟请求" }, 404);
  });

  await page.addInitScript(() => {
    window.localStorage.setItem("fpms_token", "document-deadline-create-ui-test-token");
  });

  await page.goto(`/documents/new?case_id=${caseId}&case_no=ADDGAP-DUE-001`, {
    waitUntil: "domcontentloaded",
  });

  await expect(page.getByRole("heading", { name: "登记往来文件" })).toBeVisible();
  await page.getByLabel("标题").fill("第一次审查意见通知书");
  await expect
    .poll(() => previewPayloads.filter((payload) => payload.doc_template_id === null).length)
    .toBeGreaterThan(0);

  const templateField = page.locator(".el-form-item").filter({ hasText: "文件模板" }).first();
  await templateField.getByRole("combobox").click();
  await page.getByRole("option", { name: "OA_IN — 审查意见通知书（收文）" }).click();

  await expect
    .poll(() => previewPayloads.filter((payload) => payload.doc_template_id === templateId).length)
    .toBe(0);
  await expect(page.getByText("请填写并确认官方截止日")).toHaveCount(0);
  releaseOrdinaryPreview();
  await expect.poll(() => ordinaryPreviewResponseSent).toBe(true);
  await expect(page.getByText("过期普通文件预览不得覆盖当前 OA 输入")).toHaveCount(0);
  await page.getByPlaceholder("请选择官方截止日").fill("2026-10-15");
  await expect
    .poll(() => previewPayloads.filter((payload) => payload.doc_template_id === templateId).length)
    .toBe(0);

  const sourceField = page.locator(".el-form-item").filter({ hasText: "截止日来源" }).first();
  await sourceField.locator(".el-select__wrapper").click();
  await page.getByRole("option", { name: "人工核对官方通知" }).click();
  await expect
    .poll(() => previewPayloads.filter((payload) => payload.doc_template_id === templateId).length)
    .toBe(0);

  const statusField = page.locator(".el-form-item").filter({ hasText: "确认状态" }).first();
  await statusField.locator(".el-select__wrapper").click();
  await page.getByRole("option", { name: "已确认" }).click();

  await expect
    .poll(() => previewPayloads.filter((payload) => payload.doc_template_id === templateId).length)
    .toBe(1);
  await expect.poll(() => previewRequest?.postDataJSON()).toMatchObject({
    official_due_date: "2026-10-15",
    official_due_date_source: "MANUAL_OFFICIAL_NOTICE",
    official_due_date_status: "CONFIRMED",
  });
  await expect(page.getByText("官方截止日：2026-10-15", { exact: false })).toBeVisible();
  await expect(
    page.getByText("来源 MANUAL_OFFICIAL_NOTICE；确认状态 CONFIRMED", { exact: true }),
  ).toBeVisible();

  const documentTypeField = page.locator(".el-form-item").filter({ hasText: "文件类型" }).first();
  await documentTypeField.locator(".el-select__wrapper").click();
  await page.getByRole("option", { name: "官方来文" }).click();
  await page.getByRole("button", { name: "登记往来文件" }).click();

  await expect.poll(() => createRequest?.postDataJSON()).toMatchObject({
    case_id: caseId,
    doc_template_id: templateId,
    official_due_date: "2026-10-15",
    official_due_date_source: "MANUAL_OFFICIAL_NOTICE",
    official_due_date_status: "CONFIRMED",
  });
  await expect(page.getByText("往来文件登记成功")).toBeVisible();
});

async function fulfillJson(route: Route, body: unknown, status = 200): Promise<void> {
  await route.fulfill({ status, contentType: "application/json", body: JSON.stringify(body) });
}

function hasConfirmedDeadline(payload: Record<string, unknown>): boolean {
  return Boolean(
    payload.official_due_date &&
      payload.official_due_date_source &&
      payload.official_due_date_status === "CONFIRMED",
  );
}

function backendCase(): Record<string, unknown> {
  return {
    id: caseId,
    case_no: "ADDGAP-DUE-001",
    case_type: "NORMAL",
    patent_category: "INV",
    flow_dir: "CN_DOMESTIC",
    title_cn: "官方截止日录入测试案件",
    status: "SUB_EXAM",
    applicants: [],
    inventors: [],
    priorities: [],
    bio_deposits: [],
    agent_splits: [],
  };
}

function oaTemplate(): Record<string, unknown> {
  return {
    id: templateId,
    code: "OA_IN",
    name: "审查意见通知书（收文）",
    direction: "IN",
    enabled: true,
    status_effect: "OA1",
    status_restore: null,
    deadline_template_code: "OA_REPLY",
    fee_draft_type: null,
    fee_item_list: null,
    need_reply: true,
    reply_to_template_code: null,
    input_fields: null,
  };
}

function impactPreview(payload: Record<string, unknown>): Record<string, unknown> {
  return {
    case_id: caseId,
    case_no: "ADDGAP-DUE-001",
    template_code: payload.doc_template_id === templateId ? "OA_IN" : null,
    official_due_date: payload.official_due_date ?? null,
    official_due_date_source: payload.official_due_date_source ?? null,
    official_due_date_status: payload.official_due_date_status ?? null,
    description: payload.description ?? null,
    status_impacts: [],
    deadline_impacts: hasConfirmedDeadline(payload)
      ? [
          {
            kind: "OFFICIAL_DUE_DATE",
            title: "官方截止日",
            effect: payload.official_due_date,
            enabled: true,
            requires_confirmation: false,
            detail: "来源 MANUAL_OFFICIAL_NOTICE；确认状态 CONFIRMED",
          },
        ]
      : [],
    task_impacts: [],
    fee_impacts: [],
    file_status_impacts: [],
    confirmation_required: false,
    confirmation_items: [],
    risk_tips: [],
  };
}

function createdDocument(payload: Record<string, unknown>): Record<string, unknown> {
  return {
    id: "created-document-1",
    ...payload,
    created_at: "2026-07-11T00:00:00",
    updated_at: "2026-07-11T00:00:00",
    attachments: [],
  };
}
