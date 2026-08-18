"use client";

import { useEffect, useState } from "react";
import Button from "@/components/Button";
import Spinner from "@/components/Spinner";
import { getContractText } from "@/lib/api/contracts";
import type { ContractTextPage } from "@/types/contract";

interface TextPanelProps {
  contractId: string;
}

export function TextPanel({ contractId }: TextPanelProps) {
  const [currentPage, setCurrentPage] = useState(1);
  const [textPage, setTextPage] = useState<ContractTextPage | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    setIsLoading(true);
    setError(null);

    getContractText(contractId, currentPage)
      .then((result) => {
        if (!cancelled) {
          setTextPage(result);
        }
      })
      .catch(() => {
        if (!cancelled) {
          setError("Unable to load this page of text.");
        }
      })
      .finally(() => {
        if (!cancelled) {
          setIsLoading(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, [contractId, currentPage]);

  if (isLoading) {
    return (
      <div className="flex justify-center p-6">
        <Spinner />
      </div>
    );
  }

  if (error) {
    return <p className="p-6 text-sm text-red-600">{error}</p>;
  }

  if (!textPage || textPage.chunks.length === 0) {
    return <p className="p-6 text-sm text-neutral-500">No text available.</p>;
  }

  return (
    <div className="p-6">
      <div className="space-y-4 text-sm text-neutral-800 whitespace-pre-wrap">
        {textPage.chunks.map((chunk, index) => (
          <p key={index}>{chunk.text}</p>
        ))}
      </div>

      <div className="mt-6 flex items-center justify-between">
        <Button
          onClick={() => setCurrentPage((p) => p - 1)}
          disabled={currentPage <= 1}
        >
          Previous
        </Button>
        <span className="text-sm text-neutral-500">
          Page {textPage.page} of {textPage.totalPages}
        </span>
        <Button
          onClick={() => setCurrentPage((p) => p + 1)}
          disabled={currentPage >= textPage.totalPages}
        >
          Next
        </Button>
      </div>
    </div>
  );
}