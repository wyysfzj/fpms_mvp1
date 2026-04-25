import { test as base, expect } from "@playwright/test";

import { ApiClient } from "../clients/apiClient";
import { DbClient } from "../clients/dbClient";
import { BillingPage } from "../pages/BillingPage";
import { CasePage } from "../pages/CasePage";
import { DocumentPage } from "../pages/DocumentPage";
import { FeePage } from "../pages/FeePage";
import { LoginPage } from "../pages/LoginPage";
import { ReportPage } from "../pages/ReportPage";
import { TaskPage } from "../pages/TaskPage";

type FPMSFixtures = {
  runId: string;
  api: ApiClient;
  db: DbClient;
  loginPage: LoginPage;
  casePage: CasePage;
  documentPage: DocumentPage;
  taskPage: TaskPage;
  feePage: FeePage;
  billingPage: BillingPage;
  reportPage: ReportPage;
};

export const test = base.extend<FPMSFixtures>({
  runId: [process.env.FPMS_RUN_ID || "LOCAL-RUN-001", { option: true }],

  api: async ({ request }, use) => {
    const api = new ApiClient(request, process.env.FPMS_API_URL || "http://localhost:8000/api");
    await use(api);
  },

  db: async ({}, use) => {
    const db = new DbClient(process.env.FPMS_DB_DSN);
    await use(db);
  },

  loginPage: async ({ page }, use) => {
    await use(new LoginPage(page));
  },

  casePage: async ({ page }, use) => {
    await use(new CasePage(page));
  },

  documentPage: async ({ page }, use) => {
    await use(new DocumentPage(page));
  },

  taskPage: async ({ page }, use) => {
    await use(new TaskPage(page));
  },

  feePage: async ({ page }, use) => {
    await use(new FeePage(page));
  },

  billingPage: async ({ page }, use) => {
    await use(new BillingPage(page));
  },

  reportPage: async ({ page }, use) => {
    await use(new ReportPage(page));
  },
});

export { expect };
