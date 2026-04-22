import React, { useState, useRef, useCallback, useEffect } from 'react';
import { X, Upload, CheckCircle, AlertCircle, Loader } from 'lucide-react';
import { uploadApi } from '../utils/api';
import type { JobStatusResponse } from '../utils/api';

interface AddNewModalProps {
  onClose: () => void;
  onComplete: (submissionId: string) => void;
}

type SlotStatus = 'idle' | 'uploading' | 'queued' | 'processing' | 'completed' | 'failed';

interface DocSlot {
  type: string;
  label: string;
  hint: string;
  status: SlotStatus;
  jobId?: string;
  documentType?: string;
  error?: string;
}

const INITIAL_SLOTS: DocSlot[] = [
  { type: 'PAN_CARD',      label: 'PAN Card',      hint: 'Clear photo or scan of PAN card',        status: 'idle' },
  { type: 'AADHAAR_CARD',  label: 'Aadhaar Card',  hint: 'Front side of Aadhaar card',             status: 'idle' },
  { type: 'BANK_DOCUMENT', label: 'Bank Document', hint: 'Cancelled cheque or bank passbook page', status: 'idle' },
];

const POLL_MS = 2500;

const STATUS_LABEL: Record<SlotStatus, string> = {
  idle:       'Click or drag to upload',
  uploading:  'Uploading\u2026',
  queued:     'Queued for processing\u2026',
  processing: 'Extracting data with AI\u2026',
  completed:  'Extracted successfully',
  failed:     'Failed \u2014 click to retry',
};

const AddNewModal: React.FC<AddNewModalProps> = ({ onClose, onComplete }) => {
  const [phone, setPhone]               = useState('');
  const [phoneError, setPhoneError]     = useState('');
  const [phoneReady, setPhoneReady]     = useState(false);
  const [slots, setSlots]               = useState<DocSlot[]>(INITIAL_SLOTS);
  const [submissionId, setSubmissionId] = useState<string | null>(null);
  const timers = useRef<Record<number, ReturnType<typeof setInterval>>>({});

  useEffect(() => () => { Object.values(timers.current).forEach(clearInterval); }, []);

  const patchSlot = useCallback((i: number, patch: Partial<DocSlot>) =>
    setSlots(prev => prev.map((s, idx) => idx === i ? { ...s, ...patch } : s)), []);

  const handlePhoneSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const digits = phone.replace(/\D/g, '');
    if (digits.length < 7) { setPhoneError('Enter a valid phone number'); return; }
    setPhoneError(''); setPhoneReady(true);
  };

  const handleFile = useCallback(async (idx: number, file: File) => {
    patchSlot(idx, { status: 'uploading', error: undefined });
    try {
      const res = await uploadApi.uploadDocument(file, phone);
      setSubmissionId(prev => prev ?? res.submission_id);
      patchSlot(idx, { status: 'queued', jobId: res.job_id });

      const timer = setInterval(async () => {
        try {
          const st: JobStatusResponse = await uploadApi.getJobStatus(res.job_id);
          if (st.status === 'completed') {
            clearInterval(timers.current[idx]); delete timers.current[idx];
            patchSlot(idx, { status: 'completed', documentType: st.document_type ?? undefined });
          } else if (st.status === 'failed') {
            clearInterval(timers.current[idx]); delete timers.current[idx];
            patchSlot(idx, { status: 'failed', error: st.message });
          } else {
            patchSlot(idx, { status: st.status === 'queued' ? 'queued' : 'processing' });
          }
        } catch { /* network hiccup */ }
      }, POLL_MS);
      timers.current[idx] = timer;
    } catch (err) {
      patchSlot(idx, { status: 'failed', error: err instanceof Error ? err.message : 'Upload failed. Please try again.' });
    }
  }, [phone, patchSlot]);

  const completedCount = slots.filter(s => s.status === 'completed').length;
  const anyInFlight    = slots.some(s => ['uploading','queued','processing'].includes(s.status));
  const canProceed     = completedCount > 0 && !anyInFlight && !!submissionId;

  const reset = () => {
    Object.values(timers.current).forEach(clearInterval);
    timers.current = {};
    setSlots(INITIAL_SLOTS); setSubmissionId(null); setPhoneReady(false);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-xl flex flex-col max-h-[90vh]">

        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200 flex-shrink-0">
          <div>
            <h2 className="text-base font-semibold text-gray-900">Add New Employee</h2>
            <p className="text-xs text-gray-500 mt-0.5">Upload KYC documents — AI extracts details automatically</p>
          </div>
          <button onClick={onClose} className="p-1.5 rounded-lg hover:bg-gray-100 transition-colors">
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        {/* Body */}
        <div className="flex-1 overflow-y-auto px-6 py-5 space-y-6">

          {/* Step 1 — Phone */}
          <div>
            <div className="flex items-center gap-2 mb-3">
              <span className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0 ${phoneReady ? 'bg-green-500 text-white' : 'bg-indigo-600 text-white'}`}>
                {phoneReady ? '✓' : '1'}
              </span>
              <span className="text-sm font-semibold text-gray-700">Employee Phone Number</span>
            </div>
            {!phoneReady ? (
              <form onSubmit={handlePhoneSubmit} className="flex gap-2">
                <div className="flex-1">
                  <input type="tel" value={phone} onChange={e => { setPhone(e.target.value); setPhoneError(''); }}
                    placeholder="e.g. 9876543210" autoFocus
                    className={`w-full px-3 py-2 border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 ${phoneError ? 'border-red-400' : 'border-gray-300'}`}
                  />
                  {phoneError && <p className="text-xs text-red-500 mt-1">{phoneError}</p>}
                </div>
                <button type="submit" className="px-4 py-2 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700 transition-colors whitespace-nowrap">
                  Continue
                </button>
              </form>
            ) : (
              <div className="flex items-center justify-between bg-gray-50 border border-gray-200 rounded-lg px-3 py-2">
                <span className="text-sm font-mono text-gray-700">{phone}</span>
                <button onClick={reset} className="text-xs text-indigo-600 hover:underline">Change</button>
              </div>
            )}
          </div>

          {/* Step 2 — Documents */}
          <div>
            <div className="flex items-center gap-2 mb-3">
              <span className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0 ${completedCount === 3 ? 'bg-green-500 text-white' : phoneReady ? 'bg-indigo-600 text-white' : 'bg-gray-200 text-gray-500'}`}>
                {completedCount === 3 ? '✓' : '2'}
              </span>
              <span className="text-sm font-semibold text-gray-700">Upload Documents</span>
              {phoneReady && <span className="ml-auto text-xs text-gray-400">{completedCount} / 3 processed</span>}
            </div>
            {!phoneReady ? (
              <div className="rounded-xl border border-dashed border-gray-200 p-6 text-center text-sm text-gray-400">
                Complete step 1 to unlock document upload
              </div>
            ) : (
              <div className="space-y-3">
                {slots.map((slot, idx) => (
                  <UploadZone key={slot.type} slot={slot}
                    disabled={anyInFlight && slot.status === 'idle'}
                    onFile={f => handleFile(idx, f)} />
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-gray-100 bg-gray-50 rounded-b-2xl flex items-center justify-between gap-3 flex-shrink-0">
          <p className="text-xs text-gray-400">
            {anyInFlight ? 'Processing, please wait…'
              : completedCount === 0 ? 'Upload at least one document to continue.'
              : `${completedCount} document${completedCount > 1 ? 's' : ''} ready for review.`}
          </p>
          <div className="flex gap-2">
            <button onClick={onClose} className="px-4 py-2 text-sm text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">Cancel</button>
            <button disabled={!canProceed} onClick={() => canProceed && onComplete(submissionId!)}
              className={`px-4 py-2 text-sm font-semibold rounded-lg transition-all ${canProceed ? 'bg-indigo-600 text-white hover:bg-indigo-700 shadow-sm active:scale-95' : 'bg-gray-200 text-gray-400 cursor-not-allowed'}`}>
              View Employee →
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

// ── Upload Zone ────────────────────────────────────────────────────────────────
interface UploadZoneProps { slot: DocSlot; onFile: (f: File) => void; disabled?: boolean; }

const UploadZone: React.FC<UploadZoneProps> = ({ slot, onFile, disabled = false }) => {
  const inputRef   = useRef<HTMLInputElement>(null);
  const [drag, setDrag] = useState(false);
  const clickable  = (slot.status === 'idle' || slot.status === 'failed') && !disabled;
  const inProgress = ['uploading','queued','processing'].includes(slot.status);

  const cls = slot.status === 'completed' ? 'border-green-400 bg-green-50'
    : slot.status === 'failed'  ? 'border-red-400 bg-red-50'
    : inProgress                ? 'border-indigo-300 bg-indigo-50'
    : clickable                 ? `border-gray-300 bg-white hover:border-indigo-400 hover:bg-indigo-50 ${drag ? 'border-indigo-500' : ''}`
    :                             'border-gray-200 bg-gray-50 opacity-50';

  return (
    <div>
      <div className="flex items-center justify-between mb-1">
        <span className="text-xs font-semibold text-gray-600">{slot.label}</span>
        {slot.status === 'completed' && slot.documentType && (
          <span className="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded-full font-medium">{slot.documentType.replace(/_/g, ' ')}</span>
        )}
      </div>
      <div role={clickable ? 'button' : undefined} tabIndex={clickable ? 0 : -1}
        onDragOver={e => { e.preventDefault(); if (clickable) setDrag(true); }}
        onDragLeave={() => setDrag(false)}
        onDrop={e => { e.preventDefault(); setDrag(false); if (!clickable) return; const f = e.dataTransfer.files[0]; if (f) onFile(f); }}
        onClick={() => clickable && inputRef.current?.click()}
        onKeyDown={e => e.key === 'Enter' && clickable && inputRef.current?.click()}
        className={`relative flex items-center gap-3 border-2 border-dashed rounded-xl px-4 py-3 transition-all duration-150 ${cls} ${clickable ? 'cursor-pointer' : 'cursor-default'}`}
      >
        {inProgress && (
          <div className="absolute inset-0 rounded-xl bg-white/70 flex items-center justify-center">
            <Loader className="w-5 h-5 text-indigo-500 animate-spin" />
          </div>
        )}
        <div className="flex-shrink-0">
          {slot.status === 'completed' ? <CheckCircle className="w-5 h-5 text-green-500" />
            : slot.status === 'failed' ? <AlertCircle className="w-5 h-5 text-red-500" />
            : <Upload className={`w-5 h-5 ${disabled && slot.status === 'idle' ? 'text-gray-300' : 'text-gray-400'}`} />}
        </div>
        <div className="min-w-0 flex-1">
          <p className={`text-xs font-medium ${slot.status === 'completed' ? 'text-green-700' : slot.status === 'failed' ? 'text-red-600' : 'text-gray-600'}`}>
            {STATUS_LABEL[slot.status]}
          </p>
          <p className="text-xs text-gray-400 truncate">{slot.hint} · JPG, PNG, PDF (max 10 MB)</p>
        </div>
      </div>
      {slot.error && slot.status === 'failed' && <p className="text-xs text-red-500 mt-1 px-1">{slot.error}</p>}
      <input ref={inputRef} type="file" className="hidden"
        accept=".jpg,.jpeg,.png,.webp,.tiff,.pdf,image/*,application/pdf"
        onChange={e => { const f = e.target.files?.[0]; if (f) { onFile(f); e.target.value = ''; } }}
      />
    </div>
  );
};

export default AddNewModal;
