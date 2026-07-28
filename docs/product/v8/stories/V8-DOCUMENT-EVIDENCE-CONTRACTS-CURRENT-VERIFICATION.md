# Story V8-DOCUMENT-EVIDENCE-CONTRACTS-CURRENT-VERIFICATION

- Risk: `PROTECTED`
- Outcome: prove on the current lean tree that the frozen document-evidence contract
  shapes remain exact and `EvidenceDerivationType` exposes exactly the seven ordinal-42
  values, with no `OA_REPLY_PREPARATION`.
- Change mode: current verification only; no product, test, ledger, disposition or review
  byte changes.
- Authority: the document/evidence lineage rules in `docs/product/v8/domain-contract.md`,
  the source-precedence rules in `docs/product/v8/source-decision-registry.md`, and the
  frozen contract in `tasks/postdemo/v8/FPMS-V8-DE-CONTRACTS-20260712-01.md`.
- Dependencies: the D1-D3 carriers are current-verified through
  `V8-CANARY-SCHEMA-SPINE-CURRENT-VERIFICATION`.

## Catalog ID

- `FPMS-V8-DE-CONTRACTS-20260712-01` (ordinal 42)

## Exact source and test paths

- `backend/app/modules/documents/evidence_contracts.py`
- `backend/tests/test_v8_document_evidence_contracts.py`

## Verification

From this worktree's `backend` directory, run:

```text
/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/.venv/bin/pytest -q tests/test_v8_document_evidence_contracts.py
/Users/cfcc/Workshop/myprojects/fpms_mvp1_blueprint_atomic/backend/.venv/bin/ruff check app/modules/documents/evidence_contracts.py tests/test_v8_document_evidence_contracts.py
```

Also prove the current source and exact test contain the same seven ordered
`EvidenceDerivationType` values, contain no `OA_REPLY_PREPARATION`, and pass exact
diff-check. The independent High reviewer reruns the same decisive checks on the exact
story commit.

## Later-hunk exclusion and supersession boundary

Archive commit `6b2ef89` adds exactly one `OA_REPLY_PREPARATION` line to the production enum
and one matching line to the expected test vocabulary. Those two lines belong to the later
OA-reply lane, whose catalog story
`FPMS-V8-DE-PREPARE-OA-REPLY-SEAM-20260712-01` is not current-verified, so they are
deliberately excluded from this ordinal-42 verification.

A future independently reviewed current-verification story for that later lane may
supersede the derivation vocabulary only through its own explicit authority, product/test
change, coverage mapping and exact commit/range. Until then, ordinal 42 remains verified
with exactly seven derivation values.

## Non-goals and rollback

No persistence, business adapter, endpoint, UI, OA-reply implementation, later-task enum
adoption, schema/migration, old taskctl/evidence mutation or Foundation claim. Rollback
removes only this story record and its later coverage-ledger mapping; current product/test
bytes remain unchanged.
