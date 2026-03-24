# FRFE04-FE-05 Evidence Summary

Implemented a historical manual gov-payment entry UI under the pay-list detail page.

Modified files:
- `frontend/src/modules/annuity/components/ManualGovPaymentDialog.vue`
- `frontend/src/modules/annuity/pages/PayListDetail.vue`
- `frontend/src/api/govPayments.ts`
- `frontend/src/api/govPayments.types.ts`

Verification:
- `npm run lint -- src/modules/annuity/components/ManualGovPaymentDialog.vue src/modules/annuity/pages/PayListDetail.vue src/api/govPayments.ts src/api/govPayments.types.ts`
- `npm run typecheck`
- `./scripts/task_validate.sh FRFE04-FE-05`

Outcome:
- Manual historical rows can be added from the detail page when the list is an empty historical draft list.
- `fee_item_id` is optional and omitted when blank.
