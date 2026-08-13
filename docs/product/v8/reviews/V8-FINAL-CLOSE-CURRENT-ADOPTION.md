# V8 Final Close Current Adoption Review

Verdict: APPROVED

P0: 0
P1: 0
P2: 0

P0/P1/P2: `0/0/0`

- Review class: Independent High / PROTECTED / Final
- Candidate base: `2c426f17a288f762a27bf77f9c2de9b93133d242`
- Candidate SHA: `512486b80c1cb2f0c5fe1d725cc7c8e8dd965516`
- Candidate range: `2c426f17a288f762a27bf77f9c2de9b93133d242..512486b80c1cb2f0c5fe1d725cc7c8e8dd965516`
- Exact five-path tree fingerprint:
  `34b632e7b96d9869ce9cb38229ccbfdd5e18fac8e4248bff79af9e273cf438b4`
- Ledger patch SHA-256: `bfdea80c80805ce16eb239a5001796f484e9d17a942a190ccf456fdcc2e1e1b6`

## Candidate and milestone audit

The candidate owns exactly the frozen five paths: the Row283 task card, focused Final
contract, isolated PayList runner, Final report and Final story. Their candidate-tree
fingerprint matches the reviewed value. No product, schema, migration, seed, customer
registry or release-gate behavior is included in this candidate.

The tracked Foundation and Full milestone stories and their independent review receipts
exist, are current and are reachable from the candidate. Rows 1–282 have current
dispositions. The reviewed ledger patch changes only Row283 from `PENDING` to
`CURRENT_VERIFIED`, preserves all prior rows and stories byte-for-byte, and appends exactly
one `V8-FINAL-CLOSE-CURRENT-ADOPTION` story bound to this candidate and fingerprint.

Production inputs `DG-PAYMENT-WORKBOOK:GLOBAL` and
`DG-SERVICE-RATE-VERSION:GLOBAL` remain `CONFIG_REQUIRED`; their source decisions remain
`PENDING`; production remains `409 / NO WRITE`; TEST_ONLY remains isolated;
`production_activation_claimed` and `release_claimed` remain false. This review does not
claim production configuration or release completion.

## Final matrix evidence

The mode-`0700` external log directory contained all seven required logs. Each report
command, PASS status, zero return code, observed count or summary, warnings and log digest
matched the captured evidence. The focused content-aware scan returned zero findings for
every log and for the tracked report/story.

| Lane | Observed result | Log SHA-256 |
| --- | --- | --- |
| clean SQLite upgrade and seed | upgrade to head and development seed completed | `1035d8cde370caea32402c4ea8a66764242ff98f49af2f52eca2c83ec5748e9f` |
| backend Ruff | all checks passed | `d71d2c39cb6b6e0bf858263c9842819a8527d458645355fc8ce99bd5f0e36c6e` |
| backend pytest | 6158 passed, 33 skipped, 114 subtests passed in 1797.46s | `55223d12311422f8c81b8a39e4af7fb4f53a55220c783ce602851d29ad86f2c9` |
| frontend quality | ESLint, vue-tsc and production build passed | `381b502f1417574e0377f532731c8440358270c11f46cf4577912d4181c0f34c` |
| lifecycle real E2E | 1 passed | `8ec7fac9869aaac1de37df4da065f8dddc580ea2dd01877919629ddbed7f6e34` |
| PayList real E2E | 1 passed | `d260eb233474b3d7e6b02b5b87343b51af7073b8421425d8057b61f5f6d386ac` |
| official workbook real E2E | 1 passed | `e3348c9cdbf91bba1ec82ef9726967bc1b4a2710f891d4ce862e304bffc4d8aa` |

## Fresh independent verification

- Focused Final contract: `3 passed, 2 warnings in 1.53s`.
- Scoped Ruff: passed with only the recorded inherited configuration deprecation warning.
- Final report and coverage-ledger JSON parsing: passed.
- Lean `final` milestone: passed for the exact candidate SHA.
- Candidate and ledger diff checks: passed.
- Candidate tree and sole-ledger patch hashes: matched.
- Sensitive-content scan: zero findings across seven logs, report, story and this receipt.

This approval is limited to the exact candidate and reviewed sole-ledger patch. The
implementer did not approve its own work. The controller must remove only the external log
directory and commit the reviewed ledger separately, then perform the adopted focused and
lean-Final checks. The release checker remains the final program command and was not run by
this reviewer.
