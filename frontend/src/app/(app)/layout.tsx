import type { ReactNode } from "react";
import { AppSidebar } from "@/components/sidebar/app-sidebar";
import { TopNav } from "@/components/navbar/top-nav";

// Every page under (app)/ gets the sidebar + top nav automatically -
// no more copying them into each page.tsx.
export default function AppLayout({ children }: { children: ReactNode }) {
  return (
    <div className="flex h-screen overflow-hidden bg-background">
      <AppSidebar />

      <div className="flex flex-1 flex-col overflow-hidden">
        <TopNav />
        <main className="flex-1 overflow-y-auto bg-[linear-gradient(180deg,rgba(244,247,252,0.96),rgba(255,255,255,0.96))]">
          {children}
        </main>
      </div>
    </div>
  );
}
