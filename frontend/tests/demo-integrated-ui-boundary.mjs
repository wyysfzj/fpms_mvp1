import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { spawnSync } from 'node:child_process'

const specPath = 'FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/demo-integrated-a.live-backend.spec.ts'
const guardPath = 'FPMS_Automation_Skeleton_Pack/playwright_ts/src/tests/demo-integrated-a-static-contract.mjs'
const source = readFileSync(specPath, 'utf8')

function validate(candidate) {
  return spawnSync('node', [guardPath, '--stdin'], { input: candidate, encoding: 'utf8' })
}

const plannedUi = `${source}\nasync function task6VisibleUiObservation(page: Page) {\n  const response = page.waitForResponse((item) => item.status() === 200 && item.url().includes('/oa-reply'))\n  await page.goto(\`${'${baseUrl}'}/official-workflows/oa-reply?package_id=planned\`, { waitUntil: 'domcontentloaded' })\n  await response\n}\nasync function task6CheckpointLedger() {\n  await writeFile(path.join(evidenceDir!, 'task6-checkpoints.json'), JSON.stringify({ checkpoints: [] }, null, 2))\n}\n`
const accepted = validate(plannedUi)
assert.equal(accepted.status, 0, accepted.stdout || accepted.stderr)

const foreignNavigation = validate(plannedUi.replace("`${baseUrl}/official-workflows/oa-reply?package_id=planned`", "'https://example.test/escape'"))
assert.notEqual(foreignNavigation.status, 0, 'foreign navigation must fail closed')

const arbitraryWrite = validate(plannedUi.replace("path.join(evidenceDir!, 'task6-checkpoints.json')", "'/tmp/direct-api.html'"))
assert.notEqual(arbitraryWrite.status, 0, 'arbitrary write paths must fail closed')

const directNetwork = validate(`${source}\nasync function forbidden(page: Page) { await page.request.post('/api/v1/documents/fake/attachments') }\n`)
assert.notEqual(directNetwork.status, 0, 'direct network calls must fail closed')

console.log('demo_integrated_ui_boundary=PASS')
