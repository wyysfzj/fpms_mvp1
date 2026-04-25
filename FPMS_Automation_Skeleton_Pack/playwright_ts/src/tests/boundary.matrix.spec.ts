import { test } from "../fixtures/fpms.fixtures";
import { loadBoundaryCases } from "../support/dataLoader";
import { executeBoundaryCase } from "../support/router";

const cases = loadBoundaryCases();

for (const tc of cases) {
  test(`${tc.id} @BOUNDARY ${tc.object}`, async ({
    page,
    request,
    runId,
    api,
    db,
    loginPage,
    casePage,
    documentPage,
    taskPage,
    feePage,
    billingPage,
    reportPage,
  }) => {
    const ctx = { page, request, runId, api, db, loginPage, casePage, documentPage, taskPage, feePage, billingPage, reportPage };
    await executeBoundaryCase(tc, ctx);
  });
}
