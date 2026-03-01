# FPMS MVP1 Entity Relationship Diagram

## ER Diagram

```mermaid
erDiagram

    CLIENT ||--o{ CASE : "委托"
    CLIENT ||--o{ FEE_DRAFT : "费用归属"
    CLIENT ||--|{ BILL : "出账"
    CLIENT ||--|{ PAYMENT : "付款"

    CASE ||--o{ DOCUMENT : "案件文书"
    CASE ||--o{ TASK : "期限/任务"
    CASE ||--o{ FEE_DRAFT : "费用草单"
    CASE ||--o{ CASE_APPLICANT : "申请人"
    CASE ||--o{ CASE_INVENTOR : "发明人"
    CASE ||--o{ PRIORITY : "优先权"
    CASE ||--o{ CASE_RECEIPT : "收款汇总"

    DOCUMENT ||--o{ TASK : "关联任务"
    DOCUMENT ||--o{ DOC_ATTACHMENT : "附件"
    DOCUMENT o|--|| DOC_TEMPLATE : "使用模板"

    TASK ||--o{ TASK_LOG : "操作日志"

    FEE_DRAFT ||--|{ FEE_ITEM : "费用明细"

    BILL ||--|{ BILL_ITEM : "账单明细"
    BILL ||--o{ OFFSET : "核销"

    PAYMENT ||--|{ PAYMENT_LINE : "付款分配"
    PAYMENT_LINE ||--o{ OFFSET : "冲销账单"

    FEE_ITEM ||--o{ BILL_ITEM : "出账来源"

    CLIENT {
        uuid id PK
        string client_code UK
        string name_cn
        string name_en
        string client_type "CLIENT"
        string default_currency "CNY"
        bool is_active
    }

    CASE {
        uuid id PK
        string case_no UK
        string case_type "NORMAL"
        string patent_category "INV"
        string flow_dir "CN_DOMESTIC"
        uuid client_id FK "nullable"
        string status "NOT_FILED"
        date recv_date
        date filing_date
    }

    DOCUMENT {
        uuid id PK
        uuid case_id FK "NOT NULL CASCADE"
        uuid doc_template_id FK "nullable"
        string direction "IN/OUT"
        date doc_date
        string title
        string ref_no
    }

    TASK {
        uuid id PK
        uuid case_id FK "NOT NULL CASCADE"
        uuid document_id FK "nullable"
        uuid task_template_id FK "nullable"
        string title
        date base_date
        date due_date
        date internal_due_date
        uuid worker_id FK "nullable"
        uuid supervisor_id FK "nullable"
        string status "OPEN"
        datetime done_at
    }

    FEE_DRAFT {
        uuid id PK
        uuid case_id FK "NOT NULL CASCADE"
        uuid client_id FK "nullable"
        string draft_type "GENERIC"
        string currency "CNY"
        string status "OPEN"
        decimal total_gov
        decimal total_service
        decimal total_misc
        decimal amount
    }

    FEE_ITEM {
        uuid id PK
        uuid draft_id FK "NOT NULL CASCADE"
        uuid case_id FK "nullable"
        uuid rate_id FK "nullable"
        string fee_code
        string fee_name
        string fee_type "SERVICE"
        decimal quantity
        decimal unit_price
        decimal amount
    }

    BILL {
        uuid id PK
        string bill_no UK
        uuid client_id FK "NOT NULL"
        string currency "CNY"
        string direction "AR"
        string status "UNSETTLED"
        date bill_date
        date due_date
        decimal amount
        decimal balance
    }

    BILL_ITEM {
        uuid id PK
        uuid bill_id FK "NOT NULL CASCADE"
        uuid case_id FK "nullable"
        uuid draft_id FK "nullable"
        uuid fee_item_id FK "nullable"
        string fee_code
        string fee_name
        string fee_type
        decimal amount
    }

    PAYMENT {
        uuid id PK
        string pay_no
        uuid client_id FK "NOT NULL"
        date pay_date
        string currency "CNY"
        decimal amount
    }

    PAYMENT_LINE {
        uuid id PK
        uuid payment_id FK "NOT NULL CASCADE"
        uuid case_id FK "nullable"
        decimal raw_amount
        decimal allocated_amt
        decimal balance_amt
    }

    OFFSET {
        uuid id PK
        uuid payment_line_id FK "NOT NULL CASCADE"
        uuid bill_id FK "NOT NULL CASCADE"
        decimal offset_amt
        date offset_date
        bool is_reversed
    }

    CASE_APPLICANT {
        uuid id PK
        uuid case_id FK "NOT NULL CASCADE"
        int seq
    }

    CASE_INVENTOR {
        uuid id PK
        uuid case_id FK "NOT NULL CASCADE"
        int seq
    }

    PRIORITY {
        uuid id PK
        uuid case_id FK "NOT NULL CASCADE"
        int seq
    }

    CASE_RECEIPT {
        uuid id PK
        uuid case_id FK "NOT NULL CASCADE"
        string fee_type
        decimal receivable_amt
        decimal received_amt
    }

    DOC_ATTACHMENT {
        uuid id PK
        uuid document_id FK "NOT NULL CASCADE"
    }

    DOC_TEMPLATE {
        uuid id PK
        string code UK
        string name
    }

    TASK_LOG {
        uuid id PK
        uuid task_id FK "NOT NULL CASCADE"
        string action
        string from_status
        string to_status
        string remark
    }

    FEE_RATE {
        uuid id PK
        string fee_code
        string fee_name
        string fee_type "SERVICE"
        decimal default_amount
        bool enabled
    }
```

## 核心关系链路

- **Client → Case → Document / Task / FeeDraft** — 业务主线
- **FeeDraft → FeeItem → BillItem → Bill** — 费用出账链
- **Payment → PaymentLine → Offset → Bill** — 收款核销链
- CASCADE 删除沿 Case 向下传播到 Document、Task、FeeDraft、CaseReceipt
