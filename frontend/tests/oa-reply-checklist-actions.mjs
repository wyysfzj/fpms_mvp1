import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'

const source = await readFile(
  new URL('../src/modules/documents/pages/OAReplyPackage.vue', import.meta.url),
  'utf8',
)

const actionBlock = source.match(/const requiredChecklistActions = \[[\s\S]*?\n\]/)?.[0] ?? ''
const requiredCodes = [
  'STATEMENT_TEXT_CONFIRMED',
  'PDF_FIDELITY_CONFIRMED',
  'MODIFIED_CLAIMS_CONFIRMED',
  'EXPERIMENT_DATA_FLAG_CONFIRMED',
  'PREVIEW_CONFIRMED',
  'SIGNATURE_CONFIRMED',
]

for (const code of requiredCodes) {
  assert.equal(actionBlock.match(new RegExp(code, 'g'))?.length, 1, `missing or duplicated ${code}`)
}
for (const obsoleteCode of [
  'CLOUD_SECOND_DOWNLOAD_CONFIRMED',
  'PREVIEW_TABS_CONFIRMED',
  'SUBMISSION_CONFIRMED',
  'RECEIPT_CONFIRMED',
]) {
  assert.doesNotMatch(source, new RegExp(obsoleteCode))
}
assert.match(source, /v-for="action in requiredChecklistActions"/)
assert.match(source, /@click="handleChecklistDone\(action\.code, action\.evidenceNote\)"/)
assert.match(source, /status: 'DONE'/)
assert.doesNotMatch(actionBlock, /updateOaReplyChecklist/)
console.log('oa_reply_checklist_actions=PASS')
