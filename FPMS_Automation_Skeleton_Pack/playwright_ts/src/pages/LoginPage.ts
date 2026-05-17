import type { Page } from "@playwright/test";

export class LoginPage {
  constructor(private readonly page: Page) {}

  async open(): Promise<void> {
    await this.page.goto("/login");
  }

  async login(username: string, password: string): Promise<void> {
    await this.page.goto("/login");
    await this.page.getByLabel("用户名").fill(username);
    await this.page.getByLabel("密码").fill(password);
    await this.page.getByRole("button", { name: /登\s*录/ }).click();
    await this.page.waitForURL(/\/dashboard(?:$|\?)/);
  }
}
