import { test } from "../fixtures/fpms.fixtures";
import { loadWaveCases } from "../support/dataLoader";
import { executeCase } from "../support/router";

const cases = loadWaveCases("W0");

for (const tc of cases) {
  test(`${tc.id} @${tc.priority} ${tc.topic}`, async ({
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
    await executeCase(tc, ctx);
  });
}
