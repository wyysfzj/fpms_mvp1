import { test } from "@playwright/test";

import { annotateCase } from "./annotations";
import type { BoundaryCase, CaseHandler, ExecutionContext, TestCase } from "./types";
import { isSkeleton } from "./helpers";
import { waveW0Handlers } from "../handlers/waveW0";
import { waveAHandlers } from "../handlers/waveA";
import { waveBHandlers } from "../handlers/waveB";
import { waveCHandlers } from "../handlers/waveC";
import { waveG0Handlers } from "../handlers/waveG0";
import { waveDHandlers } from "../handlers/waveD";
import { waveEHandlers } from "../handlers/waveE";
import { waveFHandlers } from "../handlers/waveF";
import { waveGHandlers } from "../handlers/waveG";
import { waveHHandlers } from "../handlers/waveH";
import { waveXHandlers } from "../handlers/waveX";
import { boundaryHandlers } from "../handlers/boundary";

const handlers: Record<string, CaseHandler<any>> = {
  ...waveW0Handlers,
  ...waveAHandlers,
  ...waveBHandlers,
  ...waveCHandlers,
  ...waveG0Handlers,
  ...waveDHandlers,
  ...waveEHandlers,
  ...waveFHandlers,
  ...waveGHandlers,
  ...waveHHandlers,
  ...waveXHandlers,
  ...boundaryHandlers,
};

export async function executeCase(tc: TestCase, ctx: ExecutionContext): Promise<void> {
  annotateCase(tc);
  const handler = handlers[tc.id];
  test.skip(isSkeleton(handler), `Skeleton only: ${tc.id} | ${tc.topic}`);
  await handler(ctx, tc);
}

export async function executeBoundaryCase(tc: BoundaryCase, ctx: ExecutionContext): Promise<void> {
  annotateCase(tc);
  const handler = handlers[tc.id];
  test.skip(isSkeleton(handler), `Boundary skeleton only: ${tc.id} | ${tc.object}`);
  await handler(ctx, tc);
}
