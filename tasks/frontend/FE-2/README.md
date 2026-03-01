# FE‑2 AI‑EOS Prompts — Execution Guide

## Run Order
Execute prompts in numeric order:
- FE‑2‑01 ... FE‑2‑24

## Style Compliance (Strict)
- Match `case_detail.html` for layout, spacing, two-column grid, and immersive mode behavior.
- Tokens must match `fpms.css` exactly via `src/styles/variables.css`.
- No inline styles / magic numbers in Vue templates.

## Evidence Logs
Each task writes:
- `task/frontend/FE-2/FE-2-XX_evidence.md`

Do not start the next task until:
- lint/typecheck/build gates are green
- evidence log exists
