type ErrorShape = {
  code?: unknown
  isAxiosError?: unknown
  response?: unknown
  status?: unknown
}

export type CommandReadStatus = 'COMPLETED' | 'IN_PROGRESS' | 'ABSENT' | 'INVALID'

export function shouldReconcileUnknownCommand(error: unknown): boolean {
  if (typeof error !== 'object' || error === null) return false
  const candidate = error as ErrorShape
  if (candidate.isAxiosError === true) return candidate.response === undefined
  return candidate.status === 0 && candidate.code === 'UNKNOWN_ERROR'
}

export function classifyCommandReadStatus(status: number): CommandReadStatus {
  if (status === 200) return 'COMPLETED'
  if (status === 202) return 'IN_PROGRESS'
  if (status === 404) return 'ABSENT'
  return 'INVALID'
}
