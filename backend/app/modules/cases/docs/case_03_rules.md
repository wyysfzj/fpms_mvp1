# Case Business Rules (MVP1)

## Validation rules (from SPEC patterns)
- CaseNo must be unique
- CaseType/PatentCategory/FlowDir must be a valid combination
- Applicant list:
  - at least 1 applicant
  - exactly 1 first applicant

## Limited edit (Agent)
- Only allow editing whitelist:
  - Title_CN, Title_EN
  - SpecPages, DrawPages, ClaimCount, ClaimPages, ManuscriptWords (optional MVP1)
  - inventors list
  - limited remarks/description
- Must NOT trigger:
  - status transitions
  - task generation
  - fee draft generation

