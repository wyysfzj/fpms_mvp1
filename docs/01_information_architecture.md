# MVP1 Information Architecture (Pages / Menu)

## Principles
- **Case-centric navigation**: most operations begin from “Case list → Case detail tabs”.
- Separate top-level module entries for users who prefer “work queues”:
  - Documents queue
  - Task (deadline) queue
  - Billing queue
- Keep MVP1 menus minimal; park non-MVP into future docs.

## Top-level menu (MVP1)
1. Dashboard
2. Cases
3. Documents
4. Tasks (Docket)
5. Fees
6. Billing
7. Settings (Admin / limited)
8. My (Agent shortcuts)

## Page inventory (MVP1)
### Dashboard
- `/dashboard` — KPIs + “today reminders” + quick links

### Cases
- `/cases` — case search/list (filters + sort + export)
- `/cases/new` — create case (Formalities only)
- `/cases/:id` — case detail (tabs)
  - Overview
  - Parties (Applicants/Inventors/Priority)
  - Documents (case-linked)
  - Tasks (case-linked)
  - Fees (case-linked fee drafts)
  - Billing (case-linked bills/receipts)
  - Limited Edit (Agent-only button)

### Documents
- `/documents` — document queue/list (filters: IN/OUT, type, date, case)
- `/documents/new` — register document
- `/documents/:id` — document detail + attachments
- `/documents/:id/render` — render template output (download docx)

### Tasks (Docket)
- `/tasks` — task list + filters (status, due date range, worker, supervisor)
- `/tasks/new` — create task
- `/tasks/:id` — task detail
- `/tasks/today` — “today reminders” page

### Fees
- `/fees/drafts` — fee draft list (by case/client/status)
- `/fees/drafts/new` — create fee draft (manual)
- `/fees/drafts/:id` — fee draft detail (items editable)
- `/fees/rates` — fee rate maintenance (Admin)

### Billing
- `/billing/bills` — bill list + filters
- `/billing/bills/:id` — bill detail (items + print)
- `/billing/payments` — payment register list
- `/billing/payments/new` — register payment
- `/billing/offsets` — payment/bill offset (split view)

### Settings
- `/settings/clients` — client maintenance (Admin/Formalities)
- `/settings/users` — user & role management (Admin)
- `/settings/templates` — template/letterhead management (Admin)
- `/settings/system` — global parameters (Admin)

## Navigation inside Case Detail
Tabs follow the original FPMS mental model:
- 案卷维护 / 中间文件 / 时限管理 / 费用管理 / 账单管理 …  
(legacy user manual describes switching modules to view those aspects).

