import { useEffect, useState } from "react";
import { getLatestJobStatus } from "@/lib/api/contracts";
import type { ContractJobStatus } from "@/types/contract";

const POLL_INTERVAL_MS = 3000;
const TERMINAL_STATUSES = ["succeeded", "failed"];

export interface UseContractStatusResult {
  jobStatus: ContractJobStatus | null;
  isPolling: boolean;
}

export function useContractStatus(
  contractId: string | null,
  initialJobStatus: ContractJobStatus | null
): UseContractStatusResult {
  const [jobStatus, setJobStatus] = useState<ContractJobStatus | null>(initialJobStatus);

  const isTerminal = jobStatus !== null && TERMINAL_STATUSES.includes(jobStatus.status);

  useEffect(() => {
    if (!contractId || isTerminal) {
      return;
    }

    const intervalId = setInterval(async () => {
      try {
        const latest = await getLatestJobStatus(contractId);
        setJobStatus(latest);
      } catch (err) {
        // A failed request doesn't mean the job failed - just try again next tick.
        console.error(`Failed to poll status for contract ${contractId}:`, err);
      }
    }, POLL_INTERVAL_MS);

    return () => clearInterval(intervalId);
  }, [contractId, isTerminal]);

  return { jobStatus, isPolling: !isTerminal && !!contractId };
}