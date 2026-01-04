# Task DB Model (MVP1)

## T_TaskTemplate (minimal)
- TaskTemplateID, Code, Name
- Default offset rules (optional MVP1)

## T_Task
- TaskID, CaseID, TaskTemplateID
- Title/ContentSummary
- OfficialDate (optional), InternalDueDate, DueDate
- WorkerID, SupervisorID
- Reminder1/2/3 (optional MVP1), RemindDaily (bool)
- Status: OPEN/DONE/CANCELLED
- DoneAt/By
- CreatedAt/By, UpdatedAt/By

## T_TaskLog
- LogID, TaskID, Action, FromStatus, ToStatus, Remark, CreatedAt/By

