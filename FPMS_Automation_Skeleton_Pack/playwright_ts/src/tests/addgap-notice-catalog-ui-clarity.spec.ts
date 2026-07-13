import { expect, test } from "@playwright/test";
import type { Route } from "@playwright/test";

test("DocumentCreate shows every official notice with Chinese execution status", async ({
  page,
}) => {
  let templateRequestUrl = "";

  await page.route("**/api/v1/**", async (route) => {
    const request = route.request();
    const url = new URL(request.url());
    const apiPath = url.pathname.replace(/^\/api\/v1/, "");

    if (request.method() === "GET" && apiPath === "/auth/me") {
      return fulfillJson(route, {
        permissions: ["DocTemplate.Read", "Doc.Create", "Case.Read"],
      });
    }
    if (request.method() === "GET" && apiPath === "/cases") {
      return fulfillJson(route, { items: [], total: 0, page: 1, page_size: 100 });
    }
    if (request.method() === "GET" && apiPath === "/doc-templates") {
      templateRequestUrl = request.url();
      return fulfillJson(route, {
        items: [...officialNoticeTemplates(), plainTemplate()],
        total: 61,
        page: 1,
        page_size: 100,
      });
    }

    return fulfillJson(route, { detail: "Unhandled Task20 mock route" }, 404);
  });

  await page.addInitScript(() => {
    window.localStorage.setItem("fpms_token", "notice-catalog-ui-clarity-test-token");
  });

  await page.goto("/documents/new", { waitUntil: "domcontentloaded" });
  await expect(page.getByRole("heading", { name: "登记往来文件" })).toBeVisible();
  await expect.poll(() => templateRequestUrl).not.toBe("");

  const query = new URL(templateRequestUrl).searchParams;
  expect(query.get("enabled")).toBe("true");
  expect(query.get("page_size")).toBe("100");

  const templateField = page.locator(".el-form-item").filter({ hasText: "文件模板" }).first();
  await templateField.getByRole("combobox").click();

  const catalogOptions = page.getByRole("option").filter({ hasText: "OFFICIAL_NOTICE_" });
  await expect(catalogOptions).toHaveCount(60);

  const executable = page.getByRole("option", {
    name: "OFFICIAL_NOTICE_001 — 受理通知-电子（可执行）",
  });
  const referenceOnly = page.getByRole("option", {
    name: "OFFICIAL_NOTICE_002 — 目录通知002（仅供参考）",
  });
  const missingStatus = page.getByRole("option", {
    name: "OFFICIAL_NOTICE_003 — 目录通知003（仅供参考）",
  });
  const malformedMetadata = page.getByRole("option", {
    name: "OFFICIAL_NOTICE_004 — 目录通知004（仅供参考）",
  });
  const missingMetadata = page.getByRole("option", {
    name: "OFFICIAL_NOTICE_005 — 目录通知005（仅供参考）",
  });
  const unknownStatus = page.getByRole("option", {
    name: "OFFICIAL_NOTICE_006 — 目录通知006（仅供参考）",
  });
  const plain = page.getByRole("option", {
    name: "GENERAL_IN_001 — 普通收文模板",
    exact: true,
  });

  await expect(executable).toBeEnabled();
  await expect(referenceOnly).toBeDisabled();
  await expect(missingStatus).toBeDisabled();
  await expect(malformedMetadata).toBeDisabled();
  await expect(missingMetadata).toBeDisabled();
  await expect(unknownStatus).toBeDisabled();
  await expect(plain).toBeEnabled();
  await executable.click();
  await expect(templateField).toContainText("OFFICIAL_NOTICE_001 — 受理通知-电子（可执行）");
});

async function fulfillJson(route: Route, body: unknown, status = 200): Promise<void> {
  await route.fulfill({
    status,
    contentType: "application/json",
    body: JSON.stringify(body),
  });
}

function officialNoticeTemplates(): Array<Record<string, unknown>> {
  return Array.from({ length: 60 }, (_, zeroBasedIndex) => {
    const index = zeroBasedIndex + 1;
    const executable = index === 1;
    const code = `OFFICIAL_NOTICE_${String(index).padStart(3, "0")}`;
    const name = executable ? "受理通知-电子" : `目录通知${String(index).padStart(3, "0")}`;
    const catalogStatus = executable
      ? "EXECUTABLE"
      : index === 3
        ? undefined
        : index === 6
          ? "PENDING"
          : "REFERENCE_ONLY";
    const inputFields =
      index === 4
        ? "{malformed"
        : index === 5
          ? null
          : JSON.stringify({
              catalog_kind: "OFFICIAL_NOTICE",
              ...(catalogStatus ? { catalog_status: catalogStatus } : {}),
            });

    return {
      id: `notice-template-${index}`,
      code,
      name,
      direction: "IN",
      enabled: true,
      status_effect: executable ? "ACCEPTED" : null,
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
  });
}

function plainTemplate(): Record<string, unknown> {
  return {
    id: "plain-template-1",
    code: "GENERAL_IN_001",
    name: "普通收文模板",
    direction: "IN",
    enabled: true,
    status_effect: null,
    status_restore: null,
    deadline_template_code: null,
    fee_draft_type: null,
    fee_item_list: null,
    need_reply: false,
    reply_to_template_code: null,
    input_fields: null,
    created_at: "2026-07-11T00:00:00",
    updated_at: "2026-07-11T00:00:00",
  };
}
