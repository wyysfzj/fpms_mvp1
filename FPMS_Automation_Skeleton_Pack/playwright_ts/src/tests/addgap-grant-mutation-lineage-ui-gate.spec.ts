import { expect, test } from "@playwright/test";
import type { Page, Route } from "@playwright/test";

const blockedReason = "来源未确认或已被替代，不能执行授权费操作";

test("ordinary grant mutations fail closed for non-confirmed lineage", async ({ page }) => {
  const calls: Array<{ method: string; path: string; body: unknown }> = [];

  await page.route("**/api/v1/**", async (route) => {
    const request = route.request();
    const apiPath = new URL(request.url()).pathname.replace(/^\/api\/v1/, "");

    if (request.method() === "GET" && apiPath === "/auth/me") {
      return fulfillJson(route, {
        permissions: [
          "GrantFeeTask.Read",
          "GrantFeeTask.Write",
          "Doc.Create",
          "DocTemplate.Read",
        ],
      });
    }
    if (request.method() === "GET" && apiPath === "/grant-fee-tasks/list") {
      return fulfillJson(route, { items: grantFeeTasks(), page: 1, page_size: 20, total: 4 });
    }
    if (request.method() === "POST" && apiPath === "/grant-fee-tasks/confirmed-ready/generate-draft") {
      calls.push({ method: request.method(), path: apiPath, body: request.postDataJSON() });
      return fulfillJson(route, {
        task_id: "confirmed-ready",
        case_id: "case-confirmed-ready",
        draft_id: "draft-confirmed-ready",
        draft_type: "GRANT_FEE",
        state: "DRAFT_GENERATED",
        draft_generated: true,
        currency: "CNY",
        amount: 1500,
        item_count: 2,
        reused: false,
      });
    }
    if (request.method() === "PUT" && apiPath === "/grant-fee-tasks/confirmed-draft/state") {
      calls.push({ method: request.method(), path: apiPath, body: request.postDataJSON() });
      return fulfillJson(route, grantFeeState("confirmed-draft", "DONE"));
    }
    if (request.method() === "POST" && apiPath === "/grant-fee-tasks/batch-instruction") {
      calls.push({ method: request.method(), path: apiPath, body: request.postDataJSON() });
      return fulfillJson(route, {
        success_count: 1,
        failure_count: 0,
        updated_task_ids: ["confirmed-ready"],
      });
    }
    if (
      apiPath.includes("legacy-ready")
      || apiPath.includes("superseded-draft")
      || apiPath === "/grant-fee-tasks/generate-notices"
    ) {
      calls.push({ method: request.method(), path: apiPath, body: request.postDataJSON() });
      return fulfillJson(route, { detail: "非确认沿革不得调用 mutation API" }, 500);
    }

    return fulfillJson(route, { detail: "未处理的 Task60 模拟请求" }, 404);
  });

  await page.addInitScript(() => {
    window.localStorage.setItem("fpms_token", "grant-mutation-lineage-ui-gate-test-token");
  });

  await page.goto("/grant-fee/tasks", { waitUntil: "domcontentloaded" });
  await expect(page.getByRole("heading", { name: "授权费任务看板" })).toBeVisible();

  const legacyRow = taskRow(page, "ADDGAP-MUTATION-LEGACY");
  await expect(legacyRow).toContainText("历史数据待核验");
  await expect(legacyRow).toContainText(blockedReason);
  await expect(legacyRow.getByRole("checkbox")).toBeDisabled();
  await expect(legacyRow.getByRole("button", { name: "生成草单" })).toBeDisabled();
  await expect(legacyRow.getByRole("button", { name: "标记完成" })).toBeDisabled();

  const supersededRow = taskRow(page, "ADDGAP-MUTATION-SUPERSEDED");
  await expect(supersededRow).toContainText("已被替代");
  await expect(supersededRow).toContainText(blockedReason);
  await expect(supersededRow.getByRole("checkbox")).toBeDisabled();
  await expect(supersededRow.getByRole("button", { name: "生成草单" })).toBeDisabled();
  await expect(supersededRow.getByRole("button", { name: "标记完成" })).toBeDisabled();

  const readyRow = taskRow(page, "ADDGAP-MUTATION-CONFIRMED-READY");
  await expect(readyRow).toContainText("来源已确认");
  await expect(readyRow.getByRole("checkbox")).toBeEnabled();
  await expect(readyRow.getByRole("button", { name: "生成草单" })).toBeEnabled();
  await readyRow.getByRole("button", { name: "生成草单" }).click();
  await expect(page.getByText("草单生成成功")).toBeVisible();

  const draftRow = taskRow(page, "ADDGAP-MUTATION-CONFIRMED-DRAFT");
  await expect(draftRow.getByRole("button", { name: "标记完成" })).toBeEnabled();
  await draftRow.getByRole("button", { name: "标记完成" }).click();
  await expect(page.getByText("授权费任务已标记完成")).toBeVisible();

  await taskRow(page, "ADDGAP-MUTATION-CONFIRMED-READY").locator(".el-checkbox").click();
  await page.getByRole("button", { name: "批量标记支付" }).click();
  await page.getByRole("button", { name: "确认", exact: true }).click();
  await expect(page.getByText("已批量更新 1 条授权费任务为支付")).toBeVisible();

  expect(calls).toEqual([
    {
      method: "POST",
      path: "/grant-fee-tasks/confirmed-ready/generate-draft",
      body: null,
    },
    {
      method: "PUT",
      path: "/grant-fee-tasks/confirmed-draft/state",
      body: { action: "mark_done" },
    },
    {
      method: "POST",
      path: "/grant-fee-tasks/batch-instruction",
      body: { task_ids: ["confirmed-ready"], action: "record_pay_instruction" },
    },
  ]);
});

function taskRow(page: Page, caseNo: string) {
  return page.getByRole("row").filter({ hasText: caseNo });
}

async function fulfillJson(route: Route, body: unknown, status = 200): Promise<void> {
  await route.fulfill({ status, contentType: "application/json", body: JSON.stringify(body) });
}

function grantFeeTasks(): Array<Record<string, unknown>> {
  return [
    grantFeeTask("confirmed-ready", "ADDGAP-MUTATION-CONFIRMED-READY", "READY_TO_DRAFT", "CONFIRMED", false),
    grantFeeTask("confirmed-draft", "ADDGAP-MUTATION-CONFIRMED-DRAFT", "DRAFT_GENERATED", "CONFIRMED", true),
    grantFeeTask("legacy-ready", "ADDGAP-MUTATION-LEGACY", "READY_TO_DRAFT", "LEGACY_UNVERIFIED", false),
    grantFeeTask("superseded-draft", "ADDGAP-MUTATION-SUPERSEDED", "DRAFT_GENERATED", "SUPERSEDED", true),
  ];
}

function grantFeeTask(
  taskId: string,
  caseNo: string,
  status: string,
  lineageStatus: string,
  draftGenerated: boolean,
): Record<string, unknown> {
  return {
    task_id: taskId,
    case_id: `case-${taskId}`,
    case_no: caseNo,
    status,
    lineage_status: lineageStatus,
    source_document_id: lineageStatus === "LEGACY_UNVERIFIED" ? null : `doc-${taskId}`,
    deadline_source: lineageStatus === "LEGACY_UNVERIFIED" ? null : "MANUAL_OFFICIAL_NOTICE",
    deadline_confirmed_at: lineageStatus === "LEGACY_UNVERIFIED" ? null : "2026-07-10T09:30:00",
    due_date: "2026-08-28",
    client_instruction: "NONE",
    gov_fee_amt: 1200,
    service_fee_amt: 300,
    currency: "CNY",
    draft_generated: draftGenerated,
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

function grantFeeState(taskId: string, state: string): Record<string, unknown> {
  return {
    task_id: taskId,
    case_id: `case-${taskId}`,
    state,
    lineage_status: "CONFIRMED",
    source_document_id: `doc-${taskId}`,
    deadline_source: "MANUAL_OFFICIAL_NOTICE",
    deadline_confirmed_at: "2026-07-10T09:30:00",
    client_instruction: "PAY",
    notify_count: 1,
    draft_generated: true,
    notice_sent: true,
    is_overdue: false,
    allowed_actions: [],
    trigger_rule: "收到授权通知书",
    deadline_rule: "以授权通知书载明期限为准",
    fee_basis: "授权阶段官费",
    fee_node_explanation: "客户确认后生成草单",
  };
}
