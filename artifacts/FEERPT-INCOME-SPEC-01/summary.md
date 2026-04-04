# Summary

## Commands
- `test -f docs/superpowers/specs/2026-04-04-fee-report-agent-income-design.md`
- `test -f docs/superpowers/plans/2026-04-04-fee-report-agent-income.md`
- `rg -n "T_CaseAgentSplit|primary_agent_id = 100%|total_service|agent-attributed service income" ...`

## Results
- Froze `RPT-FEE` agent-attributed service income semantics.
- Set `T_CaseAgentSplit` as primary authority and `primary_agent_id` as fallback.
- Confirmed the next implementation slice can proceed without schema change.

## Notes
- This wave does not implement any fee-report product behavior.
- `second_agent_id` remains context-only and is not an attribution source.
