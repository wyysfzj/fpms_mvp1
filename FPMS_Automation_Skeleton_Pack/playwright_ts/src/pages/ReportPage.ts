import type { Page } from "@playwright/test";

export class ReportPage {
  constructor(private readonly page: Page) {}

  async open(pathname = "/reports"): Promise<void> {
    await this.page.goto(pathname);
  }
}
