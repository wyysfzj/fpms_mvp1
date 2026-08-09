# Story V8-FORMAT-LETTER-RENDER-CURRENT-ADOPTION

- Risk: `PROTECTED`
- Outcome: render the reviewed Row89 context through its selected real format-letter Word
  template and return exact readable bytes, output name and content hash.
- Catalog ID: `FPMS-V8-FORMAT-LETTER-RENDER-20260712-01` (ordinal `90`).
- Product commit: `ebfe28073314a5267a6e26743b5ab4d665a22e10`.

## Observable contract

The pure renderer consumes the immutable `FormatLetterContextResult`, confines its
relative template path to an existing file below `backend/storage/templates`, renders the
reviewed context through the existing DOCX renderer, and returns one readable Word file.
The output name is exactly `{case_no}-给{applicant_names_text}的邮件.docx`; the media type
is the DOCX media type and the content identity is lowercase `sha256:` over the exact
returned bytes.

Absolute, parent-traversal, out-of-template-root, missing and directory paths fail closed.
The renderer performs no database, archive, evidence, handoff, email or filesystem write.
Row89 retains the reviewed source/mapping/template identities for the separately contracted
Row91 archive operation.

## Verification and review

The exact focused archive test produced `6 failed` at the missing-module boundary before
the implementation was restored. Exact reviewed archive source bytes then produced
`6 passed`; the current Row88/89 template/context/mapping regression tranche passed `61`
tests. Scoped Ruff, format and exact two-path diff checks passed.

A broader diagnostic had one legacy failure in `test_document_template_render_context`.
Independent review reproduced it and confirmed that its stale case-create fixture omits
the already-required `fee_reduction` field, producing HTTP 422 before document rendering;
the Row90 commit changes neither that schema nor the legacy test. Independent High review
approved the exact candidate with `P0/P1/P2 = 0/0/0`.

## Non-goals and rollback

No archive/evidence/handoff persistence, email, endpoint/UI/schema/migration, alternative
template engine or second catalog row is included. Rollback reverts the product commit and
this adoption record while leaving the accepted Row88 template set and Row89 context
builder intact.
