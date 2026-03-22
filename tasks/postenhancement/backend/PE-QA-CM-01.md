# PE-QA-CM-01 — Batch 1 Case 域验证与范围审计。

- Source: `docs/FPMS_Final_Enhancement_Plan_and_Task_Breakdown_SPEC_2.0_20260228.md` (`QA-Enh-001`, Batch 1 scoped)
- Type: `qa gate`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- 目标：对 Batch 1 的 Case 域修复进行最小必要验证与范围审计。
- Scope checked:
  - `US-CM-01`
  - `US-CM-02`
  - `US-CM-03`
  - `FR-CM-02`
  - `FR-CM-03`
  - `FR-CM-04`
  - `FR-CM-05`
- Allowlist:
  - `backend/tests/test_case_fields.py`
  - `backend/tests/test_b2_reply_chain.py`
  - `frontend/src/modules/cases/pages/CaseCreate.vue`
  - `frontend/src/modules/cases/pages/CaseEdit.vue`
  - `frontend/src/modules/cases/pages/CaseDetail.vue`
  - `frontend/src/api/cases.ts`
  - `frontend/src/api/cases.types.ts`
  - `frontend/src/api/clients.ts`
  - `backend/app/modules/cases/api.py`
  - `backend/app/modules/cases/service.py`
  - `backend/app/modules/cases/schemas.py`
  - `backend/app/modules/cases/enums.py`
  - `backend/app/modules/documents/service.py`
- Audit focus:
  - 不误改 `Fully / Missing / N/A`
  - 不误触 `document generation`
  - 共享文件串行规则是否被遵守
  - 验证是否与 task allowlist 对齐
- 验证：
  - `ruff check` on touched allowlist files
  - `pytest -q backend/tests/test_case_fields.py backend/tests/test_b2_reply_chain.py`
  - `npm run lint`
  - `npm run typecheck`
  - `./scripts/task_validate.sh <TASK-ID>` if evidence exists

## Execution Checklist

- [ ] Confirm Batch 1 only
- [ ] Run minimal backend/FE verification
- [ ] Check no scope contamination
- [ ] Produce PASS / FAIL / BLOCKED with evidence path
