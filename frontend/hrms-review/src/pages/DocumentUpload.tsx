import { useCallback, useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { FileUploadZone } from "../components/FileUploadZone";
import { uploadDocument, pollJobStatus } from "../services/uploadApi";
import type { DocumentSlot, UploadJobStatus } from "../types/upload";

const POLL_MS = 2500;

const INITIAL_SLOTS: DocumentSlot[] = [
  { type: "PAN_CARD",      label: "PAN Card",       description: "Clear photo or scan of PAN card",           uploadStatus: "idle" },
  { type: "AADHAAR_CARD",  label: "Aadhaar Card",   description: "Front side of Aadhaar card",                uploadStatus: "idle" },
  { type: "BANK_DOCUMENT", label: "Bank Document",  description: "Bank passbook page or cancelled cheque",    uploadStatus: "idle" },
];

function isValidPhone(v: string) {
  const d = v.replace(/\D/g, "");
  return d.length >= 7 && d.length <= 15;
}

export function DocumentUpload() {
  const navigate = useNavigate();

  const [phone,          setPhone]         = useState("");
  const [phoneError,     setPhoneError]    = useState("");
  const [phoneSubmitted, setPhoneSubmitted] = useState(false);
  const [slots,          setSlots]         = useState<DocumentSlot[]>(INITIAL_SLOTS);
  const [submissionId,   setSubmissionId]  = useState<string | null>(null);

  const timers = useRef<Record<number, ReturnType<typeof setInterval>>>({});

  useEffect(() => () => { Object.values(timers.current).forEach(clearInterval); }, []);

  const patch = useCallback(
    (i: number, p: Partial<DocumentSlot>) =>
      setSlots((prev) => prev.map((s, idx) => (idx === i ? { ...s, ...p } : s))),
    [],
  );

  const handlePhoneSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!isValidPhone(phone)) { setPhoneError("Enter a valid phone number (7–15 digits)."); return; }
    setPhoneError("");
    setPhoneSubmitted(true);
  };

  const handleFileSelect = useCallback(async (idx: number, file: File) => {
    patch(idx, { uploadStatus: "uploading", errorMessage: undefined });

    try {
      const res = await uploadDocument(file, phone);
      setSubmissionId((prev) => prev ?? res.submission_id);
      patch(idx, { uploadStatus: "queued", jobId: res.job_id, submissionId: res.submission_id });

      const timer = setInterval(async () => {
        try {
          const s = await pollJobStatus(res.job_id);
          if (s.status === "completed") {
            clearInterval(timers.current[idx]);
            delete timers.current[idx];
            patch(idx, { uploadStatus: "completed", documentType: s.document_type ?? undefined });
          } else if (s.status === "failed") {
            clearInterval(timers.current[idx]);
            delete timers.current[idx];
            patch(idx, { uploadStatus: "failed", errorMessage: s.message });
          } else {
            const next: UploadJobStatus = s.status === "queued" ? "queued" : "processing";
            patch(idx, { uploadStatus: next });
          }
        } catch { /* network hiccup — keep polling */ }
      }, POLL_MS);

      timers.current[idx] = timer;
    } catch (err) {
      patch(idx, {
        uploadStatus: "failed",
        errorMessage: err instanceof Error ? err.message : "Upload failed. Please try again.",
      });
    }
  }, [phone, patch]);

  const completedCount = slots.filter((s) => s.uploadStatus === "completed").length;
  const anyInFlight    = slots.some((s) => ["uploading","queued","processing"].includes(s.uploadStatus));
  const canProceed     = completedCount > 0 && !anyInFlight && !!submissionId;

  const resetFlow = () => {
    Object.values(timers.current).forEach(clearInterval);
    timers.current = {};
    setSlots(INITIAL_SLOTS);
    setSubmissionId(null);
    setPhoneSubmitted(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-indigo-50 flex items-start justify-center py-12 px-4">
      <div className="w-full max-w-2xl">

        {/* Header */}
        <div className="mb-8 text-center">
          <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-indigo-600 shadow-lg mb-4">
            <span className="text-2xl">📋</span>
          </div>
          <h1 className="text-2xl font-bold text-gray-900">KYC Document Upload</h1>
          <p className="mt-1 text-sm text-gray-500">
            Upload employee KYC documents for AI extraction and HRMS onboarding.
          </p>
        </div>

        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">

          {/* ── Step 1 — Phone number ── */}
          <div className="px-6 py-5 border-b border-gray-100">
            <div className="flex items-center gap-3 mb-4">
              <StepBadge n={1} done={phoneSubmitted} active />
              <h2 className="text-base font-semibold text-gray-800">Employee Phone Number</h2>
            </div>

            {!phoneSubmitted ? (
              <form onSubmit={handlePhoneSubmit} className="flex gap-3">
                <div className="flex-1">
                  <input
                    type="tel"
                    value={phone}
                    onChange={(e) => { setPhone(e.target.value); setPhoneError(""); }}
                    placeholder="e.g. 9876543210"
                    className={[
                      "w-full px-4 py-2.5 rounded-lg border text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500",
                      phoneError ? "border-red-400" : "border-gray-300",
                    ].join(" ")}
                    autoFocus
                  />
                  {phoneError && <p className="mt-1 text-xs text-red-600">{phoneError}</p>}
                </div>
                <button
                  type="submit"
                  className="px-5 py-2.5 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700 active:scale-95 transition-all"
                >
                  Continue →
                </button>
              </form>
            ) : (
              <div className="flex items-center justify-between">
                <span className="text-sm font-mono bg-gray-50 px-3 py-1.5 rounded-lg border border-gray-200 text-gray-700">
                  {phone}
                </span>
                <button onClick={resetFlow} className="text-xs text-indigo-600 hover:underline">
                  Change
                </button>
              </div>
            )}
          </div>

          {/* ── Step 2 — Document uploads ── */}
          <div className="px-6 py-5">
            <div className="flex items-center gap-3 mb-5">
              <StepBadge n={2} done={completedCount === 3} active={phoneSubmitted} />
              <h2 className="text-base font-semibold text-gray-800">Upload Documents</h2>
              {phoneSubmitted && (
                <span className="ml-auto text-xs text-gray-400">
                  {completedCount} / {slots.length} processed
                </span>
              )}
            </div>

            {!phoneSubmitted ? (
              <p className="text-sm text-gray-400 text-center py-8">
                Complete step 1 to unlock document upload.
              </p>
            ) : (
              <div className="flex flex-col gap-4">
                {slots.map((slot, i) => (
                  <FileUploadZone
                    key={slot.type}
                    label={slot.label}
                    description={slot.description}
                    status={slot.uploadStatus}
                    documentType={slot.documentType}
                    errorMessage={slot.errorMessage}
                    disabled={anyInFlight && slot.uploadStatus === "idle"}
                    onFileSelect={(f) => handleFileSelect(i, f)}
                  />
                ))}
              </div>
            )}
          </div>

          {/* ── Footer CTA ── */}
          {phoneSubmitted && (
            <div className="px-6 py-4 bg-gray-50 border-t border-gray-100 flex items-center justify-between">
              <p className="text-xs text-gray-400">
                {anyInFlight
                  ? "Processing documents… please wait."
                  : completedCount === 0
                  ? "Upload at least one document to continue."
                  : `${completedCount} document${completedCount > 1 ? "s" : ""} ready for review.`}
              </p>
              <button
                disabled={!canProceed}
                onClick={() => navigate(`/review?id=${submissionId}`)}
                className={[
                  "px-5 py-2.5 text-sm font-semibold rounded-lg transition-all",
                  canProceed
                    ? "bg-indigo-600 text-white hover:bg-indigo-700 active:scale-95 shadow-sm"
                    : "bg-gray-200 text-gray-400 cursor-not-allowed",
                ].join(" ")}
              >
                Review &amp; Submit →
              </button>
            </div>
          )}
        </div>

        <p className="text-center mt-4 text-xs text-gray-400">
          Already have a submission ID?{" "}
          <button
            onClick={() => {
              const id = prompt("Enter submission ID:");
              if (id?.trim()) navigate(`/review?id=${id.trim()}`);
            }}
            className="text-indigo-500 hover:underline"
          >
            Go to review page
          </button>
        </p>
      </div>
    </div>
  );
}

// ── Small helper component ─────────────────────────────────────────────────
function StepBadge({ n, done, active }: { n: number; done: boolean; active: boolean }) {
  return (
    <span className={[
      "flex-shrink-0 w-7 h-7 rounded-full flex items-center justify-center text-sm font-bold",
      done   ? "bg-green-500 text-white"  :
      active ? "bg-indigo-600 text-white" :
               "bg-gray-200 text-gray-500",
    ].join(" ")}>
      {done ? "✓" : n}
    </span>
  );
}
