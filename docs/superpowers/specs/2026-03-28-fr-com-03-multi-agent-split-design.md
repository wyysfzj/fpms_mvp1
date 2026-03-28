# FR-COM-03 Multi-Agent Split Design

**Feature:** `US-COM-03 / FR-COM-03` 多代理人提成分成

**Source of truth:**
- `docs/FPMS SPEC 2.0.md`
- `docs/FPMS_SPEC2_2nd_Review.md`

## Story Shape Classification

- shared_file_density: `high`
- prereq_dependency_density: `high`
- be_fe_coupling: `chained (BE -> FE)`
- evidence_cost: `high`

## Chosen Runbook

- chosen_runbook: `P0-prereq-heavy-story`

**Problem Statement**

`FR-COM-03` requires the system to support multi-agent commission allocation based on case-level assignment rules, not just a single `agent_id` per commission row. The required behavior is to maintain one current effective split scheme on a case, calculate the total commission first, and then split that total into separate commission records per participating internal agent.

**Approved Assumptions**

- The split source of truth is the case-level current effective configuration.
- Split members are internal users only, limited to users with agent-related roles or permissions.
- Each split line contains at least `agent_id`, `role`, and `share_ratio`.
- `share_ratio` values must sum to `100%` before save.
- Commission calculation order is: compute total commission first, then split by ratio.
- Amounts are rounded to 2 decimal places; the last member absorbs the rounding remainder.
- If no split configuration exists, fallback remains single-agent and defaults to `Case.PrimaryAgentID`.
- Recompute is allowed only for commissions that are not settled and are not already attached to settlement lines.
- Settled commissions, or commissions already included in settlement lines, are frozen.
- Each split result remains an independent commission record and continues through the existing settlement and report flow.
- Frontend maintenance must be provided on the case page.

**In Scope**

- Add durable case-level multi-agent split persistence.
- Add case-page UI for maintaining split members, roles, and ratios.
- Update commission generation to emit one commission row per split agent.
- Update recompute behavior for non-frozen commissions to use the current split configuration.
- Keep settlement/report compatibility by preserving one-agent-per-commission semantics.
- Preserve backward compatibility for single-agent cases.

**Explicit Non-Scope**

- Historical versioning of split configurations.
- Export/report redesign beyond existing settlement/report compatibility.
- New settlement grouping model.
- External participants or non-agent users in split allocation.
- Recomputing settled commissions or commissions already attached to settlement lines.
- A separate split-configuration center outside the case page.

**Recommended Design**

Use a normalized case split detail table plus the existing one-agent-per-commission model.

- Add case split detail persistence under the case domain.
- Keep `Commission` rows single-agent and independent.
- Let the commission service consume the current case split configuration when generating or recomputing commission records.
- Do not store the split definition as weakly structured JSON on the case.

**Compatibility Assessment**

- SQLite PoC compatibility: feasible.
- Phase 3 / 3.1 / 3.5 no-schema constraints: not feasible without prerequisite work.
- Shared ownership impact: high across `cases`, `commission`, related schemas, and case frontend.

**Design Conclusion**

- `不可直接实现，必须先新增 prerequisite task(s)`
- If execution is restricted to no-schema Phase 3 / 3.1 / 3.5 work, then:
  - `受 Phase / schema / shared-ownership 约束，当前应标记 BLOCKED`

**Story-Level Closure Slice**

- Case-level current effective multi-agent split can be maintained and used to generate or recompute separate per-agent commission records that continue through the existing settlement/report flow.

**Story-Level Non-Closure Boundary**

- Does not close split history versioning, export enhancement, new settlement models, external-participant allocation, or recompute of frozen commissions.
