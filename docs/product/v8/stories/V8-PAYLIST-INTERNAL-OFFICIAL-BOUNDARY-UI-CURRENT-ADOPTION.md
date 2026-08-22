# Story V8-PAYLIST-INTERNAL-OFFICIAL-BOUNDARY-UI-CURRENT-ADOPTION

- Risk: `PROTECTED`
- Integration parent: `ed6a4c5`
- Outcome: show internal exports, official workbook, payment records and official evidence
  as four visibly separate PayList facts without inferring official state from the PayList
  header.
- Catalog ID: `FPMS-V8-PAYLIST-INTERNAL-OFFICIAL-BOUNDARY-UI-20260712-01`
  (ordinal `164`, profile `TC-UI`).
- Authority: frozen catalog row `164`, its exact task contract, current-verified row `163`
  frontend boundary, and `docs/product/v8/domain-contract.md`.

## Dependency and exact paths

The sole canonical predecessor is
`FPMS-V8-PAYLIST-BOUNDARY-FE-ADAPTER-20260712-01`, current-verified by
`V8-PAYLIST-BOUNDARY-FE-ADAPTER-CURRENT-ADOPTION`.

- `frontend/src/modules/annuity/pages/PayListDetail.vue`
- `FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/v8-pay-list-boundary-ui.spec.ts`
- `docs/product/v8/stories/V8-PAYLIST-INTERNAL-OFFICIAL-BOUNDARY-UI-CURRENT-ADOPTION.md`

## Observable contract

The page presents four Simplified-Chinese sections: `内部导出`, `官方工作簿`,
`支付记录` and `官方凭证`. Each reads only the corresponding independent row-163
projection. An absent official workbook displays its explicit gate message based only on
`detail.official_workbook`; neither that state nor official evidence is inferred from
`detail.pay_list.status`. Existing payment operations and the compatible payment
projection remain unchanged.

## TDD and verification

The dedicated direct Playwright contract probe first failed `2/2` on the missing four
sections and official-workbook gate. After the minimum page change, the same probe passed
`2/2` in under one second. It is intentionally runner-only because the local Vite listener
is prohibited in the current sandbox; browser-backed verification remains owned by the
later named real-UI E2E close.

Exact page ESLint exits `0`. Direct `vue-tsc --noEmit` reports only the same seven inherited
errors in `billing.ts`, `http.ts`, `officialWorkflows.ts` and `CaseFeesTab.vue`, with no
row-164/page error. Scoped diff and whitespace checks pass. An independent High reviewer
must review the exact eventual commit and independently rerun the decisive direct probe
and page lint.

## Non-goals and rollback

No backend, API contract, PayList header/payment mutation, official workbook generation or
acceptance, evidence fabrication, lifecycle/legal status, fee/source rule, schema,
migration, unrelated page cleanup, old task/evidence mutation, ledger/review edit or
milestone claim. Rollback reverts only the three paths listed above.
