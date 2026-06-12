import { expect, test } from "@playwright/test";
import type { Page, Route } from "@playwright/test";
import fs from "node:fs";
import path from "node:path";

const apiBaseUrl = (process.env.FPMS_API_URL || "http://localhost:8000/api/v1").replace(/\/$/, "");
const repoRoot = path.resolve(process.cwd(), "../..");

const fixture = {
  caseId: "CASE-PD-P1-E2E",
  caseNo: "P1E2E-SMOKE",
  clientId: "CLIENT-PD-P1-E2E",
  filingPackageId: "FILING-PD-P1-E2E",
  feeDraftId: "FD-PD-P1-E2E",
  payListId: 860602,
  oaPackageId: "OA-PD-P1-E2E",
  sourceOaDocumentId: "DOC-OA-IN-PD-P1",
  replyDocumentId: "DOC-OA-OUT-PD-P1",
  receiptAttachmentId: "ATT-RECEIPT-PD-P1",
  letterDocumentId: "DOC-LETTER-PD-P1",
};

type ChecklistItem = {
  id: string;
  package_id: string;
  section_code: string;
  item_code: string;
  item_label: string;
  status: string;
  required: boolean;
  sort_order: number;
  evidence_note: string | null;
};

type MockState = {
  filingChecklist: ChecklistItem[];
  oaChecklist: ChecklistItem[];
  receiptRecorded: boolean;
  receiptMetadata: Record<string, unknown> | null;
  unhandledApiRequests: string[];
};

type LetterHandoffAttachmentPreview = {
  attachment_id: string;
  file_name: string;
  file_path: string;
  attachment_role: string;
  required: boolean;
  included: boolean;
  sort_order: number;
};

type LetterHandoffPreview = Record<string, unknown> & {
  attachments: LetterHandoffAttachmentPreview[];
};

let state: MockState;

test.beforeEach(async ({ page }) => {
  state = createMockState();
  await installApiContractMocks(page, state);
  await page.addInitScript(() => {
    window.localStorage.setItem("fpms_token", "pd-p1-e2e-token");
  });
});

test("@P1 全scope：案件官方字段维护入口和递交准备 gate/checklist 对齐客户流程", async ({ page }) => {
  const pageErrors = collectPageErrors(page);

  await page.goto(`/cases/no/${fixture.caseNo}/edit`, { waitUntil: "domcontentloaded" });
  await expect(page.getByRole("heading", { name: "编辑案件" })).toBeVisible();

  await page.getByText("申请人信息", { exact: true }).click();
  await expect(page.getByText("官方提交字段")).toBeVisible();
  await expect(page.getByPlaceholder("例如：中国 / CN").first()).toBeVisible();
  await expect(page.getByPlaceholder("例如：统一社会信用代码")).toBeVisible();
  await expect(page.getByPlaceholder("请输入官方证件号")).toBeVisible();
  await expect(page.getByPlaceholder("请输入官方邮编")).toBeVisible();

  await expect(page.getByText("发明人信息", { exact: true })).toBeVisible();
  await expect(page.getByPlaceholder("中国籍发明人需维护")).toBeVisible();

  await page.goto(`/official-workflows/filing-preparation?package_id=${fixture.filingPackageId}`, {
    waitUntil: "domcontentloaded",
  });
  await expect(page.getByRole("heading", { name: "新申请递交准备" })).toBeVisible();
  await expect(page.getByText("申请人官方邮编缺失").first()).toBeVisible();
  await expect(page.getByRole("link", { name: "到案件页维护" }).first()).toHaveAttribute(
    "href",
    `/cases/${fixture.caseId}/edit`,
  );
  await expect(page.getByText("技术交底书").first()).toBeVisible();
  await expect(page.getByText("委托指示（如有）")).toBeVisible();
  await expect(page.getByText("XML zip").first()).toBeVisible();
  await expect(page.getByText("合并 PDF").first()).toBeVisible();
  await expect(page.getByText("官方页面字段清单")).toBeVisible();
  await expect(page.getByText("接收类表格导入").first()).toBeVisible();

  await page.getByRole("button", { name: "确认页面预览" }).click();
  await expect(page.getByText("官方页面预览已人工确认")).toBeVisible();
  await page.getByRole("button", { name: "记录导入时间" }).click();
  await expect(page.getByText("专利业务办理系统导入请求类表格").first()).toBeVisible();
  expectNoUnexpectedRuntimeSignals(pageErrors, state);
});

test("@P1 全scope：OA答复包文件角色、人工动作、回执硬门禁和归档元数据", async ({ page }) => {
  const pageErrors = collectPageErrors(page);

  await page.goto(`/official-workflows/oa-reply?package_id=${fixture.oaPackageId}`, {
    waitUntil: "domcontentloaded",
  });
  await expect(page.getByRole("heading", { name: "OA答复工作包" })).toBeVisible();
  await expect(page.getByText("CN202610000001.0")).toBeVisible();
  await expect(page.getByText("第一次审查意见通知书").first()).toBeVisible();
  await expect(page.getByText("2026-08-20")).toBeVisible();
  await expect(page.getByText("详见随附 PDF 意见陈述书。")).toBeVisible();

  await expect(page.getByText("意见陈述 Word").first()).toBeVisible();
  await expect(page.getByText("PDF保真附件").first()).toBeVisible();
  await expect(page.getByText("修改后的权利要求书").first()).toBeVisible();
  await expect(page.getByText("修改对照页").first()).toBeVisible();
  await expect(page.getByText("其他证明文件").first()).toBeVisible();
  await expect(page.getByText("补交实验数据：是")).toBeVisible();
  await expect(page.getByText("不替代签名、扫码或正式提交")).toBeVisible();
  await expect(page.getByText("待回执归档").first()).toBeVisible();
  await expect(page.getByText("缺少必填回执元数据")).toBeVisible();
  await expect(page.getByRole("button", { name: "提交归档检查" })).toBeDisabled();

  await page.getByRole("button", { name: "确认云端二次下载" }).click();
  await expect(page.getByText("云端二次下载已人工确认").first()).toBeVisible();
  await page.getByRole("button", { name: "确认预览标签页" }).click();
  await expect(page.getByText("预览标签页已人工确认").first()).toBeVisible();
  await page.getByRole("button", { name: "确认提交结果" }).click();
  await expect(page.getByText("提交结果已人工确认").first()).toBeVisible();

  const archiveForm = page.locator(".archive-form");
  await archiveForm.getByPlaceholder("引用已上传附件ID").fill(fixture.receiptAttachmentId);
  await archiveForm.getByPlaceholder("请输入官方接收案件编号").fill("202606020001");
  await archiveForm.getByPlaceholder("请输入提交人").fill("流程人员A");
  await archiveForm.getByPlaceholder("请选择接收时间").fill("2026-06-02T10:30:00");
  await archiveForm.getByPlaceholder("逐行记录官方回执中的收到文件清单").fill("意见陈述书\n权利要求书\n修改对照页\n其他证明文件");
  await archiveForm.getByPlaceholder("可填写归档说明").fill("P1 E2E 人工下载并上传电子申请回执");
  await page.getByRole("button", { name: "记录回执元数据" }).click();
  await expect(page.getByText("回执元数据已记录")).toBeVisible();
  expect(state.receiptRecorded).toBe(true);

  await page.getByRole("button", { name: "确认回执归档" }).click();
  await expect(page.getByText("电子申请回执已归档核对").first()).toBeVisible();
  await page.getByRole("button", { name: "提交归档检查" }).click();
  await expect(page.getByText("归档检查已通过")).toBeVisible();
  await expect(page.getByText("回执依据已满足").first()).toBeVisible();
  await expect(page.getByText("归档证据已满足").first()).toBeVisible();
  expectNoUnexpectedRuntimeSignals(pageErrors, state);
});

test("@P1 全scope：费用联动、pay-list边界、信函交接和非范围声明", async ({ page }) => {
  const pageErrors = collectPageErrors(page);

  await page.goto(`/fees/drafts/${fixture.feeDraftId}?package_id=${fixture.filingPackageId}`, {
    waitUntil: "domcontentloaded",
  });
  await expect(page.getByText("费用联动核对")).toBeVisible();
  await expect(page.getByText("官方费率 / 费减清单来源待确认").first()).toBeVisible();
  await expect(page.getByText("旧系统 0 / 0.7 / 0.85 语义待客户确认").first()).toBeVisible();
  await expect(page.getByText("补充缴费信息模板字段待确认").first()).toBeVisible();
  await expect(page.getByText("内部 pay-list 不是官方上传 Excel").first()).toBeVisible();

  await page.goto(`/fee-management/pay-lists/${fixture.payListId}?package_id=${fixture.filingPackageId}`, {
    waitUntil: "domcontentloaded",
  });
  await expect(page.getByRole("heading", { name: "官费清单详情" })).toBeVisible();
  await expect(page.getByText("补充缴费信息模板").first()).toBeVisible();
  await expect(page.getByText("500").first()).toBeVisible();
  await expect(page.getByText("人工官方缴费").or(page.getByText("仅内部计划")).first()).toBeVisible();

  await page.goto(`/documents/${fixture.letterDocumentId}`, { waitUntil: "domcontentloaded" });
  await expect(page.getByText("格式函与龙虾交接")).toBeVisible();
  await expect(page.getByText("FORMAT_LETTER_OA1")).toBeVisible();
  await expect(page.getByText("张三老师：您好").first()).toBeVisible();
  await expect(page.getByText(`${fixture.caseNo} 第一次审查意见通知书`)).toBeVisible();
  await expect(page.getByText("一通格式函.docx").first()).toBeVisible();
  await expect(page.getByText("第一次审查意见通知书.pdf").first()).toBeVisible();
  await page.getByRole("button", { name: "生成交接记录" }).click();
  await expect(page.getByText("交接记录已生成")).toBeVisible();
  await expect(page.getByText("待交接").first()).toBeVisible();

  assertNoForbiddenP1AutomationClaims();
  expectNoUnexpectedRuntimeSignals(pageErrors, state);
});

function collectPageErrors(page: Page): string[] {
  const pageErrors: string[] = [];
  page.on("pageerror", (error) => pageErrors.push(error.message));
  return pageErrors;
}

function expectNoUnexpectedRuntimeSignals(pageErrors: string[], mockState: MockState): void {
  expect(pageErrors).toEqual([]);
  expect(mockState.unhandledApiRequests).toEqual([]);
}

async function installApiContractMocks(page: Page, mockState: MockState): Promise<void> {
  await page.route(`${apiBaseUrl}/**`, async (route) => {
    const request = route.request();
    const url = new URL(request.url());
    const apiPath = url.pathname.replace(/^\/api\/v1/, "");
    const method = request.method().toUpperCase();

    if (method === "GET" && apiPath === "/auth/me") {
      return fulfillJson(route, { permissions: ["*"] });
    }

    if (method === "GET" && apiPath === "/clients") {
      return fulfillJson(route, {
        items: [backendClient()],
        page: 1,
        page_size: 100,
        total: 1,
      });
    }

    if (method === "GET" && apiPath === `/clients/${fixture.clientId}`) {
      return fulfillJson(route, backendClient());
    }

    if (method === "GET" && apiPath === "/cases") {
      return fulfillJson(route, {
        items: [backendCase()],
        page: 1,
        page_size: 1,
        total: 1,
        summary: { total_case_count: 1 },
      });
    }

    if (method === "GET" && apiPath === `/cases/${fixture.caseId}`) {
      return fulfillJson(route, backendCase());
    }

    if (method === "GET" && apiPath === `/official-work-packages/${fixture.filingPackageId}/filing-preparation`) {
      return fulfillJson(route, filingPreparationPackage(mockState));
    }

    if (
      method === "PATCH"
      && apiPath.startsWith(`/official-work-packages/${fixture.filingPackageId}/filing-preparation/checklist/`)
    ) {
      const itemCode = apiPath.split("/").pop() || "";
      const item = upsertChecklist(mockState.filingChecklist, fixture.filingPackageId, itemCode, await requestBody(request), {
        section_code: "FILING_PAGE",
        item_label: itemCode === "PREVIEW_CONFIRMED" ? "官方页面预览" : "签名和递交责任",
        sort_order: itemCode === "PREVIEW_CONFIRMED" ? 40 : 50,
      });
      return fulfillJson(route, { package_id: fixture.filingPackageId, checklist_item: item });
    }

    if (method === "POST" && apiPath === `/official-work-packages/${fixture.filingPackageId}/filing-preparation/external-operations`) {
      const item = upsertChecklist(
        mockState.filingChecklist,
        fixture.filingPackageId,
        "CNIPA_IMPORT_STARTED",
        { status: "DONE", evidence_note: "专利业务办理系统导入请求类表格" },
        {
          section_code: "EXTERNAL_OPERATION",
          item_label: "接收类表格导入",
          sort_order: 60,
        },
      );
      return fulfillJson(route, { package_id: fixture.filingPackageId, checklist_item: item });
    }

    if (method === "GET" && apiPath === `/official-work-packages/${fixture.oaPackageId}/oa-reply`) {
      return fulfillJson(route, oaReplyPackage(mockState));
    }

    if (
      method === "PATCH"
      && apiPath.startsWith(`/official-work-packages/${fixture.oaPackageId}/oa-reply/checklist/`)
    ) {
      const itemCode = apiPath.split("/").pop() || "";
      const defaults = oaChecklistDefaults(itemCode);
      const item = upsertChecklist(mockState.oaChecklist, fixture.oaPackageId, itemCode, await requestBody(request), defaults);
      return fulfillJson(route, { package_id: fixture.oaPackageId, checklist_item: item });
    }

    if (method === "POST" && apiPath === `/official-work-packages/${fixture.oaPackageId}/receipts`) {
      mockState.receiptRecorded = true;
      mockState.receiptMetadata = await requestBody(request);
      return fulfillJson(route, {
        id: "RECEIPT-PD-P1-E2E",
        package_id: fixture.oaPackageId,
        receipt_kind: "ELECTRONIC_APPLICATION_RECEIPT",
        archive_status: "ARCHIVED",
        ...mockState.receiptMetadata,
      });
    }

    if (method === "POST" && apiPath === `/official-work-packages/${fixture.oaPackageId}/archive`) {
      const receiptDone = mockState.oaChecklist.some((item) => item.item_code === "RECEIPT_CONFIRMED" && item.status === "DONE");
      const canArchive = mockState.receiptRecorded && receiptDone;
      return fulfillJson(route, {
        package: {
          id: fixture.oaPackageId,
          case_id: fixture.caseId,
          package_kind: "OA_REPLY",
          status: canArchive ? "ARCHIVED" : "WAITING_RECEIPT",
          source_document_id: fixture.sourceOaDocumentId,
          reply_document_id: fixture.replyDocumentId,
          external_system: "CNIPA_WEB",
          remark: null,
        },
        evaluation: {
          package_id: fixture.oaPackageId,
          status: canArchive ? "ARCHIVED" : "WAITING_RECEIPT",
          can_archive: canArchive,
          receipt_hard_gate_satisfied: canArchive,
          blockers: canArchive
            ? []
            : [
                {
                  blocker_type: "RECEIPT",
                  item_code: "RECEIPT_CONFIRMED",
                  item_label: "回执归档",
                  status: "PENDING",
                  message: "缺少电子申请回执或收到文件清单。",
                },
              ],
        },
      });
    }

    if (method === "GET" && apiPath === `/official-work-packages/${fixture.filingPackageId}/fee-linkage`) {
      return fulfillJson(route, officialFeeLinkage());
    }

    if (method === "GET" && apiPath === `/fees/drafts/${fixture.feeDraftId}`) {
      return fulfillJson(route, backendFeeDraft());
    }

    if (method === "GET" && apiPath === `/fees/drafts/${fixture.feeDraftId}/items`) {
      return fulfillJson(route, backendFeeItems());
    }

    if (method === "GET" && apiPath === `/pay-lists/${fixture.payListId}`) {
      return fulfillJson(route, backendPayListDetail());
    }

    if (method === "GET" && apiPath === `/documents/${fixture.letterDocumentId}`) {
      return fulfillJson(route, backendLetterDocument());
    }

    if (method === "GET" && apiPath === `/official-documents/${fixture.letterDocumentId}/letter-handoff/preview`) {
      return fulfillJson(route, letterHandoffPreview());
    }

    if (method === "POST" && apiPath === `/official-documents/${fixture.letterDocumentId}/letter-handoff`) {
      return fulfillJson(route, {
        preview: letterHandoffPreview(),
        handoff: {
          id: "LH-PD-P1-E2E",
          source_document_id: fixture.letterDocumentId,
          generated_document_id: null,
          format_letter_mapping_id: "MAP-FORMAT-LETTER-OA1",
          format_letter_template_id: "TPL-FORMAT-LETTER-OA1",
          client_contact_id: "CONTACT-PD-P1-E2E",
          contact_selection_source: "PRIMARY_CONTACT",
          salutation_source: "MAPPING_RULE",
          salutation_text: "张三老师：您好",
          generated_word_path: "letters/P1E2E-SMOKE/一通格式函.docx",
          mail_subject: `${fixture.caseNo} 第一次审查意见通知书`,
          mail_body_draft: "张三老师：您好\n请查收本次官文及处理意见。",
          longxia_handoff_status: "PENDING",
          longxia_handoff_payload: null,
          handoff_at: null,
          remark: null,
          attachments: letterHandoffPreview().attachments.map((attachment, index) => ({
            id: `LH-ATT-${index + 1}`,
            handoff_id: "LH-PD-P1-E2E",
            attachment_id: attachment.attachment_id,
            file_name: attachment.file_name,
            file_path: attachment.file_path,
            attachment_role: attachment.attachment_role,
            required: attachment.required,
            included: attachment.included,
            sort_order: attachment.sort_order,
          })),
        },
      });
    }

    mockState.unhandledApiRequests.push(`${method} ${apiPath}`);
    return fulfillJson(route, { detail: "Unhandled P1 E2E mock route" }, 404);
  });
}

async function fulfillJson(route: Route, body: unknown, status = 200): Promise<void> {
  await route.fulfill({
    status,
    headers: {
      "access-control-allow-origin": "*",
      "content-type": "application/json",
    },
    body: JSON.stringify(body),
  });
}

async function requestBody(request: { postData(): string | null }): Promise<Record<string, unknown>> {
  const raw = request.postData();
  if (!raw) return {};
  return JSON.parse(raw) as Record<string, unknown>;
}

function createMockState(): MockState {
  return {
    filingChecklist: [
      checklistItem(fixture.filingPackageId, "FILING_PAGE", "CNIPA_FORM_IMPORTED", "接收类表格导入", "PENDING", true, 10, null),
      checklistItem(fixture.filingPackageId, "FILING_PAGE", "PREVIEW_CONFIRMED", "官方页面预览", "PENDING", true, 20, null),
      checklistItem(fixture.filingPackageId, "FILING_PAGE", "SIGNATURE_CONFIRMED", "签名和递交责任", "PENDING", true, 30, null),
    ],
    oaChecklist: [
      checklistItem(fixture.oaPackageId, "OA_PAGE", "CLOUD_SECOND_DOWNLOAD_CONFIRMED", "云端二次下载", "PENDING", true, 10, null),
      checklistItem(fixture.oaPackageId, "OA_PAGE", "QUERY_RESULT_CONFIRMED", "查询结果", "DONE", true, 20, "已核对申请号、官文代码和期限"),
      checklistItem(fixture.oaPackageId, "OA_PAGE", "BUSINESS_HANDLING_CONFIRMED", "业务办理", "DONE", true, 30, "已进入OA答复办理页面"),
      checklistItem(fixture.oaPackageId, "OA_PAGE", "PREVIEW_TABS_CONFIRMED", "预览标签页", "PENDING", true, 40, null),
      checklistItem(fixture.oaPackageId, "OA_PAGE", "SIGNATURE_CONFIRMED", "签名确认", "PENDING", true, 50, null),
      checklistItem(fixture.oaPackageId, "OA_PAGE", "SUBMISSION_CONFIRMED", "提交确认", "PENDING", true, 60, null),
      checklistItem(fixture.oaPackageId, "OA_PAGE", "RECEIPT_CONFIRMED", "回执归档", "PENDING", true, 70, null),
    ],
    receiptRecorded: false,
    receiptMetadata: null,
    unhandledApiRequests: [],
  };
}

function checklistItem(
  packageId: string,
  sectionCode: string,
  itemCode: string,
  itemLabel: string,
  status: string,
  required: boolean,
  sortOrder: number,
  evidenceNote: string | null,
): ChecklistItem {
  return {
    id: `CHK-${packageId}-${itemCode}`,
    package_id: packageId,
    section_code: sectionCode,
    item_code: itemCode,
    item_label: itemLabel,
    status,
    required,
    sort_order: sortOrder,
    evidence_note: evidenceNote,
  };
}

function upsertChecklist(
  items: ChecklistItem[],
  packageId: string,
  itemCode: string,
  payload: Record<string, unknown>,
  defaults: Pick<ChecklistItem, "section_code" | "item_label" | "sort_order">,
): ChecklistItem {
  const next: ChecklistItem = {
    id: `CHK-${packageId}-${itemCode}`,
    package_id: packageId,
    section_code: defaults.section_code,
    item_code: itemCode,
    item_label: defaults.item_label,
    status: String(payload.status || "DONE"),
    required: true,
    sort_order: defaults.sort_order,
    evidence_note: typeof payload.evidence_note === "string" ? payload.evidence_note : null,
  };
  const index = items.findIndex((item) => item.item_code === itemCode);
  if (index >= 0) {
    items.splice(index, 1, next);
  } else {
    items.push(next);
  }
  items.sort((left, right) => left.sort_order - right.sort_order);
  return next;
}

function oaChecklistDefaults(itemCode: string): Pick<ChecklistItem, "section_code" | "item_label" | "sort_order"> {
  const labels: Record<string, [string, number]> = {
    CLOUD_SECOND_DOWNLOAD_CONFIRMED: ["云端二次下载", 10],
    PREVIEW_TABS_CONFIRMED: ["预览标签页", 40],
    SUBMISSION_CONFIRMED: ["提交确认", 60],
    RECEIPT_CONFIRMED: ["回执归档", 70],
  };
  const [itemLabel, sortOrder] = labels[itemCode] || [itemCode, 99];
  return { section_code: "OA_PAGE", item_label: itemLabel, sort_order: sortOrder };
}

function backendClient(): Record<string, unknown> {
  return {
    id: fixture.clientId,
    client_code: "PD-P1-CUSTOMER",
    name_cn: "P1全流程客户有限公司",
    name_en: null,
    email: "p1-customer@example.com",
    client_type: "CORP",
    default_currency: "CNY",
    is_active: true,
    created_at: "2026-06-02T09:00:00",
    updated_at: "2026-06-02T09:00:00",
  };
}

function backendCase(): Record<string, unknown> {
  return {
    id: fixture.caseId,
    case_no: fixture.caseNo,
    case_type: "NORMAL",
    patent_category: "INV",
    flow_dir: "CN_DOMESTIC",
    client_id: fixture.clientId,
    client_name: "P1全流程客户有限公司",
    title_cn: "P1全流程测试方法及系统",
    status: "NOT_FILED",
    app_no: "CN202610000001.0",
    recv_date: "2026-06-02",
    filing_date: null,
    spec_pages: 18,
    claim_count: 10,
    draw_pages: 3,
    has_exam_request: true,
    fee_reduction: "0.85",
    discount_rate: "0.85",
    primary_agent_id: "AGENT-PD-P1",
    draftor_id: "DRAFTOR-PD-P1",
    applicants: [
      {
        seq: 1,
        is_first: true,
        name_cn: "P1测试申请人有限公司",
        address_cn: "北京市海淀区测试路1号",
        nationality: "CN",
        certificate_type: "统一社会信用代码",
        certificate_no: "91110000P1E2E0000X",
        official_postcode: null,
        official_applicant_kind: "企业",
      },
    ],
    inventors: [
      {
        seq: 1,
        name_cn: "李四",
        nationality: "CN",
        china_id_no: "110101199001011234",
      },
    ],
    priorities: [],
    bio_deposits: [],
    agent_splits: [],
    created_at: "2026-06-02T09:00:00",
    updated_at: "2026-06-02T09:00:00",
  };
}

function filingPreparationPackage(mockState: MockState): Record<string, unknown> {
  return {
    package: {
      id: fixture.filingPackageId,
      case_id: fixture.caseId,
      package_kind: "FILING_PREP",
      status: "NEEDS_MAINTENANCE",
      source_document_id: null,
      reply_document_id: null,
      external_system: "CNIPA_WEB",
      remark: "P1 E2E filing workflow fixture",
    },
    official_field_summary: {
      status: "NEEDS_MAINTENANCE",
      missing_codes: ["APPLICANT_OFFICIAL_POSTCODE"],
      items: [
        {
          code: "APPLICANT_OFFICIAL_POSTCODE",
          label: "申请人官方邮编",
          status: "NEEDS_MAINTENANCE",
          message: "申请人官方邮编缺失",
        },
        {
          code: "INVENTOR_CHINA_ID_NO",
          label: "中国籍发明人身份证号",
          status: "READY",
          message: "已在案件发明人行维护",
        },
      ],
    },
    technical_disclosure_gate: {
      role: "TECHNICAL_DISCLOSURE",
      required: true,
      status: "READY",
      attachment_id: "ATT-TECH-DISCLOSURE",
      file_name: "技术交底书.docx",
    },
    commission_instruction_gate: {
      role: "COMMISSION_INSTRUCTION",
      required: false,
      status: "PENDING",
      attachment_id: null,
      file_name: null,
    },
    filing_file_roles: [
      manifest("TECHNICAL_DISCLOSURE", "ATT-TECH-DISCLOSURE", "技术交底书.docx", true, true, 10, "新建案件 gate：技术交底书必传"),
      manifest("COMMISSION_INSTRUCTION", null, null, false, false, 20, "客户反馈为如有，不作为固定必传"),
      manifest("FILING_XML_ZIP", "ATT-FILING-ZIP", "请求类表格.zip", true, true, 30, "为专利业务办理系统导入做准备"),
      manifest("FILING_MERGED_PDF", null, null, true, false, 40, "官方提交后人工下载并归档"),
    ],
    official_page_checklist: mockState.filingChecklist,
    xml_zip: {
      status: "READY",
      attachment_id: "ATT-FILING-ZIP",
      file_name: "请求类表格.zip",
      placeholder: null,
    },
    merged_pdf_archive_status: "PENDING",
    fee_summary: {
      draft_count: 1,
      pay_list_count: 1,
      official_template_ready: false,
      blocker_count: 2,
    },
  };
}

function oaReplyPackage(mockState: MockState): Record<string, unknown> {
  return {
    package: {
      id: fixture.oaPackageId,
      case_id: fixture.caseId,
      package_kind: "OA_REPLY",
      status: "WAITING_RECEIPT",
      source_document_id: fixture.sourceOaDocumentId,
      reply_document_id: fixture.replyDocumentId,
      external_system: "CNIPA_WEB",
      remark: "P1 E2E OA reply fixture",
    },
    source_document: {
      id: fixture.sourceOaDocumentId,
      title: "第一次审查意见通知书",
      template_code: "OA_IN",
      direction: "IN",
      doc_date: "2026-05-20",
      ref_no: "OA-1",
      reply_to_id: null,
      need_reply: true,
      reply_date: null,
    },
    reply_document: {
      id: fixture.replyDocumentId,
      title: "第一次审查意见答复",
      template_code: "OA_OUT",
      direction: "OUT",
      doc_date: "2026-06-02",
      ref_no: "OA-OUT-1",
      reply_to_id: fixture.sourceOaDocumentId,
      need_reply: false,
      reply_date: "2026-06-02",
    },
    application_no: "CN202610000001.0",
    applicant_display: "P1测试申请人有限公司",
    notice_code: "OA-1",
    notice_name: "第一次审查意见通知书",
    issue_sequence: "一通",
    issue_date: "2026-05-20",
    official_due_date: "2026-08-20",
    internal_due_date: "2026-08-13",
    reply_status: "WAITING_RECEIPT",
    statement_text: "详见随附 PDF 意见陈述书。",
    statement_word: {
      role: "OA_STATEMENT_WORD",
      status: "READY",
      attachment_id: "ATT-OA-STATEMENT-WORD",
      file_name: "意见陈述书.docx",
      external_upload_position: "陈述的意见",
    },
    statement_pdf: {
      role: "OA_STATEMENT_PDF",
      status: "READY",
      attachment_id: "ATT-OA-STATEMENT-PDF",
      file_name: "意见陈述书.pdf",
      external_upload_position: "附加文件：意见陈述书PDF",
    },
    modified_claim_files: [
      {
        role: "OA_MODIFIED_CLAIMS",
        status: "READY",
        attachment_id: "ATT-MODIFIED-CLAIMS",
        file_name: "修改后的权利要求书.docx",
        external_upload_position: "权利要求书",
      },
    ],
    comparison_page: {
      role: "OA_AMENDMENT_COMPARISON",
      status: "READY",
      attachment_id: "ATT-COMPARISON",
      file_name: "修改对照页.pdf",
      external_upload_position: "附加文件：修改对照页",
    },
    proof_files: [
      {
        role: "OA_OTHER_PROOF",
        status: "READY",
        attachment_id: "ATT-EXPERIMENT",
        file_name: "实验数据.pdf",
        external_upload_position: "附加文件：其他证明文件",
      },
    ],
    experiment_data_submitted: true,
    official_page_checklist: mockState.oaChecklist,
    oa_file_roles: [
      manifest("OA_STATEMENT_WORD", "ATT-OA-STATEMENT-WORD", "意见陈述书.docx", true, true, 10, "意见陈述正文来源"),
      manifest("OA_STATEMENT_PDF", "ATT-OA-STATEMENT-PDF", "意见陈述书.pdf", true, true, 20, "公式/表格/图片保真附件"),
      manifest("OA_MODIFIED_CLAIMS", "ATT-MODIFIED-CLAIMS", "修改后的权利要求书.docx", true, true, 30, "主要修改文件"),
      manifest("OA_AMENDMENT_COMPARISON", "ATT-COMPARISON", "修改对照页.pdf", true, true, 40, "官方附加文件"),
      manifest("OA_OTHER_PROOF", "ATT-EXPERIMENT", "实验数据.pdf", false, true, 50, "按需补交实验数据"),
      manifest("RECEIPT_PDF", mockState.receiptRecorded ? fixture.receiptAttachmentId : null, null, true, mockState.receiptRecorded, 60, "关闭工作包硬门禁"),
    ],
  };
}

function officialFeeLinkage(): Record<string, unknown> {
  return {
    package_id: fixture.filingPackageId,
    case_id: fixture.caseId,
    payment_execution_mode: "MANUAL_OFFICIAL_PAYMENT",
    official_excel_template_ready: false,
    official_excel_generation_allowed: false,
    fee_drafts: [
      {
        id: fixture.feeDraftId,
        draft_type: "APPLY_FEE",
        status: "OPEN",
        currency: "CNY",
        total_gov: "950",
        total_service: "3000",
        total_misc: "0",
        amount: "3950",
        official_fee_reduction_note: "旧系统 0 / 0.7 / 0.85 语义待客户确认",
        official_template_status: "NEEDS_CONFIRMATION",
        official_template_version: null,
        official_template_note: "补充缴费信息模板字段待确认",
      },
    ],
    pay_lists: [
      {
        id: fixture.payListId,
        pay_list_no: "PL-PD-P1-E2E",
        status: "EXPORTED",
        currency: "CNY",
        planned_pay_date: "2026-06-05",
        paid_date: null,
        total_amount: "950",
        official_upload_template_status: "NEEDS_CONFIRMATION",
        official_upload_template_name: "补充缴费信息模板",
        official_upload_batch_limit: 500,
        official_pay_list_boundary_note: "内部 pay-list 不是官方上传 Excel；需客户提供官方模板样例后再生成。",
        manual_payment_status: "PENDING",
        gov_payment_statuses: ["PENDING"],
      },
    ],
    checklist: [
      {
        id: "FEE-CHK-RATE",
        fee_draft_id: fixture.feeDraftId,
        pay_list_id: null,
        checklist_code: "OFFICIAL_RATE_SOURCE",
        checklist_label: "官方费率来源",
        status: "NEEDS_CONFIRMATION",
        required: true,
        blocker_reason: "官方费率 / 费减清单来源待确认",
        sort_order: 10,
      },
      {
        id: "FEE-CHK-TEMPLATE",
        fee_draft_id: null,
        pay_list_id: fixture.payListId,
        checklist_code: "OFFICIAL_EXCEL_TEMPLATE",
        checklist_label: "补充缴费信息模板",
        status: "NEEDS_CONFIRMATION",
        required: true,
        blocker_reason: "补充缴费信息模板字段待确认",
        sort_order: 20,
      },
    ],
    customer_confirmation_blockers: [
      {
        blocker_code: "RATE_SOURCE",
        blocker_label: "官方费率来源",
        source_type: "FEE_DRAFT",
        source_id: fixture.feeDraftId,
        status: "NEEDS_CONFIRMATION",
        message: "官方费率 / 费减清单来源待确认",
      },
      {
        blocker_code: "PAY_LIST_TEMPLATE",
        blocker_label: "补充缴费信息模板",
        source_type: "PAY_LIST",
        source_id: String(fixture.payListId),
        status: "NEEDS_CONFIRMATION",
        message: "补充缴费信息模板字段待确认；建议上限 500 行。",
      },
    ],
  };
}

function backendFeeDraft(): Record<string, unknown> {
  return {
    id: fixture.feeDraftId,
    case_id: fixture.caseId,
    case_no: fixture.caseNo,
    client_id: fixture.clientId,
    client_name: "P1全流程客户有限公司",
    draft_type: "APPLY_FEE",
    currency: "CNY",
    status: "OPEN",
    total_gov: "950",
    total_service: "3000",
    total_misc: "0",
    amount: "3950",
    official_fee_reduction_note: "旧系统 0 / 0.7 / 0.85 语义待客户确认",
    official_template_status: "NEEDS_CONFIRMATION",
    official_template_version: null,
    official_template_note: "补充缴费信息模板字段待确认",
    created_at: "2026-06-02T09:00:00",
    updated_at: "2026-06-02T09:00:00",
  };
}

function backendFeeItems(): Record<string, unknown>[] {
  return [
    {
      id: "FEE-ITEM-PD-P1-GOV",
      draft_id: fixture.feeDraftId,
      case_id: fixture.caseId,
      rate_id: "RATE-APPLY",
      fee_code: "APPLY_FEE",
      fee_name: "申请费",
      fee_type: "GOV",
      quantity: 1,
      unit_price: "950",
      amount: "950",
      remark: "申请费",
    },
  ];
}

function backendPayListDetail(): Record<string, unknown> {
  return {
    pay_list: {
      id: fixture.payListId,
      pay_list_no: "PL-PD-P1-E2E",
      client_id: fixture.clientId,
      client_name: "P1全流程客户有限公司",
      currency: "CNY",
      status: "EXPORTED",
      planned_pay_date: "2026-06-05",
      paid_date: null,
      total_amount: "950",
      remark: "补充缴费信息模板字段待确认；内部清单不等同官方 Excel。",
      created_at: "2026-06-02T09:00:00",
      updated_at: "2026-06-02T09:00:00",
      created_by: "流程人员A",
      updated_by: "流程人员A",
    },
    gov_payments: [
      {
        id: 960602,
        pay_list_id: fixture.payListId,
        case_id: fixture.caseId,
        fee_item_id: "FEE-ITEM-PD-P1-GOV",
        status: "PENDING",
        currency: "CNY",
        paid_date: null,
        paid_amount: "950",
        official_receipt_no: null,
        remark: "人工官方缴费后登记",
        created_at: "2026-06-02T09:00:00",
        updated_at: "2026-06-02T09:00:00",
        created_by: "流程人员A",
        updated_by: "流程人员A",
      },
    ],
  };
}

function backendLetterDocument(): Record<string, unknown> {
  return {
    id: fixture.letterDocumentId,
    case_id: fixture.caseId,
    client_id: fixture.clientId,
    client_name: "P1全流程客户有限公司",
    doc_template_id: null,
    template_code: "FORMAT_LETTER_OA1",
    direction: "OUT",
    doc_type: "CLIENT_OUT",
    doc_date: "2026-06-02",
    title: "第一次审查意见通知书客户信函",
    ref_no: "LETTER-OA1",
    extra_data: "格式函交接预览，供龙虾邮件流程使用。",
    created_at: "2026-06-02T09:00:00",
    updated_at: "2026-06-02T09:00:00",
    attachments: [
      attachment("ATT-FORMAT-LETTER", fixture.letterDocumentId, "一通格式函.docx", "FORMAT_LETTER_WORD", false, false),
      attachment("ATT-OA-IN-PDF", fixture.letterDocumentId, "第一次审查意见通知书.pdf", "SOURCE_DOCUMENT", false, false),
    ],
    reply_to_id: fixture.sourceOaDocumentId,
    need_reply: false,
    reply_date: "2026-06-02",
    case_no: fixture.caseNo,
    outgoing_reg_no: null,
    forward_date: null,
  };
}

function letterHandoffPreview(): LetterHandoffPreview {
  return {
    source_document_id: fixture.letterDocumentId,
    case_id: fixture.caseId,
    case_no: fixture.caseNo,
    mapping: {
      id: "MAP-FORMAT-LETTER-OA1",
      format_letter_template_id: "TPL-FORMAT-LETTER-OA1",
      format_letter_template_code: "FORMAT_LETTER_OA1",
      output_name_rule: "{case_no}-一通格式函.docx",
      contact_rule_code: "PRIMARY_CONTACT",
      salutation_rule_code: "TITLE_SUFFIX",
    },
    template_status: "READY",
    client_contact_id: "CONTACT-PD-P1-E2E",
    contact: {
      id: "CONTACT-PD-P1-E2E",
      contact_name: "张三",
      title: "老师",
      email: "zhangsan@example.com",
    },
    contact_selection_source: "PRIMARY_CONTACT",
    salutation_source: "MAPPING_RULE",
    salutation_text: "张三老师：您好",
    generated_word_path: "letters/P1E2E-SMOKE/一通格式函.docx",
    mail_subject: `${fixture.caseNo} 第一次审查意见通知书`,
    mail_body_draft: "张三老师：您好\n请查收本次官文及处理意见。",
    attachments: [
      {
        attachment_id: "ATT-FORMAT-LETTER",
        file_name: "一通格式函.docx",
        file_path: "letters/P1E2E-SMOKE/一通格式函.docx",
        attachment_role: "FORMAT_LETTER_WORD",
        required: true,
        included: true,
        sort_order: 10,
      },
      {
        attachment_id: "ATT-OA-IN-PDF",
        file_name: "第一次审查意见通知书.pdf",
        file_path: "official/OA-1.pdf",
        attachment_role: "SOURCE_DOCUMENT",
        required: true,
        included: true,
        sort_order: 20,
      },
    ],
  };
}

function manifest(
  role: string,
  attachmentId: string | null,
  fileName: string | null,
  required: boolean,
  present: boolean,
  sortOrder: number,
  note: string,
): Record<string, unknown> {
  return {
    id: `MANIFEST-${role}`,
    package_id: role.startsWith("OA_") || role === "RECEIPT_PDF" ? fixture.oaPackageId : fixture.filingPackageId,
    attachment_id: attachmentId,
    official_file_role: role,
    source_role_alias: fileName,
    external_upload_position: present ? "官方页面对应位置" : null,
    content_hash: present ? `sha256-${role.toLowerCase()}` : null,
    required,
    present,
    sort_order: sortOrder,
    note,
  };
}

function attachment(
  id: string,
  documentId: string,
  fileName: string,
  officialFileRole: string,
  isArchiveEvidence: boolean,
  isReceiptEvidence: boolean,
): Record<string, unknown> {
  return {
    id,
    document_id: documentId,
    file_name: fileName,
    file_size: 1024,
    mime_type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    uploaded_at: "2026-06-02T09:00:00",
    official_file_role: officialFileRole,
    source_role_alias: null,
    external_upload_position: "信函交接附件清单",
    content_hash: `sha256-${id.toLowerCase()}`,
    package_usage_hint: "已纳入信函交接",
    is_archive_evidence: isArchiveEvidence,
    is_receipt_evidence: isReceiptEvidence,
  };
}

function assertNoForbiddenP1AutomationClaims(): void {
  const files = [
    "frontend/src/modules/cases/pages/FilingPreparation.vue",
    "frontend/src/modules/documents/pages/OAReplyPackage.vue",
    "frontend/src/modules/officialWorkflows/components/ReceiptArchivePanel.vue",
    "frontend/src/modules/officialWorkflows/components/FeeLinkagePanel.vue",
    "frontend/src/modules/officialWorkflows/components/LetterHandoffPanel.vue",
  ].map((relativePath) => path.join(repoRoot, relativePath));
  const forbiddenPatterns = [
    /自动提交/g,
    /自动签名/g,
    /自动扫码/g,
    /自动缴费/g,
    /自动发送邮件/g,
    /替换龙虾/g,
    /direct submit/gi,
  ];

  for (const file of files) {
    const source = fs.readFileSync(file, "utf-8");
    for (const pattern of forbiddenPatterns) {
      expect(source, `${path.relative(repoRoot, file)} must not contain ${pattern}`).not.toMatch(pattern);
    }
  }
}
