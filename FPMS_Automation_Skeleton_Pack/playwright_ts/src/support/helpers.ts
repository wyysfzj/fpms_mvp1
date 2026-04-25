import type { CaseHandler } from "./types";

export function markSkeleton<T>(handler: CaseHandler<T>): CaseHandler<T> {
  (handler as CaseHandler<T> & { __skeleton__?: boolean }).__skeleton__ = true;
  return handler;
}

export function isSkeleton<T>(handler: CaseHandler<T> | undefined): boolean {
  if (!handler) return true;
  return Boolean((handler as CaseHandler<T> & { __skeleton__?: boolean }).__skeleton__);
}
