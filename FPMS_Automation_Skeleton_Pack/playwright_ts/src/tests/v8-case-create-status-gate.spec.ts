import { expect, test } from "@playwright/test";
import type { Request, Route } from "@playwright/test";

test("CaseCreate explains automatic lifecycle initialization and omits status", async ({ page }) => {
  let createRequest: Request | null = null;

  await page.route("**/api/v1/**", async (route) => {
    const request = route.request();
    const apiPath = new URL(request.url()).pathname.replace(/^\/api\/v1/, "");

    if (request.method() === "GET" && apiPath === "/auth/me") {
      return fulfillJson(route, { permissions: ["Case.Create", "Client.Read"] });
    }
    if (request.method() === "GET" && apiPath === "/clients") {
      return fulfillJson(route, {
        items: [{ id: "client-v8-status-gate", name_cn: "生命周期测试客户" }],
        page: 1,
        page_size: 100,
        total: 1,
      });
    }
    if (request.method() === "GET" && apiPath === "/cases/document-gate/intake-preview") {
      return fulfillJson(route, intakeGatePreview());
    }
    if (request.method() === "POST" && apiPath === "/cases") {
      createRequest = request;
      return fulfillJson(route, createdCase(request.postDataJSON()), 201);
    }

    return fulfillJson(route, { detail: "未处理的 V8 案件创建状态门禁模拟请求" }, 404);
  });

  await page.addInitScript(() => {
    window.localStorage.setItem("fpms_token", "v8-case-create-status-gate-token");
  });

  await page.goto("/cases/new", { waitUntil: "domcontentloaded" });

  await expect(page.getByRole("heading", { name: "新建案件" })).toBeVisible();
  await expect(
    page.getByText("创建成功后，系统将自动初始化案件生命周期；后续状态由业务事件推进，不能在新建页面直接指定。"),
  ).toBeVisible();
  await expect(
    page.locator(".el-form-item").filter({ hasText: /^(案件状态|法律状态|状态)$/ }),
  ).toHaveCount(0);
  await expect(page.locator('[name="status"], [data-field="status"]')).toHaveCount(0);

  await page.getByPlaceholder("请输入案号（例如：P2024-001）").fill("V8-STATUS-GATE-001");
  await page.getByRole("combobox", { name: "*客户", exact: true }).click();
  await page.getByRole("option", { name: "生命周期测试客户" }).click();
  await page.getByText("控制标记", { exact: true }).click();
  await page
    .locator(".el-form-item")
    .filter({ hasText: "费用减缓比例" })
    .locator(".el-select__wrapper")
    .click();
  await page.getByRole("option", { name: "不减免（0）" }).click();
  await page.getByRole("button", { name: "创建案件" }).click();

  await expect.poll(() => createRequest?.postDataJSON()).toMatchObject({
    case_no: "V8-STATUS-GATE-001",
    client_id: "client-v8-status-gate",
    fee_reduction: "0",
  });
  expect(createRequest?.postDataJSON()).not.toHaveProperty("status");
});

async function fulfillJson(route: Route, body: unknown, status = 200): Promise<void> {
  await route.fulfill({ status, contentType: "application/json", body: JSON.stringify(body) });
}

function intakeGatePreview(): Record<string, unknown> {
  return {
    case_type: "NORMAL",
    patent_category: "INV",
    flow_dir: "CN_DOMESTIC",
    material_count: 0,
    checks: [],
    missing_items: [],
    hard_block: false,
    afterfill_audit_required: false,
    conclusion: "PASS",
    suggested_actions: [],
  };
}

function createdCase(payload: Record<string, unknown>): Record<string, unknown> {
  return {
    id: "case-v8-status-gate",
    ...payload,
    status: "NOT_FILED",
    applicants: [],
    inventors: [],
    priorities: [],
    bio_deposits: [],
    agent_splits: [],
    created_at: "2026-07-15T00:00:00",
    updated_at: "2026-07-15T00:00:00",
  };
}
