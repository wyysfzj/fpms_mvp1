# ENH-00-00 Bootstrap Pack (FPMS-aligned)

Contents:
- ENH-00-00.md: atomic task definition (aligned to your AGENTS.md)
- scripts/*.sh: reference implementations for evidence + gates
- AGENTS_PATCH_SECTION_12.md: exact text to append to AGENTS.md
- ENH-00-00_CODEX_PROMPT.md: Universal v2 prompt for agents

How to use:
1) Copy ENH-00-00.md into your tasks folder and execute it with an agent.
2) The agent should create scripts/ and artifacts/ scaffolding and append Section 12 to AGENTS.md.
3) After merge, re-run ENH-00-01 using evidence scripts:
   - ./scripts/evidence_run.sh ENH-00-01 lint (ruff commands…)
   - ./scripts/evidence_run.sh ENH-00-01 test (py_compile…)
   - ./scripts/evidence_finalize.sh ENH-00-01
   - ./scripts/task_validate.sh ENH-00-01
