import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'
import ts from 'typescript'

const root = join(dirname(fileURLToPath(import.meta.url)), '..')
const api = readFileSync(join(root, 'src/api/documents.ts'), 'utf8')
const page = readFileSync(
  join(root, 'src/modules/documents/components/AttachmentList.vue'),
  'utf8',
)
const publicContract = readFileSync(
  join(root, 'src/api/contracts/v8_document_evidence_review.contract.ts'),
  'utf8',
)

function importFunctions(source, names) {
  const sourceFile = ts.createSourceFile(
    'documents.ts',
    source,
    ts.ScriptTarget.Latest,
    true,
    ts.ScriptKind.TS,
  )
  const declarations = sourceFile.statements.filter(
    (statement) => ts.isFunctionDeclaration(statement)
      && statement.name
      && names.includes(statement.name.text),
  )
  assert.equal(declarations.length, names.length, 'all executable contract helpers must exist')
  const compiled = ts.transpileModule(
    declarations.map((declaration) => declaration.getText(sourceFile)).join('\n'),
    { compilerOptions: { module: ts.ModuleKind.ESNext, target: ts.ScriptTarget.ES2022 } },
  ).outputText
  return import(`data:text/javascript;base64,${Buffer.from(compiled).toString('base64')}`)
}

const {
  executeEvidenceReviewCommand,
  shouldReconcileEvidenceReview,
} = await importFunctions(api, [
  'shouldReconcileEvidenceReview',
  'executeEvidenceReviewCommand',
])

assert.match(api, /http\.post<BackendEvidenceReviewResult>/)
assert.match(api, /return mapEvidenceReviewResult\(\s*response\.data/)
assert.match(api, /shouldReconcileEvidenceReview\(error\)/)
assert.match(api, /if \(!shouldReconcileEvidenceReview\(error\)\) throw error/)
assert.match(api, /attachment\.reviewer_id === expectation\.expectedReviewerId/)
assert.match(api, /attachment\.review_state === expectedReviewState/)
assert.match(api, /throw error\s*\n\s*}/)
assert.doesNotMatch(
  api,
  /await http\.post\([^;]+\)\s*\n\s*const document = await getDocument/s,
  'successful POST must not depend on a follow-up document GET',
)
assert.match(publicContract, /expectation: EvidenceReviewExpectation/)
assert.doesNotMatch(api, /expectation\?: EvidenceReviewExpectation/)

assert.equal(shouldReconcileEvidenceReview({ status: 0, code: 'UNKNOWN_ERROR' }), true)
for (const error of [
  { status: 400, code: 'BAD_REQUEST' },
  { status: 409, code: 'CONFLICT' },
  { status: 500, code: 'UNKNOWN_ERROR' },
  { status: 0, code: 'OTHER' },
  null,
]) {
  assert.equal(shouldReconcileEvidenceReview(error), false)
}

async function exercise(postResult) {
  const calls = { post: 0, read: 0 }
  const result = await executeEvidenceReviewCommand(
    async () => {
      calls.post += 1
      if (postResult instanceof Error || postResult?.throwMe) throw postResult.error ?? postResult
      return postResult
    },
    async () => {
      calls.read += 1
      return 'DURABLE'
    },
  )
  return { calls, result }
}

assert.deepEqual(await exercise('POST'), { calls: { post: 1, read: 0 }, result: 'POST' })
for (const deterministicError of [
  { status: 400, code: 'BAD_REQUEST' },
  { status: 409, code: 'CONFLICT' },
]) {
  const calls = { post: 0, read: 0 }
  await assert.rejects(
    executeEvidenceReviewCommand(
      async () => { calls.post += 1; throw deterministicError },
      async () => { calls.read += 1; return 'WRONG' },
    ),
    (error) => error === deterministicError,
  )
  assert.deepEqual(calls, { post: 1, read: 0 })
}

const unknownTransport = { status: 0, code: 'UNKNOWN_ERROR' }
assert.deepEqual(
  await exercise({ throwMe: true, error: unknownTransport }),
  { calls: { post: 1, read: 1 }, result: 'DURABLE' },
)
const failedReconciliationCalls = { post: 0, read: 0 }
await assert.rejects(
  executeEvidenceReviewCommand(
    async () => { failedReconciliationCalls.post += 1; throw unknownTransport },
    async () => { failedReconciliationCalls.read += 1; throw new Error('read failed') },
  ),
  (error) => error === unknownTransport,
)
assert.deepEqual(failedReconciliationCalls, { post: 1, read: 1 })

assert.match(page, /const reviewIntents = new Map<string, DocumentEvidenceReviewPayload>\(\)/)
assert.match(page, /const existing = reviewIntents\.get\(intentKey\)/)
assert.match(page, /if \(existing\) return existing/)
assert.match(page, /reviewIntents\.set\(intentKey, payload\)/)
assert.match(page, /expectedReviewerId: currentUserId\.value/)
assert.doesNotMatch(
  page,
  /reviewDocumentEvidence\([\s\S]*?reviewed_at: new Date\(\)/,
  'the mutation call must use the immutable review intent rather than rebuilding its timestamp',
)

console.log('document evidence review reconciliation contract OK')
