# POSTENH Codex 6-Agent Team Runbook

## 1) Support Check (Current Codex)

### Supported
- Multi-agent execution via `spawn_agent` / `send_input` / `wait`.
- Parallel execution with multiple `worker` agents.
- Specialized analysis with `explorer` agents.
- Long-running wait handling with `awaiter` agents.

### Not Native (Handled by This Runbook)
- No native custom agent types named "PM/Architect/Tester/Reviewer".
- No mandatory built-in TeamCreate object.

Conclusion:
- Current Codex capability is **sufficient** for a 6-role team by role mapping.
- This runbook + `AGENTS.md` Section 13 provides the missing operational config.

## 2) Role Mapping (6 Roles)

| Team Role | Codex Execution Role | Scope |
|---|---|---|
| Team Lead / PM | Main thread | Task decomposition, assignment, dependency control, release decision |
| Architect / Designer | `explorer` | API contract freeze, module boundary and schema review |
| Backend Developer | `worker` | Execute backend atomic task files only |
| Frontend Developer | `worker` | Execute frontend atomic task files only |
| Tester | `worker` (+ `awaiter` when needed) | Run gates, regression checks, evidence verification |
| Reviewer | `explorer` | Independent review and acceptance sign-off |

## 3) Execution Rules (Must Follow)

1. One agent run = one task ID file only (atomic discipline).
2. Must assign exact task path from:
   - `tasks/postenhancement/backend/INDEX.md`
   - `tasks/postenhancement/frontend/INDEX.md`
3. No edits outside task allowlist.
4. Preserve existing implemented behavior; no opportunistic refactor.
5. Contract-first:
   - Architect freezes API request/response/error contract first.
   - FE/BE implement only after freeze.
6. Quality gate is blocking, not optional.

## 4) Suggested Team Topology

1. Lead creates one execution batch (wave) and task list.
2. Architect reviews selected tasks and emits contract notes.
3. Backend worker executes one backend task.
4. Frontend worker executes one frontend task (if paired).
5. Tester validates and captures evidence.
6. Reviewer performs independent review before lead marks done.

Recommended parallelism:
- Start with 2-3 implementation agents max on SQLite PoC to reduce lock/contention risk.
- Increase concurrency only when test stability is proven.

## 5) File Ownership and Handoff

- Architect ownership:
  - Contract notes in `artifacts/<WAVE>/contracts/*.md`
- Backend ownership:
  - `backend/app/**`, `backend/tests/**` within task allowlist
- Frontend ownership:
  - `frontend/src/**` within task allowlist
- Tester ownership:
  - `artifacts/<TASK-ID>/**` evidence outputs
- Reviewer ownership:
  - `artifacts/<WAVE>/review_report.md`

Handoff order:
1) Architect -> 2) BE/FE -> 3) Tester -> 4) Reviewer -> 5) Lead close.

## 6) Quality Gates (Blocking)

### Backend
- `ruff check --fix .`
- `ruff format .`
- `ruff check .`
- `pytest -q` (or task-defined targeted test set)

### Frontend
- `npm run lint`
- `npm run typecheck`
- `npm run build`

### Evidence (per task)
- `artifacts/<TASK-ID>/results.jsonl`
- `artifacts/<TASK-ID>/summary.md`
- `artifacts/<TASK-ID>/git/diff.patch`

### Acceptance Conditions
- All gates pass.
- Reviewer confirms no regression and no cross-scope edits.
- Status code, permission, response envelope, and SQLite compatibility comply with `AGENTS.md`.

## 7) Dispatch Template (Lead -> Agent)

Use this structure when assigning each task:

```md
Task ID: <TASK-ID>
Task File: <absolute-or-repo-relative-path>
Role: <Architect|Backend|Frontend|Tester|Reviewer>
Scope:
- Allowed files: ...
- Forbidden files: all others
Acceptance:
- ...
Gates:
- ...
Evidence output:
- artifacts/<TASK-ID>/...
```

## 8) Batch Launch Sequence

1. Select a small wave from task indexes (2-4 tasks).
2. Freeze contracts with Architect.
3. Spawn BE/FE workers for non-conflicting tasks.
4. Run Tester after implementation finishes.
5. Run Reviewer to audit all changed files and evidence.
6. Lead updates wave status and moves to next wave.

## 9) Non-Regression Guardrails

- Do not change DB schema unless task explicitly requires it.
- Do not modify router wiring unless task explicitly requires it.
- Keep response envelope and status code semantics unchanged.
- Keep permission checks in function parameters:
  - `_perm: None = Depends(require_perm("Title.Action"))`

## 10) Ready-to-Use Task Sources

- Backend atomic tasks:
  - `tasks/postenhancement/backend/INDEX.md`
- Frontend atomic tasks:
  - `tasks/postenhancement/frontend/INDEX.md`
- Overall enhancement context:
  - `tasks/postenhancement/POSTENH_SPEC2_ENHANCEMENT_PLAN.md`
  - `tasks/postenhancement/POSTENH_ATOMIC_BACKEND_TASKS.md`
  - `tasks/postenhancement/POSTENH_ATOMIC_FRONTEND_TASKS.md`
