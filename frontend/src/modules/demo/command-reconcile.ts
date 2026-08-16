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
      throw new CommandReconciliationError(`unexpected command status ${response.status}`)
    }
    if (attempt === 3) break
    await wait()
    response = await readCommand()
  }
  throw new CommandReconciliationError('command remained in progress')
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
