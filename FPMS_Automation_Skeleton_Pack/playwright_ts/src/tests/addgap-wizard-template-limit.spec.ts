import { expect, test } from "@playwright/test";

test("DocumentWizard requests enabled templates within the API page-size limit", async ({ page }) => {
  let templateRequestUrl = "";

  await page.route("**/api/v1/auth/me", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({ permissions: ["DocTemplate.Read"] }),
    });
  });

  await page.route("**/api/v1/doc-templates?**", async (route) => {
    templateRequestUrl = route.request().url();
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({ items: [], total: 0, page: 1, page_size: 100 }),
    });
  });

  await page.addInitScript(() => {
    window.localStorage.setItem("fpms_token", "wizard-template-limit-test-token");
  });

  await page.goto("/documents/wizard", { waitUntil: "domcontentloaded" });
  await expect(page.getByRole("heading", { name: "中间文件向导" })).toBeVisible();
  await expect.poll(() => templateRequestUrl).not.toBe("");

  const query = new URL(templateRequestUrl).searchParams;
  expect(query.get("page")).toBe("1");
  expect(query.get("page_size")).toBe("100");
  expect(query.get("enabled")).toBe("true");
});
