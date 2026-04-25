import type { Page } from "@playwright/test";

export class TaskPage {
  constructor(private readonly page: Page) {}

  async openMyTasks(): Promise<void> {
    await this.page.goto("/tasks/my");
  }

  async openSupervisorTasks(): Promise<void> {
    await this.page.goto("/tasks/supervisor");
  }
}
