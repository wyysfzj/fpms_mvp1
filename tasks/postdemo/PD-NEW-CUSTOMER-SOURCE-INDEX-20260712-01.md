# PD-NEW-CUSTOMER-SOURCE-INDEX-20260712-01

## Design References

- `AGENTS.md`
- `docs/postdemo/标准费率.XLS`
- `docs/postdemo/补充缴费信息模板.xlsm`
- `docs/postdemo/相关问题解答.docx`
- `docs/postdemo/文件样例及模版/**`
- `http://www.tianyueip.com/product/612`

## Story Shape Classification

- `shared_file_density`: low; only `AGENTS.md` and task evidence are writable.
- `prereq_dependency_density`: high; later review tasks depend on a verified customer-source inventory.
- `be_fe_coupling`: none; source registration is documentation-only.
- `evidence_cost`: high; legacy Word, PDF, spreadsheet, macro-enabled template, and website sources require inspection.
- `chosen_runbook`: `P0-prereq-heavy-story`

## Exact Closure Slice

Update the `AGENTS.md` source-document index so the newly supplied customer files and fee websites are durable review inputs, and create a task-local source ledger that records file type, relevant business content, authority classification, and any unresolved provenance or interpretation issue.

## Explicit Non-Closure

Do not change an audit conclusion, customer clarification question, product design, backend, frontend, database, migrations, seed data, tests, or customer source files. Do not claim that a customer-provided rate or template is an official legal source without verified provenance.

## Allowed Files

- `AGENTS.md`
- `tasks/postdemo/PD-NEW-CUSTOMER-SOURCE-INDEX-20260712-01.md`
- `artifacts/PD-NEW-CUSTOMER-SOURCE-INDEX-20260712-01/**`

## Verification Commands

- `rg -n "标准费率|补充缴费信息模板|相关问题解答|文件样例及模版|tianyueip.com/product/612|集成电路布图设计" AGENTS.md`
- `test -s artifacts/PD-NEW-CUSTOMER-SOURCE-INDEX-20260712-01/analysis/source_ledger.md`
- `git diff --check -- AGENTS.md tasks/postdemo/PD-NEW-CUSTOMER-SOURCE-INDEX-20260712-01.md`
- `./scripts/task_validate.sh PD-NEW-CUSTOMER-SOURCE-INDEX-20260712-01`

## Evidence Path

- `artifacts/PD-NEW-CUSTOMER-SOURCE-INDEX-20260712-01/`

## Done Definition

- Every newly supplied source family is indexed.
- The official fee webpage and customer Tianyue webpage are distinguished.
- Sample/template files are not treated as automatically executable templates.
- Required evidence and dirty-baseline artifacts exist and the task gate passes.

## Remaining Follow-Up Task IDs

- `PD-NEW-CUSTOMER-FEE-SOURCE-REAUDIT-20260712-01`

