# SPEC 2.0 End-to-End UI Testing Plan

## Executive Summary

**Objective**: Validate SPEC 2.0 non-document-generation scope through comprehensive browser-based manual UI testing.

**Scope**:
- Frontend smoke testing for all Batch 1-5A implemented features
- Business workflow validation from Chinese patent agency perspective
- Cross-module integration testing
- Data consistency verification

**Out of Scope**: Document generation UI, consulting/search modules

**Timeline**: 4-6 hours execution + 1 hour reporting

---

## Testing Environment Setup

### Prerequisites

#### Backend Setup
```bash
cd /Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend
source .venv/bin/activate

# Fresh database
rm -f fpms_dev.db
alembic upgrade head
python scripts/seed_dev.py

# Start server
uvicorn app.main:app --reload --port 8000
```

#### Frontend Setup
```bash
cd /Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/frontend

# Ensure demo UI enabled
echo "VITE_DEMO_UI=1" > .env
echo "VITE_API_BASE_URL=http://localhost:8000" >> .env

# Start dev server
npm run dev
```

#### Browser Access
- Frontend: http://localhost:5173
- Backend API Docs: http://localhost:8000/docs
- Test User: `admin` / `admin123`

---

## Test Data Preparation

### Seed Data Verification

After running `seed_dev.py`, verify:

```bash
cd backend
sqlite3 fpms_dev.db << EOF
SELECT COUNT(*) as user_count FROM t_user;
SELECT COUNT(*) as client_count FROM t_client;
SELECT COUNT(*) as case_count FROM t_case;
EOF
```

Expected:
- At least 1 admin user
- At least 3 test clients
- At least 5 test cases

### Additional Test Data

Create via UI during testing:
- 2 new clients (individual + organization)
- 3 new cases (patent + trademark + copyright)
- 5 tasks with different priorities
- 2 fee drafts
- 1 bill with payment
- 1 dunning record
- 1 commission settlement

---

## Testing Modules and Scenarios

### Module 1: Cases Management (Batch 1)

**Test Scope**: PE-FE-CM-01, PE-FE-CM-02, PE-FE-CM-03

#### Test 1.1: Case Creation with Extended Fields

**Steps**:
1. Navigate to Cases → Create New Case
2. Fill in basic fields: case_no, case_type, client, title
3. Fill extended fields: priority_level, estimated_hours, risk_assessment, special_notes
4. Submit and verify success message
5. Navigate to case detail page
6. Verify all extended fields display correctly

**Expected**: All fields saved and displayed correctly

#### Test 1.2: Case List Filtering and Sorting

**Steps**:
1. Navigate to Cases → Case List
2. Test filters: case_type, status, priority_level
3. Test sorting: by case_no, created_at, priority_level
4. Test search by case_no or title
5. Verify pagination works

**Expected**: Filters, sorting, search all functional

#### Test 1.3: Case Detail Tabs

**Steps**:
1. Open any case detail page
2. Navigate through tabs: Overview, Documents, Tasks, Claims, Receipts
3. Verify each tab loads data correctly
4. Test "Add Document" and "Add Task" buttons

**Expected**: All tabs functional, no console errors

---

### Module 2: Documents & Tasks (Batch 2)

**Test Scope**: PE-FE-DL-02, PE-FE-DL-03, PE-FE-WD-02, PE-FE-WD-03

#### Test 2.1: Document Upload and Metadata

**Steps**:
1. Navigate to Documents → Upload Document
2. Select file, fill metadata: doc_type, related_case, tags
3. Upload and verify success
4. Navigate to document detail
5. Verify metadata display and file download link

**Expected**: Upload successful, metadata correct, download works

#### Test 2.2: Document List and Search

**Steps**:
1. Navigate to Documents → Document List
2. Test filters: doc_type, related_case, date_range
3. Test search by filename or tags
4. Test bulk operations (if available)

**Expected**: All filters and search functional

#### Test 2.3: Task Creation with Template

**Steps**:
1. Navigate to Tasks → Create Task
2. Select task template (if available)
3. Fill: title, assignee, due_date, priority, related_case
4. Submit and verify
5. Check task appears in Task List and Dashboard

**Expected**: Task created, appears in all relevant views

#### Test 2.4: Task Status Workflow

**Steps**:
1. Open task detail page
2. Change status: Pending → In Progress → Completed
3. Add comments at each stage
4. Verify status history logged
5. Check Dashboard reflects updated status

**Expected**: Status transitions work, history tracked

---

### Module 3: Fees & Annuity (Batch 3)

**Test Scope**: PE-FE-FE-03, PE-FE-FE-04, PE-FE-AN-06

#### Test 3.1: Fee Draft Creation

**Steps**:
1. Navigate to Fees → Create Fee Draft
2. Select case and fee type
3. Fill amount, currency, description
4. Add fee items (if multi-line supported)
5. Submit and verify

**Expected**: Fee draft created with correct calculations

#### Test 3.2: Fee Rate Configuration

**Steps**:
1. Navigate to System → Fee Rates
2. View existing fee rate table
3. Edit a fee rate (if editable)
4. Verify changes reflected in new fee drafts

**Expected**: Fee rates display and update correctly

#### Test 3.3: Annuity Payment Tracking

**Steps**:
1. Navigate to Annuity → Payment List
2. Create new annuity payment record
3. Fill: case, payment_date, amount, payment_method
4. Submit and verify
5. Check payment appears in case detail

**Expected**: Annuity payment recorded and linked to case

#### Test 3.4: Government Payment Creation

**Steps**:
1. Navigate to Annuity → Gov Payment Create
2. Select case and payment type
3. Fill official fee details
4. Submit and verify
5. Check payment status tracking

**Expected**: Government payment created and tracked

---

### Module 4: Billing & Collections (Batch 4)

**Test Scope**: PE-FE-BL-01, PE-FE-BL-02, PE-FE-BL-03, PE-FE-DL-02, PE-FE-DL-03

#### Test 4.1: Bill Creation from Fee Draft

**Steps**:
1. Navigate to Billing → Create Bill
2. Select client and fee drafts
3. Review bill items and total
4. Adjust discount (if supported)
5. Generate bill and verify

**Expected**: Bill created with correct line items and total

#### Test 4.2: Payment Recording

**Steps**:
1. Navigate to Billing → Payment Create
2. Select bill to pay
3. Fill payment details: amount, method, date
4. Submit and verify
5. Check bill status updated to "Paid" or "Partially Paid"

**Expected**: Payment recorded, bill status updated

#### Test 4.3: Payment List and Filtering

**Steps**:
1. Navigate to Billing → Payment List
2. Test filters: date_range, payment_method, client
3. Test search by bill_no or client_name
4. Verify payment details clickable

**Expected**: All filters and search functional

#### Test 4.4: Dunning Record Creation

**Steps**:
1. Navigate to Collections → Dunning Detail
2. Select overdue bill
3. Create dunning record with reminder level
4. Fill contact method and notes
5. Submit and verify

**Expected**: Dunning record created and linked to bill

#### Test 4.5: Collections Dashboard

**Steps**:
1. Navigate to Collections → Overview
2. Verify overdue bills displayed
3. Check aging analysis (if available)
4. Test quick actions (send reminder, mark paid)

**Expected**: Collections data accurate, actions functional

---

### Module 5: Commission (Batch 5A)

**Test Scope**: PE-FE-COM-01, PE-FE-COM-02, PE-FE-COM-03

#### Test 5.1: Commission List View

**Steps**:
1. Navigate to Commission → Commission List
2. Verify commission records display
3. Test filters: date_range, agent, status
4. Check commission calculation accuracy

**Expected**: Commission data displays correctly

#### Test 5.2: Commission Settlement

**Steps**:
1. Navigate to Commission → Settlement
2. Select period and agent
3. Review commission items
4. Generate settlement report
5. Mark as settled

**Expected**: Settlement process completes, status updated

#### Test 5.3: Commission Configuration

**Steps**:
1. Navigate to System → Commission Rules (if available)
2. View commission rate configuration
3. Verify rules applied correctly in calculations

**Expected**: Commission rules display and apply correctly

---

### Module 6: Master Data - Clients (Common)

**Test Scope**: PE-FE-COM-01, PE-FE-COM-02, PE-FE-COM-03

#### Test 6.1: Client Creation

**Steps**:
1. Navigate to Clients → Create Client
2. Fill individual client: name, contact, email, phone
3. Submit and verify
4. Create organization client: company_name, contact_person, address
5. Verify both types created

**Expected**: Both individual and organization clients created

#### Test 6.2: Client Detail View

**Steps**:
1. Open client detail page
2. Verify tabs: Overview, Cases, Bills, Documents
3. Check related data displays correctly
4. Test "Add Case" and "Create Bill" quick actions

**Expected**: All tabs functional, quick actions work

#### Test 6.3: Client List and Search

**Steps**:
1. Navigate to Clients → Client List
2. Test filters: client_type, status
3. Test search by name, email, phone
4. Verify pagination and sorting

**Expected**: All filters and search functional

---

### Module 7: Dashboard & Today's Reminders

**Test Scope**: Cross-module integration

#### Test 7.1: Dashboard KPI Display

**Steps**:
1. Navigate to Dashboard
2. Verify KPI cards: total_cases, pending_tasks, overdue_bills, etc.
3. Check numbers match actual data
4. Test date range filter (if available)

**Expected**: KPIs accurate and update in real-time

#### Test 7.2: Todo Table

**Steps**:
1. Scroll to Todo Table on Dashboard
2. Verify tasks grouped by priority
3. Click task to navigate to detail
4. Mark task complete from dashboard

**Expected**: Todo table functional, navigation works

#### Test 7.3: Today's Reminders

**Steps**:
1. Navigate to Tasks → Today's Reminders
2. Verify tasks due today displayed
3. Test quick actions: mark complete, snooze
4. Check reminder notifications (if implemented)

**Expected**: Reminders accurate, actions functional

---

## Cross-Module Integration Tests

### Integration 1: Case → Document → Task Flow

**Steps**:
1. Create new case
2. Upload document linked to case
3. Create task linked to case
4. Verify all three entities linked correctly
5. Check case detail shows document and task

**Expected**: Full workflow functional, data linked

### Integration 2: Fee → Bill → Payment Flow

**Steps**:
1. Create fee draft for case
2. Generate bill from fee draft
3. Record payment for bill
4. Verify case shows payment history
5. Check client account balance updated

**Expected**: Full billing cycle functional

### Integration 3: Case → Annuity → Payment Flow

**Steps**:
1. Create case with annuity requirement
2. Create annuity payment record
3. Track payment status
4. Verify case detail shows annuity history

**Expected**: Annuity tracking functional

### Integration 4: Commission Calculation Flow

**Steps**:
1. Create case with assigned agent
2. Generate bill and record payment
3. Verify commission calculated automatically
4. Check commission appears in agent's list

**Expected**: Commission auto-calculation works

---

## UI/UX Quality Checks

### Check 1: Responsive Design

**Steps**:
1. Test on different screen sizes: 1920x1080, 1366x768, 1024x768
2. Verify layout adapts correctly
3. Check mobile view (if supported)

**Expected**: UI responsive, no layout breaks

### Check 2: Chinese Localization

**Steps**:
1. Verify all labels in Chinese (labels.zh.ts)
2. Check date/time format: YYYY-MM-DD HH:mm:ss
3. Verify currency format: ¥ symbol
4. Check number formatting: thousands separator

**Expected**: Full Chinese localization, correct formats

### Check 3: Error Handling

**Steps**:
1. Submit forms with missing required fields
2. Test invalid data (negative amounts, future dates)
3. Simulate network errors (disconnect backend)
4. Verify error messages clear and helpful

**Expected**: Graceful error handling, user-friendly messages

### Check 4: Loading States

**Steps**:
1. Navigate to data-heavy pages
2. Verify loading spinners display
3. Check skeleton screens (if implemented)
4. Test slow network simulation

**Expected**: Loading states clear, no blank screens

### Check 5: Navigation and Breadcrumbs

**Steps**:
1. Navigate through multiple levels
2. Verify breadcrumbs update correctly
3. Test back button functionality
4. Check menu highlighting for active page

**Expected**: Navigation intuitive, breadcrumbs accurate

---

## Browser Compatibility

Test on:
- Chrome (latest)
- Firefox (latest)
- Safari (latest, macOS only)
- Edge (latest)

For each browser:
1. Login and navigate to Dashboard
2. Create one entity in each module
3. Verify no console errors
4. Check UI rendering consistency

**Expected**: Consistent behavior across browsers

---

## Performance Checks

### Check 1: Page Load Time

**Steps**:
1. Open DevTools → Network tab
2. Navigate to each major page
3. Record load time
4. Verify < 3 seconds for initial load

**Expected**: Fast page loads, no blocking resources

### Check 2: API Response Time

**Steps**:
1. Open DevTools → Network tab
2. Perform CRUD operations
3. Check API response times
4. Verify < 500ms for most endpoints

**Expected**: Fast API responses

### Check 3: Large Data Handling

**Steps**:
1. Create 100+ cases (via seed script if needed)
2. Navigate to case list
3. Test pagination and filtering
4. Verify no performance degradation

**Expected**: Handles large datasets smoothly

---

## Acceptance Criteria Checklist

### Batch 1: Cases
- [ ] Case creation with extended fields works
- [ ] Case list filtering and sorting functional
- [ ] Case detail tabs all load correctly
- [ ] Case edit and update works
- [ ] Case status workflow functional

### Batch 2: Documents & Tasks
- [ ] Document upload and metadata works
- [ ] Document list and search functional
- [ ] Task creation with templates works
- [ ] Task status workflow functional
- [ ] Task list and filtering works

### Batch 3: Fees & Annuity
- [ ] Fee draft creation works
- [ ] Fee rate configuration functional
- [ ] Annuity payment tracking works
- [ ] Government payment creation works

### Batch 4: Billing & Collections
- [ ] Bill creation from fee drafts works
- [ ] Payment recording functional
- [ ] Payment list and filtering works
- [ ] Dunning record creation works
- [ ] Collections dashboard functional

### Batch 5A: Commission
- [ ] Commission list view works
- [ ] Commission settlement functional
- [ ] Commission calculation accurate

### Common: Master Data
- [ ] Client creation (individual + org) works
- [ ] Client detail view functional
- [ ] Client list and search works

### Cross-Module
- [ ] Case → Document → Task flow works
- [ ] Fee → Bill → Payment flow works
- [ ] Case → Annuity → Payment flow works
- [ ] Commission calculation flow works

### UI/UX Quality
- [ ] Responsive design works
- [ ] Chinese localization complete
- [ ] Error handling graceful
- [ ] Loading states clear
- [ ] Navigation intuitive

### Browser Compatibility
- [ ] Chrome works
- [ ] Firefox works
- [ ] Safari works (macOS)
- [ ] Edge works

### Performance
- [ ] Page load < 3s
- [ ] API response < 500ms
- [ ] Large data handling smooth

---

## Test Execution Log Template

```markdown
## Test Execution Log

**Date**: YYYY-MM-DD
**Tester**: [Name]
**Environment**: Dev (localhost)
**Browser**: Chrome [version]

### Module 1: Cases Management
- [ ] Test 1.1: Case Creation - PASS/FAIL - [Notes]
- [ ] Test 1.2: Case List Filtering - PASS/FAIL - [Notes]
- [ ] Test 1.3: Case Detail Tabs - PASS/FAIL - [Notes]

### Module 2: Documents & Tasks
- [ ] Test 2.1: Document Upload - PASS/FAIL - [Notes]
- [ ] Test 2.2: Document List - PASS/FAIL - [Notes]
- [ ] Test 2.3: Task Creation - PASS/FAIL - [Notes]
- [ ] Test 2.4: Task Status Workflow - PASS/FAIL - [Notes]

[Continue for all modules...]

### Issues Found
1. [Issue description] - Severity: High/Medium/Low - Module: [X]
2. [Issue description] - Severity: High/Medium/Low - Module: [Y]

### Summary
- Total Tests: [N]
- Passed: [N]
- Failed: [N]
- Blocked: [N]
- Pass Rate: [%]

### Recommendation
- [ ] Ready for acceptance
- [ ] Requires fixes before acceptance
- [ ] Critical issues blocking acceptance
```

---

## Post-Testing Actions

### If All Tests Pass

1. Generate final test report
2. Archive test execution logs
3. Update project status to "Ready for Acceptance"
4. Notify stakeholders

### If Issues Found

1. Log all issues in `findings.md` or issue tracker
2. Prioritize by severity: Critical → High → Medium → Low
3. Create fix tasks for development team
4. Re-test after fixes applied
5. Repeat until acceptance criteria met

---

## Success Criteria

**Definition of Done**:
- All acceptance criteria checkboxes checked
- No critical or high-severity issues open
- Pass rate ≥ 95%
- All cross-module integration flows functional
- UI/UX quality checks passed
- Browser compatibility verified
- Performance benchmarks met

**Final Deliverable**: Test execution log with PASS status for all critical flows and acceptance recommendation.
