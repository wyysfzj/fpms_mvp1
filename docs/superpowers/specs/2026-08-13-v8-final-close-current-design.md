# V8 Final Close — Current C3 Design

## Decision

Close Row283 as the audit-only Final/Release story after all other 282 catalog rows have
current ledger dispositions. Replace the obsolete taskctl/artifact release path with the
current lean checker. Product source, schemas, migrations, seeds, customer registries and
tests remain read-only.

The close runs the complete milestone verification exactly once on the candidate tree:

- isolated temporary SQLite `alembic upgrade head` and `seed_dev.py`;
- full backend Ruff and pytest;
- frontend lint, typecheck and production build;
- the three named current real-path Playwright specs: lifecycle overlay, PayList boundary
  and official workbook;
- a content-aware scan of only the Git-tracked Final report, close story and reviewer
  receipt, rejecting private-key material, live credential/token forms and high-confidence
  personal identifiers without echoing any matched value;
- focused Final contract and lean `final` milestone validation.

The durable Final report records exact lane IDs, literal commands, exit codes, counts,
known warnings and a SHA-256 digest of each captured command log. Logs use a mode-`0700`
temporary directory outside the repository and the report never embeds command output that
could expose secrets or PII. A
failed lane creates a separate corrective story; Row283 itself never repairs product or
weakens tests. The expensive migration/backend/frontend/E2E matrix runs once; lightweight
focused/JSON/Ruff/lean-final checks may be repeated at candidate, review and adoption.

## Configuration residual

`DG-PAYMENT-WORKBOOK:GLOBAL` and `DG-SERVICE-RATE-VERSION:GLOBAL` remain customer-owned
`CONFIG_REQUIRED` inputs with source decisions `PENDING`. Production remains `409 / NO
WRITE`, TEST_ONLY stays isolated and no production activation is claimed. This is a truthful
release residual and does not block capability or audit closure.

## Candidate and adoption

The candidate owns only the Row283 task card, focused Final contract, PayList isolated
runner, Git-tracked Final report and close story. Its exact Git tree fingerprint and the
sole coverage-ledger patch are independently reviewed. The ledger patch changes only
Row283 to `CURRENT_VERIFIED` and appends one PROTECTED story; every prior row/story remains
identical.

The focused Final contract is the C3 section 12.4 release-input consumer. It parses the
exact report and requires each matrix lane's literal command, `PASS`, zero exit code,
observed count/summary, warnings and log digest. It verifies all Rows1–282 are current,
configuration residuals are exact and, when adoption exists, Row283's candidate/tree and
reviewer receipt exist in the integration tree. The receipt must bind the candidate SHA,
tree fingerprint, reviewed sole-ledger patch hash and P0/P1/P2 `0/0/0`. The same contract
verifies the exact tracked Foundation story/review
`V8-FOUNDATION-CLOSE-CURRENT-ADOPTION.md` and Full story/review
`V8-FULL-CAPABILITY-MANIFEST-CLOSE.md` /
`V8-FULL-CAPABILITY-MANIFEST-CURRENT-ADOPTION.md`, including current reachable ledger
references. It scans report/story/receipt and every captured log without printing a matching
value, and verifies each log digest before the reviewer reads it.

The contract distinguishes three states from `git show HEAD:docs/product/v8/coverage-ledger.json`:

1. candidate: HEAD/worktree Row283 are PENDING, receipt absent, logs required;
2. pre-review: HEAD remains PENDING, worktree is the exact sole Row283 adoption patch,
   receipt may be untracked, logs remain required and are scanned;
3. adopted: HEAD Row283 is CURRENT_VERIFIED and the receipt must be tracked/reachable and
   exact; logs may be absent only because that receipt binds their digests and zero-finding
   scan.

An independent High reviewer audits the complete results and exact candidate, reruns only
the focused contract, scoped Ruff, JSON parse, lean `final` milestone and diff checks, then
creates the receipt untracked, reruns the focused receipt scan, and commits only the receipt
on P0/P1/P2 `0/0/0`. Before ledger adoption the controller removes the temporary log
directory, then separately commits only the reviewed ledger patch. The report deliberately
contains no candidate SHA or self-referential tree hash; those identities live only in the
receipt and ledger story.

## Release-last

After adoption, rerun the focused contract and lean `final` milestone. The final command of
the program is exactly:

```text
python3 scripts/v8_lean_coverage_check.py --milestone release --integration-sha HEAD
```

No subsequent byte change, test, build, Playwright run or release command is permitted in
this close. A release failure is reported without mutating the reviewed tree.
