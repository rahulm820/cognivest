/**
 * Presentation formatters for numbers, currency, and dates.
 * Pure functions, fully implemented (covered by unit tests).
 */

/** Format a number as USD currency, e.g. 1234.5 -> "$1,234.50". */
export function formatCurrency(value: number, currency = "USD", locale = "en-US"): string {
  return new Intl.NumberFormat(locale, {
    style: "currency",
    currency,
  }).format(value);
}

/** Format a number with grouping and fixed fraction digits, e.g. 12345 -> "12,345". */
export function formatNumber(value: number, fractionDigits = 0, locale = "en-US"): string {
  return new Intl.NumberFormat(locale, {
    minimumFractionDigits: fractionDigits,
    maximumFractionDigits: fractionDigits,
  }).format(value);
}

/** Format a 0-1 ratio as a percentage, e.g. 0.0825 -> "8.25%". */
export function formatPercent(ratio: number, fractionDigits = 2, locale = "en-US"): string {
  return new Intl.NumberFormat(locale, {
    style: "percent",
    minimumFractionDigits: fractionDigits,
    maximumFractionDigits: fractionDigits,
  }).format(ratio);
}

/**
 * Format an ISO date string as a short, human-readable date.
 * Returns an empty string for falsy input and "Invalid date" for unparseable input.
 */
export function formatDate(iso: string | null | undefined, locale = "en-US"): string {
  if (!iso) return "";
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return "Invalid date";
  return new Intl.DateTimeFormat(locale, {
    year: "numeric",
    month: "short",
    day: "numeric",
  }).format(date);
}

/** Compact a large number, e.g. 1_500_000 -> "1.5M". */
export function formatCompact(value: number, locale = "en-US"): string {
  return new Intl.NumberFormat(locale, { notation: "compact" }).format(value);
}
