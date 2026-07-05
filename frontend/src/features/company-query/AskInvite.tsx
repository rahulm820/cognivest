"use client";

import { MessageSquareText } from "lucide-react";

export interface AskInviteProps {
  ticker: string;
  /** Seed a question into the QueryBox draft (not auto-sent). */
  onPick: (question: string) => void;
}

/** Per-ticker example questions surfaced in the pre-ask empty state. */
const EXAMPLES: Record<string, string[]> = {
  AAPL: ["Why did Apple move on its last earnings?", "What are Apple's supply-chain risks?"],
  MSFT: ["What's driving Microsoft's AI momentum?", "How is Microsoft's cloud segment doing?"],
  TSLA: ["What supply-chain risks affect Tesla?", "How did Tesla's latest deliveries land?"],
};

const FALLBACK = ["What moved the price recently?", "What are the key risks right now?"];

/**
 * Pre-ask invite — the workspace's first impression when nothing's been asked.
 * A gentle centered card that nudges the judge into the demo instead of an
 * empty input. Chips seed the QueryBox; the hint teaches the "remember:" mode.
 */
export function AskInvite({ ticker, onPick }: AskInviteProps) {
  const examples = EXAMPLES[ticker] ?? FALLBACK;

  return (
    <div className="rounded-xl border border-dashed border-border bg-surface/60 p-8 text-center">
      <span
        className="mx-auto flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10 text-primary"
        aria-hidden
      >
        <MessageSquareText className="h-5 w-5" />
      </span>
      <h2 className="mt-4 text-[16px] font-semibold text-foreground">
        Ask anything about {ticker}
      </h2>
      <p className="mx-auto mt-1.5 max-w-md text-[13px] leading-relaxed text-text-muted">
        Answers are grounded in {ticker}&apos;s price &amp; news — each source lands as a marker on
        the chart above.
      </p>

      <div className="mt-5 flex flex-wrap items-center justify-center gap-2">
        {examples.map((q) => (
          <button
            key={q}
            type="button"
            onClick={() => onPick(q)}
            className="rounded-full border border-border bg-surface px-3.5 py-2 text-[13px] text-foreground transition-all duration-200 ease-out hover:-translate-y-0.5 hover:border-primary/60"
          >
            {q}
          </button>
        ))}
      </div>

      <p className="mt-5 text-[12px] text-text-muted">
        Tip: start with{" "}
        <span className="rounded bg-surface-raised px-1.5 py-0.5 font-mono text-primary">
          remember:
        </span>{" "}
        to teach the agent a preference.
      </p>
    </div>
  );
}
