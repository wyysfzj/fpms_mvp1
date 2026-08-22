import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'

const root = join(dirname(fileURLToPath(import.meta.url)), '..')
const page = readFileSync(join(root, 'src/modules/fees/pages/FeeDraftDetail.vue'), 'utf8')

assert.match(
  page,
  /const displayDraftId = computed\(\(\) => draft\.value\?\.id \|\| '—'\)/,
  'the customer-visible draft number must use the authoritative draft id',
)
assert.match(
  page,
  /\{\{ ZH\.feeDetail\.draftType \}\}: \{\{ getFeeDraftTypeText\(draft\.draft_type\) \}\}/,
  'the localized draft type remains a separate field',
)
assert.doesNotMatch(
  page,
  /const displayDraftId = computed\([\s\S]{0,160}getFeeDraftTypeText/,
  'the draft number must never be derived from the draft type',
)

console.log('fee draft detail identity contract OK')
