"use client";

import { useState } from "react";
import { UploadDropzone } from "./upload-dropzone";
import { UploadQueue } from "./upload-queue";
import { uploadFile, ApiError } from "@/lib/api-client";
import { useToast } from "@/components/ToastProvider";
import type { QueueItem } from "@/types/upload";

type UploadResponse = {
  contract_id: string;
};

const initialQueue: QueueItem[] = [];

function formatSize(bytes: number) {
  const mb = bytes / (1024 * 1024);
  return `${mb < 0.1 ? 0.1 : mb.toFixed(1)} MB`;
}

export function UploadPanel() {
  const [items, setItems] = useState<QueueItem[]>(initialQueue);
  const toast = useToast();

  function addFiles(files: FileList | File[]) {
    const fileArray = Array.from(files);
    const incoming = fileArray.map<QueueItem>((file, idx) => ({
      id: `${Date.now()}-${idx}-${file.name}`,
      fileName: file.name,
      sizeLabel: formatSize(file.size),
      status: "uploading",
      progress: 0,
    }));
    setItems((prev) => [...incoming, ...prev]);

    incoming.forEach((item, idx) => {
      const file = fileArray[idx];
        uploadFile<UploadResponse>("/api/contracts/", file, (percent) => {
        setItems((prev) =>
          prev.map((it) => (it.id === item.id ? { ...it, progress: percent } : it))
        );
      })
        .then((response) => {
          setItems((prev) =>
            prev.map((it) =>
              it.id === item.id
                ? {
                    ...it,
                    contractId: response.contract_id,
                    progress: 100,
                    status: "processing",
                  }
                : it
            )
          );
        })
        .catch((err) => {
          const message = err instanceof ApiError ? err.message : "Upload failed";
          toast.error(message);
          setItems((prev) => prev.filter((it) => it.id !== item.id));
        });
    });
  }

  function removeItem(id: string) {
    setItems((prev) => prev.filter((i) => i.id !== id));
  }

  function clearAll() {
    setItems([]);
  }

  return (
    <div className="flex flex-col gap-8">
      <UploadDropzone onFiles={addFiles} />
      <UploadQueue items={items} onRemove={removeItem} onClearAll={clearAll} />
    </div>
  );
}