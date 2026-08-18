export type ContractStatus = "uploaded" | "processing" | "ready" | "archived";
export type VersionProcessingStatus = "pending" | "extracting" | "done" | "failed";
export type JobStage = "upload" | "extraction" | "embedding" | "classification";
export type JobStatus = "pending" | "running" | "succeeded" | "failed" | "retrying";

export interface ContractListItem {
  id: string;
  name: string;
  status: ContractStatus;
  page_count: number | null;
  uploaded_at: string | null;
}

export interface ContractListResponse {
  items: ContractListItem[];
  page: number;
  page_size: number;
  total_items: number;
}

export interface ContractVersionApiResponse {
  version_number: number;
  uploaded_by: string;
  uploaded_at: string;
  file_name: string;
  file_size_bytes: number | null;
  page_count: number | null;
  processing_status: VersionProcessingStatus;
}

export interface ContractApiResponse {
  id: string;
  name: string;
  status: ContractStatus;
  current_version: ContractVersionApiResponse;
}

export interface ContractJobApiResponse {
  job_id: string;
  version_id: string;
  stage: JobStage;
  status: JobStatus;
  error_message: string | null;
  last_changed_at: string;
}

export interface Contract {
  id: string;
  name: string;
  status: ContractStatus;
  processingStatus: VersionProcessingStatus;
  uploadedBy: string;
  uploadDate: string;
  fileName: string;
  fileSizeBytes: number | null;
  pageCount: number | null;
  versionNumber: number;
}

export interface ContractJobStatus {
  stage: JobStage;
  status: JobStatus;
  errorMessage: string | null;
}

export interface ContractTextChunkApiResponse {
  page_number: number | null;
  chunk_order: number;
  text: string;
}

export interface ContractTextApiResponse {
  contract_id: string;
  version_number: number;
  page: number;
  page_size: number;
  total_items: number;
  total_pages: number;
  items: ContractTextChunkApiResponse[];
}

export interface TextChunk {
  pageNumber: number | null;
  text: string;
}

export interface ContractTextPage {
  page: number;
  totalPages: number;
  chunks: TextChunk[];
}

export interface FilterValuesResponse {
  statuses: string[];
  contract_types: string[];
}
