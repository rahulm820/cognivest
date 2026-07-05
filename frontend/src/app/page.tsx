import { LandingPage } from "@/features/landing";

/**
 * Marketing landing at `/` — chrome-free (outside the (app) route group).
 * Pure SVG/CSS product mock, zero API calls; "Open App →" enters /dashboard.
 */
export default function HomePage() {
  return <LandingPage />;
}
