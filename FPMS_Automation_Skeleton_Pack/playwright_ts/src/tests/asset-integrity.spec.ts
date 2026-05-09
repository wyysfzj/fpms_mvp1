import { expect, test } from "../fixtures/fpms.fixtures";
import { loadAllCases, loadBoundaryCases } from "../support/dataLoader";

test("asset integrity", async () => {
  const allCases = loadAllCases();
  const boundaryCases = loadBoundaryCases();
  expect(allCases.length).toBe(170);
  expect(boundaryCases.length).toBe(20);
  expect(new Set(allCases.map((c) => c.id)).size).toBe(170);
});
