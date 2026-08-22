import { expect, test } from "@playwright/test";
import type { Page, Request, Route } from "@playwright/test";

const templatePermissionTip = "缺少文书模板读取权限，无法选择更正通知模板";

test("replacement action fails closed for template permission and inactive lineage", async ({ page }) => {
  let templateRequests = 0;
  await mockPage(page, ["GrantFeeTask.Read", "GrantFeeTask.Write", "Doc.Create"], async (route) => {
    templateRequests += 1;
    return fulfillJson(route, templateList());
  });

  await gotoGrantTasks(page);

  const confirmedRow = taskRow(page, "ADDGAP-REPLACE-CONFIRMED");
  const replacementButton = confirmedRow.getByRole("button", { name: "更正通知" });
  await expect(replacementButton).toBeVisible();
  await expect(replacementButton).toBeDisabled();
  await expect(replacementButton).toHaveAttribute("title", templatePermissionTip);
  await expect(confirmedRow).toContainText(templatePermissionTip);

  const legacyRow = taskRow(page, "ADDGAP-REPLACE-LEGACY");
  await expect(legacyRow).toContainText("历史数据待核验，不能发起更正通知");
  await expect(legacyRow.getByRole("button", { name: "更正通知" })).toHaveCount(0);

  const supersededRow = taskRow(page, "ADDGAP-REPLACE-SUPERSEDED");
  await expect(supersededRow).toContainText("该任务已被替代，不能再次发起更正通知");
  await expect(supersededRow.getByRole("button", { name: "更正通知" })).toHaveCount(0);
  expect(templateRequests).toBe(0);
});

test("replacement dialog filters templates, posts a stable nested payload, and distinguishes reuse", async ({ page }) => {
  let templateRequestUrl = "";
  let listRequests = 0;
  const replacementRequests: Request[] = [];

  await mockPage(
    page,
    ["GrantFeeTask.Read", "GrantFeeTask.Write", "Doc.Create", "DocTemplate.Read"],
    async (route) => {
      templateRequestUrl = route.request().url();
      return fulfillJson(route, templateList());
    },
    async (route) => {
      replacementRequests.push(route.request());
      await new Promise((resolve) => setTimeout(resolve, 150));
      return fulfillJson(route, replacementResult(replacementRequests.length > 1));
    },
    () => {
      listRequests += 1;
    },
  );

  await gotoGrantTasks(page);
  await openReplacementDialog(page);

  const query = new URL(templateRequestUrl).searchParams;
  expect(query.get("direction")).toBe("IN");
  expect(query.get("enabled")).toBe("true");
  expect(query.get("page_size")).toBe("100");

  const dialog = page.getByRole("dialog", { name: "登记更正授权通知" });
  await expect(dialog.getByText("案件", { exact: true })).toHaveCount(0);
  await expect(dialog.getByText("收发方向", { exact: true })).toHaveCount(0);
  await chooseTemplate(page, dialog);
  await fillReplacementForm(page, dialog);

  const submitButton = dialog.getByRole("button", { name: "提交更正通知" });
  await submitButton.click();
  await expect(submitButton).toBeDisabled();
  await expect(page.getByText("更正通知创建成功")).toBeVisible();
  await expect(dialog).toBeHidden();
  expect(replacementRequests).toHaveLength(1);
  expect(listRequests).toBeGreaterThanOrEqual(2);

  await openReplacementDialog(page);
  const retryDialog = page.getByRole("dialog", { name: "登记更正授权通知" });
  await chooseTemplate(page, retryDialog);
  await fillReplacementForm(page, retryDialog);
  await retryDialog.getByRole("button", { name: "提交更正通知" }).click();
  await expect(page.getByText("已复用同一更正通知结果")).toBeVisible();
  await expect(retryDialog).toBeHidden();

  expect(replacementRequests).toHaveLength(2);
  expect(replacementRequests[0].postDataJSON()).toEqual(replacementRequests[1].postDataJSON());
  expect(replacementRequests[0].postDataJSON()).toEqual({
    idempotency_key: "replacement-request-key-001",
    reason: "官方重新发文并更正缴费期限",
    document: {
      doc_template_id: "grant-template-executable",
      doc_date: "2026-07-15",
      title: "更正后的授权通知书",
      ref_no: "GRANT-REPLACEMENT-001",
      official_due_date: "2026-09-15",
      official_due_date_source: "MANUAL_OFFICIAL_NOTICE",
      official_due_date_status: "CONFIRMED",
      description: "客户确认的更正授权通知",
    },
  });
});

test("replacement conflict keeps the dialog and request key for retry", async ({ page }) => {
  let capturedPayload: Record<string, unknown> | null = null;
  await mockPage(
    page,
    ["GrantFeeTask.Read", "GrantFeeTask.Write", "Doc.Create", "DocTemplate.Read"],
    async (route) => fulfillJson(route, templateList()),
    async (route) => {
      capturedPayload = route.request().postDataJSON() as Record<string, unknown>;
      return fulfillJson(
        route,
        {
          error: {
            code: "GRANT_REPLACEMENT_IDEMPOTENCY_CONFLICT",
            message: "conflict",
            details: {},
          },
        },
        409,
      );
    },
  );

  await gotoGrantTasks(page);
  await openReplacementDialog(page);
  const dialog = page.getByRole("dialog", { name: "登记更正授权通知" });
  await chooseTemplate(page, dialog);
  await fillReplacementForm(page, dialog);
  await dialog.getByRole("button", { name: "提交更正通知" }).click();

  await expect(page.getByText("去重键已用于不同内容，请核对后重试")).toBeVisible();
  await expect(dialog).toBeVisible();
  await expect(dialog.getByPlaceholder("请输入去重键")).toHaveValue("replacement-request-key-001");
  await expect(dialog.getByPlaceholder("请输入文书标题")).toHaveValue("更正后的授权通知书");
  expect(capturedPayload).not.toBeNull();
});

async function mockPage(
  page: Page,
  permissions: string[],
  templateHandler: (route: Route) => Promise<void>,
  replacementHandler?: (route: Route) => Promise<void>,
  onList?: () => void,
): Promise<void> {
  await page.route("**/api/v1/**", async (route) => {
    const request = route.request();
    const apiPath = new URL(request.url()).pathname.replace(/^\/api\/v1/, "");

    if (request.method() === "GET" && apiPath === "/auth/me") {
      return fulfillJson(route, { permissions });
    }
    if (request.method() === "GET" && apiPath === "/grant-fee-tasks/list") {
      onList?.();
      return fulfillJson(route, { items: grantFeeTasks(), page: 1, page_size: 20, total: 3 });
    }
    if (request.method() === "GET" && apiPath === "/doc-templates") {
      return templateHandler(route);
    }
    if (request.method() === "POST" && apiPath === "/grant-fee-tasks/task-confirmed/replacement-notice") {
      if (!replacementHandler) {
        return fulfillJson(route, { detail: "replacement handler missing" }, 500);
      }
      return replacementHandler(route);
    }

    return fulfillJson(route, { detail: "未处理的 Task44 模拟请求" }, 404);
  });

  await page.addInitScript(() => {
    window.localStorage.setItem("fpms_token", "grant-replacement-ui-test-token");
  });
}

async function gotoGrantTasks(page: Page): Promise<void> {
  await page.goto("/grant-fee/tasks", { waitUntil: "domcontentloaded" });
  await expect(page.getByRole("heading", { name: "授权费任务看板" })).toBeVisible();
  await expect(taskRow(page, "ADDGAP-REPLACE-CONFIRMED")).toContainText("来源已确认");
}

function taskRow(page: Page, caseNo: string) {
  return page.getByRole("row").filter({ hasText: caseNo });
}

async function openReplacementDialog(page: Page): Promise<void> {
  await taskRow(page, "ADDGAP-REPLACE-CONFIRMED")
    .getByRole("button", { name: "更正通知" })
    .click();
  await expect(page.getByRole("dialog", { name: "登记更正授权通知" })).toBeVisible();
}

async function chooseTemplate(page: Page, dialog: ReturnType<Page["getByRole"]>): Promise<void> {
  const templateField = dialog.locator(".el-form-item").filter({ hasText: "文书模板" }).first();
  await templateField.getByRole("combobox").click();
  const options = page.getByRole("option");
  await expect(options).toHaveCount(1);
  await page.getByRole("option", { name: "OFFICIAL_NOTICE_009 — 授权通知书-电子" }).click();
}

async function fillReplacementForm(
  page: Page,
  dialog: ReturnType<Page["getByRole"]>,
): Promise<void> {
  await dialog.getByPlaceholder("请选择文书日期").fill("2026-07-15");
  await dialog.getByPlaceholder("请输入文书标题").fill("更正后的授权通知书");
  await dialog.getByPlaceholder("请输入文号").fill("GRANT-REPLACEMENT-001");
  await dialog.getByPlaceholder("请选择官方期限").fill("2026-09-15");

  const sourceField = dialog.locator(".el-form-item").filter({ hasText: "期限来源" }).first();
  await sourceField.locator(".el-select__wrapper").click();
  await page.getByRole("option", { name: "人工核对官方通知" }).click();

  await expect(dialog.getByText("已确认", { exact: true })).toBeVisible();
  await dialog.getByPlaceholder("请输入替换原因").fill("官方重新发文并更正缴费期限");
  await dialog.getByPlaceholder("请输入去重键").fill("replacement-request-key-001");
  await dialog.getByPlaceholder("请输入可选说明").fill("客户确认的更正授权通知");
}

async function fulfillJson(route: Route, body: unknown, status = 200): Promise<void> {
  await route.fulfill({ status, contentType: "application/json", body: JSON.stringify(body) });
}

function templateList(): Record<string, unknown> {
  return {
    items: [
      docTemplate(
        "grant-template-executable",
        "OFFICIAL_NOTICE_009",
        "授权通知书-电子",
        JSON.stringify({ catalog_status: "EXECUTABLE", execution_behavior: "GRANT_NOTICE" }),
      ),
      docTemplate(
        "reference-template",
        "OFFICIAL_NOTICE_010",
        "专利证书",
        JSON.stringify({ catalog_status: "REFERENCE_ONLY", execution_behavior: null }),
      ),
      docTemplate(
        "oa-template",
        "OFFICIAL_NOTICE_003",
        "第一次审查意见通知书",
        JSON.stringify({ catalog_status: "EXECUTABLE", execution_behavior: "OA_REPLY" }),
      ),
      docTemplate("malformed-template", "OFFICIAL_NOTICE_999", "损坏模板", "{malformed"),
    ],
    page: 1,
    page_size: 100,
    total: 4,
  };
}

function docTemplate(id: string, code: string, name: string, inputFields: string): Record<string, unknown> {
  return {
    id,
    code,
    name,
    direction: "IN",
    enabled: true,
    status_effect: null,
    status_restore: null,
    deadline_template_code: null,
    fee_draft_type: null,
    fee_item_list: null,
    need_reply: false,
    reply_to_template_code: null,
    input_fields: inputFields,
    created_at: "2026-07-11T00:00:00",
    updated_at: "2026-07-11T00:00:00",
  };
}

function grantFeeTasks(): Array<Record<string, unknown>> {
  return [
    grantFeeTask("task-confirmed", "ADDGAP-REPLACE-CONFIRMED", "CONFIRMED"),
    grantFeeTask("task-legacy", "ADDGAP-REPLACE-LEGACY", "LEGACY_UNVERIFIED"),
    grantFeeTask("task-superseded", "ADDGAP-REPLACE-SUPERSEDED", "SUPERSEDED"),
  ];
}

function grantFeeTask(taskId: string, caseNo: string, lineageStatus: string): Record<string, unknown> {
  return {
    task_id: taskId,
    case_id: `case-${taskId}`,
    case_no: caseNo,
    status: "OPEN",
    lineage_status: lineageStatus,
    source_document_id: lineageStatus === "LEGACY_UNVERIFIED" ? null : `doc-${taskId}`,
    deadline_source: lineageStatus === "LEGACY_UNVERIFIED" ? null : "MANUAL_OFFICIAL_NOTICE",
    deadline_confirmed_at: lineageStatus === "LEGACY_UNVERIFIED" ? null : "2026-07-10T09:30:00",
    due_date: "2026-08-28",
    client_instruction: "NONE",
    gov_fee_amt: 1200,
    service_fee_amt: 300,
    currency: "CNY",
    draft_generated: false,
    notice_sent: false,
    notify_count: 0,
    is_overdue: false,
    billed: false,
    linked_bill_id: null,
    linked_bill_no: null,
    trigger_rule: "收到授权通知书",
    deadline_rule: "以授权通知书载明期限为准",
    fee_basis: "授权阶段官费",
    fee_node_explanation: "客户确认后生成草单",
  };
}

function replacementResult(reused: boolean): Record<string, unknown> {
  return {
    document: { id: "replacement-document-1" },
    replacement_task: grantFeeTask("replacement-task-1", "ADDGAP-REPLACE-CONFIRMED", "CONFIRMED"),
    superseded_task_id: "task-confirmed",
    reused,
  };
}
