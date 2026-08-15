"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import Card from "@/components/Card";
import EmptyState from "@/components/EmptyState";
import Skeleton from "@/components/Skeleton";
import { config } from "@/lib/config";

interface Contract {

    id: string;
    name: string;
    status: string;
    page_count: number | null;
    uploaded_at: string | null;
}

export default function ContractsPage() {
    const [contracts, setContracts] = useState<Contract[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        fetch(`${config.apiBaseUrl}/api/contracts/`)
        .then((res) => {
            if (!res.ok) {
            throw new Error(`Request failed: ${res.status}`);
            }
            return res.json();
        })
        .then((data) => {
            setContracts(data.items);
            setIsLoading(false);
        })
        .catch((err) => {
            setError(err.message);
            setIsLoading(false);
        });
    }, []);

    if (isLoading) {
        return (
            <div className="mx-auto w-full max-w-5xl px-6 py-8">
                <h1 className="text-2xl font-bold text-neutral-900">Contracts</h1>
                <div className="mt-6 flex flex-col gap-3">
                    <Skeleton variant="rectangle" className="h-12" />
                    <Skeleton variant="rectangle" className="h-12" />
                    <Skeleton variant="rectangle" className="h-12" />
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="mx-auto w-full max-w-5xl px-6 py-8">
                <h1 className="text-2xl font-bold text-neutral-900">Contracts</h1>
                <div className="mt-6 rounded-lg border border-danger-200 bg-danger-50 px-4 py-3 text-sm text-danger-700">
                    Couldn&apos;t load contracts. Please try again later.
                </div>
            </div>
        );
    }


    if (contracts.length === 0) {
        return (
            <div className="mx-auto w-full max-w-5xl px-6 py-8">
                    <h1 className="text-2xl font-bold text-neutral-900">Contracts</h1>
                    <Card className="mt-6">
                        <EmptyState
                            title="No contracts yet"
                            description="Upload a contract to see it here."
                    />
                </Card>
            </div>
        );
    }

    return (
    <div className="mx-auto w-full max-w-5xl px-6 py-8">
      <h1 className="text-2xl font-bold text-neutral-900">Contracts</h1>
      <Card className="mt-6" padding="none">
        <table className="w-full text-left text-sm">
          <thead className="border-b border-neutral-200 text-xs uppercase text-neutral-500">
            <tr>
              <th className="px-4 py-3 font-medium">Name</th>
              <th className="px-4 py-3 font-medium">Status</th>
              <th className="px-4 py-3 font-medium">Uploaded</th>
              <th className="px-4 py-3 font-medium">Pages</th>
            </tr>
          </thead>
          <tbody>
            {contracts.map((contract) => (
              <tr key={contract.id} className="border-b border-neutral-100 last:border-0">
                <td className="px-4 py-3">
                  <Link href={`/contracts/${contract.id}`} className="font-medium text-primary-600 hover:underline">
                    {contract.name}
                  </Link>
                </td>
                <td className="px-4 py-3">
                  <StatusBadge status={contract.status} />
                </td>
                <td className="px-4 py-3 text-neutral-600">
                  {contract.uploaded_at ? new Date(contract.uploaded_at).toLocaleDateString() : "—"}
                </td>
                <td className="px-4 py-3 text-neutral-600">
                  {contract.page_count ?? "—"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>
    </div>
  );
}


function StatusBadge({ status }: { status: string }) {
  const styles: Record<string, string> = {
    uploaded: "bg-neutral-100 text-neutral-700",
    processing: "bg-warning-100 text-warning-700",
    ready: "bg-success-100 text-success-700",
    archived: "bg-neutral-100 text-neutral-500",
  };

  return (
    <span className={`inline-block rounded-full px-2.5 py-0.5 text-xs font-medium ${styles[status] ?? styles.uploaded}`}>
      {status}
    </span>
  );
}
