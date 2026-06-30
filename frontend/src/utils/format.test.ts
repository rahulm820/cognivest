import { describe, expect, it } from "vitest";
import {
  formatCompact,
  formatCurrency,
  formatDate,
  formatNumber,
  formatPercent,
} from "./format";

describe("format utils", () => {
  it("formats currency", () => {
    expect(formatCurrency(1234.5)).toBe("$1,234.50");
  });

  it("formats numbers with grouping", () => {
    expect(formatNumber(12345)).toBe("12,345");
    expect(formatNumber(12.345, 2)).toBe("12.35");
  });

  it("formats percentages", () => {
    expect(formatPercent(0.0825)).toBe("8.25%");
  });

  it("formats compact numbers", () => {
    expect(formatCompact(1_500_000)).toBe("1.5M");
  });

  it("formats ISO dates", () => {
    expect(formatDate("2026-03-03T10:00:00Z")).toBe("Mar 3, 2026");
  });

  it("handles empty and invalid dates", () => {
    expect(formatDate("")).toBe("");
    expect(formatDate(null)).toBe("");
    expect(formatDate("not-a-date")).toBe("Invalid date");
  });
});
