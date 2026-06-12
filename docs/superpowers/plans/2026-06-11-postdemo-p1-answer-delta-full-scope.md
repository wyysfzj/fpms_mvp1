# Post-demo P1 Answer Delta Full-scope Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `atomic-evidence-gates` for every task. Use `superpowers:test-driven-development` or `tdd` for implementation tasks. Use `/grill-me` before starting the first execution wave and `/diagnose` on failures.

**Goal:** Complete the remaining P1 application enhancement scope introduced by the 2026-06-11 customer answers while preserving and reusing the existing P1 implementation.

**Architecture:** Existing P1 work packages, attachment manifests, receipt archive, fee linkage, and letter handoff remain the foundation. The answer delta adds two missing contracts: applicant-level total POA reuse and explicit fee-reduction conversion from customer reduction ratio to system payable ratio. OA PDF category is already mostly implemented and must be proven in final evidence rather than redesigned.

**Tech Stack:** FastAPI, SQLAlchemy/Alembic, SQLite-compatible migrations, Vue 3, Element Plus, TypeScript, Playwright live-backend E2E.

---

## Story Shape Classification

| Field | Value |
| --- | --- |
| shared_file_density | High. Remaining work touches migrations, applicant masterdata, cases/official workflow services, fees contracts, frontend API types, Vue pages, Playwright fixtures, and final evidence. |
| prereq_dependency_density | High. Data/API carriers must land before service/UI/E2E verification. |
| be_fe_coupling | High. Total POA and fee conversion must be visible consistently across API and UI. |
| evidence_cost | High. Every atomic task requires scoped evidence plus final AC-01..AC-18 close audit. |

chosen_runbook: `P0-prereq-heavy-story`

## Brainstorming Conclusion

Recommended approach: reuse the completed 5/31-6/2 P1 implementation and execute only answer-delta tasks. This is smaller and safer than reopening the whole P1 surface, but still supports a full-scope close audit because unchanged ACs keep their prior task evidence while AC-17 and AC-18 receive new implementation evidence.

Rejected approach 1: treat total POA as a case-level submit-package补录 field. This conflicts with the customer answer that the number belongs to the applicant/customer and is reused across cases.

Rejected approach 2: reinterpret `Case.fee_reduction` globally as a customer reduction ratio. Existing apply-fee contracts and tests use it as a payable multiplier; silently changing semantics would break older behavior. P1 should add an explicit conversion/readiness layer and only feed payable ratios into fee calculation.

P2/P3 exclusions remain unchanged: no official direct submission, no browser automation/RPA, no QR/signature automation, no auto-payment, no Longxia email sending, no official XML/package generation beyond manifest readiness.

## Full-scope Delta Summary

| Area | Current Evidence | Delta Decision |
| --- | --- | --- |
| Original P1 AC-01..AC-16 | Prior P1 task evidence under `artifacts/PD-P1-*` and QA close ledger `artifacts/PD-P1-QA-FULLSCOPE-E2E-01/close_ledger.md`. | Reuse, then revalidate in final answer-delta close audit. |
| AC-06 OA PDF category | Code and tests already include `OA_STATEMENT_PDF`, `OA_OTHER_PROOF`, and visible “其他证明文件”. | No broad rewrite; final QA must prove the category is no longer treated as pending. |
| AC-17 total POA | `Applicant`, `Client`, `Case`, and `T_CaseApplicant` currently lack total POA fields. `T_CaseApplicant.applicant_id` already links cases to applicant masterdata. | Add applicant masterdata carrier/API/UI, then expose filing readiness by linked applicant and mapping status. |
| AC-18 fee conversion | Current fee linkage text says customer semantics are待确认; apply-fee service multiplies by `case.fee_reduction`. | Add structured customer reduction ratio -> payable ratio conversion and surface it in API/UI/E2E without claiming official fee-rate seed readiness. |

## Execution Waves

### Wave 1: Data Carrier

1. `tasks/postdemo/PD-P1-DB-APPLICANT-TOTAL-POA-20260611-01.md`
   - Adds SQLite-safe applicant masterdata field for 总委托书备案编号.
   - Does not expose API/UI behavior.

### Wave 2: Backend Contracts

2. `tasks/postdemo/PD-P1-BE-APPLICANT-TOTAL-POA-API-20260611-01.md`
   - Exposes the applicant field in existing applicant masterdata API.
   - Keeps applicant uniqueness rules unchanged except for optional field normalization.

3. `tasks/postdemo/PD-P1-BE-FILING-TOTAL-POA-READINESS-20260611-01.md`
   - Filing preparation API reads linked applicant total POA and reports mapping/maintenance status.
   - Does not add official submission or XML generation.

4. `tasks/postdemo/PD-P1-BE-FEE-REDUCTION-CONVERSION-20260611-01.md`
   - Adds structured fee conversion evidence for customer reduction ratio and payable ratio in P1 fee linkage.
   - Tests `0.85 -> 0.15`, `0.7 -> 0.3`, and no reduction -> `1.0`.

### Wave 3: Frontend Surfaces

5. `tasks/postdemo/PD-P1-FE-APPLICANT-TOTAL-POA-UI-20260611-01.md`
   - Adds total POA maintenance to applicant masterdata UI.
   - Keeps all visible text Simplified Chinese.

6. `tasks/postdemo/PD-P1-FE-FEE-REDUCTION-CONVERSION-20260611-01.md`
   - Shows customer reduction ratio and computed payable ratio in fee linkage UI.
   - Removes “语义待确认” for the answered `0 / 0.7 / 0.85` rule.

### Wave 4: E2E and Close Audit

7. `tasks/postdemo/PD-P1-E2E-ANSWER-DELTA-LIVE-20260611-01.md`
   - Updates live-backend Playwright coverage for total POA reuse, OA other-proof PDF category, and fee conversion display.

8. `tasks/postdemo/PD-P1-QA-FULLSCOPE-ANSWER-DELTA-20260611-01.md`
   - Produces final item-to-AC ledger for AC-01..AC-18 with evidence paths and residual gaps.
   - Runs final targeted backend/frontend/E2E verification and task gates.

## Grill-me Checklist Before Execution

- Does AC-17 prove applicant/customer-level reuse, not case-level补录?
- Does the filing readiness API make client/applicant mismatch visible instead of hiding it?
- Does AC-18 avoid changing old payable-ratio fee calculation behavior silently?
- Do frontend labels say “减免比例” and “应缴比例” distinctly?
- Is OA PDF category proven as “附加文件 -> 其他证明文件” without implying auto-upload?
- Are direct submit, signing, QR scan, payment, and Longxia sending still non-scope?

## Done Definition

- Every task in the manifest has PASS evidence or a documented BLOCKED reason.
- Final close audit maps AC-01..AC-18 to current evidence.
- No answered customer item remains labeled as “待确认”.
- All modified UI text is Simplified Chinese.
- `./scripts/task_validate.sh <TASK-ID>` passes for every claimed PASS task.
