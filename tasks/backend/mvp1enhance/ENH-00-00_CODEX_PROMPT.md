# Universal Atomic Execution Prompt (v2) — ENH-00-00 (FPMS-aligned)

You are a coding agent executing **one and only one** atomic task.

## Task ID
ENH-00-00

## Goal
Bootstrap EOS Evidence & Gates (scripts/ + artifacts/) and append Section 12 to AGENTS.md so strict-scope tasks (e.g., ENH-00-01) can pass gates without violating atomic code scope.

## Role Declaration (Must Follow)
You are acting strictly as a **bounded executor**, not a designer, reviewer, or improver.

## Hard Rules
- Execute ONLY ENH-00-00.
- Modify ONLY allowlisted paths: scripts/, artifacts/, .gitignore, AGENTS.md.
- Do NOT touch backend/ or any application code.
- Do NOT add dependencies.
- Keep changes minimal and exactly per ENH-00-00.md.

## Required Steps
1) Implement the scripts exactly as specified.
2) Add artifacts/.gitkeep and ignore artifacts/ in .gitignore.
3) Append the provided Section 12 text to AGENTS.md verbatim.
4) chmod +x scripts/*.sh
5) Run the validation commands in ENH-00-00.md

## Evidence
- Provide git diff (only allowlisted paths)
- Provide artifacts/ENH-00-00 outputs + summary.md
