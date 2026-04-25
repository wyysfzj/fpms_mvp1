import fs from "node:fs";
import path from "node:path";

const scriptDir = path.dirname(new URL(import.meta.url).pathname);
const mockDir = path.resolve(scriptDir, "..");
const rootDir = path.resolve(mockDir, "..");

const pageFiles = [
  "01_01_case_dashboard",
  "02_02_new_case_intake_files",
  "03_03_new_case_document_checklist",
  "04_04_new_case_creation_preview",
  "05_05_case_workflow_document_dock",
  "06_06_case_dossier_timeline",
  "07_07_batch_filing_material_gate",
  "08_08_case_document_registration",
  "09_09_unfiled_file_tray",
  "10_10_doc_status_rule_matrix",
];

const bannedUiTerms = [
  "Document Dock",
  "LegalStatus",
  "ClientStatus",
  "RightsMaintenanceStatus",
  "Case-centric",
  "document-gated",
  "Mock ",
  "Step ",
];

function read(rel) {
  return fs.readFileSync(path.join(rootDir, rel), "utf8");
}

function assert(condition, message) {
  if (!condition) {
    throw new Error(message);
  }
}

function pngSize(filePath) {
  const buffer = fs.readFileSync(filePath);
  assert(buffer.readUInt32BE(0) === 0x89504e47, `${filePath} is not a PNG`);
  return {
    width: buffer.readUInt32BE(16),
    height: buffer.readUInt32BE(20),
  };
}

const requirements = JSON.parse(read("data/case_document_requirements_seed.json"));
const rules = JSON.parse(read("data/doc_status_rules_seed.json"));

const allowedCaseTypes = new Set(["NORMAL", "PCT_INTL", "PCT_NATL", "INVALIDATION", "PRIORITY", "CONSULTING", "SEARCH"]);
const allowedPatentCategories = new Set(["INV", "UM", "DES"]);
const allowedFlowDirs = new Set(["CN_DOMESTIC", "CN_OUTBOUND", "FOREIGN_INBOUND"]);

assert(requirements.length >= 8, "requirement seed should contain intake and filing rows");
for (const row of requirements) {
  assert(allowedCaseTypes.has(row.CaseType), `unsupported CaseType ${row.CaseType}`);
  assert(allowedPatentCategories.has(row.PatentCategory), `unsupported PatentCategory ${row.PatentCategory}`);
  assert(allowedFlowDirs.has(row.FlowDir), `unsupported FlowDir ${row.FlowDir}`);
  assert(row.RequirementCode, "missing RequirementCode");
  assert(row.GateScope, "missing GateScope");
}

assert(rules.length >= 6, "status rule seed should contain core official document rules");
for (const row of rules) {
  assert(row.RuleCode, "missing RuleCode");
  assert(row.DocumentEventType, `missing DocumentEventType for ${row.RuleCode}`);
  assert(row.IdempotencyKey, `missing IdempotencyKey for ${row.RuleCode}`);
}

const htmlFiles = [
  "mock-ui/index.html",
  "fpms_case_document_gate_mock_ui_index.html",
  ...pageFiles.map((file) => `mock-ui/pages/${file}.html`),
];

for (const rel of htmlFiles) {
  const html = read(rel);
  assert(html.includes('lang="zh-CN"'), `${rel} should declare zh-CN`);
  for (const term of bannedUiTerms) {
    assert(!html.includes(term), `${rel} contains banned UI term: ${term}`);
  }
}

for (const page of pageFiles) {
  const pngPath = path.join(rootDir, "mock-ui/screens", `${page}.png`);
  const svgPath = path.join(rootDir, "mock-ui/screens", `${page}.svg`);
  assert(fs.existsSync(pngPath), `missing screenshot ${pngPath}`);
  assert(fs.existsSync(svgPath), `missing svg ${svgPath}`);
  const size = pngSize(pngPath);
  assert(size.width === 1440 && size.height === 1000, `${page}.png should be 1440x1000`);
  const svg = fs.readFileSync(svgPath, "utf8");
  assert(svg.includes("data:image/png;base64,"), `${page}.svg should embed its PNG`);
}

console.log("Phase 1 package validation PASS");
