import { expect, test } from "@playwright/test";
import type { Page, Request, Route } from "@playwright/test";

const payListId = 222;
const artifactId = "11111111-1111-4111-8111-111111111222";
const secondArtifactId = "33333333-3333-4333-8333-333333333222";
const activityId = "22222222-2222-4222-8222-222222222222";
const evidenceHash = "a".repeat(64);

test("records and displays server acceptance separately from payment and ticket facts", async ({
  page,
}) => {
  let acceptanceRequest: Request | null = null;
  let accepted = false;
  let detailReads = 0;
  await mockPayListApi(page, {
    permissions: ["PayList.Read", "Fee.Edit"],
    officialWorkbookStatus: "ACTIVE",
    getArtifactStatus: () => (accepted ? "OFFICIAL_SITE_ACCEPTED" : "GENERATED"),
    onDetailRead: () => {
      detailReads += 1;
    },
    onAcceptance: async (route) => {
      acceptanceRequest = route.request();
      accepted = true;
      await fulfillJson(route, acceptanceResult(), 201);
    },
  });

  await openPayList(page);

  const panel = page.getByTestId("official-acceptance-panel");
  const artifact = panel.getByTestId(`official-acceptance-artifact-${artifactId}`);
  await expect(artifact.getByText("服务端：已生成，尚未登记官方接受")).toBeVisible();
  await expect(page.getByText("已计划", { exact: true })).toBeVisible();

  await artifact.getByRole("button", { name: "登记官方页面接受" }).click();
  await fillAcceptanceDialog(page);
  await page.getByRole("button", { name: "提交官方页面接受" }).click();

  await expect.poll(() => acceptanceRequest?.postDataJSON()).toMatchObject({
    artifact_id: artifactId,
    evidence_ref: "official-site/acceptance/receipt-222",
    evidence_sha256: evidenceHash,
    accepted_at: "2026-08-13T18:00:00",
  });
  expect(acceptanceRequest?.postDataJSON().idempotency_key).toMatch(/^[0-9a-f-]{36}$/i);

  const result = panel.getByTestId("official-acceptance-result");
  await expect(result.getByText("官方页面接受：已接受")).toBeVisible();
  await expect(result.getByText("支付：未支付")).toBeVisible();
  await expect(result.getByText("票据核验：未核验")).toBeVisible();
  await expect(result.getByText(`接受凭证引用：official-site/acceptance/receipt-222`)).toBeVisible();
  await expect(artifact.getByText("服务端：官方页面已接受")).toBeVisible();
  await expect(page.getByText("已计划", { exact: true })).toBeVisible();
  await expect(page.getByText("草稿", { exact: true })).toBeVisible();
  await expect.poll(() => detailReads).toBe(2);
});

test("official acceptance action fails closed without Fee.Edit", async ({ page }) => {
  let acceptanceCalls = 0;
  await mockPayListApi(page, {
    permissions: ["PayList.Read"],
    officialWorkbookStatus: "ACTIVE",
    getArtifactStatus: () => "GENERATED",
    onAcceptance: async (route) => {
      acceptanceCalls += 1;
      await fulfillJson(route, { detail: "不应登记官方接受" }, 500);
    },
  });

  await openPayList(page);

  const panel = page.getByTestId("official-acceptance-panel");
  await expect(panel.getByText("缺少登记官方页面接受权限")).toBeVisible();
  await expect(panel.getByRole("button", { name: "登记官方页面接受" })).toHaveCount(0);
  expect(acceptanceCalls).toBe(0);
});

for (const status of [undefined, "INACTIVE"] as const) {
  test(`official acceptance fails closed when workbook gate is ${status ?? "missing"}`, async ({
    page,
  }) => {
    let acceptanceCalls = 0;
    await mockPayListApi(page, {
      permissions: ["PayList.Read", "Fee.Edit"],
      officialWorkbookStatus: status,
      getArtifactStatus: () => "GENERATED",
      onAcceptance: async (route) => {
        acceptanceCalls += 1;
        await fulfillJson(route, { detail: "不应登记官方接受" }, 500);
      },
    });

    await openPayList(page);

    const panel = page.getByTestId("official-acceptance-panel");
    await expect(
      panel.getByText(
        status === undefined
          ? "官方工作簿门禁尚未开放，不能登记官方页面接受。"
          : "服务端模板状态为 INACTIVE，不能登记官方页面接受。",
      ),
    ).toBeVisible();
    await expect(panel.getByRole("button", { name: "登记官方页面接受" })).toHaveCount(0);
    expect(acceptanceCalls).toBe(0);
  });
}

test("clears prior acceptance facts before a different artifact fails", async ({ page }) => {
  let acceptanceCalls = 0;
  let firstAccepted = false;
  await mockPayListApi(page, {
    permissions: ["PayList.Read", "Fee.Edit"],
    officialWorkbookStatus: "ACTIVE",
    getArtifactStatus: () => (firstAccepted ? "OFFICIAL_SITE_ACCEPTED" : "GENERATED"),
    includeSecondArtifact: true,
    onAcceptance: async (route) => {
      acceptanceCalls += 1;
      if (acceptanceCalls === 1) {
        firstAccepted = true;
        await fulfillJson(route, acceptanceResult(), 201);
        return;
      }
      await fulfillJson(
        route,
        {
          error: {
            code: "PAYMENT_WORKBOOK_INPUT_CONFIG_REQUIRED",
            message: "Second artifact acceptance rejected",
            details: { gate_code: "DG-PAYMENT-WORKBOOK" },
          },
        },
        409,
      );
    },
  });

  await openPayList(page);
  const panel = page.getByTestId("official-acceptance-panel");
  await panel
    .getByTestId(`official-acceptance-artifact-${artifactId}`)
    .getByRole("button", { name: "登记官方页面接受" })
    .click();
  await fillAcceptanceDialog(page);
  await page.getByRole("button", { name: "提交官方页面接受" }).click();
  await expect(panel.getByTestId("official-acceptance-result")).toBeVisible();

  await panel
    .getByTestId(`official-acceptance-artifact-${secondArtifactId}`)
    .getByRole("button", { name: "登记官方页面接受" })
    .click();
  await expect(panel.getByTestId("official-acceptance-result")).toHaveCount(0);
  await fillAcceptanceDialog(page);
  await page.getByRole("button", { name: "提交官方页面接受" }).click();

  await expect(page.getByText("数据冲突，当前请求无法完成。")).toBeVisible();
  await expect(page.getByText("Second artifact acceptance rejected")).toHaveCount(0);
  await expect(panel.getByTestId("official-acceptance-result")).toHaveCount(0);
  await expect(
    panel
      .getByTestId(`official-acceptance-artifact-${secondArtifactId}`)
      .getByText("服务端：已生成，尚未登记官方接受"),
  ).toBeVisible();
});

test("official acceptance 409 retries with the same key and re-fetches server state", async ({
  page,
}) => {
  const acceptanceRequests: Request[] = [];
  let accepted = false;
  let detailReads = 0;
  await mockPayListApi(page, {
    permissions: ["PayList.Read", "Fee.Edit"],
    officialWorkbookStatus: "ACTIVE",
    getArtifactStatus: () => (accepted ? "OFFICIAL_SITE_ACCEPTED" : "GENERATED"),
    onDetailRead: () => {
      detailReads += 1;
    },
    onAcceptance: async (route) => {
      acceptanceRequests.push(route.request());
      if (acceptanceRequests.length === 2) {
        accepted = true;
        await fulfillJson(route, acceptanceResult(artifactId, "REUSED"), 200);
        return;
      }
      await fulfillJson(
        route,
        {
          error: {
            code: "PAYMENT_WORKBOOK_INPUT_CONFIG_REQUIRED",
            message: "Payment workbook input is not active",
            details: { gate_code: "DG-PAYMENT-WORKBOOK" },
          },
        },
        409,
      );
    },
  });

  await openPayList(page);
  const panel = page.getByTestId("official-acceptance-panel");
  await panel
    .getByTestId(`official-acceptance-artifact-${artifactId}`)
    .getByRole("button", { name: "登记官方页面接受" })
    .click();
  await fillAcceptanceDialog(page);
  const submit = page.getByRole("button", { name: "提交官方页面接受" });
  await submit.click();

  await expect(page.getByText("数据冲突，当前请求无法完成。")).toBeVisible();
  await expect(page.getByText("Payment workbook input is not active")).toHaveCount(0);
  await expect(panel.getByTestId("official-acceptance-result")).toHaveCount(0);
  await expect(panel.getByText("服务端：已生成，尚未登记官方接受")).toBeVisible();
  await expect(submit).toBeEnabled();
  expect(acceptanceRequests).toHaveLength(1);

  const firstIdempotencyKey = acceptanceRequests[0].postDataJSON().idempotency_key;
  await submit.click();

  await expect(panel.getByTestId("official-acceptance-result")).toBeVisible();
  await expect(panel.getByText("服务端：官方页面已接受")).toBeVisible();
  expect(acceptanceRequests).toHaveLength(2);
  expect(acceptanceRequests[1].postDataJSON().idempotency_key).toBe(firstIdempotencyKey);
  await expect.poll(() => detailReads).toBe(2);
});

interface MockPayListApiOptions {
  permissions: string[];
  officialWorkbookStatus?: string;
  getArtifactStatus: () => "GENERATED" | "OFFICIAL_SITE_ACCEPTED";
  includeSecondArtifact?: boolean;
  onDetailRead?: () => void;
  onAcceptance?: (route: Route) => Promise<void>;
}

async function mockPayListApi(page: Page, options: MockPayListApiOptions): Promise<void> {
  await page.route("**/api/v1/**", async (route) => {
    const request = route.request();
    const apiPath = new URL(request.url()).pathname.replace(/^\/api\/v1/, "");

    if (request.method() === "GET" && apiPath === "/auth/me") {
      return fulfillJson(route, { permissions: options.permissions });
    }
    if (request.method() === "GET" && apiPath === `/pay-lists/${payListId}`) {
      options.onDetailRead?.();
      return fulfillJson(
        route,
        payListDetail(
          options.officialWorkbookStatus,
          options.getArtifactStatus(),
          options.includeSecondArtifact,
        ),
      );
    }
    if (
      request.method() === "POST" &&
      apiPath === `/pay-lists/${payListId}/official-workbook/acceptance` &&
      options.onAcceptance
    ) {
      return options.onAcceptance(route);
    }

    return fulfillJson(route, { detail: "未处理的第222行官方接受界面模拟请求" }, 404);
  });
}

async function openPayList(page: Page): Promise<void> {
  await page.addInitScript(() => {
    window.localStorage.setItem("fpms_token", "v8-official-workbook-acceptance-ui-token");
  });
  await page.goto(`/fee-management/pay-lists/${payListId}`, {
    waitUntil: "domcontentloaded",
  });
  await expect(page.getByRole("heading", { name: "官费清单详情" })).toBeVisible();
}

async function fillAcceptanceDialog(page: Page): Promise<void> {
  const dialog = page.getByRole("dialog", { name: "登记官方页面接受" });
  await dialog
    .getByTestId("official-acceptance-evidence-ref")
    .fill("official-site/acceptance/receipt-222");
  await dialog.getByTestId("official-acceptance-evidence-sha256").fill(evidenceHash);
  await dialog.getByTestId("official-acceptance-accepted-at").fill("2026-08-13T18:00:00");
}

async function fulfillJson(route: Route, body: unknown, status = 200): Promise<void> {
  await route.fulfill({
    status,
    contentType: "application/json",
    headers: { "access-control-allow-origin": "*" },
    body: JSON.stringify(body),
  });
}

function acceptanceResult(
  targetArtifactId = artifactId,
  disposition: "CREATED" | "REUSED" = "CREATED",
): Record<string, unknown> {
  return {
    artifact_id: targetArtifactId,
    pay_list_id: payListId,
    evidence_ref: "official-site/acceptance/receipt-222",
    evidence_sha256: evidenceHash,
    accepted_at: "2026-08-13T18:00:00",
    activity_id: activityId,
    status: "OFFICIAL_SITE_ACCEPTED",
    accepted: true,
    paid: false,
    ticket_verified: false,
    idempotency_key: "official-workbook-acceptance-ui-222",
    disposition,
  };
}

function payListDetail(
  officialWorkbookStatus: string | undefined,
  artifactStatus: "GENERATED" | "OFFICIAL_SITE_ACCEPTED",
  includeSecondArtifact = false,
): Record<string, unknown> {
  return {
    pay_list: {
      id: payListId,
      pay_list_no: "PL-ROW-222",
      client_id: "client-row-222",
      currency: "CNY",
      status: "DRAFT",
      planned_pay_date: "2026-08-20",
      paid_date: null,
      total_amount: 900,
      remark: "第222行官方接受界面验证",
      created_at: "2026-08-13T00:00:00Z",
      updated_at: "2026-08-13T00:00:00Z",
      created_by: "ui-test",
      updated_by: "ui-test",
    },
    gov_payments: [
      {
        id: 222,
        pay_list_id: payListId,
        case_id: "case-row-222",
        case_no: "CN2026000222",
        fee_item_id: "fee-row-222",
        status: "PLANNED",
        currency: "CNY",
        paid_date: null,
        paid_amount: 0,
        official_receipt_no: null,
        remark: null,
      },
    ],
    export_artifacts: [
      workbookArtifact(artifactId, artifactStatus),
      ...(includeSecondArtifact ? [workbookArtifact(secondArtifactId, "GENERATED")] : []),
    ],
    ...(officialWorkbookStatus === undefined
      ? {}
      : {
          official_workbook: {
            official_upload_template_status: officialWorkbookStatus,
            official_upload_template_name: "官方缴费模板.xlsm",
            official_upload_batch_limit: 500,
            official_pay_list_boundary_note: "官方页面接受与支付、票据核验分离",
          },
        }),
  };
}

function workbookArtifact(
  targetArtifactId: string,
  status: "GENERATED" | "OFFICIAL_SITE_ACCEPTED",
): Record<string, unknown> {
  return {
    id: targetArtifactId,
    pay_list_id: payListId,
    kind: "OFFICIAL_XLSM",
    status,
    content_sha256: "b".repeat(64),
    managed_storage_path: `official-workbooks/${targetArtifactId}.xlsm`,
    template_version: "2026.08",
    generated_by: "generator-row-222",
    generated_at: "2026-08-13T17:30:00",
    idempotency_key: `official-workbook-generation-${targetArtifactId}`,
    official_acceptance_evidence_ref:
      status === "OFFICIAL_SITE_ACCEPTED" ? "official-site/acceptance/receipt-222" : null,
    official_acceptance_evidence_hash:
      status === "OFFICIAL_SITE_ACCEPTED" ? evidenceHash : null,
    official_accepted_at:
      status === "OFFICIAL_SITE_ACCEPTED" ? "2026-08-13T18:00:00" : null,
    updated_at: "2026-08-13T18:00:00",
  };
}
