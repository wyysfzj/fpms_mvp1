# Batch FC6 — Findings

## Pre-existing Implementation
- ActionCenter.vue already shows client_name (line 27)
- EnrichedTask already has client_name field (line 49)
- fetchDashboardKpi() already uses .total from paginated responses

## fetchEnrichedTasks() — unnecessary extra API call
- Lines 119-131: Fetches ALL cases (page_size=200) just to resolve client_names
- Since B6, task responses include client_name directly → can simplify
- Remove getCases call, use task.client_name directly

## fetchPipelineKpi() — unallocated payments metric is wrong
- Line 83: Sums ALL payment amounts, not just unallocated
- Comment on line 81-82 acknowledges this limitation
- Backend doesn't expose offset status on payment list
- Can't fully fix without backend changes — document as known limitation

## Bugs Found
(none yet)
