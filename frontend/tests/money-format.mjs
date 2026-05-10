import assert from 'node:assert/strict'

const { formatMoney, normalizeCurrencyCode } = await import('../.tmp-money-test/money.js')

assert.equal(normalizeCurrencyCode(''), 'CNY')
assert.equal(normalizeCurrencyCode('   '), 'CNY')
assert.equal(normalizeCurrencyCode(null), 'CNY')
assert.equal(normalizeCurrencyCode('usd'), 'USD')
assert.equal(normalizeCurrencyCode('bad-code'), 'CNY')

assert.doesNotThrow(() => formatMoney(0.14, ''))
assert.doesNotThrow(() => formatMoney(0.14, 'bad-code'))
assert.match(formatMoney(0.14, ''), /0\.14|0,14|￥|¥/)
assert.equal(formatMoney('not-a-number', ''), 'CNY not-a-number')
