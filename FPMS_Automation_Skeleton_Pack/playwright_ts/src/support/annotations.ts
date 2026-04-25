import { test } from "@playwright/test";

import type { BoundaryCase, TestCase } from "./types";

export function annotateCase(tc: TestCase | BoundaryCase): void {
  const info = test.info();
  if ("priority" in tc) {
    info.annotations.push({ type: "priority", description: tc.priority });
    info.annotations.push({ type: "wave", description: tc.wave });
    if (tc.categories.length > 0) {
      info.annotations.push({ type: "category", description: tc.categories.join(",") });
    }
    if (tc.coverage_ids.length > 0) {
      info.annotations.push({ type: "coverage", description: tc.coverage_ids.join(",") });
    }
  } else {
    info.annotations.push({ type: "boundary", description: `${tc.object}:${tc.boundary_point}` });
  }
}
