import { expect, test } from "@playwright/test";
import fs from "node:fs";
import path from "node:path";

type RouteInfo = {
  path: string;
  name: string;
  component: string;
};

const apiBaseUrl = (process.env.FPMS_API_URL || "http://localhost:8000/api/v1").replace(/\/$/, "");
const username = process.env.FPMS_USERNAME || "admin";
const password = process.env.FPMS_PASSWORD || "admin123";

function loadStaticRoutes(): RouteInfo[] {
  const routerPath = path.resolve(process.cwd(), "../../frontend/src/router/index.ts");
  const source = fs.readFileSync(routerPath, "utf-8");
  const routes: RouteInfo[] = [];
  const routePattern =
    /\{\s*path:\s*'([^']+)'\s*,\s*name:\s*'([^']+)'\s*,\s*component:\s*\(\)\s*=>\s*import\('([^']+)'\)/g;
  for (const match of source.matchAll(routePattern)) {
    const routePath = match[1];
    if (!routePath.includes(":")) {
      routes.push({ path: normalizePath(routePath), name: match[2], component: match[3] });
    }
  }
  return routes.filter((route) => route.path !== "/login");
}

function normalizePath(routePath: string): string {
  return routePath.startsWith("/") ? routePath : `/${routePath}`;
}

test("@P1 current static frontend routes render without page errors", async ({ page, request }) => {
  const login = await request.post(`${apiBaseUrl}/auth/login`, {
    data: { username, password },
  });
  expect(login.ok()).toBeTruthy();
  const token = (await login.json()).access_token as string;
  expect(token).toBeTruthy();

  await page.addInitScript((value) => {
    window.localStorage.setItem("fpms_token", value);
  }, token);

  const routes = loadStaticRoutes();
  expect(routes.length).toBeGreaterThanOrEqual(40);

  const pageErrors: string[] = [];
  page.on("pageerror", (error) => pageErrors.push(error.message));

  for (const route of routes) {
    await page.goto(route.path, { waitUntil: "domcontentloaded" });
    await expect(page.locator("#app")).toBeVisible();
    await expect(page.locator("body")).toContainText(/\S/);
  }

  expect(pageErrors).toEqual([]);
});
