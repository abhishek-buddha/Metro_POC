import axios, { AxiosError } from "axios";
import type { JobStatusResponse, UploadResponse } from "../types/upload";

const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
const API_KEY  = import.meta.env.VITE_API_KEY  || "";

const client = axios.create({ baseURL: BASE_URL });

client.interceptors.request.use((cfg) => {
  cfg.headers["X-API-Key"] = API_KEY;
  return cfg;
});

client.interceptors.response.use(
  (res) => res,
  (err: AxiosError<{ detail?: string }>) => {
    const msg =
      err.response?.data?.detail ??
      (err.response?.status === 413 ? "File is too large (max 10 MB)."       :
       err.response?.status === 415 ? "Unsupported file type."                :
       err.response?.status === 401 ? "Unauthorised — check your API key."    :
       err.response?.status === 503 ? "Service unavailable. Please retry."    :
       "An unexpected error occurred.");
    return Promise.reject(new Error(msg));
  },
);

export async function uploadDocument(
  file: File,
  phoneNumber: string,
): Promise<UploadResponse> {
  const form = new FormData();
  form.append("file", file);
  form.append("phone_number", phoneNumber);
  const { data } = await client.post<UploadResponse>(
    "/api/upload/document",
    form,
    { headers: { "Content-Type": "multipart/form-data" } },
  );
  return data;
}

export async function pollJobStatus(jobId: string): Promise<JobStatusResponse> {
  const { data } = await client.get<JobStatusResponse>(`/api/upload/status/${jobId}`);
  return data;
}
