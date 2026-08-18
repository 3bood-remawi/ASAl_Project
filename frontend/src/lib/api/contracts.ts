import type {
  Contract,
  ContractApiResponse,
  ContractJobApiResponse,
  ContractJobStatus,
  ContractTextApiResponse,
  ContractTextPage,
} from "@/types/contract";
import { get, ApiError } from "@/lib/api-client";

export class ContractNotFoundError extends Error {
  constructor(id: string) {
    super(`Contract not found: ${id}`);
    this.name = "ContractNotFoundError";
  }
}

function mapContractResponse(data: ContractApiResponse): Contract {
  const version = data.current_version;
  return {
    id: data.id,
    name: data.name,
    status: data.status,
    processingStatus: version.processing_status,
    uploadedBy: version.uploaded_by,
    uploadDate: version.uploaded_at,
    fileName: version.file_name,
    fileSizeBytes: version.file_size_bytes,
    pageCount: version.page_count,
    versionNumber: version.version_number,
  };
}

function mapJobResponse(job: ContractJobApiResponse): ContractJobStatus {
  return {
    stage: job.stage,
    status: job.status,
    errorMessage: job.error_message,
  };
}

export async function getContractDetail(id: string): Promise<Contract> {
  try {
    const data = await get<ContractApiResponse>(`/api/contracts/${id}`, {
      cache: "no-store",
    });
    return mapContractResponse(data);
  } catch (err) {
    if (err instanceof ApiError && err.status === 404) {
      throw new ContractNotFoundError(id);
    }
    throw err;
  }
}

export async function getLatestJobStatus(contractId: string): Promise<ContractJobStatus | null> {
    try {
      const job = await get<ContractJobApiResponse>(
        `/api/contracts/${contractId}/status`,
        { cache: "no-store" }
      );
      return mapJobResponse(job);
    } catch (err) {
      if (err instanceof ApiError && err.status === 404) {
        return null;
      }
      throw err;
    }
}

function mapTextResponse(data: ContractTextApiResponse): ContractTextPage {
  return {
    page: data.page,
    totalPages: data.total_pages,
    chunks: data.items.map((item) => ({
      pageNumber: item.page_number,
      text: item.text,
    })),
  };
}

export async function getContractText(
  id: string,
  page: number,
  pageSize: number = 1
): Promise<ContractTextPage> {
  const data = await get<ContractTextApiResponse>(
    `/api/contracts/${id}/text?page=${page}&page_size=${pageSize}`
  );
  return mapTextResponse(data);
}
