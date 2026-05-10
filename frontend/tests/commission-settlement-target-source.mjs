import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'

const source = await readFile(new URL('../src/modules/commission/pages/CommissionSettlement.vue', import.meta.url), 'utf8')

assert.match(source, /getCommission/)
assert.match(source, /targetSettleableCommissions/)
assert.match(source, /UNASSIGNED/)
assert.match(source, /创建目标批次/)
assert.match(source, /hasTargetSettleableSource/)
