# Frontend Architecture (Vue 3)

## Structure principles
- Feature modules under `src/modules/*`
- Shared infrastructure:
  - `src/api/` (axios client, interceptors, typed API helpers)
  - `src/router/` (routes + guards)
  - `src/store/` (Pinia root)
  - `src/layout/` (layout shell)
  - `src/components/` (shared components)
  - `src/utils/`

## Auth & route guard
- Store token in memory + localStorage (MVP1)
- Guard routes by required permissions (from `/auth/me` payload)

## UI library
- Element Plus
- Use:
  - `ElTable` for list pages with pagination
  - `ElForm` for CRUD
  - `ElTabs` for case detail tabs

## Type strategy
- Prefer generating TS types from OpenAPI (future script included)
- In MVP1, keep a thin hand-written `types.ts` to avoid blocking.

