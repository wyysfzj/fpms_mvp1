import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const here = path.dirname(fileURLToPath(import.meta.url))
const specPath = path.join(here, 'demo-integrated-a.live-backend.spec.ts')
assert.ok(fs.existsSync(specPath), `missing canonical integrated spec: ${specPath}`)
const source = fs.readFileSync(specPath, 'utf8')

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
  'bindFilingSubmission',
  'lifecycleEvidencePayload',
  'grantEvidencePayload',
  "expect(evidenceRoleMap.size).toBe(12)",
  "expect(x.checkpoints_passed).toBe(19)",
  "expect(x.role_map_count).toBe(8)",
  "expect(x.blocked_statuses).toEqual([409, 409, 409, 409])",
]) assert.ok(source.includes(token), `missing integrated contract token ${token}`)

for (const forbidden of ['page.route(', 'route.fulfill(', 'SessionLocal', 'sqlite3', 'pdP1LiveSeed', 'v6-enrich', 'test.skip', 'markSkeleton', 'contractRed', '.toBeTruthy()', 'expect({']) {
  assert.ok(!source.includes(forbidden), `forbidden construct ${forbidden}`)
}

const imports = [...source.matchAll(/from\s+['"]([^'"]+)['"]/g)].map((match) => match[1])
assert.deepEqual(imports.sort(), ['@playwright/test', 'node:fs/promises', 'node:path'].sort(), 'only audited imports are permitted')

for (const pattern of [
  /(?:page\.)?request\s*\.\s*(?:post|put|patch|fetch)\s*\([^)]*(?:attachments|evidence-versions|\/review)/s,
  /\bfetch\s*\([^)]*(?:attachments|evidence-versions|\/review)/s,
  /\baxios\s*\.\s*(?:post|put|patch)\s*\([^)]*(?:attachments|evidence-versions|\/review)/s,
]) assert.ok(!pattern.test(source), `direct evidence shortcut matched ${pattern}`)

assert.ok(!/[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}/i.test(source), 'fixed UUID forbidden')
console.log('demo_integrated_a_static_contract=PASS')
