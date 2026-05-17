import { test, expect } from "../fixtures/fpms.fixtures";

const username = process.env.FPMS_USERNAME || "admin";
const password = process.env.FPMS_PASSWORD || "admin123";

async function resetSidebarPreferences(page: import("@playwright/test").Page): Promise<void> {
  await page.evaluate(() => {
    window.localStorage.setItem("fpms_nav_mode", "work");
    window.localStorage.setItem("fpms_sidebar_collapsed", "0");
    window.localStorage.removeItem("fpms_sidebar_group_collapsed");
  });
}

test("@P0 current product sidebar supports production navigation modes and collapse state", async ({
  page,
  loginPage,
  appShell,
}) => {
  const pageErrors: string[] = [];
  page.on("pageerror", (error) => pageErrors.push(error.message));

  await loginPage.login(username, password);
  await resetSidebarPreferences(page);
  await page.goto("/dashboard", { waitUntil: "domcontentloaded" });

  await appShell.expectLoaded();
  await appShell.expectNavModeSelected("工作导航");
  await appShell.expectGroupExpanded("我的工作");
  await appShell.expectGroupExpanded("案件生命周期");
  await appShell.expectGroupExpanded("费用到回款");
  await appShell.expectGroupExpanded("授权后运营");
  await appShell.expectActiveMenu("工作台");

  await appShell.switchNavMode("模块导航");
  await appShell.expectGroupExpanded("我的工作");
  await appShell.expectGroupCollapsed("费用与账单");

  await appShell.expandGroup("费用与账单");
  await expect(appShell.menuLink("账单管理")).toBeVisible();
  await page.reload({ waitUntil: "domcontentloaded" });
  await appShell.expectGroupExpanded("费用与账单");

  await appShell.menuLink("账单管理").click();
  await expect(page).toHaveURL(/\/billing\/bills/);
  await appShell.expectGroupExpanded("费用与账单");
  await appShell.expectActiveMenu("账单管理");

  await appShell.collapseSidebar();
  await appShell.expectIconOnlySidebar();

  expect(pageErrors).toEqual([]);
});
