import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import ts from 'typescript'

const here = path.dirname(fileURLToPath(import.meta.url))
const specPath = path.join(here, 'demo-integrated-a.live-backend.spec.ts')
assert.ok(fs.existsSync(specPath), `missing canonical integrated spec: ${specPath}`)
const source = process.argv.includes('--stdin') ? fs.readFileSync(0, 'utf8') : fs.readFileSync(specPath, 'utf8')

for (let ordinal = 0; ordinal <= 18; ordinal += 1) {
  assert.ok(source.includes(`IA-${String(ordinal).padStart(2, '0')}`), `missing IA-${ordinal}`)
}

const roles = [
  'FILING_FINAL_SUBMISSION',
  'FILING_RECEIPT',
  'ACCEPTANCE_NOTICE',
  'PRELIMINARY_EXAMINATION_SOURCE',
  'PUBLICATION_NOTICE',
  'SUBSTANTIVE_EXAMINATION_SOURCE',
  'OA_NOTICE_1',
  'OA_RECEIPT_1',
  'OA_NOTICE_2',
  'OA_RECEIPT_2',
  'GRANT_NOTICE_ORIGINAL',
  'GRANT_NOTICE_REPLACEMENT',
]
for (const role of roles) assert.ok(source.includes(role), `missing bundle role ${role}`)

for (let ordinal = 0; ordinal <= 18; ordinal += 1) {
  assert.ok(
    source.includes(`test.step(checkpointContract[${ordinal}]`),
    `IA-${String(ordinal).padStart(2, '0')} lacks an executable Playwright step`,
  )
}

for (const token of [
  'attachment-open-upload',
  'attachment-file-picker',
  'setInputFiles',
  'reviewerContext',
  'evidenceRoleMap',
  'manifestSha256',
  'bundle_id',
  'bundle_version',
  'template_code',
  'template_sha256',
  'rate_item_code',
  'rate_source_ref',
  'rate_source_version',
  'rate_source_sha256',
  "expect(snapshot.business_counts).toEqual({ client: 0",
  "expect(snapshot.readiness).toBe('READY')",
  'attachmentId',
  'evidenceVersionId',
  'contentHash',
  'reviewState',
  'expected_content_hash',
  'reviewed_evidence_version_id',
  'official_due_date',
  'official_due_date_source',
  'CONFIRMED',
  'GRANT_REGISTRATION_IN_PROGRESS',
  'GRANT_REGISTRATION',
  'APPLICATION_PENDING',
  'GRANT_PENDING',
  'generate-draft',
  'batch-instruction',
  'generate-notices',
  'mark_waiting_client',
  'SETTLED',
  'FULLY_ALLOCATED',
  '0.00',
  'recordFilingSubmission',
  'recordDocumentLifecycleConsumer',
  'recordReceiptConsumer',
  'recordGrantConsumer',
  'assertCompleteEvidenceLedger',
  'expectedConsumerByRole',
  'filing_command_result',
  'filing_package_result',
  'filing_activity_result',
  'source_evidence_version_id',
  'replacement_predecessor_task_id',
  'replacement_metadata',
  'orderedEvidenceLedger',
  'x.surfaces',
  "expect(evidenceRoleMap.size).toBe(12)",
  "expect(x.checkpoints_passed).toBe(19)",
  "expect(evidenceRoleMap.size).toBe(7)",
  "expect(x.blocked_statuses).toEqual([409, 409, 409, 409])",
  "expect(x.provenance).toEqual(expectedProvenance)",
  "expect(x.source_draft_ids).toEqual([draftId])",
  "expect(x.replayed_payment_id).toBe(x.payment_id)",
  "expect(x.closed_task_ids).toEqual([x.task_id])",
  "expect(x.oa1_history_after).toEqual(x.oa1_history_before)",
]) assert.ok(source.includes(token), `missing integrated contract token ${token}`)

for (const forbidden of ['page.route(', 'route.fulfill(', 'SessionLocal', 'sqlite3', 'pdP1LiveSeed', 'v6-enrich', 'test.skip', 'markSkeleton', 'contractRed', '.toBeTruthy()', 'expect({', 'addInitScript', '.evaluate(', 'import(']) {
  assert.ok(!source.includes(forbidden), `forbidden construct ${forbidden}`)
}
for (const falseGreen of [
  'client_count: 1',
  'business_counts: { package: 0',
  'return deadline',
  'replayed_task_id: targetTask.task_id',
  'link_count: linked.body.reply_document.id ===',
]) assert.ok(!source.includes(falseGreen), `Task5 false-green construct ${falseGreen}`)
for (const task5Evidence of [
  'visibleCaseSnapshot(',
  'visibleOaTasks(',
  'task5-checkpoints.json',
  'task_identity_snapshots',
  'missing_deadline_no_write',
  'changed_deadline_no_write',
  'linked_reply_ids',
  'tasks.map((item) => item.id)',
  'matches.map((item) => item.id)',
  'observedOverlayPackages(',
  'item.package_kind, item.status',
  "typeof x.task_id).toBe('string')",
  'item.client_code === code && item.name_cn === this.clientName',
  "item.contact_name === '虚构主联系人'",
]) assert.ok(source.includes(task5Evidence), `missing Task5 observed contract ${task5Evidence}`)
for (const wrongShape of [
  'tasks.map((item) => item.task_id)',
  '.map((item) => item.package_id).filter',
]) assert.ok(!source.includes(wrongShape), `Task5 wrong response shape ${wrongShape}`)

const importLines = source.split('\n').filter((line) => /^import\s/.test(line.trimStart())).map((line) => line.trim())
assert.deepEqual(importLines, [
  "import { test, expect, type APIRequestContext, type BrowserContext, type Page } from '@playwright/test'",
  "import { mkdir, writeFile } from 'node:fs/promises'",
  "import path from 'node:path'",
], 'only three exact audited imports are permitted')

const expectedPublicLifecycleApi = {
  ARCHIVE_PACKAGE: ['POST', '/official-work-packages/{package_id}/archive'],
  GET_FILING_PACKAGE: ['GET', '/official-work-packages/{package_id}/filing-preparation'],
  GET_GRANT_TASK: ['GET', '/grant-fee-tasks/{task_id}/state'],
  GET_OA_PACKAGE: ['GET', '/official-work-packages/{package_id}/oa-reply'],
  GRANT_BATCH_INSTRUCTION: ['POST', '/grant-fee-tasks/batch-instruction'],
  GRANT_GENERATE_DRAFT: ['POST', '/grant-fee-tasks/{task_id}/generate-draft'],
  GRANT_GENERATE_NOTICES: ['POST', '/grant-fee-tasks/generate-notices'],
  GRANT_NOTICE: ['POST', '/grant-fee-tasks/{grant_fee_task_id}/lifecycle/grant-notice'],
  GRANT_REPLACEMENT: ['POST', '/grant-fee-tasks/{task_id}/replacement-notice'],
  GRANT_TASK_STATE: ['PUT', '/grant-fee-tasks/{task_id}/state'],
  LINK_OA_REPLY: ['POST', '/official-work-packages/{package_id}/oa-reply/reply-document'],
  RECORD_ACCEPTANCE: ['POST', '/documents/{document_id}/lifecycle/acceptance-notice'],
  RECORD_FILING_EXTERNAL: ['POST', '/official-work-packages/{package_id}/filing-preparation/external-operations'],
  RECORD_OA_NOTICE: ['POST', '/documents/{document_id}/lifecycle/oa-notice'],
  RECORD_PACKAGE_RECEIPT: ['POST', '/official-work-packages/{package_id}/receipts'],
  RECORD_PRELIMINARY_PASS: ['POST', '/documents/{document_id}/lifecycle/preliminary-pass'],
  RECORD_PRELIMINARY_START: ['POST', '/documents/{document_id}/lifecycle/preliminary-start'],
  RECORD_PUBLICATION: ['POST', '/documents/{document_id}/lifecycle/publication-notice'],
  RECORD_SUBSTANTIVE_START: ['POST', '/documents/{document_id}/lifecycle/substantive-start'],
  RESOLVE_FILING: ['POST', '/cases/{case_id}/official-work-packages/filing-preparation/resolve'],
  RESOLVE_OA: ['POST', '/official-documents/{document_id}/official-work-packages/oa-reply/resolve'],
}
const allowlistStart = '// BEGIN EXACT PUBLIC LIFECYCLE API ALLOWLIST'
const allowlistEnd = '// END EXACT PUBLIC LIFECYCLE API ALLOWLIST'
assert.equal(source.split(allowlistStart).length, 2, 'public lifecycle API allowlist start marker must be unique')
assert.equal(source.split(allowlistEnd).length, 2, 'public lifecycle API allowlist end marker must be unique')
const allowlistBlock = source.split(allowlistStart)[1].split(allowlistEnd)[0]
for (const [operation, [method, apiPath]] of Object.entries(expectedPublicLifecycleApi)) {
  assert.equal(
    allowlistBlock.split(`  ${operation}: { method: '${method}', path: '${apiPath}' },`).length,
    2,
    `missing exact public lifecycle operation ${operation}`,
  )
}
assert.equal((allowlistBlock.match(/^  [A-Z_]+: \{ method:/gm) || []).length, Object.keys(expectedPublicLifecycleApi).length, 'extra public lifecycle operation')
assert.ok(!/attachments|evidence-versions|\/review/.test(allowlistBlock), 'evidence upload/review must remain visible-UI-only')

const helperStart = '// BEGIN AUDITED PUBLIC API HELPER'
const helperEnd = '// END AUDITED PUBLIC API HELPER'
assert.equal(source.split(helperStart).length, 2, 'audited helper start marker must be unique')
assert.equal(source.split(helperEnd).length, 2, 'audited helper end marker must be unique')
const prefix = source.split(helperStart)[0]
const helperAndSuffix = source.split(helperStart)[1]
const helper = helperAndSuffix.split(helperEnd)[0]
const suffix = helperAndSuffix.split(helperEnd)[1]
assert.equal(helper.split('apiRequest.fetch(').length, 2, 'audited helper owns exactly one request fetch')
const outsideHelper = prefix + suffix
for (const token of ['page.request', "page['request']", "['req'+'uest']", '.fetch(', 'fetch(', 'axios', 'XMLHttpRequest', 'WebSocket', 'addInitScript', '.evaluate(', 'eval(', 'Function(', 'import(', "['fet'+'ch']", "['po'+'st']"]) {
  assert.ok(!outsideHelper.includes(token), `network call outside audited helper: ${token}`)
}

const syntax = ts.createSourceFile('demo-integrated-a.live-backend.spec.ts', source, ts.ScriptTarget.Latest, true, ts.ScriptKind.TS)
const helperBodyStart = source.indexOf(helperStart)
const helperBodyEnd = source.indexOf(helperEnd)
let auditedFetchCount = 0
const forbiddenRuntimeIdentifiers = new Set([
  'eval',
  'Function',
  'Reflect',
  'globalThis',
  'window',
  'XMLHttpRequest',
  'WebSocket',
  'axios',
  'Proxy',
])
const forbiddenNetworkMembers = new Set([
  'request',
  'fetch',
  'post',
  'put',
  'patch',
  'delete',
  'addInitScript',
  'evaluate',
  'route',
  'fulfill',
  'bind',
  'call',
  'apply',
  'addScriptTag',
  'setContent',
])
const allowedDynamicElementAccess = new Set([
  'publicLifecycleApiAllowlist[operation]',
  'expectedConsumerByRole[role]',
])
const allowedMemberCalls = new Set([
  'archiveOa1', 'click', 'close', 'completeFilingAndOa1', 'completeOa2',
  'count',
  'createBill', 'createCase', 'createClientAndContact', 'createGrantOriginal',
  'createDocumentViaVisibleUi', 'createOaOut', 'createOffset', 'createPayment', 'createServiceDraft', 'endsWith', 'entries',
  'exerciseGrantGatesAndPay', 'fill', 'filter', 'find', 'first', 'flatMap', 'get', 'getByPlaceholder', 'getByRole',
  'getAttribute', 'getByTestId', 'getByText', 'goto', 'includes', 'inspectCatalog', 'join', 'json',
  'inputValue', 'isDisabled', 'isEnabled', 'keys', 'last', 'loadLifecycleOverlay', 'locator', 'map', 'newContext', 'newPage', 'now', 'objectContaining', 'parse', 'press',
  'preflight', 'push', 'red', 'rejectInvalidReceipts', 'reloadSummary', 'replace',
  'replaceGrant', 'resolveFiling', 'publicLifecycleApi', 'screenshot', 'set', 'setDefaultTimeout', 'setInputFiles', 'setTimeout', 'slice', 'sort', 'status', 'then',
  'step', 'stringify', 'textContent', 'toBe', 'toBeDefined', 'toBeGreaterThan',
  'toBeDisabled', 'toBeEnabled', 'toBeGreaterThanOrEqual', 'toBeVisible', 'toContain', 'toContainEqual', 'toContainText', 'toEqual', 'toLowerCase',
  'toHaveCount', 'toHaveLength', 'toHaveText', 'toHaveURL', 'toHaveValue', 'toMatch', 'trim', 'uploadRole', 'url', 'values',
  'verifyContentEdit', 'verifyMissingDeadlineNoWrite', 'verifyWizardDeadline', 'visibleCaseSnapshot', 'visibleOaTasks', 'waitForResponse', 'waitForTimeout',
])
const allowedIdentifierCalls = new Set([
  'assertCompleteEvidenceLedger', 'callPublicLifecycleApi', 'encodeURIComponent', 'evidenceDescriptors',
  'expect', 'login', 'mkdir', 'observedOverlayPackages', 'recordDocumentLifecycleConsumer',
  'recordFilingSubmission', 'recordGrantConsumer', 'recordReceiptConsumer', 'test',
  'uploadAndReviewEvidenceViaVisibleUi', 'writeFile',
])
const expectedSensitiveCallCounts = new Map([
  ["page.goto(`${baseUrl}/login`, { waitUntil: 'domcontentloaded' })", 1],
  ["page.waitForResponse((response) => response.status() === 200 && response.url().includes('/auth/login'))", 1],
  ["operatorPage.goto(`${baseUrl}/documents/${documentId}`, { waitUntil: 'domcontentloaded' })", 1],
  ["operatorPage.waitForResponse((response) => response.status() === 201 && response.url().includes('/attachments'))", 1],
  ["reviewerPage.goto(`${baseUrl}/documents/${documentId}`, { waitUntil: 'domcontentloaded' })", 1],
  ["reviewerPage.waitForResponse((response) => response.status() === 200 && response.url().includes('/review'))", 1],
  ["this.operatorPage.goto(`${baseUrl}/clients/new`, { waitUntil: 'domcontentloaded' })", 1],
  ["this.operatorPage.waitForResponse((response) => response.status() === 201 && new URL(response.url()).pathname.endsWith('/api/v1/clients'))", 1],
  ["this.operatorPage.goto(`${baseUrl}/clients/${client.id}`, { waitUntil: 'domcontentloaded' })", 1],
  ["this.operatorPage.waitForResponse((response) => response.status() === 201 && new URL(response.url()).pathname.endsWith(`/api/v1/clients/${client.id}/contacts`))", 1],
  ["this.operatorPage.waitForResponse((response) => response.status() === 200 && new URL(response.url()).pathname.endsWith(`/api/v1/clients/${client.id}/contacts`))", 1],
  [`this.operatorPage.waitForResponse((response) => {
      const url = new URL(response.url())
      return response.status() === 200 && url.pathname.endsWith('/api/v1/clients') && url.searchParams.get('page_size') === '20'
    })`, 1],
  ["this.operatorPage.goto(`${baseUrl}/clients`, { waitUntil: 'domcontentloaded' })", 1],
  ["this.operatorPage.goto(`${baseUrl}/cases/new`, { waitUntil: 'domcontentloaded' })", 1],
  ["this.operatorPage.waitForResponse((response) => new URL(response.url()).pathname.endsWith('/api/v1/cases'))", 1],
  ["this.operatorPage.waitForResponse((response) => response.status() === 200 && new URL(response.url()).pathname.endsWith(`/api/v1/cases/${created.id}/lifecycle-overlay`))", 1],
  [`this.operatorPage.waitForResponse((response) => {
      const url = new URL(response.url())
      return response.status() === 200 && url.pathname.endsWith('/api/v1/tasks') && url.searchParams.get('case_id') === created.id
    })`, 1],
  [`this.operatorPage.waitForResponse((response) => {
      const url = new URL(response.url())
      return response.status() === 200 && url.pathname.endsWith('/api/v1/fees/drafts') && url.searchParams.get('case_id') === created.id
    })`, 1],
  ["this.operatorPage.goto(`${baseUrl}/cases/${created.id}`, { waitUntil: 'domcontentloaded' })", 1],
  ["this.operatorPage.waitForResponse((response) => response.status() === 200 && new URL(response.url()).pathname.endsWith('/api/v1/bills'))", 1],
  ["this.operatorPage.goto(`${baseUrl}/billing/bills`, { waitUntil: 'domcontentloaded' })", 1],
  ["this.operatorPage.waitForResponse((response) => response.status() === 200 && new URL(response.url()).pathname.endsWith('/api/v1/payments'))", 1],
  ["this.operatorPage.goto(`${baseUrl}/billing/payments`, { waitUntil: 'domcontentloaded' })", 1],
  ["this.operatorPage.waitForResponse((response) => response.status() === 200 && new URL(response.url()).pathname.endsWith('/api/v1/offsets'))", 1],
  ["this.operatorPage.goto(`${baseUrl}/billing/offsets`, { waitUntil: 'domcontentloaded' })", 1],
  ["this.operatorPage.waitForResponse((response) => response.status() === 200 && new URL(response.url()).pathname.endsWith('/api/v1/doc-templates'))", 1],
  ["this.operatorPage.goto(`${baseUrl}/documents/new?case_id=${caseId}`, { waitUntil: 'domcontentloaded' })", 2],
  [`this.operatorPage.waitForResponse(
      (response) => response.status() >= 400 && new URL(response.url()).pathname.endsWith('/api/v1/documents'),
    )`, 1],
  ["this.operatorPage.goto(`${baseUrl}/documents`, { waitUntil: 'domcontentloaded' })", 2],
  [`this.operatorPage.waitForResponse((response) => {
      const url = new URL(response.url())
      return response.status() === 200 && url.pathname.endsWith('/api/v1/documents') && url.searchParams.get('page_size') === '20'
    })`, 2],
  [`this.operatorPage.waitForResponse((response) => {
      const url = new URL(response.url())
      return response.status() === 200 && url.pathname.endsWith('/api/v1/tasks') && url.searchParams.get('page_size') === '20' && url.searchParams.get('status') === null
    })`, 2],
  ["this.operatorPage.goto(`${baseUrl}/tasks`, { waitUntil: 'domcontentloaded' })", 2],
  ["this.operatorPage.goto(`${baseUrl}/official-workflows/filing-preparation?package_id=${packageId}`, { waitUntil: 'domcontentloaded' })", 1],
  ["this.operatorPage.waitForResponse((response) => response.status() === 200 && new URL(response.url()).pathname.endsWith(`/api/v1/cases/${caseId}/lifecycle-overlay`))", 1],
  ["this.operatorPage.goto(`${baseUrl}/cases/${caseId}`, { waitUntil: 'domcontentloaded' })", 2],
  ["this.operatorPage.waitForResponse((response) => response.status() === 200 && new URL(response.url()).pathname.endsWith('/api/v1/documents/impact-preview'))", 1],
  [`this.operatorPage.waitForResponse(
      (response) => new URL(response.url()).pathname.endsWith('/api/v1/documents'),
      { timeout: 5_000 },
    )`, 1],
  ["this.operatorPage.waitForResponse((item) => item.status() === 200 && new URL(item.url()).pathname.endsWith(`/api/v1/cases/${caseId}/lifecycle-overlay`))", 1],
  ["this.operatorPage.waitForResponse((response) => response.status() === 200 && new URL(response.url()).pathname.endsWith(`/api/v1/documents/${documentId}`))", 3],
  ["this.operatorPage.goto(`${baseUrl}/documents/${documentId}`, { waitUntil: 'domcontentloaded' })", 2],
  ["this.operatorPage.goto(`${baseUrl}/documents/wizard`, { waitUntil: 'domcontentloaded' })", 2],
  ["this.operatorPage.waitForResponse((response) => response.status() === 200 && new URL(response.url()).pathname.endsWith('/api/v1/documents/wizard/task-preview'))", 1],
  ["this.operatorPage.goto(`${baseUrl}/official-workflows/filing-preparation?package_id=${this.filingPackageId}`, { waitUntil: 'domcontentloaded' })", 1],
  ["this.operatorPage.waitForResponse((response) => response.status() === 200 && new URL(response.url()).pathname.endsWith(`/api/v1/official-work-packages/${this.filingPackageId}/filing-preparation/refresh`))", 1],
  ["this.operatorPage.goto(`${baseUrl}/demo/abc`, { waitUntil: 'domcontentloaded' })", 1],
  ["this.operatorPage.waitForResponse((response) => response.status() === 200 && response.url().includes('/fees/demo-preflight'))", 1],
  ["page.goto(`${baseUrl}/demo/abc`, { waitUntil: 'domcontentloaded' })", 1],
  ["writeFile(path.join(evidenceDir!, 'evidence-role-map.json'), JSON.stringify(orderedEvidenceLedger, null, 2))", 1],
  ["writeFile(path.join(evidenceDir!, 'task5-checkpoints.json'), JSON.stringify({ checkpoints: task5Checkpoints, evidence_bindings: [...evidenceRoleMap.values()] }, null, 2))", 1],
])
assert.equal((source.match(/\bAPIRequestContext\b/g) || []).length, 3, 'evidence writes must use visible UI; APIRequestContext is confined to the audited helper and driver transport')
assert.equal((source.match(/\bapiRequest\b/g) || []).length, 4, 'evidence writes must use visible UI; apiRequest references must match the exact audited data flow')
assert.equal((source.match(/\brequest\b/g) || []).length, 2, 'evidence writes must use visible UI; Playwright request fixture references must match the exact audited data flow')

function constantString(node) {
  if (ts.isStringLiteral(node) || ts.isNoSubstitutionTemplateLiteral(node)) return node.text
  if (ts.isNumericLiteral(node)) return node.text
  if (ts.isBinaryExpression(node) && node.operatorToken.kind === ts.SyntaxKind.PlusToken) {
    const left = constantString(node.left)
    const right = constantString(node.right)
    return left === undefined || right === undefined ? undefined : left + right
  }
  return undefined
}

function memberName(node) {
  if (ts.isPropertyAccessExpression(node)) return node.name.text
  if (ts.isElementAccessExpression(node) && node.argumentExpression) return constantString(node.argumentExpression)
  if (ts.isIdentifier(node)) return node.text
  if (node.kind === ts.SyntaxKind.ImportKeyword) return 'import'
  return undefined
}

function containsTransportReference(node) {
  if (ts.isIdentifier(node) && ['apiRequest', 'request', 'page', 'context'].includes(node.text)) return true
  let found = false
  ts.forEachChild(node, (child) => {
    if (!found && containsTransportReference(child)) found = true
  })
  return found
}

function visit(node) {
  const inAuditedHelper = node.getStart(syntax) > helperBodyStart && node.getEnd() < helperBodyEnd
  if (ts.isIdentifier(node) && forbiddenRuntimeIdentifiers.has(node.text)) {
    assert.fail(`evidence writes must use visible UI; reflective network primitive ${node.text} is forbidden`)
  }
  if (ts.isIdentifier(node) && node.text === 'path') {
    const member = node.parent
    const call = ts.isPropertyAccessExpression(member)
      && member.expression === node
      && member.name.text === 'join'
      && ts.isCallExpression(member.parent)
      && member.parent.expression === member
      ? member.parent
      : undefined
    const write = call?.parent
    const isImport = ts.isImportClause(node.parent)
    const isPropertyName = (
      (ts.isPropertyAccessExpression(member) && member.name === node)
      || (ts.isPropertyAssignment(member) && member.name === node)
      || (ts.isPropertySignature(member) && member.name === node)
    )
    const isExactWriteTarget = write
      && ts.isCallExpression(write)
      && ts.isIdentifier(write.expression)
      && write.expression.text === 'writeFile'
      && write.arguments[0] === call
    const screenshotPath = call?.parent
    const screenshotOptions = screenshotPath?.parent
    const screenshotCall = screenshotOptions?.parent
    const isExactScreenshotTarget = screenshotPath
      && ts.isPropertyAssignment(screenshotPath)
      && ts.isIdentifier(screenshotPath.name)
      && screenshotPath.name.text === 'path'
      && ts.isObjectLiteralExpression(screenshotOptions)
      && ts.isCallExpression(screenshotCall)
      && ts.isPropertyAccessExpression(screenshotCall.expression)
      && screenshotCall.expression.name.text === 'screenshot'
      && screenshotCall.arguments[0] === screenshotOptions
    if (!isImport && !isPropertyName && !isExactWriteTarget && !isExactScreenshotTarget) {
      assert.fail('evidence writes must not alias or mutate the path namespace')
    }
  }
  if (ts.isIdentifier(node) && node.text === 'Object') {
    const member = node.parent
    const name = ts.isPropertyAccessExpression(member) || ts.isElementAccessExpression(member)
      ? memberName(member)
      : undefined
    const isAllowedObjectCall = name !== undefined
      && ['entries', 'keys', 'values'].includes(name)
      && ts.isCallExpression(member.parent)
      && member.parent.expression === member
    if (!isAllowedObjectCall) {
      assert.fail('evidence writes must use visible UI; Object reflection and aliasing are forbidden')
    }
  }
  if (ts.isObjectBindingPattern(node)) {
    const names = node.elements.map((element) => memberName(element.name)).sort()
    const isExactFixture = ts.isParameter(node.parent)
      && names.length === 3
      && names.join(',') === 'browser,page,request'
    if (!isExactFixture) {
      assert.fail('evidence writes must use visible UI; object destructuring is forbidden outside the exact Playwright fixture')
    }
  }
  if (ts.isPropertyAccessExpression(node) || ts.isElementAccessExpression(node)) {
    const name = memberName(node)
    const isExactAuditedFetch = name === 'fetch'
      && ts.isPropertyAccessExpression(node)
      && ts.isIdentifier(node.expression)
      && node.expression.text === 'apiRequest'
      && ts.isCallExpression(node.parent)
      && node.parent.expression === node
      && inAuditedHelper
    if (name && forbiddenNetworkMembers.has(name) && !isExactAuditedFetch) {
      assert.fail(`evidence writes must use visible UI; network member ${name} is outside the audited helper`)
    }
    if (ts.isElementAccessExpression(node) && name === undefined && !allowedDynamicElementAccess.has(node.getText(syntax))) {
      assert.fail('evidence writes must use visible UI; dynamic element access is outside the exact safe allowlist')
    }
  }
  if (ts.isBindingElement(node)) {
    const boundProperty = node.propertyName ? memberName(node.propertyName) : memberName(node.name)
    const declaration = node.parent.parent
    const initializer = ts.isVariableDeclaration(declaration) ? declaration.initializer : undefined
    if (boundProperty && forbiddenNetworkMembers.has(boundProperty) && initializer && containsTransportReference(initializer)) {
      assert.fail(`evidence writes must use visible UI; network member ${boundProperty} cannot be aliased`)
    }
  }
  if (ts.isCallExpression(node)) {
    if (ts.isElementAccessExpression(node.expression) && memberName(node.expression) === undefined && !inAuditedHelper) {
      assert.fail('evidence writes must use visible UI; dynamic computed calls are forbidden outside the audited helper')
    }
    const name = memberName(node.expression)
    if (name === 'writeFile') {
      const target = node.arguments[0]
      const payload = node.arguments[1]
      assert.ok(
        node.arguments.length === 2
          && target
          && ts.isCallExpression(target)
          && ts.isPropertyAccessExpression(target.expression)
          && ts.isIdentifier(target.expression.expression)
          && target.expression.expression.text === 'path'
          && target.expression.name.text === 'join'
          && target.arguments.length === 2
          && ts.isNonNullExpression(target.arguments[0])
          && ts.isIdentifier(target.arguments[0].expression)
          && target.arguments[0].expression.text === 'evidenceDir'
          && ts.isStringLiteral(target.arguments[1])
          && (
            target.arguments[1].text === 'evidence-role-map.json'
            || /^task(?:5|6|7|8|9|10)-checkpoints\.json$/.test(target.arguments[1].text)
          )
          && payload
          && ts.isCallExpression(payload)
          && ts.isPropertyAccessExpression(payload.expression)
          && ts.isIdentifier(payload.expression.expression)
          && payload.expression.expression.text === 'JSON'
          && payload.expression.name.text === 'stringify'
          && payload.arguments.length === 3
          && payload.arguments[1].kind === ts.SyntaxKind.NullKeyword
          && ts.isNumericLiteral(payload.arguments[2])
          && payload.arguments[2].text === '2',
        'evidence writes must use visible UI; file output is limited to the exact pretty-JSON checkpoint or final-ledger path',
      )
    }
    if (name === 'screenshot') {
      const options = node.arguments[0]
      const normalized = options?.getText(syntax).replace(/\s+/g, ' ')
      assert.equal(
        normalized,
        "{ path: path.join(evidenceDir!, 'integrated-final.png'), fullPage: true }",
        'final screenshot must use the exact run-local evidence path',
      )
    }
    const receiver = ts.isPropertyAccessExpression(node.expression) && ts.isIdentifier(node.expression.expression)
      ? node.expression.expression.text
      : undefined
    if (name === 'fetch' && receiver === 'apiRequest' && inAuditedHelper) {
      auditedFetchCount += 1
    } else if (['fetch', 'post', 'put', 'patch', 'delete', 'addInitScript', 'evaluate', 'route', 'fulfill', 'eval', 'Function', 'import'].includes(name)) {
      assert.fail(`evidence writes must use visible UI; network call ${name} is outside the audited helper`)
    } else if (ts.isIdentifier(node.expression)) {
      assert.ok(allowedIdentifierCalls.has(node.expression.text), `evidence writes must use visible UI; identifier call ${node.expression.text} is outside the exact call allowlist`)
    } else if (name !== undefined) {
      assert.ok(allowedMemberCalls.has(name), `evidence writes must use visible UI; member call ${name} is outside the exact call allowlist`)
      if (name === 'publicLifecycleApi') {
        const receiverIsThis = ts.isPropertyAccessExpression(node.expression)
          && node.expression.expression.kind === ts.SyntaxKind.ThisKeyword
        let owner = node.parent
        while (owner && !ts.isMethodDeclaration(owner)) owner = owner.parent
        const classOwner = owner?.parent
        const operation = node.arguments[0]
        assert.ok(
          receiverIsThis
            && owner
            && ts.isClassDeclaration(classOwner)
            && classOwner.name?.text === 'IntegratedJourneyDriver'
            && operation
            && ts.isStringLiteral(operation)
            && Object.hasOwn(expectedPublicLifecycleApi, operation.text)
            && node.arguments.length >= 2
            && node.arguments.length <= 3
            && ts.isObjectLiteralExpression(node.arguments[1]),
          'evidence writes must use visible UI; lifecycle wrapper calls must use this, a frozen operation and literal path parameters inside IntegratedJourneyDriver',
        )
      }
      if (name === 'goto') {
        const target = node.arguments[0]?.getText(syntax) ?? ''
        assert.ok(
          target.startsWith('`${baseUrl}/')
            && !target.startsWith('`${baseUrl}/api/')
            && !target.includes('%')
            && !/attachments|evidence-versions|\/review/.test(target),
          'evidence writes must use visible UI; navigation must stay on a non-API configured-base page',
        )
      }
    } else {
      assert.fail('evidence writes must use visible UI; indirect call is outside the exact call allowlist')
    }
  }
  if (ts.isNewExpression(node)) {
    assert.ok(
      ts.isIdentifier(node.expression)
        && ['Error', 'IntegratedJourneyDriver', 'Map', 'Set', 'URL'].includes(node.expression.text),
      'evidence writes must use only the exact constructor allowlist',
    )
  }
  ts.forEachChild(node, visit)
}

visit(syntax)
assert.equal(auditedFetchCount, 1, 'audited helper must contain exactly one apiRequest.fetch call')
assert.ok(!/[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}/i.test(source), 'fixed UUID forbidden')
console.log('demo_integrated_a_static_contract=PASS')
