# Story V8-FILING-XML-DERIVATION-GATE-CURRENT-ADOPTION

- Risk: `PROTECTED`
- Integration parent: `7fbbc4b40f2a74ffe1b75ae4e398864b0268e09b`
- Catalog row: `64`,
  `FPMS-V8-FILING-XML-DERIVATION-GATE-20260712-01`.
- Outcome: current-adopt the frozen filing XML lineage gate so an external XML package
  derives only from the current independently reviewed full filing Word, and submitted
  XML derives only through that exact external XML parent.
- Authority: the frozen row-64 task contract and its current-verified full-Word readiness
  and evidence-derivation prerequisites.

## Exact behavior and paths

The pure read-only policy accepts exactly two paths:

1. `FILING_FULL_WORD -> EXTERNAL_XML_PACKAGE` through one `FORMAT_CONVERSION` edge.
2. `FILING_FULL_WORD -> EXTERNAL_XML_PACKAGE -> SUBMITTED_XML` through ordered
   `FORMAT_CONVERSION` and `EXTERNAL_SUBMISSION` edges.

Every supplied object must be exact, nonblank, same-case and same-lineage. The source Word
must be current, approved and independently reviewed. Path shape, edge identity and
derivation type fail closed with the frozen exact error codes and precedence.

Story-owned paths:

- `backend/app/modules/documents/evidence_policy.py`
- `backend/tests/test_v8_filing_xml_derivation_gate.py`
- `docs/product/v8/cutover-dirty-path-disposition.json`
- this story card.

The focused public test is adopted byte-for-byte from the independently accepted archive
checkpoint with SHA-256
`744040f53e450aeb72b46a13735a7ec5e5220d5a362368875d07c05c372cd051`.
The product change is limited to the filing XML error members and public callable; all
other evidence policies remain untouched.

## Verification, non-goals and rollback

Run the exact focused test as RED and GREEN, then affected full-Word/evidence-policy
regressions and scoped Ruff. An independent High reviewer reviews the exact commit and
reruns the decisive focused test.

The adopted public matrix produced the contract-complete RED with `196 failed`; the
decisive failures were the missing six-argument callable and the missing path-shape/type
error members. After the minimum policy port, the exact focused GREEN passed `196` tests.
The combined focused plus noncopyable-OA-appendix regression passed `347` tests. Scoped
Ruff and diff checks passed. The disposition transfer leaves `474` unique paths, assigns
the two story paths here, and has SHA-256
`cf07860fa1604abdb30a7de71e23f418c86581373384d8da34e9fa271251ac05`.

No XML generation, packaging, external submission write, evidence mutation, API, UI,
schema, migration, fee behavior, unrelated document policy or adjacent refactor is
included. Rollback removes only this policy slice, focused test, exact disposition transfer
and story card.
