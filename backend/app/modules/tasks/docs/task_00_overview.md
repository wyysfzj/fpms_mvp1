# Tasks / Docket (MVP1)

## Purpose
Manage deadline tasks: create, query, reminders, close/reopen.

The legacy system emphasizes reminders and supervisor/worker roles.

## Tables
- T_TaskTemplate
- T_Task
- T_TaskLog

## MVP1 workflow
- Create task: set due date, internal due date, worker, supervisor
- Reminders: today reminders by worker/supervisor
- Close task: set done date; allow reopen (with log)

