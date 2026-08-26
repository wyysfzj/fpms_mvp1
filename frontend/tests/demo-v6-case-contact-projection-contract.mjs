import assert from 'node:assert/strict'
import { Buffer } from 'node:buffer'
import { readFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'
import ts from 'typescript'

const frontendRoot = join(dirname(fileURLToPath(import.meta.url)), '..')
const read = (path) => readFileSync(join(frontendRoot, path), 'utf8')
const page = read('src/modules/cases/pages/CaseDetail.vue')
const clientsApi = read('src/api/clients.ts')

function importFunction(source, name, prelude = '') {
  const sourceFile = ts.createSourceFile('contract.ts', source, ts.ScriptTarget.Latest, true, ts.ScriptKind.TS)
  const declaration = sourceFile.statements.find(
    (statement) => ts.isFunctionDeclaration(statement) && statement.name?.text === name,
  )
  assert.ok(declaration, `missing executable function: ${name}`)
  const compiled = ts.transpileModule(
    `${prelude}\n${declaration.getText(sourceFile)}\nexport { ${name} }`,
    { compilerOptions: { module: ts.ModuleKind.ESNext, target: ts.ScriptTarget.ES2022 } },
  ).outputText
  return import(`data:text/javascript;base64,${Buffer.from(compiled).toString('base64')}#${Math.random()}`)
}

function importPrimaryProjection(source, contacts) {
  const script = source.split('<script setup lang="ts">', 2)[1]?.split('</script>', 1)[0] || ''
  const sourceFile = ts.createSourceFile('CaseDetail.ts', script, ts.ScriptTarget.Latest, true, ts.ScriptKind.TS)
  const statement = sourceFile.statements.find((candidate) => (
    ts.isVariableStatement(candidate)
    && candidate.declarationList.declarations.some(
      (declaration) => ts.isIdentifier(declaration.name) && declaration.name.text === 'primaryContacts',
    )
  ))
  assert.ok(statement, 'missing executable primaryContacts projection')
  const compiled = ts.transpileModule(
    `const clientContacts = { value: globalThis.__caseContacts }\n`
      + 'const computed = (select) => select()\n'
      + `${statement.getText(sourceFile)}\nexport { primaryContacts }`,
    { compilerOptions: { module: ts.ModuleKind.ESNext, target: ts.ScriptTarget.ES2022 } },
  ).outputText
  globalThis.__caseContacts = contacts
  return import(`data:text/javascript;base64,${Buffer.from(compiled).toString('base64')}#${Math.random()}`)
}

const contacts = [
  {
    id: 'primary-1', client_id: 'client-1', contact_name: '王芳', title: '知识产权经理',
    phone: null, mobile: null, email: 'wangfang@example.test', is_primary: true,
    created_at: '2026-08-26T10:00:00', updated_at: '2026-08-26T10:00:00',
  },
  {
    id: 'secondary-1', client_id: 'client-1', contact_name: '李明', title: '法务专员',
    phone: null, mobile: null, email: 'liming@example.test', is_primary: false,
    created_at: '2026-08-26T10:00:00', updated_at: '2026-08-26T10:00:00',
  },
  {
    id: 'primary-2', client_id: 'client-1', contact_name: '赵敏', title: null,
    phone: null, mobile: null, email: null, is_primary: true,
    created_at: '2026-08-26T10:00:00', updated_at: '2026-08-26T10:00:00',
  },
]
const calls = []
globalThis.__caseContactHttp = {
  async get(url) {
    calls.push({ method: 'GET', url })
    return { data: contacts }
  },
  async post() { throw new Error('contact projection must not POST') },
  async put() { throw new Error('contact projection must not PUT') },
  async patch() { throw new Error('contact projection must not PATCH') },
  async delete() { throw new Error('contact projection must not DELETE') },
}

const clients = await importFunction(
  clientsApi,
  'getClientContacts',
  'const http = globalThis.__caseContactHttp',
)
assert.deepEqual(await clients.getClientContacts('client-1'), contacts)
assert.deepEqual(calls, [{ method: 'GET', url: '/clients/client-1/contacts' }])

const projection = await importPrimaryProjection(page, contacts)
assert.deepEqual(projection.primaryContacts.map(({ id }) => id), ['primary-1', 'primary-2'])
assert.match(page, /import \{ getClientContacts \} from '\.\.\/\.\.\/\.\.\/api\/clients'/)
assert.match(page, /await getClientContacts\(String\(caseData\.value\.client_id\)\)/)
assert.match(page, /客户主联系人/)
assert.match(page, /v-for="contact in primaryContacts"/)
for (const field of ['姓名：{{ contact.contact_name', '职务：{{ contact.title', '邮箱：{{ contact.email']) {
  assert.match(page, new RegExp(field.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')))
}
assert.doesNotMatch(page, /contact\.(?:phone|mobile)/)

delete globalThis.__caseContacts
delete globalThis.__caseContactHttp
console.log('demo V6 case contact projection contract: PASS')
