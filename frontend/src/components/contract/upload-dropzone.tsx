"use client";

import { useRef, useState, type DragEvent } from "react";
import { UploadCloud, FolderOpen } from "lucide-react";
import {
  ACCEPTED_FILE_ACCEPT_ATTR,
  ACCEPTED_FILE_EXTENSIONS,
  MAX_FILE_SIZE_BYTES,
  MAX_FILE_SIZE_MB,
} from "@/lib/site-config";

interface UploadDropzoneProps {
  onFiles: (files: FileList | File[]) => void;
}

// The <input accept> attribute only filters the native file picker dialog —
// it does nothing for drag and drop, and users can still choose "All Files"
// in the dialog anyway. So every file has to be checked here, regardless of
// which path it came in through, before it's handed off to the queue.
function getRejectionReason(file: File): string | null {
  const isAccepted = ACCEPTED_FILE_EXTENSIONS.some((ext) =>
    file.name.toLowerCase().endsWith(ext)
  );
  if (!isAccepted) {
    return `${file.name}: only PDF files are supported`;
  }
  if (file.size > MAX_FILE_SIZE_BYTES) {
    return `${file.name}: exceeds the ${MAX_FILE_SIZE_MB}MB limit`;
  }
  return null;
}

function filterValidFiles(fileList: FileList | File[]) {
  const files = Array.from(fileList);
  const valid: File[] = [];
  const rejections: string[] = [];

  for (const file of files) {
    const reason = getRejectionReason(file);
    if (reason) {
      rejections.push(reason);
    } else {
      valid.push(file);
    }
  }

  return { valid, rejections };
}

export function UploadDropzone({ onFiles }: UploadDropzoneProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [rejections, setRejections] = useState<string[]>([]);

  function processFiles(fileList: FileList | File[]) {
    const { valid, rejections: newRejections } = filterValidFiles(fileList);
    setRejections(newRejections);
    if (valid.length) {
      onFiles(valid);
    }
  }

  function handleDrop(e: DragEvent<HTMLDivElement>) {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files?.length) {
      processFiles(e.dataTransfer.files);
    }
  }

  return (
    <div
      onDragOver={(e) => {
        e.preventDefault();
        setIsDragging(true);
      }}
      onDragLeave={() => setIsDragging(false)}
      onDrop={handleDrop}
      className={`flex flex-col items-center justify-center rounded-2xl border-2 border-dashed px-6 py-14 text-center transition-all duration-300 ${
        isDragging
          ? "border-primary bg-primary/5 shadow-[0_0_0_3px_rgba(66,88,220,0.12)]"
          : "border-border bg-gradient-to-br from-white to-blue-50/60"
      }`}
    >
      <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-primary/15 to-accent shadow-sm">
        <UploadCloud className="h-8 w-8 text-primary" aria-hidden="true" />
      </div>

      <h3 className="mt-5 text-lg font-semibold text-foreground">
        Drag and drop legal files here
      </h3>
      <p className="mt-1 text-sm text-muted-foreground">
        Supported formats: PDF only (Max {MAX_FILE_SIZE_MB}MB per file)
      </p>

      {rejections.length > 0 && (
        <p className="mt-2 max-w-sm text-xs text-destructive" role="alert">
          {rejections.join(" ")}
        </p>
      )}

      <button
        type="button"
        onClick={() => inputRef.current?.click()}
        className="mt-5 inline-flex items-center gap-2 rounded-lg border border-border bg-card px-4 py-2 text-sm font-medium text-foreground shadow-sm transition-colors hover:bg-secondary"
      >
        <FolderOpen className="h-4 w-4" aria-hidden="true" />
        Browse Files
      </button>

      <input
        ref={inputRef}
        type="file"
        multiple
        accept={ACCEPTED_FILE_ACCEPT_ATTR}
        className="sr-only"
        onChange={(e) => {
          if (e.target.files?.length) processFiles(e.target.files);
          e.target.value = "";
        }}
      />
    </div>
  );
}
