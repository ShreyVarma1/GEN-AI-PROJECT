import React, { useCallback, useEffect, useRef, useState } from "react";
import { useUpload } from "../hooks/useUpload";

interface UploadPanelProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function UploadPanel({ isOpen, onClose }: UploadPanelProps) {
  const {
    isUploading,
    uploadProgress,
    uploadError,
    uploadSuccess,
    indexedDocs,
    isLoadingDocs,
    uploadFile,
    fetchIndexedDocs,
    clearMessages,
  } = useUpload();

  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (isOpen) {
      fetchIndexedDocs();
      clearMessages();
    }
  }, [isOpen]);

  const handleDrop = useCallback(
    async (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragging(false);
      const file = e.dataTransfer.files[0];
      if (file) await uploadFile(file);
    },
    [uploadFile]
  );

  const handleFileChange = useCallback(
    async (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (file) {
        await uploadFile(file);
        // Reset input so same file can be re-uploaded
        if (fileInputRef.current) fileInputRef.current.value = "";
      }
    },
    [uploadFile]
  );

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-end justify-center sm:items-center p-4">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/50 backdrop-blur-sm"
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Panel */}
      <div className="relative bg-white rounded-2xl shadow-2xl w-full max-w-md animate-slide-up">
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-slate-100">
          <div>
            <h2 className="font-semibold text-slate-800 text-base">Upload Document</h2>
            <p className="text-xs text-slate-500 mt-0.5">PDF, TXT, or DOCX — max 10MB</p>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-lg transition-colors"
            aria-label="Close upload panel"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div className="p-5 space-y-4">
          {/* Drop zone */}
          <div
            onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
            onDragLeave={() => setIsDragging(false)}
            onDrop={handleDrop}
            onClick={() => !isUploading && fileInputRef.current?.click()}
            className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all duration-150 ${
              isDragging
                ? "border-electric-500 bg-electric-50"
                : isUploading
                ? "border-slate-200 bg-slate-50 cursor-not-allowed"
                : "border-slate-300 hover:border-electric-400 hover:bg-slate-50"
            }`}
            role="button"
            aria-label="Drop zone for file upload"
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,.txt,.docx"
              onChange={handleFileChange}
              className="hidden"
              disabled={isUploading}
            />

            {isUploading ? (
              <div className="space-y-3">
                <div className="w-10 h-10 mx-auto rounded-full bg-electric-100 flex items-center justify-center">
                  <svg className="w-5 h-5 text-electric-600 animate-spin" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                  </svg>
                </div>
                <p className="text-sm text-slate-600 font-medium">Uploading & indexing...</p>
                <div className="w-full bg-slate-200 rounded-full h-2">
                  <div
                    className="bg-electric-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${uploadProgress}%` }}
                  />
                </div>
                <p className="text-xs text-slate-400">{uploadProgress}%</p>
              </div>
            ) : (
              <div className="space-y-2">
                <div className="w-12 h-12 mx-auto rounded-full bg-slate-100 flex items-center justify-center">
                  <svg className="w-6 h-6 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                      d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                  </svg>
                </div>
                <p className="text-sm font-medium text-slate-700">
                  {isDragging ? "Drop to upload" : "Drag & drop or click to browse"}
                </p>
                <p className="text-xs text-slate-400">Supported: PDF, TXT, DOCX</p>
              </div>
            )}
          </div>

          {/* Success message */}
          {uploadSuccess && (
            <div className="flex items-start gap-2 p-3 bg-green-50 border border-green-200 rounded-lg animate-fade-in">
              <svg className="w-4 h-4 text-green-600 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              <p className="text-sm text-green-700">{uploadSuccess}</p>
            </div>
          )}

          {/* Error message */}
          {uploadError && (
            <div className="flex items-start gap-2 p-3 bg-red-50 border border-red-200 rounded-lg animate-fade-in">
              <svg className="w-4 h-4 text-red-500 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <p className="text-sm text-red-600">{uploadError}</p>
            </div>
          )}

          {/* Indexed documents */}
          <div>
            <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2">
              Indexed Documents ({indexedDocs.length})
            </h3>
            {isLoadingDocs ? (
              <p className="text-xs text-slate-400">Loading...</p>
            ) : indexedDocs.length === 0 ? (
              <p className="text-xs text-slate-400 italic">No documents indexed yet.</p>
            ) : (
              <ul className="space-y-1 max-h-32 overflow-y-auto">
                {indexedDocs.map((doc, idx) => (
                  <li key={idx} className="flex items-center gap-2 text-xs text-slate-600 py-1 px-2 rounded-lg bg-slate-50">
                    <span>📄</span>
                    <span className="truncate">{doc}</span>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
