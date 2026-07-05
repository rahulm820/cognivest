"use client";

import * as React from "react";
import Link from "next/link";
import { ArrowRight, BrainCircuit, Search, TrendingUp, Eraser, Github } from "lucide-react";
import { HeroMock } from "./HeroMock";
import { useScrollReveal } from "./useScrollReveal";

const GITHUB_URL = "https://github.com/rahulm820/cognivest";

const LIFECYCLE = [
  {
    icon: BrainCircuit,
    title: "Remember",
    line: "Price + news stream into a per-company knowledge graph, deduped before they land.",
  },
  {
    icon: Search,
    title: "Recall",
    line: "Ask in plain English. Grounded, cited answers — every claim traces to a source.",
  },
  {
    icon: TrendingUp,
    title: "Improve",
    line: "Thumbs and corrections become memory that reshapes the next answer.",
  },
  {
    icon: Eraser,
    title: "Forget",
    line: "Stale context is pruned, so the graph stays sharp instead of drifting.",
  },
] as const;

const STEPS = [
  {
    n: "01",
    title: "Ingest price + news",
    line: "Collectors pull market data and web content for each watchlisted ticker.",
  },
  {
    n: "02",
    title: "Cognee builds the graph",
    line: "Entities, embeddings and relationships — one isolated dataset per company.",
  },
  {
    n: "03",
    title: "Ask, get cited answers",
    line: "Questions retrieve from the graph and return ranked, source-linked responses.",
  },
] as const;

/** Full landing experience — hero, lifecycle strip, how-it-works, footer. */
export function LandingPage() {
  useScrollReveal();

  return (
    <main className="min-h-screen bg-background">
      {/* top strip */}
      <header className="mx-auto flex h-16 w-full max-w-6xl items-center justify-between px-6">
        <div className="flex items-center gap-2">
          <span className="flex h-6 w-6 items-center justify-center rounded-md bg-primary/15 text-primary">
            ◆
          </span>
          <span className="text-base font-semibold text-foreground">Cognivest</span>
        </div>
        <div className="flex items-center gap-1.5">
          <a
            href={GITHUB_URL}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex h-9 items-center gap-1.5 rounded-lg px-3 text-[14px] font-medium text-text-muted transition-colors hover:text-foreground"
          >
            <Github className="h-4 w-4" />
            GitHub
          </a>
          <Link
            href="/dashboard"
            className="inline-flex h-9 items-center gap-1.5 rounded-lg bg-primary px-4 text-[14px] font-medium text-primary-foreground transition-colors hover:bg-primary-hover"
          >
            Open app
            <ArrowRight className="h-4 w-4" />
          </Link>
        </div>
      </header>

      {/* HERO */}
      <section className="relative mx-auto flex min-h-[calc(100vh-4rem)] w-full max-w-6xl flex-col items-center gap-12 px-6 py-16 lg:flex-row lg:justify-between lg:gap-8 lg:py-0">
        <div className="max-w-xl">
          <p
            className="animate-fade-in-up text-[12px] font-semibold uppercase tracking-[0.2em] text-primary"
            style={{ animationDelay: "0ms" }}
          >
            Built on Cognee&apos;s memory lifecycle
          </p>
          <h1
            className="animate-fade-in-up mt-4 text-4xl font-semibold leading-[1.1] tracking-tight text-foreground sm:text-5xl lg:text-6xl"
            style={{ animationDelay: "80ms" }}
          >
            Financial intelligence that remembers.
          </h1>
          <p
            className="animate-fade-in-up mt-5 max-w-lg text-[16px] leading-relaxed text-text-muted sm:text-[17px]"
            style={{ animationDelay: "160ms" }}
          >
            Per-company knowledge graphs from price + news. Cited answers. An agent that learns you
            — and forgets what&apos;s stale.
          </p>
          <div
            className="animate-fade-in-up mt-8 flex flex-wrap items-center gap-3"
            style={{ animationDelay: "240ms" }}
          >
            <Link
              href="/dashboard"
              className="inline-flex h-11 items-center gap-2 rounded-lg bg-primary px-6 text-[15px] font-medium text-primary-foreground shadow-elevated transition-colors hover:bg-primary-hover"
            >
              Open app
              <ArrowRight className="h-4 w-4" />
            </Link>
            <a
              href={GITHUB_URL}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex h-11 items-center gap-2 rounded-lg border border-border bg-surface px-6 text-[15px] font-medium text-foreground transition-colors hover:border-primary/50"
            >
              <Github className="h-4 w-4" />
              View on GitHub
            </a>
          </div>
        </div>

        <div
          className="animate-fade-in-up w-full lg:w-auto lg:shrink-0"
          style={{ animationDelay: "320ms" }}
        >
          <HeroMock />
        </div>
      </section>

      {/* LIFECYCLE STRIP */}
      <section className="mx-auto w-full max-w-6xl px-6 py-20">
        <p className="reveal text-center text-[12px] font-semibold uppercase tracking-[0.2em] text-text-muted">
          The memory lifecycle
        </p>
        <div className="reveal mt-8 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {LIFECYCLE.map(({ icon: Icon, title, line }) => (
            <div
              key={title}
              className="group rounded-xl border border-border bg-surface p-5 shadow-elevated transition-all duration-200 ease-out hover:-translate-y-1 hover:border-primary/50"
            >
              <span className="flex h-10 w-10 items-center justify-center rounded-lg bg-surface-raised text-text-muted transition-colors duration-200 group-hover:bg-primary/15 group-hover:text-primary">
                <Icon className="h-5 w-5" />
              </span>
              <h3 className="mt-4 text-[15px] font-semibold text-foreground">{title}</h3>
              <p className="mt-1.5 text-[13px] leading-relaxed text-text-muted">{line}</p>
            </div>
          ))}
        </div>
      </section>

      {/* HOW IT WORKS */}
      <section className="mx-auto w-full max-w-6xl px-6 py-20">
        <p className="reveal text-center text-[12px] font-semibold uppercase tracking-[0.2em] text-text-muted">
          How it works
        </p>
        <div className="reveal mt-8 grid grid-cols-1 gap-8 md:grid-cols-3">
          {STEPS.map(({ n, title, line }) => (
            <div key={n} className="flex flex-col">
              <span className="text-[13px] font-semibold tabular-nums text-primary">{n}</span>
              <h3 className="mt-3 text-[16px] font-semibold text-foreground">{title}</h3>
              <p className="mt-1.5 text-[14px] leading-relaxed text-text-muted">{line}</p>
            </div>
          ))}
        </div>
      </section>

      {/* FOOTER */}
      <footer className="border-t border-border">
        <div className="mx-auto flex w-full max-w-6xl flex-col items-start justify-between gap-4 px-6 py-10 sm:flex-row sm:items-center">
          <div>
            <p className="text-[14px] text-foreground">
              Runs entirely on free tiers — Gemini + local fastembed. Open source.
            </p>
            <p className="mt-1 text-[12px] text-text-muted">
              Built for WeMakeDevs × Cognee Hackathon 2026
            </p>
          </div>
          <a
            href={GITHUB_URL}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex h-9 items-center gap-1.5 rounded-lg border border-border bg-surface px-4 text-[14px] font-medium text-foreground transition-colors hover:border-primary/50"
          >
            <Github className="h-4 w-4" />
            GitHub
          </a>
        </div>
      </footer>
    </main>
  );
}
