import { expect, test } from "@playwright/test";
import type { APIRequestContext, Page } from "@playwright/test";
import { execFileSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";

process.env.NO_PROXY = mergeNoProxy(process.env.NO_PROXY);
process.env.no_proxy = mergeNoProxy(process.env.no_proxy);

const apiBaseUrl = normalizeApiBaseUrl(process.env.FPMS_API_URL || "http://127.0.0.1:8000/api/v1");
const repoRoot = path.resolve(process.cwd(), "../..");
const backendPython = path.join(repoRoot, "backend", ".venv", "bin", "python");
const liveSeedScript = path.join(process.cwd(), "src", "support", "pdP1LiveSeed.py");

type LiveFixture = {
  caseId: string;
  caseNo: string;
  clientId: string;
  filingPackageId: string;
  feeDraftId: string;
  payListId: number;
  oaPackageId: string;
  sourceOaDocumentId: string;
  replyDocumentId: string;
  receiptAttachmentId: string;
  letterDocumentId: string;
};

type OfficialFeePreviewResponse = {
  case_id: string;
  draft_type: string;
  trigger_event: string;
  idempotency_key: string;
  currency: string;
  preview_only: boolean;
  total_gov: string | number;
  candidates: Array<{
    fee_code: string;
    fee_type: string;
    quantity: string | number;
    amount: string | number;
    source_doc?: string | null;
  }>;
};

type FeeDraftDetailResponse = {
  id: string;
  draft_type: string;
  total_gov: string | number;
  total_service: string | number;
  total_misc: string | number;
  amount: string | number;
};

type FeeItemResponse = {
  fee_code?: string | null;
  fee_type?: string | null;
  amount: string | number;
};

type CaseListResponse = {
  items: Array<{
    id: string;
    case_no: string;
    client_id?: string | null;
    client_name?: string | null;
    status?: string | null;
  }>;
  total: number;
};

type ClientListResponse = {
  items: Array<{
    id: string;
    client_code?: string | null;
    name: string;
  }>;
  total: number;
};

type CaseDetailResponse = {
  id: string;
  case_no: string;
  client_id?: string | null;
  title_cn?: string | null;
  app_no?: string | null;
  grant_no?: string | null;
  patent_no?: string | null;
  discount_rate?: string | number | null;
};

type ClientDetailResponse = {
  id: string;
  client_code?: string | null;
  name_cn: string;
  email?: string | null;
};

type V5Fixture = LiveFixture & {
  preservedCaseNo: string;
  preservedClientId: string;
  grantDocumentId: string;
  grantFeeTaskId: string;
  annuityTaskIds: number[];
};

type V6Fixture = LiveFixture & {
  preservedCaseNo: string;
  preservedClientCode: string;
  grantDocumentId: string;
  grantFeeTaskId: string;
  annuityTaskIds: number[];
};

let fixture: LiveFixture;

function ensureDefaultLiveFixtureSeed(): void {
  if (fixture) {
    return;
  }
  const output = execFileSync(backendPython, [liveSeedScript], {
    cwd: path.join(repoRoot, "backend"),
    encoding: "utf8",
    env: {
      ...process.env,
      PYTHONPATH: path.join(repoRoot, "backend"),
    },
  });
  fixture = JSON.parse(output.trim()) as LiveFixture;
}

test.beforeEach(async ({ page, request }, testInfo) => {
  if (testInfo.title.includes("@P1-v5-seed") || testInfo.title.includes("@P1-v6-enrichment")) {
    return;
  }
  ensureDefaultLiveFixtureSeed();
  const token = await login(request);
  await page.addInitScript((accessToken) => {
    window.localStorage.setItem("fpms_token", accessToken);
  }, token);
});

test("@P1-v5-seed V5 demo seed preserves old comparison data and creates new customer/case", async ({
  request,
}) => {
  const output = execFileSync(backendPython, [liveSeedScript, "--variant", "v5"], {
    cwd: path.join(repoRoot, "backend"),
    encoding: "utf8",
    env: {
      ...process.env,
      PYTHONPATH: path.join(repoRoot, "backend"),
    },
  });
  const v5Fixture = JSON.parse(output.trim()) as V5Fixture;
  expect(v5Fixture.preservedCaseNo).toBe("P1E2E-LIVE");
  expect(v5Fixture.preservedClientId).toBe("CLIENT-PD-P1-LIVE");
  expect(v5Fixture.caseNo).toBe("P1E2E-V5-LIVE");
  expect(v5Fixture.clientId).toBe("CLIENT-PD-P1-V5-LIVE");
  expect(v5Fixture.filingPackageId).toBe("FILING-PD-P1-V5-LIVE");
  expect(v5Fixture.oaPackageId).toBe("OA-PD-P1-V5-LIVE");
  expect(v5Fixture.feeDraftId).toBe("FD-PD-P1-V5-LIVE");
  expect(v5Fixture.letterDocumentId).toBe("DOC-LETTER-PD-P1-V5-LIVE");
  expect(v5Fixture.grantDocumentId).toBe("DOC-GRANT-PD-P1-V5-LIVE");
  expect(v5Fixture.grantFeeTaskId).toBe("GFT-PD-P1-V5-LIVE");
  expect(v5Fixture.annuityTaskIds).toEqual([870501, 870502]);

  const token = await login(request);
  const oldCase = await getJson<CaseListResponse>(
    request,
    token,
    "/cases?case_no=P1E2E-LIVE&page=1&page_size=1",
  );
  expect(oldCase.items).toHaveLength(1);
  expect(oldCase.items[0].case_no).toBe("P1E2E-LIVE");

  const newCase = await getJson<CaseListResponse>(
    request,
    token,
    "/cases?case_no=P1E2E-V5-LIVE&page=1&page_size=1",
  );
  expect(newCase.items).toHaveLength(1);
  expect(newCase.items[0].case_no).toBe("P1E2E-V5-LIVE");
  expect(newCase.items[0].client_id).toBe("CLIENT-PD-P1-V5-LIVE");
  expect(newCase.items[0].status).toBe("NOT_FILED");

  const newClient = await getJson<ClientListResponse>(
    request,
    token,
    "/clients?q=P1五版演示客户有限公司&page=1&page_size=10",
  );
  expect(newClient.items.some((item) => item.id === "CLIENT-PD-P1-V5-LIVE")).toBe(true);
});

test("@P1-v6-enrichment V6 enrichment requires UI-created customer/case and preserves their fields", async ({
  request,
}) => {
  runLiveSeedVariant("v6-cleanup");
  expectLiveSeedVariantFailure("v6-enrich", "UI-created V6 customer and case");

  const token = await login(request);
  const client = await postJsonWithStatus<ClientDetailResponse>(
    request,
    token,
    "/clients",
    {
      client_code: "PD-P1-V6-LIVE",
      name_cn: "P1六版演示客户有限公司",
      name_en: "P1 V6 Demo Client Ltd.",
      client_type: "企业客户",
      default_currency: "CNY",
      email: "p1-v6@example.com",
      is_active: true,
    },
    201,
  );
  await postJsonWithStatus(
    request,
    token,
    `/clients/${client.id}/contacts`,
    {
      contact_name: "赵六老师",
      title: "知识产权负责人",
      mobile: "13800060006",
      email: "zhaoliu@example.com",
      is_primary: true,
    },
    201,
  );

  const createdCase = await postJsonWithStatus<CaseDetailResponse>(
    request,
    token,
    "/cases",
    {
      case_no: "P1E2E-V6-LIVE",
      case_type: "NORMAL",
      patent_category: "INV",
      flow_dir: "CN_DOMESTIC",
      status: "NOT_FILED",
      client_id: client.id,
      title_cn: "P1六版现场创建全流程演示方法及系统",
      app_no: "CN202610000006.0",
      recv_date: "2026-07-05",
      issue_date: "2026-09-20",
      grant_date: "2026-09-20",
      grant_no: "ZL202610000006.0",
      patent_no: "ZL202610000006.0",
      valid_until: "2046-07-05",
      spec_pages: 42,
      claim_count: 12,
      has_exam_request: true,
      is_fee_monitor: true,
      fee_reduction: "PARTIAL",
      applicant_kind: "ENTITY",
      discount_rate: "0.85",
      first_annuity_year: 2,
      applicants: [
        {
          seq: 1,
          is_first: true,
          name_cn: "P1六版测试申请人有限公司",
          name_en: "P1 V6 Demo Applicant Ltd.",
          address_cn: "北京市海淀区知春路6号",
          nationality: "中国",
          certificate_type: "统一社会信用代码",
          certificate_no: "91110000P1E2EV6000X",
          official_postcode: "100080",
          official_applicant_kind: "企业",
        },
      ],
      inventors: [
        {
          seq: 1,
          name_cn: "孙六",
          name_en: "Sun Liu",
          nationality: "中国",
          china_id_no: "11010119900606006X",
        },
      ],
    },
    201,
  );
  expect(createdCase.case_no).toBe("P1E2E-V6-LIVE");

  const output = runLiveSeedVariant("v6-enrich");
  const v6Fixture = JSON.parse(output.trim()) as V6Fixture;
  expect(v6Fixture.preservedCaseNo).toBe("P1E2E-LIVE");
  expect(v6Fixture.preservedClientCode).toBe("PD-P1-V6-LIVE");
  expect(v6Fixture.caseNo).toBe("P1E2E-V6-LIVE");
  expect(v6Fixture.clientId).toBe(client.id);
  expect(v6Fixture.filingPackageId).toBe("FILING-PD-P1-V6-LIVE");
  expect(v6Fixture.oaPackageId).toBe("OA-PD-P1-V6-LIVE");
  expect(v6Fixture.feeDraftId).toBe("FD-PD-P1-V6-LIVE");
  expect(v6Fixture.letterDocumentId).toBe("DOC-LETTER-PD-P1-V6-LIVE");
  expect(v6Fixture.grantDocumentId).toBe("DOC-GRANT-PD-P1-V6-LIVE");
  expect(v6Fixture.grantFeeTaskId).toBe("GFT-PD-P1-V6-LIVE");
  expect(v6Fixture.annuityTaskIds).toEqual([870601, 870602]);

  const clientAfter = await getJson<ClientDetailResponse>(request, token, `/clients/${client.id}`);
  expect(clientAfter.name_cn).toBe("P1六版演示客户有限公司");
  expect(clientAfter.email).toBe("p1-v6@example.com");

  const caseAfter = await getJson<CaseDetailResponse>(request, token, `/cases/${createdCase.id}`);
  expect(caseAfter.title_cn).toBe("P1六版现场创建全流程演示方法及系统");
  expect(caseAfter.app_no).toBe("CN202610000006.0");
  expect(caseAfter.grant_no).toBe("ZL202610000006.0");
  expect(caseAfter.patent_no).toBe("ZL202610000006.0");
  expect(Number(caseAfter.discount_rate)).toBe(0.85);
});

test("@P1-live 全scope：案件官方字段维护入口和递交准备 gate/checklist 对齐客户流程", async ({ page }) => {
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

  await page.getByText("控制标记", { exact: true }).click();
  await expect(page.getByText("年费监视", { exact: true })).toBeVisible();
  await expect(page.getByText("客户减免比例", { exact: true })).toBeVisible();
  await expect(page.getByPlaceholder("例如：0.85")).toHaveValue("0.85");
  await expect(page.getByText("系统减免比例", { exact: true })).toBeVisible();
  await expect(page.getByPlaceholder("请输入 0 到 1 之间的小数")).toHaveValue("0.8500");

  await page.goto("/settings/applicants", { waitUntil: "domcontentloaded" });
  await expect(page.getByRole("heading", { name: "申请人主数据" })).toBeVisible();
  await page.getByPlaceholder("搜索申请人名称或编码").fill("P1测试申请人有限公司");
  await page.getByRole("button", { name: "搜索" }).click();
  await expect(page.getByText("P1测试申请人有限公司")).toBeVisible();
  await expect(page.getByText("总委备-P1-LIVE-001")).toBeVisible();

  await page.goto(`/official-workflows/filing-preparation?package_id=${fixture.filingPackageId}`, {
    waitUntil: "domcontentloaded",
  });
  await expect(page.getByRole("heading", { name: "新申请递交准备" })).toBeVisible();
  await expect(page.getByText("申请人官方邮编缺失").first()).toBeVisible();
  await expect(page.getByText("总委托书备案编号").first()).toBeVisible();
  await expect(page.getByText("申请人主数据映射待确认")).not.toBeVisible();
  await expect(page.getByRole("link", { name: "到案件页维护" }).first()).toHaveAttribute(
    "href",
    `/cases/${fixture.caseId}/edit`,
  );
  await expect(page.getByText("技术交底书").first()).toBeVisible();
  await expect(page.getByText("委托指示（如有）").first()).toBeVisible();
  await expect(page.getByText("XML zip").first()).toBeVisible();
  await expect(page.getByText("合并 PDF").first()).toBeVisible();
  await expect(page.getByText("官方页面字段清单")).toBeVisible();
  await expect(page.getByText("接收类表格导入").first()).toBeVisible();

  await page.getByRole("button", { name: "确认页面预览" }).click();
  await expect(page.getByText("官方页面预览已人工确认")).toBeVisible();
  await page.getByRole("button", { name: "记录导入时间" }).click();
  await expect(page.getByText("专利业务办理系统导入请求类表格").first()).toBeVisible();
  await expect(page.getByText("操作时间").first()).toBeVisible();
  await expect(page.getByText("说明").first()).toBeVisible();
  await expect(page.getByText("occurred_at=")).toHaveCount(0);
  await expect(page.getByText("note=")).toHaveCount(0);
  await expect(page.getByText("CNIPA_IMPORT_STARTED")).toHaveCount(0);
  expectNoUnexpectedRuntimeSignals(pageErrors);
});

test("@P1-live 全scope：OA答复包文件角色、人工动作、回执硬门禁和归档元数据", async ({ page }) => {
  const pageErrors = collectPageErrors(page);

  await page.goto(`/official-workflows/oa-reply?package_id=${fixture.oaPackageId}`, {
    waitUntil: "domcontentloaded",
  });
  await expect(page.getByRole("heading", { name: "OA答复工作包" })).toBeVisible();
  await expect(page.getByText("CN202610000001.0")).toBeVisible();
  await expect(page.getByText("第一次审查意见通知书").first()).toBeVisible();
  await expect(page.getByText("2026-08-20")).toBeVisible();
  await expect(page.getByText("已关联答复文书")).toBeVisible();
  await expectNoVisibleInternalCodes(page, ["REPLY_DOCUMENT_LINKED"]);
  await expect(page.getByText("详见随附 PDF 意见陈述书。")).toBeVisible();

  await expect(page.getByText("意见陈述 Word").first()).toBeVisible();
  await expect(page.getByText("PDF保真附件").first()).toBeVisible();
  await expect(page.getByText("修改后的权利要求书").first()).toBeVisible();
  await expect(page.getByText("修改对照页").first()).toBeVisible();
  await expect(page.getByText("其他证明文件").first()).toBeVisible();
  await expect(page.getByText("补交实验数据：是").first()).toBeVisible();
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
  await archiveForm
    .getByPlaceholder("逐行记录官方回执中的收到文件清单")
    .fill("意见陈述书\n权利要求书\n修改对照页\n其他证明文件");
  await archiveForm.getByPlaceholder("可填写归档说明").fill("P1 E2E 人工下载并上传电子申请回执");
  await page.getByRole("button", { name: "记录回执元数据" }).click();
  await expect(page.getByText("回执元数据已记录")).toBeVisible();
  await expect(page.getByText("202606020001").first()).toBeVisible();
  await expect(page.getByText("流程人员A").first()).toBeVisible();
  await expect(page.getByText("意见陈述书").first()).toBeVisible();
  await expectNoVisibleInternalCodes(page, ["READY", "UNCONFIRMED"]);

  await page.getByRole("button", { name: "确认回执归档" }).click();
  await expect(page.getByText("电子申请回执已归档核对").first()).toBeVisible();
  await page.getByRole("button", { name: "提交归档检查" }).click();
  await expect(page.getByText("归档检查已通过")).toBeVisible();
  await expect(page.getByText("回执依据已满足").first()).toBeVisible();
  await expect(page.getByText("归档证据已满足").first()).toBeVisible();
  await expect(page.getByText("缺少必填回执元数据")).not.toBeVisible();
  expectNoUnexpectedRuntimeSignals(pageErrors);
});

test("@P1-live 全scope：费用联动、pay-list边界、信函交接和非范围声明", async ({ page, request }) => {
  const pageErrors = collectPageErrors(page);
  const token = await login(request);

  const preview = await postJson<OfficialFeePreviewResponse>(
    request,
    token,
    "/fees/official-fee-preview",
    {
      case_id: fixture.caseId,
      trigger_event: "FILING_ACCEPTED",
      currency: "CNY",
    },
  );
  expect(preview.case_id).toBe(fixture.caseId);
  expect(preview.trigger_event).toBe("FILING_ACCEPTED");
  expect(preview.preview_only).toBe(true);
  expect(preview.idempotency_key).toBe(`${fixture.caseId}:FILING_ACCEPTED:NO_SOURCE`);
  expect(Number(preview.total_gov)).toBe(560);
  expect(new Set(preview.candidates.map((item) => item.fee_type))).toEqual(new Set(["GOV"]));
  expect(new Set(preview.candidates.map((item) => item.fee_code))).toEqual(
    new Set([
      "CN_INV_APPLICATION_FEE",
      "CN_PUBLICATION_PRINT_FEE",
      "CN_SUBSTANTIVE_EXAM_FEE",
    ]),
  );

  const draft = await getJson<FeeDraftDetailResponse>(request, token, `/fees/drafts/${fixture.feeDraftId}`);
  expect(draft.draft_type).toBe("APPLY_FEE");
  expect(Number(draft.total_gov)).toBe(560);
  expect(Number(draft.total_service)).toBe(0);
  expect(Number(draft.total_misc)).toBe(0);
  expect(Number(draft.amount)).toBe(560);

  const draftItems = await getJson<FeeItemResponse[]>(
    request,
    token,
    `/fees/drafts/${fixture.feeDraftId}/items`,
  );
  expect(draftItems).toHaveLength(3);
  expect(new Set(draftItems.map((item) => item.fee_type))).toEqual(new Set(["GOV"]));

  await page.goto(`/fees/drafts/${fixture.feeDraftId}?package_id=${fixture.filingPackageId}`, {
    waitUntil: "domcontentloaded",
  });
  await expect(page.getByRole("heading", { name: "费用联动核对" })).toBeVisible();
  await expect(page.getByText("官方费率 / 费减清单来源待确认").first()).toBeVisible();
  await expect(page.getByText("客户减免比例").first()).toBeVisible();
  await expect(page.getByText("0.85").first()).toBeVisible();
  await expect(page.getByText("系统应缴比例").first()).toBeVisible();
  await expect(page.getByText("0.15").first()).toBeVisible();
  await expect(page.getByText("费减转换").first()).toBeVisible();
  await expect(page.getByText("客户旧系统值表示减免比例 0.85，官方计费应缴比例为 0.15。").first()).toBeVisible();
  await expect(page.getByText("旧系统 0 / 0.7 / 0.85 语义待客户确认")).not.toBeVisible();
  await expect(page.getByText("补充缴费信息模板字段待确认").first()).toBeVisible();
  await expect(page.getByText("内部 pay-list 不是官方上传 Excel").first()).toBeVisible();

  await page.goto(`/cases/no/${fixture.caseNo}`, { waitUntil: "domcontentloaded" });
  await page.getByRole("tab", { name: "费用" }).click();
  await expect(page.getByRole("heading", { name: "官费节点线" })).toBeVisible();
  await expect(page.getByText("申请/受理官费候选")).toBeVisible();
  await expect(page.getByText("候选待确认").or(page.getByText("已有费用草稿"))).toBeVisible();
  await expect(page.getByText("候选官费合计")).toBeVisible();
  await expect(page.getByText("¥560.00")).toBeVisible();
  await expect(page.getByText("费用草稿状态")).toBeVisible();
  await expect(page.getByText("已有 1 个费用草稿").first()).toBeVisible();
  await expect(page.getByText("去重键")).toBeVisible();
  await expect(page.getByText(`${fixture.caseId}:FILING_ACCEPTED:NO_SOURCE`)).toBeVisible();
  await expect(page.getByText("发明申请费").first()).toBeVisible();
  await expect(page.getByText("发明公布印刷费").first()).toBeVisible();
  await expect(page.getByText("发明实质审查费").first()).toBeVisible();

  await page.goto(`/fee-management/pay-lists/${fixture.payListId}?package_id=${fixture.filingPackageId}`, {
    waitUntil: "domcontentloaded",
  });
  await expect(page.getByRole("heading", { name: "官费清单详情" })).toBeVisible();
  await expect(page.getByText("补充缴费信息模板").first()).toBeVisible();
  await expect(page.getByText("500").first()).toBeVisible();
  await expect(page.getByText("人工官方缴费").or(page.getByText("仅内部计划")).first()).toBeVisible();
  await expectNoVisibleInternalCodes(page, ["MANUAL_ONLY", "UNCONFIRMED", "READY"]);

  await page.goto(`/documents/${fixture.letterDocumentId}`, { waitUntil: "domcontentloaded" });
  await expect(page.getByText("格式函与龙虾交接")).toBeVisible();
  await expect(page.getByText("FORMAT_LETTER_OA1")).toBeVisible();
  await expect(page.getByText("张三老师：您好").first()).toBeVisible();
  await expect(page.getByText(`${fixture.caseNo} 第一次审查意见通知书`)).toBeVisible();
  await expect(page.getByText(`${fixture.caseNo}-一通格式函.docx`).first()).toBeVisible();
  await expect(page.getByText("第一次审查意见通知书.pdf").first()).toBeVisible();
  await page.getByRole("button", { name: "生成交接记录" }).click();
  await expect(page.getByText("交接记录已生成")).toBeVisible();
  await expect(page.getByText("已准备").first()).toBeVisible();
  await expectNoVisibleInternalCodes(page, [
    "READY",
    "MANUAL_ONLY",
    "UNCONFIRMED",
    "SOURCE_OFFICIAL_DOCUMENT",
  ]);

  assertNoForbiddenP1AutomationClaims();
  expectNoUnexpectedRuntimeSignals(pageErrors);
});

test("@P1-live-demo 授权费和年费节点可以按案件号稳定展示", async ({ page }) => {
  const pageErrors = collectPageErrors(page);

  await page.goto("/grant-fee/tasks", { waitUntil: "domcontentloaded" });
  await expect(page.getByRole("heading", { name: "授权费任务看板" })).toBeVisible();
  await page.getByPlaceholder("请输入案件编号").fill(fixture.caseNo);
  await page.getByRole("button", { name: "查询" }).click();
  await expect(page.getByRole("cell", { name: new RegExp(fixture.caseNo) })).toBeVisible();
  await expect(page.getByText("以办理登记手续通知书/授权通知书载明期限为准").first()).toBeVisible();
  await expect(page.getByText("授权阶段官费按授权费任务金额展示").first()).toBeVisible();

  await page.goto("/annuity/tasks", { waitUntil: "domcontentloaded" });
  await expect(page.getByRole("heading", { name: "年费任务列表" })).toBeVisible();
  await page.getByPlaceholder("请输入案件编号").fill(fixture.caseNo);
  await page.getByRole("button", { name: "查询" }).click();
  await expect(page.getByRole("cell", { name: new RegExp(fixture.caseNo) })).toHaveCount(2);
  await expect(page.getByText("以年费任务到期日为准").first()).toBeVisible();
  await expect(page.getByText("第2年度年费，按专利类型和年度阶梯费率预估").first()).toBeVisible();
  expectNoUnexpectedRuntimeSignals(pageErrors);
});

async function login(request: APIRequestContext): Promise<string> {
  const response = await request.post(`${apiBaseUrl}/auth/login`, {
    data: {
      username: process.env.FPMS_E2E_USERNAME || "admin",
      password: process.env.FPMS_E2E_PASSWORD || "admin123",
    },
  });
  const body = await response.text();
  expect(response.status(), body).toBe(200);
  return (JSON.parse(body) as { access_token: string }).access_token;
}

async function getJson<T>(
  request: APIRequestContext,
  token: string,
  pathName: string,
): Promise<T> {
  const response = await request.get(`${apiBaseUrl}${pathName}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  const body = await response.text();
  expect(response.status(), body).toBe(200);
  return JSON.parse(body) as T;
}

async function postJson<T>(
  request: APIRequestContext,
  token: string,
  pathName: string,
  data: unknown,
): Promise<T> {
  const response = await request.post(`${apiBaseUrl}${pathName}`, {
    headers: { Authorization: `Bearer ${token}` },
    data,
  });
  const body = await response.text();
  expect(response.status(), body).toBe(200);
  return JSON.parse(body) as T;
}

async function postJsonWithStatus<T = unknown>(
  request: APIRequestContext,
  token: string,
  pathName: string,
  data: unknown,
  status: number,
): Promise<T> {
  const response = await request.post(`${apiBaseUrl}${pathName}`, {
    headers: { Authorization: `Bearer ${token}` },
    data,
  });
  const body = await response.text();
  expect(response.status(), body).toBe(status);
  return JSON.parse(body) as T;
}

function runLiveSeedVariant(variant: string): string {
  return execFileSync(backendPython, [liveSeedScript, "--variant", variant], {
    cwd: path.join(repoRoot, "backend"),
    encoding: "utf8",
    env: {
      ...process.env,
      PYTHONPATH: path.join(repoRoot, "backend"),
    },
  });
}

function expectLiveSeedVariantFailure(variant: string, message: string): void {
  try {
    runLiveSeedVariant(variant);
  } catch (error) {
    const failure = error as { stdout?: Buffer | string; stderr?: Buffer | string };
    const output = `${failure.stdout?.toString() || ""}${failure.stderr?.toString() || ""}`;
    expect(output).toContain(message);
    return;
  }
  throw new Error(`Expected live seed variant ${variant} to fail with ${message}`);
}

function collectPageErrors(page: Page): string[] {
  const pageErrors: string[] = [];
  page.on("pageerror", (error) => pageErrors.push(error.message));
  return pageErrors;
}

function expectNoUnexpectedRuntimeSignals(pageErrors: string[]): void {
  expect(pageErrors).toEqual([]);
}

async function expectNoVisibleInternalCodes(page: Page, codes: string[]): Promise<void> {
  for (const code of codes) {
    await expect(page.getByText(code, { exact: true })).toHaveCount(0);
  }
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

function mergeNoProxy(current: string | undefined): string {
  const entries = new Set(
    (current || "")
      .split(",")
      .map((entry) => entry.trim())
      .filter(Boolean),
  );
  entries.add("127.0.0.1");
  entries.add("localhost");
  return Array.from(entries).join(",");
}

function normalizeApiBaseUrl(raw: string): string {
  const normalized = raw.replace("http://localhost:", "http://127.0.0.1:").replace(/\/$/, "");
  return normalized.endsWith("/api") ? `${normalized}/v1` : normalized;
}
