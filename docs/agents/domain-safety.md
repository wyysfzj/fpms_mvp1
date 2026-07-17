# FPMS Domain Safety

These rules fail closed. Missing legal, customer, configuration, lineage, permission, or
source authority is never filled by inference.

### Rule GOV-LIFECYCLE-001 — Legal status, lifecycle, and deadline truth

Legal status, case lifecycle, filing, OA, grant, deadline, and deadline-preview behavior
must follow the approved product contract and effective source. A task may not invent a
transition, deadline, trigger, default, or legal conclusion. Unknown authority or an
unreachable transition blocks only the affected lane and requires an explicit decision.

### Rule GOV-FEE-001 — Official fee and service-receivable truth

Official fee, rate, amount, reduction, payment, late fee, service fee, and service
receivable behavior must preserve its effective source, activation decision, and
calculation provenance. Customer rate sheets are pricing/configuration sources, not
automatic current legal authority. Missing rate activation, reduction semantics, or
customer choice fails closed; estimates must not be presented as accepted obligations.

### Rule GOV-LINEAGE-001 — Document and evidence lineage

Document/evidence identity, version, derivation, review, provenance, attachment role,
submission, and archive relationships must remain explicit and reviewable. Never replace
raw evidence with a generated or promoted derivative, silently collapse versions, or
claim external submission without the required evidence.

### Rule GOV-AUTH-001 — Authentication, authorization, and permission boundaries

Protected endpoints require permission enforcement. Inject permission as a function
parameter, never inside decorator `dependencies`:

```python
_perm: None = Depends(require_perm("Title.Action"))
```

Permission codes use `Title.Action`. Authentication failures are 401; authenticated users
without permission receive 403. No task may broaden an authorization or security boundary
unless its exact HIGH contract explicitly authorizes that change.

### Rule GOV-DATA-001 — Schema, migration, seed, and destructive change safety

Schema, migration, seed, irreversible data change, and destructive operations are HIGH,
serialized work. Phase constraints and exact contracts control whether schema changes are
allowed. Migrations are forward-only where declared; do not rely on downgrade-to-base.
For a clean SQLite rebuild, remove the database and its `-wal`/`-shm` companions only when
authorized, upgrade to head, rerun the idempotent bootstrap-safe seed, and obtain a fresh
token. Seed must work when users or the Admin role do not yet exist. Never run destructive
Git or data commands without explicit authority.

### Rule GOV-SQLITE-001 — SQLite PoC compatibility and serialization

MVP1 must remain SQLite-compatible:

- Timestamp defaults use `sa.text("CURRENT_TIMESTAMP")`, not `now()`.
- Autoincrement uses `INTEGER PRIMARY KEY`; PK/FK types stay aligned. Application-generated
  UUIDs use `uuid4` and TEXT storage.
- Every connection enables `PRAGMA foreign_keys=ON`.
- Do not introduce PostgreSQL-only functions or types such as `uuid_generate_v4()`,
  `gen_random_uuid()`, `ILIKE`, `date_trunc`, `timezone`, `interval`, `JSONB`, `ARRAY`, or
  `CITEXT`; use SQLite-safe equivalents.
- Correctness must not depend on `RETURNING`; use `session.flush()` to obtain inserted IDs.
- Keep write transactions short. Tests that write SQLite or share a database run serially;
  a serialized worker waits for controller GRANT before acquiring the repository lock.

### Rule GOV-API-UI-001 — HTTP semantics, envelopes, and Simplified Chinese UI

Preserve each module's existing response envelope. GET does not require a request body.
204 has no body and no response model; return `None` or `Response(status_code=204)`. 201
returns the created resource or identifier unless the exact task says otherwise. Use 400
for explicit business validation, 401 unauthenticated, 403 forbidden, 404 not found, 409
conflict or missing configuration, and 422 FastAPI validation. The declared status code
must be compatible with the actual response body.

New or changed user-facing text is Simplified Chinese: page/menu titles, buttons, labels,
placeholders, validation/toast/error text, empty states, helper text, and dialog content.
English remains allowed for technical IDs, enum/code values, fields, protocols, paths, and
logs. Touching a page never absorbs unrelated legacy-language cleanup.

Rule-Ref: GOV-CUSTOMER-001
Rule-Ref: GOV-SCOPE-001
