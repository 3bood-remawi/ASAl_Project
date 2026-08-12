import { config } from "./config";

export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}
async function request<T>(path: string, init: RequestInit): Promise<T> {
  const res = await fetch(`${config.apiBaseUrl}${path}`, init);

  if (!res.ok) {
    const body = await res.json().catch(() => null);
    const detail = body?.detail;

    const message =
      typeof detail === "string"
        ? detail
        : typeof detail?.message === "string"
          ? detail.message
          : res.statusText;

    throw new ApiError(message, res.status);
  }

  return res.json();
}

export function get<T>(path: string): Promise<T> {
  return request<T>(path, {
    method: "GET",
  });
}

export function post<T>(path: string, body: unknown): Promise<T> {
  return request<T>(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
}

export function postFile<T>(
  path: string,
  file: File,
  fieldName = "file"
): Promise<T> {
  const formData = new FormData();
  formData.append(fieldName, file);

  return request<T>(path, {
    method: "POST",
    body: formData,
  });
}