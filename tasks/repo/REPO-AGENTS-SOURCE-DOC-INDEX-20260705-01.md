# REPO-AGENTS-SOURCE-DOC-INDEX-20260705-01

## Design References

- `AGENTS.md`
- `docs/FPMS SPEC 2.0.md`
- `docs/TXX.pdf`
- `docs/postdemo/*.docx`
- `docs/postdemo/postdemo_*.md`
- `/Users/cfcc/Documents/相关问题解答.docx`

## Story Shape Classification

- `shared_file_density`: low; only repository instruction documentation is edited.
- `prereq_dependency_density`: low; no product implementation dependency.
- `be_fe_coupling`: none.
- `evidence_cost`: low; static file scans and text checks.
- `chosen_runbook`: `P0-single-lane-story`

## Exact Closure Slice

Add a source-document index to `AGENTS.md` that points future review/audit agents to the main customer documents, post-demo customer feedback files, fee scenario source, customer answer file, FPMS design/spec documents, post-demo analysis/spec/demo/design documents, and execution evidence summary locations.

## Explicit Non-Closure

Do not change product code, tests, database, seeds, API behavior, UI behavior, customer documents, design documents, or existing task/evidence from other work. Do not extract or summarize the full contents of source documents.

## Allowed Files

- `AGENTS.md`
- `tasks/repo/REPO-AGENTS-SOURCE-DOC-INDEX-20260705-01.md`
- `artifacts/REPO-AGENTS-SOURCE-DOC-INDEX-20260705-01/**`

## Verification Commands

- `rg -n "Source Document Index|docs/postdemo/相关流程操作-20260526.docx|docs/TXX.pdf|docs/FPMS SPEC 2.0.md|相关问题解答.docx" AGENTS.md`
- `git diff --check -- AGENTS.md tasks/repo/REPO-AGENTS-SOURCE-DOC-INDEX-20260705-01.md`
- `./scripts/task_validate.sh REPO-AGENTS-SOURCE-DOC-INDEX-20260705-01`

## Evidence Path

- `artifacts/REPO-AGENTS-SOURCE-DOC-INDEX-20260705-01/`

## Remaining Follow-Up Task IDs

None
