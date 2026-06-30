"use client";

import { PRICE_RANGES, type PriceRange } from "@/constants";
import { Button } from "@/components/ui";

export interface DateRangePickerProps {
  value: PriceRange;
  onChange: (range: PriceRange) => void;
}

/**
 * Range selector for the price chart / query window.
 * TODO(phase-5): support custom from/to date picking in addition to presets.
 */
export function DateRangePicker({ value, onChange }: DateRangePickerProps) {
  return (
    <div className="flex gap-1" role="group" aria-label="Select range">
      {PRICE_RANGES.map((range) => (
        <Button
          key={range}
          size="sm"
          variant={range === value ? "default" : "outline"}
          onClick={() => onChange(range)}
        >
          {range}
        </Button>
      ))}
    </div>
  );
}
