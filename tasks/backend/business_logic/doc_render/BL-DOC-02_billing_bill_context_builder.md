# Atomic Task (v1.0)

- One task = one file = one responsibility
- No optional behavior
- Follow design docs in `docs/*.md` and project conventions in `docs/04_backend_architecture.md`
- If a task conflicts with an authoritative design doc, the design doc wins


# BL-DOC-02 — Billing: BillContextBuilder (dict context)

## Purpose
Create a deterministic context builder for Bill printing, producing a dict for docxtpl rendering.

Design references:
- `docs/00_mvp1_scope.md` (output basic Word documents (bill/task sheet) from templates)
- `docs/04_backend_architecture.md` (template context builders per output type)

## Output (EXACTLY ONE FILE)
Create ONE new file:
- `backend/app/modules/billing/doc_render_bill_context.py`

## Preconditions
- ORM models for Billing exist and are importable (Bill, BillItem, Client, etc.).
- You must inspect existing models to use correct field names.

## Required Interface (Authoritative)
Implement:

```python
class BillContextBuilder:
    def build(self, bill, bill_items, client, letter_head) -> dict:
        ...
```

Rules:
- Inputs are ORM instances (or lists) loaded by caller.
- Output is a pure-JSON-serializable dict (strings, numbers, lists, dicts).
- No DB queries inside this builder; caller passes all required objects.

## Required Context Keys (Minimum)
Return a dict containing at least:
- `bill` (dict)
- `client` (dict)
- `items` (list[dict])
- `letter_head` (dict or None)

Field mapping rule:
- Use the ORM field names to populate values.
- Include at minimum: bill id/no/date/status/amounts; item description/qty/unit_price/amount; client name/code.

## Steps
1) Create the file and implement `BillContextBuilder` per interface.
2) Implement small helper method(s) inside the same file if needed.
3) Keep imports minimal and Ruff-clean.

## Done Criteria
1) File exists and imports:
   `PYTHONPATH=backend python -c "from app.modules.billing.doc_render_bill_context import BillContextBuilder; print('OK')"`
2) `build(...)` returns a dict with keys: bill, client, items, letter_head.
