import { expect, test } from "@playwright/test";
import type { Page, Request, Route } from "@playwright/test";

const documentId = "document-grant-review-ui";
const candidateId = "candidate-grant-review-ui";
const reviewerId = "reviewer-grant-review-ui";

test("document detail shows controlled grant evidence and lets a second person review it", async ({
  page,
}) => {
  let reviewRequest: Request | null = null;
  let reviewStatus: "PENDING" | "APPROVED" = "PENDING";
  let candidateListRequestCount = 0;

  await mockGrantReviewApi(page, {
    getReviewStatus: () => reviewStatus,
    onCandidateList: () => {
      candidateListRequestCount += 1;
    },
    onReview: async (route) => {
      reviewRequest = route.request();
      reviewStatus = "APPROVED";
      await fulfillJson(route, {
        candidate_id: candidateId,
        evidence_version_id: "evidence-grant-review-ui",
        review_status: reviewStatus,
        reviewer_id: reviewerId,
        reviewed_at: "2026-08-11T12:00:00",
        candidate_snapshot_hash: "b".repeat(64),
        review_role_config_id: "review-role-config-1",
        review_role_config_snapshot_hash: "c".repeat(64),
        disposition: "CHANGED",
      });
    },
  });

  await openDocument(page);

  const panel = page.getByTestId("grant-evidence-review-panel");
  const candidate = page.getByTestId(`grant-evidence-candidate-${candidateId}`);
  await expect(panel.getByRole("heading", { name: "授权证据候选复核" })).toBeVisible();
  expect(candidateListRequestCount).toBe(0);
  await expect(panel.getByText("暂无授权证据候选")).toHaveCount(0);
  await expect(panel.locator(".error-banner")).toHaveCount(0);
  await panel.getByRole("button", { name: "加载授权证据候选" }).click();
  await expect.poll(() => candidateListRequestCount).toBe(1);
  await expect(panel.getByRole("button", { name: "刷新候选" })).toBeVisible();
  await expect(candidate.getByText("来源记录：CNIPA-2026-0001")).toBeVisible();
  await expect(candidate.getByText("来源版本：2026.08.11")).toBeVisible();
  await expect(candidate.getByText("提出人：proposer-grant-review-ui")).toBeVisible();
  await expect(candidate.getByText("复核人：未复核")).toBeVisible();
  const conflict = page.getByTestId(
    `grant-evidence-conflict-${candidateId}-授权公告日`,
  );
  await expect(conflict.getByText("冲突字段：授权公告日")).toBeVisible();
  await expect(conflict.getByText("2026-08-01")).toBeVisible();
  await expect(conflict.getByText("2026-08-02")).toBeVisible();
  await expect(candidate.getByRole("button", { name: "批准候选" })).toBeVisible();
  await expect(candidate.getByRole("button", { name: "驳回候选" })).toBeVisible();
  await expect(panel.getByText("法律状态")).toHaveCount(0);

  await candidate.getByRole("textbox", { name: "复核理由" }).fill("已核对官方来源与冲突值");
  await candidate.getByRole("button", { name: "批准候选" }).click();

  await expect.poll(() => reviewRequest?.postDataJSON()).toEqual({
    decision: "APPROVED",
    reason: "已核对官方来源与冲突值",
  });
  await expect(candidate.getByText("复核状态：已批准")).toBeVisible();
  await expect(candidate.getByText(`复核人：${reviewerId}`)).toBeVisible();
  await expect.poll(() => candidateListRequestCount).toBe(2);
  await expect(panel.getByText("法律状态")).toHaveCount(0);
  await expect(page.getByText("授权证据候选已批准")).toBeVisible();
});

interface GrantReviewApiOptions {
  getReviewStatus: () => "PENDING" | "APPROVED";
  onCandidateList: () => void;
  onReview: (route: Route) => Promise<void>;
}

async function mockGrantReviewApi(
  page: Page,
  options: GrantReviewApiOptions,
): Promise<void> {
  await page.route("**/api/v1/**", async (route) => {
    const request = route.request();
    const apiPath = new URL(request.url()).pathname.replace(/^\/api\/v1/, "");

    if (request.method() === "GET" && apiPath === "/auth/me") {
      return fulfillJson(route, {
        user: { id: reviewerId, username: "授权证据复核人", is_active: true },
        roles: [],
        permissions: ["Doc.Read", "Doc.Edit"],
      });
    }
    if (request.method() === "GET" && apiPath === `/documents/${documentId}`) {
      return fulfillJson(route, backendDocument());
    }
    if (
      request.method() === "GET" &&
      apiPath === `/documents/${documentId}/grant-evidence-candidates`
    ) {
      options.onCandidateList();
      return fulfillJson(route, [candidateResponse(options.getReviewStatus())]);
    }
    if (
      request.method() === "POST" &&
      apiPath === `/documents/grant-evidence-candidates/${candidateId}/review`
    ) {
      return options.onReview(route);
    }

    return fulfillJson(route, { detail: "未处理的授权证据复核界面模拟请求" }, 404);
  });
}

async function openDocument(page: Page): Promise<void> {
  await page.addInitScript(() => {
    window.localStorage.setItem("fpms_token", "v8-grant-evidence-review-ui-token");
  });
  await page.goto(`/documents/${documentId}`, { waitUntil: "domcontentloaded" });
  await expect(page.getByRole("heading", { name: "授权证据复核测试文档" })).toBeVisible();
}

async function fulfillJson(route: Route, body: unknown, status = 200): Promise<void> {
  await route.fulfill({ status, contentType: "application/json", body: JSON.stringify(body) });
}

function backendDocument(): Record<string, unknown> {
  return {
    id: documentId,
    case_id: "case-grant-review-ui",
    title: "授权证据复核测试文档",
    direction: "IN",
    doc_type: "OFFICIAL_IN",
    doc_date: "2026-08-11",
    created_at: "2026-08-11T08:00:00",
    updated_at: "2026-08-11T08:00:00",
    attachments: [],
  };
}

function candidateResponse(
  status: "PENDING" | "APPROVED",
): Record<string, unknown> {
  return {
    candidate_id: candidateId,
    case_id: "case-grant-review-ui",
    document_id: documentId,
    evidence_version_id: "evidence-grant-review-ui",
    terminal_event_id: "terminal-event-grant-review-ui",
    source_config_id: "source-config-1",
    source_record_id: "CNIPA-2026-0001",
    source_version: "2026.08.11",
    original_reference: "https://example.invalid/cnipa/grant/0001",
    acquisition_method: "CONTROLLED_IMPORT",
    acquired_at: "2026-08-11T08:30:00",
    evidence_scope: "GRANT_ANNOUNCEMENT",
    proposal_role_config_id: "proposal-role-config-1",
    proposed_by: "proposer-grant-review-ui",
    proposed_at: "2026-08-11T09:00:00",
    review_status: status,
    reviewer_id: status === "APPROVED" ? reviewerId : null,
    reviewed_at: status === "APPROVED" ? "2026-08-11T12:00:00" : null,
    review_reason: status === "APPROVED" ? "已核对官方来源与冲突值" : null,
    acquisition_snapshot_hash: "a".repeat(64),
    candidate_snapshot_hash: "b".repeat(64),
    facts: [
      { name: "授权公告号", raw_value: "CN-2026-0001" },
      { name: "授权公告日", raw_value: "2026-08-01" },
    ],
    conflicts: [
      { name: "授权公告日", raw_values: ["2026-08-01", "2026-08-02"] },
    ],
  };
}
