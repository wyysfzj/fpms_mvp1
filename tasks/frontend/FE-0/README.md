# FE‑0 Prompts — How to Use

## Run Order
1) `FE-0-00_AI-EOS_PROMPT.md`
2) `FE-0-01_AI-EOS_PROMPT.md`

## How to Execute
- Open the repository root in your coding agent (Gemini / Claude / other).
- Copy/paste the prompt text for the current task into the agent.
- The agent must follow AI‑EOS rules: atomic scope, strict allowlist, run gates, produce Evidence Log.
- Do NOT start the next task until the current task’s `lint/typecheck/build` gates are green and evidence is written.

## Evidence Logs
Evidence logs are written under:
- `task/frontend/FE-0/FE-0-00_evidence.md`
- `task/frontend/FE-0/FE-0-01_evidence.md`

If `task/` does not exist, the task prompts instruct the agent to create it.
