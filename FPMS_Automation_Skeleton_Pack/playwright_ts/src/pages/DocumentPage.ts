import type { Page } from "@playwright/test";

export class DocumentPage {
  constructor(private readonly page: Page) {}

  async openWizard(): Promise<void> {
    await this.page.goto("/documents/wizard");
  }
}
