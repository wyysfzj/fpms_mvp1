type ErrorShape = {
  code?: unknown
  isAxiosError?: unknown
  response?: unknown
  status?: unknown
}

export type CommandReadStatus = 'COMPLETED' | 'IN_PROGRESS' | 'ABSENT' | 'INVALID'

export interface CommandHttpResponse {
  status: number
  data: unknown
}

export class CommandReconciliationError extends Error {
  constructor(message: string) {
    super(message)
    this.name = 'CommandReconciliationError'
  }
}

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

export async function resolveCommandMutationResponse<T>(
  initialResponse: CommandHttpResponse,
  readCommand: () => Promise<CommandHttpResponse>,
  parseCompleted: (value: unknown) => T,
  wait: () => Promise<void> = () =>
    new Promise((resolve) => globalThis.setTimeout(resolve, 100)),
): Promise<T> {
  let response = initialResponse
  for (let attempt = 0; attempt < 4; attempt += 1) {
    if (response.status === 200 || response.status === 201) {
      return parseCompleted(response.data)
    }
    const classification = classifyCommandReadStatus(response.status)
    if (classification !== 'IN_PROGRESS') {
      throw new CommandReconciliationError(`命令状态异常（${response.status}）。`)
    }
    if (attempt === 3) break
    await wait()
    response = await readCommand()
  }
  throw new CommandReconciliationError('命令仍在处理中，请稍后重试。')
}

export async function reconcileThenRetryMutationOnce<T>(
  mutationError: unknown,
  readCommand: () => Promise<CommandHttpResponse>,
  retryMutation: () => Promise<CommandHttpResponse>,
  parseCompleted: (value: unknown) => T,
): Promise<T> {
  if (!shouldReconcileUnknownCommand(mutationError)) throw mutationError

  const durableResponse = await readCommand()
  const classification = classifyCommandReadStatus(durableResponse.status)
  if (classification === 'COMPLETED') {
    return parseCompleted(durableResponse.data)
  }
  if (classification === 'INVALID') throw mutationError

  // 传输结果未知时，先对账，再重试一次；重试沿用同一幂等键。
  const retryResponse = await retryMutation()
  return resolveCommandMutationResponse(retryResponse, readCommand, parseCompleted)
}

export async function reconcileUnknownMutationResult<T>(
  mutationError: unknown,
  readDurableState: () => Promise<T>,
  accept: (value: T) => boolean,
): Promise<T> {
  if (!shouldReconcileUnknownCommand(mutationError)) throw mutationError
  try {
    const value = await readDurableState()
    if (accept(value)) return value
  } catch {
    // The original mutation outcome remains authoritative when reconciliation fails.
  }
  throw mutationError
}
