# Summary

## Commands
- `./scripts/evidence_run.sh AD-DOC-TERM-01 lint /bin/zsh -lc 'if rg -n "权利要求|官方文件|公文记录|登记公文|案件账务|账务页|文档列表|编辑文档" docs/demo2.md docs/FPMS_Frontend_Manual_Test_User_Guide.md -S; then exit 1; else exit 0; fi'`
- `./scripts/evidence_run.sh AD-DOC-TERM-01 test rg -n "往来文件列表|概览/申请人/发明人/往来文件/费用/账单与收款/任务|返回/编辑往来文件|文件内容/文件信息|登记往来文件|案件收款摘要|案件账单与收款页签" docs/demo2.md docs/FPMS_Frontend_Manual_Test_User_Guide.md -S`
- `./scripts/evidence_finalize.sh AD-DOC-TERM-01`
- `./scripts/task_validate.sh AD-DOC-TERM-01`

## Results
- `docs/demo2.md` 中案件详情点击路径、页签名、按钮名、摘要表述已统一为当前真实 UI 口径：
  `申请人/发明人`、`往来文件`、`登记往来文件`、`账单与收款`、`收款摘要`
- `docs/FPMS_Frontend_Manual_Test_User_Guide.md` 中 `/documents`、`/cases/{id}`、`/documents/{id}` 的标题和详情标签已同步到当前真实 UI
- 旧口径残留扫描为空结果
- Task gate 通过

## Notes
- 本任务是文档整改任务，不涉及前端构建或 HTTP 接口状态码
- `artifacts/AD-DOC-TERM-01/git/diff.patch` 已收窄为本任务涉及的两份文档，避免混入工作区无关改动
