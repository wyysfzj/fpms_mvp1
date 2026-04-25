import type { Page } from "@playwright/test";

export class FeePage {
  constructor(private readonly page: Page) {}

  async openDrafts(): Promise<void> {
    await this.page.goto("/fees/drafts");
  }
}
