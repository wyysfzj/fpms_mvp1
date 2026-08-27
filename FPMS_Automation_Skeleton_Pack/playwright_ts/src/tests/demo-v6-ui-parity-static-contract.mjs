import assert from 'node:assert/strict'
import { existsSync, readFileSync } from 'node:fs'
import path from 'node:path'
import { pathToFileURL, fileURLToPath } from 'node:url'

const HERE = path.dirname(fileURLToPath(import.meta.url))
const PLAYWRIGHT_ROOT = path.resolve(HERE, '../..')
const WORKTREE_ROOT = path.resolve(PLAYWRIGHT_ROOT, '../..')
const CANONICAL_ROOT = path.resolve(WORKTREE_ROOT, '../..')
const compilerPath = [
  path.join(PLAYWRIGHT_ROOT, 'node_modules/typescript/lib/typescript.js'),
  path.join(CANONICAL_ROOT, 'FPMS_Automation_Skeleton_Pack/playwright_ts/node_modules/typescript/lib/typescript.js'),
].find(existsSync)
assert.ok(compilerPath, 'installed TypeScript compiler API is required for the AST gate')
const ts = (await import(pathToFileURL(compilerPath).href)).default
const STRICT_SPEC = path.join(HERE, 'demo-v6-ui-parity.live-backend.spec.ts')
const CONTRACT = JSON.parse(readFileSync(path.join(PLAYWRIGHT_ROOT, '../data/testcases/demo_v6_ui_parity_v1.json'), 'utf8'))

class StaticContractError extends Error {}

const FORBIDDEN_MODULES = new Set([
  'axios', 'http', 'https', 'node:http', 'node:https', 'sqlite3', 'sqlalchemy',
])
const FORBIDDEN_IDENTIFIERS = new Set([
  'APIRequestContext', 'SessionLocal', 'axios', 'fetch', 'mock', 'mocked', 'sqlite3', 'sqlalchemy',
])
const FORBIDDEN_MEMBERS = new Set([
  'page.addInitScript', 'page.evaluate', 'page.evaluateHandle', 'page.exposeFunction',
  'page.request', 'page.route', 'route.fulfill',
])

function fail(filename, node, message) {
  const location = node.getSourceFile().getLineAndCharacterOfPosition(node.getStart())
  throw new StaticContractError(`${filename}:${location.line + 1}:${location.character + 1}: ${message}`)
}

function propertyPath(node) {
  if (ts.isIdentifier(node)) return node.text
  if (ts.isPropertyAccessExpression(node)) return `${propertyPath(node.expression)}.${node.name.text}`
  return ''
}

function bindingContainsRequest(name) {
  if (ts.isIdentifier(name)) return name.text === 'request'
  return name.elements.some(element => ts.isBindingElement(element) && bindingContainsRequest(element.name))
}

function parseProgram(filename, source) {
  const program = ts.createSourceFile(filename, source, ts.ScriptTarget.Latest, true, ts.ScriptKind.TS)
  const syntaxError = program.parseDiagnostics?.[0]
  if (syntaxError) throw new StaticContractError(`${filename}: TypeScript parse error: ${syntaxError.messageText}`)
  return program
}

function auditProgram(filename, program) {
  const imports = []
  const visit = node => {
    if (ts.isImportDeclaration(node) && ts.isStringLiteral(node.moduleSpecifier)) {
      const moduleName = node.moduleSpecifier.text
      imports.push(moduleName)
      if (FORBIDDEN_MODULES.has(moduleName)) fail(filename, node, `forbidden module ${moduleName}`)
      if (/(^|\/)backend(\/|$)|(^|\/)scripts(\/|$)/.test(moduleName)) {
        fail(filename, node, 'backend/script import is forbidden')
      }
    }
    if (ts.isIdentifier(node) && FORBIDDEN_IDENTIFIERS.has(node.text)) {
      fail(filename, node, `forbidden identifier ${node.text}`)
    }
    if (ts.isParameter(node) && bindingContainsRequest(node.name)) {
      fail(filename, node, 'Playwright request fixture is forbidden')
    }
    if (ts.isPropertyAccessExpression(node)) {
      const member = propertyPath(node)
      if ([...FORBIDDEN_MEMBERS].some(value => member === value || member.startsWith(`${value}.`))) {
        fail(filename, node, `forbidden browser escape ${member}`)
      }
    }
    if (
      (ts.isStringLiteral(node) || ts.isNoSubstitutionTemplateLiteral(node))
      && node.text.includes('/demo/abc')
    ) fail(filename, node, '/demo/abc is forbidden')
    if (
      ts.isCallExpression(node)
      && ts.isPropertyAccessExpression(node.expression)
      && ['mock', 'mockImplementation', 'fulfill'].includes(node.expression.name.text)
    ) fail(filename, node, 'mock/dynamic fulfillment is forbidden')
    ts.forEachChild(node, visit)
  }
  visit(program)
  return imports
}

function literalText(node) {
  return ts.isStringLiteral(node) || ts.isNoSubstitutionTemplateLiteral(node) ? node.text : null
}

function auditStrictEvidenceShape(filename, program, contract) {
  const stageBindings = new Map()
  const assertionCalls = new Map()
  let passiveResponseObservation = false
  const visit = node => {
    const text = literalText(node)
    if (text && [
      'VISIBLE_UI_SURFACE_OBSERVED',
      'REQUIRED_ASSERTION_BOUND_TO_VISIBLE_UI_EVIDENCE',
    ].includes(text)) fail(filename, node, `generic result token is forbidden: ${text}`)
    if (ts.isCallExpression(node) && ts.isIdentifier(node.expression)) {
      if (node.expression.text === 'bindStageAction') {
        const stage = literalText(node.arguments[0])
        const actionId = literalText(node.arguments[1])
        const mutationExpected = node.arguments[2]?.kind === ts.SyntaxKind.TrueKeyword
          ? true : node.arguments[2]?.kind === ts.SyntaxKind.FalseKeyword ? false : null
        if (!stage || !actionId || mutationExpected === null) {
          fail(filename, node, 'bindStageAction requires literal stage, action id, and mutation boolean')
        }
        const rows = stageBindings.get(stage) || []
        rows.push({ actionId, mutationExpected })
        stageBindings.set(stage, rows)
      }
      if (node.expression.text === 'assertStrict') {
        const assertionId = literalText(node.arguments[0])
        if (!assertionId) fail(filename, node, 'assertStrict requires one literal assertion id')
        assertionCalls.set(assertionId, (assertionCalls.get(assertionId) || 0) + 1)
      }
    }
    if (
      ts.isPropertyAccessExpression(node)
      && propertyPath(node) === 'page.on'
      && node.parent && ts.isCallExpression(node.parent)
      && literalText(node.parent.arguments[0]) === 'response'
    ) passiveResponseObservation = true
    ts.forEachChild(node, visit)
  }
  visit(program)
  for (const stage of Array.from({ length: 11 }, (_, index) => String(index + 1).padStart(2, '0'))) {
    const bindings = stageBindings.get(stage) || []
    if (!bindings.length) throw new StaticContractError(`${filename}: missing stage ${stage} action binding`)
    if (stage === '11') {
      if (!bindings.some(binding => binding.mutationExpected === false)) {
        throw new StaticContractError(`${filename}: stage 11 must bind a read-only visible action`)
      }
    } else if (!bindings.some(binding => binding.mutationExpected === true)) {
      throw new StaticContractError(`${filename}: stage ${stage} must bind a visible business mutation`)
    }
  }
  const expectedAssertions = contract.strict_assertions.map(row => row.assertion_key)
  for (const assertionId of expectedAssertions) {
    if (assertionCalls.get(assertionId) !== 1) {
      throw new StaticContractError(`${filename}: strict assertion ${assertionId} must be independent and exact once`)
    }
  }
  const unknownAssertions = [...assertionCalls].filter(([key]) => !expectedAssertions.includes(key))
  if (unknownAssertions.length) {
    throw new StaticContractError(`${filename}: unknown strict assertion ${unknownAssertions[0][0]}`)
  }
  if (!passiveResponseObservation) {
    throw new StaticContractError(`${filename}: passive page response observation is required`)
  }
}

function resolveRelativeImport(sourceName, importName, sources) {
  const base = path.posix.normalize(path.posix.join(path.posix.dirname(sourceName), importName))
  const candidate = [base, `${base}.ts`, `${base}.tsx`, `${base}.mjs`, `${base}/index.ts`]
    .find(name => sources.has(name))
  if (!candidate) throw new StaticContractError(`${sourceName}: unresolved relative import ${importName}`)
  return candidate
}

function auditSourceGraph(entry, sources) {
  const visited = new Set()
  const visit = sourceName => {
    if (visited.has(sourceName)) return
    visited.add(sourceName)
    const source = sources.get(sourceName)
    if (source === undefined) throw new StaticContractError(`source is absent: ${sourceName}`)
    const imports = auditProgram(sourceName, parseProgram(sourceName, source))
    for (const importName of imports) {
      if (importName.startsWith('.')) visit(resolveRelativeImport(sourceName, importName, sources))
    }
  }
  visit(entry)
}

function auditFileGraph(entryPath) {
  const sources = new Map()
  const load = filePath => {
    if (sources.has(filePath)) return
    const source = readFileSync(filePath, 'utf8')
    sources.set(filePath, source)
    for (const importName of auditProgram(filePath, parseProgram(filePath, source))) {
      if (!importName.startsWith('.')) continue
      const base = path.resolve(path.dirname(filePath), importName)
      const candidate = [base, `${base}.ts`, `${base}.tsx`, `${base}.mjs`, path.join(base, 'index.ts')]
        .find(existsSync)
      if (!candidate) throw new StaticContractError(`${filePath}: unresolved relative import ${importName}`)
      load(candidate)
    }
  }
  load(entryPath)
  auditSourceGraph(entryPath, sources)
}

const INVALID_FIXTURES = {
  request_fixture: `import { test } from '@playwright/test'; test('x', async ({ request }) => request.get('/x'))`,
  api_request_context: `import type { APIRequestContext } from '@playwright/test'; let client: APIRequestContext`,
  page_request: `async function x(page) { await page.request.post('/x') }`,
  direct_fetch: `async function x() { await fetch('/api/v1/x') }`,
  axios_client: `import axios from 'axios'; axios.post('/api/v1/x')`,
  node_http: `import http from 'node:http'; http.request('http://localhost')`,
  sql_backend: `import sqlite3 from 'sqlite3'; sqlite3.Database('run.db')`,
  evaluate_injection: `async function x(page) { await page.evaluate(() => localStorage.clear()) }`,
  route_mock: `async function x(page) { await page.route('**/*', route => route.fulfill({ body: '{}' })) }`,
  demo_abc: `async function x(page) { await page.goto('/demo/abc') }`,
}
for (const [name, source] of Object.entries(INVALID_FIXTURES)) {
  assert.throws(
    () => auditSourceGraph('fixture.ts', new Map([['fixture.ts', source]])),
    StaticContractError,
    `negative fixture must reject: ${name}`,
  )
}
const transitiveSources = new Map([
  ['entry.ts', `import './helper'; export const ok = true`],
  ['helper.ts', `export async function bypass(page) { await page.request.get('/api/v1/x') }`],
])
assert.throws(
  () => auditSourceGraph('entry.ts', transitiveSources),
  StaticContractError,
  'transitive bypass fixture must reject',
)

const positiveShapeSource = [
  `page.on('response', response => response.status())`,
  ...Array.from({ length: 11 }, (_, index) => {
    const stage = String(index + 1).padStart(2, '0')
    return `bindStageAction('${stage}', 'stage-${stage}-visible-action', ${stage === '11' ? 'false' : 'true'})`
  }),
  ...CONTRACT.strict_assertions.map(row => `assertStrict('${row.assertion_key}', true)`),
].join('\n')
assert.doesNotThrow(
  () => auditStrictEvidenceShape('positive-shape.ts', parseProgram('positive-shape.ts', positiveShapeSource), CONTRACT),
  'complete independent stage/action/assertion shape must pass',
)
assert.throws(
  () => auditStrictEvidenceShape(
    'generic-result.ts',
    parseProgram('generic-result.ts', `${positiveShapeSource}\nconst result = 'VISIBLE_UI_SURFACE_OBSERVED'`),
    CONTRACT,
  ),
  StaticContractError,
  'generic result token must reject',
)
assert.throws(
  () => auditStrictEvidenceShape(
    'collapsed-assertion.ts',
    parseProgram(
      'collapsed-assertion.ts',
      positiveShapeSource.replace(/assertStrict\('[^']+', true\)\n/, ''),
    ),
    CONTRACT,
  ),
  StaticContractError,
  'collapsed strict assertion must reject',
)

assert.ok(existsSync(STRICT_SPEC), `strict spec is absent: ${STRICT_SPEC}`)
auditFileGraph(STRICT_SPEC)
auditStrictEvidenceShape(STRICT_SPEC, parseProgram(STRICT_SPEC, readFileSync(STRICT_SPEC, 'utf8')), CONTRACT)
assert.match(readFileSync(STRICT_SPEC, 'utf8'), /test\s*\(/, 'strict spec must contain an executable test')
console.log('demo-v6-ui-parity static contract: PASS')
