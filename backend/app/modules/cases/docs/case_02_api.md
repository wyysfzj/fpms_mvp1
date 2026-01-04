# Case APIs (MVP1)

Base path: `/api/v1/cases`

## Endpoints
1. `GET /cases`
- query params: q (free text), case_no, app_no, client_id, status, date_from, date_to
- pagination: page, page_size
- sorting: sort_by, sort_dir

2. `POST /cases`
- create NORMAL case
- validate unique CaseNo

3. `GET /cases/{case_id}`
- returns case detail with applicants/inventors/priorities

4. `PUT /cases/{case_id}`
- full edit (Formalities/Admin)

5. `POST /cases/{case_id}/limited-edit`
- limited edit whitelist fields
- permission: Case.EditLimited

6. `GET /cases/export`
- CSV export (same filters as list)

## Response conventions
- list endpoints return:
  - items[]
  - page, page_size, total

