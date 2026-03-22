# PE-BE-CM-01 — Case 域补齐：组合校验、参与方回填、状态联动、扩展字段规则。

- Source: `docs/FPMS_Final_Enhancement_Plan_and_Task_Breakdown_SPEC_2.0_20260228.md` (`BE-Enh-001`)
- Type: `service + api`
- Execution mode: Atomic (single-task, single-owner)

## Task Definition

- 目标：补齐 Batch 1 中 Case 域后端能力，覆盖以下 `Partially Implemented` 项：
  - `US-CM-01`
  - `US-CM-02`
  - `US-CM-03`
  - `FR-CM-02`
  - `FR-CM-03`
  - `FR-CM-04`
  - `FR-CM-05`
- Allowlist:
  - `backend/app/modules/cases/api.py`
  - `backend/app/modules/cases/service.py`
  - `backend/app/modules/cases/schemas.py`
  - `backend/app/modules/cases/enums.py`
  - `backend/app/modules/documents/service.py`
  - `backend/tests/test_case_fields.py`
  - `backend/tests/test_b2_reply_chain.py`
- Shared ownership files:
  - `backend/app/modules/cases/service.py`
  - `backend/app/modules/cases/schemas.py`
  - `backend/app/modules/cases/api.py`
  - `backend/app/modules/documents/service.py`
- Out of scope:
  - 任意 `document generation` 能力
  - 任意数据库 schema / migration 修改
  - Batch 2+ 需求
- 验收：
  - Case 保存时补齐组合校验与明确错误语义
  - 参与方主数据回填链路补齐后端一致性约束
  - 法律状态枚举与文书联动更新规则补齐
  - 扩展字段业务校验补齐
- 验证：
  - `ruff check --fix backend/app/modules/cases/api.py backend/app/modules/cases/service.py backend/app/modules/cases/schemas.py backend/app/modules/cases/enums.py backend/app/modules/documents/service.py backend/tests/test_case_fields.py backend/tests/test_b2_reply_chain.py`
  - `ruff format backend/app/modules/cases/api.py backend/app/modules/cases/service.py backend/app/modules/cases/schemas.py backend/app/modules/cases/enums.py backend/app/modules/documents/service.py backend/tests/test_case_fields.py backend/tests/test_b2_reply_chain.py`
  - `ruff check backend/app/modules/cases/api.py backend/app/modules/cases/service.py backend/app/modules/cases/schemas.py backend/app/modules/cases/enums.py backend/app/modules/documents/service.py backend/tests/test_case_fields.py backend/tests/test_b2_reply_chain.py`
  - `pytest -q backend/tests/test_case_fields.py backend/tests/test_b2_reply_chain.py`

## Execution Checklist

- [ ] Confirm allowlist only
- [ ] Add minimal failing backend tests first
- [ ] Implement minimal backend changes only
- [ ] Run listed verification commands
- [ ] Generate artifacts evidence
