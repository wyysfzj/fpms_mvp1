import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'

const apiTypes = await readFile(new URL('../src/api/fees.types.ts', import.meta.url), 'utf8')
const api = await readFile(new URL('../src/api/fees.ts', import.meta.url), 'utf8')
const page = await readFile(new URL('../src/modules/fees/pages/FeeDraftList.vue', import.meta.url), 'utf8')

assert.match(apiTypes, /case_no\?: string/)
assert.match(api, /\bcase_no\b/)
assert.match(api, /case_no,/)
assert.match(page, /case_no: string/)
assert.match(page, /case_no: filters\.case_no \|\| undefined/)
assert.doesNotMatch(page, /v-model="filters\.case_id"[\s\S]*placeholder="请输入案件编号"/)
