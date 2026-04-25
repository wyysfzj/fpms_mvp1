import fs from "node:fs";
import path from "node:path";
import YAML from "yaml";

import type { BoundaryCase, TestCase } from "./types";

function projectRoot(): string {
  return path.resolve(__dirname, "../../..");
}

function expandRunId<T>(value: T, runId: string): T {
  if (typeof value === "string") {
    return value.replaceAll("${RUN_ID}", runId) as T;
  }
  if (Array.isArray(value)) {
    return value.map((item) => expandRunId(item, runId)) as T;
  }
  if (value && typeof value === "object") {
    const output: Record<string, unknown> = {};
    for (const [key, inner] of Object.entries(value as Record<string, unknown>)) {
      output[key] = expandRunId(inner, runId);
    }
    return output as T;
  }
  return value;
}

function readYaml<T>(relativePath: string): T {
  const fullPath = path.join(projectRoot(), relativePath);
  const raw = fs.readFileSync(fullPath, "utf8");
  return YAML.parse(raw) as T;
}

export function loadWaveCases(wave: string, runId = process.env.FPMS_RUN_ID || "LOCAL-RUN-001"): TestCase[] {
  const payload = readYaml<{ cases: TestCase[] }>(`data/testcases/by_wave/${wave.toLowerCase()}.yaml`);
  return payload.cases.map((item) => expandRunId(item, runId));
}

export function loadBoundaryCases(runId = process.env.FPMS_RUN_ID || "LOCAL-RUN-001"): BoundaryCase[] {
  const payload = readYaml<{ boundary_cases: BoundaryCase[] }>("data/boundary/boundary_matrix.yaml");
  return payload.boundary_cases.map((item) => expandRunId(item, runId));
}

export function loadAllCases(runId = process.env.FPMS_RUN_ID || "LOCAL-RUN-001"): TestCase[] {
  const payload = readYaml<{ testcases: TestCase[] }>("data/testcases/all_testcases.yaml");
  return payload.testcases.map((item) => expandRunId(item, runId));
}
