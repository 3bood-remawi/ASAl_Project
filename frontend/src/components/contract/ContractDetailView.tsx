import Card from "@/components/Card";
import EmptyState from "@/components/EmptyState";
import { TextPanel } from "@/components/contract/TextPanel";
import type { Contract } from "@/types/contract";

interface ContractDetailViewProps {
  contract: Contract;
}

function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

export function ContractDetailView({ contract }: ContractDetailViewProps) {
  const isReady = contract.processingStatus === "done";

  return (
    <div className="p-6">
      <h1 className="text-lg font-semibold text-neutral-900">{contract.name}</h1>

      <Card className="mt-4" padding="md">
        <dl className="grid grid-cols-2 gap-y-3 gap-x-6 text-sm">
          <div>
            <dt className="text-neutral-500">File name</dt>
            <dd className="text-neutral-900">{contract.fileName}</dd>
          </div>
          <div>
            <dt className="text-neutral-500">Status</dt>
            <dd className="text-neutral-900 capitalize">{contract.status}</dd>
          </div>
          <div>
            <dt className="text-neutral-500">Uploaded</dt>
            <dd className="text-neutral-900">{formatDate(contract.uploadDate)}</dd>
          </div>
          <div>
            <dt className="text-neutral-500">Pages</dt>
            <dd className="text-neutral-900">{contract.pageCount ?? "—"}</dd>
          </div>
          <div>
            <dt className="text-neutral-500">Version</dt>
            <dd className="text-neutral-900">{contract.versionNumber}</dd>
          </div>
        </dl>
      </Card>

      <Card className="mt-4" padding="none">
        {isReady ? (
          <TextPanel contractId={contract.id} />
        ) : (
          <EmptyState
            title="Text is still being prepared"
            description="This contract hasn't finished processing yet. Check back once it's ready."
          />
        )}
      </Card>
    </div>
  );
}