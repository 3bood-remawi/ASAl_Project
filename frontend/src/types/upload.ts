export type QueueStatus = "uploading" | "processing" | "complete";

export interface QueueItem {
  id: string;
  fileName: string;
  sizeLabel: string;
  status: QueueStatus;
  progress: number; // 0-100, used while uploading
  detail?: string; // e.g. "AI Extraction in progress..." or "12 Risk Factors Detected"
  riskFactors?: number;
}
