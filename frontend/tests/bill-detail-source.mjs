import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'

const source = await readFile(new URL('../src/modules/billing/pages/BillDetail.vue', import.meta.url), 'utf8')

assert.match(source, /from '..\/..\/..\/utils\/money'/)
assert.doesNotMatch(source, /new Intl\.NumberFormat\('zh-CN',\s*\{\s*style:\s*'currency'/)
