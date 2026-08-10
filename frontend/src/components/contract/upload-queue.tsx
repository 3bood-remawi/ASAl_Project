"use client";

import {
  FileText,
  RefreshCw,
  CheckCircle2,
  MoreVertical,
  X,
} from "lucide-react";
import type { QueueItem } from "@/types/upload";

interface UploadQueueProps {
  items: QueueItem[];
  onRemove: (id: string) => void;
  onClearAll: () => void;
}

export function UploadQueue({ items, onRemove, onClearAll }: UploadQueueProps) {
  return (
    <section aria-label="Upload queue">
      <div className="mb-3 flex items-center justify-between">
        <h2 className="text-base font-semibold text-foreground">
          Queue{" "}
          <span className="text-muted-foreground">({items.length})</span>
        </h2>
        {items.length > 0 && (
          <button
            type="button"
            onClick={onClearAll}
            className="text-sm font-medium text-primary transition-colors hover:opacity-80"
          >
            Clear all
          </button>
        )}
      </div>

      {items.length === 0 ? (
        <p className="rounded-xl border border-dashed border-border bg-card px-4 py-6 text-center text-sm text-muted-foreground">
          No documents in the queue yet. Add files to get started.
        </p>
      ) : (
        <ul className="flex flex-col gap-3">
          {items.map((item) => (
            <QueueRow
              key={item.id}
              item={item}
              onRemove={() => onRemove(item.id)}
            />
          ))}
        </ul>
      )}
    </section>
  );
}

function QueueRow({
  item,
  onRemove,
}: {
  item: QueueItem;
  onRemove: () => void;
}) {
  const isUploading = item.status === "uploading";
  const isProcessing = item.status === "processing";
  const isComplete = item.status === "complete";

  return (
    <li
      className={`flex items-center gap-4 rounded-xl border bg-gradient-to-r from-white to-blue-50/30 px-4 py-3.5 shadow-sm ${
        isProcessing ? "border-l-4 border-l-warning border-border" : "border-border"
      }`}
    >
      <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-secondary">
        {isUploading && (
          <FileText className="h-5 w-5 text-muted-foreground" aria-hidden="true" />
        )}
        {isProcessing && (
          <RefreshCw
            className="h-5 w-5 animate-spin text-warning"
            aria-hidden="true"
          />
        )}
        {isComplete && (
          <CheckCircle2 className="h-5 w-5 text-success" aria-hidden="true" />
        )}
      </div>

      <div className="min-w-0 flex-1">
        <p className="truncate text-sm font-semibold text-foreground">
          {item.fileName}
        </p>

        {isUploading && (
          <>
            <p className="mt-0.5 text-xs text-muted-foreground">
              {item.sizeLabel} &bull; Uploading
            </p>
            <div className="mt-2 h-1.5 w-full overflow-hidden rounded-full bg-secondary">
              <div
                className="h-full rounded-full bg-primary transition-all duration-300"
                style={{ width: `${item.progress}%` }}
                role="progressbar"
                aria-valuenow={item.progress}
                aria-valuemin={0}
                aria-valuemax={100}
              />
            </div>
          </>
        )}

        {isProcessing && (
          <p className="mt-0.5 flex items-center gap-1.5 text-xs text-warning">
            <span className="inline-block h-1.5 w-1.5 rounded-full bg-warning" />
            Processing: {item.detail ?? "AI Extraction in progress..."}
          </p>
        )}

        {isComplete && (
          <p className="mt-0.5 text-xs text-muted-foreground">
            Complete &bull; {item.detail ?? `${item.riskFactors ?? 0} Risk Factors Detected`}
          </p>
        )}
      </div>

      <div className="flex shrink-0 items-center gap-2">
        {isUploading && (
          <>
            <span className="text-sm font-semibold text-primary">
              {item.progress}%
            </span>
            <button
              type="button"
              onClick={onRemove}
              aria-label={`Cancel upload of ${item.fileName}`}
              className="flex h-7 w-7 items-center justify-center rounded-md text-muted-foreground transition-colors hover:bg-secondary hover:text-foreground"
            >
              <X className="h-4 w-4" aria-hidden="true" />
            </button>
          </>
        )}

        {isProcessing && (
          <button
            type="button"
            aria-label={`More options for ${item.fileName}`}
            className="flex h-7 w-7 items-center justify-center rounded-md text-muted-foreground transition-colors hover:bg-secondary hover:text-foreground"
          >
            <MoreVertical className="h-4 w-4" aria-hidden="true" />
          </button>
        )}

        {isComplete && (
          <button
            type="button"
            className="rounded-lg bg-primary px-3.5 py-2 text-xs font-semibold text-primary-foreground transition-colors hover:opacity-90"
          >
            View Analysis
          </button>
        )}
      </div>
    </li>
  );
}
