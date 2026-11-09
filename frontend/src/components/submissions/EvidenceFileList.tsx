import React, { useState } from 'react';
import {
  Download,
  FileCode,
  FileImage,
  FileText,
  Loader2,
  Trash2,
} from 'lucide-react';
import { SubmissionEvidence } from '../../types/submission';
import { downloadEvidenceBlob } from '../../lib/api';

interface EvidenceFileListProps {
  submissionId: string;
  evidence: SubmissionEvidence[];
  canDelete?: boolean;
  onDelete?: (evidenceId: string) => Promise<void>;
}

export const EvidenceFileList: React.FC<EvidenceFileListProps> = ({
  submissionId,
  evidence,
  canDelete = false,
  onDelete,
}) => {
  const [downloadingId, setDownloadingId] = useState<string | null>(null);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
  };

  const getFileIcon = (mediaType: string, filename: string) => {
    const ext = filename.split('.').pop()?.toLowerCase();
    if (ext === 'pdf' || mediaType.includes('pdf')) {
      return <FileText className="h-5 w-5 text-rose-400" />;
    }
    if (['png', 'jpg', 'jpeg'].includes(ext || '') || mediaType.includes('image')) {
      return <FileImage className="h-5 w-5 text-cyan-400" />;
    }
    return <FileCode className="h-5 w-5 text-indigo-400" />;
  };

  const handleDownload = async (item: SubmissionEvidence) => {
    try {
      setDownloadingId(item.id);
      const { data, filename } = await downloadEvidenceBlob(submissionId, item.id);
      const url = window.URL.createObjectURL(data);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } finally {
      setDownloadingId(null);
    }
  };

  const handleDelete = async (evidenceId: string) => {
    if (!onDelete) return;
    try {
      setDeletingId(evidenceId);
      await onDelete(evidenceId);
    } finally {
      setDeletingId(null);
    }
  };

  if (!evidence || evidence.length === 0) {
    return (
      <div className="rounded-xl border border-dashed border-slate-800 bg-slate-950/40 p-4 text-center text-xs text-slate-500">
        No evidence files attached to this submission.
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {evidence.map((item) => (
        <div
          key={item.id}
          className="flex items-center justify-between gap-3 rounded-xl border border-slate-800/80 bg-slate-950/60 p-3.5 backdrop-blur-sm transition-all hover:border-slate-700"
        >
          <div className="flex items-center gap-3 min-w-0">
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-slate-900 border border-slate-800">
              {getFileIcon(item.media_type, item.original_filename)}
            </div>
            <div className="min-w-0">
              <div className="truncate text-xs font-semibold text-white">
                {item.original_filename}
              </div>
              <div className="flex items-center gap-2 mt-0.5 text-[11px] text-slate-400 font-mono">
                <span>{formatFileSize(item.file_size_bytes)}</span>
                <span>&bull;</span>
                <span className="truncate max-w-[140px]" title={item.sha256_hash}>
                  SHA: {item.sha256_hash.substring(0, 10)}...
                </span>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-1.5 shrink-0">
            <button
              type="button"
              onClick={() => handleDownload(item)}
              disabled={downloadingId === item.id}
              className="inline-flex items-center gap-1 rounded-lg border border-slate-700 bg-slate-900 px-2.5 py-1.5 text-xs font-medium text-slate-300 hover:border-slate-600 hover:text-white transition-colors disabled:opacity-50"
              title="Download evidence artifact"
            >
              {downloadingId === item.id ? (
                <Loader2 className="h-3.5 w-3.5 animate-spin" />
              ) : (
                <Download className="h-3.5 w-3.5" />
              )}
              <span className="hidden sm:inline">Download</span>
            </button>

            {canDelete && onDelete && (
              <button
                type="button"
                onClick={() => handleDelete(item.id)}
                disabled={deletingId === item.id}
                className="inline-flex items-center rounded-lg border border-slate-800 p-1.5 text-slate-400 hover:border-rose-900/60 hover:bg-rose-950/40 hover:text-rose-300 transition-colors disabled:opacity-50"
                title="Remove evidence"
              >
                {deletingId === item.id ? (
                  <Loader2 className="h-3.5 w-3.5 animate-spin" />
                ) : (
                  <Trash2 className="h-3.5 w-3.5 text-rose-400" />
                )}
              </button>
            )}
          </div>
        </div>
      ))}
    </div>
  );
};

