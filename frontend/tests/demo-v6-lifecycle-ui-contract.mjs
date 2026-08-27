import assert from 'node:assert/strict'
import { Buffer } from 'node:buffer'
import { existsSync, readFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'
import ts from 'typescript'

const frontendRoot = join(dirname(fileURLToPath(import.meta.url)), '..')
const read = (path) => readFileSync(join(frontendRoot, path), 'utf8')
const indexPage = read('index.html')
const filingPage = read('src/modules/cases/pages/FilingPreparation.vue')
const documentCreatePage = read('src/modules/documents/pages/DocumentCreate.vue')
const documentPage = read('src/modules/documents/pages/DocumentDetail.vue')
const oaPage = read('src/modules/documents/pages/OAReplyPackage.vue')
const receiptPanel = read('src/modules/officialWorkflows/components/ReceiptArchivePanel.vue')
const lifecyclePath = join(frontendRoot, 'src/modules/documents/components/DocumentLifecycleEvidenceActions.vue')
const lifecyclePanel = existsSync(lifecyclePath) ? readFileSync(lifecyclePath, 'utf8') : ''
const lifecycleScript = lifecyclePanel.match(/<script setup lang="ts">([\s\S]*?)<\/script>/)?.[1] || ''
const lifecycleSourceFile = ts.createSourceFile(
  'DocumentLifecycleEvidenceActions.ts', lifecycleScript, ts.ScriptTarget.Latest, true, ts.ScriptKind.TS,
)
const lifecycleProjectionNames = ['baseActions', 'isOaNoticeDocument', 'actions']
const lifecycleProjectionDeclarations = lifecycleSourceFile.statements.filter(
  (statement) => ts.isVariableStatement(statement) && statement.declarationList.declarations.some(
    (declaration) => ts.isIdentifier(declaration.name) && lifecycleProjectionNames.includes(declaration.name.text),
  ),
)
assert.equal(lifecycleProjectionDeclarations.length, lifecycleProjectionNames.length)
const evidenceLabelExpression = lifecyclePanel.match(/<el-form-item\s+:label="([^"]+)"/)?.[1]
assert.ok(evidenceLabelExpression)
const renderEvidenceLabel = new Function('isOaNoticeDocument', `return ${evidenceLabelExpression}`)
const documentsApi = read('src/api/documents.ts')
const officialApi = read('src/api/officialWorkflows.ts')
const documentCreateScript = documentCreatePage.match(/<script setup lang="ts">([\s\S]*?)<\/script>/)?.[1] || ''

assert.doesNotMatch(indexPage, /https:\/\/fonts\.(?:googleapis|gstatic)\.com/)
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
assert.match(oaPage, /selectReviewedReplyDocumentOptions/)
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
    'isOaNoticeTemplateCode',
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
const documentCreateSourceFile = ts.createSourceFile(
  'DocumentCreate.ts', documentCreateScript, ts.ScriptTarget.Latest, true, ts.ScriptKind.TS,
)
const deadlineGuardDeclaration = documentCreateSourceFile.statements.find(
  (statement) => ts.isFunctionDeclaration(statement) && statement.name?.text === 'hasPartialOfficialDeadline',
)
assert.ok(deadlineGuardDeclaration)
const deadlineGuardModule = ts.transpileModule(
  `${deadlineGuardDeclaration.getText(documentCreateSourceFile)}\nexport { hasPartialOfficialDeadline }`,
  { compilerOptions: { module: ts.ModuleKind.ESNext, target: ts.ScriptTarget.ES2022 } },
).outputText
const documentCreate = await import(
  `data:text/javascript;base64,${Buffer.from(deadlineGuardModule).toString('base64')}#${Math.random()}`,
)

assert.equal(documentCreate.hasPartialOfficialDeadline(null, null, null), false)
assert.equal(documentCreate.hasPartialOfficialDeadline('2026-11-23', null, null), true)
assert.equal(documentCreate.hasPartialOfficialDeadline('2026-11-23', 'IMPORTED_OFFICIAL_NOTICE', null), true)
assert.equal(documentCreate.hasPartialOfficialDeadline(
  '2026-11-23', 'IMPORTED_OFFICIAL_NOTICE', 'CONFIRMED',
), false)

const hashA = `sha256:${'a'.repeat(64)}`
const hashB = `sha256:${'b'.repeat(64)}`
const hashC = `sha256:${'c'.repeat(64)}`
const hashD = `sha256:${'d'.repeat(64)}`
for (const templateCode of [
  'OA_IN',
  'OFFICIAL_NOTICE_003',
  'OFFICIAL_NOTICE_005',
  'OFFICIAL_NOTICE_021',
  'OFFICIAL_NOTICE_024',
  'OFFICIAL_NOTICE_029',
]) {
  assert.equal(documents.isOaNoticeTemplateCode(templateCode), true)
}
for (const templateCode of [
  'OA_OUT',
  'ACCEPTANCE_NOTICE',
  'GRANT_NOTICE',
  'OFFICIAL_NOTICE_001',
  'OFFICIAL_NOTICE_004',
  'OFFICIAL_NOTICE_999',
  '',
  null,
]) {
  assert.equal(documents.isOaNoticeTemplateCode(templateCode), false)
}

async function loadLifecycleActionProjection(templateCode) {
  const compiled = ts.transpileModule(
    `
      const props = { document: { template_code: ${JSON.stringify(templateCode)} } }
      const computed = (factory) => ({ get value() { return factory() } })
      const isOaNoticeTemplateCode = ${documents.isOaNoticeTemplateCode.toString()}
      ${lifecycleProjectionDeclarations.map((statement) => statement.getText(lifecycleSourceFile)).join('\n')}
      export { isOaNoticeDocument, actions }
    `,
    { compilerOptions: { module: ts.ModuleKind.ESNext, target: ts.ScriptTarget.ES2022 } },
  ).outputText
  return import(`data:text/javascript;base64,${Buffer.from(compiled).toString('base64')}#${Math.random()}`)
}

const originalLifecycleActions = [
  { code: 'ACCEPTANCE_NOTICE', label: '记录受理通知' },
  { code: 'PRELIMINARY_START', label: '开始初步审查' },
  { code: 'PRELIMINARY_PASS', label: '记录初审通过' },
  { code: 'PUBLICATION_NOTICE', label: '记录公布通知' },
  { code: 'SUBSTANTIVE_START', label: '开始实质审查' },
]
const ordinaryLifecycleProjection = await loadLifecycleActionProjection('OA_OUT')
assert.equal(ordinaryLifecycleProjection.isOaNoticeDocument.value, false)
assert.equal(renderEvidenceLabel(ordinaryLifecycleProjection.isOaNoticeDocument.value), '证据文件')
assert.deepEqual(ordinaryLifecycleProjection.actions.value, originalLifecycleActions)
for (const templateCode of [
  'OA_IN',
  'OFFICIAL_NOTICE_003',
  'OFFICIAL_NOTICE_005',
  'OFFICIAL_NOTICE_021',
  'OFFICIAL_NOTICE_024',
  'OFFICIAL_NOTICE_029',
]) {
  const oaLifecycleProjection = await loadLifecycleActionProjection(templateCode)
  assert.equal(oaLifecycleProjection.isOaNoticeDocument.value, true)
  assert.equal(renderEvidenceLabel(oaLifecycleProjection.isOaNoticeDocument.value), '已复核证据版本')
  assert.deepEqual(oaLifecycleProjection.actions.value, [
    ...originalLifecycleActions,
    { code: 'OA_NOTICE', label: '记录审查意见通知' },
  ])
}
const approvedAttachment = (overrides = {}) => ({
  id: 'attachment-approved', filename: '受理通知书.pdf', file_size: 12, created_at: '2026-08-02',
  document_id: 'document-acceptance', official_file_role: 'OFFICIAL_NOTICE_PDF',
  evidence_version_id: 'evidence-approved', content_hash: hashA, role: 'ACCEPTANCE_NOTICE',
  review_state: 'APPROVED', is_current: true, is_final: true, ...overrides,
})
const reviewedReplyAttachments = (documentId, prefix) => [
  approvedAttachment({ id: `${prefix}-pdf`, document_id: documentId, filename: `${prefix}-陈述意见.pdf`, role: 'RAW_ATTACHMENT', official_file_role: 'OA_STATEMENT_PDF', evidence_version_id: `${prefix}-pdf-version`, content_hash: hashB, is_final: false }),
  approvedAttachment({ id: `${prefix}-claims`, document_id: documentId, filename: `${prefix}-修改后权利要求书.docx`, role: 'RAW_ATTACHMENT', official_file_role: 'OA_MODIFIED_CLAIMS', evidence_version_id: `${prefix}-claims-version`, content_hash: hashC, is_final: false }),
  approvedAttachment({ id: `${prefix}-word`, document_id: documentId, filename: `${prefix}-陈述意见.docx`, role: 'RAW_ATTACHMENT', official_file_role: 'OA_STATEMENT_WORD', evidence_version_id: `${prefix}-word-version`, content_hash: hashA, is_final: false }),
]
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

const collidingDocuments = [{
  id: 'document-collision', case_id: 'case-a', title: '身份碰撞证据', direction: 'OUT', reply_to_id: 'oa-collision', attachments: [
    approvedAttachment({ id: 'collision-a', document_id: 'document-collision', filename: '碰撞甲.pdf', evidence_version_id: 'collision-version', content_hash: hashB, role: 'RECEIPT_PDF', is_receipt_evidence: true }),
    approvedAttachment({ id: 'collision-b', document_id: 'document-collision', filename: '碰撞乙.pdf', evidence_version_id: 'collision-version', content_hash: hashB, role: 'RECEIPT_PDF', is_receipt_evidence: true }),
  ],
}]
const callsBeforeCollision = httpCalls.length
assert.deepEqual(documents.selectReviewedEvidenceOptions(collidingDocuments, 'case-a'), [])
assert.deepEqual(documents.selectReviewedReplyDocumentOptions(collidingDocuments, 'case-a', 'oa-collision'), [])
assert.deepEqual(documents.selectReviewedReceiptEvidenceOptions(collidingDocuments, 'case-a'), [])
for (const option of documents.selectReviewedEvidenceOptions(collidingDocuments, 'case-a')) {
  await documents.recordDocumentLifecycleEvidence('ACCEPTANCE_NOTICE', 'case-a', option, {
    effective_at: '2026-08-02T10:00:00', occurred_at: null, idempotency_key: 'must-not-run',
  })
}
assert.equal(httpCalls.length, callsBeforeCollision)

const replyDocuments = [
  ...caseDocuments,
  { id: 'reply-oa1', case_id: 'case-a', title: 'OA1答复', direction: 'OUT', reply_to_id: 'oa1', ref_no: 'OA-REPLY-1', doc_date: '2026-08-03', attachments: reviewedReplyAttachments('reply-oa1', 'oa1') },
  { id: 'reply-oa2', case_id: 'case-a', title: 'OA2答复', direction: 'OUT', reply_to_id: 'oa2', ref_no: 'OA-REPLY-2', doc_date: '2026-08-04', attachments: reviewedReplyAttachments('reply-oa2', 'oa2') },
]
const reviewedReplyOptions = documents.selectReviewedReplyDocumentOptions(replyDocuments, 'case-a', 'oa1')
assert.deepEqual(reviewedReplyOptions, [{
  document_id: 'reply-oa1', case_id: 'case-a', title: 'OA1答复',
  attachment_id: 'oa1-word', filename: 'oa1-陈述意见.docx', role: 'OA_STATEMENT_WORD',
  evidence_version_id: 'oa1-word-version', content_hash: hashA,
  ref_no: 'OA-REPLY-1', doc_date: '2026-08-03',
}])
assert.deepEqual(
  documents.selectReviewedReplyDocumentOptions(replyDocuments, 'case-a', 'oa2').map((row) => row.document_id),
  ['reply-oa2'],
)
assert.deepEqual(documents.selectReviewedEvidenceOptions(replyDocuments.slice(-2), 'case-a'), [])

const eligibleReplyDocument = replyDocuments.at(-2)
function assertReplyDocumentRejected(name, mutate) {
  const candidate = structuredClone(eligibleReplyDocument)
  mutate(candidate)
  assert.deepEqual(documents.selectReviewedReplyDocumentOptions([candidate], 'case-a', 'oa1'), [], name)
}
assertReplyDocumentRejected('missing required role', (document) => {
  document.attachments = document.attachments.filter((attachment) => attachment.official_file_role !== 'OA_STATEMENT_PDF')
})
assertReplyDocumentRejected('pending required role', (document) => {
  document.attachments[0].review_state = 'PENDING'
})
assertReplyDocumentRejected('rejected required role', (document) => {
  document.attachments[0].review_state = 'REJECTED'
})
assertReplyDocumentRejected('noncurrent required role', (document) => {
  document.attachments[0].is_current = false
})
assertReplyDocumentRejected('wrong case', (document) => {
  document.case_id = 'case-b'
})
assertReplyDocumentRejected('wrong source', (document) => {
  document.reply_to_id = 'oa2'
})
assertReplyDocumentRejected('wrong direction', (document) => {
  document.direction = 'IN'
})
assertReplyDocumentRejected('missing evidence identity', (document) => {
  document.attachments[0].evidence_version_id = ''
})
assertReplyDocumentRejected('padded evidence identity', (document) => {
  document.attachments[0].evidence_version_id = ' padded-version '
})
assertReplyDocumentRejected('mismatched attachment identity', (document) => {
  document.attachments[0].document_id = 'another-document'
})
assertReplyDocumentRejected('invalid evidence hash', (document) => {
  document.attachments[0].content_hash = `sha256:${'A'.repeat(64)}`
})
assertReplyDocumentRejected('misleading generic role cannot replace official role', (document) => {
  document.attachments[0].official_file_role = 'OA_OTHER_PROOF'
  document.attachments[0].role = 'OA_STATEMENT_PDF'
})
assertReplyDocumentRejected('duplicate required role', (document) => {
  document.attachments.push(approvedAttachment({ id: 'oa1-word-duplicate', document_id: document.id, filename: '重复陈述意见.docx', role: 'RAW_ATTACHMENT', official_file_role: 'OA_STATEMENT_WORD', evidence_version_id: 'oa1-word-duplicate-version', content_hash: hashD, is_final: false }))
})
assertReplyDocumentRejected('colliding required identity', (document) => {
  const word = document.attachments.find((attachment) => attachment.official_file_role === 'OA_STATEMENT_WORD')
  document.attachments[0].evidence_version_id = word.evidence_version_id
  document.attachments[0].content_hash = word.content_hash
})

const time = { effective_at: '2026-08-02T10:00:00', occurred_at: null, idempotency_key: 'lifecycle-action-1' }
for (const [action, path] of [
  ['ACCEPTANCE_NOTICE', 'acceptance-notice'],
  ['PRELIMINARY_START', 'preliminary-start'],
  ['PRELIMINARY_PASS', 'preliminary-pass'],
  ['PUBLICATION_NOTICE', 'publication-notice'],
  ['SUBSTANTIVE_START', 'substantive-start'],
  ['OA_NOTICE', 'oa-notice'],
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
    approvedAttachment({ id: 'not-receipt', document_id: 'receipt-document', filename: '普通附件.pdf', evidence_version_id: 'other-evidence', role: 'OTHER' }),
  ],
}]
const receiptOptions = documents.selectReviewedReceiptEvidenceOptions(receiptDocuments, 'case-a')
assert.deepEqual(receiptOptions.map((row) => row.attachment_id), ['receipt-oa1', 'receipt-oa2'])
const reviewedDraftReceiptDocuments = [
  {
    id: 'reviewed-draft-receipts', case_id: 'case-a', title: '已复核回执附件', direction: 'IN', attachments: [
      approvedAttachment({ id: 'draft-role', document_id: 'reviewed-draft-receipts', filename: '角色回执.pdf', role: 'RECEIPT_PDF', is_final: false }),
      approvedAttachment({ id: 'draft-receipt-flag', document_id: 'reviewed-draft-receipts', filename: '回执标记.pdf', role: 'OTHER', is_receipt_evidence: true, is_final: false, evidence_version_id: 'draft-receipt-flag-version' }),
      approvedAttachment({ id: 'draft-archive-flag', document_id: 'reviewed-draft-receipts', filename: '归档标记.pdf', role: 'OTHER', is_archive_evidence: true, is_final: false, evidence_version_id: 'draft-archive-flag-version' }),
      approvedAttachment({ id: 'draft-pending', document_id: 'reviewed-draft-receipts', role: 'RECEIPT_PDF', review_state: 'PENDING', is_final: false, evidence_version_id: 'draft-pending-version' }),
      approvedAttachment({ id: 'draft-rejected', document_id: 'reviewed-draft-receipts', role: 'RECEIPT_PDF', review_state: 'REJECTED', is_final: false, evidence_version_id: 'draft-rejected-version' }),
      approvedAttachment({ id: 'draft-stale', document_id: 'reviewed-draft-receipts', role: 'RECEIPT_PDF', is_current: false, is_final: false, evidence_version_id: 'draft-stale-version' }),
      approvedAttachment({ id: 'draft-missing-version', document_id: 'reviewed-draft-receipts', role: 'RECEIPT_PDF', is_final: false, evidence_version_id: null }),
      approvedAttachment({ id: 'draft-missing-hash', document_id: 'reviewed-draft-receipts', role: 'RECEIPT_PDF', is_final: false, evidence_version_id: 'draft-missing-hash-version', content_hash: null }),
      approvedAttachment({ id: 'draft-invalid-hash', document_id: 'reviewed-draft-receipts', role: 'RECEIPT_PDF', is_final: false, evidence_version_id: 'draft-invalid-hash-version', content_hash: `sha256:${'A'.repeat(64)}` }),
      approvedAttachment({ id: 'draft-ordinary', document_id: 'reviewed-draft-receipts', role: 'OTHER', is_final: false, evidence_version_id: 'draft-ordinary-version' }),
    ],
  },
  {
    id: 'reviewed-draft-wrong-case', case_id: 'case-b', title: '他案已复核回执', direction: 'IN', attachments: [
      approvedAttachment({ id: 'draft-wrong-case', document_id: 'reviewed-draft-wrong-case', role: 'RECEIPT_PDF', is_final: false, evidence_version_id: 'draft-wrong-case-version' }),
    ],
  },
]
assert.deepEqual(documents.selectReviewedEvidenceOptions(reviewedDraftReceiptDocuments, 'case-a'), [])
assert.equal(documents.selectReviewedEvidenceOptions.length, 2)
const ordinaryNonFinalEvidence = [{
  id: 'ordinary-non-final-document', case_id: 'case-a', title: '普通非最终证据', direction: 'IN', attachments: [
    approvedAttachment({ id: 'ordinary-non-final', document_id: 'ordinary-non-final-document', role: 'OTHER', is_final: false, evidence_version_id: 'ordinary-non-final-version' }),
  ],
}]
assert.deepEqual(documents.selectReviewedEvidenceOptions(ordinaryNonFinalEvidence, 'case-a'), [])
assert.deepEqual(documents.selectReviewedEvidenceOptions(ordinaryNonFinalEvidence, 'case-a', false), [])
assert.deepEqual(
  documents.selectReviewedReceiptEvidenceOptions(reviewedDraftReceiptDocuments, 'case-a').map((row) => row.attachment_id),
  ['draft-role', 'draft-receipt-flag', 'draft-archive-flag'],
)
const reviewedDraftReceiptCollision = [{
  id: 'reviewed-draft-collision', case_id: 'case-a', title: '已复核回执身份碰撞', direction: 'IN', attachments: [
    approvedAttachment({ id: 'draft-collision-a', document_id: 'reviewed-draft-collision', role: 'RECEIPT_PDF', is_final: false, evidence_version_id: 'draft-collision-version', content_hash: hashB }),
    approvedAttachment({ id: 'draft-collision-b', document_id: 'reviewed-draft-collision', role: 'RECEIPT_PDF', is_final: false, evidence_version_id: 'draft-collision-version', content_hash: hashB }),
  ],
}]
assert.deepEqual(documents.selectReviewedReceiptEvidenceOptions(reviewedDraftReceiptCollision, 'case-a'), [])
await official.createReviewedOfficialWorkPackageReceipt('package-oa1', 'case-a', receiptOptions[0], receiptPayload)
await official.createReviewedOfficialWorkPackageReceipt('package-oa2', 'case-a', receiptOptions[1], receiptPayload)
assert.deepEqual(httpCalls.slice(-2).map((call) => call.payload.receipt_attachment_id), ['receipt-oa1', 'receipt-oa2'])
await assert.rejects(
  official.createReviewedOfficialWorkPackageReceipt('package-wrong', 'case-b', receiptOptions[0], receiptPayload),
  /当前案件已复核附件/,
)

delete globalThis.__ordinal04Http
console.log('demo V6 lifecycle UI contract: PASS')
