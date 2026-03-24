# A4 Batch — Findings

## Discoveries
- SystemParam model uses integer PK (not UUID mixin) — simpler table
- `param_key` is not marked unique in the model column def, but upsert logic uses it as logical key
- `conftest.py` uses session-scoped DB with seeded admin user

## Bugs Found & Fixed
- `clients/api.py` DELETE endpoints (lines 242, 310) had implicit response models from `-> None` return annotation. With newer FastAPI, this causes `AssertionError: Status code 204 must not have a response body`. Fixed by adding `response_model=None`.

## Deviations
- None
