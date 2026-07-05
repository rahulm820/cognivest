# Frontend

The frontend is a **Next.js 14 (App Router)** TypeScript app. Stack: Tailwind CSS + shadcn/ui,
TanStack Query (server state), Zustand (global UI state), Recharts / lightweight-charts (price
charts), Axios (typed API client). Derived from [ARCHITECTURE.md §3](../ARCHITECTURE.md) and
[CLAUDE.md §4–§5](../CLAUDE.md).

## App structure

```text
frontend/src/
  app/                  # App Router pages (file-based routing)
    (auth)/             # login / OAuth callback
    dashboard/          # watchlist overview
    company/[ticker]/   # company detail: price chart + query box
    admin/              # ingestion health (admin only)
  components/
    ui/                 # shadcn primitives (Button, Input, Badge, Spinner)
    charts/             # PriceChart, NewsMarkerOverlay
    layout/             # AppShell, Sidebar, TopNav
  features/             # vertical slices: watchlist, company-query, ingestion-status
  hooks/                # useWatchlist, useCompanyPrice, useCompanyQuery, useJobRuns
  contexts/
  services/api/         # axios client + per-resource endpoint modules (ONLY API seam)
  store/                # Zustand stores
  types/                # OpenAPI-generated + hand types
  utils/  constants/  styles/
```

See [folder-structure.md](./folder-structure.md) for the full tree.

> **Status.** All screens and hooks below exist as files, but most call backend routes that are stubs
> today (`GET /companies`, `/companies/{ticker}/price`, `/admin/jobs`, `/auth/*` all raise
> `NotImplementedError`). So the pages render, but their data panels are empty. The one live path is
> the company page's **query box** → `POST /companies/{ticker}/query`. See [api.md](./api.md).

## Screens

### Dashboard — `/dashboard`

- **Purpose**: list watchlisted companies with last price, last ingestion time, alert badges.
- **Components**: `WatchlistTable`, `AddTickerModal`, `IngestionHealthBadge`.
- **State**: server state via React Query (`useWatchlist`); local state for modal open / filter text.
- **API**: `GET /companies`, `POST /companies`.
- **Interactions**: add ticker; click a row → navigate to the company page.
- **Errors**: inline toast on add-failure (invalid ticker); skeleton loaders while fetching.

### Company detail — `/company/[ticker]`

- **Purpose**: price chart with correlated news markers + a natural-language query box.
- **Components**: `PriceChart`, `NewsMarkerOverlay`, `QueryBox`, `AnswerPanel` (citation list),
  `DateRangePicker`.
- **State**: `useCompanyPrice(ticker, range)`, `useCompanyQuery` (mutation), Zustand `selectedRange`.
- **API**: `GET /companies/{ticker}/price`, `POST /companies/{ticker}/query`.
- **Interactions**: ask a question → renders the answer + **citation chips** that scroll-link to
  chart markers. Deep-linkable via query params for range/question.
- **Errors**: partial-failure UI (chart loads even if the query fails); retry via React Query.

### Admin / ingestion health — `/admin`

- **Purpose**: ops visibility into collector job runs per company.
- **Components**: `JobRunTable`, `ErrorLogPanel`.
- **State**: polling React Query (`refetchInterval`).
- **API**: `GET /admin/jobs` (admin only — see [authentication.md](./authentication.md)).

## State management strategy

| Kind | Tool | Examples |
|---|---|---|
| **Server state** | TanStack Query | `useWatchlist`, `useCompanyPrice`, `useCompanyQuery`, `useJobRuns` — caching, retry, staleness. |
| **Global UI state** | Zustand | selected ticker, date range, theme. |
| **Local state** | `useState` | modal open/close, form fields. |

React Query's cache layers on top of the backend Redis cache. GET retries use exponential backoff
(3 attempts) on idempotent reads only; mutations surface errors directly.

## API services layer

**All** API access goes through `services/api/*` — never inline `fetch`/`axios` in components (see
[coding-standards.md](./coding-standards.md)).

| Module | Functions |
|---|---|
| `services/api/client.ts` | axios instance: base URL, auth interceptor, retry-on-401-refresh. |
| `services/api/companies.ts` | `getCompanies`, `addCompany`, `getPriceSeries`. |
| `services/api/query.ts` | `postCompanyQuery`. |
| `services/api/admin.ts` | `getJobRuns`. |

Each is wrapped by a hook (`useWatchlist`, `useCompanyPrice`, `useCompanyQuery`, `useJobRuns`).
Request/response **types are generated from the backend OpenAPI spec** (see [api.md](./api.md)).

## Running it

Locally via Docker (`make up`) or natively (`cd frontend && pnpm dev`). Set
`NEXT_PUBLIC_API_BASE_URL` to the backend's `/api/v1` base. See [setup.md](./setup.md). Cloud hosting
(e.g. Vercel) is roadmap — there is no deployment config in the repo today.
