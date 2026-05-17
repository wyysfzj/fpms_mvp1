import { expect, type Locator, type Page } from "@playwright/test";

export type SidebarModeLabel = "工作导航" | "模块导航";

export class AppShellPage {
  constructor(private readonly page: Page) {}

  private get sidebar(): Locator {
    return this.page.locator(".product-sidebar");
  }

  async expectLoaded(): Promise<void> {
    await expect(this.sidebar).toBeVisible();
    await expect(this.page.getByRole("navigation", { name: "主导航" })).toBeVisible();
  }

  async expectNavModeSelected(label: SidebarModeLabel): Promise<void> {
    await expect(this.page.getByRole("tab", { name: label })).toHaveAttribute("aria-selected", "true");
  }

  async switchNavMode(label: SidebarModeLabel): Promise<void> {
    const tab = this.page.getByRole("tab", { name: label });
    await expect(tab).toBeVisible();
    await tab.click();
    await this.expectNavModeSelected(label);
  }

  groupButton(label: string): Locator {
    return this.sidebar.locator(".nav-group-button", { hasText: label }).first();
  }

  menuLink(label: string): Locator {
    return this.sidebar.getByRole("link", { name: label });
  }

  activeMenu(label: string): Locator {
    return this.sidebar.locator(".nav-item.active", { hasText: label }).first();
  }

  async expectGroupExpanded(label: string): Promise<void> {
    await expect(this.groupButton(label)).toHaveAttribute("aria-expanded", "true");
  }

  async expectGroupCollapsed(label: string): Promise<void> {
    await expect(this.groupButton(label)).toHaveAttribute("aria-expanded", "false");
  }

  async expandGroup(label: string): Promise<void> {
    const group = this.groupButton(label);
    await expect(group).toBeVisible();
    if ((await group.getAttribute("aria-expanded")) !== "true") {
      await group.click();
    }
    await this.expectGroupExpanded(label);
  }

  async collapseGroup(label: string): Promise<void> {
    const group = this.groupButton(label);
    await expect(group).toBeVisible();
    if ((await group.getAttribute("aria-expanded")) !== "false") {
      await group.click();
    }
    await this.expectGroupCollapsed(label);
  }

  async expectActiveMenu(label: string): Promise<void> {
    await expect(this.activeMenu(label)).toBeVisible();
  }

  async collapseSidebar(): Promise<void> {
    if (!(await this.sidebar.evaluate((node) => node.classList.contains("sidebar-collapsed")))) {
      await this.page.getByRole("button", { name: "收起侧栏" }).click();
    }
    await expect(this.sidebar).toHaveClass(/sidebar-collapsed/);
  }

  async expectIconOnlySidebar(): Promise<void> {
    await expect(this.sidebar.locator(".nav-group-button")).toHaveCount(0);
    await expect(this.menuLink("工作台")).toBeVisible();
    await expect(this.sidebar.locator(".nav-item.active")).toHaveCount(1);
  }
}
