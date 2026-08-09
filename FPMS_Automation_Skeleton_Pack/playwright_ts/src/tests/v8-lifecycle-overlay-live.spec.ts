import { execFileSync } from "node:child_process";
import path from "node:path";

import { expect, test } from "@playwright/test";
import type { Page, Response } from "@playwright/test";

const repoRoot = path.resolve(process.cwd(), "../..");
const backendPython =
  process.env.FPMS_BACKEND_PYTHON || path.join(repoRoot, "backend", ".venv", "bin", "python");
const liveSeedScript = path.join(process.cwd(), "src", "support", "pdV8OverlayLiveSeed.py");

const caseGateCodes = [
  "DG-FEE-APPLICATION-DRAFT",
  "DG-FEE-GRANT-YEAR-DRAFT",
  "DG-FEE-FUTURE-ANNUITY",
  "DG-GRANT-EVIDENCE-SOURCE",
  "DG-GRANT-MANUAL-REVIEW",
  "DG-PAYMENT-WORKBOOK",
  "DG-SERVICE-RATE-VERSION",
] as const;

type LiveFixture = {
  activityCount: number;
  caseId: string;
  caseNo: string;
  gateCount: number;
  namespace: string;
};

type OverlayGate = {
  gate_code: string;
  requested_scope_key: string;
  resolution_status: "RESOLVED" | "UNRESOLVED";
  gate_id: string | null;
  resolved_scope_key: string | null;
  decision_value: string | null;
  source_reference: string | null;
  source_version: string | null;
  confirmed_by: string | null;
  effective_at: string | null;
  unresolved_reason: string | null;
};

type OverlayWarning = {
  kind: string;
  code: string;
  message: string;
  activity_id: string | null;
  source_object_type: string | null;
  source_object_id: string | null;
};

type OverlayResponse = {
  case_id: string;
  lifecycle_revision: number;
  milestones: Array<{ sequence: number; lane: string }>;
  decision_gates: OverlayGate[];
  warnings: OverlayWarning[];
  next_cursor: number | null;
  has_more: boolean;
};

function seedFixture(): LiveFixture {
  const output = execFileSync(backendPython, [liveSeedScript], {
    cwd: path.join(repoRoot, "backend"),
    encoding: "utf8",
    env: {
      ...process.env,
      PYTHONPATH: path.join(repoRoot, "backend"),
    },
  });
  return JSON.parse(output.trim()) as LiveFixture;
}

function overlayResponseFor(response: Response, caseId: string): boolean {
  const url = new URL(response.url());
  return (
    response.request().method() === "GET" &&
    url.pathname.endsWith(`/cases/${caseId}/lifecycle-overlay`)
  );
}

function caseResponseFor(response: Response, caseId: string): boolean {
  const url = new URL(response.url());
  return (
    response.request().method() === "GET" &&
    url.pathname.includes("/api/v1/") &&
    url.pathname.endsWith(`/cases/${caseId}`)
  );
}

function expectedGateIdentities(caseId: string): string[] {
  return [
    ...caseGateCodes.map((code) => `${code}:case:${caseId}`),
    ...Array.from(
      { length: 22 },
      (_, index) => `DG-LEGACY-FORM-CLASS:form-${String(index + 1).padStart(3, "0")}`,
    ),
  ];
}

function gateSnapshot(overlay: OverlayResponse): Array<readonly unknown[]> {
  return overlay.decision_gates.map((gate) => [
    gate.gate_code,
    gate.requested_scope_key,
    gate.resolution_status,
    gate.gate_id,
    gate.resolved_scope_key,
    gate.decision_value,
    gate.source_reference,
    gate.source_version,
    gate.confirmed_by,
    gate.effective_at,
    gate.unresolved_reason,
  ]);
}

async function expectRealJson(response: Response): Promise<void> {
  expect(response.status(), await response.text()).toBe(200);
  expect(response.fromServiceWorker()).toBe(false);
  expect(response.headers()["content-type"]).toContain("application/json");
  const address = await response.serverAddr();
  expect(address?.port).toBeGreaterThan(0);
}

async function loginThroughUi(page: Page): Promise<Response> {
  await page.goto("/login");
  const formItems = page.locator(".el-form-item");
  await formItems.filter({ hasText: "用户名" }).locator("input").fill(
    process.env.FPMS_E2E_USERNAME || "admin",
  );
  await formItems.filter({ hasText: "密码" }).locator("input").fill(
    process.env.FPMS_E2E_PASSWORD || "admin123",
  );
  const loginResponsePromise = page.waitForResponse((response) => {
    const url = new URL(response.url());
    return response.request().method() === "POST" && url.pathname.endsWith("/auth/login");
  });
  await page.getByRole("button", { name: "登 录" }).click();
  const loginResponse = await loginResponsePromise;
  await expectRealJson(loginResponse);
  await expect(page).toHaveURL(/\/dashboard$/);
  return loginResponse;
}

async function expectRenderedGateSnapshot(page: Page, expected: string[]): Promise<void> {
  const rows = page.locator('[data-testid="overlay-decision-gates"] .gate-row');
  await expect(rows).toHaveCount(29);
  expect(await rows.evaluateAll((items) => items.map((item) => item.getAttribute("data-gate-key"))))
    .toEqual(expected);
}

test("real UI traverses stable three-page lifecycle overlay without fulfilled routes", async ({
  page,
}) => {
  test.setTimeout(120_000);
  const fixture = seedFixture();
  expect(fixture).toMatchObject({ activityCount: 401, gateCount: 29 });

  const observedApplicationResponses: Response[] = [];
  page.on("response", (response) => {
    const pathname = new URL(response.url()).pathname;
    if (pathname.includes("/api/v1/")) observedApplicationResponses.push(response);
  });

  const loginResponse = await loginThroughUi(page);
  const firstOverlayPromise = page.waitForResponse((response) =>
    overlayResponseFor(response, fixture.caseId),
  );
  const caseResponsePromise = page.waitForResponse((response) =>
    caseResponseFor(response, fixture.caseId),
  );
  await page.goto(`/cases/${fixture.caseId}`);
  const [firstResponse, caseResponse] = await Promise.all([
    firstOverlayPromise,
    caseResponsePromise,
  ]);
  await expectRealJson(caseResponse);
  await expectRealJson(firstResponse);
  const first = (await firstResponse.json()) as OverlayResponse;

  const expectedIdentities = expectedGateIdentities(fixture.caseId);
  expect(first.case_id).toBe(fixture.caseId);
  expect(first.milestones).toHaveLength(200);
  expect(first.milestones.map((item) => item.sequence)).toEqual(
    Array.from({ length: 200 }, (_, index) => index + 1),
  );
  expect(new Set(first.milestones.map((item) => item.lane))).toEqual(
    new Set(["LIFECYCLE", "DOCUMENT", "FEE"]),
  );
  expect(first.next_cursor).toBe(200);
  expect(first.has_more).toBe(true);
  expect(
    first.decision_gates.map((gate) => `${gate.gate_code}:${gate.requested_scope_key}`),
  ).toEqual(expectedIdentities);
  expect(new Set(first.decision_gates.map((gate) => gate.gate_code)).size).toBe(8);
  expect(first.decision_gates.every((gate) => gate.requested_scope_key !== "ALL-22")).toBe(
    true,
  );

  await expect(page.getByTestId("lifecycle-center-lane")).toBeVisible();
  await expect(page.getByTestId("document-evidence-lane")).toBeVisible();
  await expect(page.getByTestId("fee-obligation-lane")).toBeVisible();
  await expectRenderedGateSnapshot(page, expectedIdentities);

  const fallback = first.decision_gates.find(
    (gate) =>
      gate.gate_code === "DG-LEGACY-FORM-CLASS" && gate.requested_scope_key === "form-004",
  );
  expect(fallback).toMatchObject({
    resolution_status: "RESOLVED",
    resolved_scope_key: "ALL-22",
    decision_value: "CURRENT_OFFICIAL",
    source_reference: "v8-overlay-live-all-22",
    source_version: "2026-08-10",
  });
  const fallbackRow = page.locator(
    '[data-gate-key="DG-LEGACY-FORM-CLASS:form-004"]',
  );
  await expect(fallbackRow).toContainText("请求范围：form-004");
  await expect(fallbackRow).toContainText("解析范围：ALL-22");
  await expect(fallbackRow).toContainText("来源引用：v8-overlay-live-all-22");

  const unresolvedRow = page.locator(
    `[data-gate-key="DG-FEE-GRANT-YEAR-DRAFT:case:${fixture.caseId}"]`,
  );
  await expect(unresolvedRow).toContainText("解析状态：UNRESOLVED");
  await expect(unresolvedRow).toContainText("DECISION_GATE_NOT_FOUND");
  const referenceRow = page.locator(
    '[data-gate-key="DG-LEGACY-FORM-CLASS:form-002"]',
  );
  await expect(referenceRow.getByText("仅供参考", { exact: true })).toBeVisible();
  await expect(referenceRow.getByText("非激活", { exact: true })).toBeVisible();
  await expect(referenceRow.locator("button, input, select, textarea")).toHaveCount(0);
  expect(
    first.warnings.some(
      (warning) =>
        warning.kind === "REFERENCE_ONLY" &&
        warning.code === "DECISION_GATE_REFERENCE_ONLY" &&
        warning.message === "该客户决策分类仅供参考，不得激活",
    ),
  ).toBe(true);

  const snapshot = gateSnapshot(first);
  const secondResponsePromise = page.waitForResponse((response) =>
    overlayResponseFor(response, fixture.caseId),
  );
  await page.getByRole("button", { name: "加载更多生命周期记录" }).click();
  const secondResponse = await secondResponsePromise;
  await expectRealJson(secondResponse);
  const second = (await secondResponse.json()) as OverlayResponse;
  const secondUrl = new URL(secondResponse.url());
  expect(secondUrl.searchParams.get("after_sequence")).toBe("200");
  expect(secondUrl.searchParams.get("limit")).toBe("200");
  expect(secondUrl.searchParams.get("as_of_revision")).toBe(String(first.lifecycle_revision));
  expect(second.lifecycle_revision).toBe(first.lifecycle_revision);
  expect(second.milestones).toHaveLength(200);
  expect(second.milestones[0].sequence).toBe(201);
  expect(second.milestones[199].sequence).toBe(400);
  expect(second.next_cursor).toBe(400);
  expect(second.has_more).toBe(true);
  expect(gateSnapshot(second)).toEqual(snapshot);
  await expectRenderedGateSnapshot(page, expectedIdentities);

  const thirdResponsePromise = page.waitForResponse((response) =>
    overlayResponseFor(response, fixture.caseId),
  );
  await page.getByRole("button", { name: "加载更多生命周期记录" }).click();
  const thirdResponse = await thirdResponsePromise;
  await expectRealJson(thirdResponse);
  const third = (await thirdResponse.json()) as OverlayResponse;
  const thirdUrl = new URL(thirdResponse.url());
  expect(thirdUrl.searchParams.get("after_sequence")).toBe("400");
  expect(thirdUrl.searchParams.get("limit")).toBe("200");
  expect(thirdUrl.searchParams.get("as_of_revision")).toBe(String(first.lifecycle_revision));
  expect(third.lifecycle_revision).toBe(first.lifecycle_revision);
  expect(third.milestones.map((item) => item.sequence)).toEqual([401]);
  expect(third.next_cursor).toBeNull();
  expect(third.has_more).toBe(false);
  expect(gateSnapshot(third)).toEqual(snapshot);

  await expectRenderedGateSnapshot(page, expectedIdentities);
  await expect(page.getByText("已加载全部生命周期记录", { exact: true })).toBeVisible();
  await expect(page.getByTestId("lifecycle-center-lane")).toBeVisible();
  await expect(page.getByTestId("document-evidence-lane")).toBeVisible();
  await expect(page.getByTestId("fee-obligation-lane")).toBeVisible();
  expect(observedApplicationResponses).toContain(loginResponse);
  expect(observedApplicationResponses).toContain(caseResponse);
  expect(observedApplicationResponses).toEqual(
    expect.arrayContaining([firstResponse, secondResponse, thirdResponse]),
  );
  expect(observedApplicationResponses.every((response) => !response.fromServiceWorker())).toBe(
    true,
  );
});
