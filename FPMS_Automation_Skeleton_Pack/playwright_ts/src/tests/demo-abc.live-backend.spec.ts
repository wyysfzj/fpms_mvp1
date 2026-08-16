import { expect, test } from "@playwright/test";
import { mkdir } from "node:fs/promises";
import path from "node:path";

const evidenceDir = process.env.FPMS_DEMO_EVIDENCE_DIR;

test("@demo-abc visible customer AR receipt and offset closes exactly once", async ({ page }) => {
  test.setTimeout(120_000);
  expect(evidenceDir, "FPMS_DEMO_EVIDENCE_DIR is required").toBeTruthy();
  const suffix = `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 7)}`.toUpperCase();
  const clientName = `ABC 虚构演示客户 ${suffix}`;
  const clientCode = `ABC-${suffix}`;
  const caseNo = `ABC-DEMO-${suffix}`;

  await test.step("login through the visible UI", async () => {
    await page.goto("/login", { waitUntil: "domcontentloaded" });
    const formItems = page.locator(".el-form-item");
    await formItems.nth(0).locator("input").fill(process.env.FPMS_ADMIN_USERNAME || "");
    await formItems.nth(1).locator("input").fill(process.env.FPMS_ADMIN_PASSWORD || "");
    await page.getByRole("button", { name: "登 录" }).click();
    await expect(page).toHaveURL(/\/dashboard$/);
  });

  await test.step("create fictional client through the visible UI", async () => {
    await page.goto("/clients/new", { waitUntil: "domcontentloaded" });
    await page.getByPlaceholder("请输入客户名称").fill(clientName);
    await page.getByPlaceholder("请输入客户代码（可选）").fill(clientCode);
    await page.getByRole("button", { name: "创建客户" }).click();
    await expect(page).toHaveURL(/\/clients$/);
    await expect(page.getByText(clientName)).toBeVisible();
  });

  await test.step("create fictional case through the visible UI", async () => {
    await page.goto("/cases/new", { waitUntil: "domcontentloaded" });
    await page.getByPlaceholder("请输入案号（例如：P2024-001）").fill(caseNo);
    await page.getByPlaceholder("请输入案件标题").fill(`ABC 虚构服务费闭环 ${suffix}`);
    const clientField = page.locator(".el-form-item").filter({ hasText: "客户" }).first();
    await clientField.getByRole("combobox").click();
    await page.getByRole("option", { name: clientName }).click();
    await page.getByText("申请人信息", { exact: true }).click();
    await page.getByRole("button", { name: "新增申请人" }).click();
    const applicantField = page.locator(".el-form-item").filter({ hasText: "从客户主数据回填" });
    const applicantSelect = applicantField.getByRole("combobox");
    await applicantSelect.click();
    const applicantListboxId = await applicantSelect.getAttribute("aria-controls");
    expect(applicantListboxId, "applicant select must own a listbox").toBeTruthy();
    await page.locator(`[id="${applicantListboxId}"]`).getByRole("option", { name: clientName }).click();
    await expect(page.getByPlaceholder("申请人中文名称")).toHaveValue(clientName);
    await page.getByText("控制标记", { exact: true }).click();
    const reductionField = page.locator(".el-form-item").filter({ hasText: "费用减缓比例" });
    await reductionField.locator(".el-select__wrapper").click();
    await page.getByRole("option", { name: "不减免（0）" }).click();
    await page.getByRole("button", { name: "创建案件" }).click();
    await expect(page).toHaveURL(/\/cases$/);
    await expect(page.getByText(caseNo)).toBeVisible();
  });

  await test.step("complete the visible ABC finance closure", async () => {
    await page.goto("/demo/abc", { waitUntil: "domcontentloaded" });
    await expect(page.getByText("演示输入已校验")).toBeVisible();
    await page.getByTestId("demo-case-no").fill(caseNo);
    await page.getByRole("button", { name: "加载案件" }).click();
    await expect(page.getByText(new RegExp(`已选择 ${caseNo}`))).toBeVisible();

    await page.getByTestId("create-obligation").click();
    await expect(page.getByText(/义务 [0-9a-f-]+ · 1200\.00 CNY/)).toBeVisible();
    await page.getByTestId("create-draft").click();
    await expect(page.getByText(/草单 [0-9a-f-]+ · LOCKED · 1200\.00 CNY/)).toBeVisible();
    await page.getByTestId("create-bill").click();
    await expect(page.getByText("1200.00 CNY").first()).toBeVisible();
    await page.getByTestId("create-payment").click();
    await expect(page.getByText(/1200\.00 CNY · UNALLOCATED/)).toBeVisible();
    await page.getByTestId("create-offset").click();
    await expect(page.getByText(/SETTLED \/ 余额 0\.00 CNY/)).toBeVisible();
    await expect(page.getByText(/FULLY_ALLOCATED \/ 余额 0\.00 CNY/)).toBeVisible();
    await expect(page.getByText("1200.00 / 1200.00 CNY")).toBeVisible();
  });

  await mkdir(evidenceDir!, { recursive: true });
  await page.screenshot({
    path: path.join(evidenceDir!, "final-settled.png"),
    fullPage: true,
  });
  console.log(JSON.stringify({ case_no: caseNo, client_code: clientCode, status: "SETTLED" }));
});
