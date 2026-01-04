# Fee DB Model (MVP1)

## T_FeeRate
- RateID, Group, FeeCode, FeeName, FeeType, Currency, DefaultAmount
- Enabled

## T_FeeDraft
- DraftID, CaseID, ClientID
- Type (MVP1: GENERIC/APPLY_FEE/OA_FEE optional)
- Currency
- Status: OPEN/LOCKED
- Totals: TotalGov, TotalService, TotalMisc, Amount
- CreatedAt/By, UpdatedAt/By

## T_FeeItem
- FeeItemID, DraftID, CaseID
- FeeCode, FeeName
- FeeType (GOV/SERVICE/MISC)
- YearNo (nullable)
- Quantity (nullable), UnitPrice (nullable)
- Amount
- Remark

