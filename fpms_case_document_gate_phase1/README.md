# FPMS 案卷主线 + 文件门禁交付包

本包已按“文书事件驱动”的 approach 重写。

核心变化：

- 保留案卷主线，不建立独立文件主流程。
- 引入文件资产、文书事件、门禁快照、影响计划、效果账本。
- 新建案卷检查收案文件；递交检查最终递交材料。
- 原型页面已从旧截图壳改为真实静态页面，可重新截图。
- 种子规则已调整为与现有 CaseType、PatentCategory、FlowDir 枚举兼容。

## 内容

- FPMS_案卷主线_文件门禁增强方案_Phase1.md：修订后的业务架构方案。
- mock-ui/index.html：可浏览 10 个 mock 页面截图的总览。
- mock-ui/pages/*.html：10 个静态 mock 页面。
- mock-ui/screens/*.png：页面截图。
- mock-ui/screens/*.svg：嵌入对应 PNG 的 SVG 包装图。
- data/case_document_requirements_seed.*：材料要求规则种子。
- data/doc_status_rules_seed.*：文书事件状态/任务/费用效果规则种子。

## 推荐评审顺序

02 → 03 → 04 → 05 → 08 → 06 → 07 → 09 → 10

这个顺序可以说明：

- 收案文件如何形成文件资产。
- 文件如何满足建案门禁。
- 建案如何形成 CLIENT_INTAKE 文书事件。
- 案件详情如何展示当前节点文件材料区。
- 来文如何先预览影响再落账。
- 递交为什么必须检查最终递交材料。
