import * as React from "react";
import { Sidebar } from "./Sidebar";
import { TopNav } from "./TopNav";

/** App chrome: top nav + sidebar + main content area. */
export function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen flex-col">
      <TopNav />
      <div className="flex flex-1">
        <Sidebar />
        <main className="mx-auto w-full max-w-6xl flex-1 p-6 md:p-8">{children}</main>
      </div>
    </div>
  );
}
