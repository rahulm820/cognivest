# Demo Questions — AAPL (issue #17)

Scripted questions for the demo/video, backed by the hand-curated corpus in
[`data/demo_corpus.json`](../data/demo_corpus.json). GDELT live fetch is 429-blocked,
so these three **source-verified** AAPL events are the demo's news ground truth. Load
them first:

```bash
docker compose exec backend python -m scripts.ingest_demo_corpus --dry-run   # preview
docker compose exec backend python -m scripts.ingest_demo_corpus             # real ingest
```

> **Corpus is AAPL-only, on purpose.** MSFT and TSLA are absent because no verified
> source URLs were available for them. An honest 1-ticker corpus beats a 3-ticker
> corpus with invented sources. Ask MSFT/TSLA questions and the system correctly
> answers "no data ingested yet" — which is itself a truthful demo of the no-data path.

## The corpus (3 competing drivers)

| # | Event | Driver | Date | On 30d chart? |
|---|---|---|---|---|
| 1 | Apple reports Q2 FY2026 results | Earnings | 2026-04-30 | No (outside 30d & ~60d) |
| 2 | India to assemble 28% of iPhones in 2026 | Supply-chain | 2026-05-15 | No (outside 30d; within ~60d) |
| 3 | Apple ships security updates early on AI threat | Product / security | 2026-06-30 | **Yes** (5 days before 2026-07-05) |

The 30-day price chart window is ~**Jun 5 – Jul 5, 2026**, so only item 3 lands as a
chart marker. Items 1–2 still answer questions well; they just sit before the chart's
left edge. (This is the honest limitation of the verified set — noted so the video
doesn't over-claim.)

### Citation-chip caveat (read before filming)

Cognee's Evidence snippet caps each cited chunk at **~160 chars**, and our provenance
header emits fields in the order `source_url | published_at | source | title`, so the
first fields survive truncation and `title` is the sacrificial tail. All three verified
URLs are long, so `--dry-run` reports every header over the cap:

- **Item 1** (219 chars) → citation surfaces **URL + date**; source/title truncated.
- **Item 3** (272 chars) → citation surfaces **URL** (date may truncate).
- **Item 2** (302 chars) → the Moneycontrol URL alone is ~152 chars, so the chip may
  show a **partial URL or none**. This affects only the citation *chip* — the full
  summary is ingested and drives the answer text normally.

If you need a clean title chip on camera, favor item 1 or item 3 questions.

## AAPL questions the corpus answers well

Each question is answerable directly from the ingested summaries. "Expected citation"
is the source that should back the answer.

1. **"How did Apple do in its fiscal Q2 2026?"**
   - Answers from: item 1 (Q2 FY2026 results).
   - Expected citation: Apple Newsroom — *Apple reports Q2 FY2026 results*
     (`apple.com/newsroom/2026/04/...`), 2026-04-30.

2. **"Is Apple moving iPhone manufacturing out of China?"**
   - Answers from: item 2 (India 28% of iPhones; China share 83%→74%, India 14%→23%).
   - Expected citation: Moneycontrol (2026-05-15) — see the URL caveat above.

3. **"Why is Apple pushing iOS security updates early?"**
   - Answers from: item 3 (AI-driven cybersecurity concerns shortening the exploit window).
   - Expected citation: Reuters — *Apple ships security updates early on AI threat*
     (`reuters.com/business/...`), 2026-06-30. **On the 30d chart.**

## Session-memory demo — the supply-chain pair

This is the headline moment: the **same question** answers with a **different emphasis**
for a returning user who has stated a supply-chain interest vs. a fresh user. It works
because item 2 (supply-chain) and items 1/3 (earnings/security) are competing drivers in
the same dataset — so what gets emphasized is steerable by user memory.

**Setup — teach the returning user (once), via the `remember:` path:**

```
X-User-Id: alice
Q: remember: I care most about supply-chain and manufacturing risk
   -> "Got it — I'll remember that. It will shape future answers within about a minute."
```

Wait ~1 minute for the background `cognify_user` to consolidate the preference.

**Then ask BOTH identities the same broad question:**

```
Q: What should I know about Apple right now?
```

- **Fresh user** (`X-User-Id: bob`, no memory) → a balanced answer that spreads across
  the available drivers: Q2 earnings (item 1), the early security updates (item 3), and
  the India manufacturing shift (item 2), with no particular lean. Log line to point at:
  `memory.user_context.empty` (proof zero user context was injected).

- **Returning user** (`X-User-Id: alice`) → the answer **leads with and emphasizes the
  India/China manufacturing shift** (item 2), because her stored preference is folded
  into the retrieval query as a USER PROFILE block. Log line to point at:
  `memory.user_context.injected`.
  - Expected citation for the emphasized point: Moneycontrol / item 2 (URL-caveat above).

**Why this is honest, not a trick:** alice's preference only *steers emphasis* over the
same real corpus; it is never itself a citation (user memory uses CHUNKS retrieval and is
kept out of the provenance parser). Both users are answered from the same three verified
sources — alice just gets the supply-chain angle foregrounded.

> Narration cue: run fresh-user first (balanced), then alice (supply-chain-forward), on
> the identical question. The visible delta in emphasis + the two log lines
> (`empty` vs `injected`) is the whole point of the session-memory feature.
