import { useCallback, useRef, useState } from "react";
import type { UploadJobStatus } from "../types/upload";

interface Props {
  label: string;
  description: string;
  status: UploadJobStatus;
  onFileSelect: (file: File) => void;
  errorMessage?: string;
  documentType?: string;
  disabled?: boolean;
}

const CFG: Record<UploadJobStatus, { border: string; bg: string; icon: string; textColor: string }> = {
  idle:       { border: "border-gray-300 hover:border-indigo-400", bg: "bg-white hover:bg-indigo-50",   icon: "📄", textColor: "text-gray-400"  },
  uploading:  { border: "border-indigo-400",                        bg: "bg-indigo-50",                  icon: "⏫", textColor: "text-indigo-600" },
  queued:     { border: "border-amber-400",                         bg: "bg-amber-50",                   icon: "⏳", textColor: "text-amber-700" },
  processing: { border: "border-blue-400",                          bg: "bg-blue-50",                    icon: "🔍", textColor: "text-blue-600"   },
  completed:  { border: "border-green-400",                         bg: "bg-green-50",                   icon: "✅", textColor: "text-green-700"  },
  failed:     { border: "border-red-400",                           bg: "bg-red-50",                     icon: "❌", textColor: "text-red-600"    },
};

const HINT: Record<UploadJobStatus, string> = {
  idle:       "Drop file here or click to browse",
  uploading:  "Uploading…",
  queued:     "Queued for processing…",
  processing: "Analysing document with AI…",
  completed:  "Extracted successfully",
  failed:     "Failed — click to try again",
};

const SPINNER_STATES: UploadJobStatus[] = ["uploading", "queued", "processing"];

export function FileUploadZone({ label, description, status, onFileSelect, errorMessage, documentType, disabled = false }: Props) {
  const inputRef      = useRef<HTMLInputElement>(null);
  const [drag, setDrag] = useState(false);
  const clickable     = (status === "idle" || status === "failed") && !disabled;
  const cfg           = CFG[status];

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDrag(false);
    if (!clickable) return;
    const f = e.dataTransfer.files[0];
    if (f) onFileSelect(f);
  }, [clickable, onFileSelect]);

  return (
    <div className="flex flex-col gap-1">
      <div className="flex items-center justify-between">
        <span className="text-sm font-semibold text-gray-700">{label}</span>
        {status === "completed" && documentType && (
          <span className="text-xs bg-green-100 text-green-800 px-2 py-0.5 rounded-full font-medium">
            {documentType.replace(/_/g, " ")}
          </span>
        )}
      </div>

      <div
        role={clickable ? "button" : undefined}
        tabIndex={clickable ? 0 : -1}
        onDragOver={(e) => { e.preventDefault(); if (clickable) setDrag(true); }}
        onDragLeave={() => setDrag(false)}
        onDrop={handleDrop}
        onClick={() => clickable && inputRef.current?.click()}
        onKeyDown={(e) => e.key === "Enter" && clickable && inputRef.current?.click()}
        className={[
          "relative flex flex-col items-center justify-center gap-2 rounded-xl border-2 border-dashed px-4 py-8 transition-all duration-200 select-none",
          cfg.border, cfg.bg,
          clickable ? "cursor-pointer" : "cursor-default",
          drag ? "scale-[1.02] shadow-md" : "",
        ].join(" ")}
      >
        {SPINNER_STATES.includes(status) && (
          <div className="absolute inset-0 flex items-center justify-center rounded-xl bg-white/60">
            <div className="h-8 w-8 animate-spin rounded-full border-4 border-indigo-200 border-t-indigo-600" />
          </div>
        )}
        <span className="text-3xl">{cfg.icon}</span>
        <p className={`text-sm font-medium ${cfg.textColor}`}>{HINT[status]}</p>
        <p className="text-xs text-gray-400">{description}</p>
        <p className="text-xs text-gray-300">JPEG · PNG · WEBP · TIFF · PDF · max 10 MB</p>
      </div>

      {errorMessage && status === "failed" && (
        <p className="text-xs text-red-600">{errorMessage}</p>
      )}

      <input
        ref={inputRef}
        type="file"
        className="hidden"
        accept=".jpg,.jpeg,.png,.webp,.tiff,.pdf,application/pdf,image/*"
        onChange={(e) => {
          const f = e.target.files?.[0];
          if (f) { onFileSelect(f); e.target.value = ""; }
        }}
      />
    </div>
  );
}
