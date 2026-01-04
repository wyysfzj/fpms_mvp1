# Client Master Data (MVP1)

## Why it matters
Clients are referenced by cases and bills. The SPEC setting section highlights Client master data with addresses and contacts.

## Tables
- T_Client
- T_ClientAddress
- T_ClientContact

## Key rules
- Unique ClientCode (firm-defined)
- Support multiple addresses with flags: default billing address, default mailing address

## API
- GET `/clients` (search)
- POST `/clients`
- PUT `/clients/{id}`
- PUT `/clients/{id}/deactivate`

