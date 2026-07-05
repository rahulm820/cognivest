"use client";

import * as React from "react";
import { PriceChart } from "@/components/charts/PriceChart";
import { DateRangePicker } from "@/components/common";
import { AgentMemoryRail } from "@/features/memory/AgentMemoryRail";
import { useCompanyPrice, useCompanyQuery } from "@/hooks";
import { useUiStore } from "@/store";
import { DEFAULT_PRICE_RANGE, SEEDED_TICKERS, type PriceRange } from "@/constants";
import { buildChartMarkers } from "@/utils/markers";
import { formatCurrency } from "@/utils/format";
import { normalizeError } from "@/services/api";
import { QueryBox, extractPreference } from "./QueryBox";
import { AnswerPanel } from "./AnswerPanel";
import { MemoryCard } from "./MemoryCard";
import { AskInvite } from "./AskInvite";

/** The ack prefix the backend emits for a "remember:" directive (exact match). */
const MEMORY_ACK_PREFIX = "Got it — I'll remember";

/** Choreography beats (ms): answer → +400ms chips → +300ms markers. */
const CHIPS_DELAY = 400;
const MARKERS_DELAY = CHIPS_DELAY + 300;

/**
 * Company workspace — the choreographed demo surface. Owns the price series and
 * the query mutation so the answer's citations can drive markers on the chart
 * above. Sequences the reveal beats (answer → chips → markers) and routes a
 * "remember:" ack into the memory treatment instead of an answer panel.
 */
export function CompanyWorkspace({ ticker }: { ticker: string }) {
  const [range, setRange] = React.useState<PriceRange>(DEFAULT_PRICE_RANGE);
  const price = useCompanyPrice(ticker, range);
  const query = useCompanyQuery(ticker);
  const addSessionMemory = useUiStore((s) => s.addSessionMemory);
  const prefillQuery = useUiStore((s) => s.prefillQuery);
  const setPrefillQuery = useUiStore((s) => s.setPrefillQuery);

  // A question staged from the dashboard, or an empty-state example chip, gets
  // seeded into the QueryBox draft (NOT auto-sent). Bumping `prefillKey` remounts
  // the box so its internal draft picks up the new `initialValue`.
  const [prefill, setPrefill] = React.useState("");
  const [prefillKey, setPrefillKey] = React.useState(0);

  const seedPrefill = React.useCallback((text: string) => {
    setPrefill(text);
    setPrefillKey((k) => k + 1);
  }, []);

  React.useEffect(() => {
    if (prefillQuery && prefillQuery.ticker === ticker) {
      seedPrefill(prefillQuery.question);
      setPrefillQuery(null);
    }
  }, [prefillQuery, ticker, seedPrefill, setPrefillQuery]);

  // Stable reference: React Query keeps `price.data` identity between renders,
  // so markers/effects downstream don't churn (and the marker card stays open).
  const bars = React.useMemo(() => price.data?.bars ?? [], [price.data]);
  const name = SEEDED_TICKERS.find((c) => c.ticker === ticker)?.name;
  const lastPrice = bars.at(-1)?.c;

  const [activeQuestion, setActiveQuestion] = React.useState("");
  const [showChips, setShowChips] = React.useState(false);
  const [revealMarkers, setRevealMarkers] = React.useState(false);
  const [memoryAck, setMemoryAck] = React.useState<{ text: string } | null>(null);
  const timers = React.useRef<ReturnType<typeof setTimeout>[]>([]);
  const memSeq = React.useRef(0);

  const clearTimers = React.useCallback(() => {
    timers.current.forEach((t) => clearTimeout(t));
    timers.current = [];
  }, []);

  React.useEffect(() => clearTimers, [clearTimers]);

  const markers = React.useMemo(
    () => (memoryAck ? [] : buildChartMarkers(query.data?.citations ?? [], bars)),
    [memoryAck, query.data, bars],
  );

  function handleAsk(question: string) {
    clearTimers();
    setShowChips(false);
    setRevealMarkers(false);
    setMemoryAck(null);
    setActiveQuestion(question);

    query.mutate(
      { question },
      {
        onSuccess: (data) => {
          if (data.answer.startsWith(MEMORY_ACK_PREFIX)) {
            const text = extractPreference(question);
            memSeq.current += 1;
            addSessionMemory({ id: `mem-${memSeq.current}`, text });
            setMemoryAck({ text });
            return;
          }
          // Answer path: stagger the reveal beats.
          timers.current.push(setTimeout(() => setShowChips(true), CHIPS_DELAY));
          timers.current.push(setTimeout(() => setRevealMarkers(true), MARKERS_DELAY));
        },
      },
    );
  }

  const hasResult = query.isPending || query.isError || memoryAck != null || query.data != null;

  return (
    <div className="flex flex-col gap-6 lg:flex-row">
      <div className="min-w-0 flex-1 space-y-6">
        {/* Header: ticker badge + name + current price + range picker */}
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <span className="rounded-lg border border-primary/40 bg-primary/10 px-2.5 py-1 text-sm font-semibold tracking-wide text-primary">
              {ticker}
            </span>
            <div>
              <h1 className="text-2xl font-semibold leading-tight text-foreground">
                {name ?? ticker}
              </h1>
              {price.isLoading ? (
                <div className="shimmer mt-1 h-4 w-24 rounded" />
              ) : lastPrice != null ? (
                <div className="text-[15px] tabular-nums text-text-muted">
                  {formatCurrency(lastPrice)}
                </div>
              ) : (
                <div className="text-[13px] text-text-muted">price unavailable</div>
              )}
            </div>
          </div>
          <div className="flex items-center gap-3">
            <span
              className="hidden rounded-md border border-border bg-surface-raised px-2 py-1 font-mono text-[11px] text-text-muted sm:inline-block"
              title="per-ticker Cognee dataset"
            >
              graph: company_{ticker}
            </span>
            <DateRangePicker value={range} onChange={setRange} />
          </div>
        </div>

        <PriceChart
          ticker={ticker}
          bars={bars}
          markers={markers}
          revealMarkers={revealMarkers}
          isLoading={price.isLoading}
          isError={price.isError}
        />

        <div className="space-y-4">
          <QueryBox
            key={prefillKey}
            ticker={ticker}
            disabled={query.isPending}
            onAsk={handleAsk}
            initialValue={prefill}
          />

          {!hasResult ? (
            <AskInvite ticker={ticker} onPick={seedPrefill} />
          ) : memoryAck ? (
            <MemoryCard text={memoryAck.text} />
          ) : (
            <AnswerPanel
              answer={query.data}
              question={activeQuestion}
              ticker={ticker}
              isLoading={query.isPending}
              isError={query.isError}
              showChips={showChips}
            />
          )}

          {query.isError && !query.isPending ? (
            <p className="sr-only">{normalizeError(query.error).message}</p>
          ) : null}
        </div>
      </div>

      <AgentMemoryRail />
    </div>
  );
}
