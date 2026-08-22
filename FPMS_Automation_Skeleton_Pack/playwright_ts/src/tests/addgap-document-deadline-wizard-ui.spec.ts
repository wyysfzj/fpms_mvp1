import { expect, test } from "@playwright/test";
import type { Locator, Page, Request, Route } from "@playwright/test";

const templateId = "oa-in-wizard-template";

test("DocumentWizard persists a confirmed official deadline for every row", async ({ page }) => {
  let batchRequest: Request | null = null;

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
    if (method === "GET" && apiPath === "/doc-templates") {
      return fulfillJson(route, {
        items: [oaTemplate()],
        total: 1,
        page: 1,
        page_size: 100,
      });
    }
    if (method === "GET" && apiPath === "/cases") {
      const query = url.searchParams.get("case_no") || url.searchParams.get("app_no") || "";
      const matchingCase = wizardCases().find((item) => item.case_no === query);
      return fulfillJson(route, {
        items: matchingCase ? [matchingCase] : [],
        total: matchingCase ? 1 : 0,
        page: 1,
        page_size: 1,
      });
    }
    if (method === "POST" && apiPath === "/documents/wizard/batch-create") {
      batchRequest = request;
      const payload = request.postDataJSON() as { rows: Array<Record<string, unknown>> };
      return fulfillJson(route, {
        created: payload.rows.length,
        total: payload.rows.length,
        items: payload.rows.map((row, index) => ({
          row_index: index + 1,
          document: {
            id: `wizard-document-${index + 1}`,
            case_id: row.case_id,
            title: row.title,
            direction: "IN",
          },
        })),
      });
    }
    if (method === "GET" && apiPath === "/documents") {
      return fulfillJson(route, { items: [], total: 0, page: 1, page_size: 20 });
    }

    return fulfillJson(route, { detail: "未处理的 Task31 模拟请求" }, 404);
  });

  await page.addInitScript(() => {
    window.localStorage.setItem("fpms_token", "document-deadline-wizard-ui-test-token");
  });

  await page.goto("/documents/wizard", { waitUntil: "domcontentloaded" });
  await expect(page.getByRole("heading", { name: "中间文件向导" })).toBeVisible();

  const templateField = page.locator(".defaults-field").filter({ hasText: "文书模板" }).first();
  await templateField.locator(".el-select__wrapper").click();
  await page.getByRole("option", { name: "OA_IN - 审查意见通知书（收文）" }).click();

  await page.locator("textarea").first().fill("WIZ-DUE-001\nWIZ-DUE-002");
  await page.getByRole("button", { name: "拆分为逐行列表" }).click();
  await page.getByRole("button", { name: "解析全部" }).click();
  await expect(page.getByText("已解析")).toHaveCount(2);
  await page.getByRole("button", { name: "下一步" }).click();

  const rowCards = page.locator(".step2-row-card");
  await expect(rowCards).toHaveCount(2);

  await fillDeadlineRow(rowCards.nth(0), page, {
    dueDate: "2026-10-15",
    sourceLabel: "人工核对官方通知",
  });
  await fillDeadlineRow(rowCards.nth(1), page, {
    dueDate: "2026-11-20",
    sourceLabel: "从官方通知导入",
  });

  await page.getByRole("button", { name: "仅登记文书" }).click();
  await expect.poll(() => batchRequest?.postDataJSON()).toMatchObject({
    defaults: {
      doc_template_id: templateId,
      direction: "IN",
    },
    rows: [
      {
        case_id: "wizard-case-1",
        official_due_date: "2026-10-15",
        official_due_date_source: "MANUAL_OFFICIAL_NOTICE",
        official_due_date_status: "CONFIRMED",
      },
      {
        case_id: "wizard-case-2",
        official_due_date: "2026-11-20",
        official_due_date_source: "IMPORTED_OFFICIAL_NOTICE",
        official_due_date_status: "CONFIRMED",
      },
    ],
  });
  await expect(page.getByText("已登记 2 份文书，未写入后续任务、费用或附件。")).toBeVisible();
});

async function fillDeadlineRow(
  row: Locator,
  page: Page,
  values: { dueDate: string; sourceLabel: string },
): Promise<void> {
  await row.getByPlaceholder("请选择官方截止日").fill(values.dueDate);

  const sourceField = row.locator(".step2-field").filter({ hasText: "截止日来源" }).first();
  await sourceField.locator(".el-select__wrapper").click();
  await page.getByRole("option", { name: values.sourceLabel }).click();

  const statusField = row.locator(".step2-field").filter({ hasText: "确认状态" }).first();
  await statusField.locator(".el-select__wrapper").click();
  await page.getByRole("option", { name: "已确认" }).click();
}

async function fulfillJson(route: Route, body: unknown, status = 200): Promise<void> {
  await route.fulfill({ status, contentType: "application/json", body: JSON.stringify(body) });
}

function oaTemplate(): Record<string, unknown> {
  return {
    id: templateId,
    code: "OA_IN",
    name: "审查意见通知书（收文）",
    direction: "IN",
    enabled: true,
    status_effect: "OA1",
    deadline_template_code: "OA_REPLY",
    need_reply: true,
  };
}

function wizardCases(): Array<Record<string, unknown>> {
  return [
    {
      id: "wizard-case-1",
      case_no: "WIZ-DUE-001",
      app_no: "CN202610000001",
      title_cn: "第一件官方截止日向导案件",
      title: "第一件官方截止日向导案件",
    },
    {
      id: "wizard-case-2",
      case_no: "WIZ-DUE-002",
      app_no: "CN202610000002",
      title_cn: "第二件官方截止日向导案件",
      title: "第二件官方截止日向导案件",
    },
  ];
}
