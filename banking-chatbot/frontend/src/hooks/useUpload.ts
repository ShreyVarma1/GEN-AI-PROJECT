import { useState, useCallback } from "react";
import { chatAPI, HealthResponse } from "../lib/api";

export interface UploadedDoc {
  filename: string;
  chunksIndexed: number;
  uploadedAt: Date;
}

export function useUpload() {
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [uploadSuccess, setUploadSuccess] = useState<string | null>(null);
  const [indexedDocs, setIndexedDocs] = useState<string[]>([]);
  const [isLoadingDocs, setIsLoadingDocs] = useState(false);

  const ALLOWED_TYPES = ["application/pdf", "text/plain", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"];
  const ALLOWED_EXTENSIONS = [".pdf", ".txt", ".docx"];
  const MAX_SIZE_MB = 10;

  const validateFile = (file: File): string | null => {
    const ext = "." + file.name.split(".").pop()?.toLowerCase();
    if (!ALLOWED_EXTENSIONS.includes(ext)) {
      return `Unsupported file type. Please upload PDF, TXT, or DOCX files.`;
    }
    if (file.size > MAX_SIZE_MB * 1024 * 1024) {
      return `File too large. Maximum size is ${MAX_SIZE_MB}MB.`;
    }
    if (file.size === 0) {
      return "File is empty.";
    }
    return null;
  };

  const uploadFile = useCallback(async (file: File) => {
    const validationError = validateFile(file);
    if (validationError) {
      setUploadError(validationError);
      return false;
    }

    setIsUploading(true);
    setUploadProgress(0);
    setUploadError(null);
    setUploadSuccess(null);

    try {
      const response = await chatAPI.uploadDocument(file, (percent) => {
        setUploadProgress(percent);
      });

      const data = response.data;
      setUploadSuccess(
        `"${data.filename}" indexed successfully — ${data.chunks_indexed} chunks added.`
      );
      setIndexedDocs((prev) =>
        prev.includes(data.filename) ? prev : [...prev, data.filename]
      );
      return true;
    } catch (err: unknown) {
      const errorMsg =
        err instanceof Error ? err.message : "Upload failed. Please try again.";
      setUploadError(errorMsg);
      return false;
    } finally {
      setIsUploading(false);
      setUploadProgress(0);
    }
  }, []);

  const fetchIndexedDocs = useCallback(async () => {
    setIsLoadingDocs(true);
    try {
      const response = await chatAPI.getHealth();
      setIndexedDocs(response.data.sources || []);
    } catch {
      // Silently fail — health check is non-critical
    } finally {
      setIsLoadingDocs(false);
    }
  }, []);

  const clearMessages = useCallback(() => {
    setUploadError(null);
    setUploadSuccess(null);
  }, []);

  return {
    isUploading,
    uploadProgress,
    uploadError,
    uploadSuccess,
    indexedDocs,
    isLoadingDocs,
    uploadFile,
    fetchIndexedDocs,
    clearMessages,
  };
}
