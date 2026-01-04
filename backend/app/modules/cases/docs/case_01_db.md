# Case DB Model (MVP1)

## Tables
### T_Case
Recommended MVP1 columns (subset):
- CaseID (UUID PK)
- CaseNo (varchar, unique)
- CaseType (enum; MVP1: NORMAL)
- PatentCategory (enum: INV/UM/DESIGN)
- FlowDir (enum: CN_IN/CN_OUT/CN_DOMESTIC)
- ClientID (FK)
- Title_CN, Title_EN
- AppNo (varchar, index)
- Status (enum; MVP1 subset)
- RecvDate, FilingDate, PrioDate (computed from priorities)
- PrimaryAgentID (FK -> T_User) optional
- Description (text)
- CreatedAt/By, UpdatedAt/By

### T_CaseApplicant
- ID (UUID PK)
- CaseID (FK)
- ApplicantID (FK -> T_Applicant) nullable in MVP1 if free-text
- Name (text) for free-text fallback
- IsFirst (bool) — enforce unique first applicant

### T_CaseInventor
- ID, CaseID
- Name, Country(optional), SequenceNo

### T_Priority
- ID, CaseID
- PrioNo, PrioDate, Country

## Derived fields
- On save, set `T_Case.PrioDate = MIN(T_Priority.PrioDate)` if priorities exist.

## Indexes
- Unique CaseNo
- Index AppNo, ClientID

