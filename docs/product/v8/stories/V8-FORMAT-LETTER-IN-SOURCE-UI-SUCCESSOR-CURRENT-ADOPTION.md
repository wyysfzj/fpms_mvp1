# Story V8-FORMAT-LETTER-IN-SOURCE-UI-SUCCESSOR-CURRENT-ADOPTION

- Risk: `PROTECTED`
- Outcome: generate and archive one format-letter Word from an eligible incoming official
  document through an authenticated, idempotent HTTP command, then display its actual
  evidence version and full content hash in the incoming-document UI.
- Superseded catalog ID: `FPMS-V8-FORMAT-LETTER-IN-SOURCE-UI-20260712-01`
  (ordinal `92`).
- Successor contract:
  `docs/product/v8/stories/V8-FORMAT-LETTER-IN-SOURCE-UI-SUCCESSOR-CONTRACT.md`.
- Product commit: `d41d5e3388e93766746f5bb47fc9a4934f0149cc`.

## Observable contract

The authenticated `OfficialWorkflow.Update` endpoint accepts the incoming source, one
required operation UUID, an optional contact override and normalized remark. A new
operation composes the accepted Row89 context, Row90 renderer and Row91 archive service,
commits once in the API and returns the exact created handoff, evidence version, generated
document, attachment, filename, evidence role/state/review/current flags and full
`sha256:<64 lowercase hex>` content hash.

An exact operation replay validates the complete committed source, contact, remark,
mapping/template, handoff, attachment, evidence, derivation and managed-file identity and
returns the stored result without rerendering or writing. Drift, ambiguity, partial state,
stale/unreviewed input, invalid provenance or missing managed bytes fails closed. A commit
failure rolls back and compensates only the newly created Row91 file under its exact
device/inode identity; compensation identity drift preserves the stronger failure.

The incoming-document panel exposes the Simplified Chinese `生成并归档格式函` action only
for normalized `IN`, retains one operation UUID across a failed retry, and after success
shows the authoritative evidence version number and exact full hash. `OUT` documents never
show that action or archive identity. The frontend does not infer evidence, legal status,
deadline, fee, contact, template or eligibility facts.

## Verification and review

The contract-complete backend RED produced `2 failed, 2 passed` before the missing vertical
was implemented. Focused backend GREEN and the exact Row89/90/91 plus handoff regression
tranche passed `83` tests. Targeted Playwright passed `2` tests with one worker. Scoped Ruff,
Ruff format check, exact-file ESLint and exact diff checks passed. Current `vue-tsc` reports
the same seven pre-existing diagnostic identities; the successor added none.

Independent High review of the exact ten-file product commit reran the decisive backend
and browser checks, examined permission, transaction, replay, compensation, lineage and UI
boundaries, and approved it with `P0/P1/P2 = 0/0/0`.

## Non-goals and rollback

No email send, evidence approval/finalization, download endpoint, background job, bulk
generation, alternate template/contact policy, legacy handoff migration, schema/migration,
second-page capability or adjacent cleanup is included. Rollback reverts only the exact
product commit and this adoption record while retaining accepted Rows89, 90 and 91.
