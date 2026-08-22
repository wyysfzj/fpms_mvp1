import { expect, test } from "@playwright/test";
import type { Route } from "@playwright/test";

test("GrantFeeTaskList shows workflow status and grant lineage together", async ({ page }) => {
  await page.route("**/api/v1/**", async (route) => {
    const request = route.request();
    const apiPath = new URL(request.url()).pathname.replace(/^\/api\/v1/, "");

    if (request.method() === "GET" && apiPath === "/auth/me") {
      return fulfillJson(route, { permissions: ["GrantFeeTask.Read"] });
    }
    if (request.method() === "GET" && apiPath === "/grant-fee-tasks/list") {
      return fulfillJson(route, {
        items: grantFeeTasks(),
        page: 1,
        page_size: 20,
        total: 3,
      });
    }

    return fulfillJson(route, { detail: "未处理的 Task43 模拟请求" }, 404);
  });

  await page.addInitScript(() => {
    window.localStorage.setItem("fpms_token", "grant-lineage-ui-test-token");
  });

  await page.goto("/grant-fee/tasks", { waitUntil: "domcontentloaded" });
  await expect(page.getByRole("heading", { name: "授权费任务看板" })).toBeVisible();

  const confirmedRow = page.getByRole("row").filter({ hasText: "ADDGAP-GRANT-CONFIRMED" });
  await expect(confirmedRow).toContainText("待处理");
  await expect(confirmedRow).toContainText("来源已确认");
  await expect(confirmedRow).toContainText("来源文书");
  await expect(confirmedRow).toContainText("doc-confirmed-1");
  await expect(confirmedRow).toContainText("期限来源");
  await expect(confirmedRow).toContainText("人工核对官方通知");
  await expect(confirmedRow).toContainText("确认时间");
  await expect(confirmedRow).toContainText("2026-07-10 09:30:00");

  const legacyRow = page.getByRole("row").filter({ hasText: "ADDGAP-GRANT-LEGACY" });
  await expect(legacyRow).toContainText("等待客户");
  await expect(legacyRow).toContainText("历史数据待核验");
  await expect(legacyRow).toContainText("来源文书：未记录");
  await expect(legacyRow).toContainText("期限来源：未记录");
  await expect(legacyRow).toContainText("确认时间：未记录");

  const supersededRow = page.getByRole("row").filter({ hasText: "ADDGAP-GRANT-SUPERSEDED" });
  await expect(supersededRow).toContainText("已完成");
  await expect(supersededRow).toContainText("已被替代");
  await expect(supersededRow).toContainText("IMPORTED_VENDOR_NOTICE");
});

async function fulfillJson(route: Route, body: unknown, status = 200): Promise<void> {
  await route.fulfill({ status, contentType: "application/json", body: JSON.stringify(body) });
}

function grantFeeTasks(): Array<Record<string, unknown>> {
  return [
    grantFeeTask({
      task_id: "grant-task-confirmed",
      case_id: "case-confirmed",
      case_no: "ADDGAP-GRANT-CONFIRMED",
      status: "OPEN",
      lineage_status: "CONFIRMED",
      source_document_id: "doc-confirmed-1",
      deadline_source: "MANUAL_OFFICIAL_NOTICE",
      deadline_confirmed_at: "2026-07-10T09:30:00",
    }),
    grantFeeTask({
      task_id: "grant-task-legacy",
      case_id: "case-legacy",
      case_no: "ADDGAP-GRANT-LEGACY",
      status: "WAITING_CLIENT",
      lineage_status: "LEGACY_UNVERIFIED",
      source_document_id: null,
      deadline_source: null,
      deadline_confirmed_at: null,
    }),
    grantFeeTask({
      task_id: "grant-task-superseded",
      case_id: "case-superseded",
      case_no: "ADDGAP-GRANT-SUPERSEDED",
      status: "DONE",
      lineage_status: "SUPERSEDED",
      source_document_id: "doc-superseded-1",
      deadline_source: "IMPORTED_VENDOR_NOTICE",
      deadline_confirmed_at: "2026-07-09T16:45:00",
    }),
  ];
}

function grantFeeTask(overrides: Record<string, unknown>): Record<string, unknown> {
  return {
    due_date: "2026-08-10",
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
    ...overrides,
  };
}
