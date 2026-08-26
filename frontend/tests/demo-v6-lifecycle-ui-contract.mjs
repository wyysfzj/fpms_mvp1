import assert from 'node:assert/strict'
import { existsSync, readFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'
import ts from 'typescript'

const frontendRoot = join(dirname(fileURLToPath(import.meta.url)), '..')
const read = (path) => readFileSync(join(frontendRoot, path), 'utf8')
const filingPage = read('src/modules/cases/pages/FilingPreparation.vue')
const documentPage = read('src/modules/documents/pages/DocumentDetail.vue')
const oaPage = read('src/modules/documents/pages/OAReplyPackage.vue')
const receiptPanel = read('src/modules/officialWorkflows/components/ReceiptArchivePanel.vue')
const lifecyclePath = join(frontendRoot, 'src/modules/documents/components/DocumentLifecycleEvidenceActions.vue')
const lifecyclePanel = existsSync(lifecyclePath) ? readFileSync(lifecyclePath, 'utf8') : ''
const documentsApi = read('src/api/documents.ts')
const officialApi = read('src/api/officialWorkflows.ts')

assert.match(filingPage, /记录人工递交完成/)
assert.match(filingPage, /submissionForm\.occurredAt/)
assert.match(filingPage, /submissionForm\.note/)
assert.match(filingPage, /operation_code:\s*'EXTERNAL_SUBMISSION_RECORDED'/)
assert.match(documentPage, /<DocumentLifecycleEvidenceActions/)
assert.equal(documentPage.match(/<DocumentLifecycleEvidenceActions/g)?.length, 1)
for (const label of ['记录受理通知', '开始初步审查', '记录初审通过', '记录公布通知', '开始实质审查']) {
  assert.match(lifecyclePanel, new RegExp(label))
}
assert.match(oaPage, /答复文书/)
assert.match(oaPage, /linkReviewedOaReplyDocument/)
assert.match(receiptPanel, /回执文件/)
assert.match(receiptPanel, /createReviewedOfficialWorkPackageReceipt/)
for (const source of [filingPage, lifecyclePanel, oaPage, receiptPanel]) {
  assert.doesNotMatch(source, /<el-input[^>]+(?:attachmentId|documentId|internalId|附件ID|文档ID)/i)
}

function importFunctions(source, names, prelude = '') {
  const sourceFile = ts.createSourceFile('contract.ts', source, ts.ScriptTarget.Latest, true, ts.ScriptKind.TS)
  const declarations = sourceFile.statements.filter(
    (statement) => ts.isFunctionDeclaration(statement) && statement.name && names.includes(statement.name.text),
  )
  assert.equal(declarations.length, names.length, `missing executable helpers: ${names.join(', ')}`)
  const compiled = ts.transpileModule(
    `${prelude}\n${declarations.map((declaration) => declaration.getText(sourceFile)).join('\n')}`,
    { compilerOptions: { module: ts.ModuleKind.ESNext, target: ts.ScriptTarget.ES2022 } },
  ).outputText
  return import(`data:text/javascript;base64,${Buffer.from(compiled).toString('base64')}#${Math.random()}`)
}

const httpCalls = []
let rejectedError = null
globalThis.__ordinal04Http = {
  async post(url, payload) {
    httpCalls.push({ url, payload })
    if (rejectedError) throw rejectedError
    return { data: { url, ...payload } }
  },
}
const documents = await importFunctions(
  documentsApi,
  [
    'selectReviewedEvidenceOptions',
    'selectReviewedReplyDocumentOptions',
    'selectReviewedReceiptEvidenceOptions',
    'recordDocumentLifecycleEvidence',
  ],
  'const http = globalThis.__ordinal04Http',
)
const official = await importFunctions(
  officialApi,
  [
    'linkOaReplyDocument',
    'linkReviewedOaReplyDocument',
    'createOfficialWorkPackageReceipt',
    'createReviewedOfficialWorkPackageReceipt',
  ],
  'const http = globalThis.__ordinal04Http',
)

const hashA = `sha256:${'a'.repeat(64)}`
const hashB = `sha256:${'b'.repeat(64)}`
const approvedAttachment = (overrides = {}) => ({
  id: 'attachment-approved', filename: '受理通知书.pdf', file_size: 12, created_at: '2026-08-02',
  document_id: 'document-acceptance', official_file_role: 'OFFICIAL_NOTICE_PDF',
  evidence_version_id: 'evidence-approved', content_hash: hashA, role: 'ACCEPTANCE_NOTICE',
  review_state: 'APPROVED', is_current: true, is_final: true, ...overrides,
})
const caseDocuments = [
  { id: 'document-acceptance', case_id: 'case-a', title: '受理通知书', direction: 'IN', attachments: [approvedAttachment()] },
  { id: 'document-unreviewed', case_id: 'case-a', title: '未复核', direction: 'IN', attachments: [approvedAttachment({ id: 'pending', review_state: 'PENDING' })] },
  { id: 'document-stale', case_id: 'case-a', title: '旧版本', direction: 'IN', attachments: [approvedAttachment({ id: 'stale', is_current: false })] },
  { id: 'document-drift', case_id: 'case-a', title: '摘要漂移', direction: 'IN', attachments: [approvedAttachment({ id: 'drift', content_hash: `sha256:${'A'.repeat(64)}` })] },
  { id: 'document-wrong-case', case_id: 'case-b', title: '他案证据', direction: 'IN', attachments: [approvedAttachment({ id: 'wrong-case' })] },
]
const evidenceOptions = documents.selectReviewedEvidenceOptions(caseDocuments, 'case-a')
assert.equal(evidenceOptions.length, 1)
assert.deepEqual(evidenceOptions[0], {
  document_id: 'document-acceptance', case_id: 'case-a', title: '受理通知书',
  attachment_id: 'attachment-approved', filename: '受理通知书.pdf', role: 'ACCEPTANCE_NOTICE',
  evidence_version_id: 'evidence-approved', content_hash: hashA,
})

const replyDocuments = [
  ...caseDocuments,
  { id: 'reply-oa1', case_id: 'case-a', title: 'OA1答复', direction: 'OUT', reply_to_id: 'oa1', attachments: [approvedAttachment({ id: 'reply-a', document_id: 'reply-oa1', filename: 'OA1答复.pdf', evidence_version_id: 'reply-evidence-a', content_hash: hashA, role: 'OA_REPLY' })] },
  { id: 'reply-oa2', case_id: 'case-a', title: 'OA2答复', direction: 'OUT', reply_to_id: 'oa2', attachments: [approvedAttachment({ id: 'reply-b', document_id: 'reply-oa2', filename: 'OA2答复.pdf', evidence_version_id: 'reply-evidence-b', content_hash: hashB, role: 'OA_REPLY' })] },
]
assert.deepEqual(
  documents.selectReviewedReplyDocumentOptions(replyDocuments, 'case-a', 'oa1').map((row) => row.document_id),
  ['reply-oa1'],
)
assert.deepEqual(
  documents.selectReviewedReplyDocumentOptions(replyDocuments, 'case-a', 'oa2').map((row) => row.document_id),
  ['reply-oa2'],
)

const time = { effective_at: '2026-08-02T10:00:00', occurred_at: null, idempotency_key: 'lifecycle-action-1' }
for (const [action, path] of [
  ['ACCEPTANCE_NOTICE', 'acceptance-notice'],
  ['PRELIMINARY_START', 'preliminary-start'],
  ['PRELIMINARY_PASS', 'preliminary-pass'],
  ['PUBLICATION_NOTICE', 'publication-notice'],
  ['SUBSTANTIVE_START', 'substantive-start'],
]) {
  await documents.recordDocumentLifecycleEvidence(action, 'case-a', evidenceOptions[0], time)
  assert.deepEqual(httpCalls.at(-1), {
    url: `/documents/document-acceptance/lifecycle/${path}`,
    payload: { evidence_version_id: 'evidence-approved', ...time },
  })
}
const beforeInvalid = httpCalls.length
await assert.rejects(
  documents.recordDocumentLifecycleEvidence('ACCEPTANCE_NOTICE', 'case-b', evidenceOptions[0], time),
  /当前案件已复核证据/,
)
assert.equal(httpCalls.length, beforeInvalid)
const backendError = { status: 409, code: 'EVIDENCE_CONFLICT' }
rejectedError = backendError
await assert.rejects(
  documents.recordDocumentLifecycleEvidence('ACCEPTANCE_NOTICE', 'case-a', evidenceOptions[0], time),
  (error) => error === backendError,
)
rejectedError = null

const replyOa1 = documents.selectReviewedReplyDocumentOptions(replyDocuments, 'case-a', 'oa1')[0]
const replyOa2 = documents.selectReviewedReplyDocumentOptions(replyDocuments, 'case-a', 'oa2')[0]
await official.linkReviewedOaReplyDocument('package-oa1', 'case-a', replyOa1)
await official.linkReviewedOaReplyDocument('package-oa2', 'case-a', replyOa2)
assert.deepEqual(httpCalls.slice(-2), [
  { url: '/official-work-packages/package-oa1/oa-reply/reply-document', payload: { reply_document_id: 'reply-oa1' } },
  { url: '/official-work-packages/package-oa2/oa-reply/reply-document', payload: { reply_document_id: 'reply-oa2' } },
])

const receiptPayload = {
  receipt_kind: 'ELECTRONIC_APPLICATION_RECEIPT', receiving_case_no: 'CNIPA-1', submitter: '陈思远',
  received_at: '2026-08-02T10:00:00', received_file_list: '申请文件', archive_status: 'ARCHIVED', note: null,
}
const receiptDocuments = [{
  id: 'receipt-document', case_id: 'case-a', title: 'OA回执', direction: 'IN', attachments: [
    approvedAttachment({ id: 'receipt-oa1', document_id: 'receipt-document', filename: 'OA1回执.pdf', role: 'RECEIPT_PDF', is_receipt_evidence: true }),
    approvedAttachment({ id: 'receipt-oa2', document_id: 'receipt-document', filename: 'OA2回执.pdf', role: 'ELECTRONIC_RECEIPT', is_archive_evidence: true, content_hash: hashB, evidence_version_id: 'receipt-evidence-2' }),
    approvedAttachment({ id: 'not-receipt', document_id: 'receipt-document', filename: '普通附件.pdf', role: 'OTHER' }),
  ],
}]
const receiptOptions = documents.selectReviewedReceiptEvidenceOptions(receiptDocuments, 'case-a')
assert.deepEqual(receiptOptions.map((row) => row.attachment_id), ['receipt-oa1', 'receipt-oa2'])
await official.createReviewedOfficialWorkPackageReceipt('package-oa1', 'case-a', receiptOptions[0], receiptPayload)
await official.createReviewedOfficialWorkPackageReceipt('package-oa2', 'case-a', receiptOptions[1], receiptPayload)
assert.deepEqual(httpCalls.slice(-2).map((call) => call.payload.receipt_attachment_id), ['receipt-oa1', 'receipt-oa2'])
await assert.rejects(
  official.createReviewedOfficialWorkPackageReceipt('package-wrong', 'case-b', receiptOptions[0], receiptPayload),
  /当前案件已复核附件/,
)

delete globalThis.__ordinal04Http
console.log('demo V6 lifecycle UI contract: PASS')
