# Billing DB Model (MVP1)

## T_Bill
- BillID, BillNo
- ClientID, Currency
- Direction (AR/AP; MVP1: AR default)
- Status: UNSETTLED/PARTIALLY_SETTLED/SETTLED (BAD_DEBT future)
- BillDate, DueDate
- Totals: TotalGov, TotalService, TotalMisc, Amount, Balance
- DiscountRate (optional)
- CreatedAt/By, UpdatedAt/By

## T_BillItem
- BillItemID, BillID
- CaseID (nullable), DraftID (nullable), FeeItemID (nullable)
- FeeCode, FeeName, FeeType, YearNo
- Amount

## T_Payment
- PaymentID, PayNo
- ClientID, PayDate, Currency, Amount
- PayMethod, BankRefNo, Remark

## T_PaymentLine
- PaymentLineID, PaymentID
- CaseID (nullable)
- RawAmount, AllocatedAmt, BalanceAmt

## T_Offset
- OffsetID, PaymentLineID, BillID
- OffsetAmt, OffsetDate
- IsReversed, ReversedAt/By (future optional)

## T_CaseReceipt
- ReceiptID, CaseID, FeeType
- ReceivableAmt, ReceivedAmt
- Currency
- ReceiptDate (optional per item view)
- Source refs (BillItem/FeeItem) optional

