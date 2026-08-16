# FPMS Local Demo ABC Fast-Track Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver the approved local ABC journey from runtime input through one customer bill,
payment and offset, while preventing planning work from reopening deferred production scope.

**Architecture:** Work serially from the clean `d1df69e649f5d28cb192d347d25c8d775663aaf2`
baseline. Each atomic story must produce a runnable result before the next story starts. Only a
startup failure, unreachable ABC step, wrong-object write, duplicate write, incorrect amount or
database/UI inconsistency may block the demo lane; every other audit item remains deferred.

**Tech Stack:** Python 3.11, FastAPI, SQLAlchemy, SQLite, Vue 3, TypeScript and Playwright.

---

## Execution controls

- `shared_file_density`: high across the complete journey, low for the first story.
- `prereq_dependency_density`: high across the complete journey, low for the first story.
- `be_fe_coupling`: high across the complete journey, none for the first story.
- `evidence_cost`: targeted per story; no broad or release gate.
- `chosen_runbook`: `P0-prereq-heavy-story`, executed serially with WIP = 1.
- Replanning triggers are limited to a startup/unreachable-path blocker, a wrong or duplicate
  business write, an incorrect amount, or a changed customer/runtime input.
- Each execution interval must produce a failing test, a passing target check, a runnable API/UI
  increment or a precise blocker. Documentation-only activity is not implementation progress.

## Frozen sequence

1. Clean declared-dependency import.
2. Fail-closed local runtime-bundle preflight before database/ports.
3. Fresh run-ID-owned SQLite/storage bootstrap.
4. One runtime SERVICE item to one locked draft.
5. One locked draft to one idempotent AR bill.
6. One customer bank payment and one atomic offset.
7. Strict finance UI adapters and authoritative CNY display.
8. Two fresh visible-browser rehearsals and independent demo-scope acceptance.

Security remediation, production/PostgreSQL deployment, official fees, official templates,
PayList, bad debt, dunning, commission and product release remain explicit non-closure.

### Task 1: Declare the application-start dependency

**Task card:** `tasks/postdemo/FPMS-DEMO-ABC-LOCAL-BOOT-DEPENDENCY-20260816-01.md`

**Files:**

- Modify: `backend/pyproject.toml`
- Modify: `backend/fpms_api.egg-info/requires.txt`
- Create: `backend/tests/test_demo_declared_runtime_dependencies.py`

- [ ] **Step 1: Write the failing metadata test**

```python
from pathlib import Path
import tomllib


def test_openpyxl_is_a_declared_runtime_dependency() -> None:
    dependencies = tomllib.loads(Path("pyproject.toml").read_text())["project"]["dependencies"]
    assert "openpyxl>=3.1.5,<4" in dependencies
    assert "openpyxl>=3.1.5,<4" in Path("fpms_api.egg-info/requires.txt").read_text().splitlines()
```

- [ ] **Step 2: Run the target test and observe the missing-dependency failure**

Run: `cd backend && python3 -m pytest tests/test_demo_declared_runtime_dependencies.py -q`

Expected: FAIL because neither package metadata file declares `openpyxl`.

- [ ] **Step 3: Add the minimum runtime declaration**

Add exactly `openpyxl>=3.1.5,<4` to both tracked dependency representations. Do not touch import
sites, application behavior, Docker files, seed logic or workbook code.

- [ ] **Step 4: Run target checks and a clean-install import smoke**

Run the target test and scoped Ruff check. Then create a temporary virtual environment, install
the backend from its declared metadata and run `python -c 'import app.main'` from outside the
repository import path. Expected: every command returns 0.

- [ ] **Step 5: Validate evidence and commit the atomic story**

Evidence must pass under
`artifacts/FPMS-DEMO-ABC-LOCAL-BOOT-DEPENDENCY-20260816-01/`. Commit only the task allowlist. The
next story may begin only after independent review of this PROTECTED story.
