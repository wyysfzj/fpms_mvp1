import type { Page } from "@playwright/test";

export class BillingPage {
  constructor(private readonly page: Page) {}

  async openBills(): Promise<void> {
    await this.page.goto("/billing/bills");
  }
}
