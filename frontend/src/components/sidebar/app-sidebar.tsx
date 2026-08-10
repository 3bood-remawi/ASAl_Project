import {
  LayoutGrid,
  FolderOpen,
  ShieldAlert,
  Settings,
  Plus,
  LifeBuoy,
  LogOut,
} from "lucide-react";
import { APP_NAME, APP_TAGLINE } from "@/lib/site-config";

const navItems = [
  { label: "Dashboard", icon: LayoutGrid, active: false },
  { label: "Repository", icon: FolderOpen, active: true },
  { label: "Risk", icon: ShieldAlert, active: false },
  { label: "Settings", icon: Settings, active: false },
];

export function AppSidebar() {
  return (
    <aside className="flex h-full w-64 shrink-0 flex-col border-r border-sidebar-border bg-sidebar">
      <div className="px-6 py-6">
        <h1 className="text-xl font-bold tracking-tight text-brand">{APP_NAME}</h1>
        <p className="mt-1 text-xs text-muted-foreground">{APP_TAGLINE}</p>
      </div>

      <nav className="flex flex-col gap-1 px-3" aria-label="Primary">
        {navItems.map(({ label, icon: Icon, active }) => (
          <a
            key={label}
            href="#"
            aria-current={active ? "page" : undefined}
            className={`flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors ${
              active
                ? "bg-accent text-accent-foreground"
                : "text-muted-foreground hover:bg-secondary hover:text-foreground"
            }`}
          >
            <Icon className="h-[18px] w-[18px]" aria-hidden="true" />
            {label}
          </a>
        ))}
      </nav>

      <div className="mt-auto flex flex-col gap-1 px-3 pb-6">
        <button
          type="button"
          className="mb-4 flex items-center justify-center gap-2 rounded-lg bg-primary px-4 py-2.5 text-sm font-semibold text-primary-foreground shadow-sm transition-colors hover:opacity-90"
        >
          <Plus className="h-4 w-4" aria-hidden="true" />
          New Analysis
        </button>
        <a
          href="#"
          className="flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-muted-foreground transition-colors hover:bg-secondary hover:text-foreground"
        >
          <LifeBuoy className="h-[18px] w-[18px]" aria-hidden="true" />
          Support
        </a>
        <a
          href="#"
          className="flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-muted-foreground transition-colors hover:bg-secondary hover:text-foreground"
        >
          <LogOut className="h-[18px] w-[18px]" aria-hidden="true" />
          Sign Out
        </a>
      </div>
    </aside>
  );
}
