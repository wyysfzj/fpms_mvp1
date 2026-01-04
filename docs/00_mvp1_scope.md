# MVP1 Scope

## Product objective
Deliver a **B/S (Web) MVP** that replays the most valuable “case-driven pipeline” of FPMS:

**Case → Documents → Deadline Tasks → Fee Draft → Bill → Payment/Offset → Case Receipt**

This pipeline is the operational backbone referenced by the SPEC summary of the full lifecycle.  
MVP1 should make users confident by enabling them to:
- register a case and search it;
- register incoming/outgoing correspondence and attach files;
- create and manage docket tasks + reminders;
- create fee drafts and convert them into bills;
- register payment and offset against bills;
- view case-level receivable/received at a glance;
- output basic Word documents (bill/task sheet) from templates.

## MVP1 In-scope modules
### A. Authentication & RBAC
- Login/logout
- Role-based menu rendering
- Permission enforcement on API (RBAC)

### B. Master data (minimal)
- Client (with addresses & contacts)
- Applicant (optional in MVP1; can be “free text + upgrade later” if needed)
- Users (Admin only)

### C. Case maintenance (核心)
- Create case (NORMAL only in MVP1; extensions parked into `case_future.md`)
- Case list/search + export
- Case detail edit by Formalities
- “Limited edit” view for Agent (white list fields only)

### D. Documents & correspondence (minimal)
- Document register: IN/OUT direction, doc type, dates, attachments
- Link document to a Case
- Basic template rendering (server-side docxtpl → docx download)

### E. Deadline & docket (核心)
- Task templates (minimal set)
- Task CRUD, assign worker + supervisor
- Mark done / cancel / reopen (log maintained)
- “Today reminder” page (by worker/supervisor)

### F. Fee management (MVP)
- Fee rates (minimal: service fee items as configurable)
- Fee draft CRUD (manual or from simple doc template trigger later)
- Fee items CRUD

### G. Billing & receivables (MVP)
- Generate bill from fee draft (single client + currency constraint)
- Manual bill create (optional)
- Payment register
- Offset payment to bills; update balance/status
- Case receipt summary (by case & fee type)

### H. Settings (minimal)
- System parameters (only those needed by MVP1)
- Templates & letterhead metadata (store file path, language, group)

## Explicitly NOT in MVP1 (parked as future)
- PCT international + national plan; national entry automation
- Annual fee/renewal batch, grace rules, complex notifications
- Invalidation / litigation full workflows
- Dunning, bad debt, complex finance reports
- Commission calculation & settlement
- Full “template builder UI” (keep as file-based template upload)
- Full-text search / Elasticsearch

See per-module `*_future.md` documents.

## MVP1 success criteria (“confidence milestones”)
1. A user can create a case, search it, and open a case detail reliably.
2. A user can register an OA notice (document + attachment) and system can create a task.
3. A user can create a fee draft and generate a bill; finance can register payment & offset.
4. A user can generate a Word bill from a template and deliver it to client.

