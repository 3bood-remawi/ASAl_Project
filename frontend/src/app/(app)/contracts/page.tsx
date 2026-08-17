"use client";

import { useEffect, useState, Suspense } from "react";
import Link from "next/link";
import { useRouter, usePathname, useSearchParams } from "next/navigation";
import Card from "@/components/Card";
import EmptyState from "@/components/EmptyState";
import Skeleton from "@/components/Skeleton";
import { config } from "@/lib/config";

const PAGE_SIZE = 20;
interface Contract {

    id: string;
    name: string;
    status: string;
    page_count: number | null;
    uploaded_at: string | null;
}

function ContractsContent() {

    const [contracts, setContracts] = useState<Contract[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [totalItems, setTotalItems] = useState(0);
    
    const router = useRouter();
    const pathname = usePathname();
    const searchParams = useSearchParams();

    const name = searchParams.get("name") ?? "";
    const status = searchParams.get("status") ?? "";
    const page = Number(searchParams.get("page") ?? "1");
    const [searchInput, setSearchInput] = useState(name);
    const [filterValues, setFilterValues] = useState<{ statuses: string[] }>({ statuses: [] });

    const hasActiveFilters = name !== "" || status !== "";

    useEffect(() => {
      if (searchInput === name) return;
      const timeoutId = setTimeout(() => {
        updateParams({ name: searchInput });
      }, 400);
      return () => clearTimeout(timeoutId);
      // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [searchInput]);

    useEffect(() => {
      fetch(`${config.apiBaseUrl}/api/contracts/filter-values`)
        .then((res) => (res.ok ? res.json() : null))
        .then((data) => data && setFilterValues(data))
        .catch(() => {});
    }, []);

    useEffect(() => {

        setIsLoading(true);
        const params = new URLSearchParams();
        if (name) params.set("name", name);
        if (status) params.set("status", status);
        params.set("page", String(page));
        params.set("page_size", String(PAGE_SIZE));

        fetch(`${config.apiBaseUrl}/api/contracts/?${params.toString()}`)
        .then((res) => {
            if (!res.ok) {
              throw new Error(`Request failed: ${res.status}`);
            }
            return res.json();
        })
        .then((data) => {
            setContracts(data.items);
            setTotalItems(data.total_items);
            setIsLoading(false);
        })
        .catch((err) => {
            setError(err.message);
            setIsLoading(false);
        });
    }, [name, status, page]);

    function updateParams(updates: Record<string, string | null>) {
        const params = new URLSearchParams(searchParams.toString());
        Object.entries(updates).forEach(([key, value]) => {
            if (value) {
                params.set(key, value);
            } else {
                params.delete(key);
            }
        });
        if (!("page" in updates)) {
            params.delete("page");
        }
        router.push(`${pathname}?${params.toString()}`);
      }

const totalPages = Math.max(1, Math.ceil(totalItems / PAGE_SIZE));

let body;
    if (isLoading) {
        body = (
            <div className="mt-6 flex flex-col gap-3">
                <Skeleton variant="rectangle" className="h-12" />
                <Skeleton variant="rectangle" className="h-12" />
                <Skeleton variant="rectangle" className="h-12" />
            </div>
        );
    } else if (error) {
        body = (
            <div className="mt-6 rounded-lg border border-danger-200 bg-danger-50 px-4 py-3 text-sm text-danger-700">
                Couldn&apos;t load contracts. Please try again later.
            </div>
        );
    } else if (contracts.length === 0 && hasActiveFilters) {
        body = (
            <Card className="mt-6">
                <EmptyState
                    title="No matching contracts"
                    description="Try a different search or clear your filters."
                />
            </Card>
        );
    } else if (contracts.length === 0) {
      body = (
        <Card className="mt-6">
          <EmptyState
            title="No contracts yet"
            description="Upload a contract to see it here."
          />
        </Card>
      );
    } else {
      body = (
        <>
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
                      <Link
                        href={`/contracts/${contract.id}`}
                        className="font-medium text-primary-600 hover:underline"
                      >
                        {contract.name}
                      </Link>
                    </td>
                    <td className="px-4 py-3">
                      <StatusBadge status={contract.status} />
                    </td>
                    <td className="px-4 py-3 text-neutral-600">
                      {contract.uploaded_at
                        ? new Date(contract.uploaded_at).toLocaleDateString()
                        : "—"}
                    </td>
                    <td className="px-4 py-3 text-neutral-600">
                      {contract.page_count ?? "—"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Card>

          <div className="mt-4 flex items-center justify-between text-sm text-neutral-600">
            <span>
              Page {page} of {totalPages}
            </span>
            <div className="flex gap-2">
              <button
                type="button"
                disabled={page <= 1}
                onClick={() => updateParams({ page: String(page - 1) })}
                className="rounded-lg border border-neutral-300 px-3 py-1.5 font-medium disabled:cursor-not-allowed disabled:opacity-40"
              >
                Previous
              </button>
              <button
                type="button"
                disabled={page >= totalPages}
                onClick={() => updateParams({ page: String(page + 1) })}
                className="rounded-lg border border-neutral-300 px-3 py-1.5 font-medium disabled:cursor-not-allowed disabled:opacity-40"
              >
                Next
              </button>
            </div>
          </div>
        </>
      );
    }

    return (
    <div className="mx-auto w-full max-w-5xl px-6 py-8">
      <h1 className="text-2xl font-bold text-neutral-900">Contracts</h1>
      <div className="mt-6 flex flex-wrap gap-3">
        <input
          type="text"
          placeholder="Search by name..."
          value={searchInput}
          onChange={(e) => setSearchInput(e.target.value)}
          className="h-10 flex-1 min-w-[200px] rounded-lg border border-neutral-300 px-3 text-sm focus:border-primary-500 focus:outline-none"
        />
        <select
          value={status}
          onChange={(e) => updateParams({ status: e.target.value })}
          className="h-10 rounded-lg border border-neutral-300 px-3 text-sm focus:border-primary-500 focus:outline-none"
        >
          {filterValues.statuses.map((s) => (
            <option key={s} value={s}>
              {s.charAt(0).toUpperCase() + s.slice(1)}
            </option>
          ))}
        </select>
      </div>

      {body}
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


export default function ContractsPage() {
  return (
    <Suspense fallback={<div className="mx-auto w-full max-w-5xl px-6 py-8">Loading...</div>}>
      <ContractsContent />
    </Suspense>
  );
}