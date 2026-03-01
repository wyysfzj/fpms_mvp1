export type FieldErrors = Map<string, string[]>

function pushFieldError(fieldErrors: FieldErrors, field: string, message: string): void {
  if (!field || !message) return
  const existing = fieldErrors.get(field) || []
  existing.push(message)
  fieldErrors.set(field, existing)
}

function asMessage(value: unknown): string | null {
  if (typeof value === 'string') return value
  if (typeof value === 'number' || typeof value === 'boolean') return String(value)
  return null
}

function resolveLocField(loc: unknown): string | null {
  if (!Array.isArray(loc)) return null
  const filtered = loc
    .map((part) => (typeof part === 'string' || typeof part === 'number' ? String(part) : ''))
    .filter(Boolean)
    .filter((part) => part !== 'body' && part !== 'query' && part !== 'path')

  if (filtered.length === 0) return null
  return filtered[filtered.length - 1]
}

function mapObjectEntry(fieldErrors: FieldErrors, key: string, value: unknown): void {
  const direct = asMessage(value)
  if (direct) {
    pushFieldError(fieldErrors, key, direct)
    return
  }

  if (Array.isArray(value)) {
    for (const item of value) {
      const message = asMessage(item)
      if (message) {
        pushFieldError(fieldErrors, key, message)
      } else if (item && typeof item === 'object' && 'msg' in item) {
        const nestedMsg = asMessage((item as { msg?: unknown }).msg)
        if (nestedMsg) pushFieldError(fieldErrors, key, nestedMsg)
      }
    }
    return
  }

  if (value && typeof value === 'object' && 'msg' in value) {
    const nestedMsg = asMessage((value as { msg?: unknown }).msg)
    if (nestedMsg) {
      pushFieldError(fieldErrors, key, nestedMsg)
    }
  }
}

/**
 * Maps backend 422 `error.details` payloads into Element Plus field errors.
 * Supported shapes:
 * - { field_name: "error" }
 * - { field_name: ["error1", "error2"] }
 * - { errors: [{ loc: ["body", "field"], msg: "..." }] } (Pydantic style)
 */
export function mapValidationDetailsToFieldErrors(details?: unknown): FieldErrors {
  const fieldErrors: FieldErrors = new Map()

  if (!details) return fieldErrors

  if (Array.isArray(details)) {
    for (const entry of details) {
      if (!entry || typeof entry !== 'object') continue

      const locField = resolveLocField((entry as { loc?: unknown }).loc)
      const message = asMessage((entry as { msg?: unknown }).msg)
      if (locField && message) {
        pushFieldError(fieldErrors, locField, message)
      }
    }
    return fieldErrors
  }

  if (typeof details !== 'object') return fieldErrors

  const record = details as Record<string, unknown>
  if (Array.isArray(record.errors)) {
    for (const entry of record.errors) {
      if (!entry || typeof entry !== 'object') continue
      const locField = resolveLocField((entry as { loc?: unknown }).loc)
      const message = asMessage((entry as { msg?: unknown }).msg)
      if (locField && message) {
        pushFieldError(fieldErrors, locField, message)
      }
    }
  }

  for (const [key, value] of Object.entries(record)) {
    if (key === 'errors' || key === 'required_perm') continue
    mapObjectEntry(fieldErrors, key, value)
  }

  return fieldErrors
}
