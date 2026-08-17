import { FileText, RefreshCw } from "lucide-react";
import { StatCard } from "@/components/dashboard/stat-card";
import { RecentContracts } from "@/components/dashboard/recent-contracts";
import { DashboardActions } from "@/components/dashboard/dashboard-actions";
import { get } from "@/lib/api-client";
import { APP_NAME } from "@/lib/site-config";
import type { ContractListResponse } from "@/types/contract";

// Dashboard counts must reflect uploads/processing that just happened, so
// opt this route out of the full route cache instead of serving a stale
// snapshot (see Next.js route segment config docs).
export const dynamic = "force-dynamic";

const RECENT_CONTRACTS_LIMIT = 5;

export default async function DashboardPage() {
  const [recent, processing] = await Promise.all([
    get<ContractListResponse>(
      `/api/contracts/?page=1&page_size=${RECENT_CONTRACTS_LIMIT}&sort_by=uploaded_date&sort_order=desc`,
      { cache: "no-store" }
    ),
    get<ContractListResponse>(
      `/api/contracts/?page=1&page_size=1&status=processing`,
      { cache: "no-store" }
    ),
  ]);

  return (
    <div className="mx-auto w-full max-w-5xl px-6 py-8">
      <header className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-neutral-900">
            Dashboard
          </h1>
          <p className="mt-1 text-sm text-neutral-500">
            {APP_NAME} at a glance — track uploads and pick up where you left
            off.
          </p>
        </div>

        <DashboardActions />
      </header>

      <div className="mt-8 grid gap-4 sm:grid-cols-2">
        <StatCard
          icon={<FileText className="h-5 w-5" aria-hidden="true" />}
          label="Total Contracts"
          value={recent.total_items}
        />
        <StatCard
          icon={<RefreshCw className="h-5 w-5" aria-hidden="true" />}
          label="Still Processing"
          value={processing.total_items}
        />
      </div>

      <section className="mt-8">
        <h2 className="mb-3 text-base font-semibold text-neutral-900">
          Recent Contracts
        </h2>
        <RecentContracts contracts={recent.items} />
      </section>
    </div>
  );
}
