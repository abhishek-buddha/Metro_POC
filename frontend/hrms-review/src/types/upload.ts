export type DocumentType = "PAN_CARD" | "AADHAAR_CARD" | "BANK_DOCUMENT";

export type UploadJobStatus =
  | "idle"
  | "uploading"
  | "queued"
  | "processing"
  | "completed"
  | "failed";

export interface UploadResponse {
  job_id: string;
  submission_id: string;
  status: "queued";
  message: string;
}

export interface JobStatusResponse {
  job_id: string;
  status: "queued" | "processing" | "completed" | "failed" | "unknown";
  submission_id: string;
  document_type: DocumentType | null;
  message: string;
}

export interface DocumentSlot {
  type: DocumentType;
  label: string;
  description: string;
  uploadStatus: UploadJobStatus;
  jobId?: string;
  submissionId?: string;
  documentType?: DocumentType;
  errorMessage?: string;
}
