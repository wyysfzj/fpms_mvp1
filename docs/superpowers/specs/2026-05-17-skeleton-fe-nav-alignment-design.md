# Skeleton FE Navigation Alignment Design

## Story Shape Classification

- shared_file_density: medium
- prereq_dependency_density: low
- be_fe_coupling: frontend automation only
- evidence_cost: medium
- chosen_runbook: P0-frontend-heavy-story

## Problem

`FPMS_Automation_Skeleton_Pack/playwright_ts` still reflects older frontend assumptions:

- Login page objects target English labels instead of the current Simplified Chinese UI labels.
- Default frontend and API URLs point to stale ports/paths.
- Task page object methods navigate to routes no longer present in the current Vue router.
- Existing route smoke proves routes render, but does not verify the product sidebar behavior added for production navigation.

## Approved Closure Slice

Align the Playwright TypeScript skeleton with the current product frontend navigation surface:

- Use current Simplified Chinese login selectors.
- Add a reusable app shell/sidebar page object for the product sidebar.
- Add one targeted product-sidebar smoke covering navigation mode tabs, group expand/collapse persistence, active group visibility, and icon-only sidebar behavior.
- Update stale Playwright defaults and task page object routes to current frontend/backend development defaults.

## Non-Closure

This design does not modify product frontend code, backend code, API contracts, testcase IDs, structured YAML/JSON assets, or business workflow behavior. It does not broaden coverage beyond the product sidebar/login/task-route alignment slice.

## Runbook

Use `P0-frontend-heavy-story` because the work is frontend automation focused, has moderate shared-file density inside the Playwright skeleton fixtures/config, low prerequisite dependency, and medium evidence cost.
