# FE-2-18 Evidence Log

## Date
2026-02-07

## Commands Executed

### Quality Gates
```bash
$ npm run lint
# Output: eslint . --max-warnings 0 (PASSED, 0 warnings)

$ npm run typecheck
# Output: vue-tsc --noEmit (PASSED, no errors)

$ npm run build
# Output: vite build - built in 3.00s (PASSED)
# dist/assets/BillCreate-BLYHE7HU.js 8.89 kB
```

## Files Created/Modified
- `src/api/billing.types.ts` - Added: BillFromDraftsPayload, BillManualPayload, BillManualItem
- `src/api/billing.ts` - Added: createBillFromDrafts(), createManualBill()
- `src/modules/billing/pages/BillCreate.vue` - New: Bill creation page with two tabs
- `src/router/index.ts` - Added: /billing/bills/new route

## Manual Smoke Test Steps

### 1. Navigate to `/billing/bills/new`
- Start dev server: `npm run dev`
- Login and navigate to `/billing/bills/new`
- **Expected:**
  - Page with two tabs: "From Fee Drafts" and "Manual Entry"
  - Default tab is "From Fee Drafts"

### 2. From Fee Drafts Tab
- Enter draft IDs in the multi-select field
- Select currency (CNY/USD/EUR)
- Optionally add notes
- Click "Create Bill"
- **Expected (201):**
  - Success message
  - Redirect to bill detail page

### 3. Manual Entry Tab
- Click "Manual Entry" tab
- Fill in:
  - Client ID (required)
  - Case ID (optional)
  - Currency (required)
  - Add bill items with description, quantity, unit price
- Click "Create Bill"
- **Expected (201):**
  - Success message
  - Redirect to bill detail page

### 4. Validation Errors (422)
- Submit manual form with empty client ID
- **Expected:** "Client ID is required" error
- If backend returns 422, field errors mapped to form

### 5. Conflict Error (409)
- Submit drafts with mismatched currencies
- **Expected:** Error banner with 409 conflict message displayed

## API Assumptions
- Backend `POST /bills/from-drafts` accepts: { draft_ids: string[], currency?: string, notes?: string }
- Backend `POST /bills/manual` accepts: { client_id, case_id?, currency, items: [{description, quantity, unit_price}], notes? }
- Both return BillDetail on success
