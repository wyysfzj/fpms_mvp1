import { expect, test } from "@playwright/test";
import type { Page, Request, Route } from "@playwright/test";

const clientId = "client-v8-fee-reduction";

test("CaseCreate starts fee reduction unset and sends zero only after an explicit choice", async ({ page }) => {
  const createRequests: Request[] = [];
  await mockCaseCreateApi(page, async (route, request) => {
    createRequests.push(request);
    await fulfillJson(route, createdCase(request.postDataJSON()), 201);
  });

  await openCaseCreate(page);
  await openControlFlags(page);

  const reductionSelect = feeReductionSelect(page);
  await expect(reductionSelect).toHaveValue("");
  await expect(
    page.getByText("选择 0.7 或 0.85 前，必须已记录与当前申请人组合匹配的费用减缓审批；系统不会自动选择审批依据。"),
  ).toBeVisible();

  await openFeeReductionOptions(page);
  await expect(page.getByRole("option", { name: "不减免（0）" })).toBeVisible();
  await expect(page.getByRole("option", { name: "减免 70%（0.7）" })).toBeVisible();
  await expect(page.getByRole("option", { name: "减免 85%（0.85）" })).toBeVisible();
  await expect(page.getByRole("option", { name: /部分减免|全额减免/ })).toHaveCount(0);
  await page.keyboard.press("Escape");

  await fillRequiredFields(page, "V8-FEE-REDUCTION-ZERO");
  await page.getByRole("button", { name: "创建案件" }).click();

  await expect(page.getByText("请选择费用减缓比例")).toBeVisible();
  expect(createRequests).toHaveLength(0);

  await openFeeReductionOptions(page);
  await page.getByRole("option", { name: "不减免（0）" }).click();
  await page.getByRole("button", { name: "创建案件" }).click();

  await expect.poll(() => createRequests.length).toBe(1);
  const payload = createRequests[0].postDataJSON();
  expect(payload.fee_reduction).toBe("0");
  expect(["NONE", "PARTIAL", "FULL"]).not.toContain(payload.fee_reduction);
});

for (const choice of [
  { label: "减免 70%（0.7）", ratio: "0.7" },
  { label: "减免 85%（0.85）", ratio: "0.85" },
]) {
  test(`CaseCreate submits canonical ${choice.ratio} and surfaces an ambiguous-approval conflict`, async ({ page }) => {
    const createRequests: Request[] = [];
    await mockCaseCreateApi(page, async (route, request) => {
      createRequests.push(request);
      await fulfillJson(
        route,
        {
          error: {
            code: "FEE_REDUCTION_AMBIGUOUS_PROVENANCE",
            message: "存在多条适用的费用减缓审批，无法确定唯一审批依据。",
            details: { scope_type: "APPLICANT_SET", fee_code: "CASE_CREATE" },
          },
        },
        409,
      );
    });

    await openCaseCreate(page);
    await fillRequiredFields(page, `V8-FEE-REDUCTION-${choice.ratio.replace(".", "")}`);
    await openControlFlags(page);
    await openFeeReductionOptions(page);
    await page.getByRole("option", { name: choice.label }).click();
    await page.getByRole("button", { name: "创建案件" }).click();

    await expect.poll(() => createRequests.length).toBe(1);
    const payload = createRequests[0].postDataJSON();
    expect(payload.fee_reduction).toBe(choice.ratio);
    expect(["NONE", "PARTIAL", "FULL"]).not.toContain(payload.fee_reduction);
    await expect(page.getByText("存在多条适用的费用减缓审批，无法确定唯一审批依据。")).toBeVisible();
    await expect(page).toHaveURL(/\/cases\/new$/);
  });
}

async function mockCaseCreateApi(
  page: Page,
  handleCreate: (route: Route, request: Request) => Promise<void>,
): Promise<void> {
  await page.route("**/api/v1/**", async (route) => {
    const request = route.request();
    const apiPath = new URL(request.url()).pathname.replace(/^\/api\/v1/, "");

    if (request.method() === "GET" && apiPath === "/auth/me") {
      return fulfillJson(route, { permissions: ["Case.Create", "Client.Read"] });
    }
    if (request.method() === "GET" && apiPath === "/clients") {
      return fulfillJson(route, {
        items: [{ id: clientId, name_cn: "费用减缓测试客户" }],
        page: 1,
        page_size: 100,
        total: 1,
      });
    }
    if (request.method() === "GET" && apiPath === "/cases/document-gate/intake-preview") {
      return fulfillJson(route, intakeGatePreview());
    }
    if (request.method() === "POST" && apiPath === "/cases") {
      await handleCreate(route, request);
      return;
    }

    return fulfillJson(route, { detail: "未处理的 V8 案件创建费用减缓模拟请求" }, 404);
  });
}

async function openCaseCreate(page: Page): Promise<void> {
  await page.addInitScript(() => {
    window.localStorage.setItem("fpms_token", "v8-case-create-fee-reduction-token");
  });
  await page.goto("/cases/new", { waitUntil: "domcontentloaded" });
  await expect(page.getByRole("heading", { name: "新建案件" })).toBeVisible();
}

async function openControlFlags(page: Page): Promise<void> {
  await page.getByText("控制标记", { exact: true }).click();
}

function feeReductionSelect(page: Page) {
  return page.locator(".el-form-item").filter({ hasText: "费用减缓比例" }).getByRole("combobox");
}

async function openFeeReductionOptions(page: Page): Promise<void> {
  await page
    .locator(".el-form-item")
    .filter({ hasText: "费用减缓比例" })
    .locator(".el-select__wrapper")
    .click();
}

async function fillRequiredFields(page: Page, caseNo: string): Promise<void> {
  await page.getByPlaceholder("请输入案号（例如：P2024-001）").fill(caseNo);
  await page.getByRole("combobox", { name: "*客户", exact: true }).click();
  await page.getByRole("option", { name: "费用减缓测试客户" }).click();
}

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
    id: "case-v8-fee-reduction",
    ...payload,
    status: "NOT_FILED",
    applicants: [],
    inventors: [],
    priorities: [],
    bio_deposits: [],
    agent_splits: [],
    created_at: "2026-07-21T00:00:00",
    updated_at: "2026-07-21T00:00:00",
  };
}
