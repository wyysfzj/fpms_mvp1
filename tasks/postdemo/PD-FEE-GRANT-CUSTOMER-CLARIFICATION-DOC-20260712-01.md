# PD-FEE-GRANT-CUSTOMER-CLARIFICATION-DOC-20260712-01

## 设计依据

- `AGENTS.md`
- `docs/postdemo/相关流程操作-20260526.docx`
- `docs/postdemo/专利收费场景-20260626.docx`
- `docs/postdemo/postdemo_p1_functional_spec_20260531.md`
- `docs/postdemo/postdemo_fee_followup_trigger_design_20260705.md`
- `docs/postdemo/postdemo_p1_lifecycle_demo_design_v7_20260711.md`
- `docs/postdemo/postdemo_p1_v7_ui_e2e_success_runbook_20260711.md`
- `docs/reviews/fpms_postdemo_three_lane_pre_fix_audit_20260712.md`

## 故事形态分类

- `shared_file_density`：低，只新增本任务、客户澄清文档和证据。
- `prereq_dependency_density`：中，需要对齐客户原始文档与系统设计中的不同口径。
- `be_fe_coupling`：只读，不修改前后端。
- `evidence_cost`：低，执行内容、纯中文和范围校验。
- `chosen_runbook`：`P0-single-lane-story`

## Exact Closure Slice

新增 `docs/postdemo/postdemo_fee_draft_and_grant_status_customer_clarification_20260712.md`，用客户能够理解的纯中文解释并澄清两项业务规则：各类费用在什么条件下生成费用草单，以及什么官方证据允许把案件标记为“已授权”。文档须将来源分为“客户文档”和“系统设计”，说明差异，并提供可勾选的客户确认项。

## Explicit Non-Closure

不修改客户原始文档、既有设计、审计报告、后端、前端、数据库、迁移、费率、种子、测试和演示脚本；不决定客户尚未确认的业务规则；不实施任何费用或案件状态修复。

## Allowed Files

- `tasks/postdemo/PD-FEE-GRANT-CUSTOMER-CLARIFICATION-DOC-20260712-01.md`
- `docs/postdemo/postdemo_fee_draft_and_grant_status_customer_clarification_20260712.md`
- `artifacts/PD-FEE-GRANT-CUSTOMER-CLARIFICATION-DOC-20260712-01/**`

## Verification Commands

- `rg -n "客户文档|系统设计|需要客户确认|费用草单|已授权|建议确认结果|填写人|确认日期" docs/postdemo/postdemo_fee_draft_and_grant_status_customer_clarification_20260712.md`
- `rg -n "PAY|GRANT|FILING_ACCEPTED|FeeDraft|Case.status|P0|P1|API|UI" docs/postdemo/postdemo_fee_draft_and_grant_status_customer_clarification_20260712.md`，预期无结果。
- `git diff --check -- tasks/postdemo/PD-FEE-GRANT-CUSTOMER-CLARIFICATION-DOC-20260712-01.md docs/postdemo/postdemo_fee_draft_and_grant_status_customer_clarification_20260712.md`
- `./scripts/task_validate.sh PD-FEE-GRANT-CUSTOMER-CLARIFICATION-DOC-20260712-01`

## 完成定义

- 客户原始文档和系统设计的口径分开呈现。
- 两项争议均用非技术语言说明业务后果。
- 费用类型分别确认，不使用一个全局自动规则。
- “授权通知”和“已授权”明确分开。
- 客户可直接勾选并填写最终意见。
- 文档正文除文件路径和正式名称外使用中文。
- 证据完整且任务门禁通过。

## Evidence Path

- `artifacts/PD-FEE-GRANT-CUSTOMER-CLARIFICATION-DOC-20260712-01/`

## Remaining Follow-Up Task IDs

`None`。客户确认后的系统设计与实施须另建原子任务。
