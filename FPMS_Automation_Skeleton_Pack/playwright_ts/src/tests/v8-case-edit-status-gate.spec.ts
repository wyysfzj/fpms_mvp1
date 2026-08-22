import { expect, test } from "@playwright/test";
import type { Request, Route } from "@playwright/test";

const caseId = "case-v8-edit-status-gate";
const caseNo = "V8-EDIT-STATUS-GATE-001";

test("CaseEdit displays compatibility status read-only and omits it from updates", async ({ page }) => {
  let updateRequest: Request | null = null;

  await page.route("**/api/v1/**", async (route) => {
    const request = route.request();
    const apiPath = new URL(request.url()).pathname.replace(/^\/api\/v1/, "");

    if (request.method() === "GET" && apiPath === "/auth/me") {
      return fulfillJson(route, { permissions: ["*"] });
    }
    if (request.method() === "GET" && apiPath === "/clients") {
      return fulfillJson(route, { items: [], page: 1, page_size: 100, total: 0 });
    }
    if (request.method() === "GET" && apiPath === "/cases") {
      return fulfillJson(route, {
        items: [backendCase()],
        page: 1,
        page_size: 1,
        total: 1,
        summary: { total_case_count: 1 },
      });
    }
    if (request.method() === "GET" && apiPath === `/cases/${caseId}`) {
      return fulfillJson(route, backendCase());
    }
    if (request.method() === "PUT" && apiPath === `/cases/${caseId}`) {
      updateRequest = request;
      return fulfillJson(route, { ...backendCase(), ...request.postDataJSON() });
    }

    return fulfillJson(route, { detail: "未处理的 V8 案件编辑状态门禁模拟请求" }, 404);
  });

  await page.addInitScript(() => {
    window.localStorage.setItem("fpms_token", "v8-case-edit-status-gate-token");
  });

  await page.goto(`/cases/no/${caseNo}/edit`, { waitUntil: "domcontentloaded" });

  await expect(page.getByRole("heading", { name: "编辑案件" })).toBeVisible();
  const statusField = page.locator(".el-form-item").filter({ hasText: "法律状态" });
  await expect(statusField.getByRole("textbox")).toHaveValue("未递交");
  await expect(statusField.getByRole("textbox")).toBeDisabled();
  await expect(statusField.getByRole("combobox")).toHaveCount(0);
  await expect(page.getByText("兼容状态由案件生命周期维护，此处仅供查看，保存时不会提交。")).toBeVisible();

  await page.getByRole("button", { name: "保存修改" }).click();

  await expect.poll(() => updateRequest?.postDataJSON()).toBeTruthy();
  expect(updateRequest?.postDataJSON()).not.toHaveProperty("status");
});

async function fulfillJson(route: Route, body: unknown, status = 200): Promise<void> {
  await route.fulfill({ status, contentType: "application/json", body: JSON.stringify(body) });
}

function backendCase(): Record<string, unknown> {
  return {
    id: caseId,
    case_no: caseNo,
    case_type: "NORMAL",
    patent_category: "INV",
    flow_dir: "CN_DOMESTIC",
    client_id: "client-v8-edit-status-gate",
    client_name: "生命周期测试客户",
    title_cn: "兼容状态只读测试案件",
    status: "NOT_FILED",
    fee_reduction: "0",
    applicants: [],
    inventors: [],
    priorities: [],
    bio_deposits: [],
    agent_splits: [],
    created_at: "2026-07-15T00:00:00",
    updated_at: "2026-07-15T00:00:00",
  };
}
