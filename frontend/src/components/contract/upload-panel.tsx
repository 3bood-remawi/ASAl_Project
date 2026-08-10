"use client";

import { useEffect, useRef, useState } from "react";
import { UploadDropzone } from "./upload-dropzone";
import { UploadQueue } from "./upload-queue";
import type { QueueItem } from "@/types/upload";

const initialQueue: QueueItem[] = [];

function formatSize(bytes: number) {
  const mb = bytes / (1024 * 1024);
  return `${mb < 0.1 ? 0.1 : mb.toFixed(1)} MB`;
}

export function UploadPanel() {
  const [items, setItems] = useState<QueueItem[]>(initialQueue);
  const timers = useRef<Record<string, ReturnType<typeof setInterval>>>({});

  // Drive the progress bar for anything that is uploading.
  useEffect(() => {
    const active = items.filter((i) => i.status === "uploading");
    active.forEach((item) => {
      if (timers.current[item.id]) return;
      timers.current[item.id] = setInterval(() => {
        setItems((prev) =>
          prev.map((it) => {
            if (it.id !== item.id || it.status !== "uploading") return it;
            const next = Math.min(it.progress + 5, 100);
            if (next === 100) {
              clearInterval(timers.current[item.id]);
              delete timers.current[item.id];
              return {
                ...it,
                progress: 100,
                status: "processing",
                detail: "AI Extraction in progress...",
              };
            }
            return { ...it, progress: next };
          })
        );
      }, 400);
    });
  }, [items]);

  useEffect(() => {
    const snapshot = timers.current;
    return () => {
      Object.values(snapshot).forEach(clearInterval);
    };
  }, []);

  function addFiles(files: FileList | File[]) {
    const incoming = Array.from(files).map<QueueItem>((file, idx) => ({
      id: `${Date.now()}-${idx}-${file.name}`,
      fileName: file.name,
      sizeLabel: formatSize(file.size),
      status: "uploading",
      progress: 0,
    }));
    setItems((prev) => [...incoming, ...prev]);
  }

  function removeItem(id: string) {
    if (timers.current[id]) {
      clearInterval(timers.current[id]);
      delete timers.current[id];
    }
    setItems((prev) => prev.filter((i) => i.id !== id));
  }

  function clearAll() {
    Object.values(timers.current).forEach(clearInterval);
    timers.current = {};
    setItems([]);
  }

  return (
    <div className="flex flex-col gap-8">
      <UploadDropzone onFiles={addFiles} />
      <UploadQueue items={items} onRemove={removeItem} onClearAll={clearAll} />
    </div>
  );
}
