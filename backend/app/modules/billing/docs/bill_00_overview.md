# Billing & Receivables (MVP1)

## Purpose
Generate bills from fee drafts, register payments, offset, and track balances.

## Tables
- T_Bill, T_BillItem
- T_Payment, T_PaymentLine
- T_Offset
- T_CaseReceipt

## MVP1 workflow
- Select drafts → validate same client/currency → generate bill
- Payment register creates Payment + PaymentLine
- Offset: allocate PaymentLine balance to one/multiple bills; update balances/status

