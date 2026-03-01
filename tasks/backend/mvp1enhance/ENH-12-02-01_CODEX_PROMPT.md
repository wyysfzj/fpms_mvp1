# ENH-12-02-01 — CODEX PROMPT (AI‑EOS)

You are executing ONE atomic documentation task.

Task:
- Apply the changes described in `ENH-12-02-01.md`.

Hard rules:
- Modify ONLY `docs/api_usage_guide.md`
- Remove any `/auth/me` examples/sections
- Add a replacement “Token Validation” section that relies on an existing protected endpoint and explains 401 vs 403 vs 200
- Do NOT modify any backend code
