import type { Page } from "@playwright/test";

export class CasePage {
  constructor(private readonly page: Page) {}

  async openNewCase(): Promise<void> {
    await this.page.goto("/cases/new");
  }

  async openByCaseNo(caseNo: string): Promise<void> {
    await this.page.goto(`/cases?keyword=${encodeURIComponent(caseNo)}`);
  }

  async save(): Promise<void> {
    await this.page.getByRole("button", { name: /save|保存/i }).click();
  }
}
