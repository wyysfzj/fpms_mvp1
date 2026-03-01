# FPMS MVP1 Database Schema (Mermaid)

## How to read this diagram
- Tables follow `t_*` naming; ORM models typically use `T_*`/`CamelCase`.
- Most tables use UUID primary keys and share audit fields via mixins:
  `created_at`, `updated_at`, `created_by`, `updated_by` (some legacy tables use integer PKs).
- Relationships shown are based on the current models/migrations; some FKs are logical even if not enforced in older data.

## ER Diagram (Mermaid)

```mermaid
erDiagram
  t_user ||--o{ t_user_role : has
  t_role ||--o{ t_user_role : has
  t_role ||--o{ t_role_perm : grants

  t_client ||--o{ t_case : owns
  t_client ||--o{ t_client_address : has
  t_client ||--o{ t_client_contact : has

  t_case ||--o{ t_case_applicant : has
  t_case ||--o{ t_case_inventor : has
  t_case ||--o{ t_priority : has

  t_case ||--o{ t_document : has
  t_doc_template ||--o{ t_document : used_by
  t_document ||--o{ t_doc_attachment : has

  t_task_template ||--o{ t_task : used_by
  t_case ||--o{ t_task : has
  t_document ||--o{ t_task : links
  t_task ||--o{ t_task_log : has
  t_user ||--o{ t_task : worker
  t_user ||--o{ t_task : supervisor

  t_case ||--o{ t_fee_draft : has
  t_client ||--o{ t_fee_draft : has
  t_fee_rate ||--o{ t_fee_item : used_by
  t_fee_draft ||--o{ t_fee_item : has
  t_case ||--o{ t_fee_item : links

  t_client ||--o{ t_bill : billed
  t_bill ||--o{ t_bill_item : has
  t_case ||--o{ t_bill_item : links
  t_fee_draft ||--o{ t_bill_item : links
  t_fee_item ||--o{ t_bill_item : links

  t_client ||--o{ t_payment : pays
  t_payment ||--o{ t_payment_line : has
  t_case ||--o{ t_payment_line : links

  t_payment_line ||--o{ t_offset : offsets
  t_bill ||--o{ t_offset : offsets

  t_case ||--o{ t_case_receipt : has

  t_template ||--o{ t_document : used_for
  t_letter_head ||--o{ t_bill : used_for
  t_system_param ||--o{ t_bill : config

  t_user ||--o{ t_system_param : updates
  t_user ||--o{ t_letter_head : creates
```

## Source of truth
Alembic migrations are the authoritative source of the database shape; models should align with migrations.
