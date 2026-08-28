import assert from 'node:assert/strict'
import { Buffer } from 'node:buffer'
import { readFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'
import ts from 'typescript'

const frontendRoot = join(dirname(fileURLToPath(import.meta.url)), '..')
const read = (path) => readFileSync(join(frontendRoot, path), 'utf8')
const casesApi = read('src/api/cases.ts')
const casesTypes = read('src/api/cases.types.ts')

function importFunction(source, name) {
  const sourceFile = ts.createSourceFile(
    'contract.ts',
    source,
    ts.ScriptTarget.Latest,
    true,
    ts.ScriptKind.TS,
  )
  const declaration = sourceFile.statements.find(
    (statement) => ts.isFunctionDeclaration(statement) && statement.name?.text === name,
  )
  assert.ok(declaration, `missing executable function: ${name}`)
  const compiled = ts.transpileModule(
    `${declaration.getText(sourceFile)}\nexport { ${name} }`,
    { compilerOptions: { module: ts.ModuleKind.ESNext, target: ts.ScriptTarget.ES2022 } },
  ).outputText
  return import(
    `data:text/javascript;base64,${Buffer.from(compiled).toString('base64')}#${Math.random()}`,
  )
}

const { mapCase } = await importFunction(casesApi, 'mapCase')
const projected = mapCase({
  id: 'case-1',
  case_no: 'CYIP-CN-INV-1',
  client_id: null,
  status: 'GRANT_PENDING',
  workflow_status: 'GRANT_PENDING',
  business_stage: 'GRANT_REGISTRATION_IN_PROGRESS',
  official_procedure_stage: 'GRANT_REGISTRATION',
  legal_status: 'APPLICATION_PENDING',
  updated_at: '2026-08-28T10:00:00',
})
assert.equal(projected.workflow_status, 'GRANT_PENDING')
assert.equal(projected.business_stage, 'GRANT_REGISTRATION_IN_PROGRESS')
assert.equal(projected.official_procedure_stage, 'GRANT_REGISTRATION')
assert.equal(projected.legal_status, 'APPLICATION_PENDING')
assert.equal(projected.updated_at, '2026-08-28T10:00:00')

const legacy = mapCase({
  id: 'case-2',
  case_no: 'LEGACY-2',
  client_id: null,
  status: 'PUBLISHED',
  updated_at: null,
})
assert.equal(legacy.workflow_status, 'PUBLISHED')
assert.equal(legacy.updated_at, '')

const missingStatus = mapCase({
  id: 'case-3',
  case_no: 'MISSING-STATUS-3',
  client_id: null,
  updated_at: null,
})
assert.equal(missingStatus.workflow_status, undefined)
for (const field of [
  'workflow_status',
  'business_stage',
  'official_procedure_stage',
  'legal_status',
]) {
  assert.match(casesTypes, new RegExp(`${field}\\?: string`))
}

const workflow = read('src/constants/workflow.ts')
const labels = read('src/constants/labels.zh.ts')
const caseList = read('src/modules/cases/pages/CaseList.vue')
const dashboardApi = read('src/modules/dashboard/dashboard.api.ts')
const workflowTable = read('src/modules/dashboard/components/WorkflowCaseTable.vue')
const caseStepper = read('src/modules/cases/components/CaseStepper.vue')

assert.match(workflow, /GRANT_PENDING:.*stepText: '授权登记'/)
assert.match(workflow, /stepLabel: WORKFLOW_STEPS\[stepIndex\]\.label/)
assert.match(workflow, /stepNoText: `第\$\{stepIndex \+ 1\}步\/5`/)
assert.match(labels, /filterStatus: '流程状态'/)
assert.match(labels, /colStep: '当前阶段'/)
assert.match(labels, /colStatus: '流程状态'/)
assert.match(labels, /grantStage: '授权阶段'/)
assert.match(labels, /unknownStatus: '未知流程状态'/)
assert.match(labels, /stagePending: '阶段待确认'/)
for (const source of [caseList, workflowTable]) {
  assert.match(source, /c\.workflow_status \|\| c\.status/)
  assert.match(source, /const status = getWorkflowStatus\(c\)/)
  assert.match(source, /if \(!status\)/)
  assert.match(source, /ZH\.workflow\.unknownStatus/)
  assert.match(source, /ZH\.workflow\.stagePending/)
  assert.match(source, /getCaseWorkflow\(status\)/)
  assert.doesNotMatch(source, /getCaseWorkflow\(getWorkflowStatus\(c\)\)/)
  assert.match(source, /flow\.rule\.stepText/)
  assert.match(source, /第\$\{flow\.stepIndex \+ 1\}阶段\/5/)
}
assert.match(caseList, /row\.filing_date \|\| '待录入'/)
assert.equal(dashboardApi.match(/const status = c\.workflow_status \|\| c\.status/g)?.length, 2)
assert.equal(dashboardApi.match(/if \(!status\)/g)?.length, 2)
assert.equal(dashboardApi.match(/getStatusRule\(status\)/g)?.length, 2)
assert.match(dashboardApi, /step\.key === 'GRANTED' \? ZH\.workflow\.grantStage : step\.label/)
assert.match(caseStepper, /getCaseWorkflow\(props\.status\)/)
assert.doesNotMatch(caseStepper, /workflow_status|授权阶段|阶段\/5/)

console.log('case list lifecycle projection contract: PASS')
