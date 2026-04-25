from __future__ import annotations

from framework.helpers import skeleton_case
from framework.models import TestCase
from framework.runtime import RuntimeContext


@skeleton_case
def handle_tc_h_001(runtime: RuntimeContext, case: TestCase) -> None:
    # TC-H-001 | H1 项目立案
    # 覆盖: FR-CS-01
    # 数据: DS-CL-001, DS-U-FM-01
    # 动态值: CASE-H-${RUN_ID}-001
    # 前置: DS-U-FM-01；客户 DS-CL-001；案号 CASE-H-${RUN_ID}-001。
    # 步骤摘要: 创建 CaseType=CONSULTING 或 SEARCH 案卷，填写项目范围、负责人、预计工时、状态 NOT_STARTED 或 IN_PROGRESS。
    # 预期: 项目案卷保存成功；顾问专属字段持久化；可在高级案件查询中被检出。
    # Arrange: 准备种子数据 / 鉴权 / 页面或 API 上下文。
    # Act: 按 steps_summary 执行业务流。
    # Assert: 按 expected 做 UI / API / DB / 文件断言。
    return None

@skeleton_case
def handle_tc_h_002(runtime: RuntimeContext, case: TestCase) -> None:
    # TC-H-002 | H2 内部任务
    # 覆盖: FR-CS-02, FR-DL-06
    # 数据: <none>
    # 动态值: <none>
    # 前置: 顾问案已创建。
    # 步骤摘要: 创建项目内部任务，例如 CONSULT_SCOPING、SEARCH_EXECUTION、ANALYSIS_REPORT；调整责任人并核销。
    # 预期: 任务可正常创建、编辑、DONE；不依赖官方来文；日志完整。
    # Arrange: 准备种子数据 / 鉴权 / 页面或 API 上下文。
    # Act: 按 steps_summary 执行业务流。
    # Assert: 按 expected 做 UI / API / DB / 文件断言。
    return None

@skeleton_case
def handle_tc_h_003(runtime: RuntimeContext, case: TestCase) -> None:
    # TC-H-003 | H3 项目支出
    # 覆盖: FR-CS-03, FR-FE-08, V-EX-01, V-EX-02
    # 数据: <none>
    # 动态值: <none>
    # 前置: 顾问案已创建。
    # 步骤摘要: 录入 SEARCH_DB、TRANSLATION、TRANSPORT 等支出；测试 Quantity*UnitPrice 与 Total 不一致的手工总额。
    # 预期: 非负校验生效；Total 不一致时系统提示确认是否采用手工总额；支出可按案件/时间/类别查询。
    # Arrange: 准备种子数据 / 鉴权 / 页面或 API 上下文。
    # Act: 按 steps_summary 执行业务流。
    # Assert: 按 expected 做 UI / API / DB / 文件断言。
    return None

@skeleton_case
def handle_tc_h_004(runtime: RuntimeContext, case: TestCase) -> None:
    # TC-H-004 | H4 固定报价草单
    # 覆盖: FR-CS-04, FR-FE-02, FR-FE-03
    # 数据: <none>
    # 动态值: <none>
    # 前置: 顾问案配置固定报价。
    # 步骤摘要: 生成 CONSULT_FEE 或 SEARCH_FEE 草单，添加固定报价服务费明细。
    # 预期: 草单生成成功；TotalService 正确；TotalGov 一般为 0；状态为 OPEN。
    # Arrange: 准备种子数据 / 鉴权 / 页面或 API 上下文。
    # Act: 按 steps_summary 执行业务流。
    # Assert: 按 expected 做 UI / API / DB / 文件断言。
    return None

@skeleton_case
def handle_tc_h_005(runtime: RuntimeContext, case: TestCase) -> None:
    # TC-H-005 | H4 工时/混合报价草单
    # 覆盖: FR-CS-04, FR-FE-02, FR-FE-03
    # 数据: <none>
    # 动态值: <none>
    # 前置: 顾问案配置按工时或混合模式。
    # 步骤摘要: 创建多条服务费明细：高级顾问工时、检索分析人工时、可转嫁杂费。
    # 预期: 数量、单价、金额和杂费汇总正确；可同时包含 SERVICE 与 MISC。
    # Arrange: 准备种子数据 / 鉴权 / 页面或 API 上下文。
    # Act: 按 steps_summary 执行业务流。
    # Assert: 按 expected 做 UI / API / DB / 文件断言。
    return None

@skeleton_case
def handle_tc_h_006(runtime: RuntimeContext, case: TestCase) -> None:
    # TC-H-006 | H5 账单/收款/CaseReceipt
    # 覆盖: FR-CS-05, FR-BL-02, FR-BL-05, FR-FE-07
    # 数据: <none>
    # 动态值: <none>
    # 前置: 存在 CONSULT_FEE/SEARCH_FEE 草单。
    # 步骤摘要: 从草单生成账单；客户付款并冲销；查看 CaseReceipt。
    # 预期: 项目账单和收款闭环成功；CaseReceipt 记录项目实收；费用报表可见。
    # Arrange: 准备种子数据 / 鉴权 / 页面或 API 上下文。
    # Act: 按 steps_summary 执行业务流。
    # Assert: 按 expected 做 UI / API / DB / 文件断言。
    return None

@skeleton_case
def handle_tc_h_007(runtime: RuntimeContext, case: TestCase) -> None:
    # TC-H-007 | H6 顾问提成
    # 覆盖: FR-CS-06, FR-COM-01, FR-COM-02, FR-COM-06
    # 数据: <none>
    # 动态值: <none>
    # 前置: 顾问案账单含 SERVICE 项；存在 CONSULTING/SEARCH 提成规则。
    # 步骤摘要: 触发提成计算并查看结算候选。
    # 预期: 根据顾问/检索规则创建 Commission；可为一次性提成或 S1/S2 两阶段；满足条件可进入结算批次。
    # Arrange: 准备种子数据 / 鉴权 / 页面或 API 上下文。
    # Act: 按 steps_summary 执行业务流。
    # Assert: 按 expected 做 UI / API / DB / 文件断言。
    return None

@skeleton_case
def handle_tc_h_008(runtime: RuntimeContext, case: TestCase) -> None:
    # TC-H-008 | 状态关闭
    # 覆盖: FR-CS-01, FR-CS-05, FR-CS-06
    # 数据: <none>
    # 动态值: <none>
    # 前置: 顾问案存在未完成任务、未结账单或未结算提成。
    # 步骤摘要: 先尝试将项目状态设为 CLOSED；再在任务完成、账单结清、提成结算后重试。
    # 预期: 业务未完成时不应关闭或需强警告；全部闭环后状态可变为 CLOSED。
    # Arrange: 准备种子数据 / 鉴权 / 页面或 API 上下文。
    # Act: 按 steps_summary 执行业务流。
    # Assert: 按 expected 做 UI / API / DB / 文件断言。
    return None

HANDLERS = {
    "TC-H-001": handle_tc_h_001,
    "TC-H-002": handle_tc_h_002,
    "TC-H-003": handle_tc_h_003,
    "TC-H-004": handle_tc_h_004,
    "TC-H-005": handle_tc_h_005,
    "TC-H-006": handle_tc_h_006,
    "TC-H-007": handle_tc_h_007,
    "TC-H-008": handle_tc_h_008,
}
