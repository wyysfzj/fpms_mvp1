# BATCH-W0-WAVE-CLOSE-AUDIT-01-READINESS-GATE

## 1. Readiness Decision

Decision: **READY for W0 P0 prerequisite close audit. NO-GO for full W0 all-case close.**

Reason: W0 contains 14 testcase IDs in skeleton data. Only the four P0 prerequisite handlers are implemented and have task evidence: `TC-W0-001`, `TC-W0-007`, `TC-W0-010`, and `TC-W0-014`. The remaining 10 W0 handlers are still skeleton and must not be silently counted as closed.

## 2. Scope

| Testcase | Priority | Topic | Handler state | Readiness |
| --- | --- | --- | --- | --- |
| `TC-W0-001` | P0 | 主数据-客户 | implemented | ready for P0 close |
| `TC-W0-002` | non-P0 | W0 backlog | skeleton | future readiness required |
| `TC-W0-003` | non-P0 | W0 backlog | skeleton | future readiness required |
| `TC-W0-004` | non-P0 | W0 backlog | skeleton | future readiness required |
| `TC-W0-005` | non-P0 | W0 backlog | skeleton | future readiness required |
| `TC-W0-006` | non-P0 | W0 backlog | skeleton | future readiness required |
| `TC-W0-007` | P0 | 业务参数-费率固定金额 | implemented | ready for P0 close |
| `TC-W0-008` | non-P0 | W0 backlog | skeleton | future readiness required |
| `TC-W0-009` | non-P0 | W0 backlog | skeleton | future readiness required |
| `TC-W0-010` | P0 | 业务参数-文档模板配置 | implemented | ready for P0 close |
| `TC-W0-011` | non-P0 | W0 backlog | skeleton | future readiness required |
| `TC-W0-012` | non-P0 | W0 backlog | skeleton | future readiness required |
| `TC-W0-013` | non-P0 | W0 backlog | skeleton | future readiness required |
| `TC-W0-014` | P0 | 权限矩阵 | implemented | ready for P0 close |

## 3. Evidence Matrix

| Testcase | Automation task | Evidence status | Real-smoke note |
| --- | --- | --- | --- |
| `TC-W0-001` | `W0-AUTO-PY-W0-CLIENT-P0-01` | PASS summary exists | original task summary recorded environment skip; close audit must provide combined real smoke |
| `TC-W0-007` | `W0-AUTO-PY-W0-FEERATE-P0-01` | PASS summary exists | task summary records real smoke with `FPMS_DB_DSN=` |
| `TC-W0-010` | `W0-AUTO-PY-W0-TEMPLATE-P0-01` | PASS summary exists | task summary records real smoke with `FPMS_DB_DSN=` |
| `TC-W0-014` | `W0-AUTO-PY-W0-PERMISSION-P0-01` | PASS summary exists | task summary records real smoke with `FPMS_DB_DSN=` and a documented role fallback |

## 4. Blocker Ledger

| Blocker ID | Scope | Type | Status | Resolution |
| --- | --- | --- | --- | --- |
| `W0-FULL-CLOSE-SKELETON-BACKLOG` | `TC-W0-002/003/004/005/006/008/009/011/012/013` | automation backlog | discovered | defer to `BATCH-W0-P1P2-COMPLETION-READINESS-GATE-01` |
| `W0-CLIENT-REAL-SMOKE-GAP` | `TC-W0-001` | evidence gap | discovered | close audit must run combined W0 P0 real smoke |
| `W0-PERM-LIMITED-ROLE-FALLBACK` | `TC-W0-014` | product/env compatibility note | documented | not blocking P0 prerequisite close; carry forward if product requires distinct Limited Agent role |

## 5. Test-Maintenance Matrix

No stale skeleton expectation needs to be changed for the W0 P0 prerequisite close slice. Existing boundary assertions for `TC-W0-008`, `TC-W0-011`, and `TC-W0-013` remain valid because those handlers are still skeleton.

## 6. Allowlist Matrix

| Task | Allowed files | Shared file risk |
| --- | --- | --- |
| `BATCH-W0-WAVE-CLOSE-AUDIT-01-READINESS-GATE` | readiness task/doc/manifest and artifacts only | none |
| `BATCH-W0-WAVE-CLOSE-AUDIT-01` | close-audit task/doc and artifacts only | none |
| `BATCH-W0-P1P2-COMPLETION-READINESS-GATE-01` | to be authored later | must scan `wave_w0.py` and W0 tests before any landing |

## 7. Real-Smoke Readiness

Backend was not running at first probe. The close audit must start backend if needed and run:

`FPMS_API_URL=http://127.0.0.1:8000/api/v1 FPMS_RUN_ID=<fresh> FPMS_DB_DSN= pytest tests/test_wave_w0.py -k "TC-W0-001 or TC-W0-007 or TC-W0-010 or TC-W0-014" -q`

The command must be treated as close-audit evidence only, not as evidence for closing the 10 remaining W0 skeleton backlog cases.

## 8. Automation Landing Readiness

W0 P0 prerequisite close audit can start now. Full W0 completion cannot start until a separate readiness gate drains the non-P0 backlog.
