import { expect, test } from "@playwright/test";
import type { Locator, Page, Request, Route } from "@playwright/test";

const payListId = 218;
const artifactId = "11111111-1111-4111-8111-111111111218";

test("official workbook generation downloads only the server-returned artifact", async ({
  page,
}) => {
  let generationRequest: Request | null = null;
  let detailReads = 0;

  await mockPayListApi(page, {
    permissions: ["PayList.Read", "PayList.Export"],
    officialWorkbookStatus: "ACTIVE",
    onDetailRead: () => {
      detailReads += 1;
    },
    onGenerate: async (route) => {
      generationRequest = route.request();
      await fulfillOfficialWorkbook(route);
    },
  });

  await openPayList(page);

  const panel = page.getByTestId("official-workbook-panel");
  await expect(panel.getByText("生成不代表官方接受、已缴费或票据已核验")).toBeVisible();

  await fillOfficialWorkbookForm(panel);

  const downloadPromise = page.waitForEvent("download");
  await panel.getByRole("button", { name: "生成并下载官方工作簿" }).click();
  const download = await downloadPromise;

  expect(download.suggestedFilename()).toBe("官方缴费工作簿-218.xlsm");
  await expect.poll(() => generationRequest?.postDataJSON()).toMatchObject({
    rows: [
      {
        sequence_number: 1,
        application_number: "CN2026000218",
        business_type: "发明专利",
        invoice_title: "测试申请人有限公司",
        unified_social_credit_code: "91110000TEST000218",
        fee_type: "申请费",
        foreign_currency_amount: null,
        amount_cny: 900,
        remark: "仅供第218行界面验证",
      },
    ],
  });
  expect(generationRequest?.postDataJSON().idempotency_key).toMatch(/^[0-9a-f-]{36}$/i);

  await expect(panel.getByText(`产物编号：${artifactId}`)).toBeVisible();
  await expect(panel.getByText("服务端生成状态：已生成")).toBeVisible();
  await expect(page.getByText("草稿", { exact: true })).toBeVisible();
  await expect(page.getByText("已计划", { exact: true })).toBeVisible();
  await expect.poll(() => detailReads).toBe(2);
});

test("official workbook generation fails closed without PayList.Export", async ({ page }) => {
  let generationCalls = 0;
  await mockPayListApi(page, {
    permissions: ["PayList.Read"],
    officialWorkbookStatus: "ACTIVE",
    onGenerate: async (route) => {
      generationCalls += 1;
      await fulfillJson(route, { detail: "不应生成工作簿" }, 500);
    },
  });

  await openPayList(page);

  const panel = page.getByTestId("official-workbook-panel");
  await expect(panel.getByText("缺少生成官方工作簿权限")).toBeVisible();
  await expect(
    panel.getByRole("button", { name: "生成并下载官方工作簿" }),
  ).toHaveCount(0);
  expect(generationCalls).toBe(0);
});

for (const status of ["PENDING", "INACTIVE", "RETIRED"]) {
  test(`official workbook generation fails closed for present ${status} server state`, async ({
    page,
  }) => {
    let generationCalls = 0;
    await mockPayListApi(page, {
      permissions: ["PayList.Read", "PayList.Export"],
      officialWorkbookStatus: status,
      onGenerate: async (route) => {
        generationCalls += 1;
        await fulfillJson(route, { detail: "不应生成工作簿" }, 500);
      },
    });

    await openPayList(page);

    const panel = page.getByTestId("official-workbook-panel");
    await expect(
      panel.getByText(`服务端模板状态为 ${status}，只有 ACTIVE 状态可生成官方工作簿。`),
    ).toBeVisible();
    await expect(
      panel.getByRole("button", { name: "生成并下载官方工作簿" }),
    ).toHaveCount(0);
    expect(generationCalls).toBe(0);
  });
}

test("official workbook 409 stays download-free and supports a successful retry", async ({
  page,
}) => {
  const generationRequests: Request[] = [];
  const downloads: string[] = [];
  await mockPayListApi(page, {
    permissions: ["PayList.Read", "PayList.Export"],
    officialWorkbookStatus: "ACTIVE",
    onGenerate: async (route) => {
      generationRequests.push(route.request());
      if (generationRequests.length === 1) {
        await route.fulfill({
          status: 409,
          contentType: "application/json",
          headers: {
            "access-control-allow-origin": "*",
            "access-control-expose-headers": "X-Request-ID",
            "x-request-id": "request-row218-conflict",
          },
          body: JSON.stringify({
            error: {
              code: "PAYMENT_WORKBOOK_GATE_NOT_ACTIVE",
              message: "Payment workbook gate is not active",
              details: { gate_code: "DG-PAYMENT-WORKBOOK" },
            },
          }),
        });
        return;
      }
      await fulfillOfficialWorkbook(route);
    },
  });
  page.on("download", (download) => downloads.push(download.suggestedFilename()));

  await openPayList(page);
  const panel = page.getByTestId("official-workbook-panel");
  await fillOfficialWorkbookForm(panel);
  const generateButton = panel.getByRole("button", {
    name: "生成并下载官方工作簿",
  });

  await generateButton.click();

  await expect(page.getByText("数据冲突，当前请求无法完成。")).toBeVisible();
  await expect(page.getByText("Payment workbook gate is not active")).toHaveCount(0);
  await expect(panel.getByText("服务端生成状态：已生成")).toHaveCount(0);
  await expect(generateButton).toBeEnabled();
  expect(downloads).toEqual([]);

  const retryDownload = page.waitForEvent("download");
  await generateButton.click();
  expect((await retryDownload).suggestedFilename()).toBe("官方缴费工作簿-218.xlsm");
  await expect(panel.getByText("服务端生成状态：已生成")).toBeVisible();
  expect(generationRequests).toHaveLength(2);
  expect(generationRequests[0].postDataJSON().idempotency_key).toBe(
    generationRequests[1].postDataJSON().idempotency_key,
  );
});

test("official workbook generation stays unavailable when server gate state is absent", async ({
  page,
}) => {
  await mockPayListApi(page, {
    permissions: ["PayList.Read", "PayList.Export"],
  });

  await openPayList(page);

  const panel = page.getByTestId("official-workbook-panel");
  await expect(panel.getByText("官方工作簿门禁尚未开放")).toBeVisible();
  await expect(
    panel.getByRole("button", { name: "生成并下载官方工作簿" }),
  ).toHaveCount(0);
});

interface MockPayListApiOptions {
  permissions: string[];
  officialWorkbookStatus?: string | null;
  onDetailRead?: () => void;
  onGenerate?: (route: Route) => Promise<void>;
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
      return fulfillJson(route, payListDetail(options.officialWorkbookStatus));
    }
    if (
      request.method() === "POST" &&
      apiPath === `/pay-lists/${payListId}/official-workbook` &&
      options.onGenerate
    ) {
      return options.onGenerate(route);
    }

    return fulfillJson(route, { detail: "未处理的第218行官方工作簿界面模拟请求" }, 404);
  });
}

async function openPayList(page: Page): Promise<void> {
  await page.addInitScript(() => {
    window.localStorage.setItem("fpms_token", "v8-official-payment-workbook-ui-token");
  });
  await page.goto(`/fee-management/pay-lists/${payListId}`, {
    waitUntil: "domcontentloaded",
  });
  await expect(page.getByRole("heading", { name: "官费清单详情" })).toBeVisible();
}

async function fulfillJson(route: Route, body: unknown, status = 200): Promise<void> {
  await route.fulfill({
    status,
    contentType: "application/json",
    body: JSON.stringify(body),
  });
}

async function fulfillOfficialWorkbook(route: Route): Promise<void> {
  await route.fulfill({
    status: 201,
    contentType: "application/vnd.ms-excel.sheet.macroEnabled.12",
    headers: {
      "access-control-allow-origin": "*",
      "access-control-expose-headers": [
        "Content-Disposition",
        "X-FPMS-Artifact-ID",
        "X-FPMS-Content-SHA256",
        "X-FPMS-Template-Version",
        "X-FPMS-Template-Content-SHA256",
        "X-FPMS-Workbook-Input-Version-ID",
        "X-FPMS-Workbook-Disposition",
        "X-FPMS-Generated-Status",
      ].join(", "),
      "content-disposition":
        "attachment; filename*=UTF-8''%E5%AE%98%E6%96%B9%E7%BC%B4%E8%B4%B9%E5%B7%A5%E4%BD%9C%E7%B0%BF-218.xlsm",
      "x-fpms-artifact-id": artifactId,
      "x-fpms-content-sha256": "a".repeat(64),
      "x-fpms-template-version": "2026.08",
      "x-fpms-template-content-sha256": "b".repeat(64),
      "x-fpms-workbook-input-version-id":
        "22222222-2222-4222-8222-222222222218",
      "x-fpms-workbook-disposition": "CREATED",
      "x-fpms-generated-status": "GENERATED",
    },
    body: Buffer.from("official-workbook-row218"),
  });
}

async function fillOfficialWorkbookForm(panel: Locator): Promise<void> {
  await panel.getByTestId("official-workbook-application-number").fill("CN2026000218");
  await panel.getByTestId("official-workbook-business-type").fill("发明专利");
  await panel.getByTestId("official-workbook-invoice-title").fill("测试申请人有限公司");
  await panel
    .getByTestId("official-workbook-credit-code")
    .fill("91110000TEST000218");
  await panel.getByTestId("official-workbook-fee-type").fill("申请费");
  await panel.getByTestId("official-workbook-amount-cny").fill("900");
  await panel.getByTestId("official-workbook-remark").fill("仅供第218行界面验证");
}

function payListDetail(officialWorkbookStatus?: string | null): Record<string, unknown> {
  return {
    pay_list: {
      id: payListId,
      pay_list_no: "PL-ROW-218",
      client_id: "client-row-218",
      currency: "CNY",
      status: "DRAFT",
      planned_pay_date: "2026-08-20",
      paid_date: null,
      total_amount: 900,
      remark: "第218行官方工作簿界面验证",
      created_at: "2026-08-13T00:00:00Z",
      updated_at: "2026-08-13T00:00:00Z",
      created_by: "ui-test",
      updated_by: "ui-test",
    },
    gov_payments: [
      {
        id: 218,
        pay_list_id: payListId,
        case_id: "case-row-218",
        case_no: "CN2026000218",
        fee_item_id: "fee-row-218",
        status: "PLANNED",
        currency: "CNY",
        paid_date: null,
        paid_amount: 0,
        official_receipt_no: null,
        remark: null,
      },
    ],
    export_artifacts: [],
    ...(officialWorkbookStatus !== undefined
      ? {
          official_workbook: {
            official_upload_template_status: officialWorkbookStatus,
            official_upload_template_name: "官方缴费模板.xlsm",
            official_upload_batch_limit: 500,
            official_pay_list_boundary_note: "仅生成，不代表接受、支付或票据核验",
          },
        }
      : {}),
  };
}
