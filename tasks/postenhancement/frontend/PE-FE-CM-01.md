# PE-FE-CM-01 — Cases UI 补齐：动态校验、扩展信息分区、参与方快速回填。

- Source: `docs/FPMS_Final_Enhancement_Plan_and_Task_Breakdown_SPEC_2.0_20260228.md` (`FE-Enh-001`)
- Type: `page + api client`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- 目标：补齐 Batch 1 中 Case 域前端能力，覆盖以下 `Partially Implemented` 项：
  - `US-CM-01`
  - `US-CM-02`
  - `US-CM-03`
  - `FR-CM-02`
  - `FR-CM-03`
  - `FR-CM-04`
  - `FR-CM-05`
- Allowlist:
  - `frontend/src/modules/cases/pages/CaseCreate.vue`
  - `frontend/src/modules/cases/pages/CaseEdit.vue`
  - `frontend/src/modules/cases/pages/CaseDetail.vue`
  - `frontend/src/api/cases.ts`
  - `frontend/src/api/cases.types.ts`
  - `frontend/src/api/clients.ts`
- Shared ownership files:
  - `frontend/src/api/cases.ts`
  - `frontend/src/api/cases.types.ts`
  - `frontend/src/api/clients.ts`
- Out of scope:
  - 任意 `document generation` 能力
  - Batch 2+ 页面或通用 UI 改造
  - 无关国际化/主题重构
- 验收：
  - 新建/编辑案件表单具备动态校验和明确错误定位
  - 扩展信息按条件显示并校验
  - 参与方快速回填链路补齐
  - 案件详情能展示必要的状态联动信息
- 验证：
  - `npm run lint`
  - `npm run typecheck`
  - 手工流程验证：Case Create / Edit / Detail

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Add minimal failing FE test if repo has local test support for touched area; otherwise document manual first-fail scenario
- [ ] Implement minimal frontend changes only
- [ ] Run listed verification commands
- [ ] Record manual verification
