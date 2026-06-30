"use client";

import * as React from "react";
import { useAddTicker } from "@/hooks";
import { Button, Input } from "@/components/ui";

/**
 * Add-ticker modal feature.
 * TODO(phase-5): replace inline panel with a real shadcn Dialog + toast on error.
 */
export function AddTickerModal() {
  const [open, setOpen] = React.useState(false);
  const [ticker, setTicker] = React.useState("");
  const addTicker = useAddTicker();

  function handleAdd() {
    const value = ticker.trim().toUpperCase();
    if (!value) return;
    addTicker.mutate(value, { onSuccess: () => setOpen(false) });
  }

  if (!open) {
    return <Button onClick={() => setOpen(true)}>Add ticker</Button>;
  }

  return (
    <div className="flex items-center gap-2">
      <Input
        value={ticker}
        onChange={(e) => setTicker(e.target.value)}
        placeholder="e.g. AAPL"
        aria-label="Ticker"
        className="w-32"
      />
      <Button onClick={handleAdd} disabled={addTicker.isPending}>
        Add
      </Button>
      <Button variant="ghost" onClick={() => setOpen(false)}>
        Cancel
      </Button>
    </div>
  );
}
