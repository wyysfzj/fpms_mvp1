# Task APIs (MVP1)

Base: `/api/v1/tasks`

- GET /tasks (filters: status, due date range, worker, supervisor, case)
- POST /tasks
- GET /tasks/{id}
- PUT /tasks/{id}
- POST /tasks/{id}/close
- POST /tasks/{id}/reopen
- POST /tasks/{id}/cancel
- GET /tasks/today?as=worker|supervisor

