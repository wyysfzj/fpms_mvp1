# RBSEL-GATE-01 — Add lightweight runbook-plan validator

- Source spec: `docs/superpowers/specs/2026-03-24-runbook-selection-and-story-shape-design.md`
- Type: `validation script`
- Status: `Executable`

## Closure Slice

- Exact closure slice: create a lightweight CLI script that validates required runbook-selection headings in a plan document and exits non-zero when they are missing.
- Explicit non-closure: does not edit `AGENTS.md`, does not create the repo-local skill, and does not create or modify the reusable plan template beyond consuming it in verification.
- Remaining follow-up task ids: `RBSEL-QA-01`

## Allowlist

- `scripts/validate_plan_runbook.py`

## Verification

- `python3 scripts/validate_plan_runbook.py docs/superpowers/plans/2026-03-24-runbook-selection-and-story-shape-implementation.md`
- `python3 - <<'PY'\nfrom pathlib import Path\nfrom tempfile import TemporaryDirectory\nimport subprocess\nimport sys\nwith TemporaryDirectory() as td:\n    p = Path(td) / 'bad.md'\n    p.write_text('# Bad Plan\\n\\n## Story Shape\\n')\n    result = subprocess.run([sys.executable, 'scripts/validate_plan_runbook.py', str(p)], capture_output=True, text=True)\n    assert result.returncode != 0\n    assert 'Missing required sections' in result.stdout or 'Missing required sections' in result.stderr\nPY`

## Evidence

- `artifacts/RBSEL-GATE-01/results.jsonl`
- `artifacts/RBSEL-GATE-01/summary.md`
- `artifacts/RBSEL-GATE-01/git/diff.patch`

