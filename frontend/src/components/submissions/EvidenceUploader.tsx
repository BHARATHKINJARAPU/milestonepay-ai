import React, { useRef, useState } from 'react';
import { AlertCircle, FileUp, Loader2, Sparkles, UploadCloud, X } from 'lucide-react';

interface EvidenceUploaderProps {
  currentCount: number;
  maxFiles?: number;
  onUpload: (files: File[]) => Promise<void>;
  disabled?: boolean;
}

const ALLOWED_EXTS = ['.pdf', '.png', '.jpg', '.jpeg', '.txt'];
const MAX_BYTES = 10 * 1024 * 1024; // 10MB

export const EvidenceUploader: React.FC<EvidenceUploaderProps> = ({
  currentCount,
  maxFiles = 5,
  onUpload,
  disabled = false,
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);

  const remainingSlots = Math.max(0, maxFiles - currentCount);

  const handleFiles = (incoming: FileList | null) => {
    if (!incoming) return;
    setErrorMessage(null);

    const valid: File[] = [];
    const newFiles = Array.from(incoming);

    if (newFiles.length + selectedFiles.length > remainingSlots) {
      setErrorMessage(`Cannot exceed ${maxFiles} total files. You can attach ${remainingSlots} more.`);
      return;
    }

    for (const file of newFiles) {
      const ext = '.' + file.name.split('.').pop()?.toLowerCase();
      if (!ALLOWED_EXTS.includes(ext)) {
        setErrorMessage(`File '${file.name}' has an unsupported extension. Allowed: PDF, PNG, JPG, TXT.`);
        return;
      }
      if (file.size > MAX_BYTES) {
        setErrorMessage(`File '${file.name}' exceeds the 10 MB limit.`);
        return;
      }
      valid.push(file);
    }

    setSelectedFiles((prev) => [...prev, ...valid]);
  };

  const removeSelected = (index: number) => {
    setSelectedFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const handleUploadSubmit = async () => {
    if (selectedFiles.length === 0) return;
    try {
      setIsUploading(true);
      setErrorMessage(null);
      await onUpload(selectedFiles);
      setSelectedFiles([]);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    } catch (err: unknown) {
      setErrorMessage(err instanceof Error ? err.message : 'Evidence upload failed.');
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="space-y-3">
      {/* Dropzone */}
      <div
        onClick={() => !disabled && remainingSlots > 0 && fileInputRef.current?.click()}
        onDragOver={(e) => e.preventDefault()}
        onDrop={(e) => {
          e.preventDefault();
          if (!disabled && remainingSlots > 0) handleFiles(e.dataTransfer.files);
        }}
        className={`relative flex flex-col items-center justify-center rounded-2xl border-2 border-dashed p-6 text-center transition-all ${
          disabled || remainingSlots === 0
            ? 'border-slate-800 bg-slate-950/30 opacity-60 cursor-not-allowed'
            : 'border-slate-800 bg-slate-950/50 hover:border-cyan-500/50 hover:bg-slate-900/40 cursor-pointer'
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept=".pdf,.png,.jpg,.jpeg,.txt"
          onChange={(e) => handleFiles(e.target.files)}
          disabled={disabled || remainingSlots === 0}
          className="hidden"
        />

        <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 mb-2">
          <UploadCloud className="h-6 w-6" />
        </div>

        <div className="text-xs font-semibold text-white">
          {remainingSlots > 0
            ? 'Click or drag verification files here'
            : 'Maximum evidence files attached'}
        </div>
        <p className="mt-1 text-[11px] text-slate-400 max-w-sm">
          Supported: PDF documents, PNG/JPG screenshots, TXT logs (max 10MB each, up to {maxFiles} files).
        </p>

        <div className="mt-2 text-[10px] font-mono text-cyan-400/90">
          {currentCount} of {maxFiles} files attached ({remainingSlots} remaining)
        </div>
      </div>

      {/* Error alert */}
      {errorMessage && (
        <div className="flex items-center gap-2 rounded-xl border border-rose-500/30 bg-rose-950/40 p-3 text-xs text-rose-300">
          <AlertCircle className="h-4 w-4 shrink-0 text-rose-400" />
          <span>{errorMessage}</span>
        </div>
      )}

      {/* Selected Pending Uploads Queue */}
      {selectedFiles.length > 0 && (
        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-4 space-y-3">
          <div className="flex items-center justify-between text-xs font-semibold text-slate-300">
            <span>Ready to Upload ({selectedFiles.length})</span>
            <button
              type="button"
              onClick={handleUploadSubmit}
              disabled={isUploading || disabled}
              className="inline-flex items-center gap-1.5 rounded-lg bg-cyan-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-cyan-500 disabled:opacity-50 transition-all shadow-md shadow-cyan-950"
            >
              {isUploading ? (
                <>
                  <Loader2 className="h-3.5 w-3.5 animate-spin" />
                  Uploading...
                </>
              ) : (
                <>
                  <FileUp className="h-3.5 w-3.5" />
                  Upload Attached Files
                </>
              )}
            </button>
          </div>

          <div className="space-y-1.5">
            {selectedFiles.map((file, idx) => (
              <div
                key={idx}
                className="flex items-center justify-between rounded-lg bg-slate-950 px-3 py-2 text-xs border border-slate-800"
              >
                <div className="truncate font-mono text-slate-300 pr-2">{file.name}</div>
                <div className="flex items-center gap-2 shrink-0">
                  <span className="text-[11px] text-slate-500">
                    {(file.size / 1024).toFixed(0)} KB
                  </span>
                  {!isUploading && (
                    <button
                      type="button"
                      onClick={() => removeSelected(idx)}
                      className="text-slate-500 hover:text-rose-400"
                    >
                      <X className="h-3.5 w-3.5" />
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* AI Processing Disclosure Notice */}
      <div className="flex items-center gap-1.5 text-[11px] text-slate-500">
        <Sparkles className="h-3 w-3 text-cyan-400 shrink-0" />
        <span>Evidence files are securely processed by Google Gemini to evaluate against agreed acceptance criteria.</span>
      </div>
    </div>
  );
};

