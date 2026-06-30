"use client";

import * as React from "react";
import { useRouter } from "next/navigation";
import { Search } from "lucide-react";
import { Input } from "@/components/ui";

/**
 * Ticker search box — navigates to the company detail page on submit.
 * TODO(phase-5): add async ticker autocomplete from the backend.
 */
export function TickerSearch() {
  const router = useRouter();
  const [value, setValue] = React.useState("");

  function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    const ticker = value.trim().toUpperCase();
    if (ticker) router.push(`/company/${ticker}`);
  }

  return (
    <form onSubmit={handleSubmit} className="relative">
      <Search className="pointer-events-none absolute left-2 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
      <Input
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder="Search ticker…"
        aria-label="Search ticker"
        className="pl-8"
      />
    </form>
  );
}
