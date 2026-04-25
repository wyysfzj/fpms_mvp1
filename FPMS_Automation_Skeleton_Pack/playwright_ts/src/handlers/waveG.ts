import type { ExecutionContext, TestCase } from "../support/types";
import { markSkeleton } from "../support/helpers";

/**
 * TC-G-001 | G1 逾期识别
 * 覆盖: FR-BL-07, FR-BL-08
 * 数据: <none>
 * 动态值: <none>
 *
 * 前置:
 * 存在多张 AR 账单，其中包括未到期、已结清、坏账和逾期未结账单。
 *
 * 步骤摘要:
 * 按 ToDate 执行逾期识别或打开逾期报表。
 *
 * 预期:
 * 仅 Direction=AR、Status=UNSETTLED/PARTIALLY_SETTLED、IsBadDebt=false、DueDate<=ToDate、Balance>0 的账单被识别为逾期。
 */
export const TC_G_001 = markSkeleton(async (ctx: ExecutionContext, tc: TestCase): Promise<void> => {
  void ctx;
  void tc;
  // Arrange: 登录 / 种子准备 / 跳转页面
  // Act: 按 steps_summary 执行业务流
  // Assert: 校验 UI / API / DB / 文件输出
});

/**
 * TC-G-002 | G2 生成催款单快照
 * 覆盖: FR-BL-08
 * 数据: <none>
 * 动态值: <none>
 *
 * 前置:
 * 客户存在多张逾期账单。
 *
 * 步骤摘要:
 * 以客户+截止日生成 T_Dunning/T_DunningLine。
 *
 * 预期:
 * 催款单头和明细创建成功；OutstandingAmt 记录生成时快照，不受后续收款回写影响；TotalAmt 为各行合计。
 */
export const TC_G_002 = markSkeleton(async (ctx: ExecutionContext, tc: TestCase): Promise<void> => {
  void ctx;
  void tc;
  // Arrange: 登录 / 种子准备 / 跳转页面
  // Act: 按 steps_summary 执行业务流
  // Assert: 校验 UI / API / DB / 文件输出
});

/**
 * TC-G-003 | G2 催款范围过滤
 * 覆盖: FR-BL-08
 * 数据: <none>
 * 动态值: <none>
 *
 * 前置:
 * 客户同时存在已结清、未到期、坏账和 AP 账单。
 *
 * 步骤摘要:
 * 生成催款单。
 *
 * 预期:
 * 已结清、未到期、坏账、AP 账单不应进入催款明细。
 */
export const TC_G_003 = markSkeleton(async (ctx: ExecutionContext, tc: TestCase): Promise<void> => {
  void ctx;
  void tc;
  // Arrange: 登录 / 种子准备 / 跳转页面
  // Act: 按 steps_summary 执行业务流
  // Assert: 校验 UI / API / DB / 文件输出
});

/**
 * TC-G-004 | G3 生成催款函
 * 覆盖: FR-BL-08, FR-WD-06
 * 数据: <none>
 * 动态值: <none>
 *
 * 前置:
 * 催款单已创建；存在 DUNNING_LETTER 模板。
 *
 * 步骤摘要:
 * 从催款单生成催款函 Word/PDF 或 Email 并发送。
 *
 * 预期:
 * 催款函生成成功；可作为 T_Document 存档；T_Dunning.Status/SentDate 更新。
 */
export const TC_G_004 = markSkeleton(async (ctx: ExecutionContext, tc: TestCase): Promise<void> => {
  void ctx;
  void tc;
  // Arrange: 登录 / 种子准备 / 跳转页面
  // Act: 按 steps_summary 执行业务流
  // Assert: 校验 UI / API / DB / 文件输出
});

/**
 * TC-G-005 | G4 催款后部分付款
 * 覆盖: FR-BL-05, FR-BL-08, FR-FE-07
 * 数据: <none>
 * 动态值: <none>
 *
 * 前置:
 * 逾期账单已被催款。
 *
 * 步骤摘要:
 * 登记客户部分付款并冲销到账单。
 *
 * 预期:
 * 账单余额减少、状态更新为 PARTIALLY_SETTLED；CaseReceipt 更新已收金额；历史 DunningLine 快照不变。
 */
export const TC_G_005 = markSkeleton(async (ctx: ExecutionContext, tc: TestCase): Promise<void> => {
  void ctx;
  void tc;
  // Arrange: 登录 / 种子准备 / 跳转页面
  // Act: 按 steps_summary 执行业务流
  // Assert: 校验 UI / API / DB / 文件输出
});

/**
 * TC-G-006 | G5 多轮催款
 * 覆盖: FR-BL-08
 * 数据: <none>
 * 动态值: <none>
 *
 * 前置:
 * 账单仍有未结余额，已存在第一轮催款单。
 *
 * 步骤摘要:
 * 再次生成第二轮/第三轮催款单。
 *
 * 预期:
 * 新一轮 Dunning/DunningLine 创建成功；OutstandingAmt 反映当轮余额；旧催款数据不被覆盖。
 */
export const TC_G_006 = markSkeleton(async (ctx: ExecutionContext, tc: TestCase): Promise<void> => {
  void ctx;
  void tc;
  // Arrange: 登录 / 种子准备 / 跳转页面
  // Act: 按 steps_summary 执行业务流
  // Assert: 校验 UI / API / DB / 文件输出
});

/**
 * TC-G-007 | G6 标记坏账
 * 覆盖: FR-BL-07
 * 数据: <none>
 * 动态值: <none>
 *
 * 前置:
 * 存在长期逾期且无回收希望的应收账单。
 *
 * 步骤摘要:
 * 对账单执行“标记坏账”，填写 BadDebtDate、BadDebtReason。
 *
 * 预期:
 * Bill.IsBadDebt=true，Status=BAD_DEBT；在普通应收统计与坏账统计中区分显示。
 */
export const TC_G_007 = markSkeleton(async (ctx: ExecutionContext, tc: TestCase): Promise<void> => {
  void ctx;
  void tc;
  // Arrange: 登录 / 种子准备 / 跳转页面
  // Act: 按 steps_summary 执行业务流
  // Assert: 校验 UI / API / DB / 文件输出
});

/**
 * TC-G-008 | G7 坏账后收回
 * 覆盖: FR-BL-05, FR-BL-07, FR-FE-07
 * 数据: <none>
 * 动态值: <none>
 *
 * 前置:
 * 账单已是 BAD_DEBT。
 *
 * 步骤摘要:
 * 登记客户付款并冲销到坏账账单。
 *
 * 预期:
 * 系统仍允许登记收款和 Offset；Bill.Balance 下降；CaseReceipt 记录坏账后回收金额；账单可按策略继续保持 BAD_DEBT 或转状态。
 */
export const TC_G_008 = markSkeleton(async (ctx: ExecutionContext, tc: TestCase): Promise<void> => {
  void ctx;
  void tc;
  // Arrange: 登录 / 种子准备 / 跳转页面
  // Act: 按 steps_summary 执行业务流
  // Assert: 校验 UI / API / DB / 文件输出
});

/**
 * TC-G-009 | G7 坏账恢复策略
 * 覆盖: FR-BL-07
 * 数据: <none>
 * 动态值: <none>
 *
 * 前置:
 * 存在 BAD_DEBT 账单。
 *
 * 步骤摘要:
 * 执行“从坏账恢复”或在完全收回后检查系统状态。
 *
 * 预期:
 * 如系统支持恢复，IsBadDebt 恢复为 false，状态改为 UNSETTLED/PARTIALLY_SETTLED/SETTLED；若不支持则明确只保留 BAD_DEBT 但余额更新。
 */
export const TC_G_009 = markSkeleton(async (ctx: ExecutionContext, tc: TestCase): Promise<void> => {
  void ctx;
  void tc;
  // Arrange: 登录 / 种子准备 / 跳转页面
  // Act: 按 steps_summary 执行业务流
  // Assert: 校验 UI / API / DB / 文件输出
});

/**
 * TC-G-010 | G8 对提成的间接影响
 * 覆盖: FR-COM-04, FR-COM-05
 * 数据: <none>
 * 动态值: <none>
 *
 * 前置:
 * 存在 WaitPay=true 的提成记录，对应账单长期逾期后部分回收或坏账后回收。
 *
 * 步骤摘要:
 * 观察回款前后 Commission 可结算状态。
 *
 * 预期:
 * 只有通过 Offset/CaseReceipt 确认归属的回款才提升 PaidRatio；催款和坏账标签本身不直接改变 BaseFee，但会影响可结算性。
 */
export const TC_G_010 = markSkeleton(async (ctx: ExecutionContext, tc: TestCase): Promise<void> => {
  void ctx;
  void tc;
  // Arrange: 登录 / 种子准备 / 跳转页面
  // Act: 按 steps_summary 执行业务流
  // Assert: 校验 UI / API / DB / 文件输出
});

export const waveGHandlers: Record<string, (ctx: ExecutionContext, tc: TestCase) => Promise<void>> = {
  "TC-G-001": TC_G_001,
  "TC-G-002": TC_G_002,
  "TC-G-003": TC_G_003,
  "TC-G-004": TC_G_004,
  "TC-G-005": TC_G_005,
  "TC-G-006": TC_G_006,
  "TC-G-007": TC_G_007,
  "TC-G-008": TC_G_008,
  "TC-G-009": TC_G_009,
  "TC-G-010": TC_G_010,
};
