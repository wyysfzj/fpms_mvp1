# REPO-WINDOWS-CLONE-PATH-COMPAT-01

## Story Shape Classification

- shared_file_density: low
- prereq_dependency_density: low
- be_fe_coupling: repo-metadata-doc-only
- evidence_cost: low
- chosen_runbook: P0-single-lane-story

## Task Plan Classification

- shared_file_density: low
- prereq_dependency_density: low
- be_fe_coupling: repo-metadata-doc-only
- evidence_cost: low
- chosen_runbook: P0-single-lane-story

## Exact Closure Slice

Fix the Windows clone checkout failure caused by an invalid tracked filename in `tasks/backend/apis/`.

This closes only:

1. Rename `tasks/backend/apis/BE-APIv4-024_tasks_get_tasks_today?as=worker|supervisor.md` to a Windows-safe task filename.
2. Preserve the endpoint text `GET /tasks/today?as=worker|supervisor` inside documentation.
3. Update direct documentation references to the renamed task file.
4. Verify the tracked HEAD path list has no Windows-invalid filename characters, Windows reserved names, trailing spaces/dots, long path risks, or case-insensitive path collisions.

## Explicit Non-Closure

This task does not modify product frontend code, backend code, API behavior, database schema, migrations, seed data, permissions, Docker deployment behavior, or task acceptance semantics.

## Remaining Follow-Up Task IDs

- None

## Allowed Files

- `tasks/repo/REPO-WINDOWS-CLONE-PATH-COMPAT-01.md`
- `tasks/backend/apis/BE-APIv4-024_tasks_get_tasks_today?as=worker|supervisor.md`
- `tasks/backend/apis/BE-APIv4-024_tasks_get_tasks_today_as_worker_supervisor.md`
- `tasks/backend/apis/README.md`
- `tasks/backend/apis/PHASE3_CODEX_BATCH_GROUPED.md`
- `tasks/backend/apis/PHASE3_CODEX_BATCH_GROUPED_CLEAN.md`
- `docs/permissions_matrix.md`
- `artifacts/REPO-WINDOWS-CLONE-PATH-COMPAT-01/**`

## Verification Commands

```bash
./scripts/evidence_run.sh REPO-WINDOWS-CLONE-PATH-COMPAT-01 lint /bin/zsh -lc 'git ls-files | rg -n "BE-APIv4-024_tasks_get_tasks_today_as_worker_supervisor.md" && ! git ls-files | rg -n "BE-APIv4-024_tasks_get_tasks_today\\?as=worker\\|supervisor.md"'
```

```bash
./scripts/evidence_run.sh REPO-WINDOWS-CLONE-PATH-COMPAT-01 test /bin/zsh -lc 'python3 - <<"PY"
import subprocess
raw = subprocess.check_output(["git", "ls-files", "-z"])
paths = [p.decode("utf-8", "surrogateescape") for p in raw.split(b"\0") if p]
invalid_chars = set("<>:\"\\\\|?*")
reserved = {"CON", "PRN", "AUX", "NUL", *(f"COM{i}" for i in range(1, 10)), *(f"LPT{i}" for i in range(1, 10))}
issues = []
for path in paths:
    for part in path.split("/"):
        bad = "".join(ch for ch in part if ch in invalid_chars)
        if bad:
            issues.append((path, "invalid_chars=" + repr(bad)))
        if part.endswith(" ") or part.endswith("."):
            issues.append((path, "trailing_space_or_dot"))
        stem = part.split(".")[0].upper()
        if stem in reserved:
            issues.append((path, "reserved_name=" + stem))
        if len(part.encode("utf-8")) > 255:
            issues.append((path, "component_gt_255_bytes"))
    if len(path) > 240:
        issues.append((path, "path_len_gt_240=" + str(len(path))))
seen = {}
for path in paths:
    key = path.lower()
    if key in seen and seen[key] != path:
        issues.append((path, "case_collision_with=" + seen[key]))
    seen[key] = path
for path, reason in sorted(issues):
    print(f"{reason}\t{path}")
if issues:
    raise SystemExit(1)
print(f"Windows path compatibility scan PASS: {len(paths)} tracked paths")
PY'
```

```bash
./scripts/task_validate.sh REPO-WINDOWS-CLONE-PATH-COMPAT-01
```

## Evidence Path

- `artifacts/REPO-WINDOWS-CLONE-PATH-COMPAT-01/results.jsonl`
- `artifacts/REPO-WINDOWS-CLONE-PATH-COMPAT-01/summary.md`
- `artifacts/REPO-WINDOWS-CLONE-PATH-COMPAT-01/git/diff.patch`
- `artifacts/REPO-WINDOWS-CLONE-PATH-COMPAT-01/baseline_allowlist.diff`
- `artifacts/REPO-WINDOWS-CLONE-PATH-COMPAT-01/baseline_external_files.txt`

## Done Definition

- The invalid task filename is no longer tracked in HEAD.
- The replacement task filename is tracked and references are aligned.
- The Windows path compatibility scan passes.
- Task evidence and task gate pass.
