export type ContractStatus = "uploaded" | "processing" | "ready" | "archived";

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