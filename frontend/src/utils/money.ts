const DEFAULT_CURRENCY = 'CNY'

export function normalizeCurrencyCode(value: string | null | undefined): string {
  const normalized = String(value ?? '').trim().toUpperCase()
  if (!normalized) return DEFAULT_CURRENCY

  try {
    new Intl.NumberFormat('zh-CN', { style: 'currency', currency: normalized }).format(0)
    return normalized
  } catch {
    return DEFAULT_CURRENCY
  }
}

export function formatMoney(value: number | string | null | undefined, currency?: string | null): string {
  const curr = normalizeCurrencyCode(currency)
  const amount = value == null || value === '' ? 0 : Number(value)
  if (!Number.isFinite(amount)) {
    return `${curr} ${String(value ?? 0)}`
  }
  return new Intl.NumberFormat('zh-CN', { style: 'currency', currency: curr }).format(amount)
}
