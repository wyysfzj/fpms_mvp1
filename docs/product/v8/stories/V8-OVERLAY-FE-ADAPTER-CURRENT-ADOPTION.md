# Story V8-OVERLAY-FE-ADAPTER-CURRENT-ADOPTION

- Risk: `NORMAL`
- Contract commit: `22cf2b0`.
- Product/contract-probe commit: `6678955`.
- Catalog ID: `FPMS-V8-OVERLAY-FE-ADAPTER-20260712-01` (ordinal `266`).
- Outcome: provide the lossless typed frontend transport for lifecycle overlay pages.

The adapter defines the exact unions and fifteen nested public DTOs, explicitly maps the private
snake_case wire shape, preserves readonly ordering/nullability and keeps dates and all decimals as
strings. Requests send the three frozen query fields and return mapped response data without
catching, retrying, coercing, caching or deduplicating. The composite gate key retains all 29
identities despite repeated legacy codes.

The compile RED proved the missing modules. GREEN removed every lifecycle-overlay diagnostic;
scoped ESLint and diff checks passed. Repository typecheck still reports exactly seven captured
legacy diagnostics in four unrelated files, with no new adapter diagnostic. Independent High
review approved P0/P1/P2 all zero.

No UI, endpoint policy, numeric conversion, cache, shared-type refactor or adjacent API change is
included. Rollback removes the three files and this adoption.
