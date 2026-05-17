import type { Page } from "@playwright/test";

export class TaskPage {
  constructor(private readonly page: Page) {}

  async openTasks(): Promise<void> {
    await this.page.goto("/tasks");
  }

  async openTodayReminders(): Promise<void> {
    await this.page.goto("/tasks/today");
  }

  async openSpecialSearch(): Promise<void> {
    await this.page.goto("/tasks/special-search");
  }

  async openMyTasks(): Promise<void> {
    await this.openTasks();
  }

  async openSupervisorTasks(): Promise<void> {
    await this.openTasks();
  }
}
