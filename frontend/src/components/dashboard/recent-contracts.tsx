import Link from "next/link";
import { FileText } from "lucide-react";
import Card from "@/components/Card";
import EmptyState from "@/components/EmptyState";
import type { ContractListItem, ContractStatus } from "@/types/contract";

const statusStyles: Record<ContractStatus, string> = {
  uploaded: "bg-neutral-100 text-neutral-700",
  processing: "bg-warning-100 text-warning-700",
  ready: "bg-success-100 text-success-700",
  archived: "bg-neutral-100 text-neutral-500",
};

const statusLabels: Record<ContractStatus, string> = {
  uploaded: "Uploaded",
  processing: "Processing",
  ready: "Ready",
  archived: "Archived",
};

function formatDate(value: string | null) {
  if (!value) return "—";
  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  }).format(new Date(value));
}

interface RecentContractsProps {
  contracts: ContractListItem[];
}

export function RecentContracts({ contracts }: RecentContractsProps) {
  if (contracts.length === 0) {
    return (
      <Card padding="none">
        <EmptyState
          title="No contracts yet"
          description="Upload your first contract to get started with AI-powered analysis."
        />
      </Card>
    );
  }

  return (
    <Card padding="none" className="divide-y divide-neutral-200">
      {contracts.map((contract) => (
        <Link
          key={contract.id}
          href={`/contracts/${contract.id}`}
          className="flex items-center gap-4 px-4 py-3.5 transition-colors hover:bg-neutral-50"
        >
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-neutral-100">
            <FileText className="h-5 w-5 text-neutral-500" aria-hidden="true" />
          </div>

          <div className="min-w-0 flex-1">
            <p className="truncate text-sm font-medium text-neutral-900">
              {contract.name}
            </p>
            <p className="mt-0.5 text-xs text-neutral-500">
              {formatDate(contract.uploaded_at)}
            </p>
          </div>

          <span
            className={`shrink-0 rounded-full px-2.5 py-1 text-xs font-medium ${statusStyles[contract.status]}`}
          >
            {statusLabels[contract.status]}
          </span>
        </Link>
      ))}
    </Card>
  );
}