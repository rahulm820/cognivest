"use client";

import { useRouter } from "next/navigation";
import { Sparkles, ArrowUpRight } from "lucide-react";
import { useUiStore } from "@/store";

/**
 * "What can I ask?" — turns the space under the watchlist into a demo
 * accelerator. Each chip stages a question into the UI store and navigates to
 * that company page, where the QueryBox picks it up pre-filled (not auto-sent).
 */
const EXAMPLES = [
  { ticker: "AAPL", theme: "Earnings", question: "How did Apple's latest earnings land?" },
  {
    ticker: "TSLA",
    theme: "Supply chain",
    question: "What supply-chain risks are affecting Tesla?",
  },
  { ticker: "MSFT", theme: "Product", question: "What's driving Microsoft's AI momentum?" },
  {
    ticker: "AAPL",
    theme: "Memory",
    question: "remember: I care most about supply-chain risk",
  },
] as const;

export function AskPanel() {
  const router = useRouter();
  const setPrefillQuery = useUiStore((s) => s.setPrefillQuery);

  function launch(ticker: string, question: string) {
    setPrefillQuery({ ticker, question });
    router.push(`/company/${ticker}`);
  }

  return (
    <section className="rounded-xl border border-border bg-surface p-5 shadow-elevated">
      <div className="flex items-center gap-2">
        <Sparkles className="h-4 w-4 text-primary" />
        <h2 className="text-[13px] font-medium uppercase tracking-wide text-text-muted">
          What can I ask?
        </h2>
      </div>
      <p className="mt-1 text-[13px] text-text-muted">
        Jump straight in — these open the company workspace with the question ready.
      </p>
      <div className="mt-4 flex flex-wrap gap-2">
        {EXAMPLES.map(({ ticker, theme, question }) => (
          <button
            key={`${ticker}-${theme}`}
            type="button"
            onClick={() => launch(ticker, question)}
            className="group inline-flex items-center gap-2 rounded-full border border-border bg-surface-raised px-3.5 py-2 text-left text-[13px] text-foreground transition-all duration-200 ease-out hover:-translate-y-0.5 hover:border-primary/60"
          >
            <span className="rounded-md bg-primary/10 px-1.5 py-0.5 text-[11px] font-semibold text-primary">
              {ticker}
            </span>
            <span className="text-text-muted transition-colors group-hover:text-foreground">
              {question}
            </span>
            <ArrowUpRight className="h-3.5 w-3.5 shrink-0 text-text-muted transition-colors group-hover:text-primary" />
          </button>
        ))}
      </div>
    </section>
  );
}
