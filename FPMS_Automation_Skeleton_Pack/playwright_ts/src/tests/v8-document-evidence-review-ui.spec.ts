import { expect, test } from "@playwright/test";
import type { Page, Request, Route } from "@playwright/test";

const documentId = "document-v8-review-ui";
const caseId = "case-v8-review-ui";
const evidenceVersionId = "evidence-v8-review-ui";

test("attachment review shows server state and lets a different reviewer approve", async ({ page }) => {
  let reviewRequest: Request | null = null;
  let reviewState: "PENDING" | "APPROVED" = "PENDING";

  await mockDocumentReviewApi(page, {
    currentUserId: "reviewer-v8-review-ui",
    onReview: async (route) => {
      reviewRequest = route.request();
      reviewState = "APPROVED";
      await fulfillJson(route, { review_state: reviewState });
    },
    getReviewState: () => reviewState,
  });

  await openDocument(page);

  const attachment = page.getByTestId(`attachment-${evidenceVersionId}`);
  await expect(attachment.getByText("创建人：creator-v8-review-ui")).toBeVisible();
  await expect(attachment.getByText("复核人：未复核")).toBeVisible();
  await expect(attachment.getByText("复核状态：待复核")).toBeVisible();

  await attachment.getByRole("button", { name: "通过" }).click();

  await expect.poll(() => reviewRequest?.postDataJSON()).toMatchObject({
    case_id: caseId,
    decision: "APPROVE",
    idempotency_key: `review-ui:${evidenceVersionId}:APPROVE`,
  });
  expect(reviewRequest?.postDataJSON().reviewed_at).toMatch(
    /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$/,
  );
  await expect(attachment.getByText("复核人：reviewer-v8-review-ui")).toBeVisible();
  await expect(attachment.getByText("复核状态：已通过")).toBeVisible();
  await expect(page.getByText("附件复核已通过")).toBeVisible();
});

test("attachment creator cannot review their own evidence", async ({ page }) => {
  let reviewCalls = 0;

  await mockDocumentReviewApi(page, {
    currentUserId: "creator-v8-review-ui",
    onReview: async (route) => {
      reviewCalls += 1;
      await fulfillJson(route, { detail: "不应提交创建人自审请求" }, 500);
    },
    getReviewState: () => "PENDING",
  });

  await openDocument(page);

  const attachment = page.getByTestId(`attachment-${evidenceVersionId}`);
  await expect(attachment.getByText("创建人不能复核自己的证据版本")).toBeVisible();
  await expect(attachment.getByRole("button", { name: "通过" })).toBeDisabled();
  await expect(attachment.getByRole("button", { name: "驳回" })).toBeDisabled();
  expect(reviewCalls).toBe(0);
});

test("attachment review replaces backend errors with Simplified Chinese", async ({ page }) => {
  await mockDocumentReviewApi(page, {
    currentUserId: "reviewer-v8-review-ui",
    onReview: async (route) => {
      await fulfillJson(
        route,
        {
          error: {
            code: "EVIDENCE_REVIEW_STATE_CONFLICT",
            message: "Stored evidence review state is invalid",
          },
        },
        409,
      );
    },
    getReviewState: () => "PENDING",
  });

  await openDocument(page);
  await page
    .getByTestId(`attachment-${evidenceVersionId}`)
    .getByRole("button", { name: "驳回" })
    .click();

  await expect(page.getByText("附件复核状态已变化，请刷新后重试。")).toBeVisible();
  await expect(page.getByText("Stored evidence review state is invalid")).toHaveCount(0);
});

interface ReviewApiOptions {
  currentUserId: string;
  onReview: (route: Route) => Promise<void>;
  getReviewState: () => "PENDING" | "APPROVED";
}

async function mockDocumentReviewApi(
  page: Page,
  options: ReviewApiOptions,
): Promise<void> {
  await page.route("**/api/v1/**", async (route) => {
    const request = route.request();
    const apiPath = new URL(request.url()).pathname.replace(/^\/api\/v1/, "");

    if (request.method() === "GET" && apiPath === "/auth/me") {
      return fulfillJson(route, {
        user: { id: options.currentUserId, username: "复核测试用户", is_active: true },
        roles: [],
        permissions: ["Doc.Read", "Doc.Edit"],
      });
    }
    if (request.method() === "GET" && apiPath === `/documents/${documentId}`) {
      return fulfillJson(route, backendDocument(options.getReviewState(), options.currentUserId));
    }
    if (
      request.method() === "POST"
      && apiPath === `/documents/evidence-versions/${evidenceVersionId}/review`
    ) {
      return options.onReview(route);
    }

    return fulfillJson(route, { detail: "未处理的 V8 文件证据复核界面模拟请求" }, 404);
  });
}

async function openDocument(page: Page): Promise<void> {
  await page.addInitScript(() => {
    window.localStorage.setItem("fpms_token", "v8-document-evidence-review-ui-token");
  });
  await page.goto(`/documents/${documentId}`, { waitUntil: "domcontentloaded" });
  await expect(page.getByRole("heading", { name: "复核界面测试文档" })).toBeVisible();
}

async function fulfillJson(route: Route, body: unknown, status = 200): Promise<void> {
  await route.fulfill({ status, contentType: "application/json", body: JSON.stringify(body) });
}

function backendDocument(
  reviewState: "PENDING" | "APPROVED",
  currentUserId: string,
): Record<string, unknown> {
  return {
    id: documentId,
    case_id: caseId,
    title: "复核界面测试文档",
    direction: "IN",
    doc_type: "CLIENT_IN",
    doc_date: "2026-07-23",
    created_at: "2026-07-23T08:00:00",
    updated_at: "2026-07-23T08:00:00",
    attachments: [
      {
        id: "attachment-v8-review-ui",
        document_id: documentId,
        file_name: "待复核证据.pdf",
        file_size: 1024,
        mime_type: "application/pdf",
        uploaded_at: "2026-07-23T08:00:00",
        evidence_version_id: evidenceVersionId,
        role: "SOURCE_DOCUMENT",
        creator_id: "creator-v8-review-ui",
        reviewer_id: reviewState === "APPROVED" ? currentUserId : null,
        review_state: reviewState,
        is_current: true,
        is_final: false,
      },
    ],
  };
}
