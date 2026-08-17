"use client";

import { useRouter } from "next/navigation";
import { FolderOpen, UploadCloud } from "lucide-react";
import Button from "@/components/Button";

export function DashboardActions() {
  const router = useRouter();

  return (
    <div className="flex shrink-0 gap-3">
      <Button variant="secondary" onClick={() => router.push("/contracts")}>
        <FolderOpen className="h-4 w-4" aria-hidden="true" />
        View All Contracts
      </Button>
      <Button onClick={() => router.push("/upload")}>
        <UploadCloud className="h-4 w-4" aria-hidden="true" />
        Upload Contract
      </Button>
    </div>
  );
}