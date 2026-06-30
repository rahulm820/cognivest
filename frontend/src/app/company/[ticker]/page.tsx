"use client";

import * as React from "react";
import { PriceChart } from "@/components/charts/PriceChart";
import { DateRangePicker } from "@/components/common";
import { QueryBox } from "@/features/company-query";
import { useCompanyPrice } from "@/hooks";
import { DEFAULT_PRICE_RANGE, type PriceRange } from "@/constants";

/**
 * Company detail page — price chart + NL query box (ARCHITECTURE.md §3.3).
 * TODO(phase-5): deep-link range/question via query params; render NewsMarkerOverlay.
 */
export default function CompanyPage({ params }: { params: { ticker: string } }) {
  const ticker = params.ticker.toUpperCase();
  const [range, setRange] = React.useState<PriceRange>(DEFAULT_PRICE_RANGE);
  const { data } = useCompanyPrice(ticker, range);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">{ticker}</h1>
        <DateRangePicker value={range} onChange={setRange} />
      </div>
      <PriceChart ticker={ticker} bars={data?.bars ?? []} />
      <QueryBox ticker={ticker} />
    </div>
  );
}
