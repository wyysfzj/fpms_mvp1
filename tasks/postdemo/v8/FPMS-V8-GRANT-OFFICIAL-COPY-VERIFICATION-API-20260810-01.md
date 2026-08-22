# FPMS-V8-GRANT-OFFICIAL-COPY-VERIFICATION-API-20260810-01

Status: FROZEN / READY FOR IMPLEMENTATION
Risk class: `PROTECTED`
Runbook: `P0-single-lane-story`

## Authority and prerequisite

- Scheme A customer source SHA-256
  `e6cfd648f1d366e27bde3f74310f00033a6db60ce55d850d2e668764745faace`.
- Accepted official-copy verification carrier and service, ending at commit `65518df`.

## Exact closure

Add one synchronous authenticated endpoint:

`POST /documents/evidence-versions/{evidence_version_id}/grant-official-copy-events`

It requires `Doc.Edit`, injects the authenticated actual user as `actor_id`, captures one server
UTC-naive action time, delegates exactly once to `record_grant_official_copy_event`, and commits
once. It returns the exact result body with `201` for `CREATED` and `200` for `REUSED`.

Create strict schemas in
`backend/app/modules/documents/grant_official_copy_verification_schemas.py`:

```python
class GrantOfficialCopyEventIn(BaseModel):
    evidence_scope: GrantEvidenceScope
    event_type: GrantOfficialCopyEventType
    reason: str
    original_reference: str | None
    expected_current_event_id: str | None
    idempotency_key: str


class GrantOfficialCopyEventOut(BaseModel):
    event_id: str
    evidence_version_id: str
    evidence_scope: GrantEvidenceScope
    event_type: GrantOfficialCopyEventType
    source_config_id: str
    source_record_id: str
    role_config_id: str
    event_snapshot_hash: str
    current_identity_key: str | None
    disposition: GrantOfficialCopyDisposition
```

Input uses `extra="forbid"`; strings are nonblank, trimmed and NUL-free. Reason is at most 4096,
reference at most 512, idempotency at most 128. `expected_current_event_id`, when present, is an
exact canonical UUID. The schema enforces the service shape: ACQUIRED requires reference and null
expected current; both verification stages require null reference and a canonical expected current.
The evidence path parameter is a FastAPI UUID and is passed as canonical lowercase text.

The client cannot supply actor or action time. A service or commit exception rolls back and is
re-raised through the existing error envelope. Authentication/permission stays 401/403; malformed
path/body stays 422; service validation/conflict stays 400/409.

## Non-closure

No GET/list/update/delete endpoint, no router rewiring, UI, source/role configuration, schema,
migration, candidate ingestion/review, evidence/document mutation, legal status/lifecycle/deadline,
fee or payment behavior. Do not duplicate service rules in the route beyond strict request shape.

## Allowed files

- this task file;
- `backend/app/modules/documents/grant_official_copy_verification_schemas.py`;
- `backend/app/modules/documents/api.py`;
- `backend/tests/test_v8_grant_official_copy_verification_api.py`.

`backend/app/modules/documents/api.py` is shared and must be edited/verified serially.

## Frozen acceptance matrix

1. Exact route, method, response model and `Doc.Edit` dependency exist; no additional route exists.
2. CREATED returns 201, REUSED returns 200, with exact response body.
3. The service receives path evidence ID, strict enums/body, authenticated user and one server time;
   client actor/time and extra fields are 422.
4. Missing/invalid permission, malformed UUID or stage shape, service 400/409 and unexpected/commit
   failures preserve existing HTTP/error/rollback semantics.
5. Route owns only transaction completion and creates no direct query or product/domain write.

## Verification

- Focused RED/GREEN pytest for the named API test.
- Focused service and affected document-router permission regressions.
- Scoped Ruff and exact three-path diff-check.
- One independent High reviewer reviews the exact implementation range and reruns decisive checks.
- PASS requires `P0/P1/P2 = 0/0/0`; no Full or release gate belongs here.
