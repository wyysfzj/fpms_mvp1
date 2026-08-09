# Story V8-CASE-FEES-INSTRUCTION-UI-CURRENT-CONTRACT

- Risk: `PROTECTED`
- Outcome: close catalog row `268` with explicit PAY/HOLD/ABANDON actions on real persisted
  obligations only.
- Dependency: begin after row 267 is independently accepted; both page edits stay serialized.

## Exact retry identity

One explicit action creates one `crypto.randomUUID()` idempotency key for the selected obligation
and instruction. There is no automatic retry. If transport ends without a server response, retain
that pending key and the user's explicit retry reuses it. Any received HTTP success or business
error closes the attempt; a later click creates a new key. Choosing a different instruction always
creates a new attempt. Do not derive identity from time, status, actor or obligation content.

Send only `{instruction, idempotency_key}` to the accepted adapter. Render the server result as an
independent instruction fact and never rewrite overlay status locally. Only a returned PAY fact
shows a user-clicked draft link using the returned obligation ID. Preserve all error semantics and
perform no draft/PayList/payment mutation. Run focused Playwright and scoped ESLint; the integrated
frontend typecheck is serialized once after this page successor.

No backend/adapter/permission change, inferred eligibility, automatic navigation/retry or adjacent
cleanup. Rollback reverts only the row-268 page/test change and its adoption.
