# FPMS V8 Domain Contract

These product invariants fail closed. Missing legal, customer, configuration, lineage,
permission, data or source authority is never filled by inference.

## Legal status, lifecycle and deadlines

Legal status, case lifecycle, filing, OA, grant, deadline and deadline-preview behavior
must follow the approved product contract and effective source. Never invent a transition,
deadline, trigger, default or legal conclusion. Unknown authority or an unreachable
transition blocks only the affected lane and requires an explicit decision.

The lifecycle lane is the central case truth. Document/evidence and official-fee/service
receivable lanes may explain or trigger a reviewed lifecycle event, but cannot silently
write or infer the central legal state.

## Official fees and service receivables

Official fee, rate, amount, reduction, payment, late fee, service fee and service
receivable behavior must preserve its effective source, activation decision and
calculation provenance. Customer rate sheets are pricing/configuration sources, not
automatic current legal authority. Missing rate activation, reduction semantics or
customer choice fails closed. Estimates must never be presented as accepted obligations.

An official obligation, internal payment list, official payment workbook, payment
acceptance and official receipt are distinct states and evidence objects. Do not collapse
them into one paid/unpaid flag. Service receivables remain distinct from official fees.

## Document and evidence lineage

Document/evidence identity, version, derivation, review, provenance, attachment role,
submission and archive relationships remain explicit and reviewable. Never replace raw
evidence with a generated or promoted derivative, silently collapse versions, or claim
external submission without the required evidence.

Generated Word/XML/output, its source version, review state, external-submission package
and receipt must be linked by durable lineage. Ambiguous type, version, currentness,
cardinality or predecessor evidence fails closed.

## Lifecycle warning and conflict lineage

An overlay warning is a read-only projection of a durable lifecycle activity, customer-decision
result or source classification. It never creates, confirms or changes a legal state, lifecycle
event, decision gate or fee fact. Activity conflict codes that are expected to survive a request
must be stored as explicit child facts of that exact activity; the overlay must not reconstruct
them from free text, mutable case state or test-only payload keys.

Activity-local warnings preserve activity identity and conflict-code multiplicity. Top-level
warnings aggregate the current page's activity warnings followed by the complete decision-gate
snapshot warnings, preserving source order and provenance without deduplication. A
`HISTORICAL` or `INTERNAL_ONLY` gate is reference-only and never activation-ready. Missing or
corrupt conflict lineage fails closed rather than returning a partial or inferred overlay.

## Authentication, authorization and permission

Protected endpoints enforce permission. Inject permission as a function parameter:

```python
_perm: None = Depends(require_perm("Title.Action"))
```

Never place the permission dependency only inside decorator `dependencies`. Permission
codes use `Title.Action`. Authentication failures are 401; authenticated users without
permission receive 403. No story may broaden an authorization or security boundary unless
its exact `PROTECTED` contract explicitly authorizes that change.

## Schema, migration, seed and destructive changes

Schema, migration, seed, irreversible data change and destructive operations are
`PROTECTED` and serialized. Migrations are forward-only where declared; do not rely on
downgrade-to-base. A clean SQLite rebuild may remove the database and `-wal`/`-shm`
companions only when explicitly authorized, then upgrade to head, rerun the idempotent
bootstrap-safe seed and obtain a fresh token. Seed must work before users or Admin exist.

Never run destructive Git or data commands without explicit user authority. Migration
tests and shared database verification run serially.

## SQLite compatibility

- Timestamp defaults use `sa.text("CURRENT_TIMESTAMP")`, not `now()`.
- Autoincrement uses `INTEGER PRIMARY KEY`; PK/FK types remain aligned.
- Application UUIDs use `uuid4` with TEXT storage.
- Every connection enables `PRAGMA foreign_keys=ON`.
- Do not introduce PostgreSQL-only functions or types such as `uuid_generate_v4()`,
  `gen_random_uuid()`, `ILIKE`, `date_trunc`, `timezone`, `interval`, `JSONB`, `ARRAY` or
  `CITEXT`.
- Correctness must not depend on `RETURNING`; use `session.flush()` for inserted IDs.
- Keep writes short. SQLite-writing tests and shared database use are serialized.

## HTTP and UI contracts

Preserve each module's response envelope. GET has no required request body. 204 has no
body or response model. 201 returns the created resource or identifier unless the exact
story says otherwise. Use 400 for explicit business validation, 401 unauthenticated, 403
forbidden, 404 not found, 409 conflict/missing configuration, and 422 FastAPI validation.
Declared status and actual body must agree.

New or changed user-facing text is Simplified Chinese: page/menu titles, buttons, labels,
placeholders, validation/toast/error text, empty states, helper text and dialog content.
English remains valid for technical IDs, enum/code values, fields, protocols, paths and
logs. Touching a page never absorbs unrelated legacy-language cleanup.
