import { Search, Bell, History } from "lucide-react";

export function TopNav() {
  return (
    <header className="flex h-16 shrink-0 items-center gap-4 border-b border-border bg-card px-6">
      <div className="relative flex-1 max-w-xl">
        <Search
          className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground"
          aria-hidden="true"
        />
        <input
          type="search"
          placeholder="Search contracts, analyses, or files..."
          aria-label="Search contracts, analyses, or files"
          className="h-10 w-full rounded-lg border border-border bg-secondary/60 pl-10 pr-4 text-sm text-foreground placeholder:text-muted-foreground focus:border-ring focus:bg-card focus:outline-none focus:ring-2 focus:ring-ring/30"
        />
      </div>

      <div className="ml-auto flex items-center gap-2">
        <button
          type="button"
          aria-label="Notifications"
          className="flex h-9 w-9 items-center justify-center rounded-lg text-muted-foreground transition-colors hover:bg-secondary hover:text-foreground"
        >
          <Bell className="h-5 w-5" aria-hidden="true" />
        </button>
        <button
          type="button"
          aria-label="History"
          className="flex h-9 w-9 items-center justify-center rounded-lg text-muted-foreground transition-colors hover:bg-secondary hover:text-foreground"
        >
          <History className="h-5 w-5" aria-hidden="true" />
        </button>

        <div className="ml-2 flex items-center gap-3 border-l border-border pl-4">
          <div className="text-right">
            <p className="text-sm font-semibold leading-tight text-foreground">
              Alex Thompson
            </p>
            <p className="text-xs leading-tight text-muted-foreground">
              Senior Counsel
            </p>
          </div>
          <div
            className="flex h-9 w-9 items-center justify-center rounded-full bg-brand text-sm font-semibold text-brand-foreground"
            aria-hidden="true"
          >
            AT
          </div>
        </div>
      </div>
    </header>
  );
}
