"use client";

import { PRICE_RANGES, type PriceRange } from "@/constants";
import { cn } from "@/utils/cn";

export interface DateRangePickerProps {
  value: PriceRange;
  onChange: (range: PriceRange) => void;
}

/**
 * Segmented range selector for the price chart / query window.
 * TODO(phase-5): support custom from/to date picking in addition to presets.
 */
export function DateRangePicker({ value, onChange }: DateRangePickerProps) {
  return (
    <div
      className="inline-flex items-center gap-0.5 rounded-lg border border-border bg-surface p-0.5"
      role="group"
      aria-label="Select range"
    >
      {PRICE_RANGES.map((range) => {
        const active = range === value;
        return (
          <button
            key={range}
            type="button"
            aria-pressed={active}
            onClick={() => onChange(range)}
            className={cn(
              "rounded-md px-2.5 py-1 text-[13px] font-medium uppercase transition-colors duration-150",
              active
                ? "bg-primary/15 text-primary"
                : "text-text-muted hover:bg-surface-raised hover:text-foreground",
            )}
          >
            {range}
          </button>
        );
      })}
    </div>
  );
}
