# CASEFLD-BE-CRUD-01 Summary

## Commands
- `ruff check backend/app/modules/cases/api.py backend/app/modules/cases/schemas.py backend/app/modules/cases/service.py backend/tests/test_case_missing_fields_crud.py`
- `cd backend && pytest -q tests/test_case_missing_fields_crud.py`

## Results
- 补齐了 `CaseCreate / CaseUpdateFull / CaseDetail` 对 15 个缺失字段的 contract。
- `create / update / detail` 现在可以回写并回读这些字段。
- 新增了 `to_country` 涉外校验与 `doc_address_id / bill_address_id` 客户归属校验。
- CRUD 红测转绿，目标测试全部通过。

## Notes
- 仅关闭 `create / update / detail` CRUD slice。
- 未触碰 `CaseList`、搜索筛选、导入导出或 downstream 联动。
