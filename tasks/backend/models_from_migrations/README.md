# ORM Models from Alembic Migrations — Atomic Tasks

Execute tasks in order (by migration then table).

Each task adds ONE ORM class into ONE models.py file.


## 0001_mvp1_core_tables.py
- `BE-MD-0001-01_t_case` — `t_case`
- `BE-MD-0001-02_t_client` — `t_client`
- `BE-MD-0001-03_t_role` — `t_role`
- `BE-MD-0001-04_t_user` — `t_user`
- `BE-MD-0001-05_t_user_role` — `t_user_role`

## 0002_documents.py
- `BE-MD-0002-01_t_doc_attachment` — `t_doc_attachment`
- `BE-MD-0002-02_t_doc_template` — `t_doc_template`
- `BE-MD-0002-03_t_document` — `t_document`
- `BE-MD-0002-04_t_template` — `t_template`

## 0003_tasks.py
- `BE-MD-0003-01_t_task` — `t_task`
- `BE-MD-0003-02_t_task_log` — `t_task_log`
- `BE-MD-0003-03_t_task_template` — `t_task_template`

## 0004_fees.py
- `BE-MD-0004-01_t_fee_draft` — `t_fee_draft`
- `BE-MD-0004-02_t_fee_item` — `t_fee_item`
- `BE-MD-0004-03_t_fee_rate` — `t_fee_rate`

## 0005_billing.py
- `BE-MD-0005-01_t_bill` — `t_bill`
- `BE-MD-0005-02_t_bill_item` — `t_bill_item`
- `BE-MD-0005-03_t_case_receipt` — `t_case_receipt`
- `BE-MD-0005-04_t_offset` — `t_offset`
- `BE-MD-0005-05_t_payment` — `t_payment`
- `BE-MD-0005-06_t_payment_line` — `t_payment_line`
