import { expect, test } from "@playwright/test";
import type { APIRequestContext, APIResponse } from "@playwright/test";

const apiBase = (process.env.FPMS_API_URL || "http://127.0.0.1:8016/api/v1").replace(/\/$/, "");

type Json = Record<string, any>;

test("@addgap-real-path seven GAP outcomes work without enrichment", async ({ page, request }) => {
  test.setTimeout(180_000);
  const suffix = `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 8)}`.toUpperCase();
  const token = await login(request);
  const templates = await templateMap(request, token);
  const oa1Template = requiredTemplate(templates, "OFFICIAL_NOTICE_003");
  const oa2Template = requiredTemplate(templates, "OFFICIAL_NOTICE_005");
  const grantTemplate = requiredTemplate(templates, "OFFICIAL_NOTICE_009");
  const oaOutTemplate = requiredTemplate(templates, "OA_OUT");
  const plainTemplate = requiredTemplate(templates, "CLIENT_IN");

  await page.addInitScript((accessToken) => {
    window.localStorage.setItem("fpms_token", accessToken);
  }, token);

  const filingCase = await createCase(request, token, `ADDGAP-FILING-${suffix}`, "最终真实路径申请前准备");
  const oaCase = await createCase(request, token, `ADDGAP-OA-${suffix}`, "最终真实路径OA生命周期");
  const otherCase = await createCase(request, token, `ADDGAP-OTHER-${suffix}`, "最终真实路径跨案回执");
  const deadlineCase = await createCase(request, token, `ADDGAP-DUE-${suffix}`, "最终真实路径期限载体");
  const wizardCase = await createCase(request, token, `ADDGAP-WIZ-${suffix}`, "最终真实路径批量向导");
  const grantCase = await createCase(request, token, `ADDGAP-GRANT-${suffix}`, "最终真实路径授权替换");

  await test.step("1 wizard and catalog use the real bounded template listing", async () => {
    let wizardTemplateUrl = "";
    page.on("request", (observed) => {
      const url = new URL(observed.url());
      if (url.pathname.endsWith("/api/v1/doc-templates") && page.url().includes("/documents/wizard")) {
        wizardTemplateUrl = observed.url();
      }
    });
    await page.goto("/documents/wizard", { waitUntil: "domcontentloaded" });
    await expect(page.getByRole("heading", { name: "中间文件向导" })).toBeVisible();
    await expect.poll(() => wizardTemplateUrl).not.toBe("");
    const wizardQuery = new URL(wizardTemplateUrl).searchParams;
    expect(Number(wizardQuery.get("page_size"))).toBeLessThanOrEqual(100);
    expect(wizardQuery.get("enabled")).toBe("true");

    await page.goto(`/documents/new?case_id=${filingCase.id}&case_no=${filingCase.case_no}`, {
      waitUntil: "domcontentloaded",
    });
    await expect(page.getByRole("heading", { name: "登记往来文件" })).toBeVisible();
    const templateField = page.locator(".el-form-item").filter({ hasText: "文件模板" }).first();
    await templateField.getByRole("combobox").click();
    await expect(page.getByRole("option").filter({ hasText: "OFFICIAL_NOTICE_" })).toHaveCount(60);
    await expect(page.getByRole("option", { name: /OFFICIAL_NOTICE_001.*受理通知-电子.*可执行/ })).toBeEnabled();
    await expect(page.getByRole("option", { name: /OFFICIAL_NOTICE_003.*第一次审查意见通知书.*可执行/ })).toBeEnabled();
    await expect(page.getByRole("option", { name: /OFFICIAL_NOTICE_009.*授权通知书-电子.*可执行/ })).toBeEnabled();
    await expect(page.getByRole("option", { name: /OFFICIAL_NOTICE_010.*专利证书.*仅供参考/ })).toBeDisabled();
    await page.keyboard.press("Escape");
  });

  let filingPackage: Json;
  let oaDocument: Json;
  let oaPackage: Json;
  let oaTask: Json;
  let replyDocument: Json;

  await test.step("2 filing and OA work packages are reachable without enrichment", async () => {
    filingPackage = await okJson(request, token, "POST", `/cases/${filingCase.id}/official-work-packages/filing-preparation/resolve`, undefined, 200);
    const filingAgain = await okJson(request, token, "POST", `/cases/${filingCase.id}/official-work-packages/filing-preparation/resolve`, undefined, 200);
    expect(filingAgain.package.id).toBe(filingPackage.package.id);
    expect(filingPackage.package.package_kind).toBe("FILING_PREP");

    await page.goto(`/official-workflows/filing-preparation?package_id=${filingPackage.package.id}`, {
      waitUntil: "domcontentloaded",
    });
    await expect(page.getByRole("heading", { name: "新申请递交准备" })).toBeVisible();

    oaDocument = await createDocument(request, token, {
      case_id: oaCase.id,
      doc_template_id: oa1Template.id,
      direction: "IN",
      doc_date: "2026-07-11",
      title: `第一次审查意见通知书-${suffix}`,
      ref_no: `OA1-${suffix}`,
      official_due_date: "2026-10-15",
      official_due_date_source: "MANUAL_OFFICIAL_NOTICE",
      official_due_date_status: "CONFIRMED",
    });
    oaPackage = await okJson(request, token, "POST", `/official-documents/${oaDocument.id}/official-work-packages/oa-reply/resolve`, undefined, 200);
    const oaAgain = await okJson(request, token, "POST", `/official-documents/${oaDocument.id}/official-work-packages/oa-reply/resolve`, undefined, 200);
    expect(oaAgain.package.id).toBe(oaPackage.package.id);
    expect(oaPackage.package.source_document_id).toBe(oaDocument.id);
    expect(oaPackage.official_due_date).toBe("2026-10-15");

    await page.goto(`/official-workflows/oa-reply?document_id=${oaDocument.id}`, {
      waitUntil: "domcontentloaded",
    });
    await expect(page.getByRole("heading", { name: "OA答复工作包" })).toBeVisible();
    await expect(page.getByText(`第一次审查意见通知书-${suffix}`).first()).toBeVisible();
  });

  await test.step("3 OA reply stays open until valid receipt archive and subsequent OA is distinct", async () => {
    const tasks = await caseTasks(request, token, oaCase.id);
    oaTask = requiredItem(tasks.find((item) => item.document_id === oaDocument.id), "first OA task");
    expect(oaTask.status).toBe("OPEN");

    replyDocument = await createDocument(request, token, {
      case_id: oaCase.id,
      doc_template_id: oaOutTemplate.id,
      direction: "OUT",
      doc_date: "2026-08-20",
      title: `第一次审查意见答复-${suffix}`,
      ref_no: `OA-REPLY-${suffix}`,
      reply_to_id: oaDocument.id,
    });
    await okJson(request, token, "POST", `/official-work-packages/${oaPackage.package.id}/oa-reply/reply-document`, { reply_document_id: replyDocument.id }, 200);
    const stillOpen = await okJson(request, token, "GET", `/tasks/${oaTask.id}`, undefined, 200);
    expect(stillOpen.status).toBe("OPEN");
    expect(stillOpen.done_at).toBeNull();
    expect((await okJson(request, token, "GET", `/cases/${oaCase.id}`, undefined, 200)).status).toBe("OA1");

    for (const role of ["OA_STATEMENT_WORD", "OA_STATEMENT_PDF", "OA_MODIFIED_CLAIMS", "OA_AMENDMENT_COMPARISON", "OA_OTHER_PROOF"]) {
      const extension = ["OA_STATEMENT_WORD", "OA_MODIFIED_CLAIMS"].includes(role) ? "docx" : "pdf";
      await uploadAttachment(request, token, replyDocument.id, `${role}-${suffix}.${extension}`, role);
    }
    const receiptAttachment = await uploadAttachment(request, token, replyDocument.id, `电子申请回执-${suffix}.pdf`, "ELECTRONIC_RECEIPT");
    oaPackage = await okJson(request, token, "POST", `/official-work-packages/${oaPackage.package.id}/oa-reply/refresh`, { experiment_data_submitted: false }, 200);
    for (const item of oaPackage.official_page_checklist as Json[]) {
      await okJson(request, token, "PATCH", `/official-work-packages/${oaPackage.package.id}/oa-reply/checklist/${item.item_code}`, { status: "DONE", evidence_note: "最终真实路径人工确认" }, 200);
    }
    await okJson(request, token, "POST", `/official-work-packages/${oaPackage.package.id}/receipts`, receiptPayload(receiptAttachment.id, suffix), 201);
    const archived = await okJson(request, token, "POST", `/official-work-packages/${oaPackage.package.id}/archive`, {}, 200);
    expect(archived.package.status).toBe("ARCHIVED");
    expect(archived.evaluation.receipt_hard_gate_satisfied).toBe(true);
    expect((await okJson(request, token, "GET", `/tasks/${oaTask.id}`, undefined, 200)).status).toBe("DONE");
    expect((await okJson(request, token, "GET", `/cases/${oaCase.id}`, undefined, 200)).status).toBe("SUB_EXAM");

    const subsequent = await createDocument(request, token, {
      case_id: oaCase.id,
      doc_template_id: oa2Template.id,
      direction: "IN",
      doc_date: "2026-09-01",
      title: `第二次审查意见通知书-${suffix}`,
      ref_no: `OA2-${suffix}`,
      official_due_date: "2026-12-01",
      official_due_date_source: "IMPORTED_OFFICIAL_NOTICE",
      official_due_date_status: "CONFIRMED",
    });
    const subsequentTask = requiredItem(
      (await caseTasks(request, token, oaCase.id)).find((item) => item.document_id === subsequent.id),
      "subsequent OA task",
    );
    expect(subsequentTask.id).not.toBe(oaTask.id);
    expect(subsequentTask.status).toBe("OPEN");
  });

  await test.step("4 receipt ownership and source gates fail without mutation", async () => {
    const gateCase = await createCase(request, token, `ADDGAP-GATE-${suffix}`, "最终真实路径回执门禁");
    const gateSource = await createDocument(request, token, {
      case_id: gateCase.id,
      doc_template_id: oa1Template.id,
      direction: "IN",
      doc_date: "2026-07-12",
      title: `门禁审查意见通知书-${suffix}`,
      official_due_date: "2026-10-20",
      official_due_date_source: "MANUAL_OFFICIAL_NOTICE",
      official_due_date_status: "CONFIRMED",
    });
    const gatePackage = await okJson(request, token, "POST", `/official-documents/${gateSource.id}/official-work-packages/oa-reply/resolve`, undefined, 200);
    const gateTask = requiredItem(
      (await caseTasks(request, token, gateCase.id)).find((item) => item.document_id === gateSource.id),
      "receipt-gate OA task",
    );
    expect(gateTask.status).toBe("OPEN");

    const foreignDocument = await createDocument(request, token, {
      case_id: otherCase.id,
      direction: "OUT",
      doc_date: "2026-07-12",
      title: `跨案回执载体-${suffix}`,
    });
    const foreignAttachment = await uploadAttachment(request, token, foreignDocument.id, `跨案回执-${suffix}.pdf`, "ELECTRONIC_RECEIPT");
    const wrongCase = await rawJson(request, token, "POST", `/official-work-packages/${gatePackage.package.id}/receipts`, receiptPayload(foreignAttachment.id, suffix));
    expect(wrongCase.response.status()).toBe(400);
    expect(wrongCase.body.error.code).toBe("OFFICIAL_WORK_PACKAGE_RECEIPT_CASE_MISMATCH");

    const unrelated = await createDocument(request, token, {
      case_id: gateCase.id,
      direction: "OUT",
      doc_date: "2026-07-12",
      title: `同案非来源文书-${suffix}`,
    });
    const unrelatedAttachment = await uploadAttachment(request, token, unrelated.id, `同案错误来源-${suffix}.pdf`, "ELECTRONIC_RECEIPT");
    const wrongSource = await rawJson(request, token, "POST", `/official-work-packages/${gatePackage.package.id}/receipts`, receiptPayload(unrelatedAttachment.id, suffix));
    expect(wrongSource.response.status()).toBe(400);
    expect(wrongSource.body.error.code).toBe("OA_RECEIPT_ATTACHMENT_SOURCE_INVALID");
    expect((await okJson(request, token, "GET", `/tasks/${gateTask.id}`, undefined, 200)).status).toBe("OPEN");
    expect((await okJson(request, token, "GET", `/official-work-packages/${gatePackage.package.id}/oa-reply`, undefined, 200)).package.status).not.toBe("ARCHIVED");
  });

  await test.step("5 structured deadline survives create read update wizard and preview", async () => {
    const duePayload = {
      case_id: deadlineCase.id,
      doc_template_id: oa1Template.id,
      direction: "IN",
      doc_date: "2026-07-13",
      title: `期限载体审查意见通知书-${suffix}`,
      official_due_date: "2026-11-15",
      official_due_date_source: "MANUAL_OFFICIAL_NOTICE",
      official_due_date_status: "CONFIRMED",
    };
    const preview = await okJson(request, token, "POST", "/documents/impact-preview", duePayload, 200);
    expect(preview.official_due_date).toBe("2026-11-15");
    expect(preview.official_due_date_source).toBe("MANUAL_OFFICIAL_NOTICE");
    expect(preview.official_due_date_status).toBe("CONFIRMED");
    expect(preview.deadline_impacts.length).toBeGreaterThan(0);

    const created = await createDocument(request, token, duePayload);
    const read = await okJson(request, token, "GET", `/documents/${created.id}`, undefined, 200);
    expect(read.official_due_date).toBe("2026-11-15");
    expect(read.official_due_date_status).toBe("CONFIRMED");
    const updated = await okJson(request, token, "PUT", `/documents/${created.id}`, {
      title: `期限载体已复核-${suffix}`,
      official_due_date: "2026-11-15",
      official_due_date_source: "MANUAL_OFFICIAL_NOTICE",
      official_due_date_status: "CONFIRMED",
      description: "最终真实路径复核",
    }, 200);
    expect(updated.official_due_date_source).toBe("MANUAL_OFFICIAL_NOTICE");

    const wizard = await okJson(request, token, "POST", "/documents/wizard/batch-create", {
      defaults: {
        doc_template_id: plainTemplate.id,
        direction: "IN",
        doc_date: "2026-07-13",
        title: `批量向导期限载体-${suffix}`,
        official_due_date: "2026-12-15",
        official_due_date_source: "IMPORTED_OFFICIAL_NOTICE",
        official_due_date_status: "CONFIRMED",
      },
      rows: [{ case_id: wizardCase.id }],
      task_rows: [],
      fee_rows: [],
      attachment_rows: [],
    }, 201);
    expect(wizard.created).toBe(1);
    expect(wizard.items[0].document.official_due_date).toBe("2026-12-15");

    const malformed = await rawJson(request, token, "POST", "/documents/impact-preview", { ...duePayload, doc_date: "not-a-date" });
    expect(malformed.response.status()).toBe(422);
    expect(malformed.body.error.code).toBe("VALIDATION_ERROR");
    const incomplete = await rawJson(request, token, "POST", "/documents/impact-preview", {
      ...duePayload,
      official_due_date_source: null,
    });
    expect(incomplete.response.status()).toBe(400);

    await page.goto(`/documents/${created.id}/edit`, { waitUntil: "domcontentloaded" });
    await expect(page.getByRole("heading", { name: "编辑文档" })).toBeVisible();
    await expect(page.getByText("官方截止日").first()).toBeVisible();
    await expect(page.getByText("已确认", { exact: true }).first()).toBeVisible();
  });

  await test.step("6 grant replacement creates explicit sourced lineage and UI separates states", async () => {
    const grantCreate = await rawJson(request, token, "POST", "/documents", {
      case_id: grantCase.id,
      doc_template_id: grantTemplate.id,
      direction: "IN",
      doc_date: "2026-07-14",
      title: `授权通知书-${suffix}`,
      ref_no: `GRANT-${suffix}`,
      official_due_date: "2026-09-30",
      official_due_date_source: "MANUAL_OFFICIAL_NOTICE",
      official_due_date_status: "CONFIRMED",
    });
    expect(grantCreate.response.status()).toBe(201);
    expect(grantCreate.response.headers()["x-auto-fee-draft-created"]).toBeUndefined();
    const original = (await grantTasks(request, token, grantCase.id))[0];
    expect(original.lineage_status).toBe("CONFIRMED");
    expect(original.source_document_id).toBe(grantCreate.body.id);
    expect(original.draft_generated).toBe(false);

    const replacement = await okJson(request, token, "POST", `/grant-fee-tasks/${original.task_id}/replacement-notice`, {
      idempotency_key: `REPLACE-${suffix}`.slice(0, 64),
      reason: "官方重新发文并更正缴费期限",
      document: {
        doc_template_id: grantTemplate.id,
        doc_date: "2026-07-15",
        title: `更正授权通知书-${suffix}`,
        ref_no: `GRANT-REPLACED-${suffix}`,
        official_due_date: "2026-10-31",
        official_due_date_source: "MANUAL_OFFICIAL_NOTICE",
        official_due_date_status: "CONFIRMED",
        description: "最终真实路径更正",
      },
    }, 200);
    expect(replacement.superseded_task_id).toBe(original.task_id);
    expect(replacement.replacement_task.lineage_status).toBe("CONFIRMED");
    expect(replacement.replacement_task.source_document_id).toBe(replacement.document.id);

    await page.goto("/grant-fee/tasks", { waitUntil: "domcontentloaded" });
    await expect(page.getByRole("heading", { name: "授权费任务看板" })).toBeVisible();
    await page.getByPlaceholder("请输入案件编号").fill(grantCase.case_no);
    await page.getByRole("button", { name: "查询" }).click();
    const grantRows = page.getByRole("row").filter({ hasText: grantCase.case_no });
    await expect(grantRows).toHaveCount(2);
    await expect(grantRows.filter({ hasText: "已被替代" })).toContainText("待处理");
    await expect(grantRows.filter({ hasText: "来源已确认" })).toContainText("待处理");
  });

  await test.step("7 superseded mutations fail closed while replacement follows normal PAY draft path", async () => {
    const rows = await grantTasks(request, token, grantCase.id);
    const oldTask = requiredItem(
      rows.find((item) => item.lineage_status === "SUPERSEDED"),
      "superseded grant task",
    );
    const newTask = requiredItem(
      rows.find((item) => item.lineage_status === "CONFIRMED"),
      "replacement grant task",
    );
    const before = await okJson(request, token, "GET", `/grant-fee-tasks/${oldTask.task_id}/state`, undefined, 200);

    for (const [path, data] of [
      [`/grant-fee-tasks/${oldTask.task_id}/generate-draft`, undefined],
      ["/grant-fee-tasks/batch-instruction", { task_ids: [oldTask.task_id], action: "record_pay_instruction" }],
      ["/grant-fee-tasks/generate-notices", { task_ids: [oldTask.task_id] }],
    ] as Array<[string, Json | undefined]>) {
      const blocked = await rawJson(request, token, "POST", path, data);
      expect(blocked.response.status()).toBe(409);
      expect(blocked.body.error.code).toBe("GRANT_FEE_TASK_LINEAGE_NOT_ACTIONABLE");
      expect(blocked.body.error.details.task_id).toBe(oldTask.task_id);
      expect(blocked.body.error.details.lineage_status).toBe("SUPERSEDED");
    }
    const after = await okJson(request, token, "GET", `/grant-fee-tasks/${oldTask.task_id}/state`, undefined, 200);
    expect(after.client_instruction).toBe(before.client_instruction);
    expect(after.notify_count).toBe(before.notify_count);
    expect(after.draft_generated).toBe(before.draft_generated);

    await okJson(request, token, "PUT", `/grant-fee-tasks/${newTask.task_id}/state`, { action: "mark_waiting_client" }, 200);
    const instructed = await okJson(request, token, "POST", "/grant-fee-tasks/batch-instruction", {
      task_ids: [newTask.task_id],
      action: "record_pay_instruction",
    }, 200);
    expect(instructed.updated_task_ids).toEqual([newTask.task_id]);
    const draft = await okJson(request, token, "POST", `/grant-fee-tasks/${newTask.task_id}/generate-draft`, undefined, 200);
    expect(draft.task_id).toBe(newTask.task_id);
    expect(draft.state).toBe("DRAFT_GENERATED");
    expect(draft.draft_generated).toBe(true);
  });
});

async function login(request: APIRequestContext): Promise<string> {
  const username = process.env.FPMS_ADMIN_USERNAME;
  const password = process.env.FPMS_ADMIN_PASSWORD;
  expect(username, "FPMS_ADMIN_USERNAME is required").toBeTruthy();
  expect(password, "FPMS_ADMIN_PASSWORD is required").toBeTruthy();
  const response = await request.post(`${apiBase}/auth/login`, {
    data: {
      username,
      password,
    },
  });
  expect(response.status(), await response.text()).toBe(200);
  return (await response.json()).access_token as string;
}

async function rawJson(
  request: APIRequestContext,
  token: string,
  method: string,
  path: string,
  data?: unknown,
): Promise<{ response: APIResponse; body: Json }> {
  const response = await request.fetch(`${apiBase}${path}`, {
    method,
    headers: { Authorization: `Bearer ${token}` },
    ...(data === undefined ? {} : { data }),
  });
  return { response, body: (await response.json()) as Json };
}

async function okJson(
  request: APIRequestContext,
  token: string,
  method: string,
  path: string,
  data: unknown,
  status: number,
): Promise<Json> {
  const result = await rawJson(request, token, method, path, data);
  expect(result.response.status(), JSON.stringify(result.body)).toBe(status);
  return result.body;
}

async function createCase(request: APIRequestContext, token: string, caseNo: string, title: string): Promise<Json> {
  return okJson(request, token, "POST", "/cases", {
    case_no: caseNo,
    case_type: "NORMAL",
    patent_category: "INV",
    flow_dir: "CN_DOMESTIC",
    status: "NOT_FILED",
    title_cn: title,
  }, 201);
}

async function createDocument(request: APIRequestContext, token: string, payload: Json): Promise<Json> {
  return okJson(request, token, "POST", "/documents", payload, 201);
}

async function templateMap(request: APIRequestContext, token: string): Promise<Map<string, Json>> {
  const response = await okJson(request, token, "GET", "/doc-templates?page=1&page_size=100&enabled=true", undefined, 200);
  return new Map((response.items as Json[]).map((item) => [item.code as string, item]));
}

function requiredTemplate(templates: Map<string, Json>, code: string): Json {
  const template = templates.get(code);
  expect(template, `missing standard bootstrap template ${code}`).toBeTruthy();
  return template!;
}

function requiredItem<T>(item: T | undefined, label: string): T {
  expect(item, `missing ${label}`).toBeTruthy();
  if (item === undefined) throw new Error(`missing ${label}`);
  return item;
}

async function caseTasks(request: APIRequestContext, token: string, caseId: string): Promise<Json[]> {
  const result = await okJson(request, token, "GET", `/tasks?case_id=${caseId}&page=1&page_size=100`, undefined, 200);
  return result.items as Json[];
}

async function grantTasks(request: APIRequestContext, token: string, caseId: string): Promise<Json[]> {
  const result = await okJson(request, token, "GET", `/grant-fee-tasks/list?case_id=${caseId}&page=1&page_size=100`, undefined, 200);
  return result.items as Json[];
}

async function uploadAttachment(
  request: APIRequestContext,
  token: string,
  documentId: string,
  fileName: string,
  role: string,
): Promise<Json> {
  const response = await request.post(`${apiBase}/documents/${documentId}/attachments`, {
    headers: { Authorization: `Bearer ${token}` },
    multipart: {
      file: {
        name: fileName,
        mimeType: fileName.endsWith(".docx")
          ? "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
          : "application/pdf",
        buffer: Buffer.from("final-real-path"),
      },
      official_file_role: role,
      source_role_alias: role,
    },
  });
  const body = (await response.json()) as Json;
  expect(response.status(), JSON.stringify(body)).toBe(201);
  return body;
}

function receiptPayload(attachmentId: string, suffix: string): Json {
  return {
    receipt_kind: "ELECTRONIC_APPLICATION_RECEIPT",
    receipt_attachment_id: attachmentId,
    receiving_case_no: `RCV-${suffix}`,
    submitter: "最终真实路径测试员",
    received_at: "2026-09-01T10:30:00",
    received_file_list: "意见陈述书\n权利要求书\n电子申请回执",
    archive_status: "ARCHIVED",
    note: "真实API上传并记录的官方回执",
  };
}
