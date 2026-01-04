# MVP1 Database Subset (from SPEC; trimmed)

## Naming convention
- Keep FPMS table naming style: `T_*`
- Use `UUID` primary keys in web version (recommended) and store legacy numeric IDs as optional fields if needed.

## MVP1 tables (must-have)
### Security & audit
- `T_User`
- `T_Role`
- `T_UserRole`
- `T_AuditLog` (optional MVP1, but recommended)

### Master data
- `T_Client`
- `T_ClientAddress`
- `T_ClientContact`
- `T_Applicant` (optional MVP1; can be phased in)

### Case maintenance
- `T_Case`
- `T_CaseApplicant`
- `T_CaseInventor`
- `T_Priority`

### Documents & correspondence
- `T_DocTemplate`
- `T_Document`
- `T_DocAttachment`

### Docket / tasks
- `T_TaskTemplate`
- `T_Task`
- `T_TaskLog`

### Fees
- `T_FeeRate`
- `T_FeeDraft`
- `T_FeeItem`

### Billing & receivables
- `T_Bill`
- `T_BillItem`
- `T_Payment`
- `T_PaymentLine`
- `T_Offset`
- `T_CaseReceipt`

### Templates & system settings
- `T_Template`
- `T_LetterHead`
- `T_SystemParam`

## Indexes (MVP1 minimum)
- `T_Case(CaseNo)` unique
- `T_Case(AppNo)` non-unique index
- `T_Case(ClientID)` index
- `T_Document(CaseID, DocDate)` index
- `T_Task(CaseID, DueDate, Status)` composite index
- `T_FeeDraft(CaseID, Status)` index
- `T_Bill(ClientID, Status, BillDate)` composite index
- `T_Payment(ClientID, PayDate)` index

## Foreign keys (high-level)
- Case → Client (ClientID)
- CaseApplicant → Case + Applicant
- Document → Case + DocTemplate
- Task → Case + TaskTemplate + worker/supervisor (User)
- FeeDraft → Case + Client
- Bill → Client ; BillItem → Bill (+ Case/Draft/FeeItem optional)
- Payment → Client ; PaymentLine → Payment ; Offset → PaymentLine + Bill
- CaseReceipt → Case (+ reference to Bill/FeeItem as needed)

## Migration strategy
- Use Alembic migrations for both SQLite (dev) and Postgres (prod).
- Provide `alembic upgrade head` as standard bootstrap command.

