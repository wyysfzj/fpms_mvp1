# Sidebar Group Collapse Design

## Story Shape Classification

- shared_file_density: medium
- prereq_dependency_density: low
- be_fe_coupling: frontend-only
- evidence_cost: medium
- chosen_runbook: P0-frontend-heavy-story

## Goal

Improve the product sidebar by allowing each large navigation function group to collapse vertically, reducing visual clutter without hiding the user's current location.

## Approved Interaction

- Expanded sidebar shows each navigation group as a clickable section header.
- The section header shows the group name, optional description, visible item count, and a chevron state indicator.
- `工作导航` defaults to expanded groups so the product's end-to-end workflow remains immediately visible.
- `模块导航` defaults to a compact map: `我的工作` and the active route's group are expanded; other groups are collapsed until opened.
- User changes are persisted in `localStorage` by navigation mode and group key.
- The active route's group is always expanded even if the saved state says collapsed.
- When the whole sidebar is collapsed to icon-only width, group headers are hidden and icon links remain available.

## Architecture

Keep this as a frontend-only sidebar shell change. The existing product menu definitions, routes, labels, and permission filtering remain the source of truth. `SidebarNav.vue` decides whether a visible group is collapsed, while `ui.ts` owns persisted UI state.

## Components

- `frontend/src/stores/ui.ts`
  - Add persisted sidebar group collapse state keyed by `NavMode` and group key.
  - Expose set/toggle helpers.
- `frontend/src/components/nav/SidebarNav.vue`
  - Render group headers as buttons in expanded-sidebar mode.
  - Hide group items when the group is collapsed.
  - Keep the active group expanded.
- `frontend/src/styles/layout.css`
  - Style group headers, item containers, chevrons, counts, and collapsed-group spacing.

## Data Flow

1. The sidebar filters `PRODUCT_NAV_GROUPS` by active navigation mode and permissions.
2. It computes the active item and active group from the current route.
3. For each group, it reads the saved collapse state from the UI store.
4. Default fallback is mode-specific: work groups expanded; module groups collapsed except `我的工作` and the active group.
5. User clicks update the UI store and persist to `localStorage`.

## Error Handling

If stored collapse state is missing or malformed, the store falls back to an empty object and default behavior. No backend errors are introduced because this is UI-only.

## Testing

- Static checks: ESLint, TypeScript, build.
- Browser checks:
  - Work mode shows expanded end-to-end groups by default.
  - Module mode starts compact and can expand a group.
  - Reload preserves a user-opened group.
  - Active group stays expanded.
  - Whole-sidebar collapse still shows icon links.

## Non-Goals

- No backend, API, permission, route, database, or login changes.
- No changes to menu labels or business term mapping.
- No command palette, global search, mobile drawer, or page content redesign.
- No new navigation routes or business workflows.

## Review Note

The formal spec-review subagent loop is not used here because the active platform instructions only permit subagents when the user explicitly asks for subagent work.
