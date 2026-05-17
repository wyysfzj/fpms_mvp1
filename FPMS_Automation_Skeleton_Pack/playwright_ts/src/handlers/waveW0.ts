import type { ExecutionContext, TestCase } from "../support/types";
import { markSkeleton } from "../support/helpers";
import { expect, test, type APIRequestContext, type Page } from "@playwright/test";

/**
 * TC-W0-001 | 主数据-客户
 * 覆盖: FR-CM-03, FR-WD-09, FR-WD-10
 * 数据: DS-CL-001, DS-U-ADM
 * 动态值: <none>
 *
 * 前置:
 * 使用 DS-U-ADM 登录；准备 DS-CL-001 基本信息、两条地址、一条联系人。
 *
 * 步骤摘要:
 * 进入“设置→客户维护”，创建客户、默认文件地址、默认账单地址和联系人；保存后再打开编辑页校验。
 *
 * 预期:
 * 客户、地址、联系人均保存成功；默认地址标记唯一；搜索可按名称命中；后续案卷和账单下拉中可选。
 */
export const TC_W0_001 = markSkeleton(async (ctx: ExecutionContext, tc: TestCase): Promise<void> => {
  void ctx;
  void tc;
  // Arrange: 登录 / 种子准备 / 跳转页面
  // Act: 按 steps_summary 执行业务流
  // Assert: 校验 UI / API / DB / 文件输出
});

/**
 * TC-W0-002 | 主数据-客户地址
 * 覆盖: FR-WD-10, V-C-06
 * 数据: DS-CL-004, DS-U-ADM
 * 动态值: <none>
 *
 * 前置:
 * DS-U-ADM；客户 DS-CL-004 含一条停用地址和一条有效地址。
 *
 * 步骤摘要:
 * 将停用地址设为默认账单地址并尝试在案卷中选择；再切换为有效地址重试。
 *
 * 预期:
 * 停用地址不能被设为有效默认收件地址或在案卷中被使用；切换为有效地址后可正常引用。
 */
export const TC_W0_002 = markSkeleton(async (ctx: ExecutionContext, tc: TestCase): Promise<void> => {
  void ctx;
  void tc;
  // Arrange: 登录 / 种子准备 / 跳转页面
  // Act: 按 steps_summary 执行业务流
  // Assert: 校验 UI / API / DB / 文件输出
});

/**
 * TC-W0-003 | 主数据-申请人
 * 覆盖: FR-CM-03
 * 数据: DS-AP-001, DS-AP-002, DS-U-ADM
 * 动态值: <none>
 *
 * 前置:
 * DS-U-ADM；准备法人申请人 DS-AP-001 和自然人 DS-AP-002。
 *
 * 步骤摘要:
 * 创建申请人主数据并填写名称、国籍、地址、IsLegalEntity、HasGeneralPower、IsJobInvention 等字段；保存并搜索。
 *
 * 预期:
 * 申请人保存成功；能按名称模糊搜索；HasGeneralPower/IsLegalEntity 在案卷引用时可被带出。
 */
export const TC_W0_003 = markSkeleton(async (ctx: ExecutionContext, tc: TestCase): Promise<void> => {
  void ctx;
  void tc;
  // Arrange: 登录 / 种子准备 / 跳转页面
  // Act: 按 steps_summary 执行业务流
  // Assert: 校验 UI / API / DB / 文件输出
});

/**
 * TC-W0-004 | 主数据-申请人合并
 * 覆盖: FR-CM-03
 * 数据: DS-U-ADM
 * 动态值: <none>
 *
 * 前置:
 * DS-U-ADM；创建两条近似重复的申请人记录。
 *
 * 步骤摘要:
 * 在“申请人维护”执行合并；保留主记录，确认关联地址/标记字段。
 *
 * 预期:
 * 重复记录被合并；主记录保留，关联引用不丢失，旧记录不可再被新案选用。
 */
export const TC_W0_004 = markSkeleton(async (ctx: ExecutionContext, tc: TestCase): Promise<void> => {
  void ctx;
  void tc;
  // Arrange: 登录 / 种子准备 / 跳转页面
  // Act: 按 steps_summary 执行业务流
  // Assert: 校验 UI / API / DB / 文件输出
});

/**
 * TC-W0-005 | 主数据-国家地区
 * 覆盖: FR-CM-01, FR-FE-01, FR-CS-01
 * 数据: DS-U-ADM
 * 动态值: <none>
 *
 * 前置:
 * DS-U-ADM；准备 CN/US/JP/HK/EP 数据。
 *
 * 步骤摘要:
 * 维护国家代码、默认币种、IsDomestic、DefaultLanguage、PCT 成员标志；保存后在案卷/费率/报表处引用。
 *
 * 预期:
 * 国家配置可被案卷、费率、年费和报表使用；Domestic/PCT member 标志在规则分支中可识别。
 */
export const TC_W0_005 = markSkeleton(async (ctx: ExecutionContext, tc: TestCase): Promise<void> => {
  void ctx;
  void tc;
  // Arrange: 登录 / 种子准备 / 跳转页面
  // Act: 按 steps_summary 执行业务流
  // Assert: 校验 UI / API / DB / 文件输出
});

/**
 * TC-W0-006 | 主数据-菌种保藏单位
 * 覆盖: FR-CM-05
 * 数据: DS-BIO-UNIT-001, DS-U-ADM
 * 动态值: <none>
 *
 * 前置:
 * DS-U-ADM；准备 DS-BIO-UNIT-001。
 *
 * 步骤摘要:
 * 维护菌种保藏单位编码、中英文名、地址、联系人；保存后在案卷扩展页引用。
 *
 * 预期:
 * 菌种保藏单位保存成功；在案卷“菌种保藏”标签页可搜索选择。
 */
export const TC_W0_006 = markSkeleton(async (ctx: ExecutionContext, tc: TestCase): Promise<void> => {
  void ctx;
  void tc;
  // Arrange: 登录 / 种子准备 / 跳转页面
  // Act: 按 steps_summary 执行业务流
  // Assert: 校验 UI / API / DB / 文件输出
});

/**
 * TC-W0-007 | 业务参数-费率固定金额
 * 覆盖: FR-FE-01, FR-FE-03
 * 数据: DS-U-FI-01
 * 动态值: <none>
 *
 * 前置:
 * DS-U-FI-01；准备 CN_APPL_BASE、CN_APPL_SERVICE_BASE。
 *
 * 步骤摘要:
 * 在费率维护中创建 Group=APPLY 的 FIXED 费率，设置 FeeType、DefaultCurrency、DefaultAmount、AllowReduction/AllowDiscount。
 *
 * 预期:
 * 费率创建成功，可按 Group/Country/CaseType 查询到；后续草单生成时可被命中。
 */
export const TC_W0_007 = markSkeleton(async (ctx: ExecutionContext, tc: TestCase): Promise<void> => {
  void ctx;
  void tc;
  // Arrange: 登录 / 种子准备 / 跳转页面
  // Act: 按 steps_summary 执行业务流
  // Assert: 校验 UI / API / DB / 文件输出
});

/**
 * TC-W0-008 | 业务参数-费率分档
 * 覆盖: FR-FE-01, FR-FE-03
 * 数据: DS-U-FI-01
 * 动态值: <none>
 *
 * 前置:
 * DS-U-FI-01；准备 BY_YEAR、BY_CLAIMS、BY_PAGES、COMPOSITE 四类 CalcParams。
 *
 * 步骤摘要:
 * 创建年费分档、超项费、超页费和复合计算费率；保存后执行计算预览或在草单生成中调用。
 *
 * 预期:
 * 系统能保存 CalcMode/CalcParams；不同模式能被后续草单正确调用。
 */
export const TC_W0_008 = markSkeleton(async (ctx: ExecutionContext, tc: TestCase): Promise<void> => {
  void ctx;
  void tc;
  // Arrange: 登录 / 种子准备 / 跳转页面
  // Act: 按 steps_summary 执行业务流
  // Assert: 校验 UI / API / DB / 文件输出
});

/**
 * TC-W0-009 | 业务参数-时限模板合法配置
 * 覆盖: FR-DL-01, V-TM-01, V-TM-02, V-TM-03, V-TM-04
 * 数据: DS-U-ADM
 * 动态值: <none>
 *
 * 前置:
 * DS-U-ADM；准备模板代码 APPLY_FEE_LIMIT、OA_REPLY_LIMIT。
 *
 * 步骤摘要:
 * 创建有效模板；再分别尝试 Code 重复、AddYears/AddMonths/AddDays 全为 0、DailyRemind=true 但无 InnerOffset/Remind、DeadlineBase=CUSTOM 但调用端不传 BaseDate。
 *
 * 预期:
 * 有效模板可保存；重复 Code 被拒；无增量模板被拒；DailyRemind 配置不足被拒；调用端缺 BaseDate 时任务生成失败并给出明确错误。
 */
export const TC_W0_009 = markSkeleton(async (ctx: ExecutionContext, tc: TestCase): Promise<void> => {
  void ctx;
  void tc;
  // Arrange: 登录 / 种子准备 / 跳转页面
  // Act: 按 steps_summary 执行业务流
  // Assert: 校验 UI / API / DB / 文件输出
});

/**
 * TC-W0-010 | 业务参数-文档模板配置
 * 覆盖: FR-WD-01, FR-WD-03, V-TPL-01, V-TPL-02, V-TPL-03, V-TPL-04, V-TPL-05
 * 数据: DS-U-ADM
 * 动态值: <none>
 *
 * 前置:
 * DS-U-ADM；准备 OA_NOTICE、OA_REPLY、GRANT_NOTICE、ANNUITY_NOTICE 模板与对应 TaskTemplate/FeeRate。
 *
 * 步骤摘要:
 * 创建 DocTemplate，设置 DocType、StatusEffect、StatusRestore、DeadlineTemplateCode、FeeDraftType、FeeItemList、InputFieldList、PlainTemplateID_CN/EN。
 *
 * 预期:
 * 模板保存成功；字段映射有效；后续向导中默认值、状态联动、任务和草单生成均可被带出。
 */
export const TC_W0_010 = markSkeleton(async (ctx: ExecutionContext, tc: TestCase): Promise<void> => {
  void ctx;
  void tc;
  // Arrange: 登录 / 种子准备 / 跳转页面
  // Act: 按 steps_summary 执行业务流
  // Assert: 校验 UI / API / DB / 文件输出
});

/**
 * TC-W0-011 | 业务参数-文档模板非法配置
 * 覆盖: FR-WD-03, V-TPL-01, V-TPL-02, V-TPL-03, V-TPL-04, V-TPL-05
 * 数据: DS-U-ADM
 * 动态值: <none>
 *
 * 前置:
 * DS-U-ADM；准备不存在的 DeadlineTemplateCode、FeeCode、InputField 字段名。
 *
 * 步骤摘要:
 * 分别尝试保存：重复 TemplateCode；不存在的 DeadlineTemplateCode；只配置 StatusRestore 未说明回复逻辑；FeeItemList 引用不存在费率；InputFieldList 引用不存在字段。
 *
 * 预期:
 * 系统逐项阻止保存并提示具体错误点。
 */
export const TC_W0_011 = markSkeleton(async (ctx: ExecutionContext, tc: TestCase): Promise<void> => {
  void ctx;
  void tc;
  // Arrange: 登录 / 种子准备 / 跳转页面
  // Act: 按 steps_summary 执行业务流
  // Assert: 校验 UI / API / DB / 文件输出
});

/**
 * TC-W0-012 | 文档模板与信头
 * 覆盖: FR-WD-09, FR-WD-10, FR-BL-04
 * 数据: DS-U-ADM
 * 动态值: <none>
 *
 * 前置:
 * DS-U-ADM；准备中文/英文 Word 模板与 CN/EN 信头。
 *
 * 步骤摘要:
 * 上传 T_Template，配置 Group/Language/FilePath/Enabled；创建两套 T_LetterHead 并关联到模板。
 *
 * 预期:
 * 模板和信头均可保存；不同语言模板输出时能正确带出对应抬头。
 */
export const TC_W0_012 = markSkeleton(async (ctx: ExecutionContext, tc: TestCase): Promise<void> => {
  void ctx;
  void tc;
  // Arrange: 登录 / 种子准备 / 跳转页面
  // Act: 按 steps_summary 执行业务流
  // Assert: 校验 UI / API / DB / 文件输出
});

/**
 * TC-W0-013 | 系统参数
 * 覆盖: FR-BL-09, FR-COM-04, FR-COM-05
 * 数据: DS-U-ADM
 * 动态值: <none>
 *
 * 前置:
 * DS-U-ADM；准备催款间隔、默认 WaitPay 阈值、退款策略等参数。
 *
 * 步骤摘要:
 * 维护 T_SystemParam（若实现）；分别设置催款间隔、预收款负账单策略、WaitPay 阈值、ForceSettle 默认策略。
 *
 * 预期:
 * 参数保存成功；相关流程读取到新值，且更新后对新交易生效。
 */
export const TC_W0_013 = markSkeleton(async (ctx: ExecutionContext, tc: TestCase): Promise<void> => {
  void ctx;
  void tc;
  // Arrange: 登录 / 种子准备 / 跳转页面
  // Act: 按 steps_summary 执行业务流
  // Assert: 校验 UI / API / DB / 文件输出
});

/**
 * TC-W0-014 | 权限矩阵
 * 覆盖: FR-CM-06, FR-DL-06, FR-BL-06
 * 数据: DS-U-ADM, DS-U-AG-01, DS-U-FI-01, DS-U-FM-01, DS-U-LMT-01
 * 动态值: <none>
 *
 * 前置:
 * 准备 DS-U-ADM / DS-U-FM-01 / DS-U-AG-01 / DS-U-LMT-01 / DS-U-FI-01。
 *
 * 步骤摘要:
 * 分别以各角色登录，验证菜单、按钮和高危操作权限：案卷完整编辑、受限编辑、时限取消、反冲销、已缴费修改、坏账标记。
 *
 * 预期:
 * Admin 拥有全权限；Formalities 具备流程维护权限；Limited Editor 仅见补充信息入口；Finance 无法修改非法业务字段；高危操作仅授权用户可执行。
 */
export const TC_W0_014 = markSkeleton(async (ctx: ExecutionContext, tc: TestCase): Promise<void> => {
  void ctx;
  void tc;
  // Arrange: 登录 / 种子准备 / 跳转页面
  // Act: 按 steps_summary 执行业务流
  // Assert: 校验 UI / API / DB / 文件输出
});

/**
 * TC-W0-CFG-015 | 前端配置页真实数据展示
 * 覆盖: FR-FE-01, FR-COM-01, FR-DL-01, FR-WD-03
 * 数据: DS-U-ADM, DS-CFG-SYS-BILL-TEMPLATE
 * 动态值: FPMS_RUN_ID
 *
 * 前置:
 * DS-U-ADM 登录前端；准备 supplemental 配置数据。
 *
 * 步骤摘要:
 * 通过真实 API 写入系统参数；打开系统参数页；核对页面展示字段是否与 API payload 一致。
 *
 * 预期:
 * 列表数据来自真实 API；描述、更新时间和密文遮蔽正常展示；不使用静态 mock 数据。
 */
export const TC_W0_CFG_015 = async (ctx: ExecutionContext, tc: TestCase): Promise<void> => {
  void tc;

  const page = ctx.page as Page;
  const request = ctx.request as APIRequestContext;
  const runId = String(ctx.runId || process.env.FPMS_RUN_ID || "LOCAL-RUN-001");
  const apiBaseUrl = normalizeApiBaseUrl(process.env.FPMS_API_URL || "http://localhost:8000/api/v1");
  const username = process.env.FPMS_USERNAME || "admin";
  const password = process.env.FPMS_PASSWORD || "admin123";
  const token = await loginForConfigPage(request, apiBaseUrl, username, password);

  const normalKey = runScopedKey("pw_system_param", runId);
  const secretKey = runScopedKey("pw_secret_param", runId);
  await upsertSystemParam(request, apiBaseUrl, token, normalKey, {
    param_value: `pw-value-${runId}`,
    value_type: "string",
    description: `Playwright 参数 ${runId}`,
    is_secret: false,
  });
  await upsertSystemParam(request, apiBaseUrl, token, secretKey, {
    param_value: `secret-${runId}`,
    value_type: "string",
    description: `Playwright 密文 ${runId}`,
    is_secret: true,
  });

  await page.addInitScript((storedToken) => {
    window.localStorage.setItem("fpms_token", storedToken);
  }, token);
  await page.goto("/system/params");

  await expect(page.getByRole("heading", { name: "系统参数" })).toBeVisible();
  await expect(page.getByText(normalKey)).toBeVisible();
  await expect(page.getByText(`pw-value-${runId}`)).toBeVisible();
  await expect(page.getByText(`Playwright 参数 ${runId}`)).toBeVisible();
  await expect(page.getByText(secretKey)).toBeVisible();
  await expect(page.getByText("******")).toBeVisible();
  await expect(page.getByText(`secret-${runId}`)).toHaveCount(0);
};

function normalizeApiBaseUrl(raw: string): string {
  const trimmed = raw.replace(/\/$/, "");
  return trimmed.endsWith("/api") ? `${trimmed}/v1` : trimmed;
}

function runScopedKey(prefix: string, runId: string): string {
  return `${prefix}_${runId}`.replaceAll("-", "_");
}

async function loginForConfigPage(
  request: APIRequestContext,
  apiBaseUrl: string,
  username: string,
  password: string
): Promise<string> {
  let response;
  try {
    response = await request.post(`${apiBaseUrl}/auth/login`, {
      data: { username, password },
    });
  } catch (error) {
    test.skip(true, `真实后端不可用，跳过配置页真实 API smoke: ${String(error)}`);
    throw error;
  }
  if (!response.ok()) {
    test.skip(true, `登录真实后端失败，跳过配置页真实 API smoke: HTTP ${response.status()}`);
  }
  const payload = await response.json();
  const token = payload?.access_token;
  if (typeof token !== "string" || token.length === 0) {
    throw new Error("登录响应缺少 access_token");
  }
  return token;
}

async function upsertSystemParam(
  request: APIRequestContext,
  apiBaseUrl: string,
  token: string,
  key: string,
  payload: Record<string, unknown>
): Promise<void> {
  const response = await request.put(`${apiBaseUrl}/system/params/${key}`, {
    data: payload,
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!response.ok()) {
    throw new Error(`系统参数写入失败: ${key}, HTTP ${response.status()}`);
  }
}

export const waveW0Handlers: Record<string, (ctx: ExecutionContext, tc: TestCase) => Promise<void>> = {
  "TC-W0-001": TC_W0_001,
  "TC-W0-002": TC_W0_002,
  "TC-W0-003": TC_W0_003,
  "TC-W0-004": TC_W0_004,
  "TC-W0-005": TC_W0_005,
  "TC-W0-006": TC_W0_006,
  "TC-W0-007": TC_W0_007,
  "TC-W0-008": TC_W0_008,
  "TC-W0-009": TC_W0_009,
  "TC-W0-010": TC_W0_010,
  "TC-W0-011": TC_W0_011,
  "TC-W0-012": TC_W0_012,
  "TC-W0-013": TC_W0_013,
  "TC-W0-014": TC_W0_014,
  "TC-W0-CFG-015": TC_W0_CFG_015,
};
