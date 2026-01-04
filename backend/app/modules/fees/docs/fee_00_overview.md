# Fees (MVP1)

## Purpose
Record fee drafts (what should be charged) with items split by GOV/SERVICE/MISC.

Legacy manual highlights “once input, reused in downstream (bill, receipt...)”.

## Tables
- T_FeeRate (config)
- T_FeeDraft
- T_FeeItem

## MVP1 workflow
- Create draft for a case
- Add items (fee code, type, amount, year no optional)
- Lock draft before billing generation

