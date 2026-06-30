"use client";

import * as React from "react";
import { useCompanyQuery } from "@/hooks";
import { Button, Input } from "@/components/ui";
import { AnswerPanel } from "./AnswerPanel";

/**
 * Natural-language query box for a company.
 * TODO(phase-4): wire date-range filter from the Zustand store + deep-linking.
 */
export function QueryBox({ ticker }: { ticker: string }) {
  const [question, setQuestion] = React.useState("");
  const query = useCompanyQuery(ticker);

  function handleAsk() {
    const q = question.trim();
    if (!q) return;
    query.mutate({ question: q });
  }

  return (
    <div className="space-y-3">
      <div className="flex gap-2">
        <Input
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder={`Ask about ${ticker}…`}
          aria-label="Question"
        />
        <Button onClick={handleAsk} disabled={query.isPending}>
          Ask
        </Button>
      </div>
      <AnswerPanel
        answer={query.data}
        isLoading={query.isPending}
        isError={query.isError}
      />
    </div>
  );
}
