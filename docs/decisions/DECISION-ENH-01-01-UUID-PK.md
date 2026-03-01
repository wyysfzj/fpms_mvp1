# DECISION-ENH-01-01-UUID-PK

Date: 2026-01-04  
Status: Approved (Owner decision)  
Scope: FPMS MVP1 Enhancement (Wave 1 — RBAC foundation)

## Decision
For `T_RolePerm` (ENH-01-01), we will use a **UUID primary key stored as TEXT** (e.g., `String(36)`), generated in application code (`uuid4()`), **despite** the SQLite PoC preference for Integer autoincrement PKs.

This aligns with the authoritative task specification for ENH-01-01 and remains SQLite-compatible.

## Rationale
1. **Consistency with existing domain**: The project already uses UUID-as-string identifiers in core domain models (e.g., `Case.id = str(uuid4())`), so using UUID here avoids mixed identifier strategies.
2. **SQLite compatibility preserved**: AGENTS.md allows UUID PKs when generated in application code and stored as TEXT. We are not relying on autoincrement or RETURNING behavior.
3. **Low write frequency**: RBAC mapping tables have low write volume, so UUID performance considerations are not material for MVP1.
4. **Avoid migration churn**: Forcing Integer PKs would require redefining the ENH-01-01 contract and could cause additional alignment work in ENH-01-02 migration and related FK typing.

## Rules / Constraints (Authoritative for this decision)
- UUID must be generated in application code (`uuid4()`), stored as TEXT (`String(36)` or equivalent).
- Do NOT rely on SQLite autoincrement semantics for this table.
- FK typing must match referenced PK type **exactly**:
  - `T_RolePerm.role_id` type MUST match `T_Role.id` type.
- Timestamp defaults must remain SQLite-safe (`CURRENT_TIMESTAMP` via `sa.text("CURRENT_TIMESTAMP")` or equivalent existing pattern in repo).
- This decision applies **only** to `T_RolePerm` unless extended by a new decision document.

## Impact
- ENH-01-01 model definition must implement UUID/TEXT PK accordingly.
- ENH-01-02 migration must create TEXT PK and aligned FK types.

## Verification
- `POST /api/v1/cases` invalid body returns 422 (already fixed by ENH-00-12) — unrelated but confirms validation flow stability.
- For RBAC: migrations and model compile cleanly under SQLite and ruff.

## Alternatives Considered
### A) Force Integer autoincrement PK
Rejected because it conflicts with the ENH-01-01 task spec and increases migration churn and type-mismatch risk.

