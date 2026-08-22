# V8 Final Close Current Implementation Plan

**Goal:** Close Row283 with one independently reviewed full-program verification and run
the lean release gate last.

**Architecture:** Freeze an exact Final contract, run each broad lane once, record the
results in a Git-tracked report/story, bind an exact candidate fingerprint, independently
review one sole-ledger patch, then run the release milestone as the final command.

### Task 1: Freeze latest-wins Row283 contract and RED

Files:

- modify `tasks/postdemo/v8/FPMS-V8-FINAL-CLOSE-20260712-01.md`;
- create `backend/tests/test_v8_final_close_contract.py`;
- create `scripts/run_v8_paylist_boundary_live_isolated.py`.

Require the exact report/story, all Rows1–282 current, Row283 pre-adoption PENDING, exact
command matrix, configuration residual and release-last state. Freeze `ROW283_BASE` as the
full SHA of HEAD after this approved design/plan commit. Run
`cd backend && .venv/bin/pytest -q tests/test_v8_final_close_contract.py`; RED must be only
the missing report/story. Then implement the runner with dynamic backend/frontend ports,
temporary SQLite/storage, exact CORS origin, `FPMS_BASE_URL`, `FPMS_API_URL`,
`FPMS_BACKEND_PYTHON`, Vite `--strictPort`, child-owned readiness and awaited TERM/KILL
cleanup. Run `python3 -m py_compile scripts/run_v8_paylist_boundary_live_isolated.py` and
`cd backend && .venv/bin/ruff check tests/test_v8_final_close_contract.py ../scripts/run_v8_paylist_boundary_live_isolated.py`.
Commit task+RED+runner before any broad lane.

### Task 2: Run the complete Final matrix once

With no overlapping SQLite/milestone/build/Playwright process, create mode-`0700`
`/tmp/fpms-v8-final-close-20260813`, capture each lane's stdout/stderr into one named log,
and run in this order:

1. isolated temporary SQLite clean upgrade and seed, preserving the repository database:
   `tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT; cd backend && FPMS_ENV=test DATABASE_URL="sqlite:///$tmp/final.db" STORAGE_DIR="$tmp/storage" .venv/bin/alembic upgrade head && FPMS_ENV=test DATABASE_URL="sqlite:///$tmp/final.db" STORAGE_DIR="$tmp/storage" .venv/bin/python scripts/seed_dev.py`;
2. `cd backend && .venv/bin/ruff check .`;
3. `cd backend && .venv/bin/pytest -q`;
4. `cd frontend && npm run lint && npm run typecheck && npm run build`;
5. lifecycle real E2E through `python3 scripts/run_v8_lifecycle_overlay_live_isolated.py`;
6. PayList real E2E through `python3 scripts/run_v8_paylist_boundary_live_isolated.py`;
7. `cd FPMS_Automation_Skeleton_Pack/playwright_ts && npx playwright test src/tests/v8-official-workbook-live.spec.ts --workers=1`.

After each lane compute `shasum -a 256` over its log. Scan every log for private-key blocks,
live credential/token forms and high-confidence PRC ID/mobile patterns using the focused
contract's scanner; output only lane/rule/count and never the matched text. Any failure or
finding stops the Final close and becomes an atomic corrective story. Do not edit product or
tests inside Row283.

### Task 3: Materialize Final report/story and candidate

Files:

- create `docs/product/v8/final-close-report.json`;
- create `docs/product/v8/stories/V8-FINAL-CLOSE.md`;
- update only the focused contract as needed.

Record every exact lane ID, literal command, `PASS`, return code, observed count/summary,
warnings and SHA-256 log digest. The focused contract validates those fields and performs a
content-aware scan over only the tracked report/story and, once present, reviewer receipt;
it also verifies/scans every report-named external log. It rejects private-key blocks, live
credential/token forms and high-confidence PRC personal ID/mobile patterns while reporting
only rule/path/count, never the matched value. Freeze and validate these current milestone
inputs through their exact ledger stories and tracked paths:

- Foundation story `docs/product/v8/stories/V8-FOUNDATION-CLOSE-CURRENT-ADOPTION.md` and
  review `docs/product/v8/reviews/V8-FOUNDATION-CLOSE-CURRENT-ADOPTION.md`;
- Full story `docs/product/v8/stories/V8-FULL-CAPABILITY-MANIFEST-CLOSE.md` and review
  `docs/product/v8/reviews/V8-FULL-CAPABILITY-MANIFEST-CURRENT-ADOPTION.md`.

Run
focused pytest, scoped Ruff/format on the focused contract and PayList runner, report JSON
parse and exact diff checks. Commit only the five candidate paths. Set
`ROW283_CANDIDATE=$(git rev-parse HEAD)` after the commit. Candidate range is
`$ROW283_BASE..$ROW283_CANDIDATE`; fingerprint paths are exactly:

- `tasks/postdemo/v8/FPMS-V8-FINAL-CLOSE-20260712-01.md`;
- `backend/tests/test_v8_final_close_contract.py`;
- `scripts/run_v8_paylist_boundary_live_isolated.py`;
- `docs/product/v8/final-close-report.json`;
- `docs/product/v8/stories/V8-FINAL-CLOSE.md`.

### Task 4: Bind sole ledger patch and Final milestone

Compute the five-path tree fingerprint with
`ROW283_CANDIDATE="$ROW283_CANDIDATE" python3 -c 'import importlib.util,os,pathlib; root=pathlib.Path("."); spec=importlib.util.spec_from_file_location("checker",root/"scripts/v8_lean_coverage_check.py"); module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module); print(module.compute_tree_fingerprint(root,os.environ["ROW283_CANDIDATE"],["tasks/postdemo/v8/FPMS-V8-FINAL-CLOSE-20260712-01.md","backend/tests/test_v8_final_close_contract.py","scripts/run_v8_paylist_boundary_live_isolated.py","docs/product/v8/final-close-report.json","docs/product/v8/stories/V8-FINAL-CLOSE.md"]))'`.
The report must not contain candidate SHA/tree fields, avoiding self-reference. Change only Row283 to `CURRENT_VERIFIED` and append
`V8-FINAL-CLOSE-CURRENT-ADOPTION`; preserve every prior row/story and configuration
residual. Run:

```text
cd backend && .venv/bin/pytest -q tests/test_v8_final_close_contract.py
cd backend && .venv/bin/ruff check tests/test_v8_final_close_contract.py
python3 -m json.tool docs/product/v8/final-close-report.json >/dev/null
python3 -m json.tool docs/product/v8/coverage-ledger.json >/dev/null
python3 scripts/v8_lean_coverage_check.py --milestone final --integration-sha <candidate-sha>
git diff --check "$ROW283_BASE".."$ROW283_CANDIDATE" -- tasks/postdemo/v8/FPMS-V8-FINAL-CLOSE-20260712-01.md backend/tests/test_v8_final_close_contract.py scripts/run_v8_paylist_boundary_live_isolated.py docs/product/v8/final-close-report.json docs/product/v8/stories/V8-FINAL-CLOSE.md
git diff --check -- docs/product/v8/coverage-ledger.json
git diff --binary -- docs/product/v8/coverage-ledger.json | shasum -a 256
```

The focused contract uses HEAD's ledger to distinguish: candidate (HEAD/worktree PENDING),
pre-review (HEAD PENDING/worktree exact Row283 patch), and adopted (HEAD CURRENT). Receipt
is optional only in the first two states; external logs are mandatory and scanned until the
reviewer commits its receipt. Hash the unstaged sole-ledger patch and keep it uncommitted.

### Task 5: Independent review, adoption and release-last

Reviewer audits exact cumulative candidate plus ledger patch and full report, including
the exact log-digest/count evidence for the expensive matrix. On APPROVED
P0/P1/P2 `0/0/0`, reviewer creates untracked
`docs/product/v8/reviews/V8-FINAL-CLOSE-CURRENT-ADOPTION.md`, runs the focused contract so
the receipt and still-present logs are scanned, then commits only that receipt. The receipt
binds candidate SHA, five-path tree, sole-ledger patch SHA, each lane log digest/scan result
and 0/0/0. Controller verifies the receipt commit, removes only
`/tmp/fpms-v8-final-close-20260813`, then commits only the reviewed ledger. In adopted state
the focused contract requires the tracked/reachable exact receipt and accepts absent logs
only through that binding. Run focused Final contract, then lean `final`; the final program command is:

```text
python3 scripts/v8_lean_coverage_check.py --milestone release --integration-sha HEAD
```

After that command, report the result without changing files or running another command.
The expensive broad matrix is never rerun; focused/Ruff/JSON/lean-final are the only
repeatable candidate/review/post-adoption checks.
