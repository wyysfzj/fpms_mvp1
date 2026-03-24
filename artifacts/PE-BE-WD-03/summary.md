# PE-BE-WD-03

Status: PASS

Scope:
- `backend/app/modules/documents/api.py`
- `backend/app/modules/documents/service.py`
- `backend/tests/test_b2_reply_chain.py`

Changes:
- added shared document response builder so create/get/update all return `case_no`
- applied template-backed defaults on document update, including `need_reply`
- applied `status_restore` on reply documents when configured by the outgoing template
- preserved reply-chain auto write-off behavior while making update/create flows return FE-needed context
- expanded backend regression coverage for update-template defaults and reply-template status restore

Validation:
- `cd backend && pytest -q tests/test_b2_reply_chain.py -k 'case_no or template_defaults or status_restore'`
- `cd backend && pytest -q tests/test_b2_reply_chain.py tests/test_b3_fee_linking.py`

Notes:
- no schema change
- no document generation scope added
- this closes the remaining feasible backend document default/reply/status slice for Batch 2
