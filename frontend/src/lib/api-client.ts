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

export function get<T>(path: string, init: RequestInit = {}): Promise<T> {
  return request<T>(path, {
    method: "GET",
    ...init,
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

export function uploadFile<T>(
  path: string,
  file: File,
  onProgress: (percent: number) => void,
  fieldName = "file"
): Promise<T> {
  return new Promise((resolve, reject) => {
    const formData = new FormData();
    formData.append(fieldName, file);

    const xhr = new XMLHttpRequest();
    xhr.open("POST", `${config.apiBaseUrl}${path}`);

    xhr.upload.onprogress = (event) => {
      if (event.lengthComputable) {
        onProgress(Math.round((event.loaded / event.total) * 100));
      }
    };

    xhr.onload = () => {
      const body = JSON.parse(xhr.responseText || "null");

      if (xhr.status >= 200 && xhr.status < 300) {
        resolve(body as T);
        return;
      }

      const detail = body?.detail;
      const message =
        typeof detail === "string"
          ? detail
          : typeof detail?.message === "string"
            ? detail.message
            : xhr.statusText || "Upload failed";

      reject(new ApiError(message, xhr.status));
    };

    xhr.onerror = () => {
      reject(new ApiError("Network error — check your connection", 0));
    };

    xhr.send(formData);
  });
}