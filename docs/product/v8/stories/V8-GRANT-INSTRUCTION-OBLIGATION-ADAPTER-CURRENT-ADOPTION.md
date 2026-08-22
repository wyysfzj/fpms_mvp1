# Story V8-GRANT-INSTRUCTION-OBLIGATION-ADAPTER-CURRENT-ADOPTION

- Risk: `PROTECTED`
- Outcome: bind an explicitly named grant-fee task and confirmed grant-notice activity to
  their exact grant-year annuity obligation, then record one explicit client instruction
  through the accepted generic writer.
- Catalog ID: `FPMS-V8-GRANT-INSTRUCTION-OBLIGATION-ADAPTER-20260712-01`
  (ordinal `119`).
- Product commit: `95561455a797b0d7f261d9739be5ce23ebdd9cbb`.

## Observable contract

The exact typed service command requires the grant task, source activity, `PAY`/`HOLD`/
`ABANDON` instruction, authenticated actor identity and caller-supplied idempotency key.
It loads only the named task/activity, revalidates the accepted Row130 confirmed grant
notice, canonical source/evidence snapshot, correction lineage and complete grant-year
annuity obligation projection, and requires unique recognition cardinality.

After all fail-closed checks, it delegates exactly once to the accepted Row107 generic fee
instruction writer and returns the unchanged obligation/instruction/activity/key/reuse
facts. Exact and historical replay remain supported; key drift, new-key same-state,
missing, ambiguous, stale or divergent lineage fails without an adapter-owned write.
Caller transaction, rollback and the generic writer's savepoint/race behavior remain
unchanged.

## Verification and review

The contract-complete focused RED produced `41` expected missing-interface failures.
Minimum implementation produced `41 passed`; the exact adapter, grant-year obligation,
generic instruction and grant-notice lifecycle tranche passed `176` tests. Scoped Ruff,
format and exact diff checks passed.

Independent High review reran the same `41` focused and `176` regression tests, verified
the complete contract and approved the exact commit with `P0/P1/P2 = 0/0/0`.

## Non-goals and rollback

The legacy PUT/batch endpoints remain unchanged because their current payloads do not carry
actor or idempotency authority. No API/schema/migration, rate/reduction, automatic draft,
legacy task mutation, PayList, payment, document/evidence or lifecycle/legal-state change
is included. Rollback reverts only the exact product commit and this adoption record while
retaining Rows107 and 130.
