# Case Maintenance (MVP1)

## Goal
Provide the “Case master file” that drives downstream modules.

## MVP1 supported CaseType
- NORMAL only (domestic/inbound/outbound)

Other case types (PCT_INTL/PCT_NATIONAL/INVALIDATION/LITIGATION/CONSULTING/SEARCH) are parked as future.

## Core fields (high-level)
- CaseNo (unique)
- Titles (CN/EN)
- ClientID (FK to T_Client)
- FlowDir, PatentCategory, Status
- Key dates: RecvDate, FilingDate (optional at creation)

## Sub tables (MVP1)
- Applicants (T_CaseApplicant)
- Inventors (T_CaseInventor)
- Priority claims (T_Priority)

## MVP1 highlights
- Case list/search + export
- Limited edit view for Agents (whitelist fields only)

