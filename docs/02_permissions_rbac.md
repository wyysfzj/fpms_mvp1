# RBAC & Permission Model

## Roles (MVP1)
- Admin (系统管理员)
- Formalities (流程/案卷管理员)
- Agent (代理人/合伙人/经理 — MVP1 treat as “Agent”)
- Finance (财务)

## Permission codes (recommended)
Use `MODULE.ACTION` string codes to keep API enforcement stable.

### Core
- `Auth.Login`
- `User.Manage`
- `Role.Manage`

### Case
- `Case.Read`
- `Case.Create`
- `Case.Edit`
- `Case.EditLimited` (aligns with SPEC permission `CaseEditLimited`)
- `Case.Export`

### Document
- `Doc.Read`
- `Doc.Create`
- `Doc.Edit`
- `Doc.Attach`
- `Doc.TemplateRender`

### Task (Docket)
- `Task.Read`
- `Task.Create`
- `Task.Edit`
- `Task.Close` (mark done)
- `Task.Reopen`
- `Task.Assign` (change worker/supervisor)

### Fee
- `Fee.Read`
- `Fee.Draft.Create`
- `Fee.Draft.Edit`
- `Fee.Rate.Manage`

### Billing
- `Bill.Read`
- `Bill.CreateFromDraft`
- `Bill.CreateManual`
- `Bill.Print`
- `Payment.Create`
- `Payment.Offset`

### Settings
- `Client.Manage`
- `Template.Manage`
- `SystemParam.Manage`

## Menu-to-role matrix (MVP1)
| Menu / Page | Admin | Formalities | Agent | Finance |
|---|---:|---:|---:|---:|
| Dashboard | R | R | R | R |
| Cases: list/search | R/W | R/W | R | R |
| Cases: create | R/W | R/W | - | - |
| Case detail: full edit | R/W | R/W | - | - |
| Case detail: limited edit | R/W | R | R/W (limited) | - |
| Documents: register | R/W | R/W | R/W (OUT only) | R |
| Documents: attachments | R/W | R/W | R/W | R |
| Tasks: list | R/W | R/W | R/W | R |
| Tasks: create/edit | R/W | R/W | R/W | - |
| Fees: drafts | R/W | R/W | R | R |
| Fees: rates | R/W | R/W | - | - |
| Billing: bills | R/W | R | R | R/W |
| Billing: payments/offset | R/W | - | - | R/W |
| Settings: clients | R/W | R/W | R | R |
| Settings: users/roles | R/W | - | - | - |
| Settings: templates/system | R/W | - | - | - |

Legend: R = read, W = write, "-" = no access.

## API enforcement
- Every endpoint declares required permission(s) via `Depends(require_perm("..."))`.
- Frontend hides menus by permission, but **backend is source of truth**.

