import { AppShell } from "@/components/layout/AppShell";

/**
 * App-area layout — everything except the marketing landing page (`/`) and the
 * global 404 renders inside the chrome (top nav + sidebar).
 */
export default function AppLayout({ children }: { children: React.ReactNode }) {
  return <AppShell>{children}</AppShell>;
}
